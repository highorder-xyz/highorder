import errno
import os
import os.path
import select
import signal
import socket
import sys
import time
import traceback
import ctypes
import fcntl
import resource

import random
import tempfile
import copy

from basepy.log import logger
from setproctitle import setproctitle

def close_on_exec(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFD)
    flags |= fcntl.FD_CLOEXEC
    fcntl.fcntl(fd, fcntl.F_SETFD, flags)


def set_non_blocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)


def set_owner_process(uid, gid):
    """ set user and group of workers processes """
    if gid:
        try:
            os.setgid(gid)
        except OverflowError:
            if not ctypes:
                raise
            # versions of python < 2.6.2 don't manage unsigned int for
            # groups like on osx or fedora
            os.setgid(-ctypes.c_int(-gid).value)

    if uid:
        os.setuid(uid)


def seed():
    try:
        random.seed(os.urandom(64))
    except NotImplementedError:
        random.seed('%s.%s' % (time.time(), os.getpid()))


def daemonize(preserve_fds=None):
    """\
    Standard daemonization of a process.
    http://www.svbug.com/documentation/comp.unix.programmer-FAQ/faq_2.html#SEC16
    """

    def _maxfd(limit=1024):
        maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
        if maxfd == resource.RLIM_INFINITY:
            return limit
        else:
            return maxfd

    def _devnull(default="/dev/null"):
        if hasattr(os, "devnull"):
            return os.devnull
        else:
            return default

    def _close_fds(preserve=None):
        preserve = preserve or []
        for fd in range(0, _maxfd()):
            if fd not in preserve:
                try:
                    os.close(fd)
                except OSError:  # fd wasn't open to begin with (ignored)
                    pass

    if os.fork():
        os._exit(0)
    os.setsid()

    if os.fork():
        os._exit(0)

    os.umask(0)
    _close_fds(preserve_fds)

    os.open(_devnull(), os.O_RDWR)
    os.dup2(0, 1)
    os.dup2(0, 2)


def prevent_core_dump():
    """Prevent this process from generating a core dump.

    Sets the soft and hard limits for core dump size to zero. On
    Unix, this prevents the process from creating core dump
    altogether.

    """
    core_resource = resource.RLIMIT_CORE

    try:
        # Ensure the resource limit exists on this platform, by requesting
        # its current value
        resource.getrlimit(core_resource)
    except ValueError as e:
        raise RuntimeWarning(
            "System does not support RLIMIT_CORE resource limit ({})".format(
                e))

    # Set hard and soft limits to zero, i.e. no core dump at all
    resource.setrlimit(core_resource, (0, 0))


class Pidfile(object):
    """\
    Manage a PID file. If a specific name is provided
    it and '"%s.oldpid" % name' will be used. Otherwise
    we create a temp file using tempfile.mkstemp.
    """

    def __init__(self, fname):
        self.fname = fname
        self.pid = None

    def create(self, pid):
        oldpid = self.validate()
        if oldpid:
            if oldpid == os.getpid():
                return
            raise RuntimeError(
                "Already running on PID %s (or pid file '%s' is stale)"
                % (os.getpid(), self.fname))

        self.pid = pid

        # Write pidfile
        fdir = os.path.dirname(self.fname)
        if fdir and not os.path.isdir(fdir):
            raise RuntimeError(
                "%s doesn't exist. Can't create pidfile." % fdir)
        fd, fname = tempfile.mkstemp(dir=fdir)
        os.write(fd, "%s\n" % self.pid)
        if self.fname:
            os.rename(fname, self.fname)
        else:
            self.fname = fname
        os.close(fd)

        # set permissions to -rw-r--r--
        os.chmod(self.fname, 420)

    def rename(self, path):
        self.unlink()
        self.fname = path
        self.create(self.pid)

    def unlink(self):
        """ delete pidfile"""
        try:
            with open(self.fname, "r") as f:
                pid1 = int(f.read() or 0)

            if pid1 == self.pid:
                os.unlink(self.fname)
        except Exception:
            pass

    def validate(self):
        """ Validate pidfile and make it stale if needed"""
        if not self.fname:
            return
        try:
            with open(self.fname, "r") as f:
                wpid = int(f.read() or 0)

                if wpid <= 0:
                    return

                try:
                    os.kill(wpid, 0)
                    return wpid
                except OSError as e:
                    if e[0] == errno.ESRCH:
                        return
                    raise
        except IOError as e:
            if e[0] == errno.ENOENT:
                return
            raise


