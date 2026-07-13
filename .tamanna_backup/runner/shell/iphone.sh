#!/bin/bash
echo "🔍 Tamanna Defender: iPhone Security Scan Initiated"

# Check for jailbreak traces
ideviceinfo | grep -i "jailbreak" > /tamanna/logs/jailbreak_check.log

# Check for unsigned profiles
ideviceprovision | grep -i "Unsigned" > /tamanna/logs/profile_check.log

# Check for unusual battery drain
ideviceinfo | grep -i "BatteryCurrentCapacity" >> /tamanna/logs/battery_check.log

echo "✅ Scan complete. Echo inscribed in /tamanna/logs/"
