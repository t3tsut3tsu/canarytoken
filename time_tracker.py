import time

def execution_time(start_time, section_name):
    end_time = time.perf_counter()
    exec_time = end_time - start_time
    print(f"{section_name}: {exec_time:.6f} sec")
    return end_time