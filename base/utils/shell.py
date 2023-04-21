import subprocess

from base.utils.format import format_completed_process


class LinuxShell:
    def __init__(self, cmd):
        self.ret = subprocess.run(cmd, shell=True, capture_output=True)

    def __str__(self):
        return format_completed_process(self.ret)
