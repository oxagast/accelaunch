#!/usr/bin/env python3
import yaml
import argparse
import os
import contextlib
import psutil
import sys
import logging
from datetime import timedelta
from datetime import datetime
from pathlib import Path
version = "1.2.1"
total_apps = 0
total_files = 0

def ts():
    return f"{datetime.timestamp(datetime.now()):.4f}"


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
            if verb == True:
                logger.debug("Cached file: " + str(fp) + " (" + str(fp.stat().st_size) + "b)")
            with contextlib.redirect_stdout(None):
                for line in f:
                    print(str(line).strip())
    except Exception as e:
        if verb == True:
             logger.warning("Error cacheing file " + fp + ":" + e)

def onestart(conffile):
    with open(conffile, 'r') as configf:
        configd = yaml.full_load(configf)
    file_size = size_bytes(str(configd.get('max_file_size')))
    logger.debug("Caching files up to size: " + str(configd.get('max_file_size')) + "(" + str(file_size) + " bytes)")
    apps = configd.get('cache_apps')
    globals()['total_apps'] = len(apps)
    logger.info("Caching files for apps: " + ", ".join(apps))
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
    logger.info("Total applications: " + str(total_apps) + " apps")
    logger.info("Total files: " + str(total_files) + " files")
    logger.info("Total cached data: " + str(round(psutil.virtual_memory().cached / (1024**3), 2)) + "gb")
    percent_cached = round((psutil.virtual_memory().cached / psutil.virtual_memory().total) * 100, 2)
    logger.info("Percentage of total system memory cached: " + str(percent_cached) + "%")

pst = datetime.now()
logger = logging.getLogger('accelaunch')
logger.info("Starting AcceLaunch...")
if os.geteuid() != 0:
    logger.warning("This program must be run as root. Exiting.")
    logger.info("Total processing time: " + str(timedelta(seconds=(datetime.now() - pst).seconds)))
    exit(1)
conffile = str()
command = str()
ap = argparse.ArgumentParser()
ap.add_argument("--config", "-c", help="Path to config file", default="/usr/local/etc/accelaunch/config.yaml")
ap.add_argument("command", help="Command argument", nargs='?')
ap.add_argument("--verbose", "-v", help="Enable verbose output", action="store_true")
ap.add_argument("--very-verbose", "-V", help="Enable very verbose output", action="store_true")
ap.add_argument("--version", "-i", help="Show version information", action="store_true")

args = ap.parse_args()
if args.config is not None:
    conffile = args.config
with open(conffile, 'r') as configf:
        configd = yaml.full_load(configf)
drop_caches = configd.get('drop_caches_on_stop', False)
drop_level = configd.get('drop_caches_level', 1)
if configd.get('log_file') is not None:
    logger.setLevel(logging.DEBUG)
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setLevel(logging.INFO)
    f_handler = logging.FileHandler(configd.get('log_file'))
    f_handler.setLevel(logging.DEBUG) # Log all debug messages to the file
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
logger.info("AcceLaunch started.")
logger.debug("Configuration file: " + str(conffile))
logger.debug("Command: " + str(args.command))
logger.debug("Logging to file: " + str(configd.get('log_file')))
if args.command == "start":
    logger.info("Starting caching process...")
    onestart(conffile)
    totals_summary()
    logger.info("Total processing time: " + str(timedelta(seconds=(datetime.now() - pst).seconds)))
    exit(0)
if args.command == "restart":
    if drop_caches:
        os.sync()
        logger.warning("Disk synced. Dropping caches.")
        with open("/proc/sys/vm/drop_caches", 'w') as drop_caches_file:
            drop_caches_file.write(str(drop_level) + '\n')
    onestart(conffile)
    totals_summary()
    logger.info("Total processing time: " + str(timedelta(seconds=(datetime.now() - pst).seconds)))
    exit(0)
if args.command == "stop":
    if drop_caches:
        os.sync()
        logger.warning("Disk synced. Dropping caches...")
        with open("/proc/sys/vm/drop_caches", 'w') as drop_caches_file:
            drop_caches_file.write(str(drop_level) + '\n')
    else:
        logger.warning("Drop caches on stop is disabled in config. Not dropping caches.")
    percent_cached = round((psutil.virtual_memory().cached / psutil.virtual_memory().total) * 100, 2)
    logger.info("Percentage of total system memory cached: " + str(percent_cached) + "%")
    logger.info("Total processing time: " + str(timedelta(seconds=(datetime.now() - pst).seconds)))
    exit(0)
else:
    logging.warning("No valid arguments provided. Use --help for usage information.")
    logger.info("Total processing time: " + str(timedelta(seconds=(datetime.now() - pst).seconds)))
    exit(1)
