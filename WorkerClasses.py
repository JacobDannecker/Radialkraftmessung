from All_Imports import *

class TempControl(QObject):
    # 1 = stoped 2 = running 3 = done 
    temp_control_status = pyqtSignal(int)
    set_target_temp_lcd = pyqtSignal(int)
    enable_manual_button = pyqtSignal(bool)
    stop_running = False
    hold_time = (60*1000)
    now_temp = 0
    hysteresis = 0.5
    cwd = str(os.path.abspath("."))
    # Set up bricklets
    bricklet_ids_file = open(cwd + "/Software_RasPi/bricklet_ids.txt")
    with(bricklet_ids_file) as f:
        lines = f.readlines()
        words = [w.split() for w in lines]
        bricklet_ids_dict = dict(words)
    ip_con = IPConnection()
    ip_con.connect("localhost", 4223)
    relay_bricklet = BrickletIndustrialDualRelay(bricklet_ids_dict["relaybricklet"], ip_con) 


    def stop(self):
        self.stop_running = True 
        self.relay_bricklet.set_value(False, False)
        self.temp_control_status.emit(1)

    @pyqtSlot(tuple)
    def start(self, control_data):
        control_mode = control_data[0]
        target_temp_manual = control_data[1]
        self.temp_control_status.emit(2)
        self.stop_running = False

        if control_mode == 0:
            self.enable_manual_button.emit(False)
            while self.stop_running == False:
                self.control(target_temp_manual)
        else:
            pass
            # May add other controlmodes in future

        self.stop_running = False
        self.enable_manual_button.emit(True)
   

    def control(self, target_temp):
        self.set_target_temp_lcd.emit(target_temp)
        if self.now_temp < (target_temp - self.hysteresis):
             # Fan on, Heater on
             self.relay_bricklet.set_value(True, True)
        elif self.now_temp > (target_temp + self.hysteresis):
             # Fan on, Heater off
             self.relay_bricklet.set_value(False, True)

        if ((self.now_temp > target_temp - self.hysteresis) and 
            (self.now_temp < target_temp + self.hysteresis)):
            self.temp_control_status.emit(3)
        else:
            self.temp_control_status.emit(2)
        time.sleep(0.3)
 

    def setFilename(self, filename):
        self.filename = filename

    def updateTemp(self, temp):
        self.now_temp = temp
    
    def updateHysteresis(self, hysteresis):
        self.hysteresis = hysteresis
#------------------------------------------------------------------------------

class ReadData(QObject):
    tell_filename = pyqtSignal(str)
    tell_temp_lcd = pyqtSignal(float)
    tell_temp_control = pyqtSignal(float)
    tell_force_left_lcd = pyqtSignal(float)
    tell_force_right_lcd = pyqtSignal(float)
    read_data_status = pyqtSignal(int)
    calibration_weight_left = 0
    calibraion_weight_right = 0
    tara_left = -60
    tara_right = -40
    stop_running = True 
    cwd = str(os.path.abspath("."))
    
    # Set up bricklets
    bricklet_ids_file = open(cwd + "/Software_RasPi/bricklet_ids.txt")
    with(bricklet_ids_file) as f:
        lines = f.readlines()
        words = [w.split() for w in lines]
        bricklet_ids_dict = dict(words)

    ip_con = IPConnection()
    ip_con.connect("localhost", 4223)
    temp_bricklet = BrickletIndustrialPTC(bricklet_ids_dict["tempbricklet"], ip_con) 
    load_cell_bricklet_right = BrickletLoadCellV2(bricklet_ids_dict["loadcellright"], ip_con)
    load_cell_bricklet_left = BrickletLoadCellV2(bricklet_ids_dict["loadcellleft"], ip_con)

    def stopReadData(self):
        self.stop_running = True 
        # Tell main thread, that self.stop_running was changed
        self.read_data_status.emit(1)
       
    
    def calibrateLoadCell(self, calibration_data):
        loadcell = calibration_data[0]
        calibration_weight = calibration_data[1]
        if loadcell == 0:
            self.load_cell_bricklet_left.calibrate(calibration_weight)
        elif loadcell == 1:
            self.load_cell_bricklet_right.calibrate(calibration_weight)
    
    def tareLoadCells(self):
        self.tara_left = self.load_cell_bricklet_left.get_weight() 
        self.tara_right = self.load_cell_bricklet_right.get_weight() 

    @pyqtSlot()
    def readData(self):
        fieldnames = ["Time/s", "Force_left/N", "Force_right/N", "Temperature/degC"]
        file =  self.cwd + "/Software_RasPi/Data/" + "Werte-vom-" + str(datetime.now())
        self.tell_filename.emit(file)
        write_data_counter = 101 

        with open(Path(file), "w") as csv_file:
           csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames) 
           csv_writer.writeheader()
        # set timeoffset
        time_offset = timer()
        
        self.stop_running = False 

        # Inform mainthread that readData is running
        self.read_data_status.emit(0)

        while self.stop_running == False:
            # Get real data here lateron form sensors                
            force_right = ((self.load_cell_bricklet_right.get_weight() - self.tara_right) /1000)*9.81
            force_left = ((self.load_cell_bricklet_left.get_weight() -self.tara_left) /1000)*9.81
            temperature = self.temp_bricklet.get_temperature()/100
            self.tell_temp_control.emit(temperature)
            self.tell_temp_lcd.emit(temperature)
            self.tell_force_left_lcd.emit(force_left)
            self.tell_force_right_lcd.emit(force_right)

            # Only write every nth datapoint to file
            if write_data_counter > 30:
                with open(file, "a") as csv_file:
                    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    # Get timestamp in seconds
                    current_time = timer() - time_offset 
                    
                    data = {"Time/s": current_time,
                            "Force_left/N": force_left,
                            "Force_right/N": force_right,
                            "Temperature/degC": temperature
                            }
                    csv_writer.writerow(data)
                    write_data_counter = 0

            write_data_counter += 1
            # May be removed later 
            time.sleep(0.01)
        # Emited when reading data was stoped
        self.read_data_status.emit(2)

        
#------------------------------------------------------------------------------


