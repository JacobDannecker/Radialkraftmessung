# All inputs for Main_App.py

# QT
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QMessageBox,
                             QFileDialog, QCheckBox, QDoubleSpinBox)
#from PyQt6 import uic
from pathlib import Path
from PyQt6.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel


# Matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import (NavigationToolbar2QT
                                              as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib import animation

# Time
from datetime import datetime
import time
from timeit import default_timer as timer

# Data 
import csv
import pandas as pd

# Auxillary
import random

# System
import sys
import subprocess
import os

# Tinkerforge
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_industrial_ptc import BrickletIndustrialPTC
from tinkerforge.bricklet_load_cell_v2 import BrickletLoadCellV2
from tinkerforge.bricklet_industrial_dual_relay import BrickletIndustrialDualRelay
