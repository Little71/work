from subprocess import Popen, PIPE


class Executor:
    def __init__(self, script, timeout=None):
        self.script = script
        self.timeout = timeout

    def run(self):
        proc = Popen(self.script, shell=True, stdout=PIPE)
        code = proc.wait(self.timeout)
        txt = proc.stdout.read()
        return code, txt


if __name__ == '__main__':
    e = Executor('echo "htllo"')
    print(e.run())
