#!/usr/bin/env python3
import yaml
import argparse
import os
import psutil
import sys
import logging
import signal
from datetime import timedelta
from datetime import datetime
from pathlib import Path
version = "1.3"
total_apps = 0
total_files = 0
CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

def sigint_handler(signum, frame):
    print(ERASE_LINE, end="")
    print(CURSOR_UP_ONE + "celaunch - INFO - AcceLaunch started.")
    logger.critical("SIG(" + str(signum) + ") receieved, exiting prematurely...")
    if args.command == "start" or args.command == "restart":
        totals_summary(decp,prerunmem)
    cached_summary(decp)
    logger.info(process_time(pst))
    logging.shutdown()
    exit(1)


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
            type(f)
            if verb and verb >= 2:
                logger.debug("Cached file: " + str(fp) + " (" + str(fp.stat().st_size) + "b)")
    except Exception as e:
        if verb and verb >= 2:
             logger.error("Error cacheing file " + fp + ":" + e)

def onestart(conffile):
    with open(conffile, 'r') as configf:
        configd = yaml.full_load(configf)
    file_size = size_bytes(str(configd.get('max_file_size')))
    if args.verbose and args.verbose >= 1:
        logger.debug("Caching files up to size: " + str(configd.get('max_file_size')) + " (" + str(file_size) + " bytes)")
    apps = configd.get('cache_apps')
    globals()['total_apps'] = len(apps)
    if args.verbose and args.verbose >= 1:
        logger.info("Caching files for apps: " + ", ".join(apps))
    if configd.get("skip_files") is None:
        skip = []
    else:
        skip = configd.get("skip_files")
    for ext in configd.get('cache_extensions'):
        for stub in configd.get('path_stubs'):
            for app in apps:
                for file_path in Path(stub).rglob('*' + str(ext)):
                    if file_path.is_file() and app in file_path.parts and file_path.stat().st_size <= file_size and file_path.as_posix() not in skip:
                        skip.append(file_path.as_posix())
                        cache_file(file_path, verb=args.verbose)
                        globals()['total_files'] += 1
                for file_path in Path(stub).glob("*"):
                    if file_path.is_file() and app in file_path.parts and file_path.stat().st_size <= file_size and file_path.as_posix() not in skip:
                        if "." not in file_path.name:
                            skip.append(file_path.as_posix())
                            cache_file(file_path, verb=args.verbose)
                            globals()['total_files'] += 1
    for  file_path in configd.get('cache_files'):
        file = Path(file_path)
        if file.is_file():
            if file not in skip:
                skip.append(file.as_posix())
                cache_file(file, verb=args.verbose)
                globals()['total_files'] += 1

def cache_dropper(level):
    logger.warning("Dropping caches is usualy used for debugging purposes only. Avoid using this in production environments.")
    if level > 1:
        logger.error("Dropping dentries and inodes as per config, but there is not a good reason to do this.  If you must, use:\n                       drop_caches_level: 1")
    os.sync()
    if args.verbose and args.verbose >= 1:
        logger.warning("Disk synced. Dropping caches.")
    with open("/proc/sys/vm/drop_caches", 'w') as drop_caches_file:
        drop_caches_file.write(str(level) + '\n')

def cached_summary(vmdc):
    percent_cached = round((psutil.virtual_memory().cached / psutil.virtual_memory().total) * 100, vmdc)
    logger.info("Percentage of total system memory cached: " + str(percent_cached) + "%")

def totals_summary(dp,prerunm):
    logger.info("Total applications: " + str(total_apps) + " apps")
    logger.info("Total files: " + str(total_files) + " files")
    vmcached_gb = round(psutil.virtual_memory().cached / (1024**3), dp)
    logger.info("Total cached data: " + str(vmcached_gb) + "gb")

def process_time(start_time):
    return("Total processing time: " + str(timedelta(seconds=(datetime.now() - start_time).seconds)))

