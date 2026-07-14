#!/usr/bin/env python3
"""
Webhook Handler
"""

import json
import os

import requests


class WebhookManager:
    def __init__(self):
        self.webhooks_file = "webhooks.json"
        self.load_webhooks()

    def load_webhooks(self):
        if os.path.exists(self.webhooks_file):
            with open(self.webhooks_file, "r") as f:
                self.webhooks = json.load(f)
        else:
            self.webhooks = {"endpoints": []}

    def save_webhooks(self):
        with open(self.webhooks_file, "w") as f:
            json.dump(self.webhooks, f, indent=2)

    def add_webhook(self, url, events):
        self.webhooks["endpoints"].append(
            {"url": url, "events": events, "active": True}
        )
        self.save_webhooks()

    def trigger_webhooks(self, event_type, data):
        for webhook in self.webhooks["endpoints"]:
            if webhook["active"] and event_type in webhook["events"]:
                try:
                    response = requests.post(
                        webhook["url"],
                        json={
                            "event": event_type,
                            "data": data,
                            "timestamp": __import__("datetime")
                            .datetime.now()
                            .isoformat(),
                        },
                        timeout=10,
                    )
                    print(
                        f"✅ Webhook sent to {webhook['url']}: {response.status_code}"
                    )
                except Exception as e:
                    print(f"❌ Webhook failed for {webhook['url']}: {e}")


def main():
    print("🪝 Processing webhooks...")

    manager = WebhookManager()

    # Trigger build event
    manager.trigger_webhooks(
        "build_completed", {"repository": "BD-KING-R7", "status": "success"}
    )


if __name__ == "__main__":
    main()
