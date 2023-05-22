import paramiko
import time
import json
import traceback
from datetime import datetime
import threading
import sys
from math import log
from queue import Queue
from config import config
from logger import log as write_log    

class Monitor:
    def __init__(self, config: config, slaver_queue: Queue, online_slaver: list, slaver_state) -> None:
        self.py_cmd = "source ~/envs/miniconda3/bin/activate&&python ~/envs/get_info.py -l 2"
        self.config = config
        self.psw = self.config.psw
        self.servers = []
        self.slaver_info = self.config.slaver_info
        self.slaver_queue = slaver_queue
        self.online_slaver = online_slaver
        self.slaver_state = slaver_state
        for slaver in self.slaver_info:
            info = (slaver["ip"], slaver["name"], 22, slaver["user_name"], self.py_cmd)
            self.servers.append(info)
        self.is_running = True
        self.byteunits = ('B', 'KB', 'MB', 'GB', 'TB')
        self.webbyteunits = ('bps', ' Kbps', 'Mbps', 'Gbps')
        self.slaver_lock = threading.Lock()
        self.use_influx = False
        try:
            from influxdb import InfluxDBClient
            self.dbclient = InfluxDBClient('localhost', 8086, 'python', 'python', 'cvlab')
            self.use_influx = True
            write_log("节点信息数据库连接成功", self.config.config["server_log_path"])
        except:
            write_log("节点信息数据库连接失败", self.config.config["server_log_path"])

    def fetch_hw_info(self, server, nickname, port, username, cmd, comm):

        def parse_info_to_json(r):
            info = json.loads(r)
            # print(info['cpu'])

            ts = datetime.utcnow().isoformat()

            def get_common_body(measurement, name, fields):
                return {
                    "measurement": measurement,
                    "tags": {
                        "host": nickname,
                        measurement: name
                    },
                    "time": ts,
                    "fields": fields
                }

            cpu_body = [get_common_body("cpu", f"cpu{i:d}", {"value": j}) for i, j in enumerate(info['cpu'])]
            cpu_body.append(get_common_body("cpu", f"cpu-total", {"value": info['cpu_total']}))

            ram_body = [{
                "measurement": "ram",
                "tags": {
                    "host": nickname
                },
                "time": ts,
                "fields": info['ram']
            }]

            def parse_gpu(js):
                js['mem_available'] = js['mem_total'] - js['mem_used']
                del js['id']
                return js

            def parse_net(js):
                js['recv_bytes_ps'] = float(js['recv_bytes_ps'])
                js['sent_bytes_ps'] = float(js['sent_bytes_ps'])
                del js['id']
                return js

            net_body = [get_common_body("net", net['id'], parse_net(net)) for net in info['net']]

            if 'gpu' in info:
                gpu_body = [get_common_body("gpu", f"gpu{j['id']}", parse_gpu(j)) for j in info['gpu']]
            else:
                gpu_body = []
    
            return cpu_body + ram_body + gpu_body + net_body

        def format_json(r, nickname):
            r = json.loads(r)

            def filesizeformat(value, byteunits):
                exponent = int(log(value+0.1, 1024))
                return "%.1f %s" % (float(value) / pow(1024, exponent), byteunits[exponent])
            gpus = []
            try:
                if len(r["gpu"]) == 0:
                    gpus = [{"gpu_used": "No data", "avail_vram": "No data", "vram_percent": "No data"}]
                else:
                    for gpu in r["gpu"]:
                        gpu_info = {"gpu_used": str(gpu["load"]*100)+" %", "avail_vram": str(round((gpu["mem_total"]-gpu["mem_used"])/1024., 2))+" GB", "mem_util": gpu["mem_util"]}
                        gpus.append(gpu_info)
            except:
                gpus = [{"gpu_used": "No data", "avail_vram": "No data", "vram_percent": "No data"}]

            cpu_used = 0
            gpu_used = []
            for state in self.slaver_state:
                if nickname == state["name"]:
                    cpu_used = int(state["cpu_used"])
                    for g in state["gpu_used"]:
                        gpu_used.append(int(g))
                    break
            info = {"name": nickname, "cpu_usage": str(r["cpu_total"])+" %", "avail_ram": filesizeformat(r["ram"]["available"], self.byteunits), 
                    "web_up":filesizeformat(r["net"][0]["sent_bytes_ps"], self.webbyteunits), "web_down":filesizeformat(r["net"][0]["recv_bytes_ps"], self.webbyteunits), 
                    "gpus": gpus, "online": self.online_slaver, "cpu_used": cpu_used, "gpu_used": gpu_used}
            data = {"mode": "mon", "ui": "main" , "info": info}
            if self.slaver_queue.full():
                self.slaver_queue.get()
            self.slaver_queue.put(info)
            info = json.dumps(data)
            return info
        
        client = paramiko.SSHClient()
        # client.load_system_host_keys(filename=pub_key)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(server, username=username, port=port, timeout=30, password=self.psw)
            stdin, stdout, stderr = client.exec_command(cmd)
            write_log("计算节点 "+str(nickname)+" 连接成功", self.config.config["server_log_path"])
            while self.is_running:
                try:
                    # if client.
                    if not nickname in self.online_slaver:
                        self.online_slaver.append(nickname)
                    r = stdout.readline()
                    # print(stderr.read().decode())
                    # if stdout.channel.exit_status_ready():
                    #     break
                    if len(r):
                        send_info = format_json(r, nickname)
                        # print(r)
                        comm.send_all(send_info)
                        if self.use_influx:
                            try:
                                if self.dbclient is not None:
                                    points = parse_info_to_json(r)
                                    self.dbclient.write_points(points, time_precision='ms')
                            except:
                                pass
                    if stdout.channel.exit_status_ready():
                        break
                except:
                    print(f"Server: {nickname}:")
                    traceback.print_exc()
                    print('*' * 8)
                    break
            client.close()
            if nickname in self.online_slaver:
                self.online_slaver.remove(nickname)
                write_log("计算节点 "+nickname+" 掉线", self.config.config["server_log_path"])
                comm.send_all(json.dumps({"mode": "mon", "ui": "main" , "info": {"name": nickname, "cpu_usage": "No data", "avail_ram": "No data", "web_up":"No data", "web_down":"No data","gpus": [{"gpu_used": "No data", "avail_vram": "No data"}], "online": self.online_slaver}}))
        except Exception as e:
            # print(e)
            if nickname in self.online_slaver:
                self.online_slaver.remove(nickname)
                write_log("计算节点 "+nickname+" 连接错误", self.config.config["server_log_path"])
            print(f"Connection to {nickname} failed")

    def fetch_loop(self, *args):
        # print(args)
        retry_delay = 30
        while self.is_running:
            self.fetch_hw_info(*args,)
            if self.is_running:
                print(f"[{args[2]}]: Found some error, try again after {retry_delay}s", file=sys.stderr)
                time.sleep(retry_delay)
    
    def run(self, comm):

        thres = [threading.Thread(target=self.fetch_loop, args=(*server_info, comm)) for server_info in self.servers]
        for i, j in enumerate(self.servers):
            print(f"Connect to {j[1]}")
            thres[i].start()
        try:
            while True:
                time.sleep(60)
                try:
                    self.config.update_slaver_info()
                    for server in self.slaver_info:
                        name = server["name"]
                        flag = True
                        for s in self.servers:
                            if s[1] == name:
                                flag = False    # 判断服务器是否在列表中
                                break
                        if flag:    # 不在列表中
                            info = (server["ip"], server["name"], 22, server["user_name"], self.py_cmd)
                            print(info)
                            self.servers.append(info)
                            thres.append(threading.Thread(target=self.fetch_loop, args=(*info, comm)))
                            thres[-1].start()
                except Exception as e:
                    print("服务器列表更新失败, 原因是: "+str(e))
        except:
            pass
        self.is_running = False
        print("Stop all threads")
        for i, j in enumerate(self.servers):
            print(f"Disconnect from {j[1]}")
            thres[i].join()
        print("All threads done")

if __name__ == "__main__":
    mon = Monitor()
    mon.run()