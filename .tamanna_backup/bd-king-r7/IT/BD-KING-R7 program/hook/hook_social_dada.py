#!/usr/bin/env python3

import json
import time
import random
from datetime import datetime

CONFIG = {"interval": 10, "output_file": "social_100_plus.jsonl"}

# =========================
# TIME
# =========================


def now():
    return datetime.utcnow().isoformat()


# =========================
# CORE REAL PLATFORMS
# =========================


def core_platforms():
    return {
        "facebook": random.randint(1000, 20000),
        "instagram": random.randint(1000, 50000),
        "twitter": random.randint(1000, 30000),
        "youtube": random.randint(1000, 100000),
        "tiktok": random.randint(5000, 200000),
        "linkedin": random.randint(500, 20000),
        "reddit": random.randint(1000, 15000),
        "telegram": random.randint(500, 25000),
    }


# =========================
# 100+ VIRTUAL SOCIAL SOURCES
# =========================


def generate_virtual_sources():
    sources = {}

    categories = [
        "news_page",
        "fan_page",
        "crypto_group",
        "tech_channel",
        "gaming_community",
        "ai_forum",
        "sports_page",
        "education_group",
        "entertainment_page",
        "politics_discussion",
        "startup_page",
        "developer_community",
        "meme_page",
        "marketing_group",
    ]

    # 100+ simulated sources
    for i in range(1, 121):
        cat = random.choice(categories)

        sources[f"{cat}_{i}"] = {
            "type": cat,
            "id": i,
            "followers": random.randint(100, 50000),
            "engagement": random.randint(10, 5000),
            "activity_score": round(random.random() * 100, 2),
        }

    return sources


# =========================
# TREND ENGINE
# =========================


def trend_engine():
    trends = []

    keywords = [
        "AI",
        "Crypto",
        "Gaming",
        "Tech",
        "Sports",
        "Music",
        "Movies",
        "Startups",
        "Coding",
        "Memes",
    ]

    for i in range(20):
        trends.append(
            {
                "topic": random.choice(keywords),
                "score": random.randint(1, 100),
                "timestamp": now(),
            }
        )

    return trends


# =========================
# SAVE DATA
# =========================


def save(data):
    with open(CONFIG["output_file"], "a") as f:
        f.write(json.dumps(data) + "\n")


# =========================
# MASTER ENGINE
# =========================


def run_system():
    data = {
        "timestamp": now(),
        "core_platforms": core_platforms(),
        "virtual_sources": generate_virtual_sources(),
        "trends": trend_engine(),
        "total_sources": 8 + 120,
    }

    save(data)

    print("🚀 100+ SOCIAL HOOK RUNNING:", data["timestamp"])
    print("Sources:", data["total_sources"])


# =========================
# LOOP
# =========================

if __name__ == "__main__":
    while True:
        try:
            run_system()
            time.sleep(CONFIG["interval"])

        except KeyboardInterrupt:
            print("Stopped.")
            break

        except Exception as e:
            print("Error:", e)
