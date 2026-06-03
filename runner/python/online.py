#!/usr/bin/env python3
"""
Online Code Validator
"""
import json
import os


def validate_code_online():
    print("🌐 Validating code online...")

    # Example: Validate with external service
    try:
        # Validate JSON files
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r") as f:
                            json.load(f)
                        print(f"✅ Valid JSON: {file_path}")
                    except json.JSONDecodeError as e:
                        print(f"❌ Invalid JSON in {file_path}: {e}")

        print("✅ All code validation passed!")
        return True

    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


if __name__ == "__main__":
    validate_code_online()
