
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tamanna AI - বাংলা AI সহকারী
Owner: HM INSAN ALI

Features:
- Bengali and English text assistant
- Time, date, and basic calculations
- Persistent JSON memory
- Optional voice interaction
- Restricted Kali Linux tool assistance

Security:
- Does not execute arbitrary user-supplied shell commands.
- Kali commands are limited to an explicit allowlist.
"""

import ast
import datetime
import json
import operator
import os
import random
import re
import subprocess
import threading
from pathlib import Path

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


APP_NAME = "তামান্না AI"
APP_VERSION = "2.1.0"

MEMORY_PATH = Path(
    os.environ.get("TAMANNA_MEMORY_FILE", "tamanna_memory.json")
)


def default_memory():
    """Return the initial memory structure."""
    return {
        "user_preferences": {},
        "conversation_history": [],
        "reminders": [],
        "learned_facts": {},
        "kali_tools": {},
        "common_workflows": {},
    }


def safe_calculate(expression):
    """Evaluate basic arithmetic without using eval()."""
    expression = expression.strip()

    if not expression or len(expression) > 100:
        raise ValueError("Invalid calculation")

    allowed_chars = set("0123456789+-*/().% ")
    if any(char not in allowed_chars for char in expression):
        raise ValueError("Only basic arithmetic is supported")

    tree = ast.parse(expression, mode="eval")

    binary_ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
    }

    unary_ops = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                if abs(node.value) > 10**12:
                    raise ValueError("Number is too large")
                return node.value
            raise ValueError("Invalid value")

        if isinstance(node, ast.BinOp):
            operation = binary_ops.get(type(node.op))
            if operation is None:
                raise ValueError("Unsupported operation")

            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, (ast.Div, ast.Mod)) and right == 0:
                raise ValueError("শূন্য দিয়ে ভাগ করা যায় না")

            result = operation(left, right)

            if isinstance(result, (int, float)) and abs(result) > 10**15:
                raise ValueError("Result is too large")

            return result

        if isinstance(node, ast.UnaryOp):
            operation = unary_ops.get(type(node.op))
            if operation is None:
                raise ValueError("Unsupported operation")
            return operation(evaluate(node.operand))

        raise ValueError("Unsupported expression")

    return evaluate(tree)


class TamannaAI:
    """Core Bengali AI assistant."""

    def __init__(self):
        self.name = APP_NAME
        self.version = APP_VERSION
        self.user_name = "ব্যবহারকারী"

        self.memory_file = MEMORY_PATH
        self.memory = default_memory()

        self.tts_engine = None
        self.recognizer = None
        self.microphone_available = False

        self._tts_lock = threading.Lock()

        self.load_memory()

        print(f"🤖 {self.name} v{self.version} চালু হয়েছে!")
        print("সিস্টেম প্রস্তুত। 'সাহায্য' লিখে কমান্ড দেখুন।")

    def load_memory(self):
        """Load saved memory, or create a new memory file."""
        try:
            if self.memory_file.exists():
                with self.memory_file.open(
                    "r", encoding="utf-8"
                ) as file:
                    loaded = json.load(file)

                if isinstance(loaded, dict):
                    self.memory.update(loaded)

            for key, default in default_memory().items():
                if key not in self.memory:
                    self.memory[key] = default

            if not isinstance(
                self.memory.get("conversation_history"), list
            ):
                self.memory["conversation_history"] = []

            if not isinstance(self.memory.get("learned_facts"), dict):
                self.memory["learned_facts"] = {}

        except (OSError, json.JSONDecodeError) as exc:
            print(f"⚠️ মেমরি পড়া যায়নি: {exc}")
            self.memory = default_memory()

    def save_memory(self):
        """Save memory atomically to a JSON file."""
        try:
            self.memory_file.parent.mkdir(
                parents=True, exist_ok=True
            )

            temporary_file = self.memory_file.with_suffix(".tmp")

            with temporary_file.open(
                "w", encoding="utf-8"
            ) as file:
                json.dump(
                    self.memory,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            os.replace(temporary_file, self.memory_file)
            return True

        except OSError as exc:
            print(f"⚠️ মেমরি সংরক্ষণ করা যায়নি: {exc}")
            return False

    def setup_voice(self):
        """Initialize optional voice components when available."""
        if sr is None:
            print(
                "ভয়েসের জন্য SpeechRecognition ইনস্টল করা নেই।"
            )
            return False

        try:
            self.recognizer = sr.Recognizer()

            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(
                    source, duration=0.5
                )

            self.microphone_available = True

        except Exception as exc:
            self.microphone_available = False
            print(f"⚠️ মাইক্রোফোন প্রস্তুত নয়: {exc}")
            return False

        if pyttsx3 is not None:
            try:
                self.tts_engine = pyttsx3.init()
                self.tts_engine.setProperty("rate", 150)
            except Exception as exc:
                self.tts_engine = None
                print(f"⚠️ Text-to-speech চালু হয়নি: {exc}")

        return True

    def speak(self, text):
        """Speak text if text-to-speech is available."""
        if self.tts_engine is None:
            return False

        try:
            with self._tts_lock:
                self.tts_engine.say(str(text))
                self.tts_engine.runAndWait()
            return True
        except Exception as exc:
            print(f"⚠️ ভয়েস আউটপুট সমস্যা: {exc}")
            return False

    def listen(self):
        """Listen for Bengali speech."""
        if not self.microphone_available or self.recognizer is None:
            return ""

        try:
            with sr.Microphone() as source:
                print("🎤 শুনছি...")
                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=15,
                )

            text = self.recognizer.recognize_google(
                audio, language="bn-BD"
            )

            print(f"👤 {self.user_name}: {text}")
            return text.strip().lower()

        except sr.WaitTimeoutError:
            print("কোনো কথা শোনা যায়নি।")
        except sr.UnknownValueError:
            print("দুঃখিত, কথাটি বুঝতে পারিনি।")
        except sr.RequestError:
            print("স্পিচ রিকগনিশন পরিষেবায় সংযোগ করা যায়নি।")
        except Exception as exc:
            print(f"⚠️ ভয়েস ইনপুট সমস্যা: {exc}")

        return ""

    @staticmethod
    def normalize_bengali_digits(text):
        """Convert Bengali numerals to Western numerals."""
        translation = str.maketrans(
            "০১২৩৪৫৬৭৮৯", "0123456789"
        )
        return text.translate(translation)

    def bengali_calculation(self, command):
        """Handle simple arithmetic requests."""
        normalized = self.normalize_bengali_digits(command)

        patterns = [
            r"(-?\d+(?:\.\d+)?)\s*([+*/%])\s*(-?\d+(?:\.\d+)?)",
            r"(-?\d+(?:\.\d+)?)\s*-\s*(-?\d+(?:\.\d+)?)",
        ]

        for pattern in patterns:
            match = re.search(pattern, normalized)

            if match:
                expression = match.group(0)
                try:
                    result = safe_calculate(expression)
                    return f"হিসাবের ফলাফল: {result}"
                except (ValueError, SyntaxError, ZeroDivisionError):
                    return "হিসাবটি করা যায়নি। সংখ্যাগুলো পরীক্ষা করুন।"

        numbers = re.findall(r"-?\d+(?:\.\d+)?", normalized)

        if len(numbers) < 2:
            return (
                "হিসাব বুঝতে পারিনি। উদাহরণ: ৫ + ৩ "
                "অথবা ১০ * ২ লিখুন।"
            )

        first = float(numbers[0])
        second = float(numbers[1])

        if "যোগ" in command or "মিলিয়ে" in command:
            result = first + second
        elif "বিয়োগ" in command or "বাদ" in command:
            result = first - second
        elif "গুণ" in command:
            result = first * second
        elif "ভাগ" in command:
            if second == 0:
                return "শূন্য দিয়ে ভাগ করা যায় না।"
            result = first / second
        else:
            return "যোগ, বিয়োগ, গুণ বা ভাগ উল্লেখ করুন।"

        return f"হিসাবের ফলাফল: {result:g}"

    @staticmethod
    def get_bengali_time():
        """Return current local date and time."""
        now = datetime.datetime.now().astimezone()

        return (
            f"বর্তমান সময়: {now.strftime('%I:%M:%S %p')}, "
            f"তারিখ: {now.strftime('%d-%m-%Y')}, "
            f"দিন: {now.strftime('%A')}"
        )

    def _record_conversation(self, command, response):
        """Append a conversation entry and limit memory growth."""
        history = self.memory["conversation_history"]

        history.append({
            "timestamp": datetime.datetime.now().astimezone().isoformat(),
            "user": command,
            "ai": response,
        })

        self.memory["conversation_history"] = history[-1000:]

    def process_command(self, command):
        """Process text commands and update memory."""
        command = str(command).strip()
        if not command:
            return "দয়া করে একটি বার্তা লিখুন।"

        lowered = command.lower()
        response = ""

        greetings = [
            "হ্যালো",
            "হাই",
            "নমস্কার",
            "আসসালামু আলাইকুম",
            "কেমন আছ",
            "hello",
            "hi",
        ]

        if any(word in lowered for word in greetings):
            response = (
                f"হ্যালো {self.user_name}! আমি Tamanna AI। "
                "আপনাকে কীভাবে সাহায্য করতে পারি?"
            )

        elif (
            "সময়" in lowered
            or "কটা বাজে" in lowered
            or "তারিখ" in lowered
            or "date" in lowered
            or "time" in lowered
        ):
            response = self.get_bengali_time()

        elif any(
            word in lowered
            for word in [
                "যোগ", "বিয়োগ", "গুণ", "ভাগ",
                "ক্যালকুলেট", "হিসাব",
            ]
        ) or re.search(
            r"\d+\s*[+*/%\-]\s*\d+",
            self.normalize_bengali_digits(lowered),
        ):
            response = self.bengali_calculation(command)

        elif "আবহাওয়া" in lowered or "আবহাওয়া" in lowered:
            response = (
                "এই সংস্করণে লাইভ আবহাওয়ার API সংযুক্ত নেই। "
                "বর্তমান আবহাওয়ার জন্য একটি আবহাওয়া পরিষেবা "
                "সংযুক্ত করতে হবে।"
            )

        elif (
            "রসিকতা" in lowered
            or "জোক" in lowered
            or "মজা" in lowered
            or "joke" in lowered
        ):
            response = random.choice([
                "কম্পিউটার কেন ঠান্ডা থাকে? কারণ তার অনেক Windows আছে!",
                "ইন্টারনেটের বাংলা হলো অন্তর্জাল!",
                "প্রোগ্রামার চা খায় কেন? কোডের বাগ তাড়াতে!",
            ])

        elif (
            "সংস্করণ" in lowered
            or "ভার্সন" in lowered
            or "তোমার সম্পর্কে" in lowered
        ):
            response = (
                f"আমি {self.name}, সংস্করণ {self.version}। "
                "আমি একটি বাংলা টেক্সট ও ঐচ্ছিক ভয়েস সহকারী।"
            )

        elif "সাহায্য" in lowered or "help" in lowered:
            response = (
                "Tamanna AI কমান্ড:\n"
                "• হ্যালো — অভিবাদন\n"
                "• সময় বা আজকের তারিখ — সময় ও তারিখ\n"
                "• ৫ + ৩ অথবা ১০ * ২ — সাধারণ হিসাব\n"
                "• মনে রাখ যে আমার পছন্দ নীল — তথ্য সংরক্ষণ\n"
                "• তুমি কি জান — সংরক্ষিত তথ্য দেখুন\n"
                "• রসিকতা — একটি জোক\n"
                "• নাম পরিবর্তন — নিজের নাম সেট করুন\n"
                "• ভয়েস — ভয়েস মোড\n"
                "• সাহায্য — এই তালিকা\n"
                "• exit — প্রস্থান"
            )

        elif "মনে রাখ" in lowered:
            fact = re.sub(
                r"^.*?মনে রাখ(?: যে)?",
                "",
                command,
                flags=re.IGNORECASE,
            ).strip()

            if fact:
                self.memory["learned_facts"][fact] = True
                self.save_memory()
                response = f"আমি মনে রাখলাম: {fact}"
            else:
                response = (
                    "কী মনে রাখতে হবে লিখুন। "
                    "উদাহরণ: মনে রাখ যে আমার পছন্দ নীল"
                )

        elif "তুমি কি জান" in lowered or "তোমার কি জানা" in lowered:
            facts = self.memory["learned_facts"]

            if facts:
                response = (
                    "সংরক্ষিত তথ্য:\n"
                    + "\n".join(f"• {fact}" for fact in facts)
                )
            else:
                response = "এখনো কোনো তথ্য সংরক্ষণ করা হয়নি।"

        elif "নাম পরিবর্তন" in lowered:
            response = (
                "নাম পরিবর্তন করতে set_user_name ফাংশন ব্যবহার করুন।"
            )

        elif any(
            word in lowered
            for word in ["বিদায়", "বাই", "exit", "quit"]
        ):
            response = (
                f"বিদায় {self.user_name}! "
                "Tamanna AI ব্যবহার করার জন্য ধন্যবাদ।"
            )

        else:
            response = (
                "দুঃখিত, এই অনুরোধের উত্তর আমার বর্তমান "
                "সীমিত কমান্ডে নেই। 'সাহায্য' লিখে কমান্ড দেখুন।"
            )

        self._record_conversation(command, response)
        self.save_memory()
        return response

    def set_user_name(self, name):
        """Set the user's display name."""
        name = str(name).strip()

        if not name:
            return False

        self.user_name = name[:80]
        self.memory["user_preferences"]["name"] = self.user_name
        self.save_memory()

        print(f"আপনার সঙ্গে পরিচিত হয়ে ভালো লাগল, {self.user_name}!")
        return True

    def text_mode(self):
        """Run the interactive text interface."""
        print(f"\n{self.name} — টেক্সট মোড")
        print("সাহায্যের জন্য 'সাহায্য' লিখুন।")
        print("প্রস্থান করতে 'exit' লিখুন।\n")

        while True:
            try:
                command = input(f"{self.user_name}: ").strip()

                if command.lower() in ("exit", "quit", "বিদায়", "বাই"):
                    print(f"{self.name}: বিদায়!")
                    break

                if command.lower() in ("ভয়েস", "voice"):
                    self.voice_mode()
                    continue

                response = self.process_command(command)
                print(f"{self.name}: {response}")

            except (EOFError, KeyboardInterrupt):
                print(f"\n{self.name}: সেশন বন্ধ করা হয়েছে।")
                break

    def voice_mode(self):
        """Run voice mode if microphone support is available."""
        if not self.microphone_available:
            if not self.setup_voice():
                print("ভয়েস মোড চালু করা যায়নি। টেক্সট মোড ব্যবহার করুন।")
                return

        print("ভয়েস মোড চালু। বন্ধ করতে 'ভয়েস বন্ধ' বলুন।")
        self.speak("ভয়েস মোড চালু হয়েছে। কথা বলুন।")

        while True:
            command = self.listen()

            if not command:
                continue

            if any(
                word in command
                for word in ["ভয়েস বন্ধ", "বিদায়", "voice off"]
            ):
                self.speak("ভয়েস মোড বন্ধ করা হচ্ছে।")
                break

            response = self.process_command(command)
            print(f"{self.name}: {response}")
            self.speak(response)


