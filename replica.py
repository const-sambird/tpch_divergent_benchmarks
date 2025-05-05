class Replica:
    def __init__(self, id: int, hostname: str, port: str, dbname: str, user: str, password: str = ''):
        self.id = id
        self.hostname = hostname
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password

    def connection_string(self) -> str:
        return f'host={self.hostname} port={self.port} dbname={self.dbname} user={self.user} password={self.password}'