class HaltServer(Exception):
    def __init__(self, reason, exit_status=1):
        self.reason = reason
        self.exit_status = exit_status

    def __str__(self):
        return "<HaltServer %r %d>" % (self.reason, self.exit_status)


class Worker(object):
    SIGNALS = [
        getattr(signal, "SIG%s" % x) for x in
        "ABRT HUP QUIT USR1 USR2 WINCH CHLD".split()
    ]

    def __init__(self, ppid, target, log):
        """This is called pre-fork so it shouldn't do anything to the
        current process. If there's a need to make process wide
        changes you'll want to do that in ``self.init_process()``.
        """
        self.ppid = ppid
        self.target = target
        self.booted = False
        self.alive = True
        self.log = log

    def __str__(self):
        return "<Process %s>" % self.pid

    @property
    def pid(self):
        return os.getpid()

    def run(self):
        """This is the mainloop of a worker process."""
        if isinstance(self.target, str):
            raise Exception('target must be runnable.')
        else:
            target = self.target

        if callable(target):
            target()
        else:
            self.booted = False
            raise Exception('target function not available.')

    def init_process(self):
        # Reseed the random number generator
        seed()

        self.init_signals()

        # Enter main run loop
        self.run()
        self.booted = True

    def init_signals(self):
        # reset signaling
        [signal.signal(s, signal.SIG_DFL) for s in self.SIGNALS]
        # init new signaling
        signal.signal(signal.SIGQUIT, self.handle_quit)
        signal.signal(signal.SIGWINCH, self.handle_winch)
        signal.signal(signal.SIGUSR1, self.handle_usr1)
        signal.signal(signal.SIGABRT, self.handle_abort)
        # Don't let SIGQUIT and SIGUSR1 disturb active requests
        # by interrupting system calls
        if hasattr(signal, 'siginterrupt'):  # python >= 2.6
            signal.siginterrupt(signal.SIGQUIT, False)
            signal.siginterrupt(signal.SIGUSR1, False)

    def handle_usr1(self, sig, frame):
        pass

    def handle_abort(self, sig, frame):
        sys.exit(1)

    def handle_quit(self, sig, frame):
        sys.exit(0)

    def handle_error(self, req, client, addr, exc):
        pass

    def handle_winch(self, sig, fname):
        # Ignore SIGWINCH in worker. Fixes a crash on OpenBSD.
        return


