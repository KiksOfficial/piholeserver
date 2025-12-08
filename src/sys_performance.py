# sys_performance.py
import psutil
import subprocess
import platform
import os # Vajalik, sest temperatuuri lugemise tee võib erineda

def get_cpu_temp():
    """Loeb CPU temperatuuri, kohandudes vastavalt OS-ile (Linux/macOS)."""
    os_name = platform.system()
    
    # 1. macOS (kasutab applesmc andurit või htop/iStats stiilis käske)
    if os_name == "Darwin":
        try:
            # Enamasti on vaja kolmanda osapoole tööriista (nt osx-cpu-temp) või spetsiifilist Pythoni moodulit
            # Kuid lihtsa lahendusena on parim kasutada psutil (kui see pakub andurit)
            temps = psutil.sensors_temperatures()
            if 'cpu_thermal' in temps and temps['cpu_thermal']:
                 # Võib olla erinev nimi, nt 'cpu_temp'
                 return temps['cpu_thermal'][0].current
            elif 'cpu-package' in temps and temps['cpu-package']:
                 return temps['cpu-package'][0].current
            else:
                 return "macOS N/A" # psutil ei leia sensorit
        except Exception:
            return "macOS N/A"
            
    # 2. Linux (Raspberry Pi/teised)
    elif os_name == "Linux":
        try:
            # Raspberry Pi standardne tee
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp_raw = f.read()
                return round(int(temp_raw) / 1000.0, 1)
        except Exception:
            # Alternatiivne meetod (nt vcgencmd vanematel Pi mudelitel)
            try:
                output = subprocess.check_output("vcgencmd measure_temp", shell=True, text=True)
                temp_str = output.split('=')[1].split("'")[0]
                return float(temp_str)
            except Exception:
                return "Linux N/A"
                
    else:
        # Muud OS-id või tundmatu olukord
        return "N/A (OS)"

def get_cpu_usage():
    """Tagastab CPU kasutuse protsentides (töötab nii Macis kui Linuxis)."""
    # psutil.cpu_percent töötab platvormiüleselt
    return psutil.cpu_percent(interval=None) 

def get_ram_info():
    """Tagastab RAM-i kasutuse (GB) ja protsendi (töötab platvormiüleselt)."""
    ram = psutil.virtual_memory()
    return {
        'used_gb': round(ram.used / (1024**3), 2),
        'total_gb': round(ram.total / (1024**3), 2),
        'percent': ram.percent
    }
