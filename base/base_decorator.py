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
from functools import partial


class BaseDecorator(metaclass=ABCMeta):
    __slots__ = (
        'func',
    )

    def __init__(self, func=None):
        self.func = func

    @abstractmethod
    def __call__(self, func, instance, *call_args, **call_kwargs):
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

    def __get__(self, instance, owner):
        """
        So, what happens is that in python 3,
        for method declarations work as methods,
        when they are just defined as functions inside the class body,
        what happens is that the language makes use of the "descriptor protocol".

        And to put it simply, an ordinary method is just a function,
        until it is retrieved from an instance:
        since the function has a __get__ method,
        they are recognized as descriptors,
        and the __get__ method is the one responsible to return a "partial function"
        which is the "bound method", and will insert the self parameter upon being called.
        Without a __get__ method, the instance of SomeWrapper when retrieved from an instance,
        has no information on the instance.

        :param instance: the instance of the class where the decorated method is.
        :param owner: owner argument is the owner class
        :return:
        """
        return partial(
            self.__call__,
            partial(self.func, instance),
            instance
        )

    def call_func(self, func, *args, **kwargs):
        iscoroutinefunction = self.is_coroutine_funciton(obj=func)
        if iscoroutinefunction:
            res = self.call_async(func, *args, **kwargs)
        else:
            res = self.call_sync(func, *args, **kwargs)
        return res

    @staticmethod
    def call_async(func, *args, **kwargs):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            res = asyncio.ensure_future(func(*args, **kwargs), loop=loop)
        else:
            res = loop.run_until_complete(func(*args, **kwargs))
        return res

    @staticmethod
    def call_sync(func, *args, **kwargs):
        res = func(*args, **kwargs)
        return res

    @staticmethod
    def is_coroutine_funciton(obj):
        if isinstance(obj, functools.partial):
            while isinstance(obj, functools.partial):
                obj = obj.func
            return inspect.iscoroutinefunction(obj)
        else:
            return inspect.iscoroutinefunction(obj)
