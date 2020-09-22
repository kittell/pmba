from random import randint

class BulkTruck:
    def __init__(self, berry_type):
        self.load_avg = 75
        self.berry_type = berry_type
        
        if berry_type == 'wet':
            self.useful_ratio = 0.85
        else:
            self.useful_ratio = 0.94
        
class Bin:
    def __init__(self):
        self.volume_filled = 0

class WetBin(Bin):
    def __init__(self):
        self.berry_type = 'wet'
        self.volume = 400
        
class WetDryBin(Bin):
    def __init__(self, berry_type):
        self.berry_type = berry_type
        self.volume = 250
        
class DryBin(Bin):
    def __init__(self):
        self.berry_type = 'dry'
        self.volume = 250
        
class ReceivingFacility:
    def __init__(self, wet_ratio):
        self.wet_ratio = wet_ratio
        self.truck_queue = []
        self.truck_time_remaining = 0
        
    def get_dump_time(self):
        dump_time_min = 5
        dump_time_max = 10
        return randint(dump_time_min, dump_time_max)
        
    def get_test_time(self):
        return 0
    
    def truck_arrives(self):
        r = 0.1 * randint(1, 10)
        berry_type = 'wet'
        if r > self.wet_ratio:
            berry_type = 'dry'
        
        self.truck_queue.append(BulkTruck(berry_type))
        self.truck_time_remaining = self.get_dump_time() + self.get_test_time()
    
    def truck_leaves(self):
        self.truck_queue.pop(0)
    
    def model_step(self, time_step):
        if len(self.truck_queue) == 0:
            self.truck_arrives()
        else:
            self.truck_time_remaining -= time_step
            if self.truck_time_remaining == 0:
                self.truck_leaves()
        
class Model:
    def __init__(self):
        # Rules of the simulation
        self.time_start = 60 * 7
        self.time_end = 60 * 24
        self.time_current = self.time_start
        self.time_step = 1
        self.wet_ratio = 0.7
        self.bins_wet = 3
        self.bins_dry = 16
        self.bins_wetdry = 8
        self.bins_wetdry_dry = 0
        self.bins_wetdry_wet = self.bins_wetdry - self.bins_wetdry_dry
        
        self.rf = ReceivingFacility(self.wet_ratio)
        
    def model_step(self):
        self.rf.model_step(self.time_step)
    
    def model_run(self):
        self.print_current()
        while self.time_current < self.time_end:
            self.time_current += self.time_step
            self.model_step()
            self.print_current()
        
    def print_current(self):
        output = ''
        output += str(self.time_current)
        output += ','
        try:
            output += str(self.rf.truck_queue[0].berry_type)
        except:
            output += 'none'
        output += ','
        output += str(self.rf.truck_time_remaining)
    
        print(output)
    
m = Model()
m.model_run()