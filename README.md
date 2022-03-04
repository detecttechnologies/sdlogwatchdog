# Systemd Log Watchdog

Staleness-based watchdog for systemd services. Staleness is assessed based on recency of log messages

## Intro

A watchdog for any systemd service that allows detecting processes/services/units that have frozen. It restarts them based on staleness/oldness of log messages. This is strictly designed to work for Linux based systems, and has only been tested on Ubuntu. However, it should work for other Linux-based OSes too.

`systemd` unit-configuration does allow the following internally:
* `Restart`, `RestartSec`: Restarts the service by assessing the "deadness" of the service
* `WatchDogSec`: Restarts the service by assessing the "liveness" of the service

However, these configurations also come with their fair share of limitations. `Restart` relies on the processes exiting for `systemd` to act upon it. And the inbuilt `WatchDog` of `systemd` requires the service to actively send out signals (called `sd_notify`) for systemd to NOT kill it. Sometimes though, we just want a simple solution that can restart freezing processes which have STOPPED sending log messages too. Furthermore, systemd's inbuilt Watchdog only comes with systemd version > 240, which is not available in earlier OS versions like Ubuntu 18.

## Installation
```bash
sudo -H pip3 install git+https://github.com/detecttechnologies/sdlogwatchdog.git@main
```
**NOTE:** As the program adds a systemd-service, the pip-installation **has** to be run with `sudo` as mentioned above. It is important that this is followed even when using conda/venv.


## Usage

The syntax for usage is:
```bash
sudo systemctl start sdlogwatchdog@"service1=staletimeout1".service
```

The `staletimeout` is the maximum permissible time for which the service can be left alive without it being killed and restarted. It supports any format for time specification supported by `python-dateutil`. Additionally, if no units are passed (ref: examples below), then it takes the units as seconds

### Examples:
* Let us say you want to monitor a systemd-service called `my-program1.service`. If it doesn't throw any log messages for 25 seconds, you would like it to be restarted. Then, the command you need to run is
    ```bash
    sudo systemctl start sdlogwatchdog@"my-program1=25".service
    # OR 
    sudo systemctl start sdlogwatchdog@"my-program1=25s".service
    ```
* Suppose you want to monitor a unit called `my-program2.service`, with a staleness timeout of 1 day , 3 hours, and 10 minutes:
    ```bash
    sudo systemctl start sdlogwatchdog@"my-program2=1d 3h 10m".service
    ```