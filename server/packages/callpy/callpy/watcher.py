import os
import subprocess
import signal
import time
import sys
import copy
from typing import Optional, List

class Watcher(object):
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
        self.target = target
        self.proc_name = self.target
        self.workers  = []

    def init_signals(self):
        signal.signal(signal.SIGINT, self.handle_int)
        signal.signal(signal.SIGTERM, self.handle_term)
        signal.signal(signal.SIGILL, self.handle_quit)

    def run(self):
        last_argv = sys.argv[-1]
        if last_argv.lower() == 'worker':
            self.run_as_worker()
        else:
            self.init_signals()
            while 1:
                self.manage_workers()
                time.sleep(0.1)

    def run_as_worker(self):
        self.target()

    def manage_workers(self):
        for p in self.workers:
            p.poll()

        terminated = list(filter(lambda x: x.returncode != None, self.workers))
        self.workers = list(filter(lambda x: x.returncode == None, self.workers))

        count = self.num_workers - len(self.workers)


        if count > 0:
            args = copy.copy(sys.orig_argv)
            args.append('worker')
            for _ in range(count):
                p = subprocess.Popen(args, shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
                self.workers.append(p)

    def handle_quit(self, sig, frame):
        """SIGILL handling"""
        self.stop()
        raise StopIteration

    def handle_int(self, sig, frame):
        """SIGINT handling"""
        self.stop()
        raise StopIteration

    def handle_term(self, sig, frame):
        """SIGTERM handling"""
        self.stop()
        raise StopIteration

    def stop(self):
        """\
        Stop workers
        """
        for p in self.workers:
            p.poll()
            if p.returncode == None:
                p.terminate()
        sys.exit(1)

