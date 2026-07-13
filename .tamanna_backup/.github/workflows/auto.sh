#!/bin/bash
while true; do
  adb shell pm disable-user --user 0 com.infinix.xoslauncher
  sleep 60
done