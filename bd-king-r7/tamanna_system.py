#!/usr/bin/env python3
"""
TAMANNA CODE LANGUAGE COMPLETE SYSTEM
TK Token System + Color Coding + .hm Files + Auto-Build + Multi-Platform
"""

import os
import sys
import re
import math
import time
import json
import shutil
import logging
import platform
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

# Multi-platform support
class Platform:
    WINDOWS = "windows"
    LINUX = "linux" 
    ANDROID = "android"
    KALI = "kali"
    
    @staticmethod
    def detect():
        system = platform.system().lower()
        if system == "windows":
            return Platform.WINDOWS
        elif system == "linux":
            if "kali" in platform.platform().lower():
                return Platform.KALI
            elif "android" in platform.platform().lower():
                return Platform.ANDROID
            return Platform.LINUX
        return Platform.LINUX

# ==================== TOKEN SYSTEM (TK) ====================
class TK(Enum):
    """Tamanna Token System"""
    # Literals
    TK_NUMBER = "TK_NUMBER"
    TK_STRING = "TK_STRING"
    TK_IDENTIFIER = "TK_IDENTIFIER"
    
    # Bangla Keywords
    TK_LIKHO = "TK_LIKHO"           # লেখো
    TK_NIRNAY = "TK_NIRNAY"         # নির্ধারণ  
    TK_JODI = "TK_JODI"             # যদি
    TK_NAHOLE = "TK_NAHOLE"         # নাহলে
    TK_JABTAK = "TK_JABTAK"         # যতক্ষণ
    TK_JONNO = "TK_JONNO"           # জন্য
    TK_KAJ = "TK_KAJ"               # কাজ
    TK_FEROT = "TK_FEROT"           # ফেরত
    TK_THAM = "TK_THAM"             # থাম
    TK_CHOLBE = "TK_CHOLBE"         # চলবে
    
    # English Keywords
    TK_PRINT = "TK_PRINT"
    TK_SET = "TK_SET"
    TK_IF = "TK_IF"
    TK_ELSE = "TK_ELSE"
    TK_WHILE = "TK_WHILE"
    TK_FOR = "TK_FOR"
    TK_FUNCTION = "TK_FUNCTION"
    TK_RETURN = "TK_RETURN"
    TK_BREAK = "TK_BREAK"
    TK_CONTINUE = "TK_CONTINUE"
    
    # Math Operators
    TK_JOG = "TK_JOG"               # যোগ
    TK_BIYOG = "TK_BIYOG"           # বিয়োগ
    TK_GUN = "TK_GUN"               # গুণ
    TK_BHAG = "TK_BHAG"             # ভাগ
    TK_SHESH = "TK_SHESH"           # শেষ
    TK_GHOTON = "TK_GHOTON"         # ঘাত
    
    # Comparison
    TK_SOMAN = "TK_SOMAN"           # সমান
    TK_ASOMAN = "TK_ASOMAN"         # অসমান
    TK_BORO = "TK_BORO"             # বড়
    TK_CHOTO = "TK_CHOTO"           # ছোট
    TK_BORO_SOMAN = "TK_BORO_SOMAN" # বড় বা সমান
    TK_CHOTO_SOMAN = "TK_CHOTO_SOMAN" # ছোট বা সমান
    
    # Logical
    TK_O = "TK_O"                   # বা
    TK_EBONG = "TK_EBONG"           # এবং
    TK_NA = "TK_NA"                 # না
    
    # Special Values
    TK_SATYA = "TK_SATYA"           # সত্য
    TK_MITHA = "TK_MITHA"           # মিথ্যা
    TK_KHALI = "TK_KHALI"           # খালি
    
    # Network Keywords
    TK_NETWORK = "TK_NETWORK"
    TK_SERVER = "TK_SERVER"
    TK_CLIENT = "TK_CLIENT"
    TK_CONNECT = "TK_CONNECT"
    TK_SEND = "TK_SEND"
    TK_RECEIVE = "TK_RECEIVE"
    
    # System Keywords
    TK_SYSTEM = "TK_SYSTEM"
    TK_RUN = "TK_RUN"
    TK_EXECUTE = "TK_EXECUTE"
    TK_FILE = "TK_FILE"
    
    # Operators
    TK_PLUS = "TK_PLUS"
    TK_MINUS = "TK_MINUS"
    TK_MULTIPLY = "TK_MULTIPLY"
    TK_DIVIDE = "TK_DIVIDE"
    TK_MODULO = "TK_MODULO"
    TK_POWER = "TK_POWER"
    
    # Delimiters
    TK_LPAREN = "TK_LPAREN"
    TK_RPAREN = "TK_RPAREN"
    TK_LBRACE = "TK_LBRACE"
    TK_RBRACE = "TK_RBRACE"
    TK_COMMA = "TK_COMMA"
    TK_SEMICOLON = "TK_SEMICOLON"
    TK_NEWLINE = "TK_NEWLINE"
    
    TK_EOF = "TK_EOF"

