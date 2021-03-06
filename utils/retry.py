#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2020/1/20
# IDE: PyCharm


from GenericUtils.utils.exception import (
    http_exception,
    mysql_exception,
)
from GenericUtils.base.base_decorator import BaseDecorator
from GenericUtils import utils_config
import mysql.connector
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


def check_argument(func):
    """
    Decorate __call__ function in the class decorator
    prep the argument right for differerent condition:
    1. decorator with/without argument
    2. decorate function/class function (which will call __get__ before __call__)
    :param func:
    :return:
    """

    def wrapper(*args, **kwargs):
        if len(args) == 2 and issubclass(args[0].__class__, BaseDecorator) and hasattr(args[1], '__call__'):
            ## decorate a class function
            args[0].func = args[1]
            return args[0]
        elif len(args) >= 2 and issubclass(args[0].__class__, BaseDecorator) and hasattr(args[1], '__call__'):
            ## decorate a class function
            return func(args[0], args[1], args[2], *args[3:], **kwargs)
        else:
            ## decorate a function
            return func(args[0], None, None, *args[1:], **kwargs)
            # return func(*args, **kwargs)

    return wrapper


class Retrier(BaseDecorator):
    """
    A universal decorator providing retrying feature

    Suppoorting:
    1. decorator with/without argument
    2. decorate function/instance's function (which will call __get__ before __call__)
    3. decrate async/sync function
    """
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
            func=func,
        )
        self.exceptions = exceptions
        self.exception_return = exception_return
        self.other_exception_return = other_exception_return
        self.retry = retry
        self.countdown = countdown
        self.verbose = verbose

    @check_argument
    def __call__(self, func, instance, *call_args, **call_kwargs):
        """
        If you inherit this class(Retrier) and need the universal feature,
        try not to forget the @check_argument decorator
        :param func:
        :param instance:
        :param call_args:
        :param call_kwargs:
        :return:
        """

        func = self.func if self.func else call_args[0]
        iscoroutinefunction = self.is_coroutine_funciton(obj=func)

        ## decorate async function
        @functools.wraps(func)
        async def wrapped_async(*args, **kwargs):
            args, kwargs = (call_args, call_kwargs) if self.func else (args, kwargs)
            return await self.retry_async(
                func,
                *args,
                **kwargs
            )

        ## decorate sync function
        @functools.wraps(func)
        def wrapped_sync(*args, **kwargs):
            args, kwargs = (call_args, call_kwargs) if self.func else (args, kwargs)
            return self.retry_sync(
                func,
                *args,
                **kwargs
            )

        if iscoroutinefunction:
            return wrapped_async() if self.func else wrapped_async
        else:
            return wrapped_sync() if self.func else wrapped_sync

    async def retry_async(self, func, *args, **kwargs):
        for retry_num in range(self.retry):

            ## execute countdown
            if retry_num > 0:
                print(f"Encounter Exception Retrying in {self.countdown} seconds")
                await asyncio.sleep(self.countdown)

            ## execute the func
            try:
                res = await func(*args, **kwargs)
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

    def retry_sync(self, func, *args, **kwargs):
        for retry_num in range(self.retry):

            ## execute countdown
            if retry_num > 0:
                print(f"Encounter Exception Retrying in {self.countdown} seconds")
                time.sleep(self.countdown)

            ## execute the func
            try:
                res = self.call_sync(
                    func,
                    *args,
                    **kwargs
                )
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


class RequestRetry(Retrier):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        kwargs = {
            **{
                "countdown": 5,
                "verbose": 2,
            },
            **kwargs
        }
        super().__init__(
            *args,
            **kwargs
        )
        self.exceptions = http_exception


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
        kwargs = {
            **{
                "countdown": 30,
            },
            **kwargs
        }
        super().__init__(
            *args,
            **kwargs
        )
        self.exceptions = http_exception
        self.host = kwargs.get("host") if "host" in kwargs else utils_config.host
        self.port = kwargs.get("port") if "port" in kwargs else utils_config.port
        self.user_name = kwargs.get("user_name") if "user_name" in kwargs else utils_config.user_name
        self.password = kwargs.get("password") if "password" in kwargs else utils_config.password
        self.database = kwargs.get("database") if "database" in kwargs else utils_config.database
        self.charset = kwargs.get("charset") if "charset" in kwargs else "utf8"
        self.dictionary = kwargs.get("dictionary") if "dictionary" in kwargs else True

    async def retry_async(self, func, *args, **kwargs):
        for retry_num in range(self.retry):

            ## execute countdown
            if retry_num > 0:
                print(f"Encounter Exception Retrying in {self.countdown} seconds")
                await asyncio.sleep(self.countdown)

            ## execute the func
            try:
                kwargs['conn'], kwargs['cur'] = self.connect()
                res = await func(*args, **kwargs)
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

    def retry_sync(self, func, *args, **kwargs):
        for retry_num in range(self.retry):

            ## execute countdown
            if retry_num > 0:
                print(f"Encounter Exception Retrying in {self.countdown} seconds")
                time.sleep(self.countdown)

            ## execute the func
            try:
                kwargs['conn'], kwargs['cur'] = self.connect()
                res = self.call_sync(
                    func,
                    *args,
                    **kwargs
                )
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
    import asyncio


    # # @Retrier(
    # #     exceptions=(KeyError,),
    # #     verbose=3,
    # #     countdown=3
    # # )
    # @Retrier
    # async def test1(*args, **kwargs):
    # # def test1(*args, **kwargs):
    #     print("Starting test")
    #     print(locals())
    #     raise KeyError

    # test1(1, 2, 5, a=3, b=4)
    # asyncio.run(test1(1, 2, 3, a=3, b=4))

    # class A:
    #     target = 123
    #
    #     @Retrier(
    #         exceptions=(KeyError,),
    #         verbose=3,
    #         countdown=3,
    #     )
    #     # @Retrier
    #     # def test2(self, *args, **kwargs):
    #     async def test2(self, *args, **kwargs):
    #         print("Starting test")
    #         print(locals())
    #         raise KeyError

    # aa = A()
    # aa.test2(1, 2, 5, a=3, b=4)
    # asyncio.run(aa.test2(1, 2, 3, a=3, b=4))

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

    # @MysqlRetry(
    #     host='127.0.0.1',
    #     port=3306,
    #     user_name='root',
    #     password='root',
    #     database='test_database'
    # )
    # def test1(*args, **kwargs):
    # # async def test1(*args, **kwargs):
    #     print(locals())
    #     cur, conn = kwargs['cur'], kwargs['conn']
    #     cur.execute(
    #         operation='''
    #             SELECT * FROM `TABLE`;
    #         '''
    #     )
    #     result = cur.fetchall()
    #     return result


    # print(test1(1, 2, 3, a=3, b=4))
    # print(asyncio.run(test1(1, 2, 3, a=3, b=4)))


    class A:
        target = 123

        @MysqlRetry(
            host='127.0.0.1',
            port=3306,
            user_name='root',
            password='root',
            database='test_database'
        )
        # def test2(self, *args, **kwargs):
        async def test2(self, *args, **kwargs):
            print(locals())
            cur, conn = kwargs['cur'], kwargs['conn']
            cur.execute(
                operation='''
                    SELECT * FROM `TABLE`;
                '''
            )
            result = cur.fetchall()
            return result

    aa = A()
    # print(aa.test2(1, 2, 5, a=3, b=4))
    print(asyncio.run(aa.test2(1, 2, 3, a=3, b=4)))
