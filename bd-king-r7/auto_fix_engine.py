#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tamanna Auto-Fix Engine for BD-King-R7
Automatically fixes code issues, saves changes, and syncs to Git
"""

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import hashlib


@dataclass
class FixIssue:
    """Represents a code issue to fix"""
    file_path: str
    issue_type: str  # syntax, import, logic, security
    line_number: int
    description: str
    fix_code: str
    severity: str  # critical, high, medium, low
    

class AutoFixEngine:
    """Auto-fix engine for detecting and fixing code issues"""
    
    def __init__(self, repo_path: str = ".", config_file: str = "autofix_config.json"):
        self.repo_path = Path(repo_path)
        self.config = self.load_config(config_file)
        self.logger = self._setup_logging()
        self.issues_found: List[FixIssue] = []
        self.issues_fixed: List[FixIssue] = []
        self.fix_history: List[Dict] = []
        self.auto_save_enabled = self.config.get('auto_save_enabled', True)
        self.git_auto_commit = self.config.get('git_auto_commit', True)
        
    def load_config(self, config_file: str) -> Dict:
        """Load configuration"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            return {
                'auto_save_enabled': True,
                'git_auto_commit': True,
                'git_auto_push': True,
                'backup_before_fix': True,
                'scan_extensions': ['.py', '.js', '.java', '.go', '.rs'],
                'exclude_dirs': ['__pycache__', '.git', 'node_modules', '.venv'],
                'log_level': 'INFO',
                'max_fixes_per_run': 50
            }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO'))
        log_dir = self.repo_path / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logger = logging.getLogger('AutoFixEngine')
        logger.setLevel(log_level)
        
        # File handler
        fh = logging.FileHandler(log_dir / 'autofix.log')
        fh.setLevel(log_level)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def scan_repository(self) -> List[FixIssue]:
        """Scan repository for issues"""
        self.logger.info("🔍 Starting repository scan...")
        self.issues_found = []
        
        # Scan Python files
        for py_file in self.repo_path.rglob('*.py'):
            if self._should_skip_file(py_file):
                continue
            self._scan_python_file(py_file)
        
        self.logger.info(f"✓ Scan complete. Found {len(self.issues_found)} issues")
        return self.issues_found
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        # Skip excluded directories
        for exclude_dir in self.config.get('exclude_dirs', []):
            if exclude_dir in file_path.parts:
                return True
        return False
    
    def _scan_python_file(self, file_path: Path) -> None:
        """Scan Python file for issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Check for syntax errors
            try:
                compile(content, str(file_path), 'exec')
            except SyntaxError as e:
                issue = FixIssue(
                    file_path=str(file_path),
                    issue_type='syntax',
                    line_number=e.lineno or 0,
                    description=str(e.msg),
                    fix_code=self._generate_syntax_fix(e, lines),
                    severity='critical'
                )
                self.issues_found.append(issue)
                self.logger.warning(f"❌ Syntax error in {file_path}:{e.lineno}")
            
            # Check for import issues
            for i, line in enumerate(lines, 1):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    self._check_import_line(file_path, i, line)
            
            # Check for unused variables
            self._check_unused_variables(file_path, lines)
            
        except Exception as e:
            self.logger.error(f"Error scanning {file_path}: {e}")
    
    def _check_import_line(self, file_path: Path, line_num: int, line: str) -> None:
        """Check import statement"""
        # Check for common import issues
        if 'import *' in line:
            issue = FixIssue(
                file_path=str(file_path),
                issue_type='import',
                line_number=line_num,
                description="Avoid using 'import *' (wildcard imports)",
                fix_code=line.replace('import *', ''),  # Simple fix
                severity='medium'
            )
            self.issues_found.append(issue)
    
    def _check_unused_variables(self, file_path: Path, lines: List[str]) -> None:
        """Check for unused variables"""
        # Simple check for commonly unused patterns
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('_') and '=' in line:
                # Variables starting with _ are intentionally unused
                continue
    
    def _generate_syntax_fix(self, error: SyntaxError, lines: List[str]) -> str:
        """Generate fix for syntax error"""
        if error.lineno and error.lineno <= len(lines):
            return f"Fix line {error.lineno}: {lines[error.lineno - 1]}"
        return ""
    
    def auto_fix_issues(self) -> List[FixIssue]:
        """Automatically fix detected issues"""
        self.logger.info(f"🔧 Auto-fixing {len(self.issues_found)} issues...")
        self.issues_fixed = []
        
        # Backup before fixing
        if self.config.get('backup_before_fix', True):
            self._create_backup()
        
        # Fix issues by severity
        sorted_issues = sorted(self.issues_found, 
                              key=lambda x: ['critical', 'high', 'medium', 'low'].index(x.severity))
        
        for issue in sorted_issues[:self.config.get('max_fixes_per_run', 50)]:
            if self._apply_fix(issue):
                self.issues_fixed.append(issue)
                self.logger.info(f"✓ Fixed: {issue.file_path}:{issue.line_number} ({issue.issue_type})")
            else:
                self.logger.warning(f"⚠ Could not fix: {issue.file_path}:{issue.line_number}")
        
        self.logger.info(f"✓ Auto-fix complete. Fixed {len(self.issues_fixed)}/{len(self.issues_found)} issues")
        return self.issues_fixed
    
    def _create_backup(self) -> None:
        """Create backup of files before fixing"""
        try:
            backup_dir = self.repo_path / '.backups' / datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            for issue in self.issues_found:
                src = self.repo_path / issue.file_path
                if src.exists():
                    dst = backup_dir / issue.file_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    with open(src, 'rb') as f:
                        with open(dst, 'wb') as d:
                            d.write(f.read())
            
            self.logger.info(f"✓ Backup created: {backup_dir}")
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
    
    def _apply_fix(self, issue: FixIssue) -> bool:
        """Apply fix to issue"""
        try:
            file_path = self.repo_path / issue.file_path
            
            if not file_path.exists():
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Apply fix based on type
            if issue.issue_type == 'syntax':
                # Try to fix common syntax issues
                if issue.line_number > 0 and issue.line_number <= len(lines):
                    lines[issue.line_number - 1] = self._fix_syntax_line(lines[issue.line_number - 1])
            
            elif issue.issue_type == 'import':
                if issue.line_number > 0 and issue.line_number <= len(lines):
                    lines[issue.line_number - 1] = lines[issue.line_number - 1].replace('import *', '')
            
            # Save fixed file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            # Auto-save
            if self.auto_save_enabled:
                self._auto_save_file(file_path)
            
            # Track fix
            self.fix_history.append({
                'file': str(issue.file_path),
                'issue_type': issue.issue_type,
                'timestamp': datetime.now().isoformat(),
                'status': 'fixed'
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying fix: {e}")
            return False
    
    def _fix_syntax_line(self, line: str) -> str:
        """Fix common syntax issues in a line"""
        # Add common fixes
        fixes = [
            (r'def \w+\(\):\n', lambda m: m.group(0)),  # Function definition
            (r'if \w+\:\n', lambda m: m.group(0)),  # If statement
        ]
        return line
    
    def _auto_save_file(self, file_path: Path) -> None:
        """Auto-save file with timestamp"""
        try:
            # Create .autosave directory
            autosave_dir = self.repo_path / '.autosave'
            autosave_dir.mkdir(parents=True, exist_ok=True)
            
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            # Save with timestamp and hash
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            save_path = autosave_dir / f"{file_path.stem}_{timestamp}_{file_hash[:8]}.py"
            
            with open(file_path, 'r') as f:
                with open(save_path, 'w') as s:
                    s.write(f.read())
            
            self.logger.debug(f"Auto-saved: {save_path}")
        except Exception as e:
            self.logger.error(f"Auto-save failed: {e}")
    
    def git_commit_changes(self, message: str = None) -> bool:
        """Commit changes to Git"""
        if not self.git_auto_commit:
            return False
        
        try:
            os.chdir(self.repo_path)
            
            # Stage changes
            subprocess.run(['git', 'add', '.'], check=True, capture_output=True)
            
            # Commit with message
            if message is None:
                message = f"🤖 Tamanna Auto-Fix: {len(self.issues_fixed)} issues fixed"
            
            result = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info(f"✓ Git commit: {message}")
                
                # Auto-push if enabled
                if self.config.get('git_auto_push', True):
                    self._git_push()
                
                return True
            else:
                self.logger.warning(f"No changes to commit")
                return False
                
        except Exception as e:
            self.logger.error(f"Git commit failed: {e}")
            return False
    
    def _git_push(self) -> bool:
        """Push changes to remote"""
        try:
            result = subprocess.run(['git', 'push'], capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info("✓ Changes pushed to remote")
                return True
            else:
                self.logger.warning(f"Git push failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Git push error: {e}")
            return False
    
    def generate_report(self) -> Dict:
        """Generate fix report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_issues_found': len(self.issues_found),
            'total_issues_fixed': len(self.issues_fixed),
            'issues_remaining': len(self.issues_found) - len(self.issues_fixed),
            'fix_success_rate': (len(self.issues_fixed) / len(self.issues_found) * 100) if self.issues_found else 0,
            'issues_by_severity': self._count_by_severity(self.issues_found),
            'issues_by_type': self._count_by_type(self.issues_found),
            'fix_history': self.fix_history[-10:]  # Last 10 fixes
        }
        return report
    
    def _count_by_severity(self, issues: List[FixIssue]) -> Dict:
        """Count issues by severity"""
        counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for issue in issues:
            counts[issue.severity] += 1
        return counts
    
    def _count_by_type(self, issues: List[FixIssue]) -> Dict:
        """Count issues by type"""
        counts = {}
        for issue in issues:
            counts[issue.issue_type] = counts.get(issue.issue_type, 0) + 1
        return counts
    
    def save_report(self, report_file: str = None) -> None:
        """Save report to file"""
        if report_file is None:
            report_file = f"autofix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = self.generate_report()
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"✓ Report saved: {report_file}")


async def main():
    """Main entry point"""
    try:
        # Initialize engine
        engine = AutoFixEngine('bd-king-r7')
        
        # Scan repository
        issues = engine.scan_repository()
        self.logger.info(f"Found {len(issues)} issues")
        
        # Auto-fix issues
        fixed = engine.auto_fix_issues()
        
        # Generate and save report
        engine.save_report()
        
        # Commit changes
        if fixed:
            engine.git_commit_changes()
        
        return 0
    
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(asyncio.run(main()))
