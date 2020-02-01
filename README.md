# GenericUtils
##### A module contains utils that are imported frequently


  
1. Retrier
2. RequestRetry
3. MysqlRetry
4. get_host_ip
5. pager
6. redis_connection
7. user_agent


##### demonstration
  
1. Retrier    

    A universial class decorator for both coroutine function and normal function.   
    It catches `exceptions` declares specifically by user in the arguments of the decorator, and retries it by stated `retry` time and `countdown` between every retry if one of the `exceptions` occurs.
    It will not do anything as long as the function run smoothly, or else `exception_return` will be return when the retry time exhausts or return `other_exception_return` if any Exception, others than the `exceptions`, are caught.
    
    Demo:  
    
    ```python
    
    from GenericUtils import Retrier  
    
    ## decorate normal function
    @Retrier(
        exceptions=(KeyError,),
        exception_return=False,
        other_exception_return=False,
        retry=3,
        countdown=0,
    )
    def test1(*args, **kwargs):
        print("Starting test")
        raise KeyError

    test1(1, 2, a=3, b=4)




    ## decorate coroutine function
    @Retrier(
        exceptions=(KeyError,)
    )
    async def test2(*args, **kwargs):
        print("Starting test")
        raise KeyError
    ## call it like normal function
    test2(1, 2, a=3, b=4)
    ```
2. RequestRetry    

    A universial class decorator for both coroutine function and normal function.   
    It catches `http_exception` define in GenericUtils.utils.exception, and retries it by stated `retry` time and sleep `5` seconds between every retry if one of the `http_exception` occurs.
    It will not do anything as long as the function run smoothly, or else `exception_return` will be return when the retry time exhausts or return `other_exception_return` if any Exception, others than the `exceptions`, are caught.
    
    Demo:  
    
    ```python
    from GenericUtils import RequestRetry  
    from aiohttp.client_exceptions import ServerDisconnectedError
    from requests.exceptions import ConnectionError
 
 
    ## decorate normal function
    @RequestRetry(
        exception_return=False,
        other_exception_return=False,
        retry=3,
     )
    def test3(*args, **kwargs):
        print("Starting test")
        raise ConnectionError
     
    test3(1, 2, a=3, b=4)



    ## decorate coroutine function
    @RequestRetry(
        exception_return=False,
        other_exception_return=False,
        retry=3,
     )
    async def test4(*args, **kwargs):
        print("Starting test")
        raise ServerDisconnectedError

    test4(1, 2, a=3, b=4)
    ```
3. MysqlRetry    

    It catches `mysql_exception` define in GenericUtils.utils.exception, and retries it by stated `retry` time and sleep `30` seconds between every retry if one of the `mysql_exception` occurs.
    It will construct the mysql connector and cursor by mysql.connector before we execute the function, and commit & close the connection after the function finishes.
    If one of `mysql_exception` occurs, rollback the cursor and retry. `exception_return` will be returned when the retry time exhausts.
    If any others Exception occurs, rollback the cursor and return `other_exception_return`.
    
    Demo:  
    
    ```python
    from GenericUtils import MysqlRetry  
    from mysql.connector.errors import OperationalError
     
    @MysqlRetry(
        exception_return=False,
        other_exception_return=False,
        retry=3,
        host = "127.0.0.1",
        port = "3306",
        user_name = "user_name",
        password = "password",
        database = "database",
     )
    def test5(*args, **kwargs):
        print("Starting test")
        conn, cur = kwargs["conn"], kwargs["cur"]
        cur.execute(
           operation="SELECT * FROM TABLE_NAME"
        )
        results = cur.fetchall()
        print(results[0])
        raise OperationalError
     
    test5(1, 2, a=3, b=4)
    ```
4. get_host_ip    

    get local ip addr
    
    Demo:  
    
    ```python
    from GenericUtils import get_host_ip  
    ip = get_host_ip()
    print(ip)
    ```
5. pager    

    paging util
    
    Demo:  
    
    ```python
    from GenericUtils import pager  
    for _ in pager(5, 61, 20):
        print(_)
    ```
6. redis_connection    

    redis connection
    
    Demo:  
    
    ```python
    from GenericUtils import redis_connection  
    connection = redis_connection(host="127.0.0.1",
                                  port="6379",
                                  password="password",
                                  db=0,
                                  decode_responses=True
                  )
    connection.sadd("test", 1)
    ```
7. user_agent