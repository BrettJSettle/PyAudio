from sklearn.svm import SVC
import numpy as np
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import pyqtgraph as pg
import os, sys
from PyQt4 import uic
import file_manager
from scipy.io import wavfile
from recorder import SoundPlayer
if sys.version_info.major==2:
	import cPickle as pickle # pickle serializes python objects so they can be saved persistantly.  It converts a python object into a savable data structure
else:
	import pickle

class SoundPlotWidget(pg.PlotWidget):
	def __init__(self, parent=None):
		pg.PlotWidget.__init__(self, parent)
		self.setXRange(0, 60000)
		self.setYRange(-20000, 20000)
		self.bounds = pg.LinearRegionItem()
		self.disableAutoRange()
		self.soundLine = pg.PlotDataItem()
		#sound line can be 2D with stereo. Plot 2 lines?
		self.addItem(self.bounds)
		self.bounds.setMovable(False)
		for l in self.bounds.lines:
			l.setMovable(True)
		self.addItem(self.soundLine)
		self.getViewBox().mouseDragEvent = self.onDrag

	def onDrag(self, event, **kargs):
		x1, x2 = self.bounds.getRegion()
		pos = self.mapToView(event.scenePos())
		if event.isStart():
			self.bounds.setRegion([pos.x(), pos.x()])
			event.accept()
			return
		elif event.isFinish():
			self.bounds.setRegion([x1, pos.x()])
			event.accept()
			return
		elif len(kargs) == 0:
			self.bounds.setRegion([x1, pos.x()])
			event.accept()
			return
		pg.ViewBox.mouseDragEvent(self.getViewBox(), event, **kargs)

	def setData(self, data):
		self.soundLine.setData(data)
		self.bounds.setBounds([0, len(data)])

	def getSelection(self):
		x1, x2 = self.bounds.getRegion()
		x, y = self.soundLine.getData()
		return y[x1:x2+1]