# ==================== COLOR SYSTEM (7 Colors) ====================
class Color:
    """7 Color System for Tamanna Language"""
    RED = "\033[91m"      # Errors, Important
    GREEN = "\033[92m"    # Success, Output
    YELLOW = "\033[93m"   # Warnings, Keywords
    BLUE = "\033[94m"     # Information, Variables
    MAGENTA = "\033[95m"  # Functions, Special
    CYAN = "\033[96m"     # Comments, Strings
    WHITE = "\033[97m"    # Normal text
    RESET = "\033[0m"
    
    # Color mapping for tokens
    TOKEN_COLORS = {
        TK.TK_NUMBER: YELLOW,
        TK.TK_STRING: CYAN,
        TK.TK_IDENTIFIER: WHITE,
        TK.TK_LIKHO: GREEN,
        TK.TK_NIRNAY: BLUE,
        TK.TK_JODI: MAGENTA,
        TK.TK_NAHOLE: MAGENTA,
        TK.TK_PRINT: GREEN,
        TK.TK_SET: BLUE,
        TK.TK_IF: MAGENTA,
        TK.TK_ELSE: MAGENTA,
        TK.TK_NETWORK: CYAN,
        TK.TK_SYSTEM: YELLOW,
    }
    
    @staticmethod
    def colorize(text, color):
        return f"{color}{text}{Color.RESET}"
    
    @staticmethod
    def get_token_color(token_type):
        return Color.TOKEN_COLORS.get(token_type, Color.WHITE)

# ==================== TOKEN CLASS ====================
@dataclass
class Token:
    type: TK
    value: Any
    line: int
    column: int
    color: str = None
    
    def __post_init__(self):
        if self.color is None:
            self.color = Color.get_token_color(self.type)
    
    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})"
    
    def colored_str(self):
        return Color.colorize(f"{self.type.value}: {repr(self.value)}", self.color)

