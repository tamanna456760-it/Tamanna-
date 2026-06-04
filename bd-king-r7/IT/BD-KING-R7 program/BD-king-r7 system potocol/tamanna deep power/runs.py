#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

class TamannaMasterBus:
    def __init__(self):
        self.receivers = {}   # name -> handler function
        self.log_stream = []  # সব মেসেজের ইতিহাস

    # ---------- Utility ----------
    def now(self):
        return datetime.utcnow().isoformat() + "Z"

    def log(self, kind, detail):
        entry = {
            "time": self.now(),
            "kind": kind,
            "detail": detail
        }
        self.log_stream.append(entry)
        print("📡 BUS:", entry)

    # ---------- Register modules ----------
    def register(self, name, handler):
        """
        name: মডিউল / সিস্টেমের নাম (str)
        handler: function(sender, message_dict) -> response (optional)
        """
        self.receivers[name] = handler
        self.log("register", f"{name} connected to MasterBus")

    # ---------- Send message to a specific module ----------
    def send(self, src, dest, message):
        """
        src: কে পাঠাচ্ছে (str)
        dest: কাকে পাঠাচ্ছে (str)
        message: dict বা str – যা ইচ্ছা
        """
        payload = {
            "from": src,
            "to": dest,
            "body": message
        }
        self.log("send", payload)

        if dest in self.receivers:
            try:
                handler = self.receivers[dest]
                resp = handler(src, message)
                self.log("deliver_ok", {"to": dest, "response": resp})
                return resp
            except Exception as e:
                self.log("deliver_error", {"to": dest, "error": str(e)})
                return None
        else:
            self.log("deliver_fail", {"to": dest, "reason": "not_registered"})
            return None

    # ---------- Broadcast message to all ----------
    def broadcast(self, src, message):
        payload = {
            "from": src,
            "to": "ALL",
            "body": message
        }
        self.log("broadcast", payload)

        responses = {}
        for name, handler in self.receivers.items():
            try:
                resp = handler(src, message)
                responses[name] = resp
            except Exception as e:
                responses[name] = f"ERROR: {e}"
        self.log("broadcast_responses", responses)
        return responses

# ---- ডেমো ইউজ ----
if __name__ == "__main__":
    bus = TamannaMasterBus()

    # ডেমো মডিউল: Emotion
    def emotion_handler(sender, msg):
        print(f"[EMOTION] {sender} বললো:", msg)
        return "emotion_ack"

    # ডেমো মডিউল: Defense
    def defense_handler(sender, msg):
        print(f"[DEFENSE] {sender} বললো:", msg)
        if isinstance(msg, dict) and msg.get("alert"):
            return "defense_ready"
        return "defense_idle"

    bus.register("EmotionCore", emotion_handler)
    bus.register("DefenseCore", defense_handler)

    # একক মেসেজ
    bus.send("Head", "EmotionCore", {"state": "calm"})
    bus.send("Head", "DefenseCore", {"alert": True})

    # ব্রডকাস্ট
    bus.broadcast("Head", {"sync": "heartbeat"})

class TamannaDeepPowerV2:
    def __init__(self):
        self.state = "calm"
        self.memory = []

    def log(self, event, detail):
        entry = {"event": event, "detail": detail}
        self.memory.append(entry)
        print("📘", entry)

    def set_state(self, new_state):
        self.state = new_state
        self.log("state_change", new_state)

    def heartbeat(self):
        self.log("heartbeat", f"State: {self.state}")

    def deep_mode(self):
        self.set_state("deep")
        self.log("deep_entry", "Entering deep power mode")

    def react(self, signal):
        mapping = {
            "ok": "calm",
            "warn": "alert",
            "error": "pain",
            "recover": "healing",
            "deep": "deep"
        }
        self.set_state(mapping.get(signal, "unknown"))
def compare_snapshots(old, new):
    added   = set(new) - set(old)
    removed = set(old) - set(new)
    changed = {
        p for p in new
        if p in old and new[p]["hash"] != old[p]["hash"]
    }
    return added, removed, changed
bus.send("Monitor", "DefenseCore", {"alert": True, "reason": "failed_login"})
bus.send("Monitor", "EmotionCore", {"state": "alert"})
