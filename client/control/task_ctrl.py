from PyQt5 import QtCore, QtGui, QtWidgets
from gui import task_ctrl
import time

class task_ctrl_c(QtWidgets.QDialog, task_ctrl):
    _signal = QtCore.pyqtSignal(dict)
    def  __init__ (self):
        super(task_ctrl_c, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('./icon.ico'))
        reg = QtCore.QRegExp(r'^[0-9]*[1-9][0-9]*$')
        pValidator = QtGui.QRegExpValidator(self)
        pValidator.setRegExp(reg)
        self.need_GPUs.setValidator(pValidator)
        self.__connect()
        self.folder_name.setReadOnly(True)
        self.task_id = None
        self.ok.setDefault(True)
        self.ok.setAutoDefault(True)
        
    
    def __connect(self):
        # 逻辑操作与按钮连接
        self.open_folder.clicked.connect(self.open_folder_func)
        self.ok.clicked.connect(self.ok_func)
        self.cancel.clicked.connect(self.close)
        pass

    def init(self, slaver_list, curr_task_ids):
        # 添加任务时显示的信息
        self.task_id = None
        self.folder_name.setText("/data/")
        self.exec_name.setText("")
        self.need_GPUs.setText("1")
        self.set_slaver.clear()
        self.set_slaver.addItem("<默认>")
        self.set_slaver.addItems(slaver_list)
        self.prev_task.clear()
        self.prev_task.addItem("(无)")
        self.prev_task.addItems(curr_task_ids)
        self.is_urgent.setChecked(False)
        self.is_reuse_GPU.setChecked(False)

    def set_info(self, info, slaver_list, curr_task_ids, task_id=None):
        # 设置修改任务信息
        self.task_id = task_id
        self.set_slaver.clear()
        self.set_slaver.addItem("<默认>")
        self.set_slaver.addItems(slaver_list)
        self.prev_task.clear()
        self.prev_task.addItem("(无)")
        self.prev_task.addItems(curr_task_ids)
        if not info["envs"] == "":
            for i in range(self.envs.count()):
                if info["envs"] == self.envs.itemText(i):
                    self.envs.setCurrentIndex(i)
        self.folder_name.setText(info["path"])
        self.exec_name.setText(info["exec"])
        if not info["slaver"] == "<默认>":
            for i in range(self.set_slaver.count()):
                if info["slaver"] == self.set_slaver.itemText(i):
                    self.set_slaver.setCurrentIndex(i)
        self.need_GPUs.setText(str(info["need_gpus"]))
        for i in range(self.prev_task.count()):
            if info["prev"] == self.prev_task.itemText(i):
                self.prev_task.setCurrentIndex(i)
            if self.task_id == self.prev_task.itemText(i):
                self.prev_task.removeItem(i)
        self.is_urgent.setChecked(info["is_urgent"])
        self.is_reuse_GPU.setChecked(info["is_reuse_gpu"])
        pass

    def open_folder_func(self):
        # 打开文件夹
        self._signal.emit({"func": "open_folder","info": ""})
        pass

    def ok_func(self):
        # 确认
        if self.exec_name.text() == "":
            QtWidgets.QMessageBox.warning(self, "错误", "请输入执行命令")
            return
        if self.need_GPUs.text() == "":
            QtWidgets.QMessageBox.warning(self, "错误", "请输入所需GPU数量")
            return
        task_info = {   # 任务信息
            "task_id": self.task_id if self.task_id else "",    # 任务id，新建任务时id为空，修改时为该任务的id
            "envs": self.envs.currentText(),  # 执行任务时的环境
            "path": self.folder_name.text(),    # 执行任务时进入的文件夹路径
            "exec": self.exec_name.text(),     # 任务的执行命令
            "need_gpus": self.need_GPUs.text(),    # 执行该任务所需的gpu数量
            "slaver": self.set_slaver.currentText(),    # 指定任务分配在哪个计算节点
            "prev": self.prev_task.currentText(),   # 前驱任务，只有前驱任务执行完毕后才会执行当前任务
            "is_urgent": 1 if self.is_urgent.isChecked() else 0,  # 该任务是否紧急
            "is_reuse_gpu": 1 if self.is_reuse_GPU.isChecked() else 0,    # 该任务是否复用GPU(即一个gpu上运行多个任务)
            "state": ""     #状态
        }
        # print(task_info)
        self._signal.emit({"func": "ok", "info": task_info})
        self.close()