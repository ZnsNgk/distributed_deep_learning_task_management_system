from PyQt5 import QtCore, QtGui, QtWidgets
from gui import filename_ctrl

class filename_ctrl_c(QtWidgets.QDialog, filename_ctrl):
    _signal = QtCore.pyqtSignal(dict)
    def  __init__ (self):
        super(filename_ctrl_c, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('./icon.ico'))
        self.old_name = ""
        self.__connect()
    
    def __connect(self):
        self.name.returnPressed.connect(self.sent)
    
    def set_info(self, mode: str, root: str):
        self.mode = mode
        self.root = root
    
    def set_text(self, text: str):
        # 设置显示文字
        self.title.setText(text)
    
    def set_filename(self, name: str):
        # 获得原始文件名
        self.name.setText(name)
        self.old_name = name
    
    def sent(self):
        # 将名称返回给主窗口
        info = {"mode": self.mode, "root": self.root, "name": self.name.text(), "old_name": self.old_name}
        self._signal.emit(info)
        self.close()