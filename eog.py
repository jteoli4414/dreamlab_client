import sys
import time
import re
import serial
import collections
from enum import Enum
from random import randint
from threading import Thread
from time import sleep
from typing import Union

from PyQt5.QtWidgets import *
from pglive.kwargs import Axis
from pglive.sources.data_connector import DataConnector
from pglive.sources.live_axis import LiveAxis
from pglive.sources.live_plot import LiveLinePlot
from pglive.sources.live_plot_widget import LivePlotWidget

# Serial Variables
DATA_LEN = 7
BAUD_RATE = 115200
BYTE_SIZE = 8
TIMEOUT_SERIAL = 2

# Graphing Variables
EVENT_QUEUE_SIZE = 10
MATCH_QUEUE_SIZE = 10
BUFFER_SIZE = 100
EPOCH_PERIOD = 1000

# What Type of EOG signal
class SignalMode(Enum):
    INTEGRAL_WITH_HYSTER = 1
    DIFFERENTIAL_WITH_HYSTER = 2
    INTEGRAL_NO_HYSTER = 1
    DIFFERENTIAL_NO_HYSTER = 2

# What is the signal doing
class SignalSlope(Enum):
    INIT = 1
    RISING = 2
    FALLING = 3

# Where is the signal
class SignalZone(Enum):
    ZERO = 1
    POSITIVE = 2
    NEGATIVE = 3

class SignalThresholdEvent(Enum):
    POSITIVE_EDGE_RISE = 1
    POSITIVE_EDGE_FALL = 2
    NEGATIVE_EDGE_RISE = 3
    NEGATIVE_EDGE_FALL = 4

class SignalMatchEvent(Enum):
    POSITIVE_MATCH = 1
    NEGATIVE_MATCH = 2

