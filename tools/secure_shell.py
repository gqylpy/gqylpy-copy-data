import re
import os
import paramiko

from tools import uuid4


class SecureShell:
    _EXEC_INSTRUCTIONS = 'exit', 'quit', 'e', 'q'

    _NOW_PATH_MARK: str = ''
    _NOW_PATH_CMD: str = ''

    _UP_FILE_DEFAULT_PATH: str = '/root/'
    _UP_OR_DOWN_FILE_DEFAULT_SUFFIX: str = '.txt'

    def __init__(self, connect: str, auth: str, timeout: int = 10):
        """
        :param connect: host:port
        :param auth: user@pwd
        """
        self.timeout = timeout
        connect = connect.split(':')
        connect.append(22) if len(connect) != 2 else int(connect[1])
        self.auth = re.match(rf'(?P<u>.+?)@(?P<p>.+)', auth).group('u', 'p')

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(*connect, *self.auth, timeout=timeout)

    def _parse_result(self, result: 'stdout or stderr') -> str:
        return result.read().decode()

    def _print(self, data: str = '\n', color: int = 37, font: int = 0) -> None:
        print(f'\033[{font};{color};0m{data}\033[0m')

    def _set_prompt(self) -> str:
        try:
            hostname: str = self.cmd('echo $HOSTNAME')[1][:11].strip()
            home: str = re.match(r'.*/(.+)', self.cmd('echo $HOME')[1].strip()).group(1)
            path_mark: str = '~' if self._NOW_PATH_MARK == home else \
                self._NOW_PATH_MARK if self._NOW_PATH_MARK else '~'
            mark: str = '#' if self.auth[0] == 'root' else '$'
            return f'[{self.auth[0]}@{hostname} {path_mark}]{mark} ' if hostname else '>>> '
        except Exception:
            return '>>> '

    def _receive_cmd(self, flags: str) -> str or False:
        while True:
            cmd: str = input(flags or self._set_prompt()).strip()
            if cmd:
                break
        if cmd in self._EXEC_INSTRUCTIONS:
            return False
        if flags:
            return cmd
        now_path_cmd: str = self._NOW_PATH_CMD and self._NOW_PATH_CMD + ';'
        return f"{now_path_cmd}{re.sub(r';$', '', cmd)} && pwd"

    def _ext_path_info(self, result: str, flags: str) -> str:
        if flags:
            return result
        pattern = re.compile(r'\n?(.+)\n$')
        now_path: str = pattern.findall(result)[0]
        self._NOW_PATH_MARK: str = now_path.split('/')[-1] or '/'
        self._NOW_PATH_CMD: str = f'cd {now_path}'
        return pattern.sub('', result)

    def cmd(self, cmd: str) -> tuple:
        """Execute the command
        如果你的程序需要在远程服务器中执行命令并取得结果，可使用此方法
        :param cmd: 命令
        :return: 命令执行结果
        """
        stdin, stdout, stderr = self.client.exec_command(cmd, self.timeout)
        result: str = self._parse_result(stdout)
        return bool(result), result or self._parse_result(stderr)

    def cmdp(
            self,
            cmd: str,
            print_color: int = 37,
            print_font: int = 0,
            *args,
            **kwargs) -> None:
        """Execute the command and print
        直接输出命令结果
        :param cmd: 命令
        :param print_color: 输出字符颜色
        :param print_font: 输出字符字体
        """
        stdin, stdout, stderr = self.client.exec_command(cmd, self.timeout)
        result: str = self._parse_result(stdout) or self._parse_result(stderr)
        self._print(result, print_color, print_font)

    def inter_mode(
            self,
            flags: str = None,
            print_color: int = 37,
            print_font: int = 0,
            *args,
            **kwargs) -> None:
        """Interactive mode
        交互模式，类似于终端，使用例如 "tail -f file" 的指令会导致程序卡死
        :param flags: 交互提示符
        :param print_color: 打印字符颜色
        :param print_font: 打印字符字体
        """
        while True:
            try:
                cmd: str = self._receive_cmd(flags)
                if not cmd:
                    break
                stdin, stdout, stderr = self.client.exec_command(
                    cmd, self.timeout)
                result: str = self._parse_result(stdout)
                result: str = self._ext_path_info(
                    result, flags) if result else self._parse_result(stderr)
                self._print(result or ' ', print_color, print_font)
            except KeyboardInterrupt:
                break

    def upload_file(
            self,
            local_path: str,
            remote_path: str = None,
            flags: bool = False,
            *args,
            **kwargs) -> True or None:
        """Upload file
        上传文件
        :param local_path: 本地路径
        :param remote_path: 远程路径
        :param flags: 是否在输出相关信息
        """
        remote_path: str = remote_path or f'/root/{uuid4()}.txt'
        if self.client.open_sftp().put(local_path, remote_path):
            flags and self._print(f'Uploaded successfully -> {remote_path}', 32)
            return True
        self._print('Uploaded failed', 31)

    def download_file(
            self,
            remote_path: str,
            local_path: str = None,
            flags: bool = False,
            *args,
            **kwargs) -> True or None:
        """Download file
        下载文件
        :param remote_path: 远程路径
        :param local_path: 本地路径
        :param flags: 是否在输出相关信息
        """
        local_path: str = local_path or f'{uuid4()}.txt'
        self.client.open_sftp().get(remote_path, local_path)
        if os.path.isfile(local_path):
            flags and self._print(f'Download successful -> {remote_path}', 32)
            return True
        self._print('Download failed', 31)
