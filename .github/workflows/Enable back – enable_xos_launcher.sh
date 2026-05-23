#!/bin/bash

# ============================================
# Advanced Launcher Enabler / Disabler
# ============================================

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default package (can be overridden by argument)
DEFAULT_PKG="com.infinix.xoslauncher"
PKG="${1:-$DEFAULT_PKG}"
ACTION="${2:-enable}"   # enable, disable, or toggle

# Function to check if adb is installed
check_adb() {
    if ! command -v adb &> /dev/null; then
        echo -e "${RED}[✗] ADB not found. Please install Android Platform Tools.${NC}"
        exit 1
    fi
}

# Function to check if device is connected
check_device() {
    local device_count=$(adb devices | grep -v "List" | grep -c "device$")
    if [ "$device_count" -eq 0 ]; then
        echo -e "${RED}[✗] No device connected. Please connect your Android device and enable USB debugging.${NC}"
        exit 1
    elif [ "$device_count" -gt 1 ]; then
        echo -e "${YELLOW}[!] Multiple devices found. Using first device.${NC}"
    fi
    echo -e "${GREEN}[✓] Device connected.${NC}"
}

# Function to get current state of package
get_package_state() {
    local state=$(adb shell pm list packages -d | grep -q "$PKG" && echo "disabled" || echo "enabled")
    echo "$state"
}

# Function to enable package
enable_package() {
    echo -e "${BLUE}[+] Enabling package: $PKG${NC}"
    local result=$(adb shell pm enable "$PKG" 2>&1)
    if [[ $result == *"already enabled"* ]]; then
        echo -e "${YELLOW}[!] Package already enabled.${NC}"
    elif [[ $result == *"enabled"* ]]; then
        echo -e "${GREEN}[✓] Package enabled successfully.${NC}"
    else
        echo -e "${RED}[✗] Failed to enable: $result${NC}"
        return 1
    fi
    return 0
}

# Function to disable package
disable_package() {
    echo -e "${BLUE}[+] Disabling package: $PKG${NC}"
    local result=$(adb shell pm disable "$PKG" 2>&1)
    if [[ $result == *"already disabled"* ]]; then
        echo -e "${YELLOW}[!] Package already disabled.${NC}"
    elif [[ $result == *"disabled"* ]]; then
        echo -e "${GREEN}[✓] Package disabled successfully.${NC}"
    else
        echo -e "${RED}[✗] Failed to disable: $result${NC}"
        return 1
    fi
    return 0
}

# Function to toggle package state
toggle_package() {
    local current_state=$(get_package_state)
    echo -e "${BLUE}[+] Current state: $current_state${NC}"
    if [ "$current_state" == "enabled" ]; then
        disable_package
    else
        enable_package
    fi
}

# Function to show usage
show_usage() {
    echo -e "${BLUE}Usage: $0 [package_name] [enable|disable|toggle]${NC}"
    echo ""
    echo "Examples:"
    echo "  $0                                 # Toggle default launcher (com.infinix.xoslauncher)"
    echo "  $0 com.android.chrome disable      # Disable Chrome"
    echo "  $0 com.android.chrome enable       # Enable Chrome"
    echo "  $0 com.android.chrome toggle       # Toggle Chrome"
    echo ""
    echo "Requirements:"
    echo "  - Android device connected with USB debugging enabled"
    echo "  - ADB installed and in PATH"
    exit 0
}

# Main execution
main() {
    # Check for help flag
    if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        show_usage
    fi

    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}   Advanced Package Manager for Android${NC}"
    echo -e "${BLUE}============================================${NC}"

    check_adb
    check_device

    # Verify package exists
    if ! adb shell pm list packages | grep -q "$PKG"; then
        echo -e "${RED}[✗] Package '$PKG' not found on device.${NC}"
        exit 1
    fi

    # Perform action
    case "$ACTION" in
        enable)
            enable_package
            ;;
        disable)
            disable_package
            ;;
        toggle)
            toggle_package
            ;;
        *)
            echo -e "${RED}[✗] Invalid action: $ACTION. Use enable, disable, or toggle.${NC}"
            show_usage
            ;;
    esac

    # Optional: restart launcher if needed (for launcher packages)
    if [[ "$PKG" == *"launcher"* ]] && [[ "$ACTION" == "enable" ]]; then
        echo -e "${YELLOW}[!] Launcher enabled. You may need to press Home button to activate.${NC}"
    fi

    echo -e "${GREEN}[✓] Operation completed.${NC}"
}

# Run main function with all arguments
main "$@"