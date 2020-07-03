import os
import json

root_path = '/data/hello_world/media'


def fetch_all_abspath(
        path: str,
        file: 'Not param' = [],
        dir: 'Not param' = []
) -> tuple:
    for name in os.listdir(path):
        full_path = os.path.join(path, name)
        if os.path.isfile(full_path):
            file.append(full_path)
        else:
            dir.append(full_path.replace(root_path, ''))
            fetch_all_abspath(full_path)
    return file, dir


if __name__ == '__main__':
    data = fetch_all_abspath(root_path)
    print(json.dumps(data))
