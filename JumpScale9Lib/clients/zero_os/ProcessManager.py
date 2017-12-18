import redis
import uuid
import json
import textwrap
import shlex
import base64
import signal
import socket
import logging
import time
import sys
from js9 import j
from .Client import *

DefaultTimeout = 10  # seconds

logger = logging.getLogger('g8core')



class ProcessManager:
    _process_chk = j.tools.typechecker.get({
        'pid': typchk.Or(int, typchk.IsNone()),
    })

    _kill_chk = j.tools.typechecker.get({
        'pid': int,
        'signal': int,
    })

    def __init__(self, client):
        self._client = client

    def list(self, id=None):
        """
        List all running processes

        :param id: optional PID for the process to list
        """
        args = {'pid': id}
        self._process_chk.check(args)
        return self._client.json('process.list', args)

    def kill(self, pid, signal=signal.SIGTERM):
        """
        Kill a process with given pid

        :WARNING: beware of what u kill, if u killed redis for example core0 or coreX won't be reachable

        :param pid: PID to kill
        """
        args = {
            'pid': pid,
            'signal': int(signal),
        }
        self._kill_chk.check(args)
        return self._client.json('process.kill', args)

