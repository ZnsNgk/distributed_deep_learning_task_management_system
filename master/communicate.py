import socket
import threading
from process import process
import time
from logger import log
import queue

class Communicate:
    def __init__(self, port, buffer, listen, mode, log_path, offline_queue: queue.Queue) -> None:
        # mode = sendonly(仅发送数据), act(交互)
        self.address = '0.0.0.0'
        self.log_path = log_path
        self.port = port
        self.buffsize = buffer
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 16777216)
        self.s.bind((self.address, self.port))
        self.s.setblocking(True)
        self.s.settimeout(10)
        self.s.listen(listen)     #最大连接数
        self.lock = threading.Lock()
        self.conn_list = []
        self.conn_dt = {}
        self.is_act = True if mode=="act" else False
        self.offline_queue = offline_queue


    def tcplink(self, sock, addr):
        while True:
            try:
                flag = True
                recvdata = ""
                while flag:
                    recv = sock.recv(self.buffsize).decode('utf-8')
                    recvdata += recv
                    if recvdata[-12:] == "_<END_SEND>_":
                        flag = False
                recvdata = recvdata.replace("_<END_SEND>_", "")
                # print(recvdata, addr)
                if recvdata == "CLIEND_CLOSE":
                    sock.close()
                    if self.is_act:
                        log(str(addr[0])+" 已下线", self.log_path)
                    _index = self.conn_list.index(addr)
                    self.conn_dt.pop(addr)
                    self.conn_list.pop(_index)
                    break
                else:
                    if self.is_act:
                        try:
                            send_info, need_send = process(recvdata)
                            if need_send:
                                send_info += "_<END_SEND>_"
                                # print(send_info)
                                self.send(send_info, sock)
                        except Exception as e:
                            print(str(e))
                if not recvdata:
                    break
            except Exception as e:
                try:
                    self.conn_dt[sock].close()
                except:
                    pass
                if self.is_act:
                    log(str(addr[0])+" 连接丢失", self.log_path)
                    for _ in range(10): #防止出问题, 放10次
                        self.offline_queue.put(addr[0])
                _index = self.conn_list.index(addr)
                self.conn_dt.pop(addr)
                self.conn_list.pop(_index)
                print(e)
                break
    
    def send(self, send_text: str, sock):
        try:
            self.lock.acquire()
            sock.send(send_text.encode())
            self.lock.release()
        except Exception as e:
            self.lock.release()
            print(e)
    
    def send_all(self, send_text: str):
        if not self.offline_queue.empty():
            # 发现有掉线IP
                offline_ip = self.offline_queue.get()
                for sock, addr in zip(self.conn_dt.keys(), self.conn_list):
                    if offline_ip == addr[0]:
                        print(addr,'offline')
                        try:
                            self.conn_dt[sock].setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 0)
                            self.conn_dt[sock].setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 16777216)
                            self.conn_dt[sock].close()
                        except Exception as e:
                            print(e)
                        try:
                            _index = self.conn_list.index(addr)
                            self.conn_dt.pop(addr)
                            self.conn_list.pop(_index)
                        except:
                            pass
                        break

        for sock, addr in zip(self.conn_dt.keys(), self.conn_list):
            try:
                # print(addr, send_text)
                send_text += "_<END_SEND>_"
                ret = self.conn_dt[sock].sendall(send_text.encode())
            except Exception as e:
                print(e)
                try:
                    self.conn_dt[sock].close()
                except:
                    pass
                log(str(addr[0])+" 连接丢失", self.log_path)
                print(addr,'offline')
                try:
                    _index = self.conn_list.index(addr)
                    self.conn_dt.pop(addr)
                    self.conn_list.pop(_index)
                except:
                    pass
                break
    
    def recs(self):
        while True:
            try:
                clientsock, clientaddress = self.s.accept()
                clientsock.getsockname()
                print(clientaddress)
                if clientaddress not in self.conn_list:
                    self.conn_list.append(clientaddress)
                    clientsock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    clientsock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 5)
                    clientsock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 2)
                    clientsock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
                    self.conn_dt[clientaddress] = clientsock
                    
                print('connect from:', clientaddress)
                if self.is_act:
                    log(str(clientaddress[0])+" 已上线", self.log_path)
                #在这里创建线程，就可以每次都将socket进行保持
                t=threading.Thread(target=self.tcplink,args=(clientsock,clientaddress))
                t.start()
            except Exception as e:
                pass

if __name__ == '__main__':
    comm = Communicate()
    t1 = threading.Thread(target=comm.recs, args=(), name='rec')
    t1.start()