class LetterClassifier(SVC):
	'''
	C=1.0, cache_size=200, class_weight=None, coef0=0.0,
	decision_function_shape=None, degree=3, gamma='auto', kernel='rbf',
	max_iter=-1, probability=False, random_state=None, shrinking=True,
	tol=0.001, verbose=False)
	'''
	mem_file = os.path.join(os.environ['APPDATA'], 'training_data.npz')
	def __init__(self, **kargs):
		SVC.__init__(self, **kargs)
		self.trainX = []
		self.trainY = []
		self.names = []
		self.model = None
		self.player = SoundPlayer()
		self.load_mem()

	def plotWavFile(self, fname):
		if fname == '':
			return
		self.filename = fname
		self.build_recent_actions()
		s, data = wavfile.read(fname)
		print("Wav file has rate %s and shape %s" % (s, np.shape(data)))
		if np.ndim(data) > 1:
			print("Data has %d dimensions, 1st is being used" % np.ndim(data))
			data = data[:, 0]
		self.ui.plotWidget.setData(data)

	def teach_gui(self):

		if not hasattr(self, 'ui'):
			self.ui = uic.loadUi('LetterClassifier.ui')
			self.ui.consoleWidget.localNamespace.update({'classifier': self, 'plot': self.ui.plotWidget, 'player': self.player, 'ui': self.ui, "recorderWidget": self.ui.recorderWidget})
			self.ui.actionOpen.triggered.connect(lambda : self.plotWavFile(file_manager.getOpenFileName()))
			self.ui.actionSave_Memory.triggered.connect(lambda : self.save(file_manager.getSaveFileName()))
			self.ui.menuRecent_Files.aboutToShow.connect(self.build_recent_actions)
			self.ui.browseButton.pressed.connect(lambda : self.plotWavFile(file_manager.getOpenFileName()))
			self.ui.learnButton.pressed.connect(self.ui_learn_pressed)
			self.ui.unlearnButton.pressed.connect(self.ui_unlearn_pressed)
			self.ui.loadButton.pressed.connect(lambda : self.load_mem(file_manager.getOpenFileName()))
			self.ui.clearMemButton.pressed.connect(lambda : self.clear_memory(erase=False))
			self.ui.predictButton.pressed.connect(self.ui_predict_pressed)
			self.ui.outputTree.itemClicked.connect(self.ui_tree_clicked)
			self.ui.setAcceptDrops(True)
			self.ui.playButton.pressed.connect(self.play_selection)
			self.ui.eventFilter = self.eventFilter
			self.ui.installEventFilter(self.ui)
			self.build_recent_actions()
			self.ui.closeEvent = lambda ev: self.save()
		self.ui.show()
		self.updateTreeView()

	def ui_tree_clicked(self, item):
		if item.parent() != None:
			data = self.trainX[self.names.index(item.text(0))]
			self.ui.plotWidget.soundLine.setData(data)
			item = item.parent()
		self.ui.outputLineEdit.setText(item.text(0))

	def play_selection(self):
		selection = self.ui.plotWidget.getSelection()
		self.player.write(selection)

	def build_recent_actions(self):
		self.ui.menuRecent_Files.clear()
		def plotFunc(fname):
			return lambda : self.plotWavFile(fname)
		if len(file_manager.recent_files()) == 0:
			no_recent = self.ui.menuRecent_Files.addAction("No Recent Files")
			no_recent.setEnabled(False)
			self.ui.menuRecent_Files.addAction(no_recent)
		for fname in file_manager.recent_files():
			self.ui.menuRecent_Files.addAction(QAction(fname, self.ui.menuRecent_Files, triggered=plotFunc(fname)))

	def eventFilter(self,obj,event):
		if (event.type()==QEvent.DragEnter):
			if event.mimeData().hasUrls():
				event.accept()   # must accept the dragEnterEvent or else the dropEvent can't occur !!!
			else:
				event.ignore()
		if (event.type() == QEvent.Drop):
			if event.mimeData().hasUrls():   # if file or link is dropped
				file_manager.update_history(*[url.toString()[8:] for url in event.mimeData().urls()])
				url = event.mimeData().urls()[0]   # get first url
				filename=url.toString()
				filename=str(filename)
				filename=filename.split('file:///')[1]
				print('filename={}'.format(filename))
				self.plotWavFile(filename)  #This fails on windows symbolic links.  http://stackoverflow.com/questions/15258506/os-path-islink-on-windows-with-python
				event.accept()
			else:
				event.ignore()
		return False # lets the event continue to the edit

	def ui_learn_pressed(self):
		values = self.ui.plotWidget.getSelection()
		output = str(self.ui.outputLineEdit.text())
		self.ui.outputLineEdit.clear()
		name = os.path.basename(self.filename)
		num = 2
		while name in self.names:
			name = "%s_%d" % (os.path.basename(self.filename), num)
			num += 1
		self.add_training_case(name, values, output)
		self.updateTreeView()

	def ui_unlearn_pressed(self):
		items = self.ui.outputTree.selectedItems()
		for item in items:
			try:
				i = self.names.index(item.text(0))
				self.trainX.pop(i)
				self.trainY.pop(i)
				self.names.pop(i)
			except Exception as e:
				print(e)
		self.updateTreeView()

	def ui_predict_pressed(self):
		self.fit()
		points = self.ui.plotWidget.getSelection()
		xs = [points[i] for i in np.linspace(0, len(points)-1, self.ui.intervalSpin.value())]
		val = self.predict(xs)
		self.ui.predictionLabel.setText("%s" % val)

	def updateTreeView(self):
		if not hasattr(self, 'ui') or not self.ui.isVisible():
			print("no ui")
			return
		self.ui.outputTree.clear()
		items = {}
		for i, output in enumerate(self.trainY):
			if output in items:
				items[output].append(QTreeWidgetItem([self.names[i]]))
			else:
				items[output] = [QTreeWidgetItem([self.names[i]])]
		for output, children in items.items():
			item = QTreeWidgetItem([output])
			item.addChildren(children)
			self.ui.outputTree.addTopLevelItem(item)

	def clear_memory(self, erase=False):
		self.trainX = []
		self.trainY = []
		self.names = []
		self.updateTreeView()
		if erase:
			os.remove(LetterClassifier.mem_file)

	def add_training_case(self, name, x, y):
		self.trainX.append([i for i in x])
		self.trainY.append(y)
		self.names.append(name)
			
	def fit(self):
		x = []
		y = []
		for i in range(len(self.names)):
			js = np.linspace(0, len(self.trainX[i]) - 1, self.ui.intervalSpin.value(), dtype=np.int)
			x.append([self.trainX[i][j] for j in js])
			y.append(self.trainY[i])
		self.model = SVC.fit(self, x, y)

	def predict(self, X):
		return SVC.predict(self, X)

	def save(self, fname=None):
		if fname == None:
			fname = LetterClassifier.mem_file
		pickle.dump({'trainX': self.trainX, 'trainY': self.trainY, 'names': self.names}, open(fname, 'wb'))
		#np.savez(LetterClassifier.mem_file, trainX=self.trainX, trainY=self.trainY, names=self.names)
		
	def load_mem(self, fname=None):
		if fname == None:
			fname = LetterClassifier.mem_file
		try:	
			if os.path.exists(fname):
				#f = np.load(fname)
				f = pickle.load(open(fname, 'rb'))
				self.trainX = f['trainX']
				self.trainY = f['trainY']
				self.names = f['names']
			if len(self.trainX) != len(self.trainY) or len(self.trainX) != len(self.names) or len(self.trainY) != len(self.names):
				raise Exception("Invalid sizes")
		except Exception as e:
			print(e)
			if input("Clear memory (y/n): ") == 'y':
				self.clear_memory()

if __name__ == '__main__':
	app = QApplication([])
	LC = LetterClassifier()
	LC.teach_gui()
	app.exec_()
