import yaml
from pathlib import Path

def size_bytes(m_size_str):
    if "mb" in str(m_size_str).lower():
        return int(''.join(ch for ch in m_size_str if ch.isdigit())) * 1024 * 1024
    if "kb" in str(m_size_str).lower():
        return int(''.join(ch for ch in m_size_str if ch.isdigit())) * 1024
    if "b" in str(m_size_str).lower():
        return int(''.join(ch for ch in m_size_str if ch.isdigit()))
    else: return int(3000000)

def cache_file(fp):
    try:
        with open(fp, 'br') as cachef:
            cachef.read();
            print("Cached file: " + str(fp) + " (" + str(fp.stat().st_size) + "b)")
    except Exception as e:
        print(f"Error cacheing file {fp}: {e}")


print("Accelaunch - A boottime file cacher")
with open('config.yml', 'r') as configf:
    configd = yaml.full_load(configf)
file_size = size_bytes(str(configd.get('max_file_size')))
print(f"Caching files up to size: {configd.get('max_file_size')} ({file_size} bytes)")
apps = configd.get('cache_apps')
print("Caching files for apps: " + ", ".join(apps))
for ext in configd.get('cache_extensions'):
    for stub in configd.get('path_stubs'):
        for app in apps:
            for file_path in Path(stub).rglob('*' + ext):
                if file_path.is_file():
                    if app in file_path.parts:
                        if file_path.stat().st_size <= file_size:
                            cache_file(file_path)
            for file_path in Path(stub).glob("*"):
                if file_path.is_file():
                    if app in file_path.parts:
                        if file_path.stat().st_size <= file_size:
                            if "." not in file_path.name:
                                cache_file(file_path)
