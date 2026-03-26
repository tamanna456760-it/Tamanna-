# performance_monitor.py - Application performance monitoring
import time
import threading
from dataclasses import dataclass
from typing import Dict, List
import statistics

@dataclass
class PerformanceMetrics:
    response_time: float
    throughput: float
    error_rate: float
    timestamp: float

class APMMonitor:
    """Application Performance Monitoring for your own applications"""
    
    def __init__(self):
        self.metrics: Dict[str, List[PerformanceMetrics]] = {}
        self.lock = threading.Lock()
    
    def record_metric(self, endpoint: str, response_time: float, 
                     success: bool = True):
        """Record performance metrics for an endpoint"""
        with self.lock:
            if endpoint not in self.metrics:
                self.metrics[endpoint] = []
            
            # Calculate current metrics
            recent_metrics = self.metrics[endpoint][-100:]  # Last 100 requests
            total_requests = len(recent_metrics) + 1
            error_count = sum(1 for m in recent_metrics if m.error_rate > 0)
            error_rate = (error_count + (0 if success else 1)) / total_requests
            
            metric = PerformanceMetrics(
                response_time=response_time,
                throughput=total_requests / 60,  # Requests per minute
                error_rate=error_rate,
                timestamp=time.time()
            )
            
            self.metrics[endpoint].append(metric)
    
    def get_performance_report(self):
        """Generate performance report"""
        report = {}
        for endpoint, metrics in self.metrics.items():
            if metrics:
                recent = metrics[-50:]  # Last 50 metrics
                report[endpoint] = {
                    'avg_response_time': statistics.mean(m.response_time for m in recent),
                    'p95_response_time': sorted([m.response_time for m in recent])[int(0.95 * len(recent))],
                    'current_error_rate': recent[-1].error_rate if recent else 0,
                    'throughput': recent[-1].throughput if recent else 0
                }
        return report

# Usage example for legitimate application monitoring
if __name__ == "__main__":
    monitor = APMMonitor()
    
    # Simulate monitoring some endpoints
    endpoints = ['/api/users', '/api/products', '/api/orders']
    for i in range(100):
        for endpoint in endpoints:
            response_time = 0.1 + (i % 10) * 0.01  # Simulated response time
            success = i % 20 != 0  # Simulate occasional errors
            monitor.record_metric(endpoint, response_time, success)
        
        time.sleep(0.1)
    
    print("Performance Report:")
    report = monitor.get_performance_report()
    for endpoint, metrics in report.items():
        print(f"{endpoint}: {metrics}")