def help_message():
    help_text = "\n                AcceLaunch " + version + "\n\n"
    help_text += " Usage: accelaunch.py [options] <command>\n\n"
    help_text += " Commands:\n"
    help_text += "   start         Start the caching process\n"
    help_text += "   restart       Restart the caching process\n"
    help_text += "   stop          Stop the caching process\n"
    help_text += "   help          Show this help message\n\n"
    help_text += " Options:\n"
    help_text += "   -c, --config <path>      Path to config file (default: /usr/local/etc/accelaunch/config.yaml)\n"
    help_text += "   -v, --verbose            Enable verbose output\n"
    help_text += "   -V, --version            Show version information\n"
    print(help_text)

pst = datetime.now()
signal.signal(signal.SIGINT, sigint_handler)
prerunmem = psutil.virtual_memory().cached
decp = 1
logger = logging.getLogger('accelaunch')
logger.info("Starting AcceLaunch...")
if os.geteuid() != 0:
    logger.critical("This program must be run as root. Exiting.")
    logger.info(process_time(pst))
    logging.shutdown()
    exit(1)
conffile = str()
command = str()
ap = argparse.ArgumentParser()
ap.add_argument("--config", "-c", help="Path to config file", default="/usr/local/etc/accelaunch/config.yaml")
ap.add_argument("command", help="Command argument", nargs='?')
ap.add_argument("--verbose", "-v", help="Enable verbose output", action="count", default=0)
ap.add_argument("--version", "-V", help="Show version information", action="store_true")
args = ap.parse_args()
if args.config is not None:
    conffile = args.config
try:
    with open(conffile, 'r') as configf:
        configd = yaml.full_load(configf)
except FileNotFoundError:
    logger.warning("Configuration file not found: " + str(conffile) + ". Exiting.")
    logger.info(process_time(pst))
    logging.shutdown()
    exit(1)
except IOError as e:
    logger.warning("Error reading configuration file: " + str(e) + ". Exiting.")
    logger.info(process_time(pst))
    logging.shutdown()
    exit(1)
drop_caches = configd.get('drop_caches_on_stop', False)
drop_level = configd.get('drop_caches_level', 1)
if configd.get('log_file') is not None:
    logger.setLevel(logging.DEBUG)
    c_handler = logging.StreamHandler(sys.stdout)
    if args.verbose and args.verbose >= 1:
        c_handler.setLevel(logging.DEBUG)
    else:
        c_handler.setLevel(logging.INFO)
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)
    if os.access(configd.get('log_file'), os.W_OK):
        f_handler = logging.FileHandler(configd.get('log_file'))
        f_handler.setLevel(logging.DEBUG) # Log all debug messages to the file
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)
    else:
        logger.warning("Log file is not writable: " + str(configd.get('log_file')) + ". Continuing without file logging.")
logger.info("AcceLaunch started.")
logger.debug("Configuration file: " + str(conffile))
if configd.get('cache_extensions') is None or configd.get('path_stubs') is None or configd.get('cache_apps') is None:
    logger.critical("Configuration file is missing required fields. Exiting.")
    logger.info(process_time(pst))
    logging.shutdown()
    exit(1)
if args.version:
    logger.info("AcceLaunch v" + version)
    exit(0)
if args.command == "help" or args.command is None:
    help_message()
    exit(1)
if args.command == "start":
    if args.verbose and args.verbose >= 1:
        logger.info("Caching in progress...")
    onestart(conffile)
    totals_summary(decp,prerunmem)
    cached_summary(decp)
    logger.info(process_time(pst))
    logging.shutdown()
    exit(0)
if args.command == "restart":
    if drop_caches and drop_level in [1, 2, 3]:
        cache_dropper(drop_level)
    else:
        if args.verbose and args.verbose >= 1:
            logger.debug("Drop caches on restart is disabled in config. Not dropping caches.")
    onestart(conffile)
    totals_summary(decp,prerunmem)
    cached_summary(decp)
    logger.info(process_time(pst))
    logging.shutdown()
    exit(0)
if args.command == "stop":
    if drop_caches and drop_level in [1, 2, 3]:
        cache_dropper(drop_level)
    else:
        if args.verbose and args.verbose >= 1:
            logger.debug("Drop caches on stop is disabled in config. Not dropping caches.")
    cached_summary(decp)
    logger.info(process_time(pst))
    logging.shutdown()
    exit(0)
else:
    logger.critical("No valid arguments provided. Use --help for usage information.")
    logger.info(process_time(pst))
    logging.shutdown()
    exit(1)

