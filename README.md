# AcceLaunch
## A boottime disk cache populator for frequently used applications on Linux systems.

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
- Linux operating system (requires `/proc/sys/vm/drop_caches`)
- Root privileges

### Installation

1. Clone the repository:
```bash
git clone https://github.com/oxagast/accelaunch.git
cd accelaunch
```

2. Install dependencies:
```bash
pip install pyyaml
```

3. Create the configuration directories:
```bash
sudo mkdir -p /usr/local/etc/accelaunch /usr/local/lib/accelauch
```

4. Copy the scripts to a system location:
```bash
sudo cp accelaunch.py /usr/local/bin/accelaunch
sudo cp config.yaml /usr/local/etc/accelaunch/config.yaml
sudo cp accelaunch.service /usr/lib/systemd/system/accelaunch.service
sudo chmod +x /usr/local/bin/accelaunch
```

5. Initialize systemd:
```bash
sudo systemctl daemon-reload
sudo systemctl enable accelaunch
```

### Configuration

Create a configuration file at `/usr/local/etc/accelaunch/config.yaml` with the following structure:

```yaml
# Maximum file size to cache
max_file_size: "10MB"

# Applications to cache (directory names)
cache_apps:
  - firefox
  - chrome
  - vscode
  - python3

# File extensions to cache
cache_extensions:
  - .so      # Shared libraries
  - .py      # Python files
  - .bin     # Binaries

# Base paths to search
path_stubs:
  - /usr/lib
  - /usr/bin
  - /opt

# Drop caches on stop/restart
drop_caches_on_stop: true
```

### Usage

Accelaunch must be run with root privileges:

```bash
systemctl start accelaunch
```

### License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

### Author

Marshall Whittaker

### Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.
