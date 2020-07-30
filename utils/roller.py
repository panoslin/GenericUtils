#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2020/7/30
# IDE: PyCharm

def roller(iterable, interval=10):
    page = 0
    while True:
        a, b = page * interval, page * interval + interval
        page += 1
        if a < len(iterable):
            yield iterable[a:b]
        else:
            break