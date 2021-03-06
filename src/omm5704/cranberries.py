from random import randint

class BulkTruck:
    def __init__(self, truck_id, berry_type):
        self.truck_id = truck_id
        self.berry_type = berry_type
        self.load_avg = 75
        self.at_dumper = False
        
        if berry_type == 'wet':
            self.useful_ratio = 0.85
        else:
            self.useful_ratio = 0.94
            
        self.initialize_truck_load()
    
    def initialize_truck_load(self):
        self.load_initial = self.load_avg
        self.load_current = self.load_initial
        self.load_dry = self.useful_ratio * self.load_initial
        
    def adjust_load(self, load_diff):
        self.load_current += load_diff
        # TODO: how to handle load < 0
        
       
class Bin:
    def __init__(self):
        self.filled = 0
        self.capacity = 0
        
    def adjust_contents(self, contents_diff):
        remaining = 0
        if contents_diff > 0 :
            adjust_bin = min(self.capacity - self.filled, contents_diff)
        else:
            adjust_bin = min(self.filled, -contents_diff)
            
        self.filled += adjust_bin
        remaining -= adjust_bin
        print(self.berry_type, adjust_bin, self.filled)
        return remaining

class WetBin(Bin):
    def __init__(self):
        super().__init__()
        self.berry_type = 'wet'
        self.capacity = 400
        
class WetDryBin(Bin):
    def __init__(self, berry_type):
        super().__init__()
        self.berry_type = berry_type
        self.capacity = 250
        
class DryBin(Bin):
    def __init__(self):
        super().__init__()
        self.berry_type = 'dry'
        self.capacity = 250

class Dumper:
    def __init__(self, model_settings):
        self.dump_time_min = 5
        self.dump_time_max = 10
        
        self.initialize_dumper()
        
    def assign_truck(self, truck_id):
        self.truck_id = truck_id
        self.time_remaining = randint(self.dump_time_min, self.dump_time_max)
        
    def initialize_dumper(self):
        self.truck_id = None
        self.time_remaining = None
    
    def model_step(self, time_step):
        if self.truck_id is not None:
            self.time_remaining -= time_step
        
