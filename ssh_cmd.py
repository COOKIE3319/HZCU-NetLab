# Decompiled from ssh_cmd.pyc (Python 3.8)
import paramiko


class MySSH:

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._transport = None
        self._sftp = None
        self._client = None

    def connect(self, username, passwd):
        transport = paramiko.Transport((self._host, self._port))
        transport.connect(username=username, password=passwd)
        self._transport = transport

    def download(self, remotepath, localpath):
        if self._sftp is None:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
        self._sftp.get(remotepath, localpath)

    def put(self, localpath, remotepath):
        if self._sftp is None:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
        self._sftp.put(localpath, remotepath)

    def exec_cmd(self, command):
        if self._client is None:
            self._client = paramiko.SSHClient()
        self._client._transport = self._transport
        stdin, stdout, stderr = self._client.exec_command(command)
        data = stdout.read()
        if len(data) > 0:
            ret = data.strip()
            print(ret.decode())
            return ret
        err = stderr.read()
        if len(err) > 0:
            print(err.strip())
        return err

    def close(self):
        if self._transport:
            self._transport.close()
        if self._client:
            self._client.close()
