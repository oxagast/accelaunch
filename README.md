# AcceLaunch

## A boottime disk cache populator for frequently used apps

### Overview

Accelaunch is a Python utility designed to speed up application launch times by preloading frequently used application files into the system's disk cache at boot time. By reading application binaries, libraries, and related files into memory during system startup, subsequent launches of these applications can be significantly faster.

### Features

- **YAML-based configuration** - Simple, human-readable configuration file
- **Selective caching** - Cache specific applications and file types based on your needs
- **Size limits** - Configure maximum file size to cache, preventing memory waste
- **Path and extension filtering** - Target specific file extensions and directory paths
- **Cache management** - Start, stop, and restart commands with optional cache dropping
- **Verbose mode** - Detailed output for monitoring what's being cached
- **Statistics reporting** - Summary of total apps, files, and data cached

### Requirements

- Python 3.x
- PyYAML library
- psutil library
- logging library
- Linux operating system
- Root privileges

### Installation

1. Clone the repository:

```bash
git clone https://github.com/oxagast/accelaunch.git
cd accelaunch
```

2. Install dependencies:

```bash
sudo apt install python3-psutil python3-yaml
```

3. Run make to install:

```bash
make install
```

4. Initialize systemd:

```bash
sudo systemctl daemon-reload
sudo systemctl enable accelaunch
```

5. Skip to the Configuration section to set up your config file.

6. Lastly, reboot the computer to see Accelaunch in action!

### Configuration

Copy the example config to `/usr/local/etc/accelaunch/config.yaml` and edit it to your specific needs:

```yaml
# The maximum file size to cache. Files larger than this will be skipped.
max_file_size: "10MB"

# The applications to cache at boot time.
cache_apps:
  - firefox
  - chrome
  - vscode
  - python3

# Specific file extensions to cache.
cache_extensions:
  - .so      # Shared libraries
  - .py      # Python files
  - .bin     # Binaries

# Paths to check for the files in.
path_stubs:
  - /usr/lib
  - /usr/bin
  - /opt

# Files that should always be cached, regardless of other settings.
cache_files:
  - /usr/bin/firefox
  - /usr/bin/snap

# The log file location.  Opetional.
log_file: /var/log/accelaunch.log

# On stop or restart you can have Accelaunch drop the disk caches.  This is
# optional and not recommended, but is here for debugging or specific use cases.
# Don't set this to true unless you know what you are doing.
drop_caches_on_stop: false

# This should usually be set to 1, which drops pagecache only.  2 drops 
# dentries and inodes, and 3 drops all three.  This applies to the above setting.
drop_caches_level: 1
```

### Usage

If you installed per the instructions above, Accelaunch will run automatically at boot. You can also manage it using systemd
using the usual systemd start/stop/restart commands.

### License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

### Author

Marshall Whittaker

### Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
