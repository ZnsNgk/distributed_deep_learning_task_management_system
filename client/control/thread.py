from PyQt5 import QtCore, QtWidgets
import time
from socket import *
import json
import paramiko
from scp import SCPClient
import os
from queue import Queue

class comm_thread(QtCore.QThread):
    # 基于socket的通信线程
    _signal = QtCore.pyqtSignal(dict)
    def __init__(self, data=None, parent=None, port=None, addr=None, buffer=None):
        super(comm_thread, self).__init__(parent)
        self.address = addr   #服务器的ip地址
        self.port=port
        self.buffsize=buffer
        self.s=socket(AF_INET, SOCK_STREAM)
        self.p = parent
        self.max_recv_err = 1
        try:
            self.s.connect((self.address, self.port))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self.p, "服务器连接失败", str(e))
            exit(1)
    
    def send(self, text:str):
        # 向服务端发送消息
        text += "_<END_SEND>_"
        try:
            self.s.send(text.encode(encoding="utf-8"))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self.p, "消息发送失败", str(e))

    def run(self):
        # 监听服务器
        err_data = ""
        err_flag = False
        err_count = 0
        while True:
            try:
                flag = True
                recvdata = ""
                while flag:
                    recv = self.s.recv(self.buffsize).decode('utf-8')
                    recvdata += recv
                    if recvdata[-12:] == "_<END_SEND>_":
                        flag = False
                recvdata = recvdata.replace("_<END_SEND>_", "")
            except Exception as e:
                self._signal.emit({"mode": "conn_err", "info": str(e)})
                time.sleep(5)
            try:
                if err_flag:
                    err_data += recvdata
                    json_info = json.loads(err_data)
                    err_count = 0
                    err_flag = False
                    err_data = ""
                else:
                    json_info = json.loads(recvdata)
                self._signal.emit(json_info)
            except Exception as e:
                err_count += 1
                err_flag = True
                err_data += recvdata
                if err_count > self.max_recv_err:
                    self._signal.emit({"mode": "recv_err", "info": ""})
                    err_flag = False
                    err_data = ""
                    err_count = 0
                # self._signal.emit({"mode": "recv_err", "info": str(e)})


class scp_thread(QtCore.QThread):
    # 基于ssh的文件操作线程
    _signal = QtCore.pyqtSignal(str)
    def __init__(self, data=None, parent=None, ssh_port=None, addr=None, psw=None, username=None):
        super(scp_thread, self).__init__(parent)
        self.address = addr   #服务器的ip地址
        self.ssh_port = ssh_port    #ssh端口
        self.psw = psw  #密码
        self.user_name = username
    
    def set_info(self, mode, local_path, server_path, is_dir):
        self.mode = mode    #S(下载 服务器->本地)    C(上传 本地->服务器)    mv(剪贴 服务器->服务器)    cp(复制 服务器->服务器)
        self.local_path = local_path
        self.server_path = server_path
        self.is_dir = is_dir
    
    def run(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=self.address, port=self.ssh_port, username=self.user_name, password=self.psw, timeout=30)
            if self.mode == "S":
                # 下载文件
                sftp = SCPClient(ssh.get_transport(), socket_timeout=15.0)
                self._signal.emit("正在将 "+self.server_path+" 下载到 "+self.local_path+"/")
                sftp.get("."+self.server_path, self.local_path+"/", recursive=self.is_dir)
            elif self.mode == "C":
                # 上传文件
                sftp = SCPClient(ssh.get_transport(), socket_timeout=15.0)
                for path in self.local_path:
                    self._signal.emit("正在将 "+path+" 上传到 "+self.server_path)
                    sftp.put(path, "."+self.server_path)
            elif self.mode == "mv" or self.mode == "cp":
                # 移动到, 复制到
                if self.mode == "cp":
                    self.mode = "cp -r"
                cmd = self.mode + " ."+self.local_path + " ."+self.server_path
                self._signal.emit("正在将 "+self.local_path+(" 移动" if self.mode=="mv" else " 复制")+ "到 "+self.server_path)
                stdin, stdout, stderr = ssh.exec_command(cmd)
                err = stderr.read().decode("utf-8")
                self._signal.emit("错误: "+str(err).replace("\n", " "))
                ssh.close()
                if not err == "":
                    return
            else:
                ssh.close()
                return
            self._signal.emit("完成! ")
            ssh.close()
        except Exception as e:
            self._signal.emit("错误: "+str(e).replace("\n", " "))
            ssh.close()

