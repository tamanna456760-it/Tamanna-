
Tamanna AI - বাংলা AI অ্যাসিস্টেন্ট সিস্টেম
একটি সম্পূর্ণ বাংলা AI সহকারী সিস্টেম
"""

import json
import random
import datetime
import requests
import re
from typing import Dict, List, Any
import speech_recognition as sr
import pyttsx3
import threading
import time

class TamannaAI:
    def __init__(self):
        self.name = "তামান্না AI"
        self.version = "2.0"
        self.user_name = "ব্যবহারকারী"
        self.memory_file = "tamanna_memory.json"
        self.load_memory =
"tamanna456760-it"
        
        # টেক্সট টু স্পিচ ইঞ্জিন সেটআপ
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        
        # স্পিচ রিকগনিশন সেটআপ
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # AI ক্ষমতা
        self.capabilities = {
            "voice_assistant": True,
            "calculations": True,
            "reminders": True,
            "entertainment": True,
            "bengali_support": True
        }
        
        print(f"🤖 {self.name} v{self.version} শুরু হয়েছে!")
        print("সিস্টেম প্রস্তুত। 'সাহায্য' লিখুন কমান্ড জানতে।")
    
    def load_memory(self):
        """মেমরি লোড করুন"""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                self.memory = json.load(f)
        except FileNotFoundError:
            self.memory = {
                "user_preferences": {},
                "conversation_history": [],
                "reminders": [],
                "learned_facts": {}
            }
            self.save_memory()
    
    def save_memory(self):
        """মেমরি সেভ করুন"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def speak(self, text: str):
        """টেক্সট কে speech এ রূপান্তর করুন"""
        def speak_thread():
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        
        thread = threading.Thread(target=speak_thread)
        thread.start()
    
    def listen(self) -> str:
        """কথা শুনুন"""
        try:
            with self.microphone as source:
                print("🎤 শুনছি...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=5)
            
            text = self.recognizer.recognize_google(audio, language='bn-BD')
            print(f"👤 {self.user_name}: {text}")
            return text.lower()
        except sr.UnknownValueError:
            return "দুঃখিত, আমি বুঝতে পারিনি"
        except sr.RequestError:
            return "স্পিচ রিকগনিশন এরর"
        except sr.WaitTimeoutError:
            return "কোন কথা শোনা যায়নি"
    
    def bengali_calculation(self, command: str) -> str:
        """বাংলা ক্যালকুলেশন প্রসেস করুন"""
        # সংখ্যা ম্যাপিং
        number_map = {
            'শূন্য': 0, 'এক': 1, 'দুই': 2, 'তিন': 3, 'চার': 4,
            'পাঁচ': 5, 'ছয়': 6, 'সাত': 7, 'আট': 8, 'নয়': 9,
            'দশ': 10, 'বিশ': 20, 'তিরিশ': 30, 'চল্লিশ': 40, 'পঞ্চাশ': 50,
            'ষাট': 60, 'সত্তর': 70, 'আশি': 80, 'নব্বই': 90, 'একশ': 100
        }
        
        try:
            # যোগ
            if 'যোগ' in command or 'মিলিয়ে' in command:
                numbers = re.findall(r'\d+', command)
                if len(numbers) >= 2:
                    result = sum(map(int, numbers))
                    return f"যোগফল: {result}"
            
            # বিয়োগ
            elif 'বিয়োগ' in command or 'বাদ' in command:
                numbers = re.findall(r'\d+', command)
                if len(numbers) >= 2:
                    result = int(numbers[0]) - int(numbers[1])
                    return f"বিয়োগফল: {result}"
            
            # গুণ
            elif 'গুণ' in command:
                numbers = re.findall(r'\d+', command)
                if len(numbers) >= 2:
                    result = int(numbers[0]) * int(numbers[1])
                    return f"গুণফল: {result}"
            
            # ভাগ
            elif 'ভাগ' in command:
                numbers = re.findall(r'\d+', command)
                if len(numbers) >= 2:
                    if int(numbers[1]) != 0:
                        result = int(numbers[0]) / int(numbers[1])
                        return f"ভাগফল: {result:.2f}"
                    else:
                        return "শূন্য দিয়ে ভাগ করা যায় না"
            
            return "ক্যালকুলেশন বুঝতে পারিনি"
        except:
            return "ক্যালকুলেশন এ সমস্যা হয়েছে"
    
    def get_bengali_time(self):
        """বাংলা সময় দিন"""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        date_str = now.strftime("%A, %d %B %Y")
        
        time_translation = {
            "AM": "সকাল",
            "PM": "বিকাল"
        }
        
        bengali_time = time_str
        for eng, bn in time_translation.items():
            bengali_time = bengali_time.replace(eng, bn)
        
        return f"বর্তমান সময়: {bengali_time}, তারিখ: {date_str}"
    
    def process_command(self, command: str) -> str:
        """ব্যবহারকারীর কমান্ড প্রসেস করুন"""
        command = command.lower()
        response = ""
        
        # কথোপকথন হিস্ট্রি স্টোর করুন
        self.memory["conversation_history"].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "user": command,
            "ai": ""
        })
        
        # বাংলা অভিবাদন
        if any(word in command for word in ["হ্যালো", "হাই", "নমস্কার", "আসসালামু আলাইকুম", "কেমন আছ"]):
            responses = [
                f"নমস্কার {self.user_name}! আমি কীভাবে আপনাকে সাহায্য করতে পারি?",
                f"আসসালামু আলাইকুম {self.user_name}! আমি আপনার সেবায় готов!",
                f"হ্যালো {self.user_name}! আজকে আমি আপনাকে কিভাবে সাহায্য করতে পারি?",
                f"কেমন আছেন {self.user_name}? আমি এখানে আছি আপনাকে সাহায্য করতে!"
            ]
            response = random.choice(responses)
        
        # সময় এবং তারিখ
        elif "সময়" in command or "কটা বাজে" in command:
            response = self.get_bengali_time()
        
        elif "তারিখ" in command or "ক তারিখ" in command:
            current_date = datetime.datetime.now().strftime("%A, %d %B %Y")
            response = f"আজকের তারিখ: {current_date}"
        
        # ক্যালকুলেশন
        elif any(word in command for word in ["যোগ", "বিয়োগ", "গুণ", "ভাগ", "ক্যালকুলেট"]):
            response = self.bengali_calculation(command)
        
        # আবহাওয়া (সিমুলেটেড)
        elif "আবহাওয়া" in command or "আবহাওয়া" in command:
            weather_conditions = ["রৌদ্রোজ্জ্বল", "মেঘলা", "বৃষ্টি", "আংশিক মেঘলা", "ঝড়ো"]
            temperatures = random.randint(20, 35)
            response = f"আজকের আবহাওয়া {random.choice(weather_conditions)} এবং তাপমাত্রা {temperatures}°C"
        
        # রসিকতা
        elif "রসিকতা" in command or "জোক" in command or "মজা" in command:
            jokes = [
                "কম্পিউটার কে বাংলা শেখায় কে? ডিজিটাল ঠাকুরমা!",
                "ইন্টারনেট এর বাংলা কি? অন্তর্জাল!",
                "কম্পিউটার ভাইয়া, তুমি কি চাঁদে যাবে? না, আমি Cloud এ থাকি!",
                "মোবাইল ফোন বলল: আমি খুব ব্যাস্ত, Call রেখেছি!"
            ]
            response = random.choice(jokes)
        
        # সিস্টেম তথ্য
        elif "সংস্করণ" in command or "ভার্সন" in command or "তোমার সম্পর্কে" in command:
            response = f"আমি {self.name} সংস্করণ {self.version}. আমি আপনার বাংলা AI সহকারী!"
        
        # সাহায্য কমান্ড
        elif "সাহায্য" in command or "help" in command:
            response = """
🤖 **তামান্না AI কমান্ড সমূহ:**
• অভিবাদন: হ্যালো, নমস্কার, আসসালামু আলাইকুম
• সময়/তারিখ: সময় কটা, আজ তারিখ কত
• ক্যালকুলেশন: ৫+৩ যোগ কর, ১০*২ গুণ কর
• আবহাওয়া: আজকের আবহাওয়া কেমন
• বিনোদন: একটি রসিকতা বল
• সিস্টেম: সংস্করণ, তোমার সম্পর্কে, সাহায্য
• ভয়েস: ভয়েস মড
• প্রস্থান: বিদায়, বাই, এক্সিট

আমি আপনার পছন্দ মনে রাখতে এবং কথোপকথন থেকে শিখতে পারি!
"""
        
        # মেমরি অপারেশন
        elif "মনে রাখ" in command and "যে" in command:
            key = command.replace("মনে রাখ যে", "").strip()
            self.memory["learned_facts"][key] = True
            self.save_memory()
            response = f"আমি মনে রাখলাম: {key}"
        
        elif "তুমি কি জান" in command or "তোমার কি জানা" in command:
            if self.memory["learned_facts"]:
                facts = ", ".join(self.memory["learned_facts"].keys())
                response = f"আমি এই বিষয়গুলি জানি: {facts}"
            else:
                response = "আমি এখনো কিছু শিখিনি। আমাকে কিছু বলুন মনে রাখার জন্য!"
        
        # প্রস্থান কমান্ড
        elif any(word in command for word in ["বিদায়", "বাই", "exit", "quit", "চলে যাই"]):
            response = f"বিদায় {self.user_name}! আপনাকে সাহায্য করে ভালো লাগল। আবার দেখা হবে! 👋"
        
        else:
            responses = [
                "দুঃখিত, আমি বুঝতে পারিনি। আবার বলুন?",
                "এটা মজার! আরও বলুন?",
                "আমি এখনো শিখছি। অন্য কিছু জিজ্ঞাসা করুন?",
                "আমি ভাবছি... আসলে, অন্য কিছু জিজ্ঞাসা করুন?",
                f"আপনার বার্তার জন্য ধন্যবাদ, {self.user_name}. আর কীভাবে সাহায্য করতে পারি?"
            ]
            response = random.choice(responses)
        
        # AI রেসপন্স দিয়ে আপডেট করুন
        if self.memory["conversation_history"]:
            self.memory["conversation_history"][-1]["ai"] = response
        
        self.save_memory()
        return response
    
    def voice_mode(self):
        """ভয়েস মড এক্টিভেট করুন"""
        print("🎤 ভয়েস মড চালু! কথা বলুন।")
        self.speak("ভয়েস মড চালু হয়েছে। আমি কিভাবে আপনাকে সাহায্য করতে পারি?")
        
        while True:
            try:
                command = self.listen()
                if any(word in command for word in ["ভয়েস মড বন্ধ", "শুনা বন্ধ", "বিদায়"]):
                    self.speak("ভয়েস মড বন্ধ করছি। টেক্সট ইন্টারফেসে ফিরছি।")
                    break
                
                response = self.process_command(command)
                print(f"🤖 {self.name}: {response}")
                self.speak(response)
                
            except KeyboardInterrupt:
                self.speak("ব্যবহারকারী দ্বারা ভয়েস মড বন্ধ করা হয়েছে")
                break
    
    def text_mode(self):
        """টেক্সট-ভিত্তিক ইন্টার্যাকশন মড"""
        print(f"\n{self.name} টেক্সট মড চালু")
        print("আপনার কমান্ড লিখুন বা 'ভয়েস' লিখুন ভয়েস মডে যেতে")
        print("প্রস্থান করতে 'exit' লিখুন\n")
        
        while True:
            try:
                command = input(f"{self.user_name}: ").strip()
                
                if command.lower() == 'ভয়েস':
                    self.voice_mode()
                    continue
                
                if command.lower() in ['exit', 'quit', 'বিদায়']:
                    response = self.process_command(command)
                    print(f"🤖 {self.name}: {response}")
                    break
                
                response = self.process_command(command)
                print(f"🤖 {self.name}: {response}")
                
            except KeyboardInterrupt:
                print(f"\n🤖 {self.name}: বিদায়! তামান্না AI ব্যবহার করার জন্য ধন্যবাদ।")
                break
    
    def set_user_name(self, name: str):
        """ব্যবহারকারীর নাম সেট করুন"""
        self.user_name = name
        self.memory["user_preferences"]["name"] = name
        self.save_memory()
        print(f"🤖 আপনার সাথে পরিচয় হয়ে ভালো লাগল, {self.user_name}!")

def main():
    """তামান্না AI চালানোর মূল ফাংশন"""
    ai = TamannaAI()
    
    # স্বাগতম সিকোয়েন্স
    print("\n" + "="*60)
    print(f"🚀 তামান্না AI v{ai.version} এ স্বাগতম")
    print("="*60)
    
    # ব্যবহারকারীর নাম সেট করুন
    user_name = input("আমি আপনাকে কি নামে ডাকব? ").strip() or "ব্যবহারকারী"
    ai.set_user_name(user_name)
    
    # ইন্টার্যাকশন মড নির্বাচন করুন
    print("\n🎮 উপলব্ধ মড:")
    print("1. টেক্সট মড ('টেক্সট' লিখুন)")
    print("2. ভয়েস মড ('ভয়েস' লিখুন)")
    
    while True:
        mode = input("\nমড নির্বাচন করুন (টেক্সট/ভয়েস): ").strip().lower()
        if mode in ['টেক্সট', 'text', '1']:
            ai.text_mode()
            break
        elif mode in ['ভয়েস', 'voice', '2']:
            ai.voice_mode()
            break
        else:
            print("দয়া করে 'টেক্সট' বা 'ভয়েস' নির্বাচন করুন")

if __name__ == "__main__":
    main()