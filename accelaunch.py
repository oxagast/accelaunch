#!/usr/bin/env python3
import yaml
import argparse
import os
import contextlib
from datetime import timedelta
from datetime import datetime
from pathlib import Path

total_cached = 0
total_apps = 0
total_files = 0

def ts():
    return f"{datetime.timestamp(datetime.now()):.2f}"


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
            if verb == True:
                print(str(ts()) + " Cached file: " + str(fp) + " (" + str(fp.stat().st_size) + "b)")
            with contextlib.redirect_stdout(None):
                for line in f:
                    print(str(line).strip())
    except Exception as e:
        if verb == True:
             print(str(ts()) + " Error cacheing file " + fp + ":" + e)

def onestart(conffile):
    with open(conffile, 'r') as configf:
        configd = yaml.full_load(configf)
    file_size = size_bytes(str(configd.get('max_file_size')))
    print(str(ts()) + " Caching files up to size: " + str(configd.get('max_file_size')) + "({file_size} bytes)")
    apps = configd.get('cache_apps')
    globals()['total_apps'] = len(apps)
    print(str(ts()) + " Caching files for apps: " + ", ".join(apps))
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
    for  extras_path in configd.get('extra_files'):
        extra = Path(extras_path)
        if extra.is_file():
            cache_file(extra, verb=args.verbose)
            globals()['total_files'] += 1

def totals_summary():
    print(str(ts()) + " Total applications: " + str(total_apps) + " apps")
    print(str(ts()) + " Total files: " + str(total_files) + " files")
    print(str(ts()) + " Total cached data: " + str(round(total_cached / 1024 / 1024, 1)) + "mb")

print("Accelaunch - A boottime file cacher")
if os.geteuid() != 0:
    print(str(ts()) + " This program must be run as root. Exiting.")
    exit(1)
conffile = str()
command = str()
ap = argparse.ArgumentParser()
ap.add_argument("--config", "-c", help="Path to config file", default="/usr/local/etc/accelaunch/config.yaml")
ap.add_argument("command", help="Command argument", nargs='?')
ap.add_argument("--verbose", "-v", help="Enable verbose output", action="store_true")
args = ap.parse_args()
if args.config is not None:
    conffile = args.config
with open(conffile, 'r') as configf:
        configd = yaml.full_load(configf)
        print(str(ts()) + " Config file " + str(conffile) + " loaded.")
drop_caches = configd.get('drop_caches_on_stop', False)
if configd.get('log_file') is not None:
    log_path = Path(configd.get('log_file'))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.touch(exist_ok=True)
    logf = open(log_path, 'a')
    os.dup2(logf.fileno(), 1)
    os.dup2(logf.fileno(), 2)
print(str(ts()) + " Logging to file: " + str(configd.get('log_file')))
if args.command == "start":
    onestart(conffile)
    totals_summary()
    exit(0)
if args.command == "restart":
    if drop_caches:
        os.sync()
        print(str(ts()) + " Disk synced. Dropping caches...")
        with open("/proc/sys/vm/drop_caches", 'w') as drop_caches_file:
            drop_caches_file.write('3\n')
    onestart(conffile)
    totals_summary()
    exit(0)
if args.command == "stop":
    if drop_caches:
        os.sync()
        print(str(ts()) + " Disk synced. Dropping caches...")
        with open("/proc/sys/vm/drop_caches", 'w') as drop_caches_file:
            drop_caches_file.write('3\n')
    else:
        print(str(ts()) + " Drop caches on stop is disabled in config. Not dropping caches.")
    exit(0)
else:
    print(str(ts()) + " No valid arguments provided. Use --help for usage information.")
    exit(1)
