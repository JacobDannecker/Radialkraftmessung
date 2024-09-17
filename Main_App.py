#!/usr/bin/env python3
# Main_App.py
# Import from all_imports.py
from All_Imports import *
from WorkerClasses import *
from MainWindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):

    # Create Signals for controlling threads
    start_temp_control = pyqtSignal(tuple)
    stop_temp_control = pyqtSignal()
    read_data = pyqtSignal()
    stop_read_data = pyqtSignal()
    calibrate_loadcell = pyqtSignal(tuple)
    update_hysteresis = pyqtSignal(int)
    taraSig = pyqtSignal()

    # Structure 
    filename = ""
    restart_flag = 0
    read_data_status = 0 
    # Plot
    x_lim_default = 15*60
    y_lim_temp_default = 120 
    y_lim_force_default = 5 
    # Tinkerforge
    host = "localhost"
    port = 4223

    # Paths
    cwd = str(os.path.abspath("."))

    # Animation
    animation_interval = 100
    def __init__(self):
        super().__init__()

        # Set up window
        self.setupUi(self)
        self.showFullScreen()
        # Set up buttons in MainWindow

        # Set up Threads
        self.temp_control_worker = TempControl()
        self.temp_thread = QThread()
        self.read_data_worker = ReadData()
        self.read_data_thread = QThread()

        # Connect signals workerthreads -> mainthread 
        self.temp_control_worker.temp_control_status.connect(
                self.updateControlStatus)
        self.read_data_worker.tell_temp_lcd.connect(self.updateNowTempLCD)
        self.read_data_worker.tell_force_left_lcd.connect(self.updateForceLeftLCD)
        self.read_data_worker.tell_force_right_lcd.connect(self.updateForceRightLCD)
        self.read_data_worker.tell_filename.connect(self.updateFilename)
        self.read_data_worker.read_data_status.connect(self.statusReadData)
        self.temp_control_worker.set_target_temp_lcd.connect(self.setTargetTempLCD)
        self.temp_control_worker.enable_manual_button.connect(self.enableManualControl)

        # Connect signals mainthread -> workerthreads 
        self.start_temp_control.connect(self.temp_control_worker.start)
        self.stop_temp_control.connect(self.temp_control_worker.stop)
        self.read_data.connect(self.read_data_worker.readData)
        self.stop_read_data.connect(self.read_data_worker.stopReadData)
        self.calibrate_loadcell.connect(self.read_data_worker.calibrateLoadCell)
        self.update_hysteresis.connect(self.temp_control_worker.updateHysteresis)
        self.taraSig.connect(self.read_data_worker.tareLoadCells)

        # Connect signals workerthreads -> workerthreads
        self.read_data_worker.tell_temp_control.connect(self.temp_control_worker.updateTemp)

        # Move workers to Threads
        self.temp_control_worker.moveToThread(self.temp_thread)
        self.read_data_worker.moveToThread(self.read_data_thread)

        # Start Threads
        self.read_data_thread.start()
        self.temp_thread.start()

        # Set up control status label 
        self.green_dot = QPixmap(self.cwd + "/Software_RasPi/Pics/green_dot.png").scaled(25, 25)
        self.yellow_dot = QPixmap(self.cwd + "/Software_RasPi/Pics/yellow_dot.png").scaled(25, 25)
        self.red_dot = QPixmap(self.cwd + "/Software_RasPi/Pics/red_dot.png").scaled(25, 25)

        self.control_status_label = QLabel()
        self.info_layout.addWidget(self.control_status_label)
        self.control_status_label.hasScaledContents()
        self.control_status_label.setMaximumHeight(25)
        self.control_status_label.setMaximumWidth(25)
        self.control_status_label.setPixmap(self.red_dot)
        
        # Set up Buttons in Main Window
        self.manual_apply_button.clicked.connect(self.manualControl)
        self.calibrate_zero_left_button.clicked.connect(self.calibrateZeroLeft)        
        self.calibrate_weight_left_button.clicked.connect(self.calibrateWeightLeft)        
        self.calibrate_zero_right_button.clicked.connect(self.calibrateZeroRight)        
        self.calibrate_weight_right_button.clicked.connect(self.calibrateWeightRight)        
        self.stop_temp_control_button.clicked.connect(self.stopTempControl)
        self.export_button.clicked.connect(self.exportData)         
        self.tara_button.clicked.connect(self.tara)
        
        # set up Spinboxes
        self.hysteresis_spinbox.valueChanged.connect(self.updateHysteresis)

        self.read_data.emit()
        self.stopTempControl() 
        # Start and animation
        self.plot_button.clicked.connect(self.startPlot)
        
        
    def closeEvent(self, event):
        """Reimplement the closing event to display a
        QMessageBox before closing."""
        answer = QMessageBox.question(self, "Quit Application?",
                                      "Are you sure you want to QUIT?",
                                      QMessageBox.StandardButton.No |
                                      QMessageBox.StandardButton.Yes,
                                      QMessageBox.StandardButton.Yes)
        if answer == QMessageBox.StandardButton.Yes:
            self.stop_read_data.emit()
            time.sleep(0.5)
            event.accept()
        if answer == QMessageBox.StandardButton.No:
            event.ignore()

