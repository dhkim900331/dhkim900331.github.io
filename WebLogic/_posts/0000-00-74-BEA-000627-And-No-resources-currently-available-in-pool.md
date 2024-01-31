---
date: 2023-12-14 17:56:01 +0900
layout: post
title: "[WebLogic/Datasource] BEA-000627 And No resources currently available in pool"
tags: [Middleware, WebLogic, Datasource, Connection Pool, JDBC]
typora-root-url: ..
---

# 1. Overview
BEA-000627 Reached maximum capacity of pool "{0}", making "{2}" new resource instances instead of "{1}" 메시지와 No resources currently available in pool 메시지간의 차이점을 알아본다.

{{ site.content.br_big }}

# 2. Descriptions
BEA-000627 메시지와 No resources currently available in pool 은 기본적으로, Datasource connection pool 에 available connection이 부족한 상황에서 발생할 수 있다.

그러나 항상, 부족한 상황에서만 나오는 것은 아니기에 두 메시지가 다른 타이밍에 출력될 수 있다.



상황 재현을 위해 Pool Min/Max 가 2/2 인 환경에서,

많은 요청 유입으로 Available connection이 부족한 타이밍에 아래의 메시지가 추가 요청마다  기록된다.

```
<Nov 28, 2023 1:03:20,626 PM KST> <Info> <Common> <BEA-000627> <Reached maximum capacity of pool "Oracle", making "0" new resource instances instead of "1".>
<Nov 28, 2023 1:03:23,595 PM KST> <Info> <Common> <BEA-000627> <Reached maximum capacity of pool "Oracle", making "0" new resource instances instead of "1".>
<Nov 28, 2023 1:03:27,593 PM KST> <Info> <Common> <BEA-000627> <Reached maximum capacity of pool "Oracle", making "0" new resource instances instead of "1".>
```

위는 실제로, 총 5개의 동시 요청이 유입되었을 때이다.



BEA-000627 메시지를 유발한 추가 요청들은,

Connection Reserve Timeout (기본값 10s) 동안 Connection 을 기다리다가

얻지 못하였을 때 아래와 같은 메시지를 기록하며 실패한다.

```
weblogic.jdbc.extensions.PoolLimitSQLException:
  weblogic.common.resourcepool.ResourceLimitException:
    No resources currently available in pool Oracle to allocate to applications, please increase the size of the pool and retry..
      at weblogic.jdbc.common.internal.JDBCUtil.wrapAndThrowResourceException(JDBCUtil.java:290)
      at weblogic.jdbc.pool.Driver.connect(Driver.java:154)
      at weblogic.jdbc.jts.Driver.getNonTxConnection(Driver.java:665)
      at weblogic.jdbc.jts.Driver.connect(Driver.java:129)
      at weblogic.jdbc.common.internal.WLDataSourceImpl.getConnectionInternal(WLDataSourceImpl.java:655)
      at weblogic.jdbc.common.internal.WLDataSourceImpl.getConnection(WLDataSourceImpl.java:611)
      at weblogic.jdbc.common.internal.WLDataSourceImpl.getConnection(WLDataSourceImpl.java:604)
      at weblogic.jdbc.common.internal.RmiDataSource.getConnection(RmiDataSource.java:108)
      at jsp_servlet.__sql._jspService(__sql.java:100)
      ...
      at weblogic.work.ExecuteThread.run(ExecuteThread.java:360)
```



BEA-000627 메시지는 Log가 기록될 당시, Available Connection 수 보다 많은 요청이 유입되었을 때 기록되는 것이고

No resources currently available in pool 메시지는 Available Connection 이 없는 상황에서, 10초 이후에도 Connection을 얻지 못했을 때 발생하지만,

Available Connection이 있더라도, Connection을 너무 느리게 할당 받는 slow timing issue 로도 충분히 발생할 수 있다.



그러므로, 단순히 Pool에 Connection이 부족하다고 하여 반드시 두 메시지가 나란히 기록되어야 하는 것은 아니다.

{{ site.content.br_big }}

# 3. References

[BEA-000001 to BEA-2194843](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/fmerr/bea-000001-bea-2194843.html)

**BEA-000627 Reached maximum capacity of pool 메시지와 No resources currently available in pool 의 차이점 (Doc ID 2999836.1)**
