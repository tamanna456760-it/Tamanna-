import json
import os

LANGUAGES = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.html': 'HTML',
    '.css': 'CSS',
    '.java': 'Java',
    '.c': 'C',
    '.cpp': 'C++',
    '.cs': 'C#',
    '.rb': 'Ruby',
    '.php': 'PHP',
    # অন্যান্য ভাষা যুক্ত করতে পারো
}

def analyze_files_in_directory(directory):
    issues = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1]
            language = LANGUAGES.get(ext, 'Unknown')
            try:
                with open(file_path, 'r', errors='ignore') as f:
                    code = f.read()
                    lines = code.split('\n')
                    
                    # সাধারণ লিন্টিং ইস্যু ধরার উদাহরণ
                    if 'console.log' in code and language != 'JavaScript':
                        issues.append({
                            'file': file_path,
                            'type': 'Unexpected console.log',
                            'language': language,
                            'details': 'console.log found in non-JS file'
                        })
                    # আরও সাধারণ ইস্যু ধরার জন্য তুমি লজিক যোগ করতে পারো, যেমন indentation, ভুল সিনট্যাক্স, ইত্যাদি
                    
            except Exception as e:
                issues.append({
                    'file': file_path,
                    'type': 'Read error',
                    'language': language,
                    'details': str(e)
                })
    
    with open('issues.json', 'w') as f:
        json.dump(issues, f, indent=4)

if __name__ == "__main__":
    directory_to_scan = '.'  # বর্তমান ডিরেক্টরি
    analyze_files_in_directory(directory_to_scan)