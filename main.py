from paramiko import SSHClient


class Executor:
    _addr = "192.168.1.20"
    _port = 22
    _uname = "ubnt"
    _passwd = "ubnt"
    def __init__(self, addr: str, port: int, uname: str, passwd: str) -> None:
        self._addr = addr
        self._port = port
        self._uname = uname
        self._passwd = passwd
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

    def exec(self, cmd: str, path: str = None) -> list:
        if not self.active:
            raise ConnectionAbortedError("Lost connection!")
        if path:
            cmd = f"cd {path}; {cmd}"
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
    
    def create_file(self, filename: str) -> bool:
        if type(filename) is not str:
            raise TypeError("Filename should be string!")
        if len(filename) == 0:
            raise ValueError("Filename should not be empty!")
        out, err = self.exec(f"touch {filename}")
        if len(err):
            print("Error while creating file:", err)
            return False
        return True

    def write_to_file(self, filename: str, lines: list, overwrite: bool = False) -> bool:
        if type(filename) is not str:
            raise TypeError("Filename should be string!")
        if len(filename) == 0:
            raise ValueError("Filename should not be empty!")
        if type(lines) is not list:
            raise TypeError("Lines should be a list!")
        if len(lines) == 0:
            raise ValueError("Cannor write empty lines list")
        mode = ">" if overwrite else ">>"
        out, err = self.exec(f'echo "' + '\n'.join(lines) + f'" {mode} {filename}')
        if len(err):
            print("Error while writing to file:", err)
            return False
        return True
    
    def read_file(self, filename: str) -> list:
        if type(filename) is not str:
            raise TypeError("Filename should be string!")
        if len(filename) == 0:
            raise ValueError("Filename should not be empty!")
        if not filename in [x.strip() for x in self.list_files()]:
            raise FileNotFoundError(f"{filename} file doesn't exist!")
        out, err = self.exec(f'cat "{filename}"')
        if len(err):
            print("Error while reading file:", err)
            return []
        return out
    
    def get_location(self) -> str:
        out, err = self.exec("pwd")
        if len(err):
            print("Error while getting location", err)
            return None
        return out[0].strip()

    def change_directory(self, dirr: str) -> bool:
        if type(dirr) is not str:
            raise TypeError("Directory name should be string!")
        out, err = self.exec(f"cd {dirr}")
        if len(err):
            print("Error while changing directory:", err)
            return False
        return True

    def close(self):
        self.client.close()

    def __bool__(self) -> bool:
        return self.active


if __name__ == "__main__":
    airos = Executor()

    print(airos.exec_input("./test.sh", ['Mati', '18']))
    
    # airos.change_password("test")
    
    for file in airos.list_files():
        print("File:", file.strip())
    
    # airos.client.close()
    
    print("Status:", bool(airos))

    airos.create_file("created-by-python.txt")

    airos.write_to_file("created-by-python.txt", ['Hello', 'World!'])
    
    for file in airos.list_files():
        print("File:", file.strip())

    print(airos.read_file("created-by-python.txt"))

    airos.write_to_file("created-by-python.txt", ['Not', 'Any More!'], overwrite=True)

    print(airos.read_file("created-by-python.txt"))

    print("pwd", airos.get_location())

    print(airos.exec("pwd", path="testdir"))