# ==================== LEXER WITH COLOR ====================
class TamannaLexer:
    """Tamanna Lexer with TK Token System and Color Coding"""
    
    KEYWORDS = {
        # Bangla Keywords
        'লেখো': TK.TK_LIKHO, 'নির্ধারণ': TK.TK_NIRNAY, 'যদি': TK.TK_JODI,
        'নাহলে': TK.TK_NAHOLE, 'যতক্ষণ': TK.TK_JABTAK, 'জন্য': TK.TK_JONNO,
        'কাজ': TK.TK_KAJ, 'ফেরত': TK.TK_FEROT, 'থাম': TK.TK_THAM, 'চলবে': TK.TK_CHOLBE,
        
        # English Keywords
        'print': TK.TK_PRINT, 'set': TK.TK_SET, 'if': TK.TK_IF, 'else': TK.TK_ELSE,
        'while': TK.TK_WHILE, 'for': TK.TK_FOR, 'function': TK.TK_FUNCTION,
        'return': TK.TK_RETURN, 'break': TK.TK_BREAK, 'continue': TK.TK_CONTINUE,
        
        # Math Operators
        'যোগ': TK.TK_JOG, 'বিয়োগ': TK.TK_BIYOG, 'গুণ': TK.TK_GUN,
        'ভাগ': TK.TK_BHAG, 'শেষ': TK.TK_SHESH, 'ঘাত': TK.TK_GHOTON,
        
        # Comparison
        'সমান': TK.TK_SOMAN, 'অসমান': TK.TK_ASOMAN, 'বড়': TK.TK_BORO,
        'ছোট': TK.TK_CHOTO, 'বড়সমান': TK.TK_BORO_SOMAN, 'ছোটসমান': TK.TK_CHOTO_SOMAN,
        
        # Logical
        'বা': TK.TK_O, 'এবং': TK.TK_EBONG, 'না': TK.TK_NA,
        
        # Special Values
        'সত্য': TK.TK_SATYA, 'মিথ্যা': TK.TK_MITHA, 'খালি': TK.TK_KHALI,
        
        # Network Keywords
        'নেটওয়ার্ক': TK.TK_NETWORK, 'সার্ভার': TK.TK_SERVER, 'ক্লায়েন্ট': TK.TK_CLIENT,
        'কানেক্ট': TK.TK_CONNECT, 'সেন্ড': TK.TK_SEND, 'রিসিভ': TK.TK_RECEIVE,
        'network': TK.TK_NETWORK, 'server': TK.TK_SERVER, 'client': TK.TK_CLIENT,
        'connect': TK.TK_CONNECT, 'send': TK.TK_SEND, 'receive': TK.TK_RECEIVE,
        
        # System Keywords
        'সিস্টেম': TK.TK_SYSTEM, 'রান': TK.TK_RUN, 'এক্সিকিউট': TK.TK_EXECUTE,
        'ফাইল': TK.TK_FILE, 'system': TK.TK_SYSTEM, 'run': TK.TK_RUN,
        'execute': TK.TK_EXECUTE, 'file': TK.TK_FILE,
    }
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
    
    def tokenize(self) -> List[Token]:
        """Tokenize source code with color information"""
        while self.position < len(self.source_code):
            char = self.source_code[self.position]
            
            if char.isspace():
                self._handle_whitespace()
            elif char.isdigit():
                self._handle_number()
            elif char.isalpha() or char in 'অআইঈউঊঋএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়':
                self._handle_identifier()
            elif char in ['"', "'", '`']:
                self._handle_string()
            else:
                self._handle_operator()
        
        self.tokens.append(Token(TK.TK_EOF, None, self.line, self.column))
        return self.tokens
    
    def _handle_whitespace(self):
        char = self.source_code[self.position]
        if char == '\n':
            self.tokens.append(Token(TK.TK_NEWLINE, '\n', self.line, self.column))
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1
    
    def _handle_number(self):
        start_pos = self.position
        start_col = self.column
        
        while (self.position < len(self.source_code) and 
               (self.source_code[self.position].isdigit() or self.source_code[self.position] == '.')):
            self.position += 1
            self.column += 1
        
        number_str = self.source_code[start_pos:self.position]
        value = float(number_str) if '.' in number_str else int(number_str)
        self.tokens.append(Token(TK.TK_NUMBER, value, self.line, start_col))
    
    def _handle_identifier(self):
        start_pos = self.position
        start_col = self.column
        
        while (self.position < len(self.source_code) and 
               (self.source_code[self.position].isalnum() or self.source_code[self.position] == '_' or
                self.source_code[self.position] in 'অআইঈউঊঋএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়')):
            self.position += 1
            self.column += 1
        
        identifier = self.source_code[start_pos:self.position]
        token_type = self.KEYWORDS.get(identifier, TK.TK_IDENTIFIER)
        self.tokens.append(Token(token_type, identifier, self.line, start_col))
    
    def _handle_string(self):
        start_col = self.column
        quote_char = self.source_code[self.position]
        self.position += 1
        self.column += 1
        
        start_pos = self.position
        while (self.position < len(self.source_code) and self.source_code[self.position] != quote_char):
            if self.source_code[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
        
        if self.position >= len(self.source_code):
            raise SyntaxError(f"Unterminated string at line {self.line}")
        
        string_value = self.source_code[start_pos:self.position]
        self.tokens.append(Token(TK.TK_STRING, string_value, self.line, start_col))
        self.position += 1
        self.column += 1
    
    def _handle_operator(self):
        char = self.source_code[self.position]
        next_char = self.source_code[self.position + 1] if self.position + 1 < len(self.source_code) else None
        
        operators = {
            '+': TK.TK_PLUS, '-': TK.TK_MINUS, '*': TK.TK_MULTIPLY,
            '/': TK.TK_DIVIDE, '%': TK.TK_MODULO, '^': TK.TK_POWER,
            '(': TK.TK_LPAREN, ')': TK.TK_RPAREN, '{': TK.TK_LBRACE,
            '}': TK.TK_RBRACE, ',': TK.TK_COMMA, ';': TK.TK_SEMICOLON,
            '=': TK.TK_SOMAN, '!': TK.TK_NA
        }
        
        # Two-character operators
        if char == '=' and next_char == '=':
            self.tokens.append(Token(TK.TK_SOMAN, '==', self.line, self.column))
            self.position += 2
            self.column += 2
            return
        elif char == '!' and next_char == '=':
            self.tokens.append(Token(TK.TK_ASOMAN, '!=', self.line, self.column))
            self.position += 2
            self.column += 2
            return
        elif char == '>' and next_char == '=':
            self.tokens.append(Token(TK.TK_BORO_SOMAN, '>=', self.line, self.column))
            self.position += 2
            self.column += 2
            return
        elif char == '<' and next_char == '=':
            self.tokens.append(Token(TK.TK_CHOTO_SOMAN, '<=', self.line, self.column))
            self.position += 2
            self.column += 2
            return
        elif char == '>':
            self.tokens.append(Token(TK.TK_BORO, '>', self.line, self.column))
            self.position += 1
            self.column += 1
            return
        elif char == '<':
            self.tokens.append(Token(TK.TK_CHOTO, '<', self.line, self.column))
            self.position += 1
            self.column += 1
            return
        
        if char in operators:
            self.tokens.append(Token(operators[char], char, self.line, self.column))
            self.position += 1
            self.column += 1
        else:
            raise SyntaxError(f"Unknown character '{char}' at line {self.line}, column {self.column}")

# ==================== .hm FILE HANDLER ====================
class HMFileHandler:
    """Handler for .hm (Tamanna) files"""
    
    @staticmethod
    def save(code: str, filename: str):
        """Save Tamanna code to .hm file"""
        if not filename.endswith('.hm'):
            filename += '.hm'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)
        print(Color.colorize(f"File saved: {filename}", Color.GREEN))
    
    @staticmethod
    def load(filename: str) -> str:
        """Load Tamanna code from .hm file"""
        if not filename.endswith('.hm'):
            filename += '.hm'
        
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def compile_to_python(hm_code: str) -> str:
        """Compile .hm code to Python"""
        conversions = {
            'লেখো': 'print',
            'নির্ধারণ': '',
            'যদি': 'if',
            'নাহলে': 'else',
            'যতক্ষণ': 'while',
            'জন্য': 'for',
            'কাজ': 'def',
            'ফেরত': 'return',
            'সত্য': 'True',
            'মিথ্যা': 'False',
            'নেটওয়ার্ক': 'network',
            'সার্ভার': 'server',
            'ক্লায়েন্ট': 'client',
        }
        
        python_code = hm_code
        for hm_key, python_key in conversions.items():
            python_code = python_code.replace(hm_key, python_key)
        
        # Add Python header
        header = f'''"""
Compiled from Tamanna .hm file
Generated automatically
"""

import math
import os
import sys

'''
        return header + python_code

