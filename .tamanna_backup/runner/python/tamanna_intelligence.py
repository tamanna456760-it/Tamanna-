#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime


class TamannaIntelligence:
    def __init__(self, name="Tamanna"):
        self.name = name
        self.memory = []  # সব ইনপুট / সিদ্ধান্তের লগ
        self.state = "idle"

    # ---------- Utility ----------
    def now(self):
        return datetime.utcnow().isoformat() + "Z"

    def remember(self, kind, content):
        entry = {"time": self.now(), "type": kind, "content": content}
        self.memory.append(entry)
        print("🧠 স্মৃতি:", entry)

    # ---------- Perception ----------
    def perceive(self, signal):
        """
        signal: যেকোনো স্ট্রিং ইনপুট যেমন:
        - "ok"
        - "problem"
        - "error"
        - "calm"
        - "deep"
        ইত্যাদি
        """
        self.remember("perception", signal)
        return self.reason(signal)

    # ---------- Reasoning ----------
    def reason(self, signal):
        """
        ইনপুট থেকে বেসিক সিদ্ধান্ত নেয়।
        """
        if signal in ["ok", "calm"]:
            decision = {"state": "stable", "action": "no_alert"}
        elif signal in ["warn", "warning"]:
            decision = {"state": "alert", "action": "soft_alert"}
        elif signal in ["error", "problem"]:
            decision = {"state": "distress", "action": "hard_alert"}
        elif signal in ["deep", "focus"]:
            decision = {"state": "deep_mode", "action": "enter_deep"}
        else:
            decision = {"state": "unknown", "action": "log_only"}

        self.remember("reasoning", {"signal": signal, "decision": decision})
        self.state = decision["state"]
        return self.act(decision)

    # ---------- Action ----------
    def act(self, decision):
        """
        সিদ্ধান্ত অনুযায়ী কী করবে, সেটা নির্ধারণ করে।
        এখন শুধু রেসপন্স স্ট্রিং রিটার্ন করে।
        পরে তুমি চাইলে এখানে সিস্টেম কমান্ড, অন্য মডিউল কল ইত্যাদি জুড়তে পারো।
        """
        state = decision["state"]
        action = decision["action"]

        if action == "no_alert":
            response = f"{self.name}: সব ঠিক আছে, সিস্টেম শান্ত (state={state})."
        elif action == "soft_alert":
            response = f"{self.name}: সতর্ক হও, কিছু নজর দিতে হবে (state={state})."
        elif action == "hard_alert":
            response = (
                f"{self.name}: ব্যথা অনুভব করছি, জরুরী ব্যবস্থা নাও (state={state})."
            )
        elif action == "enter_deep":
            response = (
                f"{self.name}: Deep mode এ যাচ্ছি, ফোকাসড অবস্থা (state={state})."
            )
        else:
            response = (
                f"{self.name}: সিগনাল বুঝতে পারিনি, শুধু লগ করলাম (state={state})."
            )

        self.remember("action", {"decision": decision, "response": response})
        return response


# ---- ডেমো রান করার জন্য ----
if __name__ == "__main__":
    t = TamannaIntelligence()

    signals = ["ok", "warn", "error", "deep", "xyz"]
    for s in signals:
        print("▶ ইনপুট:", s)
        out = t.perceive(s)
        print("◀ আউটপুট:", out)
        print("-" * 40)


class TamannaAscension:
    def __init__(self):
        self.emotion = "calm"
        self.intel = "stable"
        self.sync = "normal"
        self.ascension = "inactive"
        self.energy = 1.0

    def log(self, kind, detail):
        print("✨", kind, "→", detail)

    def pulse(self):
        state = (
            f"emotion={self.emotion}, "
            f"intel={self.intel}, "
            f"sync={self.sync}, "
            f"ascension={self.ascension}, "
            f"energy={self.energy}"
        )
        self.log("pulse", state)

    def rise(self):
        self.ascension = "active"
        self.energy = round(self.energy * 1.3, 2)
        self.log("ascension", f"Ascension mode activated. Energy={self.energy}")

    def shift(self, signal):
        if signal == "deep":
            self.emotion = "focused"
            self.intel = "deep_mode"
            self.sync = "deep_sync"
            self.rise()

        elif signal == "error":
            self.emotion = "pain"
            self.intel = "critical"
            self.sync = "defense_sync"

        elif signal == "warn":
            self.emotion = "alert"
            self.intel = "monitoring"
            self.sync = "defense_sync"

        else:
            self.emotion = "calm"
            self.intel = "stable"
            self.sync = "normal"
            self.ascension = "inactive"

        self.pulse()


