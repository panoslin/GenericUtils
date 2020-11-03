#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2020/11/3
# IDE: PyCharm

from GenericUtils.base.base_decorator import BaseDecorator
import functools
import time
import traceback


"""
verbose:
    1: NO LOG
    2: NO traceback for ALL `exceptions`
    3: NO traceback for `exceptions`
    4: ALL
"""
LOG_LEVEL = {
    "NO LOG": 1,
    "NO traceback": 2,
    "NO exceptions": 3,
    "ALL": 4,
}


def log(level, funcname, benchmark, exception):
    if level >= benchmark:
        traceback.print_exc()
        print(f"Encounter Exception: while operating func {funcname}: {exception}")
    elif level > LOG_LEVEL["NO LOG"]:
        print(f"Encounter Exception: while operating func {funcname}: {exception}")
    elif level == LOG_LEVEL["NO LOG"]:
        pass



class Retrier(BaseDecorator):
    __slots__ = (
        'func',
        'exceptions',
        'exception_return',
        'other_exception_return',
        'retry',
        'countdown',
        'verbose',
    )
    def __init__(
            self,
            func=None,
            exceptions=(Exception,),
            exception_return=False,
            other_exception_return=False,
            retry=3,
            countdown=0,
            verbose=4,
            *args,
            **kwargs
    ):
        """

        :param exceptions: Exception to be caught specifically
        :param exception_return: return if the exceptions are caught
        :param other_exception_return: return if Exception, others than the exceptions, are caught
        :param retry: how many times to retry
        :param countdown: retry interval, measure by second
        """
        super().__init__(
            func=func
        )
        self.exceptions = exceptions
        self.exception_return = exception_return
        self.other_exception_return = other_exception_return
        self.retry = retry
        self.countdown = countdown
        self.verbose = verbose

    def __call__(self, func, instance, *call_args, **call_kwargs):
        func = self.func if self.func else call_args[0]

        @functools.wraps(func)
        def wrapped_function(*args, **kwargs):
            for retry_num in range(self.retry):

                ## execute countdown
                if retry_num > 0:
                    print(f"Encounter Exception Retrying in {self.countdown} seconds")
                    time.sleep(self.countdown)

                ## execute the func
                try:
                    if self.func:
                        res = self.call_func(func, *call_args, **call_kwargs)
                    else:
                        res = self.call_func(func, *args, **kwargs)
                    return res
                except self.exceptions as e:
                    log(
                        level=self.verbose,
                        funcname=func.__name__,
                        benchmark=LOG_LEVEL["ALL"],
                        exception=e
                    )
                    continue
                except Exception as e:
                    log(
                        level=self.verbose,
                        funcname=func.__name__,
                        benchmark=LOG_LEVEL["NO exceptions"],
                        exception=e
                    )
                    return self.other_exception_return
            else:
                ## end of retry
                print(f"RUN OUT OF CHANCES: while operating func {func.__name__}")
                return self.exception_return

        return wrapped_function() if self.func else wrapped_function

    def __get__(self, instance, owner):
        return functools.partial(
            self.__call__,
            functools.partial(self.func, instance),
            instance
        )

if __name__ == '__main__':

    import asyncio

    # @Retrier(
    #     exceptions=(KeyError,),
    #     verbose=3,
    #     countdown=3,
    # )
    @Retrier
    # async def test1(*args, **kwargs):
    def test1(*args, **kwargs):
        print("Starting test")
        print(locals())
        raise KeyError
    # async def test1(*args, **kwargs):
    #     print("Starting test")
    #     print(locals())
    #     raise KeyError

    test1(1, 2, a=3, b=4)


    class A:
        target = 123

        # @Retrier(
        #     exceptions=(KeyError,),
        #     verbose=3,
        #     countdown=3,
        # )
        @Retrier
        def test2(self, a, b):
        # async def test1(self, a, b):
            print(a)
            print(b)

    # aa = A()
    # asyncio.run(aa.test2(1, 2))

