# coding=utf8

from .utils import is_sae

if not is_sae:
    import pickle, os

    class KVClient(object):
        path = 'kb.bin'

        @classmethod
        def config(cls, path):
            cls.path = path

        def __init__(self, namespace='', pickler=None, unpickler=None, path=None, debug=0):
            """ @debug(bool): 适应sae.KVClient. """
            self.namespace = namespace
            self.pickler = pickler or pickle.Pickler
            self.unpickler = unpickler or pickle.Unpickler
            if path:
                self.path = path
            if os.path.exists(self.path):
                self._load()
            else:
                self.data = {}

        def _dump(self):
            with open(self.path, 'wb') as f:
                self.pickler(f).dump(self.data)

        def _load(self):
            with open(self.path, 'rb') as f:
                self.data = self.unpickler(f).load()

        def real_key(self, key, prefix=''):
            """ 返回存储的key. """
            return '_'.join([item for item in [self.namespace, prefix, key] if item])

        def set(self, key, val, time=0, min_compress_len=0):
            key = self.real_key(key)
            if key in self.data and self.data.get(key)==val:
                return True
            self.data[key] = val
            self._dump()
            return True

        def add(self, key, val, time=0, min_compress_len=0):
            """ 如果key存在, 则跳过并返回False. """
            key = self.real_key(key)
            if key in self.data:
                return False
            self.data[key] = val
            self._dump()
            return True

        def replace(self, key, val, time=0, min_compress_len=0):
            """ 如果key不存在, 则跳过并返回False. """
            key = self.real_key(key)
            if key not in self.data:
                return False
            self.data[key] = val
            self._dump()
            return True

        def delete(self, key, time=0):
            """ 如果key不存在, 则跳过并返回False. """
            key = self.real_key(key)
            if key not in self.data:
                return False
            self.data.pop(key)
            self._dump()

        def get(self, key):
            key = self.real_key(key)
            return self.data.get(key)

        def get_multi(self, keys, key_prefix=''):
            """ 一次获取多个key值.返回一个dict, 其key为keys的元素, 非real_key. """
            real_keys = [self.real_key(key, key_prefix) for key in keys]
            vals = [self.data.get(key) for key in real_keys]
            return dict(zip(keys, vals))

        def get_by_prefix(self, prefix, max_count=100, start_key=None):
            """ 未实现start_key功能. """
            prefix = self.real_key(prefix)
            prefix = prefix and prefix + '_'
            start = len(prefix_len)
            result = []
            for key in self.data:
                if max_count and key.startswith(prefix):
                    result.append((key[start:], self.data.get(key)))
                    max_count -= 1
            return result

        def getkeys_by_prefix(self, prefix, max_count=100, start_key=None):
            """ 未实现start_key功能. """
            prefix = self.real_key(prefix)
            prefix = prefix and prefix + '_'
            start = len(prefix_len)
            result = []
            for key in self.data:
                if max_count and key.startswith(prefix):
                    result.append(key[start:])
                    max_count -= 1
            return result

        def get_info(self):
            return {}

        def disconnect_all(self):
            pass

else:
    from sae.kvdb import KVClient as Client

    class KVClient(Client):
        def __init__(self, namespace='', pickler=None, unpickler=None, path=None, debug=0):
            super(Client, self).__init__(debug=debug)
            self.namespace = namespace

        def real_key(self, key, prefix=''):
            """ 返回存储的key. """
            return '_'.join([item for item in [self.namespace, prefix, key] if item])

        def set(self, key, val, time=0, min_compress_len=0):
            key = self.real_key(key)
            return super(Client, self).set(key, val, time=time, min_compress_len=min_compress_len)

        def add(self, key, val, time=0, min_compress_len=0):
            """ 如果key存在, 则跳过并返回False. """
            key = self.real_key(key)
            return super(Client, self).add(key, val, time=time, min_compress_len=min_compress_len)

        def replace(self, key, val, time=0, min_compress_len=0):
            """ 如果key不存在, 则跳过并返回False. """
            key = self.real_key(key)
            return super(Client, self).replace(key, val, time=time, min_compress_len=min_compress_len)

        def delete(self, key, time=0):
            """ 如果key不存在, 则跳过并返回False. """
            key = self.real_key(key)
            return super(Client, self).delete(key, time=time)

        def get(self, key):
            key = self.real_key(key)
            return super(Client, self).get(key)

        def get_multi(self, keys, key_prefix=''):
            """ 一次获取多个key值.返回一个dict, 其key为keys的元素, 非real_key. """
            key_prefix = self.real_key(key_prefix)
            key_prefix = key_prefix and key_prefix + '_'
            return super(Client, self).get_multi(keys, key_prefix=key_prefix)


        def get_by_prefix(self, prefix, max_count=100, start_key=None):
            """ 未实现start_key功能. """
            prefix = self.real_key(prefix)
            prefix = prefix and prefix + '_'
            return super(Client, self).get_by_prefix(prefix, max_count=max_count, start_key=start_key)

        def getkeys_by_prefix(self, prefix, max_count=100, start_key=None):
            """ 未实现start_key功能. """
            prefix = self.real_key(prefix)
            prefix = prefix and prefix + '_'
            return super(Client, self).getkeys_by_prefix(prefix, max_count=max_count, start_key=start_key)

        def get_info(self):
            super(Client, self).get_info()

        def disconnect_all(self):
            super(Client, self).disconnect_all()
