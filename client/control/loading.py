from PyQt5 import QtCore, QtGui, QtWidgets
from gui import loading

class loading_c(QtWidgets.QDialog, loading):
    def  __init__ (self, parent=None):
        super(loading_c, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('./icon.ico'))
    
    def set_text(self, text: str):
        # 设置显示文字
        self.label.setText(text)