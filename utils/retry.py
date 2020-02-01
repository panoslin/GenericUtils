#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2020/1/20
# IDE: PyCharm


import traceback
import inspect
import asyncio
import functools
import time


class retrier:

    def __init__(
            self,
            exceptions=(Exception,),
            exception_return=False,
            other_exception_return=False,
            retry=3,
            countdown=0,
    ):
        """

        :param exceptions: Exception to be catch specifically
        :param exception_return: return if exceptions are caught
        :param other_exception_return: return if Exception, others than exceptions, are caught
        :param retry: how many time to retry
        :param countdown: retry interval
        """
        self.exceptions = exceptions
        self.exception_return = exception_return
        self.other_exception_return = other_exception_return
        self.retry = retry
        self.countdown = countdown

    def __call__(self, func):
        iscoroutinefunction = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        def wrapped_function(*args, **kwargs):
            for retry_num in range(self.retry):

                ## execute countdown
                if retry_num > 0:
                    time.sleep(self.countdown)

                ## execute the func
                try:
                    if iscoroutinefunction:
                        res = asyncio.run(func(*args, **kwargs))
                    else:
                        res = func(*args, **kwargs)
                    return res
                except self.exceptions:
                    traceback.print_exc()
                    continue
                except:
                    traceback.print_exc()
                    return self.other_exception_return
            else:
                ## end of retry
                ## return exception_return
                return self.exception_return

        return wrapped_function


if __name__ == '__main__':
    # @retrier(
    #     exceptions=(KeyError,)
    # )
    # def test1(*args, **kwargs):
    #     print("Starting test")
    #     raise KeyError
    #
    #
    # test1(1, 2, a=3, b=4)

    @retrier(
        exceptions=(KeyError,)
    )
    async def test2(*args, **kwargs):
        print("Starting test")
        raise KeyError


    test2(1, 2, a=3, b=4)
