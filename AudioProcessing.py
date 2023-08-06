import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np
import scipy
from scipy.io.wavfile import read
from scipy.fft import fft
import matplotlib.pyplot as plt

class App(QWidget):
    def __init__(self):
        super().__init__()

        #time domain data buffors
        self.dataY = []
        self.dataX = []
        self.dataFs = 0
        #frequency domain data buffors
        self.dataYF = []
        self.dataXF = []


        self.title = 'AudioAnalyzer'
        self.left = 100
        self.top = 100
        self.width = 1000
        self.height = 500
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width,self.height)

        self.amplitude = QDoubleSpinBox(self)
        self.amplitude.setValue(1)
        self.amplitude.valueChanged.connect(self.set_data)
        self.frequency = QSpinBox(self)
        self.frequency.setMaximum(100_000)
        self.frequency.setValue(3)
        self.frequency.valueChanged.connect(self.set_data)
        self.sampling_frequency = QSpinBox(self)
        self.sampling_frequency.valueChanged.connect(self.set_data)
        self.sampling_frequency.setMaximum(100_000)
        self.sampling_frequency.setValue(44_100)
        self.time_end = QDoubleSpinBox(self)
        self.time_end.setValue(4)
        self.time_end.valueChanged.connect(self.set_data)

        save = QAction('Save', self)
        save.triggered.connect(self.save)
        upload = QAction('Upload', self)
        upload.triggered.connect(self.upload)
        exit = QAction('Exit', self)
        exit.triggered.connect(self.exit)
        fft_a = QAction('FFT', self)
        fft_a.triggered.connect(self.fourier_transform)
        ifft_a = QAction('IFFT', self)
        ifft_a.triggered.connect(self.inverse_fourier_transform)
        filter_a = QAction('Filter Designer', self)
        filter_a.triggered.connect(self.filter_design)
        aboutProgram = QAction('About', self)
        aboutProgram.triggered.connect(self.about_program)

        self.menuBar = QMenuBar()
        self.fileMenu = QMenu("File")
        self.menuBar.addMenu(self.fileMenu)
        self.fileMenu.addAction(save)
        self.fileMenu.addAction(upload)
        self.fileMenu.addAction(exit)
        self.optionMenu = QMenu('Tools')
        self.menuBar.addMenu(self.optionMenu)
        self.optionMenu.addAction(fft_a)
        self.optionMenu.addAction(ifft_a)
        self.helpMenu = QMenu('Help')
        self.menuBar.addMenu(self.helpMenu)
        self.helpMenu.addAction(aboutProgram)

        self.waveforms = QComboBox(self)
        self.waveforms.addItem("Sine")
        self.waveforms.addItem("Square")
        self.waveforms.addItem("Triangle")
        self.waveforms.addItem("Sawtooth")
        self.waveforms.addItem("White Noise")
        self.waveforms.activated.connect(self.set_data)
        self.waveforms.setCurrentText("Sine")


        amplitude_label = QLabel(self)
        amplitude_label.setText("Amplitude")
        frequency_label = QLabel(self)
        frequency_label.setText("Frequency")
        sampling_frequency_label = QLabel(self)
        sampling_frequency_label.setText("Sampling frequency")
        time_end_label = QLabel(self)
        time_end_label.setText("Signal duration")


        main_layout = QHBoxLayout()
        layout_adjustment = QVBoxLayout()
        graph_layout = QVBoxLayout()

        layout_adjustment.addWidget(self.waveforms)
        layout_adjustment.addWidget(amplitude_label)
        layout_adjustment.addWidget(self.amplitude)
        layout_adjustment.addWidget(frequency_label)
        layout_adjustment.addWidget(self.frequency)
        layout_adjustment.addWidget(sampling_frequency_label)
        layout_adjustment.addWidget(self.sampling_frequency)
        layout_adjustment.addWidget(time_end_label)
        layout_adjustment.addWidget(self.time_end)

        main_layout.addLayout(layout_adjustment)


        self.graph = pg.PlotWidget()
        graph_layout.addWidget(self.graph)
        self.graph_f = pg.PlotWidget()
        graph_layout.addWidget(self.graph_f)

        main_layout.addLayout(graph_layout)


        main_layout.setMenuBar(self.menuBar)

        self.setLayout(main_layout)


        self.show()

    def upload(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", options=options)
        fileName = fileName[60:] #hard coded to change
        # print(fileName)
        Fs, data = read(fileName)
        N = data.size
        Ts = 1 / Fs
        t = np.arange(N) * Ts
        self.dataX = t
        self.dataY = data
        self.dataFs = 1/Ts
        self.plotter()
    def exit(self):
        os._exit(0)

    def fourier_transform(self):
        t = self.dataX
        y = self.dataY
        N = len(t)
        dt = t[1] - t[0]
        yf = np.fft.fft(y)#[0:N // 2]
        xf = np.fft.fftfreq(N, d=dt)#[0:N // 2]
        self.dataXF = xf
        self.dataYF = yf
        self.fft_plotter()


    def inverse_fourier_transform(self):
        xf = self.dataXF
        yf = self.dataYF
        Fs = self.dataFs
        y = np.fft.ifft(yf)
        N = len(xf)
        t = np.arange(0, N / Fs, 1 / Fs)
        self.dataX = t
        self.dataY = np.real(y)
        self.plotter(pen_color="yes")

    def plotter(self, pen_color=None):
        self.graph.clear()
        t = self.dataX
        y = self.dataY
        if pen_color == "yes":
            pen = pg.mkPen(color=(255, 128, 0), width=2)
            self.plot = self.graph.plot(t, y, pen=pen, symbol='o',symbolSize=15, symbolBrush=(255, 0, 128))
        else:

            self.graph.plot(t, y)

    def fft_plotter(self):
        self.graph_f.clear()
        frequency_domain = self.dataXF[0:len(self.dataXF)//2]
        amplitude = self.dataYF[0:len(self.dataXF)//2]
        non_zero_amp = []
        for i in range(len(amplitude)):
            if (amplitude[i]>0.01):
                non_zero_amp.append(i)
        xf_axis = np.max(non_zero_amp)
        amplitude = np.array(amplitude)/len(amplitude)
        self.graph_f.plot(frequency_domain, abs(amplitude))
        self.graph_f.setXRange(0,frequency_domain[xf_axis],padding=0)

    def filter_design(self):
        print("filter")
    def about_program(self):
        print("about")

    def sine(self, amplitude, frequency, time):
        values = amplitude*np.sin(2*np.pi*frequency*time)
        return values

    def square(self, amplitude, frequency, duty_cycle, time):
        values = amplitude*scipy.signal.square(2*np.pi*frequency*time, duty_cycle)
        return values

    def triangle(self, amplitude, frequency, time, symmetry):
        values = amplitude*scipy.signal.sawtooth(2*np.pi*frequency*time, symmetry)
        return values

    def sawtooth(self, amplitude, frequency, time):
        values = amplitude*scipy.signal.sawtooth(2*np.pi*frequency*time)
        return values

    def white_noise(self, mean, standard_deviation, samples_number):
        values = np.random.normal(mean, standard_deviation, size=len(samples_number))
        return values

    def set_data(self):
        amplitude = self.amplitude.value()
        frequency = self.frequency.value()
        sampling_frequency = int(self.sampling_frequency.value())
        time_end = float(self.time_end.value())
        time = np.linspace(0, time_end, int(sampling_frequency * time_end))
        signal = self.waveforms.currentText()
        y = []
        if (signal == "Sine"):
            y = self.sine(amplitude, frequency, time)
        elif (signal == "Square"):
            y = self.square(amplitude, frequency, 0.5, time)
        elif (signal == "Triangle"):
            y = self.triangle(amplitude, frequency, time, 0.5)
        elif (signal == "Sawtooth"):
            y = self.sawtooth(amplitude, frequency, time)
        elif (signal == "White Noise"):
            y = self.white_noise(0, amplitude, time)
        self.dataY = y
        self.dataX = time
        self.dataFs = sampling_frequency
        self.plotter()

    def save(self):
        data = self.dataY
        sampling = 44_100
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getOpenFileName()", "", options=options)
        file = open(f'{fileName}.wav', 'w')
        audio_data = np.int16(data)

        scipy.io.wavfile.write(f'{fileName}.wav', sampling, audio_data)
        file.close()


app = QApplication(sys.argv)
ex = App()
app.exec_()
