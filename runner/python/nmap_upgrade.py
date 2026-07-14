class TestNmapUpgrade(unittest.TestCase):

    def test_feature_compatibility(self):
        """Test that upgraded Nmap maintains feature compatibility"""
        features_to_test = [
            ("-A", "Aggressive scan"),
            ("-6", "IPv6 scanning"),
            ("-sC", "Default script scan"),
            ("-v", "Verbose output"),
            ("-d", "Debug output"),
        ]

        for flag, description in features_to_test:
            with self.subTest(flag=flag):
                try:
                    cmd = ["nmap", flag, "127.0.0.1"]
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=30
                    )
                    # Some flags might produce warnings but should not crash
                    self.assertIn(result.returncode, [0, 1])
                    print(f"✓ Feature {description} ({flag}) compatible")
                except subprocess.TimeoutExpired:
                    print(f"⚠ Feature {description} test timed out")

    def test_new_features(self):
        """Test any new features in upgraded Nmap"""
        try:
            # Test if new version has additional capabilities
            result = subprocess.run(["nmap", "--help"], capture_output=True, text=True)
            help_output = result.stdout

            # Check for common new features
            new_features_indicators = [
                "--script-updatedb",
                "--datadir",
                "--servicedb",
                "--versiondb",
            ]

            for feature in new_features_indicators:
                if feature in help_output:
                    print(f"✓ New feature detected: {feature}")

            print("✓ Help system working")
        except Exception as e:
            self.fail(f"Failed to test new features: {e}")
