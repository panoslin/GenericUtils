#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 9/11/19
# IDE: PyCharm

import redis
import config


def redis_connection(host=config.redis_host,
                     port=config.redis_port,
                     password=config.redis_auth,
                     db=config.redis_db,
                     decode_responses=True):
    return redis.Redis(host=host,
                       port=port,
                       password=password,
                       db=db,
                       decode_responses=decode_responses)


if __name__ == '__main__':
    pass
