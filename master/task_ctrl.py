import threading
from global_var import wait_queue, wait_task, exec_task, hist_task, task_lock, stop_lock, stop_task
from queue import Queue
import time
import json
import datetime
import copy
import os
import paramiko
from logger import log
from config import config

class Task_Control:
    def __init__(self, config: config, slaver_queue: Queue, oneline_server, slaver_state) -> None:
        self.config = config
        self.root = self.config.config["root"]
        self.slaver_queue = slaver_queue
        self.online_server = oneline_server
        self.slaver_state = slaver_state
        self.exec_pool = []     # 正在运行的线程池
        self.exec_id = []     # 正在运行的任务ID, 其下标与exec_pool对应
        self.load_task()
        self.thread_ret_queue = Queue(0)    #用于接收子线程返回值
        self.state_lock = threading.Lock()
        pass
    
    def load_task(self):
        try:
            with open("./task_info/wait_task.json", "r", encoding="utf-8") as f:
                t = json.load(f)
            wait_task.extend(t)
            print("load wait_task.json success.")
        except Exception as e:
            print("load wait_task.json falid, "+str(e))
        
        try:
            with open("./task_info/exec_task.json", "r", encoding="utf-8") as f:
                t = json.load(f)
            exec_task.extend(t)
            print("load exec_task.json success.")
        except Exception as e:
            print("load exec_task.json falid, "+str(e))
        
        try:
            with open("./task_info/hist_task.json", "r", encoding="utf-8") as f:
                t = json.load(f)
            hist_task.extend(t)
            print("load hist_task.json success.")
        except Exception as e:
            print("load hist_task.json falid, "+str(e))
        if not len(exec_task) == 0:
            for t in exec_task:
                t["state"] = "offline_error"
                log("任务 "+t["task_id"]+" 运行错误, 原因是服务端下线", self.config.config["server_log_path"])
                hist_task.append(t)
            exec_task.clear()
    
    def dump_task_loop(self):
        while True:
            time.sleep(60)
            task_lock.acquire()
            try:
                with open("./task_info/wait_task.json", "w", encoding="utf-8") as f:
                    json.dump(wait_task, f, indent=2)
                # print("dump wait_task.json success.")
            except Exception as e:
                print("dump wait_task.json falid, "+str(e))
            
            try:
                with open("./task_info/exec_task.json", "w", encoding="utf-8") as f:
                    json.dump(exec_task, f, indent=2)
                # print("dump exec_task.json success.")
            except Exception as e:
                print("dump exec_task.json falid, "+str(e))
            
            try:
                with open("./task_info/hist_task.json", "w", encoding="utf-8") as f:
                    json.dump(hist_task, f, indent=2)
                # print("dump hist_task.json success.")
            except Exception as e:
                print("dump hist_task.json falid, "+str(e))
            task_lock.release()
    
    def check_and_move_to_exec(self):
        # 检查节点状态, 若有空闲节点则移动一个任务到执行区

        if not self.slaver_queue.empty():
            # 获取节点状态
            curr_state = self.slaver_queue.get()
            self.state_lock.acquire()
            # 初始化并获得节点信息
            gpu_reuse = []
            gpu_used = []
            gpu_mem_util = []
            for gpu in curr_state["gpus"]:
                if not gpu["gpu_used"] == "No data":
                    gpu_used.append(False)
                    gpu_mem_util.append(gpu["mem_util"])
                    if gpu["mem_util"] < 0.5:
                        gpu_reuse.append(True) # 显存占用低于50%, 可以复用
                        # gpu_used.append(False)
                    else:
                        gpu_reuse.append(False)
                        # gpu_used.append(True)
            for s in self.config.slaver_info:
                if s["name"] == curr_state["name"]:
                    ip = s["ip"]
                    user_name = s["user_name"]
                    gpu_count = s["gpu_count"]
            state = {"name": curr_state["name"], "ip": ip, "user_name": user_name, "gpu_count": gpu_count ,"gpu_reuse": gpu_reuse, "gpu_used": gpu_used, "cpu_used": False, "avail_gpus": gpu_count, "mem_util": gpu_mem_util}
            flag = False
            for i in range(len(self.slaver_state)):
                if state["name"] == self.slaver_state[i]["name"]:
                    flag = True
                    idx = i
            if flag:
                self.slaver_state[idx]["gpu_reuse"] = gpu_reuse
                self.slaver_state[idx]["mem_util"] = gpu_mem_util
                # self.slaver_state[idx]["gpu_used"] = gpu_used
                # for j in range(len(self.slaver_state[idx]["gpu_used"])):
                #     if not self.slaver_state[idx]["gpu_used"][j]:
                #         self.slaver_state[idx]["gpu_used"][j] = gpu_used[j]
            else:
                self.slaver_state.append(state)
            for i in range(len(self.slaver_state)):
                if self.slaver_state[i]["name"] not in self.online_server:
                    self.slaver_state.pop(i)
                    break
            
            task_lock.acquire()
            scan_sceq = []  #扫描顺序
            insert_idx = 0
            for i in range(len(wait_task)):
                # 扫描是否存在紧急任务, 并确定扫描顺序
                if wait_task[i]["is_urgent"] == 1:
                    scan_sceq.insert(insert_idx, i)
                    insert_idx += 1
                else:
                    scan_sceq.append(i)

            for i in scan_sceq:
                # 将等待区的一个任务移动到执行区
                can_run = [False, False, False] # 经过一系列判断, 确定这个任务能不能执行, 第一个参数为是否存在空闲节点, 第二个参数为该任务的前驱任务是否完成, 第三个参数为当前节点GPU是否可供运行
                task = wait_task[i]
                # print(task)
                gpu_count = task["need_gpus"]
                is_reuse_gpu = True if task["is_reuse_gpu"] == 1 else False
                need_gpus = int(task["need_gpus"])
                if not task["prev"] == "(无)":
                    for h in hist_task:
                        if task["prev"] == h["task_id"]:
                            can_run[1] = True
                else:
                    can_run[1] = True
                if need_gpus > 0:
                    # 使用GPU的任务
                    for j in range(len(self.slaver_state)):
                        gpu_num = []
                        if task["slaver"] == "<默认>":
                            # 不指定特定节点的任务
                            pass
                        elif not task["slaver"] == self.slaver_state[j]["name"]:
                            # 指定了特定节点的任务
                            continue
                        if self.slaver_state[j]["avail_gpus"] >= need_gpus:
                            if can_run[1]:
                                if is_reuse_gpu:
                                    # 如果设置了gpu复用
                                    reuse_gpu_counts = sum(self.slaver_state[j]["gpu_reuse"])
                                    remain_gpus = need_gpus
                                    if reuse_gpu_counts >= need_gpus:
                                        for reuse, used, num in zip(self.slaver_state[j]["gpu_reuse"], self.slaver_state[j]["gpu_used"], range(self.slaver_state[j]["gpu_count"])):   # 判断该节点的GPU是否有足够的显存供任务运行
                                            if reuse and not used:
                                                remain_gpus -= 1   # 存在GPU具备足够的显存
                                                gpu_num.append(num)
                                            if remain_gpus == 0:
                                                can_run[2] = True
                                                task["slaver"] = self.slaver_state[j]["name"]  # 将任务分配至节点
                                                can_run[0] = True
                                                break
                                else:
                                    remain_gpus = need_gpus
                                    for mem_util, used, num in zip(self.slaver_state[j]["mem_util"], self.slaver_state[j]["gpu_used"], range(self.slaver_state[j]["gpu_count"])):   # 判断该节点的GPU是否有足够的显存供任务运行
                                        if mem_util < 0.1 and not used:
                                            remain_gpus -= 1
                                            gpu_num.append(num)
                                        if remain_gpus == 0:
                                            self.slaver_state[j]["avail_gpus"] -= need_gpus
                                            can_run[2] = True
                                            task["slaver"] = self.slaver_state[j]["name"]  # 将任务分配至节点
                                            can_run[0] = True
                                            break
                                if sum(can_run) == 3:
                                    task["gpu_num"] = gpu_num
                                    break
                else:
                    # 不使用GPU的任务
                    for j in range(len(self.slaver_state)):
                        if task["slaver"] == "<默认>":
                            # 不指定特定节点的任务
                            pass
                        elif not task["slaver"] == self.slaver_state[j]["name"]:
                            # 指定了特定节点的任务
                            continue
                        if not self.slaver_state[j]["cpu_used"]:
                            if can_run[1]:
                                task["slaver"] = self.slaver_state[j]["name"]  # 将任务分配至节点
                                self.slaver_state[j]["cpu_used"] = True
                                can_run[0] = True
                                can_run[2] = True
                                break
                if sum(can_run) == 3:
                    # 任务可以执行
                    wait_task.pop(i)
                    task["state"] = "pexec"
                    exec_task.append(task)
                    break
            task_lock.release()
            self.state_lock.release()
        
    def check_complete_task(self):
        # 检查已经完成的任务，并将其放入历史任务中
        if not self.thread_ret_queue.empty():
            # 有结束的任务
            self.state_lock.acquire()
            ret = self.thread_ret_queue.get()
            task_id = ret["task_id"]
            ret_code = ret["ret"]
            for i in range(len(self.exec_pool)):
                # 获得执行线程池中的任务信息
                if self.exec_pool[i]["task_id"] == task_id:
                    if not self.exec_pool[i]["thread"].is_alive():  #如果该任务在线程池中且线程已经退出
                        # 释放资源
                        for j in range(len(self.slaver_state)):
                            if self.exec_pool[i]["slaver"] == self.slaver_state[j]["name"]: #寻找节点
                                if int(self.exec_pool[i]["need_gpus"]) > 0:
                                    if self.exec_pool[i]["is_reuse_gpu"] == 1:
                                        #设置了GPU复用则不释放GPU
                                        pass
                                    else:
                                        self.slaver_state[j]["avail_gpus"] += int(self.exec_pool[i]["need_gpus"])   #恢复GPU数量
                                        for g in self.exec_pool[i]["gpu_num"]:
                                            self.slaver_state[j]["gpu_used"][g] = False     #释放GPU占用
                                else:
                                    self.slaver_state[j]["cpu_used"] = False    #释放CPU占用
                                break

                        self.exec_pool.pop(i)   # 从线程池里弹出任务
                        if self.exec_id[i] == task_id:
                            self.exec_id.pop(i)  # 从正在运行的任务ID列表中将该任务的ID删除
                        else:
                            self.exec_id.remove(task_id)  # 从正在运行的任务ID列表中将该任务的ID删除
                        task_lock.acquire()
                        for i in range(len(exec_task)):
                            # 从正在执行任务列表移动到历史任务列表
                            if exec_task[i]["task_id"] == task_id:
                                task = exec_task.pop(i)
                                # 根据返回值更新状态
                                # {"wait": "等待中", "exec": "运行中", "pexec": "准备中", "accp": "完成", "err": "错误", "offline_error": "错误, 节点掉线", "term": "中止"}
                                if ret_code == 0:
                                    task["state"] = "accp"
                                    log("任务 "+task_id+" 运行完成", self.config.config["server_log_path"])
                                elif ret_code == -1:
                                    task["state"] = "offline_error"
                                    log("任务 "+task_id+" 因计算节点原因运行错误", self.config.config["server_log_path"])
                                elif ret_code == -2:
                                    task["state"] = "term"
                                    log("任务 "+task_id+" 被中止", self.config.config["server_log_path"])
                                else:
                                    task["state"] = "err"
                                    log("任务 "+task_id+" 运行错误", self.config.config["server_log_path"])
                                hist_task.append(task)
                                break
                        task_lock.release()
                        break
                    else:
                        self.thread_ret_queue.put(ret)  # 未退出则再放回完成任务的队列中

            self.state_lock.release()
    
    def run_task(self):
        # 执行任务
        task_lock.acquire()
        for e in exec_task:
            if e["task_id"] not in self.exec_id:
                self.exec_id.append(e["task_id"])
                self.exec_pool.append(copy.deepcopy(e))
        task_lock.release()

        self.state_lock.acquire()
        for i in range(len(self.exec_pool)):
            if "cmd" not in self.exec_pool[i].keys():
                print(self.exec_pool[i])
                self.exec_pool[i]["cmd"] = "source .bashrc&&source ~/envs/miniconda3/bin/activate&&conda activate "+self.exec_pool[i]["envs"]+"&&cd "+self.root+self.exec_pool[i]["path"][1:]+"&&export PYTHONUNBUFFERED=1&&export NCCL_P2P_DISABLE=1&&export QT_QPA_PLATFORM=offscreen "
                slaver_name = self.exec_pool[i]["slaver"]
                cuda = "&&export CUDA_VISIBLE_DEVICES="
                if int(self.exec_pool[i]["need_gpus"]) > 0:
                    # 设置了使用GPU
                    for j in range(len(self.slaver_state)):
                        if slaver_name == self.slaver_state[j]["name"]:
                            ip = self.slaver_state[j]["ip"]
                            for k in self.exec_pool[i]["gpu_num"]:
                                if not self.exec_pool[i]["is_reuse_gpu"] == 1:
                                    self.slaver_state[j]["gpu_used"][k] = True # 占用GPU
                                cuda += str(k)
                                cuda += ","
                            break
                else:
                    # 设置只使用cpu
                    for j in range(len(self.slaver_state)):
                        if slaver_name == self.slaver_state[j]["name"]:
                            ip = self.slaver_state[j]["ip"]
                            cuda += str(self.slaver_state[j]["gpu_count"])
                            cuda += ","
                            break
                cuda = cuda[:-1]    #去掉最后的逗号
                for s in self.config.slaver_info:
                    # 获得使用计算节点的用户名
                    if s["name"] == self.exec_pool[i]["slaver"]:
                        self.exec_pool[i]["user_name"] = s["user_name"]
                        break
                self.exec_pool[i]["cmd"] += cuda
                self.exec_pool[i]["cmd"] += "&&"
                self.exec_pool[i]["cmd"] += self.exec_pool[i]["exec"]
                self.exec_pool[i]["ip"] = ip
                exec_thread = threading.Thread(target=self.exec_cmd, args=(self.exec_pool[i]["task_id"], self.exec_pool[i]["ip"], self.exec_pool[i]["cmd"],self.exec_pool[i]["user_name"], ))
                self.exec_pool[i]["thread"] = exec_thread
                self.exec_pool[i]["thread"].start()
        self.state_lock.release()
        
    def exec_cmd(self, task_id, ip, cmd, user_name):
        client = paramiko.SSHClient()
        # client.load_system_host_keys(filename=pub_key)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        is_running = True
        try:
            client.connect(ip, username=user_name, port=22, timeout=5, password=self.config.psw)
            stdin, stdout, stderr = client.exec_command(cmd, bufsize=0, get_pty=True)
            # chan = client.get_transport().open_session()
            # chan.get_pty()
            # chan.invoke_shell()
            # chan.send(cmd)
            log("任务 "+task_id+" 开始运行", self.config.config["server_log_path"])
            while is_running:
                if stdout.channel.recv_ready():
                    msg = stdout.channel.recv(4096).decode(encoding="utf-8", errors="ignore")
                    with open(os.path.join(self.root, self.config.config["train_log_path"], task_id+".log"), "a") as f:
                        f.write(msg)
                if stdout.channel.exit_status_ready():
                    self.thread_ret_queue.put({"task_id": task_id, "ret": stdout.channel.recv_exit_status()})
                    with open(os.path.join(self.root, self.config.config["train_log_path"], task_id+".log"), "a") as f:
                        f.write("\n\nProgram Exit With Code "+str(stdout.channel.recv_exit_status()))
                    is_running = False
                    client.close()
                # if chan.recv_ready():
                #     with open(os.path.join(self.root, self.config.config["train_log_path"], task_id+".log"), "a") as f:
                #         f.write(chan.recv(4096).decode(encoding="utf-8",errors="ignore"))
                # if chan.recv_stderr_ready():
                #     with open(os.path.join(self.root, self.config.config["train_log_path"], task_id+".log"), "a") as f:
                #         f.write(chan.recv_stderr(4096).decode(encoding="utf-8",errors="ignore"))
                # if chan.exit_status_ready():
                #     self.thread_ret_queue.put({"task_id": task_id, "ret": chan.recv_exit_status()})
                #     with open(os.path.join(self.root, self.config.config["train_log_path"], task_id+".log"), "a") as f:
                #         f.write("\n\nProgram Exit With Code "+str(chan.recv_exit_status()))
                time.sleep(0.01)
                stop_lock.acquire()
                if task_id in stop_task:
                    is_running = False
                    self.thread_ret_queue.put({"task_id": task_id, "ret": -2})
                    stop_task.remove(task_id)
                    # chan.shutdown(2)
                    client.close()
                stop_lock.release()
        except Exception as e:
            print(e)
            self.thread_ret_queue.put({"task_id": task_id, "ret": -1})
            is_running = False
            client.close()

    def main_loop(self, comm):
        while True:
            flag = False
            while not flag:
                global wait_queue
                flag = wait_queue.empty()
                if not flag:
                    task = wait_queue.get()
                    print("get "+str(task))
                    curr_time = str(datetime.datetime.now())[2:-4]
                    curr_time = curr_time.replace("-", "").replace(":", "").replace(" ", "").replace(".", "")
                    task["task_id"] = curr_time
                    task["state"] = "wait"
                    task_lock.acquire()
                    wait_task.append(task)
                    log("添加了任务 "+task["task_id"], self.config.config["server_log_path"])
                    task_lock.release()
            # print(self.slaver_state)
            self.check_and_move_to_exec()
            self.run_task()
            self.check_complete_task()

            task_lock.acquire()
            for e in range(len(exec_task)):
                if os.path.exists(os.path.join(self.root, self.config.config["train_log_path"], exec_task[e]["task_id"]+".log")) and not exec_task[e]["state"] == "exec":
                    exec_task[e]["state"] = "exec"
            task_lock.release()

            # print(self.slaver_state)
            if len(hist_task) > 100:
                send_his_task = hist_task[-100:]
            else:
                send_his_task = hist_task
            try:
                send_str = {"mode": "task_mon", "ui": "main" , "info": {"wait": wait_task, "exec": exec_task, "hist": send_his_task}}
                comm.send_all(json.dumps(send_str))
            except Exception as e:
                print(e)
            time.sleep(2)

    def run(self, comm):
        main_thred = threading.Thread(target=self.main_loop, args=(comm, ))
        dump_thread = threading.Thread(target=self.dump_task_loop)
        main_thred.start()
        dump_thread.start()
        while True:
            time.sleep(1)
       
    