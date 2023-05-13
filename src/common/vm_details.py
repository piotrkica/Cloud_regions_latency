class VmDetails:
    def __init__(self, id: str, ip: str, login: str, password: str):
        self.id = id
        self.ip = ip
        self.login = login
        self.password = password

    def __str__(self):
        return f"VmDetails{(self.id, self.ip, self.login, self.password)}"
