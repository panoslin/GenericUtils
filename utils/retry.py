#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2020/1/20
# IDE: PyCharm


import traceback
import inspect
import asyncio
import functools
import time
from GenericUtils.utils.exception import (
    http_exception,
    mysql_exception,
)
from GenericUtils import utils_config
import mysql.connector


class Retrier:

    def __init__(
            self,
            exceptions=(Exception,),
            exception_return=False,
            other_exception_return=False,
            retry=3,
            countdown=0,
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
                    print(f"Encounter Exception Retrying in {self.countdown} seconds")
                    time.sleep(self.countdown)

                ## execute the func
                try:
                    if iscoroutinefunction:
                        loop = asyncio.get_event_loop()
                        res = asyncio.ensure_future(func(*args, **kwargs), loop=loop)
                        # res = asyncio.run()
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


class RequestRetry(Retrier):

    def __init__(self, *args, **kwargs):
        Retrier.__init__(self, *args, **kwargs)
        self.exceptions = http_exception
        self.countdown = 5


class MysqlRetry(Retrier):

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

    def __call__(self, func):
        iscoroutinefunction = inspect.iscoroutinefunction(func)

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
                    if iscoroutinefunction:
                        res = asyncio.run(func(*args, **kwargs))
                    else:
                        res = func(*args, **kwargs)
                    kwargs['conn'].commit()
                    kwargs['cur'].close()
                    kwargs['conn'].close()
                    return res
                except self.exceptions:
                    traceback.print_exc()
                    if 'conn' in kwargs:
                        kwargs['conn'].rollback()
                        kwargs['cur'].close()
                        kwargs['conn'].close()
                    continue
                except:
                    traceback.print_exc()
                    if 'conn' in kwargs:
                        kwargs['conn'].rollback()
                        kwargs['cur'].close()
                        kwargs['conn'].close()
                    return self.other_exception_return
            else:
                ## end of retry
                ## return exception_return
                return self.exception_return

        return wrapped_function

    def connect(self):
        # Construct MySQL connect
        conn = mysql.connector.connect(
            user=self.user_name,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            charset=self.charset,
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

    # @Retrier(
    #     exceptions=(KeyError,)
    # )
    # def test1(*args, **kwargs):
    #     print("Starting test")
    #     # raise KeyError
    #
    #
    # test1(1, 2, a=3, b=4)

    # @Retrier(
    #     exceptions=(KeyError,)
    # )
    # async def test2(*args, **kwargs):
    #     print("Starting test")
    #     raise KeyError
    #
    # test2(1, 2, a=3, b=4)

    # from aiohttp.client_exceptions import ServerDisconnectedError
    #
    # @RequestRetry()
    # async def test3(*args, **kwargs):
    #     print("Starting test")
    #     raise ServerDisconnectedError
    #
    #
    # test3(1, 2, a=3, b=4)
