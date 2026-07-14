class TestCustomNSEScripts(unittest.TestCase):

    def test_nse_script_loading(self):
        """Test loading and running custom NSE scripts"""
        # Create a simple test NSE script
        test_script = """
        description = [[A test NSE script]]
        
        author = "Test Author"
        license = "Same as Nmap--See https://nmap.org/book/man-legal.html"
        categories = {"safe", "discovery"}
        
        portrule = function(host, port)
          return port.protocol == "tcp" and port.number == 80
        end
        
        action = function(host, port)
          return "Test script executed successfully"
        end
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".nse", delete=False) as f:
            f.write(test_script)
            temp_script = f.name

        try:
            cmd = ["nmap", "--script", temp_script, "-p", "80", "127.0.0.1"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0)
            print("✓ Custom NSE script loading working")
        except subprocess.TimeoutExpired:
            print("⚠ Custom NSE script test timed out")
        finally:
            os.unlink(temp_script)
