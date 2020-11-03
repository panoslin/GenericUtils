#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2020/1/20
# IDE: PyCharm


import traceback
import functools
import time
from GenericUtils.base.base_decorator import BaseDecorator
from GenericUtils.utils.exception import (
    http_exception,
    mysql_exception,
)
from GenericUtils import utils_config
import mysql.connector
from functools import partial

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
        functools.update_wrapper(self, func)
        self.exceptions = exceptions
        self.exception_return = exception_return
        self.other_exception_return = other_exception_return
        self.retry = retry
        self.countdown = countdown
        self.verbose = verbose

    def __call__(self, func, instance, *call_args, **call_kwargs):
        func = self.func if self.func else call_args[0]

        # @functools.wraps(func)
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
        return partial(
            self.__call__,
            partial(self.func, instance),
            instance
        )

class RequestRetry(Retrier):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs
        )
        self.exceptions = http_exception
        self.countdown = 5
        self.verbose = 3

    def __get__(self, instance, owner):
        return partial(
            self.__call__,
            partial(self.func, instance),
            instance
        )

class MysqlRetry(Retrier):
    __slots__ = (
        'host',
        'port',
        'user_name',
        'password',
        'database',
        'charset',
        'dictionary',
    )

    def __init__(self, *args, **kwargs):
        Retrier.__init__(self, *args, **kwargs)
        self.exceptions = mysql_exception
        self.countdown = 30

        self.host = kwargs.get("host") if "host" in kwargs else utils_config.host
        self.port = kwargs.get("port") if "port" in kwargs else utils_config.port
        self.user_name = kwargs.get("user_name") if "user_name" in kwargs else utils_config.user_name
        self.password = kwargs.get("password") if "password" in kwargs else utils_config.password
        self.database = kwargs.get("database") if "database" in kwargs else utils_config.database
        self.charset = kwargs.get("charset") if "charset" in kwargs else "utf8"
        self.dictionary = kwargs.get("dictionary") if "dictionary" in kwargs else True

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
                    kwargs['conn'], kwargs['cur'] = self.connect()
                    if self.func:
                        res = self.call_func(func, *call_args, **call_kwargs)
                    else:
                        res = self.call_func(func, *args, **kwargs)
                    kwargs['conn'].commit()
                    kwargs['cur'].close()
                    kwargs['conn'].close()
                    return res
                except self.exceptions as e:
                    log(
                        level=self.verbose,
                        funcname=func.__name__,
                        benchmark=LOG_LEVEL["ALL"],
                        exception=e
                    )
                    if 'conn' in kwargs:
                        kwargs['conn'].rollback()
                        kwargs['cur'].close()
                        kwargs['conn'].close()
                    continue
                except Exception as e:
                    log(
                        level=self.verbose,
                        funcname=func.__name__,
                        benchmark=LOG_LEVEL["NO exceptions"],
                        exception=e
                    )
                    if 'conn' in kwargs:
                        kwargs['conn'].rollback()
                        kwargs['cur'].close()
                        kwargs['conn'].close()
                    return self.other_exception_return
            else:
                ## end of retry
                print(f"RUN OUT OF CHANCES: while operating func {func.__name__}")
                return self.exception_return

        return wrapped_function() if self.func else wrapped_function

    def connect(self):
        # Construct MySQL connect
        conn = mysql.connector.connect(
            user=self.user_name,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            charset=self.charset,
            use_pure=True,
        )
        cur = conn.cursor(dictionary=self.dictionary)
        return conn, cur

    @staticmethod
    def close(conn, cur):
        cur.close()
        conn.close()

    @staticmethod
    def commit(conn):
        conn.commit()

    @staticmethod
    def rollback(conn):
        conn.rollback()


if __name__ == '__main__':
    pass

    # # @Retrier(
    # #     exceptions=(KeyError,),
    # #     verbose=3,
    # #     countdown=3,
    # # )
    # @Retrier
    # def test1(*args, **kwargs):
    #     print("Starting test")
    #     print(locals())
    #     raise KeyError
    # test1(1, 2, a=3, b=4)

    # @Retrier(
    #     exceptions=(KeyError,)
    # )
    # async def test2(*args, **kwargs):
    #     print("Starting test")
    #     print(locals())
    #     # raise KeyError
    #
    # test2(1, 2, a=3, b=4)

    # from aiohttp.client_exceptions import ServerDisconnectedError
    # # @RequestRetry(
    # #     countdown=2
    # # )
    # @RequestRetry
    # # async def test3(*args, **kwargs):
    # #     print("Starting test")
    # #     print(locals())
    # #     # raise ServerDisconnectedError
    # def test3(*args, **kwargs):
    #     print("Starting test")
    #     print(locals())
    #     raise ServerDisconnectedError
    # test3(1, 2, a=3, b=4)

    # with Retrier(exceptions=(KeyError,), ) as arya:
    #     print("Starting test")
    #     raise KeyError
