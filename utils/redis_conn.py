#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 9/11/19
# IDE: PyCharm
try:
    import redis
except ModuleNotFoundError:
    pass
from GenericUtils import utils_config


def redis_connection(host=utils_config.redis_host,
                     port=utils_config.redis_port,
                     password=utils_config.redis_auth,
                     db=utils_config.redis_db,
                     decode_responses=utils_config.redis_decode_responses):
    return redis.Redis(host=host,
                       port=port,
                       password=password,
                       db=db,
                       decode_responses=decode_responses)


if __name__ == '__main__':
    pass
