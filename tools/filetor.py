"""File Operation"""
import json
import yaml


def filetor(
        file: str,
        data: ... = None,
        type: 'enum(text, yaml, json)' = None,
        encoding: str = 'UTF-8',
        *a, **kw) -> str or dict:
    """
    if data is None:
        Read file according to `type`.
    else:
        Write `data` to `file` according to `type`.

    Do you have a better idea?
    """
    if type is None:
        if file.endswith('yaml') or file.endswith('yml'):
            type = 'yaml'
        elif file.endswith('json'):
            type = 'json'
        else:
            type = 'text'

    if data is None:
        mode = 'r'
        if type == 'yaml':
            operating = 'yaml.safe_load(f)'
        elif type == 'json':
            operating = 'json.load(f, *a, **kw)'
        else:
            operating = 'f.read()'
    else:
        mode = 'w'
        if type == 'yaml':
            operating = 'yaml.safe_dump(data, f, **kw)'
        elif type == 'json':
            operating = 'json.dump(data, f, *a, **kw)'
        else:
            operating = 'f.write(str(data))'

    with open(file, mode, encoding=encoding) as f:
        return eval(operating)
