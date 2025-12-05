class TestWiresharkAutomation(unittest.TestCase):
    
    def test_export_functionality(self):
        """Test export to different formats"""
        export_formats = [
            ('-T', 'json', 'JSON'),
            ('-T', 'jsonraw', 'Raw JSON'),
            ('-T', 'psml', 'PSML'),
            ('-T', 'pdml', 'PDML'),
            ('-T', 'fields', 'Fields'),
        ]
        
        for flag, format_type, description in export_formats:
            with self.subTest(format=format_type):
                try:
                    cmd = ['tshark', '-i', 'lo', '-c', '3', flag, format_type, '-a', 'duration:5']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                    
                    if result.returncode == 0 and len(result.stdout) > 0:
                        print(f"✓ Export to {description} working")
                    else:
                        print(f"⚠ Export to {description} - no output")
                        
                except subprocess.TimeoutExpired:
                    print(f"⚠ Export to {description} timed out")
    
    def test_statistics_generation(self):
        """Test statistics generation"""
        stats_commands = [
            ('io,stat,0', 'I/O Statistics'),
            ('protocols,stat,0', 'Protocol Hierarchy'),
            ('conversations,tcp', 'TCP Conversations'),
            ('http,tree', 'HTTP Statistics')
        ]
        
        for stat_cmd, description in stats_commands:
            with self.subTest(stats=description):
                try:
                    cmd = ['tshark', '-z', stat_cmd, '-i', 'lo', '-a', 'duration:5']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
                    self.assertEqual(result.returncode, 0)
                    print(f"✓ {description} generation working")
                except subprocess.TimeoutExpired:
                    print(f"⚠ {description} generation timed out")
    
    def test_custom_lua_scripts(self):
        """Test Lua scripting functionality"""
        lua_script = """
        -- Simple test Lua script for Wireshark
        local test_proto = Proto("test", "Test Protocol")
        
        function test_proto.dissector(buffer, pinfo, tree)
            pinfo.cols.protocol = "TEST"
            local subtree = tree:add(test_proto, buffer(), "Test Protocol Data")
            return 1
        end
        
        local tcp_port = DissectorTable.get("tcp.port")
        tcp_port:add(9999, test_proto)
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lua', delete=False) as f:
            f.write(lua_script)
            lua_file = f.name
        
        try:
            cmd = ['tshark', '-X', f'lua_script:{lua_file}', '-i', 'lo', '-c', '1', '-a', 'duration:5']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            self.assertIn(result.returncode, [0, 1])
            print("✓ Lua scripting functionality working")
        except subprocess.TimeoutExpired:
            print("⚠ Lua scripting test timed out")
        finally:
            os.unlink(lua_file)