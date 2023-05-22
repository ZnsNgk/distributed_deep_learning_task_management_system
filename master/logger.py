import datetime
import os
import threading

log_lock = threading.Lock()

def log(string, file_name, need_time=True):
    save_str = ''
    if need_time:
        save_str = str(datetime.datetime.now().replace(microsecond=0)) + ' :'
    save_str = save_str + string
    print(save_str)
    log_path = os.path.join(file_name)
    log_lock.acquire()
    with open(log_path,'a') as f:
        f.write(save_str+"\n")
    log_lock.release()