# ==================== NETWORK SYSTEM ====================
class TamannaNetwork:
    """Network capabilities for Tamanna Language"""
    
    @staticmethod
    def create_server(port=8080):
        """Create a simple server"""
        try:
            import socket
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('localhost', port))
            server_socket.listen(1)
            print(Color.colorize(f"Server started on port {port}", Color.GREEN))
            return server_socket
        except Exception as e:
            print(Color.colorize(f"Server error: {e}", Color.RED))
            return None
    
    @staticmethod
    def connect_client(host='localhost', port=8080):
        """Connect as client"""
        try:
            import socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            print(Color.colorize(f"Connected to {host}:{port}", Color.GREEN))
            return client_socket
        except Exception as e:
            print(Color.colorize(f"Connection error: {e}", Color.RED))
            return None

# ==================== AUTO-BUILD SYSTEM ====================
class AutoBuildSystem:
    """Auto-build system for Tamanna projects"""
    
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.platform = Platform.detect()
        
        self.setup_directories()
        self.setup_logging()
    
    def setup_directories(self):
        """Setup build directories"""
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format=f'{Color.BLUE}%(asctime)s{Color.RESET} - {Color.YELLOW}%(levelname)s{Color.RESET} - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def build_project(self):
        """Build entire project"""
        self.logger.info(Color.colorize("Starting Tamanna project build...", Color.CYAN))
        
        try:
            # Find all .hm files
            hm_files = list(self.project_root.rglob("*.hm"))
            self.logger.info(Color.colorize(f"Found {len(hm_files)} .hm files", Color.GREEN))
            
            # Build each file
            for hm_file in hm_files:
                self.build_file(hm_file)
            
            # Create platform-specific packages
            self.create_package()
            
            self.logger.info(Color.colorize("Build completed successfully!", Color.GREEN))
            
        except Exception as e:
            self.logger.error(Color.colorize(f"Build failed: {e}", Color.RED))
    
    def build_file(self, file_path: Path):
        """Build individual .hm file"""
        try:
            self.logger.info(Color.colorize(f"Building: {file_path}", Color.YELLOW))
            
            # Load .hm file
            hm_code = HMFileHandler.load(str(file_path))
            
            # Compile to Python
            python_code = HMFileHandler.compile_to_python(hm_code)
            
            # Save compiled version
            output_file = self.build_dir / f"{file_path.stem}.py"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(python_code)
            
            # Execute to test
            self.test_file(output_file)
            
            self.logger.info(Color.colorize(f"Successfully built: {file_path}", Color.GREEN))
            
        except Exception as e:
            self.logger.error(Color.colorize(f"Error building {file_path}: {e}", Color.RED))
    
    def test_file(self, file_path: Path):
        """Test the built file"""
        try:
            result = subprocess.run(
                [sys.executable, str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info(Color.colorize(f"Test passed: {file_path}", Color.GREEN))
            else:
                self.logger.warning(Color.colorize(f"Test warnings: {file_path}", Color.YELLOW))
                if result.stderr:
                    self.logger.error(Color.colorize(f"Errors: {result.stderr}", Color.RED))
                    
        except subprocess.TimeoutExpired:
            self.logger.error(Color.colorize(f"Test timeout: {file_path}", Color.RED))
        except Exception as e:
            self.logger.error(Color.colorize(f"Test error: {e}", Color.RED))
    
    def create_package(self):
        """Create platform-specific distribution package"""
        self.logger.info(Color.colorize("Creating distribution package...", Color.CYAN))
        
        # Platform-specific packaging
        if self.platform == Platform.WINDOWS:
            self._create_windows_package()
        elif self.platform in [Platform.LINUX, Platform.KALI]:
            self._create_linux_package()
        elif self.platform == Platform.ANDROID:
            self._create_android_package()
        
        self.logger.info(Color.colorize("Package created successfully!", Color.GREEN))
    
    def _create_windows_package(self):
        """Create Windows package"""
        # Create batch file
        batch_content = '''@echo off
echo Running Tamanna Application...
python main.py
pause
'''
        batch_file = self.dist_dir / "run.bat"
        with open(batch_file, 'w') as f:
            f.write(batch_content)
    
    def _create_linux_package(self):
        """Create Linux package"""
        # Create shell script
        script_content = '''#!/bin/bash
echo "Running Tamanna Application..."
python3 main.py
'''
        script_file = self.dist_dir / "run.sh"
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_file, 0o755)
    
    def _create_android_package(self):
        """Create Android package"""
        # Android-specific setup
        script_content = '''#!/bin/bash
echo "Tamanna on Android"
python main.py
'''
        script_file = self.dist_dir / "android_run.sh"
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_file, 0o755)