# Methods for MainWindow ------------------------------------------------------
    def stopTempControl(self):
        self.stop_temp_control.emit()

    def manualControl(self):
        control_mode = 0
        target_temp_manual = self.target_temp_manual_spinbox.value()
        control_data = (control_mode, target_temp_manual) 
        self.start_temp_control.emit(control_data)
   
    def setTargetTempLCD(self, temp):
        self.target_temp_lcd.display(temp)
   
    def enableManualControl(self, flag):
        self.manual_apply_button.setEnabled(flag) 

    def exportData(self):
        subprocess.run(["nemo"])
    
    def tara(self):
        self.taraSig.emit()

# Methods connected to signals from workerthreads ----------------------------- 

    def updateControlStatus(self, status):
        """Gives feedback weather controll loop is active or not."""
        if status == 1:
            self.control_status_label.setPixmap(self.red_dot)
        elif status == 2:
            self.control_status_label.setPixmap(self.yellow_dot)
        elif status == 3:
            self.control_status_label.setPixmap(self.green_dot)

    def stopReadData(self):
        self.stop_read_data.emit()

    def updateFilename(self, filename):
        self.filename = filename

    def statusReadData(self, status):
        self.read_data_status = status

    def updateNowTempLCD(self, now_temp):
        self.temp_lcd.display(now_temp)

    def updateForceLeftLCD(self, force_left):
        self.force_left_lcd.display(force_left)

    def updateForceRightLCD(self, force_right):
        self.force_right_lcd.display(force_right)
    
    def updateHysteresis(self):
        hysteresis = self.hysteresis_spinbox.value()
        self.update_hysteresis.emit(hysteresis)

