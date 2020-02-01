#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by panos on 2019/7/2
# IDE: PyCharm


from aiohttp.client_exceptions import (ServerConnectionError,
                                       ClientOSError,
                                       ClientConnectorCertificateError,
                                       ClientPayloadError
                                       )
from requests.exceptions import (
    ConnectionError,
    Timeout,
)
from mysql.connector.errors import (OperationalError,
                                    ProgrammingError,
                                    DatabaseError,
                                    InterfaceError)
import asyncio

http_exception = (
    asyncio.TimeoutError,
    ServerConnectionError,
    ClientPayloadError,
    ClientConnectorCertificateError,
    ClientOSError,
    ConnectionError,
    Timeout,
)

mysql_exception = (
    OperationalError,
    ProgrammingError,
    DatabaseError,
    InterfaceError
)
