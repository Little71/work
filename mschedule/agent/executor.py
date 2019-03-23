from subprocess import Popen, PIPE


class Executor:
    @classmethod
    def run(cls, script, timeout=None):
        proc = Popen(script, shell=True, stdout=PIPE)
        code = proc.wait(timeout)
        txt = proc.stdout.read()
        return code, txt


if __name__ == '__main__':
    e = Executor('echo "htllo"')
    print(e.run())
