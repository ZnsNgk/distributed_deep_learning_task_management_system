from queue import Queue
import threading

wait_queue = Queue(0)   # 等待区任务队列，由交流线程放入数据，任务管理线程读取
visible_folder = []
task_lock = threading.Lock()
wait_task = []
exec_task = []
hist_task = []
stop_task = []  # 需要停止的任务
stop_lock = threading.Lock()