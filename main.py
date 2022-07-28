from paramiko import SSHClient, transport


class Executor:
    _addr = "192.168.1.20"
    _port = 22
    _uname = "ubnt"
    _passwd = "ubnt"
    def __init__(self) -> None:
        self.client = SSHClient()
        self.client.load_system_host_keys()
        self.client.connect(self._addr, port=self._port, username=self._uname, password=self._passwd)
        self.transport = self.client.get_transport()
    
    @property
    def data(self) -> dict:
        return {"addr": self._addr, "port": self._port, "uname": self._uname, "passwd": self._passwd}
    
    @property
    def active(self) -> bool:
        return self.transport.is_active()

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
    
    def list_files(self) -> list:
        out, err = self.exec("ls .")
        if len(err):
            print("Errors", err)
        return out

    def close(self):
        self.client.close()


if __name__ == "__main__":
    airos = Executor()

    # print(airos.exec_input("./test.sh", ['Mati', '18']))
    # airos.change_password("test")
    for file in airos.list_files():
        print("File:", file.strip())
    airos.client.close()
    print(airos.transport.is_active())
    for file in airos.list_files():
        print("File:", file.strip())