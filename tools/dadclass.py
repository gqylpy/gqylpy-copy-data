from collections import Iterable


class SingletonMode:
    """Inherit me, you will
    become a singleton class.
    """
    _instance = None

    def __new__(cls, *a, **kw):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance


class Dict(dict):
    """Dict == dict
    I inherited 'dict', my main function is to
    allow the dict to get or set values by `d.key`.

    Warning:
        After testing, 'Dict' gets values about
        6 times slower than the native `dict`.
    """

    def __init__(self, ____: dict or list = None, **kw):
        for name, value in (____ or kw).items():
            self[name] = Dict(value)

    def __new__(cls, ____={}, **kw):
        if isinstance(____, dict):
            return dict.__new__(cls)

        if isinstance(____, Iterable) and not isinstance(____, str):
            return [Dict(v) for v in ____]

        return ____

    def __getattribute__(self, name):
        """`self.name` to `self[name]`"""
        try:
            return super().__getitem__(name)
        except KeyError:
            try:
                return super().__getattribute__(name)
            except AttributeError:
                raise KeyError(name)

    def __setattr__(self, name, value):
        """`self.name = value` to `self[name] = value`"""
        self.__setitem__(name, value)

    def __delattr__(self, name):
        """`del self.name` to `del self[name]`"""
        self.__delitem__(name)

    def __deepcopy__(self, memo):
        """
        This method must be implemented,  otherwise
        `KeyError: '__deepcopy__'` will appear when
        `copy.deepcopy (Dict obj)` is called.
        """
        return Dict(self)

    def __getstate__(self):
        return True

    def __setstate__(self, name):
        return True
