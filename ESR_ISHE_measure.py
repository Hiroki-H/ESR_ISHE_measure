#%%　imoprt package
from queue import Queue
import re
import pyvisa as visa
import time  
import matplotlib.pyplot as plt 
import pandas as pd 
import matplotlib.cm as cm
import numpy as np
from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

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
    def ISHE_measure(self):
        while self.ROOP:
            global x, y
            x = np.arange(0, 2*np.pi, 0.05*np.pi)
            y = np.sin(x)
            print(1)
            time.sleep(1)
        return x,y
    
        #スレッドをスタートさせる
    def start(self):
        thread = ThreadPoolExecutor()
        future = thread.submit(self.ISHE_measure)
        # thread = threading.Thread(target = self.ISHE_measure)
        # thread.start()

    def make_data_fig(self,fig,x,y,make = True):
        if make:
            self.ax.plot(x, y,'o-')
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('y')
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

    layout = [[sg.Text('measurement_system')],
            [sg.Button('Start Measure',key='-start-'), sg.Button('stop',key='-stop-'), sg.Button('Clear',key='-clear-'), sg.Cancel('close'),sg.Button('view',key='-view-')],
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
        print(x,y)
        print('測定が終了しました。')


    fig_agg = ISHE.draw_figure(window['-CANVAS-'].TKCanvas, ISHE.fig)

    while True:
        event, values = window.read()

        if event in (None, 'close'):
            break
        elif event == '-start-':
            a= startEvent(event)
            #x,y=ISHE.ISHE_measure()
        elif event == '-view-':
            fig = ISHE.make_data_fig(ISHE.fig,x,y, make=True)
            fig_agg.draw()
        elif event == '-stop-':
            end_measure(event)
        elif event == '-clear-':
            fig = ISHE.make_data_fig(ISHE.fig,x,y, make=False)
            fig_agg.draw()

    window.close()