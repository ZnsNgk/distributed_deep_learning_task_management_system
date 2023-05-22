from config import config
import json
import paramiko
import os
import copy
import datetime
import base64
from global_var import wait_queue, wait_task, exec_task, hist_task, task_lock, visible_folder, stop_task, stop_lock
from logger import log

def process(info):
    conf = config("conf.json")
    conf.get_info()
    user_name = os.getlogin()
    root = "/home/" + user_name
    try:
        info = json.loads(info.replace("'", '"'))
        mode = info["mode"]
        msg = info["info"]
        ui = info["ui"]
        if mode == "env_list":
            ret = os.popen("conda env list | awk '{print $1}'")
            res = ret.read()
            res = res.replace("\n\n", "").split("\n")
            res = res[2:]
            send_info = {"mode": "ret_env_list", "ui": ui , "info": res}
            send_info = json.dumps(send_info)
            return (send_info, True)
        elif mode == "test_env":
            py_cmd = "source ~/envs/miniconda3/bin/activate&&conda activate " + msg
            client = paramiko.SSHClient()
            # client.load_system_host_keys(filename=pub_key)
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect("127.0.0.1", username=user_name, port=22, timeout=30, password=conf.psw)
                stdin, stdout, stderr = client.exec_command(py_cmd)
                stdout = stdout.read()
                stdout = stdout.decode()
                stderr = stderr.read()
                stderr = stderr.decode()
                if stdout == "" and stderr == "":
                    ret = "True"
                elif not stderr == "":
                    ret = stderr
                send_info = {"mode": "ret_test_env", "ui": ui , "info": ret}
                send_info = json.dumps(send_info)
                return (send_info, True)
            except Exception as e:
                print(e)
                return ("", False)
        elif mode == "py_v":
            py_cmd = "source ~/envs/miniconda3/bin/activate&&conda activate " + msg+"&&python -V"
            client = paramiko.SSHClient()
            # client.load_system_host_keys(filename=pub_key)
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect("127.0.0.1", username=user_name, port=22, timeout=30, password=conf.psw)
                stdin, stdout, stderr = client.exec_command(py_cmd)
                stdout = stdout.read()
                stdout = stdout.decode()
                stderr = stderr.read()
                stderr = stderr.decode()
                if not stderr == "":
                    ret = {"res": "falied", "msg": stderr}
                else:
                    ret = {"res": "seccess", "msg": stdout}
                send_info = {"mode": "ret_py_v", "ui": ui , "info": ret}
                send_info = json.dumps(send_info)
                return (send_info, True)
            except Exception as e:
                print(e)
                return ("", False)
        elif mode == "cuda_pt":
            py_cmd = "source ~/envs/miniconda3/bin/activate&&conda activate " + msg+"&&python ~/envs/check_cuda_pt.py"
            client = paramiko.SSHClient()
            # client.load_system_host_keys(filename=pub_key)
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect("127.0.0.1", username=user_name, port=22, timeout=30, password=conf.psw)
                stdin, stdout, stderr = client.exec_command(py_cmd)
                stdout = stdout.read()
                stdout = stdout.decode()
                stderr = stderr.read()
                stderr = stderr.decode()
                if not stderr == "":
                    ret = {"res": "falied", "msg": stderr}
                else:
                    ret = {"res": "seccess", "msg": stdout}
                send_info = {"mode": "ret_cuda_pt", "ui": ui , "info": ret}
                send_info = json.dumps(send_info)
                return (send_info, True)
            except Exception as e:
                print(e)
                return ("", False)
        elif mode == "cuda_tf":
            py_cmd = "source ~/envs/miniconda3/bin/activate&&conda activate " + msg+"&&python ~/envs/check_cuda_tf.py"
            client = paramiko.SSHClient()
            # client.load_system_host_keys(filename=pub_key)
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect("127.0.0.1", username=user_name, port=22, timeout=30, password=conf.psw)
                stdin, stdout, stderr = client.exec_command(py_cmd)
                stdout = stdout.read()
                stdout = stdout.decode()
                stderr = stderr.read()
                stderr = stderr.decode()
                if not stderr == "":
                    ret = {"res": "falied", "msg": stderr}
                else:
                    ret = {"res": "seccess", "msg": stdout}
                send_info = {"mode": "ret_cuda_tf", "ui": ui , "info": ret}
                send_info = json.dumps(send_info)
                return (send_info, True)
            except Exception as e:
                print(e)
                return ("", False)
        elif mode == "pkgs":
            py_cmd = "source ~/envs/miniconda3/bin/activate&&conda activate " + msg+"&&conda list"
            client = paramiko.SSHClient()
            # client.load_system_host_keys(filename=pub_key)
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect("127.0.0.1", username=user_name, port=22, timeout=30, password=conf.psw)
                stdin, stdout, stderr = client.exec_command(py_cmd)
                stdout = stdout.read()
                stdout = stdout.decode()
                stderr = stderr.read()
                stderr = stderr.decode()
                if not stderr == "":
                    ret = {"res": "falied", "msg": stderr.replace('"', '\"').replace("'", "\'")}
                else:
                    ret = {"res": "seccess", "msg": stdout.replace('"', '\"').replace("'", "\'")}
                send_info = {"mode": "ret_pkgs", "ui": ui , "info": ret}
                send_info = json.dumps(send_info)
                return (send_info, True)
            except Exception as e:
                print(e)
                return ("", False)
        elif mode == "get_folder":
            cmd = "cd ~" + msg+"&&ls -l | grep ^d | awk -F \" \" '{for (i=9;i<=NF;i++)printf(\"%s \", $i);print \"\"}'"
            ret = os.popen(cmd)
            ret = ret.read()
            folder_list = ret.replace("\n\n", "").split("\n")[:-1]
            new_folder_list = []
            for file in folder_list:
                new_folder_list.append(file[:-1])
            cmd = "cd ~" + msg+"&&ls -l | grep ^[^d] | awk -F \" \" '{for (i=9;i<=NF;i++)printf(\"%s \", $i);print \"\"}'"
            ret = os.popen(cmd)
            ret = ret.read()
            file_list = ret.replace("\n\n", "").split("\n")[1:-1]
            new_file_list = []
            for file in file_list:
                new_file_list.append(file[:-1])
            cmd = "cd ~" + msg+"&&pwd"
            ret = os.popen(cmd)
            ret = ret.read()
            curr_path = ret.replace(root, "").replace("\n", "")
            send_info = {"mode": "ret_folder", "ui": ui , "info": {"folder": new_folder_list, "file": new_file_list, "curr_path": curr_path}}
            send_info = json.dumps(send_info)
            return (send_info, True)
        elif mode == "get_file":
            cmd = "cat ~" + msg
            try:
                ret = os.popen(cmd)
                ret = ret.read()
                ret = str(base64.b64encode(bytes(ret, encoding="utf-8")).decode("utf-8"))
                send_info = {"mode": "ret_file", "ui": ui , "info": {"file_name": "~" + msg, "content": ret, "state": "success"}}
                send_info = json.dumps(send_info)
            except Exception as e:
                send_info = {"mode": "ret_file", "ui": ui , "info": {"file_name": "~" + msg, "content": "", "state": "failed"}}
                send_info = json.dumps(send_info)
            return (send_info, True)
        elif mode == "save_file":
            path = root + msg["path"]
            content = msg["content"]
            try:
                content = str(base64.b64decode(bytes(str(content).encode("utf-8"))).decode("utf-8")) 
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                send_info = {"mode": "ret_save_file", "ui": ui , "info": "success"}
            except Exception as e:
                send_info = {"mode": "ret_save_file", "ui": ui , "info": str(e).replace(root, "")}
            send_info = json.dumps(send_info)
            return (send_info, True)
        elif mode == "file_operate":
            opera = msg["mode"]
            curr_folder = msg["root"]
            name = msg["name"]
            old_name = msg["old_name"]
            if opera == "mkdir" or opera == "touch":
                cmd = "cd " + root + curr_folder + "&&" + opera + " " + name
            elif opera == "mv":
                cmd = "cd " + root + curr_folder + "&&" + opera + " " + old_name + " " + name
            try:
                ret = os.popen(cmd)
                ret = ret.read()
                if ret == "":
                    send_info = {"mode": "ret_file_operate", "ui": ui , "info": "success"}
                else:
                    send_info = {"mode": "ret_file_operate", "ui": ui , "info": ret}
            except Exception as e:
                send_info = {"mode": "ret_file_operate", "ui": ui , "info": str(e).replace(root, "")}
            send_info = json.dumps(send_info)
            return (send_info, True)
        elif mode == "rm_file":
            path =  root + msg
            try:
                os.remove(path)
                send_info = {"mode": "ret_rm_file", "ui": ui , "info": "success"}
                log("删除了文件 "+path.replace(root, ""), conf.config["server_log_path"])
            except:
                try:
                    os.removedirs(path)
                    send_info = {"mode": "ret_rm_file", "ui": ui , "info": "success"}
                    log("删除了文件夹 "+path.replace(root, ""), conf.config["server_log_path"])
                except Exception as e:
                    send_info = {"mode": "ret_rm_file", "ui": ui , "info": str(e).replace(root, "")}
                    log("删除文件或文件夹 "+path.replace(root, "")+"失败, 原因是"+str(e).replace(root, ""), conf.config["server_log_path"])
            send_info = json.dumps(send_info)
            return (send_info, True)
        elif mode == "add_task":
            try:
                wait_queue.put(msg)
                send_info = {"mode": "ret_add_task", "ui": ui , "info": ""}
            except Exception as e:
                send_info = {"mode": "ret_add_task", "ui": ui , "info": str(e)}
            send_info = json.dumps(send_info)
            return (send_info, True)    
        elif mode == "change_task":
            task_id = msg["task_id"]
            ret = False
            task_lock.acquire()
            try:
                for i in range(len(wait_task)):
                    if task_id == wait_task[i]["task_id"]:
                        wait_task[i] = msg
                        if wait_task[i]["state"] == "":
                            wait_task[i]["state"] = "wait"
                        ret = True
                for i in range(len(hist_task)):
                    if task_id == hist_task[i]["task_id"]:
                        hist_task.pop(i)
                        wait_queue.put(msg)
                        ret = True
                        break
                if not ret:
                    send_info = {"mode": "ret_change_task", "ui": ui , "info": "修改失败, 原因可能是任务已经开始运行或任务已经被删除"}
                    log("任务 "+task_id+" 修改失败", conf.config["server_log_path"])
                else:
                    send_info = {"mode": "ret_change_task", "ui": ui , "info": ""}
                    log("任务 "+task_id+" 被修改", conf.config["server_log_path"])
            except Exception as e:
                send_info = {"mode": "ret_change_task", "ui": ui , "info": "修改失败, 原因是: \n"+str(e)}
                log("任务 "+task_id+" 修改失败", conf.config["server_log_path"])
            task_lock.release()
            send_info = json.dumps(send_info)
            return (send_info, True)
        elif mode == "del_task":
            task_id = msg
            ret = False
            task_lock.acquire()
            try:
                for i in range(len(wait_task)):
                    if task_id == wait_task[i]["task_id"]:
                        wait_task.pop(i)
                        print(len(wait_task))
                        ret = True
                        break
                for i in range(len(hist_task)):
                    if task_id == hist_task[i]["task_id"]:
                        hist_task.pop(i)
                        ret = True
                        break
                if not ret:
                    send_info = {"mode": "ret_del_task", "ui": ui , "info": {"task_id": task_id, "info": "任务"+task_id+"删除失败, 原因可能是任务已经开始运行或任务不存在"}}
                    log("任务 "+task_id+" 删除失败", conf.config["server_log_path"])
                else:
                    send_info = {"mode": "ret_del_task", "ui": ui , "info": {"task_id": task_id, "info": ""}}
                    log("任务 "+task_id+" 删除成功", conf.config["server_log_path"])
            except Exception as e:
                send_info = {"mode": "ret_del_task", "ui": ui , "info": {"task_id": task_id, "info": "任务"+task_id+"删除失败, 原因是: \n"+str(e)}}
                log("任务 "+task_id+" 删除失败", conf.config["server_log_path"])
            task_lock.release()
            send_info = json.dumps(send_info)
            return (send_info, True)
        elif mode == "resub_task":
            task_id = msg
            ret = False
            task_lock.acquire()
            try:
                for i in range(len(wait_task)):
                    if task_id == wait_task[i]["task_id"]:
                        resub = copy.deepcopy(wait_task[i])
                        ret = True
                        break
                for i in range(len(exec_task)):
                    if task_id == exec_task[i]["task_id"]:
                        resub = copy.deepcopy(exec_task[i])
                        ret = True
                        break
                for i in range(len(hist_task)):
                    if task_id == hist_task[i]["task_id"]:
                        resub = copy.deepcopy(hist_task[i])
                        ret = True
                        break
                if ret:
                    curr_time = str(datetime.datetime.now())[2:-4]
                    curr_time = curr_time.replace("-", "").replace(":", "").replace(" ", "").replace(".", "")
                    resub["task_id"] = curr_time
                    resub["state"] = "wait"
                    wait_task.append(resub)
                    send_info = {"mode": "ret_resub_task", "ui": ui , "info": {"task_id": resub["task_id"], "info": ""}}
                    log("任务 "+task_id+" 被重新提交", conf.config["server_log_path"])
                    pass
                else:
                    send_info = {"mode": "ret_resub_task", "ui": ui , "info": {"task_id": task_id, "info": "任务"+task_id+"重新提交失败, 原因可能是找不到该任务"}}
                    log("任务 "+task_id+" 重新提交失败", conf.config["server_log_path"])
            except Exception as e:
                send_info = {"mode": "ret_resub_task", "ui": ui , "info": {"task_id": task_id, "info": "任务"+task_id+"重新提交失败, 原因是: \n"+str(e)}}
                log("任务 "+task_id+" 重新提交失败", conf.config["server_log_path"])
            task_lock.release()
            send_info = json.dumps(send_info)
            return (send_info, True)
        elif mode == "get_root":
            send_info = {"mode": "ret_root", "ui": ui , "info": visible_folder}
            send_info = json.dumps(send_info)
            return (send_info, True)
        elif mode == "stop_task":
            flag = False
            for e in exec_task:
                if msg == e["task_id"]:
                    flag = True
                    stop_lock.acquire()
                    stop_task.append(msg)
                    stop_lock.release()
            if flag:
                send_info = {"mode": "ret_stop_task", "ui": ui , "info": {"task_id": msg, "info": "success"}}
            else:
                send_info = {"mode": "ret_stop_task", "ui": ui , "info": {"task_id": msg, "info": "failed"}}
            send_info = json.dumps(send_info)
            return (send_info, True)
        elif mode == "get_train_log_path":
            path = os.path.join(root, conf.config["train_log_path"], msg+".log")
            send_info = {"mode": "ret_train_log_path", "ui": ui , "info": path}
            send_info = json.dumps(send_info)
            return (send_info, True)
        elif mode == "get_server_log":
            send_info = {"mode": "ret_server_log", "ui": ui , "info": conf.config["server_log_path"]}
            send_info = json.dumps(send_info)
            return (send_info, True)

        else:
            return ("", False)
    except Exception as e:
        print(e)
    pass