

import threading


class SingletonClass(object):
  def __new__(cls) -> any:
    if not hasattr(cls, 'instance'):
      cls.instance: SingletonClass = super(SingletonClass, cls).__new__(cls)
    return cls.instance