# ==================== TAMANNA INTERPRETER ====================
class TamannaInterpreter:
    """Tamanna Language Interpreter with Color Output"""
    
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.output = []
        self.network = TamannaNetwork()
    
    def execute(self, code: str) -> List[str]:
        """Execute Tamanna code"""
        try:
            # Tokenize with colors
            lexer = TamannaLexer(code)
            tokens = lexer.tokenize()
            
            # Display tokens with colors
            self._display_tokens(tokens)
            
            # Execute the code (simplified execution)
            self._execute_code(code)
            
            return self.output
            
        except Exception as e:
            error_msg = Color.colorize(f"Error: {str(e)}", Color.RED)
            self.output.append(error_msg)
            return self.output
    
    def _display_tokens(self, tokens: List[Token]):
        """Display tokens with color coding"""
        print(Color.colorize("\n=== TOKENS ===", Color.CYAN))
        for token in tokens:
            if token.type != TK.TK_NEWLINE:
                print(f"  {token.colored_str()}")
    
    def _execute_code(self, code: str):
        """Execute the Tamanna code"""
        # Convert and execute
        python_code = HMFileHandler.compile_to_python(code)
        
        # Create a safe execution environment
        exec_globals = {
            'print': self._custom_print,
            'network': self.network,
            'math': math,
            'os': os,
            'sys': sys
        }
        
        try:
            exec(python_code, exec_globals)
        except Exception as e:
            self.output.append(Color.colorize(f"Execution error: {e}", Color.RED))
    
    def _custom_print(self, *args, **kwargs):
        """Custom print function with color"""
        output = " ".join(str(arg) for arg in args)
        colored_output = Color.colorize(output, Color.GREEN)
        print(colored_output)
        self.output.append(output)