class log_thread(QtCore.QThread):
    # 基于ssh的日志查看线程
    _signal = QtCore.pyqtSignal(str)
    def __init__(self, data=None, parent=None, ssh_port=None, addr=None, psw=None, username=None):
        super(log_thread, self).__init__(parent)
        self.address = addr   #服务器的ip地址
        self.ssh_port = ssh_port    #ssh端口
        self.psw = psw  #密码
        self.user_name = username
        self.start_to_run = False
        self.log_path = ""
        self.mode = "tail"
    
    def set_log_path(self, path: str):
        self.log_path = path
    
    def set_mode(self, mode: str):
        self.mode = mode
    
    def run(self):
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=self.address, port=self.ssh_port, username=self.user_name, password=self.psw, timeout=30)
                ssh.connect(self.address, username=self.user_name, port=self.ssh_port, timeout=30, password=self.psw)
                chan = ssh.get_transport().open_session()
                if self.mode == "tail":
                    cmd = "tail -n 100 -f "+self.log_path
                elif self.mode == "cat":
                    cmd = "cat "+self.log_path
                chan.exec_command(cmd)
                while self.start_to_run:
                    if chan.recv_ready():
                            recv = chan.recv(4096).decode(encoding="utf-8",errors="ignore")
                            self._signal.emit(recv)
                    if chan.recv_stderr_ready():
                            recv = chan.recv_stderr(4096).decode(encoding="utf-8",errors="ignore")
                            self._signal.emit(recv)
                    time.sleep(0.01)
            except Exception as e:
                self._signal.emit("日志查看失败, 原因是: "+str(e))
                ssh.close()
            ssh.close()
    
    def set_run(self, mode: bool):
        self.start_to_run = mode

class terminal_thread(QtCore.QThread):
    # 基于ssh的命令行交互线程
    _signal = QtCore.pyqtSignal(str)
    def __init__(self, data=None, parent=None, ssh_port=None, addr=None, psw=None, username=None):
        super(terminal_thread, self).__init__(parent)
        self.address = addr   #服务器的ip地址
        self.ssh_port = ssh_port    #ssh端口
        self.psw = psw  #密码
        self.user_name = username
        self.cmd_list = Queue(0)
        self.can_run = True
    
    def put_cmd(self, cmd):
        self.cmd_list.put(cmd)
    
    def set_run(self, mode: bool):
        self.can_run = mode
    
    def run(self):
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=self.address, port=self.ssh_port, username=self.user_name, password=self.psw, timeout=30)
                chan = ssh.get_transport().open_session()
                chan.invoke_shell()
                chan.send("source ~/envs/miniconda3/bin/activate\n")
                while self.can_run:
                    if not self.cmd_list.empty():
                        cmd = self.cmd_list.get()
                        chan.send(cmd+"\n")
                    if chan.recv_ready():
                        recv = chan.recv(4096).decode(encoding="utf-8",errors="ignore")
                        self._signal.emit(recv)
                    if chan.recv_stderr_ready():
                        recv = chan.recv_stderr(4096).decode(encoding="utf-8",errors="ignore")
                        self._signal.emit(recv)
                    time.sleep(0.01)
            except Exception as e:
                self._signal.emit("连接错误, 原因是 " + str(e) + ", 即将退出")
                ssh.close()
            ssh.close()
            self._signal.emit("退出连接")