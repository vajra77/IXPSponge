import lockfile
from time import sleep
import daemon
import signal
import syslog
import json
import toml
import getopt
import sys

from ixpsponge.threads import Sweeper, Monitor
from ixpsponge.threads.tconfig import TConfig


def sig_shutdown(signum, frame):
    pass


def usage():
    print("Usage: xsponget -c <path_to_config_file>")


if __name__ == "__main__":

    config_file = "assets/xsponget.conf"

    opts, args = getopt.getopt(sys.argv[1:], "hc:", ["help", "config="])

    for opt, arg in opts:
        if opt == "--config":
            config_file = arg
        elif opt == "--help":
            usage()
            exit(0)
        else:
            print("Unhandled option %s" % opt, file=sys.stderr)
            usage()
            exit(1)

    try:
        config = TConfig(config_file)

    except FileNotFoundError:
        print("Configuration file not found", file=sys.stderr)
        usage()
        exit(1)

    with daemon.DaemonContext(
            pidfile=lockfile.FileLock(config.get('general', 'pid_file')),
            signal_map={
                signal.SIGTERM: sig_shutdown,
                signal.SIGTSTP: sig_shutdown,
                signal.SIGHUP: sig_shutdown,
            }):

        if config.get('sweeper', 'enabled'):
            sweeper_t = Sweeper(config)
            sweeper_t.start()

        if config.get('monitor', 'enabled'):
            monitor_t = Monitor(config)
            monitor_t.start()


