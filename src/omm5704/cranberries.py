from random import randint
from prompt_toolkit.key_binding.bindings.named_commands import self_insert

class BulkTruck:
    def __init__(self, berry_type):
        self.load_avg = 75
        self.berry_type = berry_type
        
        if berry_type == 'wet':
            self.useful_ratio = 0.85
        else:
            self.useful_ratio = 0.94
            
        self.initialize_truck_load()
    
    def initialize_truck_load(self):
        self.load_initial = self.load_avg
        self.load_current = self.load_initial
        self.load_dry = self.useful_ratio * self.load_initial
        
       
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
    def __init__(self, model_settings):
        self.dump_time_min = 5
        self.dump_time_max = 10
        
        # Setup bins
        self.bins_wet = list()
        self.capacity_wet = 0
        self.filled_wet = 0
        
        self.bins_dry = list()
        self.capacity_dry = 0
        self.filled_dry = 0
        
        self.initialize_bins(model_settings)
    
    def initialize_bins(self, model_settings):
        # Wet bins
        for i in range(model_settings['bins_wet']):
            b = WetBin()
            self.capacity_wet += b.volume
            self.bins_wet.append(b)
            
        # Dry bins
        for i in range(model_settings['bins_dry']):
            b = DryBin()
            self.capacity_dry += b.volume
            self.bins_wet.append(b)
            
        # Wet/dry bins
        for i in range(model_settings['bins_wetdry_dry']):
            b = WetDryBin('dry')
            self.capacity_dry += b.volume
            self.bins_dry.append(b)
            
        for i in range(model_settings['bins_wetdry_wet']):
            b = WetDryBin('wet')
            self.capacity_wet += b.volume
            self.bins_wet.append(b)
                     
    
    def get_dump_time(self):
        return randint(self.dump_time_min, self.dump_time_max)
        
    def get_test_time(self):
        return 0
        
    def model_step(self, time_step):
        self.transfer_load_to_bin()
        
    def transfer_load_to_bin(self):
        pass
    
    def print_output(self):
        output = ''
        output += 'dry:'
        output += str(self.filled_dry) + '/' + str(self.capacity_dry)
        output += ','
        output += 'wet:'
        output += str(self.filled_wet) + '/' + str(self.capacity_wet)
        
        return output
        

class TruckQueue(list):
    def __init__(self, model_settings):
        self.time_remaining = list()
        
        self.wet_ratio = model_settings['wet_ratio']
        self.total_count = 0
        self.total_wait = 0
    
    def model_step(self, time_step, model_settings):
        if len(self) > 0:
            self.time_remaining[0] -= time_step
        
        self.truck_leaves()
        self.truck_arrives(model_settings)
        self.truck_waits(time_step)
    
    def truck_waits(self, time_step):
        # Count the total amount of wait time of trucks over the course of the model
        waiting = len(self) - 1
        if waiting > 0:
            self.total_wait += time_step * waiting
    
    def truck_arrives(self, model_settings):
        # Rules for truck arrival
        #   - truck queue is empty
        arrives = False
        if len(self) == 0:
            arrives = True

        if arrives:
            self.total_count += 1
            
            r = 0.1 * randint(1, 10)
            berry_type = 'wet'
            if r > self.wet_ratio:
                berry_type = 'dry'
            
            self.append(BulkTruck(berry_type))
            self.time_remaining.append(model_settings['dump_time'] + model_settings['test_time'])
    
    def truck_leaves(self):
        if len(self) > 0:
            if self.time_remaining[0] == 0:
                self.pop(0)
                self.time_remaining.pop(0)
                
                
    def print_output(self):
        output = ''
        output += str(len(self))
        output += ','
        output += str(self.total_count)
        
        return output
    
        
class Model:
    def __init__(self):
        # MODEL SETTINGS
        self.model_settings = dict()
        
        # Time
        self.time_start = 60 * 7
        self.time_end = 60 * 24
        self.time_current = self.time_start
        self.time_step = 1
        
        # Trucks
        self.model_settings['wet_ratio'] = 0.7
        
        # Receiving
        
        
        # Holding
        self.model_settings['bins_wet'] = 3
        self.model_settings['bins_dry'] = 16
        self.model_settings['bins_wetdry'] = 8
        self.model_settings['bins_wetdry_dry'] = 0
        self.model_settings['bins_wetdry_wet'] = self.model_settings['bins_wetdry'] - self.model_settings['bins_wetdry_dry']
        
        # Processing
        
        # Separating
        
        # Bulking and bagging
        
        # INITIALIZE
        self.truck_queue = TruckQueue(self.model_settings)
        self.receiving = ReceivingFacility(self.model_settings)
        
    def model_step(self):
        self.update_random_model_settings()
        self.truck_queue.model_step(self.time_step, self.model_settings)
        self.receiving.model_step(self.time_step, self.truck_queue)
    
    def model_run(self):
        self.print_output()
        while self.time_current < self.time_end:
            self.time_current += self.time_step
            self.model_step()
            self.print_output()
        
    def update_random_model_settings(self):
        self.model_settings['dump_time'] = self.receiving.get_dump_time()
        self.model_settings['test_time'] = self.receiving.get_test_time()
        
    def get_test_time(self):
        return 0
    
    def print_output(self):
        output = ''
        output += str(self.time_current)
        
        output += '; '
        output += self.truck_queue.print_output()
        
        output += '; '
        output += self.receiving.print_output()
    
        print(output)
    
m = Model()
m.model_run()