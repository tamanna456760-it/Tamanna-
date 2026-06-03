#!/bin/bash

# Tamanna File Manager - Cross-platform zip/unzip operations
# Supports Linux, macOS, and Windows (with WSL/Cygwin)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TAMANNA_DIR="tamanna_files"
BACKUP_DIR="tamanna_backups"
LOG_FILE="tamanna_operations.log"

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Detect operating system
detect_os() {
    case "$(uname -s)" in
        Darwin*)    OS="macOS" ;;
        Linux*)     OS="Linux" ;;
        CYGWIN*)    OS="Windows" ;;
        MINGW*)     OS="Windows" ;;
        *)          OS="UNKNOWN" ;;
    esac
    echo "$OS"
}

# Check for required tools
check_dependencies() {
    local missing_tools=()
    
    if ! command -v unzip &> /dev/null; then
        missing_tools+=("unzip")
    fi
    
    if ! command -v zip &> /dev/null; then
        missing_tools+=("zip")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_message "${RED}Missing required tools: ${missing_tools[*]}${NC}"
        install_dependencies "${missing_tools[@]}"
    fi
}

# Install missing dependencies
install_dependencies() {
    local OS=$(detect_os)
    
    case "$OS" in
        "Linux")
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y "$@"
            elif command -v yum &> /dev/null; then
                sudo yum install -y "$@"
            elif command -v pacman &> /dev/null; then
                sudo pacman -S --noconfirm "$@"
            fi
            ;;
        "macOS")
            if command -v brew &> /dev/null; then
                brew install "$@"
            else
                log_message "${RED}Please install Homebrew first${NC}"
                exit 1
            fi
            ;;
        "Windows")
            log_message "${YELLOW}Please install missing tools manually or use WSL${NC}"
            ;;
    esac
}

# Create directory structure
setup_directories() {
    mkdir -p "$TAMANNA_DIR"
    mkdir -p "$BACKUP_DIR"
    log_message "${GREEN}Created directory structure${NC}"
}

# Extract Tamanna files
extract_tamanna() {
    local file="$1"
    local extract_dir="$2"
    
    if [ -z "$extract_dir" ]; then
        extract_dir="$TAMANNA_DIR/extracted_$(date +%Y%m%d_%H%M%S)"
    fi
    
    log_message "${BLUE}Extracting $file to $extract_dir${NC}"
    
    if [ ! -f "$file" ]; then
        log_message "${RED}File $file not found!${NC}"
        return 1
    fi
    
    mkdir -p "$extract_dir"
    
    if unzip -q "$file" -d "$extract_dir"; then
        log_message "${GREEN}Successfully extracted $file${NC}"
        echo "$extract_dir"
    else
        log_message "${RED}Failed to extract $file${NC}"
        return 1
    fi
}

# Create zip archive
create_tamanna_zip() {
    local source="$1"
    local output_file="$2"
    
    if [ -z "$output_file" ]; then
        output_file="tamanna_archive_$(date +%Y%m%d_%H%M%S).zip"
    fi
    
    log_message "${BLUE}Creating archive $output_file from $source${NC}"
    
    if [ -d "$source" ]; then
        if zip -qr "$output_file" "$source"; then
            log_message "${GREEN}Successfully created $output_file${NC}"
            echo "$output_file"
        else
            log_message "${RED}Failed to create archive${NC}"
            return 1
        fi
    elif [ -f "$source" ]; then
        if zip -q "$output_file" "$source"; then
            log_message "${GREEN}Successfully created $output_file${NC}"
            echo "$output_file"
        else
            log_message "${RED}Failed to create archive${NC}"
            return 1
        fi
    else
        log_message "${RED}Source $source not found!${NC}"
        return 1
    fi
}

# Backup Tamanna files
backup_tamanna() {
    local backup_name="tamanna_backup_$(date +%Y%m%d_%H%M%S).zip"
    
    log_message "${YELLOW}Creating backup: $backup_name${NC}"
    
    if [ -d "$TAMANNA_DIR" ]; then
        create_tamanna_zip "$TAMANNA_DIR" "$BACKUP_DIR/$backup_name"
    else
        log_message "${YELLOW}No tamanna files to backup${NC}"
    fi
}

# List contents of zip file
list_zip_contents() {
    local file="$1"
    
    if [ ! -f "$file" ]; then
        log_message "${RED}File $file not found!${NC}"
        return 1
    fi
    
    log_message "${BLUE}Contents of $file:${NC}"
    unzip -l "$file" | tee -a "$LOG_FILE"
}

# Batch extract multiple files
batch_extract() {
    local pattern="$1"
    local extract_base="$TAMANNA_DIR/batch_extract_$(date +%Y%m%d_%H%M%S)"
    
    mkdir -p "$extract_base"
    
    for file in $pattern; do
        if [ -f "$file" ]; then
            local extract_dir="$extract_base/$(basename "$file" .zip)"
            extract_tamanna "$file" "$extract_dir"
        fi
    done
}

# Show usage information
show_usage() {
    cat << EOF
${GREEN}Tamanna File Manager${NC}

Usage: $0 [OPTIONS]

Options:
  -e, --extract FILE [DIR]    Extract zip file to directory (optional)
  -c, --create SOURCE [OUTPUT] Create zip archive from source
  -l, --list FILE            List contents of zip file
  -b, --backup               Create backup of tamanna files
  -a, --batch PATTERN        Batch extract multiple files (use quotes for patterns)
  -s, --setup                Setup directory structure
  --clean                    Remove all tamanna files and backups
  -h, --help                 Show this help message

Examples:
  $0 --setup
  $0 --extract data.zip
  $0 --create my_folder archive.zip
  $0 --list package.zip
  $0 --backup
  $0 --batch "*.zip"
  $0 --clean

EOF
}

# Cleanup function
cleanup() {
    log_message "${YELLOW}Cleaning up tamanna files and backups...${NC}"
    rm -rf "$TAMANNA_DIR"
    rm -rf "$BACKUP_DIR"
    log_message "${GREEN}Cleanup completed${NC}"
}

# Main script execution
main() {
    log_message "${GREEN}=== Tamanna File Manager Started ===${NC}"
    
    # Detect OS and check dependencies
    OS=$(detect_os)
    log_message "Operating System: $OS"
    check_dependencies
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--extract)
                extract_tamanna "$2" "$3"
                shift 3
                ;;
            -c|--create)
                create_tamanna_zip "$2" "$3"
                shift 3
                ;;
            -l|--list)
                list_zip_contents "$2"
                shift 2
                ;;
            -b|--backup)
                backup_tamanna
                shift
                ;;
            -a|--batch)
                batch_extract "$2"
                shift 2
                ;;
            -s|--setup)
                setup_directories
                shift
                ;;
            --clean)
                cleanup
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_message "${RED}Unknown option: $1${NC}"
                show_usage
                exit 1
                ;;
        esac
    done
    
    log_message "${GREEN}=== Tamanna File Manager Completed ===${NC}"
}

# Run main function with all arguments
main "$@"