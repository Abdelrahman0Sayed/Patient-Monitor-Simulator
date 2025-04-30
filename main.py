from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QTimer
import numpy as np 
import pyqtgraph as pg
import pandas as pd
from PyQt5.QtMultimedia import QSoundEffect, QSound
from PyQt5.QtCore import QUrl
import os
from scipy.signal import find_peaks



def detect_r_peaks(ecg_signal, sampling_rate, prominence=0.5):
        """Detects R-peaks in an ECG signal using scipy.signal.find_peaks."""
        peaks, _ = find_peaks(ecg_signal, height=0.5, prominence=prominence, distance=int(0.15 * sampling_rate))
        return peaks



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        font_id = QtGui.QFontDatabase.addApplicationFont("./Fonts/Bebas_Neue/BebasNeue-Regular.ttf")
        if font_id < 0:
            print("Error loading font file")
            font_family = "Arial"
        else:
            font_family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0]

        custom_font = QtGui.QFont(font_family)
        custom_font.setPointSize(90)
        custom_font.setBold(True)
        
        # Dark green background like real patient monitors
        MainWindow.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                border: 1px solid white;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003300;
            }
        """)

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainAreaLayout = QtWidgets.QVBoxLayout()
        self.mainAreaLayout.setObjectName("mainAreaLayout")
        
        # Top control bar with load button
        self.controlBar = QtWidgets.QHBoxLayout()
        self.controlBar.setContentsMargins(0, 0, 0, 10)
        
        self.loadfileBtn = QtWidgets.QPushButton("Load ECG File")
        self.loadfileBtn.setObjectName("loadfileBtn")
        self.loadfileBtn.clicked.connect(self.uploadFile)
        self.loadfileBtn.setFixedWidth(150)
        self.controlBar.addWidget(self.loadfileBtn)
        
        self.controlBar.addStretch()
        self.mainAreaLayout.addLayout(self.controlBar)
        
        # ECG Plot Widget with black background like real ECG monitors
        self.plotWidget = pg.PlotWidget()
        self.plotWidget.setBackground('#1e1e1e')  # Black background
        self.plotWidget.showGrid(x=True, y=True, alpha=0.3)
        self.plotWidget.setObjectName("plotWidget")
        self.plotWidget.setLabel('left', 'mV', color='white')
        self.plotWidget.setLabel('bottom', 'Time (s)', color='white')
        self.plotWidget.setTitle('ECG', color='white', size='12pt')
        self.plotWidget.getAxis('left').setPen(pg.mkPen('white'))
        self.plotWidget.getAxis('bottom').setPen(pg.mkPen('white'))
        
        # Add ECG trace with green color like real monitors
        self.plotCurve = self.plotWidget.plot(
            [], [], 
            pen=pg.mkPen(color="#ffa500", width=2)
        )
        
        self.mainAreaLayout.addWidget(self.plotWidget, stretch=4)

        # Arrhythmia Detection Display
        self.arrhythmiaContainer = QtWidgets.QWidget()
        self.arrhythmiaContainer.setFixedHeight(200)  # Set fixed height
        self.arrhythmiaContainer.setStyleSheet("""
            QWidget {
                background-color: black;
                border: 2px solid #ff0000;
                border-radius: 5px;
                margin: 5px;
            }
            QLabel {
                color: #ff0000;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.arrhythmiaLayout = QtWidgets.QVBoxLayout(self.arrhythmiaContainer)
    
        self.arrhythmiaTitle = QtWidgets.QLabel("ARRHYTHMIA DETECTION")
        self.arrhythmiaTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.arrhythmiaLayout.addWidget(self.arrhythmiaTitle)
        
        self.arrhythmiaLabel = QtWidgets.QLabel("")
        self.arrhythmiaLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.arrhythmiaLabel.setStyleSheet("font-size: 20px;")
        self.arrhythmiaLayout.addWidget(self.arrhythmiaLabel)
        
        self.mainAreaLayout.addWidget(self.arrhythmiaContainer)

        # Status bar at bottom (like real monitors)
        self.statusBar = QtWidgets.QStatusBar()
        self.statusBar.setStyleSheet("""
            QStatusBar {
                background-color: #1e1e1e;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-top: 2px solid white;
            }
        """)
        self.statusBar.showMessage("MONITORING...")
        self.mainAreaLayout.addWidget(self.statusBar)

        self.horizontalLayout.addLayout(self.mainAreaLayout)
        
        # Sidebar Layout for Vitals - styled like real patient monitor
        self.sidebarLayout = QtWidgets.QVBoxLayout()
        self.sidebarLayout.setObjectName("sidebarLayout")
        self.sidebarLayout.setContentsMargins(10, 10, 10, 10)
        self.sidebarLayout.setSpacing(20)
        
        sidebarWidth = 300  # Increased width

        # Header label
        self.vitalsHeader = QtWidgets.QLabel("VITAL SIGNS")
        self.vitalsHeader.setFixedWidth(sidebarWidth)
        self.vitalsHeader.setFixedHeight(200)  # Fixed height for header
        self.vitalsHeader.setAlignment(QtCore.Qt.AlignCenter)
        self.vitalsHeader.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                border-bottom: 2px solid white;
                padding-bottom: 5px;
                margin-bottom: 10px;
            }
        """)
        self.sidebarLayout.addWidget(self.vitalsHeader)
        
        # Heart Rate (styled like real monitor)
        self.hrContainer = QtWidgets.QWidget()
        self.hrContainer.setStyleSheet("""
            QWidget {
                background-color: black;
                border: 2px solid white;
                border-radius: 5px;
            }
        """)
        self.hrLayout = QtWidgets.QVBoxLayout(self.hrContainer)
        
        self.hrTitle = QtWidgets.QLabel("HEART RATE")
        self.hrTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.hrTitle.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        self.hrLayout.addWidget(self.hrTitle)
        
        self.hrLabel = QtWidgets.QLabel("--")
        self.hrLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.hrLabel.setStyleSheet("""
            QLabel {
                color: #ff0000;
                font-size: 48px;
                font-weight: bold;
            }
        """)
        self.hrLayout.addWidget(self.hrLabel)
        
        self.hrUnit = QtWidgets.QLabel("BPM")
        self.hrUnit.setAlignment(QtCore.Qt.AlignCenter)
        self.hrUnit.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)
        self.hrLayout.addWidget(self.hrUnit)
        self.sidebarLayout.addWidget(self.hrContainer)
        
        # SpO2 (styled like real monitor)
        self.spo2Container = QtWidgets.QWidget()
        self.spo2Container.setStyleSheet("""
            QWidget {
                background-color: black;
                border: 2px solid white;
                border-radius: 5px;
            }
        """)
        self.spo2Layout = QtWidgets.QVBoxLayout(self.spo2Container)
        
        self.spo2Title = QtWidgets.QLabel("SpO2")
        self.spo2Title.setAlignment(QtCore.Qt.AlignCenter)
        self.spo2Title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        self.spo2Layout.addWidget(self.spo2Title)
        
        self.spo2Label = QtWidgets.QLabel("--")
        self.spo2Label.setAlignment(QtCore.Qt.AlignCenter)
        self.spo2Label.setStyleSheet("""
            QLabel {
                color: #00ffff;
                font-size: 48px;
                font-weight: bold;
            }
        """)
        self.spo2Layout.addWidget(self.spo2Label)
        
        self.spo2Unit = QtWidgets.QLabel("%")
        self.spo2Unit.setAlignment(QtCore.Qt.AlignCenter)
        self.spo2Unit.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)
        self.spo2Layout.addWidget(self.spo2Unit)
        self.sidebarLayout.addWidget(self.spo2Container)
        
        # Blood Pressure (styled like real monitor)
        self.bpContainer = QtWidgets.QWidget()
        self.bpContainer.setStyleSheet("""
            QWidget {
                background-color: black;
                border: 2px solid white;
                border-radius: 5px;
            }
        """)
        self.bpLayout = QtWidgets.QVBoxLayout(self.bpContainer)
        
        self.bpTitle = QtWidgets.QLabel("BLOOD PRESSURE")
        self.bpTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.bpTitle.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        self.bpLayout.addWidget(self.bpTitle)
        
        self.bpLabel = QtWidgets.QLabel("--/--")
        self.bpLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.bpLabel.setStyleSheet("""
            QLabel {
                color: #ffff00;
                font-size: 48px;
                font-weight: bold;
            }
        """)
        self.bpLayout.addWidget(self.bpLabel)
        
        self.bpUnit = QtWidgets.QLabel("mmHg")
        self.bpUnit.setAlignment(QtCore.Qt.AlignCenter)
        self.bpUnit.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)
        self.bpLayout.addWidget(self.bpUnit)
        self.sidebarLayout.addWidget(self.bpContainer)
        
        # Temperature (styled like real monitor)
        self.tempContainer = QtWidgets.QWidget()
        self.tempContainer.setStyleSheet("""
            QWidget {
                background-color: black;
                border: 2px solid white;
                border-radius: 5px;
            }
        """)
        self.tempLayout = QtWidgets.QVBoxLayout(self.tempContainer)
        
        self.tempTitle = QtWidgets.QLabel("TEMPERATURE")
        self.tempTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.tempTitle.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        self.tempLayout.addWidget(self.tempTitle)
        
        self.temperatureLabel = QtWidgets.QLabel("--")
        self.temperatureLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.temperatureLabel.setStyleSheet("""
            QLabel {
                color: #ff9900;
                font-size: 48px;
                font-weight: bold;
            }
        """)
        self.tempLayout.addWidget(self.temperatureLabel)
        
        self.tempUnit = QtWidgets.QLabel("°C")
        self.tempUnit.setAlignment(QtCore.Qt.AlignCenter)
        self.tempUnit.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)
        self.tempLayout.addWidget(self.tempUnit)
        self.sidebarLayout.addWidget(self.tempContainer)
        
        # Add stretch to push everything up
        self.sidebarLayout.addStretch()
        
        self.horizontalLayout.addLayout(self.sidebarLayout)
        MainWindow.setCentralWidget(self.centralwidget)

        # Animation variables
        self.timer = QTimer()
        self.timer.timeout.connect(self.updatePlot)
        self.currentIndex = 0
        self.windowSize = 5  # seconds to display
        self.ecgData = None
        self.timeData = None
        self.alarm_sound = None  # Store QSound instance
        self.samplingRate = 1000  # Default sampling rate (Hz)
        self.pointsToShow = self.windowSize * self.samplingRate
        self.arrhythmia_types = [
            "Normal Sinus Rhythm",
            "Atrial Fibrillation",
            "Ventricular Tachycardia",
            "Bradycardia",
            "Tachycardia",
            "Premature Ventricular Contraction"
        ]
        self.current_arrhythmia = ""


        self.initializePlot()

        self.timer.start(20)  # ~50fps update

    def initializePlot(self):
        """Initialize the plot for continuous scrolling"""
        self.plotWidget.setXRange(0, self.windowSize)  # Dynamic scrolling range
        self.plotWidget.setYRange(-2, 2)  # ECG amplitude range
        self.plotWidget.setLimits(yMin=-5, yMax=5)

        # Create the ECG curve (keep previous data)
        self.plotCurve = self.plotWidget.plot(
            [], [], 
            pen=pg.mkPen(color="#ffa500", width=2)  # Green ECG line
        )

    def uploadFile(self):
        try:
            filePath, _ = QFileDialog.getOpenFileName(
                None,
                "Select ECG Data File",
                "",
                "CSV Files (*.csv);;Text Files (*.txt);;All Files (*.*)"
            )
            
            if filePath:
                # Reset the HR label before loading new data
                self.hrLabel.setText("--")
                
                self.plotWidget.clear()
                # Reset arrhythmia detection
                self.current_arrhythmia = ""
                self.arrhythmiaLabel.setText("")
                self.arrhythmiaLabel.setStyleSheet("font-size: 20px;")
                
                # Read CSV file
                self.data = pd.read_csv(filePath)
                
                # Get ECG data (assuming first column is time, second is ECG)
                self.timeData = self.data.iloc[:, 0].values
                self.ecgData = self.data.iloc[:, 1].values
                
                # Calculate sampling rate from time data
                if len(self.timeData) > 1:
                    self.samplingRate = 1 / (self.timeData[1] - self.timeData[0])
                    self.pointsToShow = int(self.windowSize * self.samplingRate)
                
                # Extract vitals from first row
                if len(self.data) > 0:
                    row = self.data.iloc[0]
                    # Update SpO2
                    if 'SpO2 (%)' in row:
                        self.spo2Label.setText(f"{row['SpO2 (%)']:.0f}")
                    else:
                        self.spo2Label.setText("--")
                    
                    # Update temperature
                    if 'TEMP (*C)' in row:
                        self.temperatureLabel.setText(f"{row['TEMP (*C)']:.1f}")
                    else:
                        self.temperatureLabel.setText("--")
                        
                    # Update sys/dias blood pressures
                    if 'Systolic Blood Pressure' in row and 'Diastolic Blood Pressure' in row:
                        self.bpLabel.setText(f"{int(row['Systolic Blood Pressure'])}/{int(row['Diastolic Blood Pressure'])}")
                    else:
                        self.bpLabel.setText("--/--")
                
                # Reset plot
                self.initializePlot()
                self.currentIndex = 0
                self.statusBar.showMessage(f"Loaded: {filePath.split('/')[-1]}")
                
                # Clear any previous analysis state
                if hasattr(self, 'analyzed_ecg_data'):
                    delattr(self, 'analyzed_ecg_data')
                
        except Exception as e:
            self.statusBar.showMessage(f"Error: {str(e)}")
            print(f"Error loading file: {e}")

    def updateVitals(self, current_index):
        """Update the vital signs display from the current data index"""
        if self.ecgData is None or self.timeData is None:
            return

        try:
            # Only update every 1 second (1000 milliseconds) 
            if current_index % self.samplingRate != 0:
                return
                
            if current_index < len(self.timeData):
                current_time = self.timeData[current_index]
                # Get the closest row index for the current time
                data_index = np.abs(self.data['Time'] - current_time).argmin()
                row = self.data.iloc[data_index]
                
                if 'Heart_Rate' in row:
                    self.hrLabel.setText(f"{row['Heart_Rate']:.0f}")
                
                if 'SPO2' in row:
                    self.spo2Label.setText(f"{row['SPO2']:.0f}")
                
                if 'Blood_Pressure' in row:
                    bp = row['Blood_Pressure'].split('/')
                    sys_bp = float(bp[0])
                    dia_bp = float(bp[1])
                    self.bpLabel.setText(f"{sys_bp:.0f}/{dia_bp:.0f}")
                
                if 'Temperature' in row:
                    self.temperatureLabel.setText(f"{row['Temperature']:.1f}")
                if( self.current_arrhythmia == "Bradycardia" and row['Heart_Rate'] < 60) or (self.current_arrhythmia == "Tachycardia"): 
                    print("Trigerring.....")
                    self.trigger_alarm()

        except Exception as e:
            print(f"Error updating vitals: {e}")

    
    def trigger_alarm(self):
        if os.path.exists("./sounds/AlarmSound.wav"):
            self.alarm_sound = QSound("./sounds/AlarmSound.wav")
            self.alarm_sound.play()
            # Create a timer to stop the sound after 2 seconds
            QTimer.singleShot(5000, self.stop_alarm)
    
    def stop_alarm(self):
        if self.alarm_sound:
            self.alarm_sound.stop()
        QSound.stop()

    def detectArrhythmia(self):
        if self.ecgData is None or self.timeData is None or self.samplingRate <= 0:
            self.current_arrhythmia = "No ECG Data"
            self.arrhythmiaLabel.setText(self.current_arrhythmia)
            return

        # Get the current window of ECG data
        start_idx = max(0, self.currentIndex - self.pointsToShow)
        end_idx = min(self.currentIndex, len(self.ecgData))
        current_ecg_segment = self.ecgData[start_idx:end_idx]

        if len(current_ecg_segment) < self.samplingRate:  # Need at least 1 second of data
            self.current_arrhythmia = "Analyzing..."
            self.arrhythmiaLabel.setText(self.current_arrhythmia)
            return

        try:
            # Use the correct method to detect R peaks
            r_peaks_indices = detect_r_peaks(current_ecg_segment, self.samplingRate)

            if len(r_peaks_indices) >= 2:
                # Calculate RR intervals (time between consecutive R peaks)
                rr_intervals = np.diff(r_peaks_indices) / self.samplingRate  # in seconds
                
                # Check if there are any valid RR intervals
                if len(rr_intervals) > 0:
                    # Calculate average RR interval with a check for zero values
                    valid_intervals = rr_intervals[rr_intervals > 0]  # Filter out any zero values
                    
                    if len(valid_intervals) > 0:
                        avg_rr_interval = np.mean(valid_intervals)
                        
                        # Calculate heart rate with a check for zero
                        if avg_rr_interval > 0:
                            heart_rate = 60 / avg_rr_interval
                            self.hrLabel.setText(f"{heart_rate:.0f}")
                            
                            # Calculate RR interval variability (for AFib detection)
                            rr_variability = np.std(valid_intervals) / np.mean(valid_intervals) if len(valid_intervals) > 3 else 0
                            
                            # Check for PVC - look for premature beats followed by compensatory pause
                            has_pvc = False
                            for i in range(len(valid_intervals) - 1):
                                # PVC typically has a short RR interval followed by a long one
                                if valid_intervals[i] < 0.7 * avg_rr_interval and valid_intervals[i+1] > 1.3 * avg_rr_interval:
                                    has_pvc = True
                                    break
                            
                            # Determine the arrhythmia type
                            if heart_rate < 60:
                                self.current_arrhythmia = "Bradycardia"
                            elif heart_rate > 150 and np.std(valid_intervals) < 0.05:
                                # Ventricular Tachycardia: very fast and regular rhythm
                                self.current_arrhythmia = "Ventricular Tachycardia"
                                # # Play alarm sound for dangerous arrhythmia
                                # if os.path.exists("./sounds/AlarmSound.wav"):
                                #     QSound.play("./sounds/AlarmSound.wav")
                            elif heart_rate > 100:
                                self.current_arrhythmia = "Tachycardia"
                            elif rr_variability > 0.2:
                                # Atrial Fibrillation: characterized by irregular RR intervals
                                self.current_arrhythmia = "Atrial Fibrillation"
                            elif has_pvc:
                                self.current_arrhythmia = "Premature Ventricular Contraction"
                            else:
                                self.current_arrhythmia = "Normal Sinus Rhythm"
                        else:
                            self.current_arrhythmia = "Invalid RR interval"
                            self.hrLabel.setText("--")
                    else:
                        self.current_arrhythmia = "No valid RR intervals"
                        self.hrLabel.setText("--")
                else:
                    self.current_arrhythmia = "No RR intervals calculated"
                    self.hrLabel.setText("--")
            else:
                self.hrLabel.setText("--")
                self.current_arrhythmia = "Not enough R-peaks detected"

        except Exception as e:
            self.current_arrhythmia = f"Error in analysis: {e}"
            print(f"Error in arrhythmia detection: {e}")

        # Update the UI with the detected arrhythmia
        print(self.current_arrhythmia)
        self.arrhythmiaLabel.setText(self.current_arrhythmia)
        
        if self.current_arrhythmia != "Normal Sinus Rhythm":
            self.statusBar.showMessage(f"ARRHYTHMIA DETECTED: {self.current_arrhythmia}", 5000)
            if self.current_arrhythmia in ["Ventricular Tachycardia", "Atrial Fibrillation"]:
                self.arrhythmiaLabel.setStyleSheet("font-size: 20px; color: #ff0000;")  # Red for dangerous
            else:
                self.arrhythmiaLabel.setStyleSheet("font-size: 20px; color: #ffff00;")  # Yellow for less severe
        else:
            self.statusBar.showMessage("Normal Rhythm Detected", 5000)  # Changed message
            self.arrhythmiaLabel.setStyleSheet("font-size: 20px; color: #ffa500;")  # Added # to color code



    def updatePlot(self):
        """Update the plot with new data points in real-time (Cine Mode)"""
        if self.ecgData is None or self.timeData is None:
            return

        self.currentIndex += 10  # Adjust for smoother scrolling

        if self.currentIndex >= len(self.ecgData):
            self.currentIndex = len(self.ecgData) - 1
            self.timer.stop()
            return

        # Define the scrolling window range
        start_idx = max(0, self.currentIndex - self.pointsToShow)
        end_idx = min(self.currentIndex, len(self.ecgData))

        x_data = self.timeData[start_idx:end_idx]
        y_data = self.ecgData[start_idx:end_idx]

        # Update the plot dynamically
        self.plotCurve.setData(x_data, y_data)

        # Shift the x-axis to keep the latest data in view
        if self.timeData[self.currentIndex] > self.windowSize:
            view_start = self.timeData[self.currentIndex] - self.windowSize
            view_end = self.timeData[self.currentIndex]
            self.plotWidget.setXRange(view_start, view_end, padding=0)
        else:
            self.plotWidget.setXRange(0, self.windowSize)

        self.detectArrhythmia()
        self.updateVitals(self.currentIndex)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())