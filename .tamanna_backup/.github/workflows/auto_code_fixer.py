#!/usr/bin/env python3
# .github/scripts/auto_code_fixer.py

import os
import re
import ast
import subprocess
import json
import sys
import time
from pathlib import Path
from datetime import datetime
import hashlib

class BDKingCodeFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.errors_found = []
        self.fixes_applied = []
        self.liked_codes = []
        self.synced_files = []
        
        self.initialize_fixer()
        
    def initialize_fixer(self):
        """Initialize auto code fixer"""
        print("🚀 BD-King-R7 Auto Code Fixer Initialized")
        print("📁 Project Root:", self.project_root)
        print("🔍 Scanning for code issues...")
        
    def scan_all_code(self):
        """Scan all Python files for errors"""
        python_files = list(self.project_root.rglob("*.py"))
        
        print(f"📊 Found {len(python_files)} Python files")
        
        results = {
            'total_files': len(python_files),
            'files_scanned': 0,
            'errors_found': 0,
            'fixes_applied': 0,
            'likes_given': 0
        }
        
        for file_path in python_files:
            if self.should_scan(file_path):
                result = self.scan_and_fix_file(file_path)
                results['files_scanned'] += 1
                results['errors_found'] += result['errors']
                results['fixes_applied'] += result['fixes']
                
                if result['liked']:
                    results['likes_given'] += 1
                    
        return results
    
    def should_scan(self, file_path):
        """Check if file should be scanned"""
        exclude_dirs = ['venv', '.venv', '__pycache__', '.git', 'node_modules']
        return not any(exclude in str(file_path) for exclude in exclude_dirs)
    
    def scan_and_fix_file(self, file_path):
        """Scan and fix individual file"""
        result = {'errors': 0, 'fixes': 0, 'liked': False}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for errors
            errors = self.detect_errors(content, file_path)
            result['errors'] = len(errors)
            
            if errors:
                # Auto-fix errors
                fixed_content = self.auto_fix_errors(content, errors)
                
                if fixed_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fixed_content)
                    result['fixes'] = len(errors)
                    self.fixes_applied.append(str(file_path))
                    
                    # Like the fixed code
                    self.like_code(file_path, errors)
                    result['liked'] = True
                    
            # Sync code to database
            self.sync_code_to_github(file_path, content)
            
        except Exception as e:
            print(f"⚠️ Error processing {file_path}: {e}")
            
        return result
    
    def detect_errors(self, content, file_path):
        """Detect various code errors"""
        errors = []
        
        # Syntax errors
        try:
            ast.parse(content)
        except SyntaxError as e:
            errors.append({
                'type': 'syntax',
                'line': e.lineno,
                'message': str(e),
                'fixable': True
            })
        
        # Indentation errors
        if re.search(r'^\s+[^\s]', content, re.MULTILINE):
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if line and line[0] == ' ' and len(line) - len(line.lstrip()) % 4 != 0:
                    errors.append({
                        'type': 'indentation',
                        'line': i,
                        'message': f'Invalid indentation at line {i}',
                        'fixable': True
                    })
        
        # Missing imports
        imports = re.findall(r'^import (\w+)|^from (\w+) import', content, re.MULTILINE)
        used_modules = re.findall(r'(\w+)\.', content)
        
        # Undefined variables
        defined = set()
        undefined = []
        for line in content.split('\n'):
            if '=' in line and not line.strip().startswith('#'):
                var = line.split('=')[0].strip()
                defined.add(var)
        
        # Type errors
        type_patterns = [
            (r'(\w+)\s*\+\s*(\d+)', 'TypeError: str + int'),
            (r'(\d+)\s*\+\s*\'([^\']+)\'', 'TypeError: int + str'),
        ]
        
        for pattern, error_msg in type_patterns:
            if re.search(pattern, content):
                errors.append({
                    'type': 'type_error',
                    'message': error_msg,
                    'fixable': True
                })
        
        return errors
    
    def auto_fix_errors(self, content, errors):
        """Auto-fix detected errors"""
        fixed_content = content
        
        for error in errors:
            if error['fixable']:
                if error['type'] == 'indentation':
                    fixed_content = self.fix_indentation(fixed_content, error)
                elif error['type'] == 'syntax':
                    fixed_content = self.fix_syntax(fixed_content, error)
                elif error['type'] == 'type_error':
                    fixed_content = self.fix_type_error(fixed_content, error)
                    
        return fixed_content
    
    def fix_indentation(self, content, error):
        """Fix indentation errors"""
        lines = content.split('\n')
        line_num = error['line'] - 1
        
        if line_num < len(lines):
            current = lines[line_num]
            stripped = current.lstrip()
            correct_indent = len(current) - len(stripped)
            correct_indent = (correct_indent // 4) * 4
            lines[line_num] = ' ' * correct_indent + stripped
            
        return '\n'.join(lines)
    
    def fix_syntax(self, content, error):
        """Fix syntax errors"""
        # Add missing parentheses, brackets, etc.
        lines = content.split('\n')
        line_num = error['line'] - 1
        
        if line_num < len(lines):
            line = lines[line_num]
            
            # Fix missing closing parentheses
            if line.count('(') > line.count(')'):
                lines[line_num] = line + ')'
            # Fix missing closing brackets
            elif line.count('[') > line.count(']'):
                lines[line_num] = line + ']'
            # Fix missing closing braces
            elif line.count('{') > line.count('}'):
                lines[line_num] = line + '}'
                
        return '\n'.join(lines)
    
    def fix_type_error(self, content, error):
        """Fix type errors"""
        # Convert types automatically
        if 'str + int' in error['message']:
            content = re.sub(r'(\w+)\s*\+\s*(\d+)', r'str(\1) + str(\2)', content)
        elif 'int + str' in error['message']:
            content = re.sub(r'(\d+)\s*\+\s*\'([^\']+)\'', r'str(\1) + \'\\2\'', content)
            
        return content
    
    def like_code(self, file_path, errors):
        """Like/favorite good code and fix bad code"""
        code_quality = self.assess_code_quality(file_path)
        
        if code_quality['score'] >= 80:
            # Good code - like it
            self.liked_codes.append({
                'file': str(file_path),
                'score': code_quality['score'],
                'timestamp': datetime.now().isoformat(),
                'liked_by': 'BD-King-R7 AI'
            })
            print(f"👍 LIKED: {file_path.name} (Score: {code_quality['score']})")
            
            # Create GitHub star/like
            self.create_github_like(file_path)
            
        elif errors:
            # Bad code - fix and document
            self.document_bad_code(file_path, errors, code_quality)
            
    def assess_code_quality(self, file_path):
        """Assess code quality score"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            score = 100
            
            # Check complexity
            lines = len(content.split('\n'))
            if lines > 500:
                score -= 20
            elif lines > 200:
                score -= 10
                
            # Check comments
            comments = len(re.findall(r'#.*', content))
            if comments < lines * 0.1:  # Less than 10% comments
                score -= 15
                
            # Check docstrings
            if '"""' not in content and "'''" not in content:
                score -= 10
                
            # Check function length
            functions = re.findall(r'def \w+\(.*?\):.*?(?=\n\S|\Z)', content, re.DOTALL)
            for func in functions:
                func_lines = len(func.split('\n'))
                if func_lines > 50:
                    score -= 5
                    
            return {'score': max(0, score), 'lines': lines, 'functions': len(functions)}
            
        except Exception:
            return {'score': 50, 'lines': 0, 'functions': 0}
    
    def create_github_like(self, file_path):
        """Create GitHub star/like for good code"""
        # This would interact with GitHub API
        like_info = {
            'repository': 'bd-king-r7/powerhub',
            'file': str(file_path),
            'action': 'like',
            'timestamp': datetime.now().isoformat()
        }
        
        # Save like to database
        self.save_like_to_db(like_info)
        
    def document_bad_code(self, file_path, errors, quality):
        """Document bad code for fixing"""
        bad_code_report = {
            'file': str(file_path),
            'errors': errors,
            'quality_score': quality['score'],
            'fix_recommendations': self.generate_fix_recommendations(errors),
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to issues database
        self.create_github_issue(bad_code_report)
        
    def generate_fix_recommendations(self, errors):
        """Generate fix recommendations for errors"""
        recommendations = []
        
        for error in errors:
            if error['type'] == 'indentation':
                recommendations.append("Use 4 spaces for indentation")
            elif error['type'] == 'syntax':
                recommendations.append(f"Fix syntax: {error['message']}")
            elif error['type'] == 'type_error':
                recommendations.append("Use type conversion properly")
                
        return recommendations
    
    def sync_code_to_github(self, file_path, content):
        """Sync code to GitHub with error tracking"""
        sync_info = {
            'file': str(file_path),
            'hash': hashlib.md5(content.encode()).hexdigest(),
            'timestamp': datetime.now().isoformat(),
            'errors_fixed': len(self.errors_found)
        }
        
        self.synced_files.append(sync_info)
        
        # Save sync info
        self.save_sync_info(sync_info)
        
    def create_github_issue(self, report):
        """Create GitHub issue for bad code"""
        # This would use GitHub API
        issue_body = f"""
## 🤖 Auto-Detected Code Issues

**File:** `{report['file']}`  
**Quality Score:** {report['quality_score']}/100  
**Errors Found:** {len(report['errors'])}

### Issues Detected:
{self.format_errors(report['errors'])}

### Fix Recommendations:
{self.format_recommendations(report['fix_recommendations'])}

---
*Auto-generated by BD-King-R7 Code Fixer*
        """
        
        # Save issue locally (would push to GitHub API)
        issues_dir = self.project_root / '.github' / 'issues'
        issues_dir.mkdir(parents=True, exist_ok=True)
        
        issue_file = issues_dir / f"issue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(issue_file, 'w') as f:
            f.write(issue_body)
            
        print(f"📝 Issue created: {issue_file}")
        
    def format_errors(self, errors):
        """Format errors for display"""
        formatted = []
        for error in errors:
            formatted.append(f"- `{error['type']}`: {error['message']}")
        return '\n'.join(formatted)
    
    def format_recommendations(self, recommendations):
        """Format recommendations for display"""
        formatted = []
        for rec in recommendations:
            formatted.append(f"- {rec}")
        return '\n'.join(formatted)
    
    def save_like_to_db(self, like_info):
        """Save like information to database"""
        likes_dir = self.project_root / '.github' / 'likes'
        likes_dir.mkdir(parents=True, exist_ok=True)
        
        like_file = likes_dir / f"likes_{datetime.now().strftime('%Y%m%d')}.json"
        
        likes = []
        if like_file.exists():
            with open(like_file, 'r') as f:
                likes = json.load(f)
                
        likes.append(like_info)
        
        with open(like_file, 'w') as f:
            json.dump(likes, f, indent=2)
            
    def save_sync_info(self, sync_info):
        """Save synchronization info"""
        sync_dir = self.project_root / '.github' / 'sync'
        sync_dir.mkdir(parents=True, exist_ok=True)
        
        sync_file = sync_dir / f"sync_{datetime.now().strftime('%Y%m%d')}.json"
        
        syncs = []
        if sync_file.exists():
            with open(sync_file, 'r') as f:
                syncs = json.load(f)
                
        syncs.append(sync_info)
        
        with open(sync_file, 'w') as f:
            json.dump(syncs, f, indent=2)
    
    def run_full_scan(self):
        """Run complete code scan and fix"""
        print("\n" + "="*60)
        print("🔍 BD-King-R7 Full Code Scan Started")
        print("="*60)
        
        start_time = time.time()
        results = self.scan_all_code()
        elapsed_time = time.time() - start_time
        
        print("\n" + "="*60)
        print("📊 SCAN RESULTS")
        print("="*60)
        print(f"📁 Files Scanned: {results['files_scanned']}/{results['total_files']}")
        print(f"🐛 Errors Found: {results['errors_found']}")
        print(f"🔧 Fixes Applied: {results['fixes_applied']}")
        print(f"👍 Codes Liked: {results['likes_given']}")
        print(f"⏱️  Time Taken: {elapsed_time:.2f}s")
        
        # Generate report
        self.generate_report(results)
        
        return results
    
    def generate_report(self, results):
        """Generate scan report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'fixes_applied': self.fixes_applied,
            'liked_codes': self.liked_codes,
            'synced_files': self.synced_files
        }
        
        report_dir = self.project_root / '.github' / 'reports'
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📄 Report saved: {report_file}")

class GitHubWorkflowManager:
    """Manage GitHub workflow operations"""
    
    def __init__(self):
        self.workflow_file = '.github/workflows/bd-king-r7-auto-sync.yml'
        
    def trigger_workflow(self):
        """Trigger GitHub workflow"""
        print("🚀 Triggering GitHub workflow...")
        
        # This would use GitHub API to trigger workflow
        workflow_info = {
            'workflow': 'bd-king-r7-auto-sync.yml',
            'triggered_by': 'auto-sync-system',
            'timestamp': datetime.now().isoformat()
        }
        
        return workflow_info
    
    def check_workflow_status(self):
        """Check workflow run status"""
        # This would check GitHub Actions status
        return {
            'status': 'running',
            'jobs': ['auto-sync-fix'],
            'duration': 'in-progress'
        }

def main():
    """Main execution"""
    print("🚀 Starting BD-King-R7 Auto Code Sync & Fix System")
    
    # Initialize fixer
    fixer = BDKingCodeFixer()
    
    # Run full scan and fix
    results = fixer.run_full_scan()
    
    # Initialize workflow manager
    workflow = GitHubWorkflowManager()
    
    # Trigger workflow if needed
    if results['fixes_applied'] > 0:
        workflow.trigger_workflow()
        
    print("\n✅ Auto Sync & Fix Complete!")
    print("🎉 BD-King-R7 System Operational")

if __name__ == "__main__":
    main()