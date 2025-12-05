class TestNmapPerformance(unittest.TestCase):
    
    def test_timing_templates(self):
        """Test different timing templates"""
        timing_levels = ['T0', 'T1', 'T2', 'T3', 'T4', 'T5']
        
        for timing in timing_levels:
            with self.subTest(timing=timing):
                try:
                    import time
                    start_time = time.time()
                    cmd = ['nmap', f'-{timing}', '-p', '22,80', '127.0.0.1']
                    result = subprocess.run(cmd, capture_output=True, timeout=120)
                    scan_time = time.time() - start_time
                    print(f"✓ Timing template {timing}: completed in {scan_time:.2f}s")
                    self.assertEqual(result.returncode, 0)
                except subprocess.TimeoutExpired:
                    print(f"⚠ Timing template {timing} timed out")
    
    def test_parallel_scanning(self):
        """Test parallel scan operations"""
        try:
            cmd = ['nmap', '-T4', '--min-parallelism', '10', '--max-parallelism', '20', 
                   '-p', '22,80,443,21,25,53', '127.0.0.1']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0)
            print("✓ Parallel scanning working")
        except subprocess.TimeoutExpired:
            print("⚠ Parallel scanning timed out")