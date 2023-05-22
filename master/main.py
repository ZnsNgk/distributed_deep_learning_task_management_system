from monitor import Monitor
from communicate import Communicate
from global_var import visible_folder
from config import config
from task_ctrl import Task_Control
import threading
import time
from queue import Queue
from logger import log

class Main:
    def __init__(self) -> None:
        self.config = config("conf.json")
        ret = self.config.get_info()
        if ret:
            raise ret
        self.slaver_state_queue = Queue(len(self.config.slaver_info)*5) # 节点信息队列，由节点监控线程放入数据，任务管理线程读取
        self.online_slaver = [] #在线计算节点列表
        self.slaver_state = [] # 当前计算节点状态
        global visible_folder
        visible_folder.extend(self.config.visible_folders)
        self.monitor = Monitor(self.config, self.slaver_state_queue, self.online_slaver, self.slaver_state)
        self.offline_queue = Queue(0)
        self.monitor_comm = Communicate(self.config.socket_info["monitor_port"], self.config.socket_info["buffer"], self.config.socket_info["listen"], "sendonly", self.config.config["server_log_path"], self.offline_queue)
        self.communicate = Communicate(self.config.socket_info["data_port"], self.config.socket_info["buffer"], self.config.socket_info["listen"], "act", self.config.config["server_log_path"], self.offline_queue)
        self.task_ctrl = Task_Control(self.config, self.slaver_state_queue, self.online_slaver, self.slaver_state)
        self.task_comm = Communicate(self.config.socket_info["train_state_port"], self.config.socket_info["buffer"], self.config.socket_info["listen"], "sendonly", self.config.config["server_log_path"], self.offline_queue)
    
    def run(self):
        try:
            t1 = threading.Thread(target=self.monitor.run, args=(self.monitor_comm,))
            t2 = threading.Thread(target=self.monitor_comm.recs)
            
            t3 = threading.Thread(target=self.communicate.recs)
            
            t4 = threading.Thread(target=self.task_ctrl.run, args=(self.task_comm,))
            t5 = threading.Thread(target=self.task_comm.recs)
            
            t1.start()
            t2.start()
            t3.start()
            t4.start()
            t5.start()
            log("服务端已上线", self.config.config["server_log_path"])
            while True:
                time.sleep(10)

        except KeyboardInterrupt:
            log("服务端下线", self.config.config["server_log_path"])

if __name__ == "__main__":
    app = Main()
    app.run()