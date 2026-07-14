#!/usr/bin/env python3
import subprocess
import threading
import time


class RealTimeWiresharkTest:
    """Test real-time network monitoring capabilities"""

    def __init__(self):
        self.capture_process = None
        self.analysis_process = None

    def start_realtime_capture(self, interface="lo", duration=30):
        """Start real-time packet capture and analysis"""
        print(f"🔍 Starting real-time capture on {interface} for {duration} seconds...")

        # Start capture
        capture_cmd = ["tshark", "-i", interface, "-w", "realtime_capture.pcap"]
        self.capture_process = subprocess.Popen(capture_cmd)

        # Start real-time analysis in separate thread
        analysis_thread = threading.Thread(target=self.realtime_analysis)
        analysis_thread.start()

        # Let it run for specified duration
        time.sleep(duration)

        # Stop capture
        self.capture_process.terminate()
        self.capture_process.wait()

        print("✅ Real-time capture test completed")

    def realtime_analysis(self):
        """Perform real-time analysis on captured packets"""
        analysis_cmd = ["tshark", "-r", "realtime_capture.pcap", "-z", "io,stat,1"]

        while self.capture_process and self.capture_process.poll() is None:
            try:
                result = subprocess.run(
                    analysis_cmd, capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    print("📊 Real-time statistics updated")
                time.sleep(2)
            except subprocess.TimeoutExpired:
                continue


# Usage example
if __name__ == "__main__":
    monitor = RealTimeWiresharkTest()
    monitor.start_realtime_capture(duration=10)
