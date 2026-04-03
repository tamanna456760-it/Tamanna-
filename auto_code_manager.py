#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
অটোমেটিক কোড ম্যানেজমেন্ট সিস্টেম
- অটো সেভ
- অটো ফিক্স  
- অটো রাইট
- গিটহাব সিঙ্ক
"""

import os
import sys
import subprocess
import json
import re
from datetime import datetime
from pathlib import Path

class AutoCodeManager:
    def __init__(self):
        self.home = str(Path.home())
        self.repo_path = os.path.join(self.home, "my_ai_codes")
        self.errors_log = os.path.join(self.repo_path, "errors_log.json")
        self.fixes_log = os.path.join(self.repo_path, "fixes_log.json")
        self.github_url = None
        
    def setup_github(self):
        """গিটহাব সেটআপ"""
        print("\n📦 গিটহাব সেটআপ...")
        
        # গিট কনফিগার
        name = input("আপনার গিটহাব ইউজারনেম: ")
        email = input("আপনার গিটহাব ইমেইল: ")
        
        subprocess.run(["git", "config", "--global", "user.name", tamanna456760-it])
        subprocess.run(["git", "config", "--global", "user.email", tamanna456760@gmail.com])
        
        repo_name = input("রিপোজিটরির নাম (enter = my_ai_codes): ")
        if not repo_name:
            repo_name = "my_ai_codes"
            
        self.github_url = f"https://github.com/{tamanna456760-it}/{tamanna-}.git"
        
        # রিপোজিটরি তৈরি
        if not os.path.exists(self.repo_path):
            os.makedirs(self.repo_path)
            subprocess.run(["git", "init"], cwd=self.repo_path)
            
            # রিমোট অ্যাড
            subprocess.run(["git", "remote", "add", "origin", self.github_url], cwd=self.repo_path)
            
            print(f"\n✅ সেটআপ সম্পন্ন!")
            print(f"👉 গিটহাবে নতুন রিপোজিটরি তৈরি করুন: {self.github_url}")
            input("\nরিপোজিটরি তৈরি করে এন্টার প্রেস করুন...")
    
    def save_code(self, filename, code, description=""):
        """কোড সেভ করা"""
        filepath = os.path.join(self.repo_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {description}\n")
            f.write(f"# সেভ করা হয়েছে: {datetime.now()}\n")
            f.write(f"# {'='*50}\n\n")
            f.write(code)
        
        print(f"✅ কোড সেভ করা হয়েছে: {filename}")
        self._git_commit(f"সেভ: {filename} - {description}")
        return filepath
    
    def auto_fix_code(self, filepath):
        """অটো এরর ফিক্স"""
        print(f"\n🔧 ফিক্সিং: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        
        fixed_code = code
        fixes_applied = []
        
        # কমন এরর ফিক্স
        fixes = [
            (r'print\s*(.+?)\n', r'print(\1)\n'),  # পাইথন 2 প্রিন্ট
            (r'except\s*:\s*\n', r'except Exception as e:\n    pass\n'),  # ব্লাঙ্ক এক্সেপ্ট
            (r'=\s*=\s*', r'=='),  # এসাইনমেন্ট এরর
            (r'(\w+)\s*\+\s*(\w+)', r'str(\1) + str(\2)'),  # টাইপ কনভার্শন
        ]
        
        for pattern, replacement in fixes:
            if re.search(pattern, fixed_code):
                fixed_code = re.sub(pattern, replacement, fixed_code)
                fixes_applied.append(pattern)
        
        if fixed_code != code:
            backup = filepath + ".backup"
            with open(backup, 'w', encoding='utf-8') as f:
                f.write(code)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            
            print(f"✅ {len(fixes_applied)} টি এরর ফিক্স করা হয়েছে")
            self._log_fix(filepath, fixes_applied)
            return True
        else:
            print("✅ কোন এরর নেই")
            return False
    
    def auto_write_code(self, prompt):
        """AI দিয়ে অটো কোড লেখা"""
        print(f"\n🤖 কোড জেনারেট করা হচ্ছে: {prompt}")
        
        # বেসিক কোড টেম্পলেট
        templates = {
            "web scraper": '''
import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

url = input("URL দিন: ")
data = scrape_website(url)
print("স্ক্র্যাপিং সম্পন্ন!")
''',
            "api": '''
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello World", "status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
''',
            "automation": '''
import os
import time

def auto_task():
    print("অটোমেশন শুরু...")
    # আপনার কোড এখানে লিখুন
    for i in range(10):
        print(f"Task {i+1} সম্পন্ন")
        time.sleep(1)

if __name__ == "__main__":
    auto_task()
'''
        }
        
        for keyword, template in templates.items():
            if keyword in prompt.lower():
                return template
        
        # ডিফল্ট টেম্পলেট
        return f'''
# {prompt}
# অটো জেনারেটেড কোড
# সময়: {datetime.now()}

def main():
    print("প্রোগ্রাম শুরু...")
    # আপনার কোড এখানে লিখুন
    pass

if __name__ == "__main__":
    main()
'''
    
    def _git_commit(self, message):
        """গিট কমিট"""
        try:
            subprocess.run(["git", "add", "."], cwd=self.repo_path, capture_output=True)
            subprocess.run(["git", "commit", "-m", message], cwd=self.repo_path, capture_output=True)
            subprocess.run(["git", "push", "-u", "origin", "main"], cwd=self.repo_path, capture_output=True)
            print(f"✅ গিটহাবে আপলোড: {message}")
        except:
            print("⚠️ গিট পুশ ব্যর্থ (হাতে পুশ করুন)")
    
    def _log_fix(self, filepath, fixes):
        """ফিক্স লগ"""
        log = {
            "file": filepath,
            "time": str(datetime.now()),
            "fixes": fixes
        }
        
        if os.path.exists(self.fixes_log):
            with open(self.fixes_log, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log)
        with open(self.fixes_log, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def scan_and_fix_all(self):
        """সব কোড স্ক্যান ও ফিক্স"""
        print("\n🔍 সব কোড ফাইলের জন্য স্ক্যান চলছে...")
        
        fixed_files = []
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith(('.py', '.js', '.sh', '.html', '.css')):
                    filepath = os.path.join(root, file)
                    if self.auto_fix_code(filepath):
                        fixed_files.append(file)
        
        print(f"\n✅ {len(fixed_files)} টি ফাইল ফিক্স করা হয়েছে")
        return fixed_files
    
    def run(self):
        """মেইন মেনু"""
        while True:
            print("\n" + "="*50)
            print("🤖 অটো কোড ম্যানেজার")
            print("="*50)
            print("1. নতুন কোড সেভ করুন")
            print("2. গিটহাবে আপলোড করুন")
            print("3. অটো এরর ফিক্স")
            print("4. AI দিয়ে কোড লিখুন")
            print("5. সব ফাইল স্ক্যান করুন")
            print("6. এক্সিট")
            
            choice = input("\nআপনার choice (1-6): ")
            
            if choice == "1":
                name = input("ফাইলের নাম (যেমন: my_code.py): ")
                print("কোড লিখুন (শেষে ctrl+D দিন):")
                lines = []
                try:
                    while True:
                        line = input()
                        lines.append(line)
                except EOFError:
                    pass
                code = "\n".join(lines)
                desc = input("বিবরণ (অপশনাল): ")
                self.save_code(name, code, desc)
                
            elif choice == "2":
                self._git_commit("ম্যানুয়াল আপলোড")
                
            elif choice == "3":
                file = input("ফাইলের পাথ দিন: ")
                if os.path.exists(file):
                    self.auto_fix_code(file)
                else:
                    print("❌ ফাইল পাওয়া যায়নি")
                    
            elif choice == "4":
                prompt = input("কী ধরনের কোড চান? (web scraper/api/automation): ")
                code = self.auto_write_code(prompt)
                print("\n" + "="*50)
                print(code)
                print("="*50)
                save = input("সেভ করবেন? (y/n): ")
                if save.lower() == 'y':
                    name = input("ফাইলের নাম: ")
                    self.save_code(name, code, prompt)
                    
            elif choice == "5":
                self.scan_and_fix_all()
                
            elif choice == "6":
                print("👋 বাই-বাই!")
                break

if __name__ == "__main__":
    manager = AutoCodeManager()
    manager.setup_github()
    manager.run()