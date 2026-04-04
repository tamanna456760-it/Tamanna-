# 🤖 AI Auto System Runner

এই প্রজেক্টটি একটি সম্পূর্ণ **AI-powered automation system**, যা GitHub repository এর কোডগুলোকে:

- 🔍 Scan করে (Error/Issue detect)
- 🛠 Auto Fix করে
- 🧠 AI System Monitor করে
- 🔄 প্রতি নির্দিষ্ট সময় পর পর auto run করে

---

## ⚙️ System Architecture

এই সিস্টেমে ৩টি মূল Python স্ক্রিপ্ট আছে:

### 1️⃣ lint_detect_issues.py
📌 কাজ:
- সব ফাইল scan করে
- error, missing code, duplicate code detect করে
- report তৈরি করে

---

### 2️⃣ auto_fix_helper.py
📌 কাজ:
- scanner এর report নেয়
- error fix করে
- missing code add করে
- code optimize করে

---

### 3️⃣ ai_system_monitor.py
📌 কাজ:
- AI system health check করে
- communication check করে
- master AI-কে report পাঠায়
- system stable রাখে

---

## 🔄 Automation (GitHub Actions)

📁 Workflow file: