from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QStyle, QApplication
from gui import main_ui
from control.task_ctrl import task_ctrl_c
from control.loading import loading_c
from control.filename_control import filename_ctrl_c
from control.folder_select import folder_select_c
from control.read_file import read_file_c
from control.help_file import readme_c
from control.thread import comm_thread, scp_thread, log_thread, terminal_thread
import copy
import json, time
import base64

class main_ui_c(main_ui):
    def  __init__ (self):
        self.setupUi(self)
        self.__load_server_info()
        self.__connect()
        self.__init_tabel()
        self.__init_child_window()
        self.__child_connect()
        self.__init_thread()
        self.__thread_connect()
        self.__set_init_state()
        self.__init_root()
        self.slaver_list = []
        self.curr_file_list = []
        self.curr_folder_list = []
        self.curr_wait_list = []
        self.curr_exec_list = []
        self.curr_hist_list = []
        self.root = []
        self.recv_err_count = 0 # 接收失败计数
    
    def __init_root(self):
        # 获取服务器的可见目录
        self.send_info({'mode':'get_root','ui': 'main', 'info': ""})

    def __load_server_info(self):
        # 加载服务端信息
        try:
            with open("server_info.json", "r", encoding="utf-8") as f:
                info = json.load(f)
            self.server_info = info
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "错误", "服务端信息获取失败, 原因是：\n"+str(e))
            exit(1)
    
    def __set_init_state(self):
        # 设置按钮等元素初始状态
        self.stop_button.setEnabled(False)
        self.change.setEnabled(False)
        self.delete_2.setEnabled(False)
        self.move.setEnabled(False)
        self.copy.setEnabled(False)
        self.new_folder.setEnabled(False)
        self.new_file.setEnabled(False)
        self.remane.setEnabled(False)
        self.delete_file.setEnabled(False)
        self.upload.setEnabled(False)
    
    def __init_tabel(self):
        # 初始化所有表格和窗口
        self.info_list = QtGui.QStandardItemModel(0, 7)
        self.info_list.setHorizontalHeaderLabels(['节点名', 'CPU使用量', 'CPU被占用', '可用RAM', '网络下行', '网络上行', 'GPU使用量', 'GPU被占用', '可用VRAM'])
        self.info_window.setModel(self.info_list)
        self.info_window.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.info_window.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.info_window.verticalHeader().setDefaultSectionSize(100)
        self.info_window.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.wait_list = QtGui.QStandardItemModel(0, 10)
        self.wait_list.setHorizontalHeaderLabels(['任务ID', '使用环境', '项目路径', '执行命令', '拟使用计算节点', 'GPU需求数', '前驱任务', '是否紧急', '是否复用GPU', '状态'])
        self.wait_table.setModel(self.wait_list)
        self.wait_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.wait_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.wait_table.verticalHeader().setDefaultSectionSize(100)
        self.wait_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.wait_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.wait_table.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.wait_table.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        self.wait_table.horizontalHeader().setSectionResizeMode(7, QtWidgets.QHeaderView.ResizeToContents)
        self.wait_table.horizontalHeader().setSectionResizeMode(8, QtWidgets.QHeaderView.ResizeToContents)
        self.wait_table.horizontalHeader().setSectionResizeMode(9, QtWidgets.QHeaderView.ResizeToContents)

        self.exec_list = QtGui.QStandardItemModel(0, 10)
        self.exec_list.setHorizontalHeaderLabels(['任务ID', '使用环境', '项目路径', '执行命令', '计算节点', '使用GPU数量', '前驱任务', '是否紧急', '是否复用GPU', '状态'])
        self.exec_table.setModel(self.exec_list)
        self.exec_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.exec_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.exec_table.verticalHeader().setDefaultSectionSize(100)
        self.exec_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.exec_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.exec_table.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.exec_table.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        self.exec_table.horizontalHeader().setSectionResizeMode(7, QtWidgets.QHeaderView.ResizeToContents)
        self.exec_table.horizontalHeader().setSectionResizeMode(8, QtWidgets.QHeaderView.ResizeToContents)
        self.exec_table.horizontalHeader().setSectionResizeMode(9, QtWidgets.QHeaderView.ResizeToContents)

        self.history_list = QtGui.QStandardItemModel(0, 10)
        self.history_list.setHorizontalHeaderLabels(['任务ID', '使用环境', '项目路径', '执行命令', '计算节点', '使用GPU数量', '前驱任务', '是否紧急', '是否复用GPU', '状态'])
        self.history_table.setModel(self.history_list)
        self.history_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.history_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.history_table.verticalHeader().setDefaultSectionSize(100)
        self.history_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.history_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(7, QtWidgets.QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(8, QtWidgets.QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(9, QtWidgets.QHeaderView.ResizeToContents)
        
        self.file_tree_model = QtGui.QStandardItemModel()
        self.file_tree.setModel(self.file_tree_model)
        self.file_tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.curr_folder.setText("/")

        self.env_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.curr_log.setOverwriteMode(True)

        self.log_view.setReadOnly(True)

    def __connect(self):
        # 逻辑操作与按钮连接
        # self.server_setting.triggered.connect(self.set_server)
        self.exit.triggered.connect(self.close)
        self.add.triggered.connect(self.add_task)
        self.change.triggered.connect(self.change_task)
        self.delete_2.triggered.connect(self.del_task)
        self.help.triggered.connect(self.readme)
        self.about.triggered.connect(self.show_about)
        self.add_button.clicked.connect(self.add_task)
        self.change_button.clicked.connect(self.change_task)
        self.delete_button.clicked.connect(self.del_task)
        self.stop_button.clicked.connect(self.stop_task)
        self.resub_button.clicked.connect(self.resub_task)
        self.upload.clicked.connect(self.upload_file)
        self.download.clicked.connect(self.download_file)
        self.watch.clicked.connect(self.watch_file)
        self.move.clicked.connect(lambda: self.file_operate("mv"))
        self.copy.clicked.connect(lambda: self.file_operate("cp"))
        self.new_folder.clicked.connect(lambda: self.file_create("mkdir"))
        self.new_file.clicked.connect(lambda: self.file_create("touch"))
        self.remane.clicked.connect(lambda: self.file_create("mv"))
        self.delete_file.clicked.connect(self.remove_file)
        self.tabWidget.currentChanged.connect(self.change_tab)
        self.tabWidget_2.currentChanged.connect(self.change_task_tab)
        self.test_env.clicked.connect(self.test_env_func)
        self.get_python_version.clicked.connect(self.get_python_version_func)
        self.get_pkgs.clicked.connect(self.get_pkgs_func)
        self.test_cuda_pt.clicked.connect(self.test_cuda_pt_func)
        self.test_cuda_tf.clicked.connect(self.test_cuda_tf_func)
        self.file_tree.clicked.connect(self.select_file)
        self.file_tree.doubleClicked.connect(self.open_file)
        self.pushButton.clicked.connect(self.reflush)
        self.exec_table.doubleClicked.connect(lambda: self.show_train_log("exec"))
        self.history_table.doubleClicked.connect(lambda: self.show_train_log("hist"))
        self.term_input.returnPressed.connect(self.send_term_cmd)
        self.shutdown_ssh.triggered.connect(self.shut_ssh)

    def __init_child_window(self):
        # 初始化所有子窗口
        self.loading_window = loading_c()
        self.loading_window.setWindowTitle("请稍后")
        self.loading_window.setModal(True)
        self.task_ctrl_window = task_ctrl_c()
        # self.task_ctrl_window.setModal(True)
        self.read_file_window = read_file_c()
        self.read_file_window.setModal(True)
        self.read_file_window.setWindowTitle("预览文件")
        self.folder_select_window = folder_select_c()
        self.folder_select_window.setModal(True)
        self.filename_ctrl_window = filename_ctrl_c()
        self.filename_ctrl_window.setModal(True)
        self.loading_window.set_text("正在与服务器通信中，请稍后...")
        self.readme_window = readme_c()
    
    def __init_thread(self):
        # 初始化并开启所有子线程
        self.monitor_th = comm_thread(parent=self, port=self.server_info["monitor_port"], addr=self.server_info["IP"], buffer=self.server_info["buffer"])   #节点监控通信线程
        self.data_th = comm_thread(parent=self, port=self.server_info["data_port"], addr=self.server_info["IP"], buffer=self.server_info["buffer"])     #操作通信线程
        self.scp_th = scp_thread(ssh_port=self.server_info["ssh_port"], addr=self.server_info["IP"], psw=self.server_info["psw"], username=self.server_info["username"])    #ssh文件操作线程
        self.task_th = comm_thread(parent=self, port=self.server_info["train_state_port"], addr=self.server_info["IP"], buffer=self.server_info["buffer"])     #任务监控线程
        self.train_log_th = log_thread(ssh_port=self.server_info["ssh_port"], addr=self.server_info["IP"], psw=self.server_info["psw"], username=self.server_info["username"])    #训练日志查看线程
        self.term_th = terminal_thread(ssh_port=self.server_info["ssh_port"], addr=self.server_info["IP"], psw=self.server_info["psw"], username=self.server_info["username"])  #命令行线程
        self.server_log_th = log_thread(ssh_port=self.server_info["ssh_port"], addr=self.server_info["IP"], psw=self.server_info["psw"], username=self.server_info["username"])    #服务器日志查看线程
        
        self.server_log_th.set_mode("tail")

        self.monitor_th.start()
        self.data_th.start()
        self.task_th.start()

    def __thread_connect(self):
        # 对所有子线程的信号进行连接
        self.monitor_th._signal.connect(self.proceed_comm)
        self.data_th._signal.connect(self.proceed_comm)
        self.scp_th._signal.connect(self.proceed_scp)
        self.task_th._signal.connect(self.proceed_comm)
        self.train_log_th._signal.connect(self.curr_log.write)
        self.term_th._signal.connect(self.show_term)
        self.server_log_th._signal.connect(self.log_view.write)
    
    def __child_connect(self):
        # 将所有子窗口的信号进行连接
        self.filename_ctrl_window._signal.connect(self.file_create_signal)
        self.read_file_window._signal.connect(self.save_file)
        self.folder_select_window._signal.connect(self.folder_select_process)
        self.task_ctrl_window._signal.connect(self.task_ctrl_process)

    def close(self):
        exit(0)
    
    def send_info(self, info: str):
        # 向服务端发送信息
        try:
            info = json.dumps(info)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "错误", "发送失败, 原因是打包信息时出现非法字符:\n"+str(e))
            return
        try:
            self.data_th.send(info)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "错误", "发送失败, 原因是"+str(e))

    # def set_server(self):
    #     # 设置服务器参数
    #     pass

    def select_file(self):
        # 选择文件
        curr_name = self.file_tree.currentIndex().data()
        is_file = False
        if curr_name in self.curr_file_list:
            is_file = True
        elif curr_name in self.curr_folder_list:
            is_file = False
        self.curr_file.setText(curr_name)
        if is_file:
            self.watch.setText("预览")
        else:
            self.watch.setText("打开")
        if curr_name == "..":
            # 选中了上级指针
            self.move.setEnabled(False)
            self.copy.setEnabled(False)
            self.remane.setEnabled(False)
            self.delete_file.setEnabled(False)
        else:
            # 选中了其他
            self.move.setEnabled(True)
            self.copy.setEnabled(True)
            self.remane.setEnabled(True)
            self.delete_file.setEnabled(True)
        if self.curr_folder.text() == "/":
            # 位于主目录
            self.move.setEnabled(False)
            self.copy.setEnabled(False)
            self.new_folder.setEnabled(False)
            self.new_file.setEnabled(False)
            self.remane.setEnabled(False)
            self.delete_file.setEnabled(False)
    
    def open_file(self):
        # 打开文件或文件夹
        self.watch_file()

    def add_task(self):
        # 添加任务
        self.task_ctrl_window.setWindowTitle("添加任务")
        self.send_info({'mode':'env_list','ui': 'task', 'info':''})
        self.task_ctrl_window.init(self.slaver_list, self.curr_wait_list+self.curr_exec_list)
        self.task_ctrl_window.show()

    def change_task(self):
        # 修改当前任务
        if self.task_ctrl_window.envs.count() == 0:
            self.send_info({'mode':'env_list','ui': 'task', 'info':''})
        def str_to_bool_int(s:str):
            if s == "是":
                return 1
            elif s == "否":
                return 0
            else:
                return 0

        idx = self.tabWidget_2.currentIndex()
        if idx == 0:
            selected = self.wait_table.selectionModel().selectedRows()
            if len(selected) == 0:
                QtWidgets.QMessageBox.warning(self, "警告", "请选择任务")
                return
            index = QtCore.QPersistentModelIndex(selected[0])
            index = index.row()
            task_info = {   # 任务信息
            "task_id": self.wait_list.item(index, 0).text(),    # 任务id，新建任务时id为空，修改时为该任务的id
            "envs": self.wait_list.item(index, 1).text(),  # 执行任务时的环境
            "path": self.wait_list.item(index, 2).text(),    # 执行任务时进入的文件夹路径
            "exec": self.wait_list.item(index, 3).text(),     # 任务的执行命令
            "need_gpus": self.wait_list.item(index, 5).text(),    # 执行该任务所需的gpu数量
            "slaver": self.wait_list.item(index, 4).text(),    # 指定任务分配在哪个计算节点
            "prev": self.wait_list.item(index, 6).text(),   # 前驱任务，只有前驱任务执行完毕后才会执行当前任务
            "is_urgent": str_to_bool_int(self.wait_list.item(index, 7).text()),  # 该任务是否紧急
            "is_reuse_gpu": str_to_bool_int(self.wait_list.item(index, 8).text())    # 该任务是否复用GPU(即一个gpu上运行多个任务)
        }
        elif idx == 2:
            selected = self.history_table.selectionModel().selectedRows()
            if len(selected) == 0:
                QtWidgets.QMessageBox.warning(self, "警告", "请选择任务")
                return
            index = QtCore.QPersistentModelIndex(selected[0])
            index = index.row()
            task_info = {   # 任务信息
            "task_id": self.history_list.item(index, 0).text(),    # 任务id，新建任务时id为空，修改时为该任务的id
            "envs": self.history_list.item(index, 1).text(),  # 执行任务时的环境
            "path": self.history_list.item(index, 2).text(),    # 执行任务时进入的文件夹路径
            "exec": self.history_list.item(index, 3).text(),     # 任务的执行命令
            "need_gpus": int(self.history_list.item(index, 5).text()),    # 执行该任务所需的gpu数量
            "slaver": self.history_list.item(index, 4).text(),    # 指定任务分配在哪个计算节点
            "prev": self.history_list.item(index, 6).text(),   # 前驱任务，只有前驱任务执行完毕后才会执行当前任务
            "is_urgent": str_to_bool_int(self.history_list.item(index, 7).text()),  # 该任务是否紧急
            "is_reuse_gpu": str_to_bool_int(self.history_list.item(index, 8).text())
            }
        else:
            return
        
        self.task_ctrl_window.setWindowTitle("修改任务: "+task_info["task_id"])
        self.task_ctrl_window.set_info(task_info, self.slaver_list, self.curr_wait_list+self.curr_exec_list, task_info["task_id"])
        self.task_ctrl_window.show()

    def del_task(self):
        # 删除当前任务
        cb = QtWidgets.QCheckBox()
        cb.setText("同时删除该任务的所有后继任务")
        mb = QtWidgets.QMessageBox(self)
        mb.setCheckBox(cb)
        mb.setWindowTitle('警告') 
        mb.setText("确认删除这个任务吗? 该操作不可逆! ") 
        mb.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        idx = self.tabWidget_2.currentIndex()
        if idx == 0:
            selected = self.wait_table.selectionModel().selectedRows()
            if len(selected) == 0:
                QtWidgets.QMessageBox.warning(self, "警告", "请选择任务")
                return
            index = QtCore.QPersistentModelIndex(selected[0])
            index = index.row()
            task_id = self.wait_list.item(index, 0).text()
        elif idx == 2:
            selected = self.history_table.selectionModel().selectedRows()
            if len(selected) == 0:
                QtWidgets.QMessageBox.warning(self, "警告", "请选择任务")
                return
            index = QtCore.QPersistentModelIndex(selected[0])
            index = index.row()
            task_id = self.history_list.item(index, 0).text()
        else:
            return
        reply = mb.exec_()
        if reply == QtWidgets.QMessageBox.No:
            return
        info = {'mode':'del_task','ui': 'main', 'info': task_id}
        self.send_info(info)
        time.sleep(0.1)
        if cb.isChecked():
            def del_tasks(curr_task_id):
                # 递归删除该任务的所有后继任务(包括后继的后继)
                counts = self.wait_list.rowCount()
                for i in range(counts):
                    prev_task_id = self.wait_list.item(i, 6).text()
                    if curr_task_id == prev_task_id:
                        info = {'mode':'del_task','ui': 'main', 'info': self.wait_list.item(i, 0).text()}
                        self.send_info(info)
                        time.sleep(0.1)
                        del_tasks(self.wait_list.item(i, 0).text())
                counts = self.history_list.rowCount()
                for i in range(counts):
                    prev_task_id = self.history_list.item(i, 6).text()
                    if task_id == prev_task_id:
                        info = {'mode':'del_task','ui': 'main', 'info': self.history_list.item(i, 0).text()}
                        self.send_info(info)
                        time.sleep(0.1)
                        del_tasks(self.wait_list.item(i, 0).text())
            del_tasks(task_id)

    def stop_task(self):
        # 中止当前任务
        idx = self.tabWidget_2.currentIndex()
        if idx == 1:
            selected = self.exec_table.selectionModel().selectedRows()
            if len(selected) == 0:
                QtWidgets.QMessageBox.warning(self, "警告", "请选择任务")
                return
            index = QtCore.QPersistentModelIndex(selected[0])
            index = index.row()
            task_id = self.exec_list.item(index, 0).text()
            info = {'mode':'stop_task','ui': 'main','info': task_id}
            self.send_info(info)
        else:
            return

    def resub_task(self):
        # 重新提交当前任务
        idx = self.tabWidget_2.currentIndex()
        if idx == 0:
            selected = self.wait_table.selectionModel().selectedRows()
            if len(selected) == 0:
                QtWidgets.QMessageBox.warning(self, "警告", "请选择任务")
                return
            index = QtCore.QPersistentModelIndex(selected[0])
            index = index.row()
            task_id = self.wait_list.item(index, 0).text()
        elif idx == 1:
            selected = self.wait_table.selectionModel().selectedRows()
            if len(selected) == 0:
                QtWidgets.QMessageBox.warning(self, "警告", "请选择任务")
                return
            index = QtCore.QPersistentModelIndex(selected[0])
            index = index.row()
            task_id = self.exec_list.item(index, 0).text()
        elif idx == 2:
            selected = self.history_table.selectionModel().selectedRows()
            if len(selected) == 0:
                QtWidgets.QMessageBox.warning(self, "警告", "请选择任务")
                return
            index = QtCore.QPersistentModelIndex(selected[0])
            index = index.row()
            task_id = self.history_list.item(index, 0).text()
        else:
            return
        info = {'mode':'resub_task','ui': 'main', 'info': task_id}
        self.send_info(info)

    def shut_ssh(self):
        # 关闭命令行的ssh连接
        self.term_th.set_run(False)
    
    def send_term_cmd(self):
        # 命令行发送消息
        cmd = self.term_input.text()
        self.term_th.put_cmd(cmd)
        self.term_output.appendPlainText("$ "+cmd)
        self.term_input.clear()
    
    def show_term(self, text: str):
        # 将命令行运行结果返回至界面
        self.term_output.appendPlainText(text)

    def readme(self):
        # 帮助文档
        self.readme_window.show()

    def show_train_log(self, mode):
        # 显示训练日志
        self.curr_log.clear()
        self.train_log_th.set_run(False)
        if self.train_log_th.isRunning():
            self.train_log_th.terminate()
        if mode == "exec":
            self.train_log_th.set_mode("tail")
            selected = self.exec_table.selectionModel().selectedRows()
            if len(selected) == 0:
                QtWidgets.QMessageBox.warning(self, "警告", "请选择任务")
                return
            index = QtCore.QPersistentModelIndex(selected[0])
            index = index.row()
            task_id = self.exec_list.item(index, 0).text()
            state = self.exec_list.item(index, 9).text()
            if state == "准备中":
                # 准备状态的任务还没产生日志
                self.curr_log.write("任务处于准备状态, 暂无日志, 请稍后...")
                return
        elif mode == "hist":
            self.train_log_th.set_mode("cat")
            selected = self.history_table.selectionModel().selectedRows()
            if len(selected) == 0:
                QtWidgets.QMessageBox.warning(self, "警告", "请选择任务")
                return
            index = QtCore.QPersistentModelIndex(selected[0])
            index = index.row()
            task_id = self.history_list.item(index, 0).text()
        else:
            return
        info = {'mode':'get_train_log_path','ui': 'main', 'info':task_id}
        self.send_info(info)
        pass

    def show_about(self):
        # 关于文档
        QtWidgets.QMessageBox.about(self, "关于", "分布式深度学习任务管理系统 版本1.0\n作者: 许鹏程\n此软件为开源软件, 欢迎使用和测试。\n若在使用中发现问题, 欢迎提出意见和建议。")

    def upload_file(self):
        # 上传文件
        if self.scp_th.isRunning():
            QtWidgets.QMessageBox.warning(self, "警告", "正在进行文件传输, 请稍后...")
        else:
            file_name, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "上传文件", "", "")
            if file_name != "":
                self.scp_th.set_info("C", file_name, self.curr_folder.text(), False)
                self.scp_th.start()

    def download_file(self):
        # 下载文件
        if self.scp_th.isRunning():
            QtWidgets.QMessageBox.warning(self, "警告", "正在进行文件传输, 请稍后...")
        else:
            if self.curr_file.text() == "":
                QtWidgets.QMessageBox.warning(self, "警告", "请选择要下载的文件")
            elif self.curr_file.text() == "..":
                QtWidgets.QMessageBox.warning(self, "警告", "你不可以下载上级目录指针")
            else:
                folder_name = QtWidgets.QFileDialog.getExistingDirectory(self, "选择下载位置", "")
                if folder_name != "":
                    is_folder = False
                    if self.curr_file.text() in self.curr_file_list:
                        is_folder = False
                    elif self.curr_file.text() in self.curr_folder_list:
                        is_folder = True
                    self.scp_th.set_info("S", folder_name, self.curr_folder.text()+self.curr_file.text(), is_folder)
                    self.scp_th.start()

    def watch_file(self):
        # 预览文件
        curr_name = self.file_tree.currentIndex().data()
        if not self.curr_file.text() == "":
            is_file = True
            if curr_name in self.curr_file_list:
                is_file = True
            elif curr_name in self.curr_folder_list:
                is_file = False
            if is_file:
                # 预览文件
                info = {'mode':'get_file','ui': 'main', 'info':self.curr_folder.text()+self.curr_file.text()}
                self.send_info(info)
            else:
                # 打开文件夹
                info = {'mode':'get_folder','ui': 'main', 'info':self.curr_folder.text()+curr_name}
                self.send_info(info)
    
    def save_file(self, text: str):
        # 保存文件
        try:
            text = str(base64.b64encode(bytes(text, encoding="utf-8")).decode("utf-8"))
            info = {'mode':'save_file','ui': 'main','info':{"path": self.curr_folder.text()+self.curr_file.text(), "content": text}}
            self.send_info(info)
        except:
            QtWidgets.QMessageBox.warning(self, "保存文件", "保存失败, 原因是: 编码错误, 文件中可能存在非法字符")
    
    def reflush(self):
        # 刷新
        if self.curr_folder.text() == "/":
            # 位于主目录
            pass
        else:
            self.file_tree_model.clear()
            info = {'mode':'get_folder','ui': 'main','info':self.curr_folder.text()}
            self.send_info(info)
            
    def file_operate(self, mode: str):
        # 文件操作(移动, 复制)
        if self.scp_th.isRunning():
            # 正在进行文件操作
            QtWidgets.QMessageBox.warning(self, "警告", "正在进行文件操作, 请稍后...")
        else:
            if not self.curr_file.text() == "":
                self.folder_select_window.setWindowTitle("复制到" if mode=="cp" else "移动到")
                self.folder_select_window.get_curr_folder_info(curr_folder=self.curr_folder.text(), folder_list=self.curr_folder_list, wake_ui="main", opera=mode)
                self.folder_select_window.show()
            else:
                QtWidgets.QMessageBox.warning(self, "警告", "请先选择需要"+ ("复制" if mode=="cp" else "移动") +"的文件或文件夹！")
    
    def file_create(self, mode: str):
        # 创建, 重命名文件(文件夹)
        if not self.curr_folder.text() == "":
            self.filename_ctrl_window.set_info(mode, self.curr_folder.text())
            self.filename_ctrl_window.set_filename("")
            if mode == "mkdir":
                # 新建文件夹
                self.filename_ctrl_window.setWindowTitle("新建文件夹")
                self.filename_ctrl_window.set_text("请输入文件夹名称：")
                self.filename_ctrl_window.show()
            elif mode == "touch":
                # 新建文件
                self.filename_ctrl_window.setWindowTitle("新建文件")
                self.filename_ctrl_window.set_text("请输入文件名称：")
                self.filename_ctrl_window.show()
            elif mode == "mv":
                # 重命名
                if not self.curr_file.text() == "":
                    self.filename_ctrl_window.setWindowTitle("重命名")
                    self.filename_ctrl_window.set_text("请输入新名称：")
                    self.filename_ctrl_window.set_filename(self.curr_file.text())
                    self.filename_ctrl_window.show()
                else:
                    QtWidgets.QMessageBox.warning(self, "警告", "请先选择需要重命名的文件！")
        else:
            if mode == "mv":
                QtWidgets.QMessageBox.warning(self, "警告", "请先选择需要重命名的文件！")
            else:
                QtWidgets.QMessageBox.warning(self, "警告", "请先确定文件要创建在哪儿！")
    
    def remove_file(self):
        # 删除文件
        reply = QtWidgets.QMessageBox.warning(self, "删除文件", "确认删除这个文件吗? 该操作不可逆! ", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            info = {'mode':'rm_file','ui': 'main','info':self.curr_folder.text()+self.curr_file.text()}
            self.send_info(info)

    def test_env_func(self):
        # 测试环境
        curr_env = self.env_list.currentIndex().data()
        if not curr_env == None:
            # 选择了某个环境
            info = {'mode':'test_env','ui': 'main','info':curr_env}
            self.send_info(info)
    
    def get_python_version_func(self):
        # 查看python版本
        curr_env = self.env_list.currentIndex().data()
        if not curr_env == None:
            # 选择了某个环境
            info = {'mode':'py_v','ui': 'main','info':curr_env}
            self.send_info(info)
            self.loading_window.show()
    
    def test_cuda_pt_func(self):
        # 查看pytorch的cuda支持情况
        curr_env = self.env_list.currentIndex().data()
        if not curr_env == None:
            # 选择了某个环境
            info = {'mode':'cuda_pt','ui': 'main','info':curr_env}
            self.send_info(info)
            self.loading_window.show()
    
    def test_cuda_tf_func(self):
        # 查看tensorflow的cuda支持情况
        curr_env = self.env_list.currentIndex().data()
        if not curr_env == None:
            # 选择了某个环境
            info = {'mode':'cuda_tf','ui': 'main','info':curr_env}
            self.send_info(info)
            self.loading_window.show()
    
    def get_pkgs_func(self):
        # 查看当前环境下的包
        curr_env = self.env_list.currentIndex().data()
        if not curr_env == None:
            # 选择了某个环境
            info = {'mode':'pkgs','ui': 'main','info':curr_env}
            self.send_info(info)
            self.loading_window.show()
    
    def file_create_signal(self, ret: dict):
        # 对文件名子窗口发送的信号进行操作
        info = {'mode':'file_operate','ui': 'main','info': ret}
        self.send_info(info)
        pass

    def change_tab(self, idx):
        # 点击了主界面的tab
        if idx == 0:
            # 节点监控
            self.change.setEnabled(False)
            self.delete_2.setEnabled(False)
            pass
        elif idx == 1:
            # 训练管理
            self.change.setEnabled(True)
            self.delete_2.setEnabled(True)
            pass
        elif idx == 2:
            # 文件管理
            self.change.setEnabled(False)
            self.delete_2.setEnabled(False)
            self.curr_file.setText("")
            pass
        elif idx == 3:
            # 环境管理
            self.change.setEnabled(False)
            self.delete_2.setEnabled(False)
            self.send_info({'mode':'env_list','ui': 'main', 'info':''})
            pass
        elif idx == 4:
            # 命令行
            self.change.setEnabled(False)
            self.delete_2.setEnabled(False)
            self.term_th.set_run(True)
            if not self.term_th.isRunning():
                self.term_th.start()
            pass
        elif idx == 5:
            # 日志信息
            self.change.setEnabled(False)
            self.delete_2.setEnabled(False)
            if not self.server_log_th.isRunning():
                self.send_info({'mode':'get_server_log','ui': 'main', 'info':''})

    def change_task_tab(self, idx):
        # 点击了任务管理界面的tab
        if idx == 0:
            # 等待区
            self.stop_button.setEnabled(False)
            self.delete_button.setEnabled(True)
            self.delete_2.setEnabled(True)
            self.change_button.setEnabled(True)
            self.change.setEnabled(True)
            self.resub_button.setEnabled(True)
        elif idx == 1:
            # 执行区
            self.stop_button.setEnabled(True)
            self.delete_button.setEnabled(False)
            self.delete_2.setEnabled(False)
            self.change_button.setEnabled(False)
            self.change.setEnabled(False)
            self.resub_button.setEnabled(False)
        elif idx == 2:
            # 历史任务
            self.stop_button.setEnabled(False)
            self.delete_button.setEnabled(True)
            self.delete_2.setEnabled(True)
            self.change_button.setEnabled(True)
            self.change.setEnabled(True)
            self.resub_button.setEnabled(True)

    def closeEvent(self, event):
        # 退出软件
        # 关闭所有窗口
        self.loading_window.close()
        self.task_ctrl_window.close()
        self.read_file_window.close()
        self.folder_select_window.close()
        self.filename_ctrl_window.close()
        self.readme_window.close()
        # 向服务端发送断开连接消息
        self.data_th.send("CLIEND_CLOSE")
        self.monitor_th.send("CLIEND_CLOSE")
        self.task_th.send("CLIEND_CLOSE")
        # 终止所有子线程
        if self.data_th.isRunning():
            self.data_th.terminate()
        if self.monitor_th.isRunning():
            self.monitor_th.terminate()
        if self.scp_th.isRunning():
            self.scp_th.terminate()
        if self.task_th.isRunning():
            self.task_th.terminate()
        if self.train_log_th.isRunning():
            self.train_log_th.terminate()
        if self.server_log_th.isRunning():
            self.server_log_th.terminate()
    
    def proceed_scp(self, text:str):
        # 处理文件操作(上传, 下载, 移动到, 复制到)的结果
        self.curr_opera.setText(text)
        if "完成" in text or "错误" in text:
            self.reflush()
    
    def folder_select_process(self, info):
        # 对选择文件夹界面的信号进行处理
        func = info["func"] # 操作
        wake = info["wake"] # 该子窗口由哪个窗口调用
        msg = info["info"]  # 操作内容
        if func == "open_folder":
            self.send_info(msg)
        elif func == "ok":
            if wake == "main":
                # 由主窗口调用
                self.scp_th.set_info(msg["opera"], self.curr_folder.text()+self.curr_file.text(), msg["target"], False)
                self.scp_th.start()
            elif wake == "task":
                # 由任务添加, 修改窗口调用
                self.task_ctrl_window.folder_name.setText(msg["target"])
        else:
            pass
    
    def task_ctrl_process(self, info):
        # 对任务创建, 修改界面信号进行处理
        func = info["func"] # 操作
        msg = info["info"]  # 操作内容
        if func == "open_folder":
            self.folder_select_window.setWindowTitle("选择项目路径")
            if self.task_ctrl_window.folder_name.text() == "/":
                self.folder_select_window.set_wake_ui("task")
                self.folder_select_window.get_curr_folder_info("/", folder_list=self.root, wake_ui="task")
                self.folder_select_window.show()
            else:
                self.folder_select_window.set_wake_ui("task")
                self.send_info({'mode':'get_folder','ui': 'folder_select', 'info':self.task_ctrl_window.folder_name.text()})
                self.folder_select_window.show()
        elif func == "ok":
            if msg["task_id"] == "":
                self.send_info({'mode':'add_task','ui': 'task_ctrl', 'info': msg})
            else:
                self.send_info({'mode':'change_task','ui': 'task_ctrl', 'info': msg})
        pass

    def proceed_comm(self, info):
        # 对服务端发送的数据进行处理并显示
        def bool_int_to_str(i: int):
            if i == 0:
                return "否"
            elif i == 1:
                return "是"
            else:
                return "否"
        try:
            self.recv_err_count = 0 # 重置接收失败计数
            mode = info["mode"]
            msg = info["info"]
            ui = info["ui"]
            if mode == "mon":
                # 将节点信息展示在主窗口
                name = msg["name"]
                online = msg["online"]
                if name not in self.slaver_list:
                    self.slaver_list.append(name)
                idx = self.slaver_list.index(name)
                self.info_list.setItem(idx, 0, QtGui.QStandardItem(name))
                self.info_list.setItem(idx, 1, QtGui.QStandardItem(msg["cpu_usage"]))
                self.info_list.setItem(idx, 2, QtGui.QStandardItem(bool_int_to_str(msg["cpu_used"])))
                self.info_list.setItem(idx, 3, QtGui.QStandardItem(msg["avail_ram"]))
                self.info_list.setItem(idx, 4, QtGui.QStandardItem(msg["web_down"]))
                self.info_list.setItem(idx, 5, QtGui.QStandardItem(msg["web_up"]))
                gpu_used = ""
                avail_vram = ""
                for g in msg["gpus"]:
                    gpu_used += g["gpu_used"]
                    gpu_used += "  "
                    avail_vram += g["avail_vram"]
                    avail_vram += "  "
                self.info_list.setItem(idx, 6, QtGui.QStandardItem(gpu_used))
                if len(msg["gpu_used"]) == 0:
                    self.info_list.setItem(idx, 7, QtGui.QStandardItem("No data"))
                else:
                    gpu_state = ""
                    for u in msg["gpu_used"]:
                        gpu_state += bool_int_to_str(u)
                        gpu_state += "  "
                    self.info_list.setItem(idx, 7, QtGui.QStandardItem(gpu_state))

                self.info_list.setItem(idx, 8, QtGui.QStandardItem(avail_vram))
                need_delete = []
                for i in range(self.info_list.rowCount()):
                    n = self.info_list.item(i, 0).text()
                    if n not in online:
                        self.slaver_list.remove(n)
                        need_delete.append(i)
                for idx in need_delete:
                    self.info_list.removeRow(idx)
            elif mode == "ret_env_list":
                # 返回环境信息
                if ui == "main":
                    # 将环境信息显示在主窗口
                    env_info = QtCore.QStringListModel()
                    env_info.setStringList(msg)
                    self.env_list.setModel(env_info)
                elif ui == "task":
                    # 将环境信息显示在任务创建, 修改窗口
                    self.task_ctrl_window.envs.clear()
                    self.task_ctrl_window.envs.addItems(msg)
                else:
                    pass
            elif mode == "ret_test_env":
                # 返回环境测试结果
                if msg == "True":
                    QtWidgets.QMessageBox.information(self, "环境测试成功", "环境测试成功")
                else:
                    QtWidgets.QMessageBox.information(self, "环境测试失败", msg)
                self.loading_window.close()
            elif mode == "ret_py_v":
                # 返回该环境的python版本
                if msg["res"] == "seccess":
                    QtWidgets.QMessageBox.information(self, "Python版本", msg["msg"])
                elif msg["res"] == "falied":
                    QtWidgets.QMessageBox.information(self, "Python版本获取失败", msg["msg"])
                self.loading_window.close()
            elif mode == "ret_cuda_pt":
                # 返回该环境使用pytorch时的cuda可用情况
                if msg["res"] == "seccess":
                    QtWidgets.QMessageBox.information(self, "Cuda结果(PyTorch)", msg["msg"])
                elif msg["res"] == "falied":
                    QtWidgets.QMessageBox.information(self, "错误", msg["msg"])
                self.loading_window.close()
            elif mode == "ret_cuda_tf":
                # 返回该环境使用tensorflow时的cuda可用情况
                if msg["res"] == "seccess":
                    QtWidgets.QMessageBox.information(self, "Cuda结果(PyTorch)", msg["msg"])
                elif msg["res"] == "falied":
                    QtWidgets.QMessageBox.information(self, "错误", msg["msg"])
                self.loading_window.close()
            elif mode == "ret_pkgs":
                # 返回该环境的包
                if msg["res"] == "seccess":
                    self.pkg_list.setText(msg["msg"])
                elif msg["res"] == "falied":
                    QtWidgets.QMessageBox.information(self, "错误", msg["msg"])
                self.loading_window.close()
            elif mode == "ret_folder":
                # 返回当前目录下的所有文件和文件夹
                if ui == "main":
                    # 返回到主界面
                    self.curr_folder.setText(msg["curr_path"]+"/")
                    self.file_tree_model.clear()
                    self.curr_file_list = msg["file"]
                    self.curr_folder_list = msg["folder"]
                    self.curr_file.setText("")
                    if msg["curr_path"] == "":
                        self.curr_file_list = []
                        self.curr_folder_list = self.root
                        for f in self.root:
                            self.file_tree_model.appendRow(QtGui.QStandardItem(QApplication.style().standardIcon(21), f))
                        self.move.setEnabled(False)
                        self.copy.setEnabled(False)
                        self.new_folder.setEnabled(False)
                        self.new_file.setEnabled(False)
                        self.remane.setEnabled(False)
                        self.delete_file.setEnabled(False)
                        self.upload.setEnabled(False)
                    else:
                        self.curr_folder_list.insert(0, "..")
                        for folder in msg["folder"]:
                            self.file_tree_model.appendRow(QtGui.QStandardItem(QApplication.style().standardIcon(21), folder))
                        for file in msg["file"]:
                            self.file_tree_model.appendRow(QtGui.QStandardItem(QApplication.style().standardIcon(25), file))
                        self.move.setEnabled(True)
                        self.copy.setEnabled(True)
                        self.new_folder.setEnabled(True)
                        self.new_file.setEnabled(True)
                        self.remane.setEnabled(True)
                        self.delete_file.setEnabled(True)
                        self.upload.setEnabled(True)
                elif ui == "folder_select":
                    # 返回到选择文件夹界面
                    if msg["curr_path"] == "":
                        self.folder_select_window.get_curr_folder_info(msg["curr_path"]+"/", self.root, None)
                        self.folder_select_window.ok.setEnabled(False)
                    else:
                        folder_list = msg["folder"]
                        folder_list.insert(0, "..")
                        self.folder_select_window.get_curr_folder_info(msg["curr_path"]+"/", folder_list, None)
                        self.folder_select_window.ok.setEnabled(True)
                else:
                    pass
            elif mode == "ret_file":
                # 返回文件内容
                state = msg["state"]
                if state == "success":
                    try:
                        content = str(base64.b64decode(bytes(str(msg["content"]).encode("utf-8"))).decode("utf-8")) 
                        self.read_file_window.textEdit.setText(content)
                        self.read_file_window.setWindowTitle("正在预览 "+msg["file_name"][1:])
                        self.read_file_window.show()
                    except:
                        QtWidgets.QMessageBox.information(self, "文件打开失败", "解码失败")
                else:
                    QtWidgets.QMessageBox.information(self, "文件打开失败", "该文件无法打开, 原因可能是其不是文本文件或包含非法字符")
            elif mode == "ret_save_file":
                # 返回文件保存结果
                if msg == "success":
                    QtWidgets.QMessageBox.information(self, "保存文件", "保存成功! ")
                else:
                    QtWidgets.QMessageBox.information(self, "保存文件", "保存失败, 原因是: \n"+msg)
                self.reflush()
            elif mode == "ret_file_operate":
                # 返回文件操作(新建, 重命名)结果
                if msg == "success":
                    self.reflush()
                else:
                    QtWidgets.QMessageBox.information(self, "文件操作失败", msg)
            elif mode == "ret_rm_file":
                # 返回文件删除结果
                if msg == "success":
                    pass
                else:
                    QtWidgets.QMessageBox.information(self, "删除文件", "删除失败, 原因是: \n"+msg)
                self.reflush()
            elif mode == "ret_add_task":
                # 返回添加任务结果
                if msg:
                    QtWidgets.QMessageBox.information(self, "添加任务", "添加失败, 原因是: \n"+msg)
                else:
                    QtWidgets.QMessageBox.information(self, "添加任务", "添加成功")
            elif mode == "task_mon":
                # 任务监控
                state_info = {"wait": "等待中", "exec": "运行中", "pexec": "准备中", "accp": "完成", "err": "错误", "offline_error": "错误, 节点掉线", "term": "中止"}
                wait_task = msg["wait"]
                wait_task_ids = []
                for item in wait_task:
                    wait_task_ids.append(item["task_id"])
                exec_task = msg["exec"]
                exec_task_ids = []
                for item in exec_task:
                    exec_task_ids.append(item["task_id"])
                hist_task = msg["hist"]
                hist_task_ids = []
                for item in hist_task:
                    hist_task_ids.append(item["task_id"])
                for item in wait_task:
                    task_id = item["task_id"]
                    if task_id not in self.curr_wait_list:
                        self.curr_wait_list.append(task_id)
                    idx = self.curr_wait_list.index(task_id)
                    self.wait_list.setItem(idx, 0, QtGui.QStandardItem(task_id))    # 任务ID
                    self.wait_list.setItem(idx, 1, QtGui.QStandardItem(item["envs"]))   # 使用环境
                    self.wait_list.setItem(idx, 2, QtGui.QStandardItem(item["path"]))   # 项目路径
                    self.wait_list.setItem(idx, 3, QtGui.QStandardItem(item["exec"]))   # 执行命令
                    self.wait_list.setItem(idx, 4, QtGui.QStandardItem(item["slaver"])) # 拟使用计算节点
                    self.wait_list.setItem(idx, 5, QtGui.QStandardItem(item["need_gpus"])) # GPU需求数
                    self.wait_list.setItem(idx, 6, QtGui.QStandardItem(item["prev"]))   # 前驱任务
                    self.wait_list.setItem(idx, 7, QtGui.QStandardItem(bool_int_to_str(item["is_urgent"]))) # 是否紧急
                    self.wait_list.setItem(idx, 8, QtGui.QStandardItem(bool_int_to_str(item["is_reuse_gpu"]))) # 是否复用GPU'
                    self.wait_list.setItem(idx, 9, QtGui.QStandardItem(state_info[item["state"]]))
                need_delete = []
                for i in range(self.wait_list.rowCount()):
                    n = self.wait_list.item(i, 0).text()
                    if n not in wait_task_ids:
                        self.curr_wait_list.remove(n)
                        need_delete.append(i)
                need_delete.sort(reverse=True)
                for idx in need_delete:
                    self.wait_list.removeRow(idx)
                
                for item in exec_task:
                    task_id = item["task_id"]
                    if task_id not in self.curr_exec_list:
                        self.curr_exec_list.append(task_id)
                    idx = self.curr_exec_list.index(task_id)
                    self.exec_list.setItem(idx, 0, QtGui.QStandardItem(task_id))    # 任务ID
                    self.exec_list.setItem(idx, 1, QtGui.QStandardItem(item["envs"]))   # 使用环境
                    self.exec_list.setItem(idx, 2, QtGui.QStandardItem(item["path"]))   # 项目路径
                    self.exec_list.setItem(idx, 3, QtGui.QStandardItem(item["exec"]))   # 执行命令
                    self.exec_list.setItem(idx, 4, QtGui.QStandardItem(item["slaver"])) # 拟使用计算节点
                    self.exec_list.setItem(idx, 5, QtGui.QStandardItem(item["need_gpus"])) # GPU需求数
                    self.exec_list.setItem(idx, 6, QtGui.QStandardItem(item["prev"]))   # 前驱任务
                    self.exec_list.setItem(idx, 7, QtGui.QStandardItem(bool_int_to_str(item["is_urgent"]))) # 是否紧急
                    self.exec_list.setItem(idx, 8, QtGui.QStandardItem(bool_int_to_str(item["is_reuse_gpu"]))) # 是否复用GPU'
                    self.exec_list.setItem(idx, 9, QtGui.QStandardItem(state_info[item["state"]]))
                need_delete = []
                for i in range(self.exec_list.rowCount()):
                    n = self.exec_list.item(i, 0).text()
                    if n not in exec_task_ids:
                        self.curr_exec_list.remove(n)
                        need_delete.append(i)
                need_delete.sort(reverse=True)
                for idx in need_delete:
                    self.exec_list.removeRow(idx)
                
                for item in hist_task:
                    task_id = item["task_id"]
                    if task_id not in self.curr_hist_list:
                        self.curr_hist_list.append(task_id)
                    idx = self.curr_hist_list.index(task_id)
                    self.history_list.setItem(idx, 0, QtGui.QStandardItem(task_id))    # 任务ID
                    self.history_list.setItem(idx, 1, QtGui.QStandardItem(item["envs"]))   # 使用环境
                    self.history_list.setItem(idx, 2, QtGui.QStandardItem(item["path"]))   # 项目路径
                    self.history_list.setItem(idx, 3, QtGui.QStandardItem(item["exec"]))   # 执行命令
                    self.history_list.setItem(idx, 4, QtGui.QStandardItem(item["slaver"])) # 拟使用计算节点
                    self.history_list.setItem(idx, 5, QtGui.QStandardItem(item["need_gpus"])) # GPU需求数
                    self.history_list.setItem(idx, 6, QtGui.QStandardItem(item["prev"]))   # 前驱任务
                    self.history_list.setItem(idx, 7, QtGui.QStandardItem(bool_int_to_str(item["is_urgent"]))) # 是否紧急
                    self.history_list.setItem(idx, 8, QtGui.QStandardItem(bool_int_to_str(item["is_reuse_gpu"]))) # 是否复用GPU'
                    self.history_list.setItem(idx, 9, QtGui.QStandardItem(state_info[item["state"]]))
                need_delete = []
                for i in range(self.history_list.rowCount()):
                    n = self.history_list.item(i, 0).text()
                    if n not in hist_task_ids:
                        self.curr_hist_list.remove(n)
                        need_delete.append(i)
                need_delete.sort(reverse=True)
                for idx in need_delete:
                    self.history_list.removeRow(idx)
            elif mode == "ret_change_task":
                if msg == "":
                    QtWidgets.QMessageBox.information(self, "修改任务", "修改成功")
                else:
                    QtWidgets.QMessageBox.information(self, "修改任务", msg)
            elif mode == "ret_del_task":
                task_id = msg["task_id"]
                ret = msg["info"]
                if ret == "":
                    QtWidgets.QMessageBox.information(self, "删除任务 "+task_id, "任务"+ task_id+"删除成功")
                else:
                    QtWidgets.QMessageBox.information(self, "删除任务"+task_id, msg)
            elif mode == "ret_resub_task":
                task_id = msg["task_id"]
                ret = msg["info"]
                if ret == "":
                    QtWidgets.QMessageBox.information(self, "重新提交任务 ", "重新提交任务成功, 新任务ID为"+ task_id)
                else:
                    QtWidgets.QMessageBox.information(self, "重新提交任务", msg)
            elif mode == "ret_root":
                # 返回服务器可见目录
                self.root = copy.deepcopy(msg)
                self.curr_folder_list = copy.deepcopy(msg)
                for f in self.root:
                    self.file_tree_model.appendRow(QtGui.QStandardItem(QApplication.style().standardIcon(21), f))
            elif mode == "ret_stop_task":
                # 返回停止结果
                task_id = msg["task_id"]
                if msg["info"] == "success":
                    QtWidgets.QMessageBox.information(self, "停止任务 ", "任务"+ task_id+ "停止成功")
                elif msg["info"] == "failed":
                    QtWidgets.QMessageBox.information(self, "停止任务 ", "任务"+ task_id+ "停止失败, 原因是该任务已不在执行区中")
            elif mode == "ret_train_log_path":
                # 返回日志路径
                self.train_log_th.set_log_path(msg)
                self.train_log_th.set_run(True)
                self.train_log_th.start()
            elif mode == "ret_server_log":
                # 返回服务端日志路径
                self.server_log_th.set_log_path(msg)
                self.server_log_th.set_run(True)
                if not self.server_log_th.isRunning():
                    self.server_log_th.start()
            
            elif mode == "recv_err":
                # 服务端消息接收失败
                self.loading_window.close()
                QtWidgets.QMessageBox.information(self, "消息接收失败", "消息接收失败, 请再试一次")

            elif mode == "conn_err":
                # 服务端连接失败
                self.loading_window.close()
                QtWidgets.QMessageBox.information(self, "服务器连接失败", msg)
                self.data_th.terminate()
                self.monitor_th.terminate()
        except Exception as e:
            self.recv_err_count += 1
            if self.recv_err_count == 3:
                QtWidgets.QMessageBox.information(self, "消息接收失败", "消息接收失败")
                self.recv_err_count = 0