class Signal():
    signalMode = SignalMode.INTEGRAL_NO_HYSTER # Int or Diff
    signalSlope = SignalSlope.INIT
    signalZone = SignalZone.ZERO
    isCalibrated = False
    isHyster = False
    isDetecting = False

    maxVal = 0.0 # highest positive
    minVal = 0.0 # lowest negative
    center = 0.0

    highHysterWindow=0.0
    highRiseTrigger=0.0 # (hysteresis mode) Rising edge trigger +
    highFallTrigger=0.0 # (hysteresis mode) Falling edge trigger +
    highTrigger=0.0 # (no hysteresis mode) Trigger + 

    lowHysterWindow=0.0
    lowRiseTrigger=0.0 # (hysteresis mode) Rising edge trigger -
    lowFallTrigger=0.0 # (hysteresis mode) Falling edge trigger -
    lowTrigger=0.0 # (no hysteresis mode) Trigger - (no hysteresis)

    prevVal = 0.0
    curVal = 0.0

    prevEvent = 0

    events_queue = None
    match_queue = None

    positivePolarityMatch = None # Postive Polarity Match Pattern
    negativePolarityMatch = None # Negative Polarity Match Pattern
    posStateIncrement = 0
    negStateIncrement = 0
    
    def __init__(self, mode, center, min, max, lowTrigger, highTrigger):
        self.signalMode = mode
        # Define Eye Motion artifacts based on either integral wave or differential wave
        if((self.signalMode == SignalMode.INTEGRAL_WITH_HYSTER.value) or (self.signalMode == SignalMode.INTEGRAL_NO_HYSTER)):
            self.positivePolarityMatch = [SignalThresholdEvent.POSITIVE_EDGE_RISE, SignalThresholdEvent.POSITIVE_EDGE_FALL]
            self.negativePolarityMatch = [SignalThresholdEvent.NEGATIVE_EDGE_FALL, SignalThresholdEvent.NEGATIVE_EDGE_RISE]
        elif(self.signalMode == SignalMode.DIFFERENTIAL_WITH_HYSTER.value) or (self.signalMode == SignalMode.DIFFERENTIAL_NO_HYSTER):
            self.positivePolarityMatch = [SignalThresholdEvent.POSITIVE_EDGE_RISE, SignalThresholdEvent.POSITIVE_EDGE_FALL, SignalThresholdEvent.NEGATIVE_EDGE_FALL, SignalThresholdEvent.NEGATIVE_EDGE_RISE]
            self.negativePolarityMatch = [SignalThresholdEvent.NEGATIVE_EDGE_FALL, SignalThresholdEvent.NEGATIVE_EDGE_RISE, SignalThresholdEvent.POSITIVE_EDGE_RISE, SignalThresholdEvent.POSITIVE_EDGE_FALL]
        else:
            self.positivePolarityMatch = None
            self.negativePolarityMatch = None

        self.minVal = min
        self.maxVal = max
        self.lowTrigger = lowTrigger
        self.highTrigger = highTrigger
        self.center = center
        self.events_queue = collections.deque(maxlen=EVENT_QUEUE_SIZE)
        self.match_queue = collections.deque(maxlen=MATCH_QUEUE_SIZE)
        self.curVal = 0.0
        self.prevVal = 0.0
        # With Hyster
        if((self.signalMode == SignalMode.INTEGRAL_WITH_HYSTER.value) or (self.signalMode == SignalMode.DIFFERENTIAL_WITH_HYSTER.value)):
            self.isHyster = True
            self.isCalibrated = False
        # No Hyster
        elif((self.signalMode == SignalMode.INTEGRAL_NO_HYSTER.value) or (self.signalMode == SignalMode.DIFFERENTIAL_NO_HYSTER.value)):
            self.isCalibrated = True

        self.isDetecting = False

    def boundCheckPos(self, val):
        ret = val
        if(val > self.maxVal):
            ret = self.maxVal
        elif(val < self.center):
            ret = self.center
        return ret
    
    def boundCheckNeg(self, val):
        ret = val
        if(val > self.center):
            ret = self.center
        elif(val < self.minVal):
            ret = self.minVal
        return ret
    
    def setHyster(self, lowWindow, highWindow):
        self.lowRiseTrigger = self.boundCheckNeg(self.lowTrigger+(lowWindow/2))
        self.lowFallTrigger = self.boundCheckNeg(self.lowTrigger-(lowWindow/2))
        self.highRiseTrigger = self.boundCheckPos(self.highTrigger+(highWindow/2))
        self.highFallTrigger = self.boundCheckPos(self.highTrigger-(highWindow/2))
        self.isCalibrated = True

    def updateSignal(self, val):
        self.prevVal = self.curVal
        self.curVal = val
        if(self.isCalibrated and self.isHyster):
            self.updateZone()
            self.updateSlope()
            self.edgeDetectHyster()
        elif(self.isCalibrated):
            self.updateZone()
            self.updateSlope()
            self.edgeDetectNoHyster()

    def updateZone(self):
        if(self.curVal > self.center):
            self.signalZone = SignalZone.POSITIVE
        elif(self.curVal < self.center):
            self.signalZone = SignalZone.NEGATIVE
        else:
            self.signalZone = SignalZone.ZERO
            
    def updateSlope(self):
        if(self.prevVal >= self.curVal):
            self.signalState = SignalSlope.FALLING
        else:
            self.signalState = SignalSlope.RISING

    def edgeDetectHyster(self):
        event = None
        if(self.isDetecting): # If detecting is happening and signal reached trigger and did not repeat last trigger add event tuple
            if(self.curVal >= self.highRiseTrigger and self.prevVal < self.highRiseTrigger):
                if((self.prevEvent != SignalThresholdEvent.POSITIVE_EDGE_RISE.value)):
                    event = SignalThresholdEvent.POSITIVE_EDGE_RISE
            elif(self.curVal < self.highFallTrigger and self.prevVal >= self.highFallTrigger):
                if((self.prevEvent != SignalThresholdEvent.POSITIVE_EDGE_FALL.value)):
                    event = SignalThresholdEvent.POSITIVE_EDGE_FALL
            elif(self.curVal >= self.lowRiseTrigger and self.prevVal < self.lowRiseTrigger):
                if((self.prevEvent != SignalThresholdEvent.NEGATIVE_EDGE_RISE.value)):
                    event = SignalThresholdEvent.NEGATIVE_EDGE_RISE
            elif(self.curVal < self.lowFallTrigger and self.prevVal >= self.lowFallTrigger):
                if((self.prevEvent != SignalThresholdEvent.NEGATIVE_EDGE_FALL.value)):
                    event = SignalThresholdEvent.NEGATIVE_EDGE_FALL

        if (event != None):
            #print([event, time.time(), self.curVal, self.prevVal])
            self.events_queue.append([event, time.time()])
            self.prevEvent = event.value
            self.matchPattern(event)
            
    def edgeDetectNoHyster(self):
        if(self.isDetecting):
            if(self.curVal >= self.highTrigger and self.prevVal < self.highTrigger):
                if((self.prevEvent != SignalThresholdEvent.POSITIVE_EDGE_RISE.value)):
                    self.events_queue.append(SignalThresholdEvent.POSITIVE_EDGE_RISE)
                    self.prevEvent = SignalThresholdEvent.POSITIVE_EDGE_RISE.value
            elif(self.curVal < self.highTrigger and self.prevVal >= self.highTrigger):
                if((self.prevEvent != SignalThresholdEvent.POSITIVE_EDGE_FALL.value)):
                    self.events_queue.append(SignalThresholdEvent.POSITIVE_EDGE_FALL)
                    self.prevEvent = SignalThresholdEvent.POSITIVE_EDGE_FALL.value
            elif(self.curVal >= self.lowTrigger and self.prevVal < self.lowTrigger):
                if((self.prevEvent != SignalThresholdEvent.NEGATIVE_EDGE_RISE.value)):
                    self.events_queue.append(SignalThresholdEvent.NEGATIVE_EDGE_RISE)
                    self.prevEvent = SignalThresholdEvent.NEGATIVE_EDGE_RISE.value
            elif(self.curVal < self.lowTrigger and self.prevVal >= self.lowTrigger):
                if((self.prevEvent != SignalThresholdEvent.NEGATIVE_EDGE_FALL.value)):
                    self.events_queue.append(SignalThresholdEvent.NEGATIVE_EDGE_FALL)
                    self.prevEvent = SignalThresholdEvent.NEGATIVE_EDGE_FALL.value

    def matchPattern(self, event):
        # Attempt Match Positive
        if(self.posStateIncrement > self.negStateIncrement):
            if(self.positivePolarityMatch[self.posStateIncrement].value == event.value):
                self.posStateIncrement += 1
                self.negStateIncrement = 0
        elif(self.posStateIncrement < self.negStateIncrement):
            if(self.negativePolarityMatch[self.negStateIncrement].value == event.value):
                self.negStateIncrement += 1
                self.posStateIncrement = 0
        else:
            if(self.positivePolarityMatch[self.posStateIncrement].value == event.value):
                self.posStateIncrement += 1
            elif(self.negativePolarityMatch[self.negStateIncrement].value == event.value):
                self.negStateIncrement += 1

        if(self.posStateIncrement == (len(self.positivePolarityMatch))):
            self.match_queue.append([SignalMatchEvent.POSITIVE_MATCH, time.time()])
            self.posStateIncrement = 0
            self.negStateIncrement = 0
        if(self.negStateIncrement == (len(self.negativePolarityMatch))):
            self.match_queue.append([SignalMatchEvent.NEGATIVE_MATCH, time.time()])
            self.negStateIncrement = 0
            self.posStateIncrement = 0

