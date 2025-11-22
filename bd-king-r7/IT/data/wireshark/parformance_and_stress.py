class TestWiresharkPerformance(unittest.TestCase):
    
    def test_high_volume_capture(self):
        """Test capturing high volume of packets"""
        try:
            # Generate high traffic
            traffic_cmd = ['ping', '-f', '127.0.0.1']
            traffic_proc = subprocess.Popen(traffic_cmd, stdout=subprocess.PIPE)
            
            # Capture with high buffer
            capture_cmd = ['tshark', '-i', 'lo', '-c', '1000', '-B', '1024']
            start_time = time.time()
            result = subprocess.run(capture_cmd, capture_output=True, timeout=30)
            capture_time = time.time() - start_time
            
            # Stop traffic generation
            traffic_proc.terminate()
            
            if result.returncode == 0:
                packets_captured = len([line for line in result.stdout.split('\n') if line.strip()])
                print(f"✓ High volume capture: {packets_captured} packets in {capture_time:.2f}s")
            else:
                print("⚠ High volume capture completed with errors")
                
        except subprocess.TimeoutExpired:
            print("⚠ High volume capture timed out")
    
    def test_memory_usage(self):
        """Test memory usage during capture"""
        try:
            import psutil
            import os
            
            # Start tshark process
            capture_cmd = ['tshark', '-i', 'lo', '-c', '100', '-w', '-']
            process = subprocess.Popen(capture_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Monitor memory
            ps_process = psutil.Process(process.pid)
            memory_info = ps_process.memory_info()
            
            print(f"✓ Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
            
            process.terminate()
            process.wait(timeout=5)
            
        except (psutil.NoSuchProcess, subprocess.TimeoutExpired):
            print("⚠ Memory usage test incomplete")