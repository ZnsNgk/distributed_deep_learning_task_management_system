# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'task_control.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(300, 480)
        Dialog.setMinimumSize(QtCore.QSize(300, 480))
        Dialog.setMaximumSize(QtCore.QSize(300, 480))
        self.cancel = QtWidgets.QPushButton(Dialog)
        self.cancel.setGeometry(QtCore.QRect(160, 430, 131, 41))
        self.cancel.setObjectName("cancel")
        self.ok = QtWidgets.QPushButton(Dialog)
        self.ok.setGeometry(QtCore.QRect(10, 430, 131, 41))
        self.ok.setObjectName("ok")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 30, 71, 21))
        self.label.setObjectName("label")
        self.envs = QtWidgets.QComboBox(Dialog)
        self.envs.setGeometry(QtCore.QRect(100, 30, 191, 21))
        self.envs.setObjectName("envs")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 86, 81, 20))
        self.label_2.setObjectName("label_2")
        self.open_folder = QtWidgets.QPushButton(Dialog)
        self.open_folder.setGeometry(QtCore.QRect(200, 80, 93, 28))
        self.open_folder.setObjectName("open_folder")
        self.folder_name = QtWidgets.QLineEdit(Dialog)
        self.folder_name.setGeometry(QtCore.QRect(10, 120, 281, 21))
        self.folder_name.setObjectName("folder_name")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(10, 170, 72, 21))
        self.label_4.setObjectName("label_4")
        self.exec_name = QtWidgets.QLineEdit(Dialog)
        self.exec_name.setGeometry(QtCore.QRect(100, 170, 191, 21))
        self.exec_name.setObjectName("exec_name")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(10, 220, 111, 21))
        self.label_5.setObjectName("label_5")
        self.set_slaver = QtWidgets.QComboBox(Dialog)
        self.set_slaver.setGeometry(QtCore.QRect(170, 220, 121, 22))
        self.set_slaver.setObjectName("set_slaver")
        self.set_slaver.addItem("")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(10, 270, 131, 20))
        self.label_3.setObjectName("label_3")
        self.need_GPUs = QtWidgets.QLineEdit(Dialog)
        self.need_GPUs.setGeometry(QtCore.QRect(172, 270, 121, 21))
        self.need_GPUs.setObjectName("need_GPUs")
        self.is_urgent = QtWidgets.QCheckBox(Dialog)
        self.is_urgent.setGeometry(QtCore.QRect(10, 390, 91, 19))
        self.is_urgent.setObjectName("is_urgent")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(10, 310, 101, 20))
        self.label_6.setObjectName("label_6")
        self.prev_task = QtWidgets.QComboBox(Dialog)
        self.prev_task.setGeometry(QtCore.QRect(10, 340, 281, 22))
        self.prev_task.setObjectName("prev_task")
        self.prev_task.addItem("")
        self.is_reuse_GPU = QtWidgets.QCheckBox(Dialog)
        self.is_reuse_GPU.setGeometry(QtCore.QRect(160, 390, 91, 19))
        self.is_reuse_GPU.setObjectName("is_reuse_GPU")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.ok.setText(_translate("Dialog", "确认"))
        self.cancel.setText(_translate("Dialog", "取消"))
        self.label.setText(_translate("Dialog", "选择环境："))
        self.label_2.setText(_translate("Dialog", "项目路径："))
        self.open_folder.setText(_translate("Dialog", "打开文件夹"))
        self.label_4.setText(_translate("Dialog", "执行命令："))
        self.label_5.setText(_translate("Dialog", "指定计算节点："))
        self.set_slaver.setItemText(0, _translate("Dialog", "<默认>"))
        self.label_3.setText(_translate("Dialog", "需求的GPU数量："))
        self.need_GPUs.setText(_translate("Dialog", "1"))
        self.is_urgent.setText(_translate("Dialog", "紧急任务"))
        self.label_6.setText(_translate("Dialog", "前驱任务："))
        self.prev_task.setItemText(0, _translate("Dialog", "(无)"))
        self.is_reuse_GPU.setText(_translate("Dialog", "复用GPU"))
