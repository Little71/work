from subprocess import Popen, PIPE
from util import getlogger

logger = getlogger(__name__,'x:/xx.log')

class Executor:
    @classmethod
    def run(cls, script, timeout=None):
        proc = Popen(script, shell=True, stdout=PIPE)
        code = proc.wait(timeout)
        txt = proc.stdout.read()
        logger.info(f'{code} {txt}')
        return code, txt
