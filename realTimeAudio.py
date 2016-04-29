import sys
import numpy as np
from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
from recorder import *
import wave
import pyqtgraph as pg
import file_manager
import script_editor
import scipy.io.wavfile as wav_reader


class RecorderWidget(QtGui.QWidget):
    x = np.array([0])
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        uic.loadUi('recorderWidget.ui', self)
        self.installEventFilter(self)
        self.setAcceptDrops(True)
        self.soundLine=pg.PlotDataItem()
        self.fftLine = pg.PlotDataItem()
        self.fftWidget.addItem(self.fftLine)
        self.soundWidget.addItem(self.soundLine)
        self.soundWidget.setYRange(-10, 10)
        self.fftWidget.setYRange(0, 1000)

        self.timer = QTimer()
        self.timer.start(1.0)
        self.connect(self.timer, SIGNAL('timeout()'), self.plotAudio) 

        self.listener=SoundListener()
        self.setupSpectrogram()
        self.listener.setup()
        self.recordButton.pressed.connect(self.recordPressed)

    def plotAudio(self):
        if self.listener.newAudio==False:
            return
        xs = len(RecorderWidget.x)
        RecorderWidget.x = np.hstack([RecorderWidget.x, self.listener.audio / 1000])
        self.soundLine.setData(self.listener.audio / 1000)
        xs,ys=self.listener.fft()
        ys /= 1000
        self.fftLine.setData(x=xs, y=ys)
        self.updateSpectrogram(self.listener.audio)
        self.listener.newAudio=False
        return

        xs,ys=self.listener.fft()
        RecorderWidget.x = np.hstack([RecorderWidget.x, xs + max(RecorderWidget.x)])
        self.soundLine.setData(xs)

    def setupSpectrogram(self):
        self.spectrogramItem = pg.ImageItem()
        self.spectrogramWidget.addItem(self.spectrogramItem)

        self.spectrogram_array = np.zeros((1000, self.listener.BUFFERSIZE/2+1))

        # bipolar colormap
        pos = np.array([0., 1., 0.5, 0.25, 0.75])
        color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
        cmap = pg.ColorMap(pos, color)
        lut = cmap.getLookupTable(0.0, 1.0, 256)

        self.spectrogramItem.setLookupTable(lut)
        self.spectrogramItem.setLevels([-50,40])

        freq = np.arange((self.listener.BUFFERSIZE/2)+1)/(float(self.listener.BUFFERSIZE)/self.listener.RATE)
        yscale = 1.0/(self.spectrogram_array.shape[1]/freq[-1])
        self.spectrogramItem.scale((1./self.listener.RATE)*self.listener.BUFFERSIZE, yscale)

        self.spectrogramWidget.setLabel('left', 'Frequency', units='Hz')

        self.spectrogramWidget.win = np.hanning(self.listener.BUFFERSIZE)
        self.spectrogramWidget.show()

    def updateSpectrogram(self, chunk):
        # normalized, windowed frequencies in data chunk
        spec = np.fft.rfft(chunk*self.spectrogramWidget.win) / self.listener.BUFFERSIZE
        # get magnitude 
        psd = abs(spec)
        # convert to dB scale
        psd = 20 * np.log10(psd)

        # roll down one and replace leading edge with new data
        self.spectrogram_array = np.roll(self.spectrogram_array, -1, 0)
        self.spectrogram_array[-1:] = psd

        self.spectrogramItem.setImage(self.spectrogram_array, autoLevels=False)

    def recordPressed(self):
        if self.recordButton.text() == 'Record':
            self.recordButton.setText('Stop Recording')
            self.listener.continuousStart()
        else:
            self.recordButton.setText('Record')
            self.listener.continuousEnd()
            self.listener.setup()
        
if __name__ == "__main__":
    app = QtGui.QApplication([])
        
    rw = RecorderWidget()
        ### DISPLAY selfDOWS
    rw.show()
    code=app.exec_()
    rw.listener.close()
    sys.exit(code)