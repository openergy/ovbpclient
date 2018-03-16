import asyncio
import types


def get_loop():
    """
    Rules :
    * 1 loop per thread (prevents from multiple run_until_compete on same loop in sync code)
    * 1 thread pool per process
    * 1 process pool per process
    """
    try:
        return asyncio.get_event_loop()
    except RuntimeError:  # in a thread, loop may not be set
        asyncio.set_event_loop(asyncio.new_event_loop())
        return asyncio.get_event_loop()


class SyncWrapper:
    def __init__(self, async_object):
        self._async_object = async_object

    def __getattr__(self, item):
        if asyncio.iscoroutinefunction(getattr(self._async_object, item)):
            return types.MethodType(self.sync_maker(item), self)
        else:
            return getattr(self._async_object, item)

    @staticmethod
    def sync_maker(item):
        def sync_func(self, *args, **kwargs):
            return get_loop().run_until_complete(getattr(self._async_object, item)(*args, **kwargs))
        return sync_func

    @property
    def async(self):
        return self._async_object
