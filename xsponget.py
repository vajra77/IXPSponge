from ixpsponge.threads import Sweeper, Monitor, TConfig
import lockfile
import daemon
import signal
import syslog
import getopt
import sys


ALL_THREADS = []


def sig_shutdown(signum, frame):
    for thread in ALL_THREADS:
        thread.halt()

    for thread in ALL_THREADS:
        thread.join()

    exit(0)


def usage():
    print("Usage: xsponget -c <path_to_config_file>")


if __name__ == "__main__":

    config_file = "assets/xsponget.conf"

    opts, args = getopt.getopt(sys.argv[1:], "hc:", ["help", "config="])

    for opt, arg in opts:
        if opt == "-c":
            config_file = arg
        elif opt == "-h":
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
            syslog.syslog(syslog.LOG_INFO, "Sweeper thread is enabled")
            sweeper_t = Sweeper(config)
            ALL_THREADS.append(sweeper_t)
            sweeper_t.start()

        if config.get('monitor', 'enabled'):
            syslog.syslog(syslog.LOG_INFO, "Monitor thread is enabled")
            monitor_t = Monitor(config)
            ALL_THREADS.append(monitor_t)
            monitor_t.start()

        # join all threads
        for t in ALL_THREADS:
            t.join()





