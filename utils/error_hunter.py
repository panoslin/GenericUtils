#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/6
# IDE: PyCharm

import traceback
import wrapt
import functools



def ErrorHunter(wrapped=None,
                 default_exception_return=False,
                 ):
    if wrapped is None:
        return functools.partial(ErrorHunter,
                                 default_exception_return=default_exception_return,
                                 )

    @wrapt.decorator
    def wrapper(func, instance, args, kwargs):

        try:
            return func(*args, **kwargs)
        except:
            traceback.print_exc()
            return default_exception_return

    return wrapper(wrapped)