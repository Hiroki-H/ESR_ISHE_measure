#%%　imoprt package
from queue import Queue
import re
from turtle import update
import pyvisa as visa
import time  
import matplotlib.pyplot as plt 
import pandas as pd 
import matplotlib.cm as cm
import numpy as np
from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#import threading
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import PySimpleGUI as sg

#%% confirming the address connected to GPIB
# rm=visa.ResourceManager() 
# print(rm.list_resources())


# #%% define kethley2182A nanovoltmeter
# keithley2182A = rm.open_resource(  'GPIB0::8::INSTR'  )
# #%% set keithley2182
# #keithley2182A.write("*RST")
# keithley2182A.write(":SENSe:VOLTage:NPLCycles 1") # medium
# keithley2182A.write(":SENSe:VOLTage:DFILter 0") # digital filter off


"""
MatplotlibのグラフをCanvasに埋め込む

"""
class ISHE_sys:
    def __init__(self):
        self.fig = plt.figure(figsize=(5, 4))
        self.ax = self.fig.add_subplot(111)
        self.ROOP = True #ループのフラグ
        self.x=[]
        self.y=[]
    # pyqtgraph live plot

    def update(self,x1,y1):
        global curve, ptr, x ,y
        #   Xm[:-1] = Xm[1:]                      # shift data in the temporal mean 1 sample left
        #keithley2450.write(":SOUR:VOLT " + str(V))
        #yvalue = keithley2450.query(":READ? \"defbuffer1\" ,source")
        #xvalue =  keithley2450.query(":READ?")       # read line (single value) from the serial port
        self.x.append(float(x1))
        self.y.append(float(y1))
        #   Xm[-1] = float(value)                 # vector containing the instantaneous values
        #   ptr += 1                              # update x position for displaying the curve
        curve.setData(self.x,self.y)                     # set the curve with this data
        #curve.setPos(0,float(x[-1]))                   # set x position in the graph to 0
        pg.QtGui.QApplication.processEvents()    # you MUST process the plot now


    def ISHE_measure(self):
        i=1
        global points, V
        points=[]
        V=[]
        while self.ROOP:
            points.append(i)
            V.append(np.sin(i/180*np.pi))
            i+=10
            self.update(i,np.sin(i/180*np.pi))
            time.sleep(0.5)
        return points,V


    
        #スレッドをスタートさせる
    def start(self):
        thread = ThreadPoolExecutor()
        future = thread.submit(self.ISHE_measure)
        # thread = threading.Thread(target = self.ISHE_measure)
        # thread.start()

    def make_data_fig(self,fig,points,V,make = True):
        if make:
            self.ax.plot(points, V,'o-')
            self.ax.set_xlabel('data_number')
            self.ax.set_ylabel('$V_{ISHE}$ (V)')
            fig.tight_layout()
            return fig

        else:
            self.ax.cla()
            return fig

    def draw_figure(self,canvas, figure):
        figure_canvas = FigureCanvasTkAgg(figure, canvas)
        figure_canvas.draw()
        figure_canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas


if __name__ == '__main__':

        
    sg.theme('Light Blue 2')

    layout = [[sg.Text('measurement_system with keithley2182A(nanovoltmeter)')],
    [sg.Text("save_file"), sg.InputText(), sg.FolderBrowse(key="save_file")],
    [sg.Text('filename', size=(6, 1)), sg.In(default_text='test', size=(30, 1),key='filename')],
    [sg.Text('GPIB address', size=(10, 1)), sg.In(default_text='GPIB0::8::INSTR', size=(30, 1),key='GPIB')],
            [sg.Button('Start Measure',key='-start-'), sg.Button('Stop',key='-stop-'),sg.Button('View',key='-view-'), sg.Button('Clear',key='-clear-'),
            sg.Button('Save',key='-save-'), sg.Cancel('Close')],
            [sg.Canvas(key='-CANVAS-')]
            ]

    window = sg.Window('ISHE measurement window', layout, location =(100,100), finalize=True)

    # figとCanvasを関連付ける
    ISHE=ISHE_sys()

    def startEvent(event):#スタートボタン押下時の処理
        ISHE.ROOP = True
        ISHE.start()
    def end_measure(event):
        ISHE.ROOP = False
        print('測定が終了しました。')


    fig_agg = ISHE.draw_figure(window['-CANVAS-'].TKCanvas, ISHE.fig)

    while True:
        event, values = window.read()

        if event in (None, 'Close'):
            break
        elif event == '-start-':
            try:
                ### START QtApp #####
                app = pg.QtGui.QApplication([])            # you MUST do this once (initialize things)
                ####################
                win = pg.GraphicsWindow(title='Signal from serial port') # creates a window
                p = win.addPlot(title='Realtime plot')  # creates empty space for the plot in the window
                curve = p.plot( pen =(0, 114, 189), symbolBrush =(0, 114, 189),
                                    symbolPen ='w', symbol ='p', symbolSize = 14, name ="symbol ='p'")
                p.showGrid(x=True,y=True)
                p.setLabel('left', "Resistance", units='ohm')
                p.setLabel('bottom', "Current", units='A')
                a= startEvent(event)
                #x,y=ISHE.ISHE_measure()
            except Exception as e:
                sg.popup('この操作は受け付けられないな( ･´ｰ･｀)\n'+str(e),title='Error')
        elif event == '-view-':
            try:
                fig = ISHE.make_data_fig(ISHE.fig,points,V, make=True)
                fig_agg.draw()
            except Exception as e:
                sg.popup('この操作は受け付けられないな( ･´ｰ･｀)\n'+str(e),title='Error')
        elif event == '-stop-':
            end_measure(event)
        elif event == '-clear-':
            try:
                fig = ISHE.make_data_fig(ISHE.fig,points,V, make=False)
                fig_agg.draw()
            except Exception as e:
                sg.popup('この操作は受け付けられないな( ･´ｰ･｀)\n'+str(e),title='Error')
        elif event == '-save-':
            try:
                data = pd.DataFrame([points,V], index=['data_points','V_ISHE(V)']).T
                data.to_csv(values['save_file']+'/'+values['filename']+'.csv',index = False)
            except Exception as e:
                sg.popup('（´・ω・｀）データが保存できないお\n'+str(e),title='Error')


    window.close()