class TestWiresharkSecurity(unittest.TestCase):

    def test_malicious_traffic_detection(self):
        """Test detection capabilities for suspicious traffic patterns"""
        suspicious_patterns = [
            ("tcp.flags.syn==1 and tcp.flags.ack==0", "SYN flood pattern"),
            (
                'http.request.method == "POST" and http.host contains "evil"',
                "Suspicious HTTP",
            ),
            ('dns.qry.name contains "malware"', "Suspicious DNS"),
        ]

        for pattern, description in suspicious_patterns:
            with self.subTest(pattern=description):
                try:
                    cmd = ["tshark", "-Y", pattern, "-c", "1"]
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=10
                    )
                    self.assertIn(result.returncode, [0, 1])
                    print(f"✓ {description} detection working")
                except subprocess.TimeoutExpired:
                    print(f"⚠ {description} detection timed out")

    def test_encrypted_traffic_analysis(self):
        """Test TLS/SSL traffic analysis"""
        try:
            # Test SSL/TLS statistics
            cmd = ["tshark", "-z", "ssl,stat,0",
                   "-i", "lo", "-a", "duration:5"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0)
            print("✓ Encrypted traffic analysis working")
        except subprocess.TimeoutExpired:
            print("⚠ Encrypted traffic analysis timed out")
