# -*- coding: utf-8 -
import errno
import os
import select
import signal
import sys
import time
import platform
import traceback
import pwd
import os.path
import fcntl
from subprocess import Popen
import json
import configparser
import shlex
import argparse
from basepy.log import logger


def run_manager():
    parser = argparse.ArgumentParser(prog="callpy-manager")
    parser.add_argument("command", help="run from manage.init config", choices=["run", "list"])
    args = parser.parse_args()
    manager = ProcessManager()
    if args.command == 'run':
        manager.run()
    elif args.command == 'list':
        manager.list()
    else:
        parser.print_help()


class Process(object):
    def __init__(self, name, cmdline, doc='', number=1):
        self.name = name
        self.number = number
        self.doc = doc
        self.processes = {}
        self.cmd = shlex.split(cmdline)
        self.start_failed = 0

    def init_process(self):
        for i in range(self.number):
            p = Popen(self.cmd, cwd=os.getcwd())
            self.processes[i+1] = {'process':p, 'started':time.time()}
            logger.info('Process [{}] [pid={}] started.'.format(self.name, p.pid))

    def poll(self):
        for i in range(self.number):
            procinfo = self.processes[i+1]
            p = procinfo['process']
            if procinfo.get('returncode') != None:
                continue
            p.poll()
            if p.returncode != None:
                ended = time.time()
                if ended - procinfo['started'] <= 3:
                    logger.error('processes<%s:%s>, start failed, exit too quickly'%(self.name, i+1))
                    procinfo['status'] = 'start_failed'
                    procinfo['returncode'] = p.returncode
                    self.start_failed += 1
                else:
                    logger.error('processes<%s:%s>, exit:%s, will restart.'%(self.name, i+1, p.returncode))
                    self.reinit_process(i+1)

    def reinit_process(self, index):
        p = Popen(self.cmd, cwd=os.getcwd())
        self.processes[index] = {'process':p, 'started':time.time()}


    def terminate(self):
        for i in range(self.number):
            procinfo = self.processes[i+1]
            if procinfo.get('returncode') != None:
                continue
            p = procinfo['process']
            p.terminate()

    def kill(self):
        for i in range(self.number):
            procinfo = self.processes[i+1]
            if procinfo.get('returncode') != None:
                continue
            p = procinfo['process']
            p.kill()



def close_on_exec(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
    flags |= fcntl.FD_CLOEXEC
    fcntl.fcntl(fd, fcntl.F_SETFD, flags)


def set_non_blocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)


class ProcessManager(object):
    SIG_QUEUE = []
    SIGNALS = [getattr(signal, "SIG%s" % x) \
            for x in "HUP QUIT INT TERM".split()]
    SIG_NAMES = dict(
        (getattr(signal, name), name[3:].lower()) for name in dir(signal)
        if name[:3] == "SIG" and name[3] != "_"
    )

    def __init__(self):
        self.conf = []
        self.load_config()
        self.processes = {}
        self.load_process()
        self.init_signals()

    def load_config(self):
        with open('manager.ini') as f:
            config = configparser.ConfigParser(allow_no_value=True)
            config.read_string(f.read())
            for section in config.sections():
                if not section.startswith("program:"):
                    continue
                name = section[len("program:"):]
                self.conf.append((name, dict(config[section])))

    def init_signals(self):
        self.PIPE = pair = os.pipe()
        for p in pair:
            set_non_blocking(p)
            close_on_exec(p)

        # intialiatze all signals
        [signal.signal(s, self.signal) for s in self.SIGNALS]


    def signal(self, sig, frame):
        if len(self.SIG_QUEUE) < 5:
            self.SIG_QUEUE.append(sig)
            self.wakeup()

    def handle_hup(self):
        """\
        HUP handling.
        - Reload configuration
        - Start the new worker processes with a new configuration
        """
        self.reload()

    def handle_quit(self):
        "SIGQUIT handling"
        self.stop()
        raise StopIteration

    def handle_int(self):
        "SIGINT handling"
        self.stop()
        raise StopIteration

    def handle_term(self):
        "SIGTERM handling"
        self.stop()
        raise StopIteration

    def wakeup(self):
        """\
        Wake up the arbiter by writing to the PIPE
        """
        try:
            os.write(self.PIPE[1], b'.')
        except IOError as e:
            if e.errno not in [errno.EAGAIN, errno.EINTR]:
                raise

    def sleep(self):
        """\
        Sleep until PIPE is readable or we timeout.
        A readable PIPE means a signal occurred.
        """
        try:
            ready = select.select([self.PIPE[0]], [], [], 1.0)
            if not ready[0]:
                return
            while os.read(self.PIPE[0], 1):
                pass
        except select.error as e:
            if e.args[0] not in [errno.EAGAIN, errno.EINTR]:
                raise
        except OSError as e:
            if e.errno not in [errno.EAGAIN, errno.EINTR]:
                raise
        except KeyboardInterrupt:
            sys.exit()


    def load_process(self):
        i = 1
        for name, param in self.conf:
            p = Process(name, param.get('command'),
                number=int(param.get('numprocs', 1)))
            if name in self.processes:
                name = '{}-{}'.format(name, i)
                i += 1
            self.processes[name] = p

    def list(self):
        texts = ['processes:']
        for k, v in self.processes.items():
            texts.append('\t%s:  %s'%(k, v.cmd))
        print('\n'.join(texts))

    def run(self):
        for name, process in self.processes.items():
            process.init_process()
        while 1:
            try:
                if not self.processes:
                    logger.info('no available processes, exit...')
                    sys.exit()
                for process in self.processes.values():
                    process.poll()
                sig = self.SIG_QUEUE.pop(0) if len(self.SIG_QUEUE) else None
                if sig is None:
                    self.sleep()
                    continue

                if sig not in self.SIG_NAMES:
                    logger.info("Ignoring unknown signal: %s", sig)
                    continue

                signame = self.SIG_NAMES.get(sig)
                handler = getattr(self, "handle_%s" % signame, None)
                if not handler:
                    logger.error("Unhandled signal: %s", signame)
                    continue
                logger.info("Handling signal: %s", signame)
                handler()
            except StopIteration:
                self.halt()
            except KeyboardInterrupt:
                self.halt()
            except SystemExit:
                raise
            except Exception:
                logger.error("TRACEBACK", "Unhandled exception in main loop:",
                    traceback.format_exc())
                self.halt(-1)


    def reload(self):
        pass

    def halt(self, exit_status=0):
        self.stop()
        sys.exit(exit_status)

    def stop(self):
        for process in self.processes.values():
            process.terminate()
