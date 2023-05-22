from PyQt5 import QtWidgets, QtCore, QtGui
from control import main_ui_c
import os
import sys, time

class mywindow(QtWidgets.QMainWindow, main_ui_c):
    def  __init__ (self):
        super(mywindow, self).__init__()
        self.setWindowTitle("分布式深度学习任务管理系统")
        self.setWindowIcon(QtGui.QIcon('./icon.ico'))

def run():
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    ui = mywindow()
    ui.show()
    sys.exit(app.exec_())

if __name__=="__main__":
    run()