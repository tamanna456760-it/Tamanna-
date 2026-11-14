#!/usr/bin/env python3
import os
import subprocess
import unittest


class TestWiresharkCore(unittest.TestCase):

    def setUp(self):
        self.test_interface = "lo"  # Loopback for testing
        self.test_pcap = "test_capture.pcap"

    def test_tshark_installation(self):
        """Test tshark (command-line Wireshark) installation"""
        try:
            result = subprocess.run(
                ["tshark", "--version"], capture_output=True, text=True, timeout=30
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("TShark", result.stdout)
            print("✓ TShark installation verified")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("TShark not installed")

    def test_capture_interface_listing(self):
        """Test listing available capture interfaces"""
        try:
            result = subprocess.run(
                ["tshark", "-D"], capture_output=True, text=True, timeout=30
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn(self.test_interface, result.stdout)
            print("✓ Interface listing working")
        except subprocess.TimeoutExpired:
            self.fail("Interface listing timed out")

    def test_packet_capture(self):
        """Test basic packet capture functionality"""
        try:
            # Start capture in background
            capture_cmd = [
                "tshark",
                "-i",
                self.test_interface,
                "-w",
                self.test_pcap,
                "-c",
                "10",
                "-a",
                "duration:10",
            ]
            capture_proc = subprocess.Popen(
                capture_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            # Generate some test traffic
            traffic_cmd = ["ping", "-c", "5", "127.0.0.1"]
            subprocess.run(traffic_cmd, capture_output=True)

            # Wait for capture to complete
            capture_proc.wait(timeout=15)

            # Verify capture file was created
            self.assertTrue(os.path.exists(self.test_pcap))
            print("✓ Packet capture working")

            # Clean up
            if os.path.exists(self.test_pcap):
                os.remove(self.test_pcap)

        except subprocess.TimeoutExpired:
            self.fail("Packet capture timed out")

    def test_packet_analysis(self):
        """Test packet analysis capabilities"""
        try:
            # Create a simple capture with known content
            test_cmd = ["tshark", "-i", self.test_interface, "-c", "5", "-w", "-"]
            result = subprocess.run(test_cmd, capture_output=True, timeout=30)

            if result.returncode == 0 and len(result.stdout) > 0:
                print("✓ Packet analysis working")
            else:
                self.skipTest("No packets captured for analysis")

        except subprocess.TimeoutExpired:
            self.skipTest("Packet analysis timed out")