# Plot and animation ---------------------------------------------------------- 
    def setUpAnimation(self):
        self.x_lim = self.x_lim_default 
        self.y_lim_temp = self.y_lim_temp_default 
        self.y_lim_force = self.y_lim_force_default
        self.figure = Figure()
        self.ax_temp = self.figure.add_subplot()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas)
        self.plot_layout.addWidget(self.toolbar)
        self.plot_layout.addWidget(self.canvas)
        
        # ax_temp 
        self.ax_temp.set(xlim=(0, self.x_lim), ylim=(0, self.y_lim_temp))
        self.ax_temp.set_ylabel("Temp / degC", color="k")
        self.ax_temp.set_xlabel("Time / s")
        self.ax_temp.locator_params(tight=True, nbins=10)
        self.ax_temp.grid()

        # ax_force 
        self.ax_force = self.ax_temp.twinx()
        self.ax_force.set(ylim=(-5, self.y_lim_force))
        self.ax_force.set_ylabel("Force / N")
        self.ax_force.spines["left"].set_position(("axes", -0.09))
        self.ax_force.yaxis.set_label_position("left")
        self.ax_force.yaxis.set_ticks_position("left")

        self.force_right_points, = self.ax_force.plot([],[],  marker="none", 
                                                        linestyle="-",
                                                        linewidth=0.8,
                                                        color="g",
                                                        markeredgecolor="g",
                                                        markerfacecolor="g",
                                                        label="F_right")

        self.force_left_points, = self.ax_force.plot([], [],  marker="none", 
                                                        linestyle="-",
                                                        linewidth=0.8,
                                                        color="r",
                                                        markeredgecolor="r",
                                                        markerfacecolor="r",
                                                        label="F_left")


        self.temp_points, = self.ax_temp.plot([],[],    marker="none", 
                                                        linestyle="-",
                                                        linewidth=0.8,
                                                        color="b",
                                                        markeredgecolor="k",
                                                        markerfacecolor="k",
                                                        label="Temp")
        
        self.ax_temp.legend(loc="lower right")
        self.ax_force.legend(loc="upper right")


    def animate(self, i):
        data = pd.read_csv(self.filename)

        elapsed_time = data["Time/s"]
        f_l = data["Force_left/N"]
        f_r = data["Force_right/N"]
        temp = data["Temperature/degC"]
        
        # Rescaling x_axis
        if elapsed_time.iloc[-1] > self.x_lim:
            self.x_lim += 5*60 
            self.ax_temp.set(xlim=(0, self.x_lim))
        
        # Rescaling y_axis
        if f_l.iloc[-1] > self.y_lim_force: 
            self.y_lim_force += f_l.iloc[-1]/3
            self.ax_force.set(ylim=(0, self.y_lim_force))

        if f_r.iloc[-1] > self.y_lim_force:
            self.y_lim_force += f_l.iloc[-1]/3 
            self.ax_force.set(ylim=(0, self.y_lim_force))

        if temp.iloc[-1] > self.y_lim_temp:
            self.y_lim_temp += temp.iloc[-1]/3
            self.ax_temp.set(ylim=(0, self.y_lim_temp))


        self.force_left_points.set_data(elapsed_time, f_l)
        self.force_right_points.set_data(elapsed_time, f_r)
        self.temp_points.set_data(elapsed_time, temp)
        self.canvas.draw()
        
        return (self.force_left_points, self.force_right_points,
                self.temp_points)
        

    def startPlot(self):
        if self.restart_flag == 0:
            self.restart_flag +=1
            self.plot_button.setText("Restart Plot") 
            self.setUpAnimation()
            self.anim = animation.FuncAnimation(self.figure, self.animate, 
                                                 interval=self.animation_interval, blit=True,
                                                 cache_frame_data=False) 
        else:
            self.anim.pause()
            self.stop_read_data.emit()
            self.read_data.emit()
            time.sleep(1)
            self.x_lim = self.x_lim_default
            self.y_lim_force = self.y_lim_force_default
            self.y_lim_temp = self.y_lim_temp_default
            self.ax_temp.set(xlim=(0, self.x_lim), ylim=(0, self.y_lim_temp))
            self.ax_force.set(ylim=(0, self.y_lim_force))
            self.anim = animation.FuncAnimation(self.figure, self.animate, 
                                                 interval=self.animation_interval, blit=True,
                                                 cache_frame_data=False)


        

    def calibrateZeroLeft(self):
        self.calibrate_zero_left_button.setEnabled(False)        
        self.calibrate_loadcell.emit((0, 0))
        self.calibrate_weight_left_button.setEnabled(True)
        
    def calibrateWeightLeft(self):
        self.calibrate_weight_left_button.setEnabled(False)
        calibration_weight = self.calibration_left_spinbox.value()
        self.calibrate_loadcell.emit((0, calibration_weight))
        self.calibrate_zero_left_button.setEnabled(True)        
        
    def calibrateZeroRight(self):
        self.calibrate_zero_right_button.setEnabled(False)
        self.calibrate_loadcell.emit((1, 0))
        self.calibrate_weight_right_button.setEnabled(True)

    def calibrateWeightRight(self):
        self.calibrate_weight_right_button.setEnabled(False)
        calibration_weight = self.calibration_right_spinbox.value()
        self.calibrate_loadcell.emit((1, calibration_weight))
        self.calibrate_zero_right_button.setEnabled(True)

if __name__ == "__main__":
    # Create a QApplication and the main_window
    app = QApplication([])
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
