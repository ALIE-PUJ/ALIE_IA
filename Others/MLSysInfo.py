import torch
import psutil
import platform
import GPUtil

# pip install torch psutil gputil

def get_device_info():
    print("="*40, "System Information", "="*40)
    
    # General system information
    print(f"System: {platform.system()}")
    print(f"Node Name: {platform.node()}")
    print(f"Release: {platform.release()}")
    print(f"Version: {platform.version()}")
    print(f"Machine: {platform.machine()}")
    print(f"Processor: {platform.processor()}")
    print(f"Architecture: {platform.architecture()[0]}")

    # CPU information
    print("\n" + "="*40, "CPU Information", "="*40)
    cpu_count = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    print(f"Physical cores: {psutil.cpu_count(logical=False)}")
    print(f"Total cores: {cpu_count}")
    print(f"Max Frequency: {cpu_freq.max:.2f}Mhz")
    print(f"Min Frequency: {cpu_freq.min:.2f}Mhz")
    print(f"Current Frequency: {cpu_freq.current:.2f}Mhz")
    print(f"CPU Usage per Core:")
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
        print(f"Core {i}: {percentage}%")
    print(f"Total CPU Usage: {psutil.cpu_percent()}%")

    # RAM information
    print("\n" + "="*40, "Memory Information", "="*40)
    svmem = psutil.virtual_memory()
    print(f"Total: {get_size(svmem.total)}")
    print(f"Available: {get_size(svmem.available)}")
    print(f"Used: {get_size(svmem.used)}")
    print(f"Percentage: {svmem.percent}%")

    # Disk information
    print("\n" + "="*40, "Disk Information", "="*40)
    partitions = psutil.disk_partitions()
    for partition in partitions:
        print(f"Device: {partition.device}")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            print(f"  Total Size: {get_size(partition_usage.total)}")
            print(f"  Used: {get_size(partition_usage.used)}")
            print(f"  Free: {get_size(partition_usage.free)}")
            print(f"  Percentage: {partition_usage.percent}%")
        except PermissionError:
            continue
    
    # GPU information (if CUDA is available)
    print("\n" + "="*40, "GPU Information", "="*40)
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        num_gpus = torch.cuda.device_count()
        print(f"Number of available GPUs: {num_gpus}")
        for i in range(num_gpus):
            gpu_name = torch.cuda.get_device_name(i)
            vram_total = torch.cuda.get_device_properties(i).total_memory
            vram_total_gb = vram_total / (1024 ** 3)
            print(f"GPU {i}: {gpu_name}")
            print(f"  Total VRAM: {vram_total_gb:.2f} GB")
            print(f"  CUDA Device: {torch.cuda.current_device()}")
        print("\n")
    else:
        print("CUDA is not available. Using CPU.")

    # Detailed GPU information using GPUtil
    gpus = GPUtil.getGPUs()
    if gpus:
        print("="*40, "Detailed GPU Information", "="*40)
        for gpu in gpus:
            print(f"GPU {gpu.id}: {gpu.name}")
            print(f"  Load: {gpu.load * 100:.1f}%")
            print(f"  Free Memory: {gpu.memoryFree}MB")
            print(f"  Used Memory: {gpu.memoryUsed}MB")
            print(f"  Total Memory: {gpu.memoryTotal}MB")
            print(f"  Temperature: {gpu.temperature} °C")
            print(f"  UUID: {gpu.uuid}")
            print("\n")
    else:
        print("No GPUs detected using GPUtil.")

    # Final CUDA compatibility message
    if cuda_available:
        print("\nThis device is CUDA compatible.")
    else:
        print("\nThis device is NOT CUDA compatible.")

# Helper function to convert bytes to a human-readable format
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor

if __name__ == "__main__":
    get_device_info()
