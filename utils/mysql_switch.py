#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 11/13/18
# IDE: PyCharm

import mysql.connector
import traceback
import wrapt
import functools
import config
from raven.utils.exception import mysql_exception


def MysqlRetry(wrapped=None,
               default_exception_return=False,
               default_other_exception_return=False,
               host=config.host,
               port=config.port,
               user_name=config.user_name,
               password=config.password,
               database=config.database,
               ):
    """
    work as a decorator
    providing keywork arguments for the decorated function
    containg kwargs['conn'] and kwargs['cur'],
    which are the MySQLConnection object and cursor object from mysql-connector-python, respectively.

    """
    if wrapped is None:
        return functools.partial(MysqlRetry,
                                 default_exception_return=default_exception_return,
                                 default_other_exception_return=default_other_exception_return,
                                 host=host,
                                 port=port,
                                 user_name=user_name,
                                 password=password,
                                 database=database,
                                 )

    @wrapt.decorator
    def wrapper(func, instance, args, kwargs):
        for _ in range(config.RETRY):
            try:
                kwargs['conn'], kwargs['cur'] = connect(
                    host=host,
                    port=port,
                    user_name=user_name,
                    password=password,
                    database=database,
                    charset='utf8',
                )
                res = func(*args, **kwargs)
            except mysql_exception:
                traceback.print_exc()
                kwargs['conn'].rollback()
                kwargs['cur'].close()
                kwargs['conn'].close()
                continue
            except:
                traceback.print_exc()
                kwargs['conn'].rollback()
                kwargs['cur'].close()
                kwargs['conn'].close()
                return default_other_exception_return
            else:
                kwargs['conn'].commit()
                kwargs['cur'].close()
                kwargs['conn'].close()
                return res
        else:
            return default_exception_return

    return wrapper(wrapped)


def connect(host, port, user_name, password, database, dictionary=True, charset='utf8'):
    # Construct MySQL connect
    conn = mysql.connector.connect(
        user=user_name,
        password=password,
        host=host,
        port=port,
        database=database,
        charset=charset,
    )
    cur = conn.cursor(dictionary=dictionary)
    return conn, cur


def close(conn, cur):
    cur.close()
    conn.close()


def commit(conn):
    conn.commit()


def rollback(conn):
    conn.rollback()
