from PyQt5 import QtCore, QtGui, QtWidgets

class LogTextEdit(QtWidgets.QPlainTextEdit):
    def write(self, message: str):
        # self.moveCursor(QtGui.QTextCursor.End)
        # self.insertPlainText(message)

        # print(message.encode())
        message = message.replace("\r\n", "\n")
        message = message.split("\r")
        for m in message:
            if not m and m == message[0]:
                continue
            if not m:
                continue
            if len(m) == 1 and m[0] == "\n":
                self.appendPlainText("")
            self.replace_last_line(m)

        # if not hasattr(self, "flag"):
        #     self.flag = False
        # if not hasattr(self, "is_tqdm"):
        #     self.is_tqdm = False
        # if not hasattr(self, "last_tqdm"):
        #     self.last_tqdm = ""
        # if not hasattr(self, "space_line"):
        #     self.space_line = 0
        # message = message.replace('\r', '\n')
        # message = message.split("\n")
        # if message[0] == "":
        #     message = message[1:]
        # for m in message:
        #     if m:
        #         if "%" in m and "|" in m and "/" in m and "[" in m and "," in m and "]" in m and "<" in m and ("/s" in m or "s/" in m):
        #             self.is_tqdm = True
        #         else:
        #             self.is_tqdm = False
        #         if self.flag:
        #             if self.last_tqdm == m:
        #                 method = "replace_last_line"
        #             else:
        #                 method = "replace_last_line"
        #         else:
        #             method = "appendPlainText"
        #         QtCore.QMetaObject.invokeMethod(self,
        #             method,
        #             QtCore.Qt.QueuedConnection, 
        #             QtCore.Q_ARG(str, m))
        #         if self.is_tqdm == True:
        #             self.flag = True
        #             self.last_tqdm = m
        #         else:
        #             self.flag = False
        #     else:
        #         if self.is_tqdm == True:
        #             self.flag = True
        #         else:
        #             self.flag = False
        #         self.space_line += 1
        #         if self.space_line == 2:
        #             QtCore.QMetaObject.invokeMethod(self,
        #             "appendPlainText",
        #             QtCore.Qt.QueuedConnection, 
        #             QtCore.Q_ARG(str, ""))
        #             self.space_line = 0
        # self.space_line = 0

    @QtCore.pyqtSlot(str)
    def replace_last_line(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.select(QtGui.QTextCursor.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.insertBlock()
        self.setTextCursor(cursor)
        self.insertPlainText(text)