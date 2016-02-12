# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_plot.ui'
#
# Created: Tue Jan 26 10:57:42 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_win_plot(object):
    def setupUi(self, win_plot):
        win_plot.setObjectName(_fromUtf8("win_plot"))
        win_plot.resize(1220, 872)
        self.centralwidget = QtGui.QWidget(win_plot)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.editorButton = QtGui.QPushButton(self.centralwidget)
        self.editorButton.setObjectName(_fromUtf8("editorButton"))
        self.horizontalLayout.addWidget(self.editorButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.playButton = QtGui.QPushButton(self.centralwidget)
        self.playButton.setObjectName(_fromUtf8("playButton"))
        self.horizontalLayout.addWidget(self.playButton)
        self.openButton = QtGui.QPushButton(self.centralwidget)
        self.openButton.setObjectName(_fromUtf8("openButton"))
        self.horizontalLayout.addWidget(self.openButton)
        self.recordButton = QtGui.QPushButton(self.centralwidget)
        self.recordButton.setObjectName(_fromUtf8("recordButton"))
        self.horizontalLayout.addWidget(self.recordButton)
        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 10)
        self.horizontalLayout.setStretch(2, 2)
        self.horizontalLayout.setStretch(3, 2)
        self.horizontalLayout.setStretch(4, 2)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 2)
        self.tlWidget = PlotWidget(self.centralwidget)
        self.tlWidget.setObjectName(_fromUtf8("tlWidget"))
        self.gridLayout.addWidget(self.tlWidget, 0, 0, 1, 1)
        self.trWidget = PlotWidget(self.centralwidget)
        self.trWidget.setObjectName(_fromUtf8("trWidget"))
        self.gridLayout.addWidget(self.trWidget, 0, 1, 1, 1)
        self.blWidget = PlotWidget(self.centralwidget)
        self.blWidget.setObjectName(_fromUtf8("blWidget"))
        self.gridLayout.addWidget(self.blWidget, 1, 0, 1, 1)
        self.brWidget = SpectrogramWidget(self.centralwidget)
        self.brWidget.setObjectName(_fromUtf8("brWidget"))
        self.gridLayout.addWidget(self.brWidget, 1, 1, 1, 1)
        self.gridLayout.setRowStretch(0, 1)
        self.gridLayout.setRowStretch(1, 1)
        win_plot.setCentralWidget(self.centralwidget)

        self.retranslateUi(win_plot)
        QtCore.QMetaObject.connectSlotsByName(win_plot)

    def retranslateUi(self, win_plot):
        win_plot.setWindowTitle(_translate("win_plot", "MainWindow", None))
        self.editorButton.setText(_translate("win_plot", "Editor", None))
        self.playButton.setText(_translate("win_plot", "Play Selected", None))
        self.openButton.setText(_translate("win_plot", "Open File", None))
        self.recordButton.setText(_translate("win_plot", "Record", None))

from SpectrogramWidget import SpectrogramWidget
from pyqtgraph import PlotWidget

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    win_plot = QtGui.QMainWindow()
    ui = Ui_win_plot()
    ui.setupUi(win_plot)
    win_plot.show()
    sys.exit(app.exec_())

