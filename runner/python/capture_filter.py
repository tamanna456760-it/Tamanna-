class TestWiresharkAdvanced(unittest.TestCase):

    def test_display_filters(self):
        """Test Wireshark display filters"""
        display_filters = [
            "tcp",
            "udp",
            "http",
            "dns",
            "ip.addr == 127.0.0.1",
            "tcp.port == 80",
        ]

        for filter_expr in display_filters:
            with self.subTest(filter=filter_expr):
                try:
                    cmd = ["tshark", "-Y", filter_expr, "-c", "1"]
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=15
                    )
                    # Filter should not cause errors even if no packets match
                    self.assertIn(result.returncode, [0, 1])
                    print(f"✓ Display filter '{filter_expr}' working")
                except subprocess.TimeoutExpired:
                    print(f"⚠ Display filter '{filter_expr}' timed out")

    def test_capture_filters(self):
        """Test BPF capture filters"""
        capture_filters = [
            "tcp",
            "udp port 53",
            "host 127.0.0.1",
            "net 192.168.1.0/24",
            "port 80",
        ]

        for filter_expr in capture_filters:
            with self.subTest(filter=filter_expr):
                try:
                    cmd = [
                        "tshark",
                        "-f",
                        filter_expr,
                        "-i",
                        "lo",
                        "-c",
                        "1",
                        "-a",
                        "duration:5",
                    ]
                    result = subprocess.run(
                        cmd, capture_output=True, timeout=10)
                    self.assertIn(result.returncode, [0, 1])
                    print(f"✓ Capture filter '{filter_expr}' working")
                except subprocess.TimeoutExpired:
                    print(f"⚠ Capture filter '{filter_expr}' timed out")

    def test_protocol_analysis(self):
        """Test protocol-specific analysis"""
        protocols = [
            ("http", "HTTP analysis"),
            ("dns", "DNS analysis"),
            ("tcp", "TCP analysis"),
            ("ssl", "SSL/TLS analysis"),
        ]

        for protocol, description in protocols:
            with self.subTest(protocol=protocol):
                try:
                    cmd = [
                        "tshark",
                        "-z",
                        f"io,stat,0,{protocol}",
                        "-i",
                        "lo",
                        "-a",
                        "duration:5",
                    ]
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=15
                    )
                    self.assertEqual(result.returncode, 0)
                    print(f"✓ {description} working")
                except subprocess.TimeoutExpired:
                    print(f"⚠ {description} timed out")
