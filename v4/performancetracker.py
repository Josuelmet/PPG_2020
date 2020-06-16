import time


class PerformanceTracker():
        
    def reset(self):
        self.previous_time = time.time()
        self.total_time = 0
        self.call_count = 0
        
    def __init__(self):
        self.reset()
        
        
    def track_performance(self, print_period=True, print_frequency=True):
        
        current_time = time.time()
        elapsed_time = current_time - self.previous_time
        
        self.total_time = self.total_time + elapsed_time
        self.previous_time = current_time
        self.call_count = self.call_count + 1
        
        if (print_period):
            print('This loop took {} seconds'.format(elapsed_time))
        if (print_frequency):
            print('Average loop frequency: {}'.format(self.call_count / self.total_time))
        
        
        
'''
A simple test of the performance tracker's capabilities.
'''
if __name__ == '__main__':
    tracker = PerformanceTracker()
    
    for i in range(10):
        time.sleep(0.1)
        tracker.track_performance()
