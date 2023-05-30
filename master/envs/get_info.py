import sys
import psutil
import argparse
import GPUtil
# import setproctitle
import json
import time
# from pynvml import *
import traceback


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", type=int, default=3, help="display interval")
    args = parser.parse_args()
    return args


def main():
    # setproctitle.setproctitle('python gen_hw_usage')
    args = parse_args()

    if args.l < 1:
        args.l = 1
        
    previous_net = None
    
    enable_nvidia = False
    try:
        nvmlInit()
        deviceCount = nvmlDeviceGetCount()
    except:
        enable_nvidia = False
    # print(deviceCount)
    while True:
        try:
            res = {}
            res['cpu'] = psutil.cpu_percent(percpu=True)
            res['cpu_total'] = psutil.cpu_percent()
            res['ram'] = psutil.virtual_memory()._asdict()
            current_net = psutil.net_io_counters(pernic=True)
            if_info = psutil.net_if_stats()
            
            res['net'] = []
            
            for if_stat in if_info:
                if if_info[if_stat].speed > 0:
                    res['net'].append({
                        'id': if_stat,
                        'bandwidth': if_info[if_stat].speed, # Mbps
                        'recv_bytes_ps': (current_net[if_stat].bytes_recv - previous_net[if_stat].bytes_recv) * 8 / args.l if previous_net is not None else 0, # bps
                        'sent_bytes_ps': (current_net[if_stat].bytes_sent - previous_net[if_stat].bytes_sent) * 8 / args.l if previous_net is not None else 0 # bps
                    })
            
            previous_net = current_net
            
            # processing
            # res['process'] = [{**{'cpu': proc.cpu_percent(), 'vms': proc.memory_info().vms}, **proc.info} for proc in psutil.process_iter(['pid', 'name', 'username']) if proc.status() != 'idle']
            try: 
                res['gpu'] = [{'id': gpu.id, 'load': gpu.load, 'mem_used': gpu.memoryUsed, 'mem_total': gpu.memoryTotal, 'mem_util': gpu.memoryUtil} for gpu in GPUtil.getGPUs()]
            except ValueError:
                res['gpu'] = []
                enable_nvidia = False

            if enable_nvidia:
                
                gpu_proc = []
                for device_id in range(deviceCount):
                    hd = nvmlDeviceGetHandleByIndex(device_id)
                    cps = nvmlDeviceGetComputeRunningProcesses(hd) + nvmlDeviceGetGraphicsRunningProcesses(hd)

                    for ps in cps :
                        pp = ps.pid
                        name = nvmlSystemGetProcessName(ps.pid).decode("utf-8") 
                        proc = psutil.Process(pp)

                        gpu_proc.append({'name': name, 'pid': pp, 'mem_gpu': ps.usedGpuMemory, 'cpu': proc.cpu_percent(), 'ram': proc.memory_info().vms, 'username': proc.username()})

                res['gpu_proc'] = gpu_proc

            print(json.dumps(res), flush=True)
            time.sleep(args.l)
        except:
            traceback.print_exc()
            break
    
    if enable_nvidia:
        nvmlShutdown()


if __name__ == '__main__':
    main()
