import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QApplication)
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
#import serial
import random

class CustomPlot(pg.PlotWidget):
    def __init__(self, title=''):
        pg.PlotWidget.__init__(self, title=title)
        self.curve = self.plot()

# The top container/widget for the graphs
class Window(QWidget):
    def __init__(self):
        super().__init__()
        
        self.windowWidth = 500                      # width of the window displaying the curve
        #0を500個作成（Xm）
        self.Xm = np.linspace(0,0,self.windowWidth) # create array that will contain the relevant time series 
        self.Ym = np.linspace(0,0,self.windowWidth)
        self.Zm = np.linspace(0,0,self.windowWidth)
        self.ptr = -self.windowWidth                # set first x position
        self.k = 5 #### 信号計算の代替シミュレーション用初期値
        
        self.initUI() # call the UI set up
        '''
        self.portName = "COM6"
        self.baudrate = 115200
        self.ser = serial.Serial(self.portName,self.baudrate)
        '''
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateGraph)
        self.timer.start(30)
    
    # set up the UI
    def initUI(self):
        
        self.layout = QVBoxLayout(self) # create the layout
        self.pginput = CustomPlot(title="Signal from serial port - Realtime plot") # class abstract both the classes
        self.pginfer = CustomPlot(title="signal calculation - inference") # "" "" ""
        self.layout.addWidget(self.pginput)
        self.layout.addWidget(self.pginfer)
        self.show()
    
    # update graph
    def updateGraph(self):
        
        self.Xm[:-1] = self.Xm[1:]          # shift data in the temporal mean 1 sample left
        self.Ym[:-1] = self.Ym[1:]
        self.Zm[:-1] = self.Zm[1:]
        '''
        self.volt = ser.readline().rstrip() # シリアル通信で受け取った情報（文字列）を改行コードがくるまで代入します。byte型で得る
        self.volt = self.volt.decode()
        self.volt = float(self.volt)
        '''
        self.volt = random.randrange(0.0, 6.0) #### 入力信号の代替シミュレーション
        self.Xm[-1] = self.volt             # vector containing the instantaneous values
        self.Ym[-1] = self.volt
        self.ptr += 1                       # update x position for displaying the curve
        self.pginput.curve.setData(self.Xm)               # set the curve with this data
        self.pginput.curve.setPos(self.ptr,0)             # set x position in the graph to 0
        
        self.x = self.Ym[len(self.Ym)-131:len(self.Ym)-1] #適当な関数で変換
        # self.k = cal(x)
        self.k += random.randint(-5, 5) #### 上記信号計算の代替シミュレーション
        self.Zm[-1] = self.k
        self.pginfer.curve.setData(self.Zm)
        self.pginfer.curve.setPos(self.ptr,0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())