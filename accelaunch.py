import yaml
import argparse
import os
import contextlib
from pathlib import Path

total_cached = 0
total_apps = 0
total_files = 0

def size_bytes(m_size_str):
    if "mb" in str(m_size_str).lower():
        return int(''.join(ch for ch in m_size_str if ch.isdigit())) * 1024 * 1024
    if "kb" in str(m_size_str).lower():
        return int(''.join(ch for ch in m_size_str if ch.isdigit())) * 1024
    if "b" in str(m_size_str).lower():
        return int(''.join(ch for ch in m_size_str if ch.isdigit()))
    else: return int(3000000)

def cache_file(fp, verb):
    try:
        with open(fp, 'br') as cachef:
            f = cachef.read()
            globals()['total_cached'] += fp.stat().st_size
            with contextlib.redirect_stdout(None):
                for line in f:
                    print(str(line).strip())
            if verb == True:
                print("Cached file: " + str(fp) + " (" + str(fp.stat().st_size) + "b)")
    except Exception as e:
        if verb == True:
            print(f"Error cacheing file {fp}: {e}")

def onestart(conffile):
    with open(conffile, 'r') as configf:
        configd = yaml.full_load(configf)
    file_size = size_bytes(str(configd.get('max_file_size')))
    print(f"Caching files up to size: {configd.get('max_file_size')} ({file_size} bytes)")
    apps = configd.get('cache_apps')
    globals()['total_apps'] = len(apps)
    print("Caching files for apps: " + ", ".join(apps))
    for ext in configd.get('cache_extensions'):
        for stub in configd.get('path_stubs'):
            for app in apps:
                for file_path in Path(stub).rglob('*' + str(ext)):
                    if file_path.is_file():
                        if app in file_path.parts:
                            if file_path.stat().st_size <= file_size:
                                cache_file(file_path, verb=args.verbose)
                                globals()['total_files'] += 1
                for file_path in Path(stub).glob("*"):
                    if file_path.is_file():
                        if app in file_path.parts:
                            if file_path.stat().st_size <= file_size:
                                if "." not in file_path.name:
                                    cache_file(file_path, verb=args.verbose)
                                    globals()['total_files'] += 1

def totals_summary():
    print("Total applications: " + str(total_apps) + " apps")
    print("Total files: " + str(total_files) + " files")
    print("Total cached data: " + str(round(total_cached / 1024 / 1024, 1)) + "mb")

print("Accelaunch - A boottime file cacher")
if os.geteuid() != 0:
    print("This program must be run as root. Exiting.")
    exit(1)
conffile = str()
command = str()
ap = argparse.ArgumentParser()
ap.add_argument("--config", "-c", help="Path to config file", default="/etc/accelaunch/config.yaml")
ap.add_argument("command", help="Prose argument", nargs='?')
ap.add_argument("--verbose", "-v", help="Enable verbose output", action="store_true")
args = ap.parse_args()
if args.config is not None:
    conffile = args.config
if args.command == "start":
    onestart(conffile)
    totals_summary()
    exit(0)
if args.command == "restart":
    os.sync()
    with open("/proc/sys/vm/drop_caches", 'w') as drop_caches_file:
        drop_caches_file.write('3\n')
    onestart(conffile)
    totals_summary()
    exit(0)
if args.command == "stop":
    print("Syncing disk and dropping caches...")
    os.sync()
    with open("/proc/sys/vm/drop_caches", 'w') as drop_caches_file:
        drop_caches_file.write('3\n')
    exit(0)
else:
    print("No valid arguments provided. Use --help for usage information.")
    exit(1)