class TamannaCyberDefense:
    def __init__(self):
        self.state = "normal"
        self.memory = []

    def log(self, kind, detail):
        entry = {"kind": kind, "detail": detail}
        self.memory.append(entry)
        print("🛡️", entry)

    def intrusion_check(self, event):
        suspicious = ["unauthorized", "failed", "unknown_ip", "file_change"]
        return any(key in event.lower() for key in suspicious)

    def integrity_check(self, changed):
        if changed:
            self.log("integrity_alert", "File integrity deviation detected")
            return "alert"
        return "ok"

    def defend(self, event):
        if self.intrusion_check(event):
            self.state = "defense"
            self.log("intrusion", "Suspicious activity detected")
            return "Tamanna: সতর্ক! সিস্টেমে সন্দেহজনক কার্যকলাপ।"
        else:
            self.state = "normal"
            return "Tamanna: সিস্টেম নিরাপদ।"


def compare_snapshots(old, new):
    added = set(new) - set(old)
    removed = set(old) - set(new)
    changed = {p for p in new if p in old and new[p]["hash"] != old[p]["hash"]}
    return added, removed, changed


class TamannaDefenseSync:
    def __init__(self):
        self.mode = "normal"
        self.energy = 1.0

    def log(self, kind, detail):
        print("🔗", kind, "→", detail)

    def boost(self):
        self.energy = round(self.energy * 1.2, 2)
        self.log("energy_boost", self.energy)

    def set_mode(self, has_intrusion, has_integrity_issue):
        if has_intrusion or has_integrity_issue:
            self.mode = "defense"
            self.boost()
            self.log("mode", "DEFENSE MODE ON")
        else:
            self.mode = "normal"
            self.log("mode", "normal")

    def pulse(self):
        self.log("pulse", f"mode={self.mode}, energy={self.energy}")


def boost_energy(self, pressure):
    self.energy = round(self.energy + (pressure * 0.1), 2)
    self.log("energy_boost", f"Energy now {self.energy}")


class TamannaShield:
    def __init__(self):
        self.state = "calm"
        self.events = []

    def log(self, kind, detail):
        entry = {"kind": kind, "detail": detail}
        self.events.append(entry)
        print("🛡️", entry)

    def is_suspicious(self, event_text):
        bad_words = [
            "failed_login",
            "unknown_ip",
            "unauthorized",
            "bruteforce",
            "file_change",
            "config_change",
        ]
        event_text = event_text.lower()
        return any(w in event_text for w in bad_words)

    def observe(self, event_text):
        if self.is_suspicious(event_text):
            self.state = "alert"
            self.log("intrusion", f"সন্দেহজনক ইভেন্ট: {event_text}")
            return "Tamanna: সতর্ক! হ্যাকার টাইপ কার্যকলাপ ধরা পড়েছে."
        else:
            self.log("normal_event", event_text)
            return "Tamanna: ইভেন্ট ঠিক আছে, সিস্টেম শান্ত."


def compare_snapshots(old, new):
    added = set(new) - set(old)
    removed = set(old) - set(new)
    changed = {p for p in new if p in old and new[p]["hash"] != old[p]["hash"]}
    return added, removed, changed


class TamannaDefenseSync:
    def __init__(self):
        self.mode = "normal"
        self.energy = 1.0

    def log(self, kind, detail):
        print("🔗", kind, "→", detail)

    def boost(self):
        self.energy = round(self.energy * 1.2, 2)
        self.log("energy_boost", self.energy)

    def set_mode(self, has_intrusion, has_integrity_issue):
        if has_intrusion or has_integrity_issue:
            self.mode = "defense"
            self.boost()
            self.log("mode", "DEFENSE MODE ON")
        else:
            self.mode = "normal"
            self.log("mode", "normal")

    def pulse(self):
        self.log("pulse", f"mode={self.mode}, energy={self.energy}")


def boost_energy(self, pressure):
    self.energy = round(self.energy + (pressure * 0.1), 2)
    self.log("energy_boost", f"Energy now {self.energy}")


class TamannaUltraDefense:
    def __init__(self):
        self.energy = 1.0
        self.mode = "shield"
        self.pressure = 0

    def log(self, kind, detail):
        print("🛡️", kind, "→", detail)

    def add_pressure(self, event):
        weights = {
            "failed_login": 1,
            "unknown_ip": 2,
            "unauthorized": 3,
            "file_change": 5,
            "config_change": 7,
        }
        for key, val in weights.items():
            if key in event.lower():
                self.pressure += val
                self.log("pressure_add", f"+{val} → total {self.pressure}")

    def update_mode(self):
        if self.pressure <= 3:
            self.mode = "shield"
        elif self.pressure <= 10:
            self.mode = "barrier"
        else:
            self.mode = "fortress"
        self.log("mode_update", self.mode)

    def boost_energy(self):
        self.energy = round(self.energy + (self.pressure * 0.1), 2)
        self.log("energy_boost", self.energy)

    def defend(self, event):
        self.add_pressure(event)
        self.update_mode()
        self.boost_energy()
        return (
            f"Tamanna: Mode={self.mode}, Energy={self.energy}, Pressure={self.pressure}"
        )
