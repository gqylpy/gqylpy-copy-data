import config as _
# The configuration should be loaded before all modules are loaded.

import os
import json

from tools import filetor
from tools import genpath
from tools import abspath
from tools import decrypt
from tools import SecureShell

from config import core as cnf

ssh = SecureShell(
    connect=None,
    auth=None,
    timeout=1000)

media_dir = abspath(cnf.path.db, 'media')
genpath(media_dir)

all_path_file = abspath(cnf.path.db, 'all_path.json')


def fetch_all_path() -> []:
    ssh.upload_file(
        local_path=abspath(cnf.path.db, 'fetch_all_path.py'),
        remote_path='/root/fetch_all_path.py')
    status, data = ssh.cmd(
        '/usr/local/python3.6.5/bin/python3 /root/fetch_all_path.py')

    if not status:
        print(data)

    return json.loads(data)



def run():
    if not os.path.exists(all_path_file):
        filetor(all_path_file, fetch_all_path())

    file_path, dir_path = filetor(all_path_file)

    amount = len(file_path)

    for dir in dir_path:
        genpath(abspath(media_dir, dir[1:]))

    for count, remote_path in enumerate(file_path, 1):
        local_path = abspath(media_dir, remote_path.split('media/')[-1])

        if os.path.exists(local_path):
            print(f'{count}/{amount} --exists')
            continue

        try:
            ssh.download_file(remote_path, local_path)
            print(f'{count}/{amount}')
        except (Exception, KeyboardInterrupt) as e:
            print(e)
            try:
                os.remove(local_path)
                print(f'delete: {local_path}')
            except FileNotFoundError as e:
                print(f'delete: {e}')
            return
