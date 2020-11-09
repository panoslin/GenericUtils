#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/2
# IDE: PyCharm


try:
    from aiohttp.client_exceptions import (ServerConnectionError,
                                           ClientOSError,
                                           ClientConnectorCertificateError,
                                           ClientPayloadError,
                                           ClientConnectorError
                                           )
except ModuleNotFoundError:
    pass

try:
    from requests.exceptions import (
        ConnectionError,
        Timeout,
    )
except ModuleNotFoundError:
    pass

try:
    from mysql.connector.errors import (
        OperationalError,
        InterfaceError
    )
except ModuleNotFoundError:
    pass

import asyncio

http_exception = (
    asyncio.TimeoutError,
    ServerConnectionError,
    ClientPayloadError,
    ClientConnectorCertificateError,
    ClientOSError,
    ConnectionError,
    Timeout,
    ClientConnectorError,
)

mysql_exception = (
    OperationalError,
    InterfaceError
)