class Window(QWidget):
    running = False

    eogx_signal = None
    eogy_signal = None

    eogx = collections.deque(maxlen=BUFFER_SIZE)
    eogy = collections.deque(maxlen=BUFFER_SIZE)

    events = []
    
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QGridLayout(self)

        eogx_plot = LiveLinePlot(pen="blue")
        eogy_plot = LiveLinePlot(pen="orange")

        self.eogx_signal = Signal(SignalMode.DIFFERENTIAL_WITH_HYSTER.value, 1600, 0, 3100, 1300, 2000)
        self.eogy_signal = Signal(SignalMode.DIFFERENTIAL_WITH_HYSTER.value, 1600, 0, 3100, 1300, 2000)

        self.eogx_signal.setHyster(10, 10)
        self.eogy_signal.setHyster(10, 10)

        # Data connectors for each plot with dequeue of 600 points

        self.eogx_connector = DataConnector(eogx_plot, max_points=EPOCH_PERIOD)
        self.eogy_connector = DataConnector(eogy_plot, max_points=EPOCH_PERIOD)

        # Setup bottom axis with TIME tick format
        # You can use Axis.DATETIME to show date as well
        bottom_axis = LiveAxis("bottom", **{Axis.TICK_FORMAT: Axis.TIME})

        # Create plot itself
        self.chart_view = LivePlotWidget(title="Line Plot - Time series @ 60Hz", axisItems={'bottom': bottom_axis})
        # Show grid
        self.chart_view.showGrid(x=True, y=True, alpha=0.3)
        # Set labels
        self.chart_view.setLabel('bottom', 'Datetime', units="s")
        self.chart_view.setLabel('left', 'Price')

        self.chart_view.addItem(eogx_plot)
        self.chart_view.addItem(eogy_plot)

        # Create Detection button 
        self.start_button = QPushButton("Detect")
        self.start_button.clicked.connect(self.start_button_clicked)

        # using -1 to span through all rows available in the window
        layout.addWidget(self.chart_view, 0, 0, 0, 2)
        layout.addWidget(self.start_button, 3, 0, 1, 2)

    def start_button_clicked(self):
        if(self.eogx_signal.isDetecting == False):
            self.eogx_signal.isDetecting = True
            self.eogy_signal.isDetecting = True
        else:
            self.eogx_signal.isDetecting = False
            self.eogy_signal.isDetecting = False

    def update(self):
        """Generate data at 60Hz"""
        while self.running:
            timestamp = time.time()
            eogx_p = 0
            eogy_p = 0
            try:
                eogx_p = int(self.eogx.pop())
                self.eogx_signal.updateSignal(eogx_p)
                eogy_p = int(self.eogy.pop())
                self.eogy_signal.updateSignal(eogy_p)
            except Exception as e:
                print(str(e))

            try:
                print(self.eogx_signal.match_queue.pop())
            except:
                pass
            self.eogx_connector.cb_append_data_point(eogx_p, timestamp)
            self.eogy_connector.cb_append_data_point(eogy_p, timestamp)
            sleep(1/60)

    def start_app(self):
        """Start Thread generator"""
        self.running = True
        Thread(target=self.update).start()
        Thread(target=self.serial_stream).start()

    def serial_stream(self):
        serialPort = serial.Serial(port="COM3", baudrate=BAUD_RATE, bytesize=BYTE_SIZE, timeout=TIMEOUT_SERIAL, stopbits=serial.STOPBITS_ONE)
        serialString = ""  # Used to hold data coming over UART
        while 1:
            # Wait until there is data waiting in the serial buffer
            if serialPort.in_waiting > 0:
                # Read data out of the buffer until a carraige return / new line is found
                serialString = serialPort.readline()
                # Print the contents of the serial data
                numbers = [int(num) for num in re.findall(r'\d+', serialString.decode("ascii"))]
                if(len(numbers) == 2):
                    self.eogx.append(int(numbers[0]))
                    self.eogy.append(int(numbers[1]))




if __name__ == '__main__':
   app = QApplication(sys.argv)
   window = Window()
   window.show()
   window.start_app()
   app.exec()
   window.running = False