class ReceivingFacility:
    def __init__(self, model_settings):
        # Setup truck queue
        self.truck_queue = TruckQueue(model_settings)
        
        # Setup dumpers
        self.dumpers = dict()
        for i in range(0, model_settings['dumpers']):
            self.dumpers[i + 1] = Dumper(model_settings)
        
        # Setup bins
        self.bins_wet = list()
        self.capacity_wet = 0
        self.filled_wet = 0
        self.empty_wet = 0
        
        self.bins_dry = list()
        self.capacity_dry = 0
        self.filled_dry = 0
        self.empty_dry = 0
        
        self.initialize_bins(model_settings)
    
    def initialize_bins(self, model_settings):
        # Wet bins
        for i in range(model_settings['bins_wet']):
            b = WetBin()
            self.capacity_wet += b.capacity
            self.bins_wet.append(b)
            
        # Dry bins
        for i in range(model_settings['bins_dry']):
            b = DryBin()
            self.capacity_dry += b.capacity
            self.bins_dry.append(b)
            
        # Wet/dry bins
        for i in range(model_settings['bins_wetdry_dry']):
            b = WetDryBin('dry')
            self.capacity_dry += b.capacity
            self.bins_dry.append(b)
            
        for i in range(model_settings['bins_wetdry_wet']):
            b = WetDryBin('wet')
            self.capacity_wet += b.capacity
            self.bins_wet.append(b)
        
        self.update_bin_status()
    
    def update_bin_status(self):        
        self.filled_dry = 0
        for b in self.bins_dry:
            self.filled_dry += b.filled
        self.empty_dry = self.capacity_dry - self.filled_dry
            
        self.filled_wet = 0
        for b in self.bins_wet:
            self.filled_wet += b.filled
        self.empty_wet = self.capacity_wet - self.filled_wet
        
    def get_test_time(self):
        return 0
        
    def model_step(self, time_step):
        self.truck_queue.model_step(time_step)
        
        for d in self.dumpers:
            self.dumpers[d].model_step(time_step)
        
        self.assign_trucks_to_dumpers()
        self.transfer_load_to_bin()
        self.dismiss_trucks()
        
    
    def dismiss_trucks(self):
        for d in self.dumpers:
            truck_id = self.dumpers[d].truck_id
            if truck_id is not None:
                if self.dumpers[d].time_remaining <= 0:
                    truck = self.truck_queue.get_truck(truck_id)
                    if truck.load_current <= 0:
                        # Only dismiss the truck if it has transferred its load
                        self.dumpers[d].initialize_dumper()
                        self.truck_queue.truck_leaves(truck_id)
    
    def assign_trucks_to_dumpers(self):
        # Find first open dumper
        for truck in self.truck_queue:
            # Find trucks that are not at a dumper
            if truck.at_dumper == False:
                # Find open dumper
                for d in self.dumpers:
                    if self.dumpers[d].truck_id is None:
                        # Assign a truck to the empty dumper
                        truck.at_dumper = True
                        self.dumpers[d].assign_truck(truck.truck_id)
                        break
                        
        
    def transfer_load_to_bin(self):
        # TODO: useful abstraction: dumper ready for truck to dump, (maybe short delay), leave/pop
        
        # If all the bins are full, skip the rest
        if self.empty_dry == 0 and self.empty_wet == 0:
            return
        
        for d in self.dumpers:
            if self.dumpers[d].truck_id is not None:
                if self.dumpers[d].time_remaining <= 0:
                    # Ready to transfer
                    truck = self.truck_queue.get_truck(self.dumpers[d].truck_id)
                    
                    # Find an open bin, if there is one
                    # TODO: feels like an abstraction hiding here
                    berry_type = truck.berry_type
                    if berry_type == 'dry':
                        if self.empty_dry > 0:
                            load_transfer = min(truck.load_current, self.empty_dry)
                            remaining_transfer = load_transfer
                            
                            for b in self.bins_dry:
                                # Add load to bin
                                remaining_transfer = b.adjust_contents(remaining_transfer)
                                
                    else:
                        if self.empty_wet > 0:
                            load_transfer = min(truck.load_current, self.empty_wet)
                            remaining_transfer = load_transfer
                            
                            for b in self.bins_wet:
                                # Add load to bin
                                remaining_transfer = b.adjust_contents(remaining_transfer)
                    
                    # Remove load from truck
                    truck.adjust_load(-load_transfer)
                    # Update bin status
                    self.update_bin_status()
                    
    
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
        
        self.wet_ratio = model_settings['wet_ratio']
        self.total_count = 0
        self.total_wait = 0
    
    def model_step(self, time_step):

        self.truck_arrives()
        self.truck_waits(time_step)
    
    def get_truck(self, get_id):
        for truck in self:
            if truck.truck_id == get_id:
                return truck
            
#         return None
    
    def truck_waits(self, time_step):
        # Count the total amount of wait time of trucks over the course of the model
        waiting = len(self) - 1
        if waiting > 0:
            self.total_wait += time_step * waiting
    
    def truck_arrives(self):
        # Rules for truck arrival
        #   - truck queue is empty
        arrives = False
#         if len(self) == 0:
#             arrives = True


        # For now: a truck arrives every minute
        arrives = True
        if arrives:
            self.total_count += 1
            
            r = 0.1 * randint(1, 10)
            berry_type = 'wet'
            if r > self.wet_ratio:
                berry_type = 'dry'
            
            self.append(BulkTruck(self.total_count, berry_type))
#             self.time_remaining.append(model_settings['dump_time'] + model_settings['test_time'])
    
    def truck_leaves(self, remove_id):
        for t in range(len(self)):
            if self[t].truck_id == remove_id:
                self.pop(t)
                break
                
                
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
        self.model_settings['dumpers'] = 5
        
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
        self.receiving = ReceivingFacility(self.model_settings)
        
    def model_step(self):
        self.update_random_model_settings()
        self.receiving.model_step(self.time_step)
    
    def model_run(self):
        self.print_output()
        while self.time_current < self.time_end:
            self.time_current += self.time_step
            self.model_step()
            self.print_output()
        
    def update_random_model_settings(self):
#         self.model_settings['dump_time'] = self.receiving.get_dump_time()
#         self.model_settings['test_time'] = self.receiving.get_test_time()
        pass
        
    def get_test_time(self):
        return 0
    
    def print_output(self):
        output = ''
        output += str(self.time_current)
        
        output += '; '
        output += self.receiving.truck_queue.print_output()
        
        output += '; '
        output += self.receiving.print_output()
    
        print(output)
    
m = Model()
m.model_run()