class KaliTamannaAI(TamannaAI):
    """Restricted Kali Linux helper.

    Only predefined, read-only commands are available.
    This class does not execute arbitrary shell input.
    """

    ALLOWED_COMMANDS = {
        "python_version": ["python3", "--version"],
        "git_version": ["git", "--version"],
        "nmap_help": ["nmap", "--help"],
    }

    def __init__(self):
        super().__init__()
        self.name = "তামান্না AI - সিকিউরিটি সহকারী"

    def execute_command(self, command_name):
        """Run one predefined command without a shell."""
        argv = self.ALLOWED_COMMANDS.get(command_name)

        if argv is None:
            return (
                "এই কমান্ড অনুমোদিত নয়। "
                "অনুমোদিত নাম: "
                + ", ".join(sorted(self.ALLOWED_COMMANDS))
            )

        try:
            result = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
                shell=False,
            )

            output = result.stdout or result.stderr or "কোনো আউটপুট নেই।"
            return output[:3000]

        except FileNotFoundError:
            return f"প্রয়োজনীয় টুল পাওয়া যায়নি: {argv[0]}"
        except subprocess.TimeoutExpired:
            return "কমান্ডের সময়সীমা শেষ হয়েছে।"
        except OSError as exc:
            return f"কমান্ড চালানো যায়নি: {exc}"

    def process_kali_command(self, command):
        """Respond to supported security-helper requests."""
        lowered = command.lower()

        if "python version" in lowered or "python সংস্করণ" in lowered:
            return self.execute_command("python_version")

        if "git version" in lowered or "git সংস্করণ" in lowered:
            return self.execute_command("git_version")

        if "nmap help" in lowered or "nmap সাহায্য" in lowered:
            return self.execute_command("nmap_help")

        if "নেটওয়ার্ক স্ক্যান" in lowered:
            return (
                "নেটওয়ার্ক স্ক্যানের আগে নিজের বা অনুমোদিত "
                "নেটওয়ার্ক নিশ্চিত করুন। এই সংস্করণ স্বয়ংক্রিয়ভাবে "
                "কোনো নেটওয়ার্ক স্ক্যান করে না।"
            )

        return "এই সিকিউরিটি অনুরোধটি সমর্থিত নয়।"

    def enhanced_process_command(self, command):
        """Try supported security commands before general chat."""
        response = self.process_kali_command(command)

        if response != "এই সিকিউরিটি অনুরোধটি সমর্থিত নয়।":
            return response

        return self.process_command(command)


def main():
    """Start Tamanna AI."""
    print("=" * 55)
    print(f"{APP_NAME} v{APP_VERSION}")
    print("Owner: HM INSAN ALI")
    print("=" * 55)

    assistant = TamannaAI()

    saved_name = assistant.memory["user_preferences"].get("name")
    if saved_name:
        assistant.set_user_name(saved_name)
    else:
        try:
            name = input("আপনাকে কী নামে ডাকব? ").strip()
            if name:
                assistant.set_user_name(name)
        except (EOFError, KeyboardInterrupt):
            print("\nনাম সেট করা হয়নি।")

    try:
        assistant.text_mode()
    except KeyboardInterrupt:
        print("\nTamanna AI বন্ধ হয়েছে।")


if __name__ == "__main__":
    main()
