#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2020/1/20
# IDE: PyCharm


import traceback
import wrapt
import functools
# import inspect
# import asyncio


def retrier(wrapped=None,
            exceptions=(Exception,),
            exception_return=False,
            other_exception_return=False,
            retry=3,
            ):
    if wrapped is None:
        return functools.partial(retrier,
                                 exceptions=exceptions,
                                 exception_return=exception_return,
                                 other_exception_return=other_exception_return,
                                 retry=retry,
                                 )

    @wrapt.decorator
    def wrapper(func, instance, args, kwargs):

        # iscoroutinefunction = inspect.iscoroutinefunction(func)

        for _ in range(retry):
            try:
                # if iscoroutinefunction:
                #     loop = asyncio.new_event_loop()
                #     asyncio.set_event_loop(loop)
                #     res = loop.run_until_complete(func(*args, **kwargs))
                #     loop.close()
                # else:
                res = func(*args, **kwargs)
            except exceptions:
                traceback.print_exc()
                continue
            except:
                traceback.print_exc()
                return other_exception_return
            else:
                return res
        else:
            return exception_return

    return wrapper(wrapped)


def async_retrier(wrapped=None,
                  exceptions=(Exception,),
                  exception_return=False,
                  other_exception_return=False,
                  retry=3,
                  ):
    if wrapped is None:
        return functools.partial(async_retrier,
                                 exceptions=exceptions,
                                 exception_return=exception_return,
                                 other_exception_return=other_exception_return,
                                 retry=retry,
                                 )

    @wrapt.decorator
    async def wrapper(func, instance, args, kwargs):

        # iscoroutinefunction = inspect.iscoroutinefunction(func)

        for _ in range(retry):
            try:
                res = await func(*args, **kwargs)
                # if iscoroutinefunction:
                #     loop = asyncio.new_event_loop()
                #     asyncio.set_event_loop(loop)
                #     res = loop.run_until_complete(func(*args, **kwargs))
                #     loop.close()
                # else:
                #     res = func(*args, **kwargs)
            except exceptions:
                traceback.print_exc()
                continue
            except:
                traceback.print_exc()
                return other_exception_return
            else:
                return res
        else:
            return exception_return

    return wrapper(wrapped)
