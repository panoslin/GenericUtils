#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2020/10/30
# IDE: PyCharm

from abc import (
    ABCMeta,
    abstractmethod
)

import inspect
import asyncio
import functools


class BaseDecorator(metaclass=ABCMeta):

    def __init__(self, func=None):
        self.func = func

    @abstractmethod
    def __call__(self, *call_args, **call_kwargs):
        func = self.func if self.func else call_args[0]

        # iscoroutinefunction = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        def wrapped_function(*args, **kwargs):
            ## execute the func
            if self.func:
                res = self.call_func(func=func, *call_args, **call_kwargs)
            else:
                res = self.call_func(func=func, *args, **kwargs)
            return res

        return wrapped_function() if self.func else wrapped_function

    @staticmethod
    def call_func(func, *args, **kwargs):
        iscoroutinefunction = inspect.iscoroutinefunction(func)
        if iscoroutinefunction:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                res = asyncio.ensure_future(func(*args, **kwargs), loop=loop)
            else:
                res = loop.run_until_complete(func(*args, **kwargs))
        else:
            res = func(*args, **kwargs)
        return res