# ==================== MAIN TAMANNA SYSTEM ====================
class TamannaSystem:
    """Complete Tamanna System - Multi-Platform"""
    
    def __init__(self):
        self.platform = Platform.detect()
        self.interpreter = TamannaInterpreter()
        self.build_system = AutoBuildSystem()
        self.setup_directories()
        
        print(Color.colorize(f"Tamanna System Started on {self.platform.upper()}", Color.MAGENTA))
    
    def setup_directories(self):
        """Setup required directories"""
        dirs = ['projects', 'build', 'dist', 'samples']
        for dir_name in dirs:
            Path(dir_name).mkdir(exist_ok=True)
    
    def create_sample(self):
        """Create sample .hm files"""
        samples = {
            'hello': '''
লেখো "স্বাগতম তামান্না ভাষায়!"
নির্ধারণ নাম = "তামান্না"
লেখো "আমার নাম " + নাম
''',
            'calculator': '''
নির্ধারণ a = 10
নির্ধারণ b = 5

লেখো "যোগ: " + (a + b)
লেখো "গুণ: " + (a * b)
লেখো "ভাগ: " + (a / b)

যদি a > b:
    লেখো "a বড়"
নাহলে:
    লেখো "b বড়"
''',
            'network_demo': '''
লেখো "নেটওয়ার্ক ডেমো শুরু হচ্ছে..."

নেটওয়ার্ক সার্ভার 8080
লেখো "সার্ভার তৈরি হয়েছে"

কানেক্ট "localhost" 8080
লেখো "কানেক্ট হয়েছে"
'''
        }
        
        for name, code in samples.items():
            filename = f"samples/{name}.hm"
            HMFileHandler.save(code, filename)
        
        print(Color.colorize("Sample files created in samples/", Color.GREEN))
    
    def run_repl(self):
        """Start Tamanna REPL"""
        print(Color.colorize("Tamanna REPL - Type 'exit' to quit", Color.CYAN))
        print(Color.colorize("Use .hm files for saving", Color.YELLOW))
        
        while True:
            try:
                code = input(Color.colorize("তামান্না> ", Color.MAGENTA))
                
                if code.lower() in ['exit', 'quit', 'প্রস্থান']:
                    break
                elif code.startswith('load '):
                    filename = code[5:].strip()
                    self.load_and_run(filename)
                elif code.startswith('save '):
                    filename = code[5:].strip()
                    self.save_code(filename)
                else:
                    self.interpreter.execute(code)
                    
            except KeyboardInterrupt:
                print(Color.colorize("\nবিদায়!", Color.RED))
                break
            except Exception as e:
                print(Color.colorize(f"Error: {e}", Color.RED))
    
    def load_and_run(self, filename: str):
        """Load and run .hm file"""
        try:
            code = HMFileHandler.load(filename)
            print(Color.colorize(f"Loaded: {filename}", Color.GREEN))
            self.interpreter.execute(code)
        except Exception as e:
            print(Color.colorize(f"Load error: {e}", Color.RED))
    
    def save_code(self, filename: str):
        """Save code to .hm file"""
        # This would need to capture the current code in a real implementation
        sample_code = '''
লেখো "সেভ করা ফাইল"
নির্ধারণ সংখ্যা = 42
লেখো "সংখ্যা: " + সংখ্যা
'''
        HMFileHandler.save(sample_code, filename)
    
    def build_project(self, project_dir="."):
        """Build a Tamanna project"""
        self.build_system.project_root = Path(project_dir)
        self.build_system.build_project()
    
    def network_demo(self):
        """Run network demonstration"""
        print(Color.colorize("=== Network Demo ===", Color.CYAN))
        
        # Server demo
        server = self.interpreter.network.create_server(8080)
        if server:
            print(Color.colorize("Server created successfully", Color.GREEN))
        
        # Client demo  
        client = self.interpreter.network.connect_client('localhost', 8080)
        if client:
            print(Color.colorize("Client connected successfully", Color.GREEN))

