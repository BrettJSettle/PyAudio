import speech_recognition as sr
import numpy as np

from PyQt4 import uic, QtGui

app = QtGui.QApplication([])
class MainWindow(QtGui.QMainWindow):
	def __init__(self):
		super().__init__()
		uic.loadUi('speechrecognition.ui', self)
		self.r = sr.Recognizer()
		self.m = sr.Microphone()
		self.recording = False
		self.actionRecord_Background.triggered.connect(self.record_background)
		self.actionClear_Background.triggered.connect(self.clear_background)
		self.startButton.pressed.connect(self.toggle_recording)

	def record_background(self):
		print("A moment of silence, please...")
		with self.m as source: self.r.adjust_for_ambient_noise(source)
		print("Set minimum energy threshold to {}".format(self.r.energy_threshold))

	def clear_background(self):
		self.r.adjust_for_ambient_noise(self.m, 0)
		print("Set minimum energy threshold to {}".format(self.r.energy_threshold))

	def toggle_recording(self):
		v = self.startButton.text() == 'Start Recording'
		if v:
			self.recording = True
			self.record()
			self.startButton.setText('Stop Recording')
		else:
			self.startButton.setText('Start Recording')
			self.recording = False
			self.stopper()

	def record(self):
		def callback(recognizer, arr):
			try:
				np_arr = np.fromstring(arr.get_raw_data())
				print(recognizer.recognize_google(arr))
			except Exception as e:
				print("Unable to catch that. %s" % e)

		self.stopper = self.r.listen_in_background(self.m, callback)


win = MainWindow()
win.show()
app.exec_()