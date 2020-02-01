#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/5
# IDE: PyCharm

import socket

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
    except:
        return '0.0.0.0'
    else:
        try:
            ip = s.getsockname()[0]
        except:
            ip = '0.0.0.0'
        s.close()
        return ip