from PyQt5 import QtCore, QtGui, QtWidgets
from gui import read_file

class read_file_c(QtWidgets.QDialog, read_file):
    _signal = QtCore.pyqtSignal(str)
    def  __init__ (self):
        super(read_file_c, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('./icon.ico'))
        self.__connect()
    
    def __connect(self):
        self.pushButton.clicked.connect(self.save_func)
        self.pushButton_2.clicked.connect(self.close)
    
    def save_func(self):
        # 保存文件
        text = self.textEdit.toPlainText()
        self._signal.emit(text)
        self.close()