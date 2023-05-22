from PyQt5 import QtCore, QtGui, QtWidgets
from gui import folder_select
from PyQt5.QtWidgets import QStyle, QApplication

class folder_select_c(QtWidgets.QDialog, folder_select):
    _signal = QtCore.pyqtSignal(dict)
    def  __init__ (self):
        super(folder_select_c, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('./icon.ico'))
        self.curr_folder.setReadOnly(True)
        self.file_tree_model = QtGui.QStandardItemModel()
        self.folder_tree.setModel(self.file_tree_model)
        self.folder_tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.wake_ui = ""
        self.__connect()
    
    def __connect(self):
        self.ok.clicked.connect(self.ok_func)
        self.cancel.clicked.connect(self.close)
        self.folder_tree.doubleClicked.connect(self.open_file)
    
    def set_wake_ui(self, wake_ui):
        self.wake_ui = wake_ui

    def get_curr_folder_info(self, curr_folder, folder_list, wake_ui, opera=None):
        if wake_ui:
            self.wake_ui = wake_ui
        if opera:
            self.opera = opera
        self.curr_folder.setText(curr_folder)
        self.folder_list = folder_list
        self.file_tree_model.clear()
        for folder in self.folder_list:
            self.file_tree_model.appendRow(QtGui.QStandardItem(QApplication.style().standardIcon(21), folder))
    
    def open_file(self):
        # 打开文件夹
        curr_name = self.folder_tree.currentIndex().data()
        info = {"func": "open_folder", "wake": self.wake_ui, "info": {'mode':'get_folder','ui': 'folder_select', 'info':self.curr_folder.text()+curr_name}}
        self._signal.emit(info)
    
    def ok_func(self):
        # 确认
        if self.wake_ui == "main":
            info = {"func": "ok", "wake": self.wake_ui, "info": {"target": self.curr_folder.text(), "opera": self.opera}}
            self._signal.emit(info)
        elif self.wake_ui == "task":
            info = {"func": "ok", "wake": self.wake_ui, "info": {"target": self.curr_folder.text()}}
            self._signal.emit(info)
        else:
            pass
        self.close()
    