class Supervisor(object):
    """
    Supervisor maintain the workers processes alive. It launches or
    kills them if needed. It also manages application reloading
    via SIGHUP/USR2.
    """

    # A flag indicating if a worker failed to
    # to boot. If a worker process exist with
    # this error code, the arbiter will terminate.
    WORKER_BOOT_ERROR = 3

    START_CTX = {}

    WORKERS = {}
    PIPE = []

    # I love dynamic languages
    SIG_QUEUE = []
    SIGNALS = [
        getattr(signal, "SIG%s" % x) for x in
        "HUP QUIT INT TERM TTIN TTOU USR1 USR2 WINCH".split()
    ]
    SIG_NAMES = dict((getattr(signal, name), name[3:].lower())
                     for name in dir(signal)
                     if name[:3] == "SIG" and name[3] != "_")

    WORKER_CLASS = Worker

    def __init__(self,
                 prog,
                 daemon=False,
                 workers=1,
                 pid=None,
                 target=None):
        self.stop_timeout = 120
        self.prog = prog
        self.num_workers = workers
        self.daemon = daemon
        self.pid = os.getpid()
        self.pidfile = None
        if pid is not None:
            self.pidfile = Pidfile(pid)
            self.pidfile.create(self.pid)
        self.target = target
        self.proc_name = self.target
        self.WORKER_CLASS = Worker
        if hasattr(self.WORKER_CLASS, 'setup'):
            self.WORKER_CLASS.setup()

        self.reexec_pid = 0
        self.name = "Supervisor of {}".format(self.prog)

        self.log = logger

        # get current path, try to use PWD env first
        try:
            a = os.stat(os.environ['PWD'])
            b = os.stat(os.getcwd())
            if a.st_ino == b.st_ino and a.st_dev == b.st_dev:
                cwd = os.environ['PWD']
            else:
                cwd = os.getcwd()
        except Exception:
            cwd = os.getcwd()

        args = sys.argv[:]
        args.insert(0, sys.executable)

        # init start context
        self.START_CTX = {"args": args, "cwd": cwd, 0: sys.executable}

    def start(self):
        """Initialize the arbiter. Start listening and set pidfile if needed.
        """
        self.log.info("Starting %s", self.prog)
        self.init_signals()

    def init_signals(self):
        """\
        Initialize supervisor signal handling. Most of the signals
        are queued. Child signals only wake up the supervisor.
        """
        # close old PIPE
        if self.PIPE:
            [os.close(p) for p in self.PIPE]

        # initialize the pipe
        self.PIPE = pair = os.pipe()
        for p in pair:
            set_non_blocking(p)
            close_on_exec(p)

        # intialiatze all signals
        [signal.signal(s, self.signal) for s in self.SIGNALS]
        signal.signal(signal.SIGCHLD, self.handle_chld)

    def signal(self, sig, frame):
        if len(self.SIG_QUEUE) < 5:
            self.SIG_QUEUE.append(sig)
            self.wakeup()

    def run(self):
        """Main supervisor loop."""
        if self.daemon:
            prevent_core_dump()
            daemonize()
        self.start()
        setproctitle("supervisor of {} [{}]".format(self.prog, self.proc_name))

        self.manage_workers()
        while True:
            try:
                sig = self.SIG_QUEUE.pop(0) if len(self.SIG_QUEUE) else None
                if sig is None:
                    self.sleep()
                    self.manage_workers()
                    continue

                if sig not in self.SIG_NAMES:
                    self.log.info("Ignoring unknown signal: %s", sig)
                    continue

                signame = self.SIG_NAMES.get(sig)
                handler = getattr(self, "handle_%s" % signame, None)
                if not handler:
                    self.log.error("Unhandled signal: %s", signame)
                    continue
                self.log.info("Handling signal: %s", signame)
                handler()
                self.wakeup()
            except StopIteration:
                self.halt()
            except KeyboardInterrupt:
                self.halt()
            except HaltServer as inst:
                self.halt(reason=inst.reason, exit_status=inst.exit_status)
            except SystemExit:
                raise
            except Exception:
                self.log.error("Unhandled exception in main loop:\n%s",
                               traceback.format_exc())
                self.stop()
                if self.pidfile is not None:
                    self.pidfile.unlink()
                sys.exit(-1)

    def handle_chld(self, sig, frame):
        """SIGCHLD handling"""
        self.reap_workers()
        self.wakeup()

    def handle_hup(self):
        """\
        HUP handling.
        - Reload configuration
        - Start the new worker processes with a new configuration
        - Gracefully shutdown the old worker processes
        """
        self.log.info("Hang up: %s", self.name)
        self.reload()

    def handle_quit(self):
        """SIGQUIT handling"""
        self.stop()
        raise StopIteration

    def handle_int(self):
        """SIGINT handling"""
        self.stop()
        raise StopIteration

    def handle_term(self):
        """SIGTERM handling"""
        self.stop()
        raise StopIteration

    def handle_ttin(self):
        """\
        SIGTTIN handling.
        Increases the number of workers by one.
        """
        self.num_workers += 1
        self.manage_workers()

    def handle_ttou(self):
        """\
        SIGTTOU handling.
        Decreases the number of workers by one.
        """
        if self.num_workers <= 1:
            return
        self.num_workers -= 1
        self.manage_workers()

    def handle_usr1(self):
        """\
        SIGUSR1 handling.
        Kill all workers by sending them a SIGUSR1
        """
        self.kill_workers(signal.SIGUSR1)

    def handle_usr2(self):
        """\
        SIGUSR2 handling.
        Creates a new supervisor/worker set as a slave of the current
        supervisor without affecting old workers. Use this to do live
        deployment with the ability to backout a change.
        """
        self.reexec()

    def handle_winch(self):
        """SIGWINCH handling"""
        if os.getppid() == 1 or os.getpgrp() != os.getpid():
            self.log.info("graceful stop of workers")
            self.num_workers = 0
            self.kill_workers(signal.SIGQUIT)
        else:
            self.log.info("SIGWINCH ignored. Not daemonized")

    def wakeup(self):
        """\
        Wake up the arbiter by writing to the PIPE
        """
        try:
            os.write(self.PIPE[1], b'.')
        except IOError as e:
            if e.errno not in [errno.EAGAIN, errno.EINTR]:
                raise

    def halt(self, reason=None, exit_status=0):
        """ halt arbiter """
        self.stop()
        self.log.info("Shutting down: %s", self.name)
        if reason is not None:
            self.log.info("Reason: %s", reason)
        if self.pidfile is not None:
            self.pidfile.unlink()
        sys.exit(exit_status)

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

    def stop(self):
        """\
        Stop workers
        """
        sig = signal.SIGTERM
        self.kill_workers(sig)
        limit = time.time() + self.stop_timeout
        while self.WORKERS and time.time() < limit:
            time.sleep(0.1)
        self.kill_workers(signal.SIGKILL)

    def reexec(self):
        """\
        Relaunch the supervisor and workers.
        """
        if self.pidfile is not None:
            self.pidfile.rename("%s.oldbin" % self.pidfile.fname)

        self.reexec_pid = os.fork()
        if self.reexec_pid != 0:
            self.name = "Old {}".format(self.name)
            return

        os.chdir(self.START_CTX['cwd'])

        os.execvpe(self.START_CTX[0], self.START_CTX['args'], os.environ)

    def reload(self):
        # TODO reload
        # manage workers
        self.manage_workers()

    def reap_workers(self):
        """\
        Reap workers to avoid zombie processes
        """
        exitcodes = set()
        try:
            while True:
                wpid, status = os.waitpid(-1, os.WNOHANG)
                self.log.info('waitpid:%s, status:%s' % (wpid, status))
                if not wpid:
                    break
                if self.reexec_pid == wpid:
                    self.reexec_pid = 0
                else:
                    # A worker said it cannot boot. We'll shutdown
                    # to avoid infinite start/stop cycles.
                    exitcode = status >> 8
                    exitcodes.add(exitcode)
                    if exitcode == 0:
                        self.num_workers -= 1
                    self.WORKERS.pop(wpid, None)
        except OSError as e:
            if e.errno == errno.ECHILD:
                pass
        if self.WORKER_BOOT_ERROR in exitcodes:
            reason = "Worker failed to boot."
            raise HaltServer(reason, self.WORKER_BOOT_ERROR)

    def manage_workers(self):
        """\
        Maintain the number of workers by spawning or killing
        as required.
        """
        if len(self.WORKERS.keys()) < self.num_workers:
            self.spawn_workers()

        workers = self.WORKERS.items()
        while len(workers) > self.num_workers:
            (pid, _) = workers.pop(0)
            self.kill_worker(pid, signal.SIGQUIT)

    def spawn_worker(self):
        worker = self.WORKER_CLASS(self.pid, self.target, self.log)

        pid = os.fork()

        if pid != 0:
            self.WORKERS[pid] = worker
            return pid

        # Process Child
        worker_pid = os.getpid()
        try:
            setproctitle("worker of {} [{}]".format(self.prog, self.proc_name))
            self.log.info("Booting worker with pid: %s" % (worker_pid))
            worker.init_process()
            sys.exit(0)
        except SystemExit:
            raise
        except Exception:
            self.log.error("Exception in worker process:\n",
                           traceback.format_exc())
            self.log.error('Exception in worker:%s' % (worker.booted))
            if not worker.booted:
                sys.exit(self.WORKER_BOOT_ERROR)
            sys.exit(-1)
        finally:
            self.log.info("Worker exiting (pid: %s)", worker_pid)

    def spawn_workers(self):
        """\
        Spawn new workers as needed.

        This is where a worker process leaves the main loop
        of the supervisor process.
        """

        for i in range(self.num_workers - len(self.WORKERS.keys())):
            self.spawn_worker()

    def kill_workers(self, sig):
        """\
        Kill all workers with the signal `sig`
        :attr sig: `signal.SIG*` value
        """
        for pid in self.WORKERS.keys():
            self.kill_worker(pid, sig)

    def kill_worker(self, pid, sig):
        """Kill a worker.

        :attr pid: int, worker pid
        :attr sig: `signal.SIG*` value
        """
        try:
            os.kill(pid, sig)
        except OSError as e:
            if e.errno == errno.ESRCH:
                try:
                    self.WORKERS.pop(pid)
                    return
                except (KeyError, OSError):
                    return
            raise
