import sys
import subprocess as sp
from datetime import datetime
from dateutil import parser
from time import sleep


def get_configuration(all_services):
    # In case the time format has spaces
    arg = " ".join(sys.argv[1:])
    decoding_dict = {
        r"x2b": "+",
        r"x3d": "=",
        r"x3a": ":",
        r"x3b": ";",
        r"x2c": ",",
        r"x20": " ",
    }

    for key, value in decoding_dict.items():
        arg = arg.replace(key, value)

    try:
        service, time = arg.split("=", maxsplit=1)
    except ValueError:
        print(f"NOTE: Service `{arg}` does not have a stale timeout. Assuming 10 sec to be the stale timeout")
        service = arg
        time = "10s"

    # Cleanup the passed service name and stale timeout
    permissible_suffixes = [
        ".service",
        ".socket",
        ".device",
        ".mount",
        ".automount",
        ".swap",
        ".target",
        ".path",
        ".timer",
        ".slice",
        ".scope",
    ]
    if not any(service.endswith(x) for x in permissible_suffixes):
        service += ".service"

    if service not in all_services:
        print(f"ERROR: Service `{service}` does not exist in systemd's unit-list.")
        sys.exit(1)

    if time.isdigit():
        time = time + "s"
    try:
        t = parser.parse(time)
    except parser._parser.ParserError:
        print(f"ERROR: Service `{service}` has a stale timeout `{time}` that is not parse-able.")
        sys.exit(1)
    time_limit = (t.hour * 60 + t.minute) * 60 + t.second

    return service, time_limit


if len(sys.argv) == 1:
    print("Usage: python3 -m sdlogwatchdog service=staletimeout")
    sys.exit(1)

all_services = [
    x.replace("●", " ").split()[0]
    for x in sp.check_output("systemctl list-units --all --type=service".split()).decode().split("\n")
    if x
]

service, time_limit = get_configuration(all_services)

max_digits = len(str(time_limit)) + 1
upper_cap = int("9" * max_digits)
print(f"Service: {service}, Permissible Staleness in seconds: {time_limit}")
print("Staleness values printed below are current_staleness / permissible_staleness * 100")
print("Processes are restarted if the staleness values exceed 100%.")
while True:
    journalctl_command = f"journalctl -u {service} -n 1 --no-pager -o short-iso".split()
    last_log_line = [x for x in sp.check_output(journalctl_command).decode().split("\n") if x][-1]
    try:
        last_log_t = datetime.strptime(last_log_line[:24], "%Y-%m-%dT%H:%M:%S%z")
        time_since_last_log = min((datetime.now(tz=last_log_t.tzinfo) - last_log_t).seconds, upper_cap)
    except ValueError:  # Ex: if there are no journalctl logs for the service
        time_since_last_log = upper_cap

    to_restart = time_since_last_log > time_limit
    staleness = time_since_last_log / time_limit * 100
    print(f"Service={service:20}  |  Restarting={to_restart:1}  |  CurrentStaleness={staleness:.1f}%")
    if to_restart:
        sp.call(f"systemctl restart {service}".split())

    sleep(time_limit // 2)