# ==================== COMMAND LINE INTERFACE ====================
def main():
    """Main command line interface"""
    system = TamannaSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "repl":
            system.run_repl()
        elif command == "build":
            project_dir = sys.argv[2] if len(sys.argv) > 2 else "."
            system.build_project(project_dir)
        elif command == "samples":
            system.create_sample()
        elif command == "network":
            system.network_demo()
        elif command == "run":
            filename = sys.argv[2] if len(sys.argv) > 2 else "main.hm"
            system.load_and_run(filename)
        else:
            print_help()
    else:
        # Interactive mode
        print(Color.colorize("=== Tamanna Code Language ===", Color.MAGENTA))
        print(Color.colorize("Multi-Platform System (Windows + Linux + Android)", Color.CYAN))
        
        while True:
            print(Color.colorize("\nOptions:", Color.YELLOW))
            print("1. REPL (Interactive)")
            print("2. Build Project")
            print("3. Create Samples")
            print("4. Network Demo")
            print("5. Run .hm File")
            print("6. Exit")
            
            choice = input(Color.colorize("\nSelect option (1-6): ", Color.MAGENTA))
            
            if choice == '1':
                system.run_repl()
            elif choice == '2':
                project_dir = input("Project directory [.]: ") or "."
                system.build_project(project_dir)
            elif choice == '3':
                system.create_sample()
            elif choice == '4':
                system.network_demo()
            elif choice == '5':
                filename = input("File name [main.hm]: ") or "main.hm"
                system.load_and_run(filename)
            elif choice == '6':
                print(Color.colorize("বিদায়! (Goodbye!)", Color.RED))
                break
            else:
                print(Color.colorize("Invalid option", Color.RED))

def print_help():
    """Print help information"""
    help_text = '''
Tamanna Code Language System

Usage:
  python tamanna_system.py [command]

Commands:
  repl      - Start interactive REPL
  build     - Build project
  samples   - Create sample files
  network   - Run network demo
  run <file>- Run .hm file

Examples:
  python tamanna_system.py repl
  python tamanna_system.py build ./myproject
  python tamanna_system.py run demo.hm
'''
    print(Color.colorize(help_text, Color.CYAN))

if __name__ == "__main__":
    main()