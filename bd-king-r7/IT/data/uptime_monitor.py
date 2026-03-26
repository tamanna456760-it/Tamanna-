# uptime_monitor.py - Legitimate website monitoring
import requests
import time
import smtplib
from email.mime.text import MimeText

class WebsiteMonitor:
    """Monitor website availability for legitimate purposes"""
    
    def __init__(self, websites_to_monitor):
        self.websites = websites_to_monitor
        self.uptime_log = {}
    
    def check_website(self, url, timeout=10):
        """Check if a website is accessible"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            response_time = time.time() - start_time
            
            return {
                'status': 'UP' if response.status_code == 200 else 'DOWN',
                'response_time': response_time,
                'status_code': response.status_code,
                'timestamp': time.time()
            }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'DOWN',
                'error': str(e),
                'timestamp': time.time()
            }
    
    def monitor_websites(self, interval=300):
        """Continuously monitor websites"""
        while True:
            for website in self.websites:
                result = self.check_website(website)
                self.uptime_log[website] = result
                
                if result['status'] == 'DOWN':
                    print(f"ALERT: {website} is DOWN - {result.get('error', 'Unknown error')}")
                else:
                    print(f"OK: {website} - {result['response_time']:.2f}s")
            
            time.sleep(interval)

# Legitimate usage - monitor your own websites
if __name__ == "__main__":
    my_websites = [
        "https://google.com",
        "https://github.com", 
        "https://stackoverflow.com"
    ]
    
    monitor = WebsiteMonitor(my_websites)
    monitor.monitor_websites(interval=60)