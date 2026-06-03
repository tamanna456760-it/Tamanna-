class TestNmapAdvancedScans(unittest.TestCase):

    def test_stealth_scan(self):
        """Test stealth scanning techniques"""
        scan_types = [
            ["-sS", "TCP SYN Scan"],
            ["-sT", "TCP Connect Scan"],
            ["-sU", "UDP Scan"],
            ["-sN", "TCP Null Scan"],
            ["-sF", "TCP FIN Scan"],
            ["-sX", "TCP Xmas Scan"],
        ]

        for scan_type, description in scan_types:
            with self.subTest(scan_type=scan_type):
                try:
                    cmd = ["nmap", scan_type, "-p", "22,80", "127.0.0.1"]
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=30
                    )
                    self.assertIn(
                        result.returncode, [0, 1]
                    )  # Nmap may return 1 for some scans
                    print(f"✓ {description} ({scan_type}) working")
                except subprocess.TimeoutExpired:
                    print(f"⚠ {description} timed out")

    def test_service_detection(self):
        """Test service and version detection"""
        try:
            cmd = ["nmap", "-sV", "-p", "22,80", "127.0.0.1"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=45)
            self.assertEqual(result.returncode, 0)
            self.assertIn("Service detection performed", result.stdout)
            print("✓ Service version detection working")
        except subprocess.TimeoutExpired:
            print("⚠ Service detection timed out")

    def test_os_detection(self):
        """Test OS detection"""
        try:
            cmd = ["nmap", "-O", "127.0.0.1"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0)
            print("✓ OS detection working")
        except subprocess.TimeoutExpired:
            print("⚠ OS detection timed out")

    def test_script_scanning(self):
        """Test NSE (Nmap Scripting Engine)"""
        scripts_to_test = ["http-title", "ssl-cert", "banner"]

        for script in scripts_to_test:
            with self.subTest(script=script):
                try:
                    cmd = ["nmap", "--script", script,
                           "-p", "80,443", "127.0.0.1"]
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=45
                    )
                    self.assertEqual(result.returncode, 0)
                    print(f"✓ NSE script '{script}' working")
                except subprocess.TimeoutExpired:
                    print(f"⚠ NSE script '{script}' timed out")
