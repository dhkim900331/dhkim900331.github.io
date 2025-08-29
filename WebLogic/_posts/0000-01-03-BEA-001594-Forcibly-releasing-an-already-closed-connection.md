---
date: 2025-01-02 23:04:36 +0900
layout: post
title: "[WebLogic] BEA-001594: Forcibly releasing an already closed connection back into the data source connection pool"
tags: [Middleware, WebLogic, Connection Pool, Datasource]
typora-root-url: ..
---

# 1. Overview

`<Warning> <JDBC> <BEA-001594> <Forcibly releasing an already closed connection "weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@34" back into the data source connection pool "orcl".>`

발생 원인


<br><br>


# 2. Descriptions

[BEA Messages](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/fmerr/bea-000001-bea-2194843.html) 기본적인 설명에 따르면,

`BEA-001594`은 이미 닫힌 커넥션을 사용하려 할 때, WLS 가 이를 다시 Datasource로 돌려 보내며 발생하는 Warning 메시지다.

<br>

일반적으로 발생하는 시나리오는, Application이 Datasource로 부터 Connection을 받은 뒤,

DB Server가 Restart 되거나, Network 문제로 DB Server와 연결되어 있던 Socket Connection이 영향을 받게 되면

Application이 가지고 있던 Connection은 Stale하므로 사용하려 할 때, 발생한다.

<br>

WLS 수준에서 해결 방법은, Test Frequency 는 해당 사이클 사이를 감지하지 못하므로, Test Connections on Reserver를 활성화 한다.

<br>

## 2.1 Reproduction

재현을 위해서

다음의 Datasource 설정을 구성한다.

```
Initial Capacity/Maximum Capacity : 1/15
Test Connections On Reserve : Unchecked
Test Frequency : 0
```

<br>

Datasource는 Initial 만큼의 Connection이 준비된다.

```
<Info> <Common> <BEA-000628> <Created "1" resources for pool "orcl", out of which "1" are available and "0" are unavailable.>
```

<br>

 다음의 `sql.jsp`를 호출하여, Application이 정상 Connection을 얻고 sleep 상태에 들어간다.

```jsp
conn = ds.getConnection();
stmt = conn.createStatement();
Thread.sleep(120000);
rs = stmt.executeQuery("SELECT * FROM emp");
rs.close()
stmt.close()
conn.close()
```

<br>

DB Server를 재시작한다.

<br>

jsp가 120초 Sleep에서 깨어난 후, Socket이 사라졌으므로 Exception이 발생한다.

Exception이 발생한 App은 처리가 종료되고, Connection은 Pool로 복귀된다.

```
java.sql.SQLRecoverableException: No more data to read from socket
        at oracle.jdbc.driver.T4CMAREngineNIO.prepareForUnmarshall(T4CMAREngineNIO.java:784)
        at oracle.jdbc.driver.T4CMAREngineNIO.unmarshalUB1(T4CMAREngineNIO.java:429)
        at oracle.jdbc.driver.T4CTTIfun.receive(T4CTTIfun.java:407)
        at oracle.jdbc.driver.T4CTTIfun.doRPC(T4CTTIfun.java:268)
        at oracle.jdbc.driver.T4C8Oall.doOALL(T4C8Oall.java:655)
        at oracle.jdbc.driver.T4CStatement.doOall8(T4CStatement.java:229)
        at oracle.jdbc.driver.T4CStatement.doOall8(T4CStatement.java:41)
        at oracle.jdbc.driver.T4CStatement.executeForDescribe(T4CStatement.java:765)
        at oracle.jdbc.driver.OracleStatement.executeMaybeDescribe(OracleStatement.java:983)
        at oracle.jdbc.driver.OracleStatement.doExecuteWithTimeout(OracleStatement.java:1168)
        at oracle.jdbc.driver.OracleStatement.executeQuery(OracleStatement.java:1362)
        at oracle.jdbc.driver.OracleStatementWrapper.executeQuery(OracleStatementWrapper.java:369)
        at weblogic.jdbc.wrapper.Statement.executeQuery(Statement.java:499)
        at jsp_servlet.__sql._jspService(__sql.java:105)
```

<br>

jsp 재 호출 시, Datasource 에서 다시 Connection을 얻지만 여전히, Stale 하기 때문에 Exception이 재현된다.

```
<Warning> <JDBC> <BEA-001594> <Forcibly releasing an already closed connection "weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@34" back into the data source connection pool "orcl".>
java.sql.SQLException: Attempt to set connection harvestable to false but the connection is already closed.
        at weblogic.jdbc.wrapper.Connection.setConnectionHarvestable(Connection.java:1592)
        at weblogic.jdbc.common.internal.WLDataSourceImpl.getConnectionInternal(WLDataSourceImpl.java:690)
        at weblogic.jdbc.common.internal.WLDataSourceImpl.getConnection(WLDataSourceImpl.java:611)
        at weblogic.jdbc.common.internal.WLDataSourceImpl.getConnection(WLDataSourceImpl.java:604)
        at weblogic.jdbc.common.internal.RmiDataSource.getConnection(RmiDataSource.java:108)
        at jsp_servlet.__sql._jspService(__sql.java:100)
```

<br>

Datasource의 Test Frequency 를 설정한다.

```
Initial Capacity/Maximum Capacity : 1/15
Test Connections On Reserve : Unchecked
Test Frequency : 240
```

```
<Dec 18, 2024 12:30:34,594 PM KST> <Info> <Common> <BEA-000626> <Free resources in pool "orcl" will be tested every "240" seconds.>
<Info> <Common> <BEA-000628> <Created "1" resources for pool "orcl", out of which "1" are available and "0" are unavailable.>
```

```
# Sleep 에서 깨어난 이후 동일한 Exception
java.sql.SQLRecoverableException: No more data to read from socket
```

<br>

JSP 재차 호출 시, Test Frequency (240초) 사이클이 지나, 건전한 Connection으로 교체될 때 까지 발생한다.

```
<Dec 18, 2024 12:32:47,908 PM KST> <Warning> <JDBC> <BEA-001594> <Forcibly releasing an already closed connection "weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@55" back into the data source connection pool "orcl".>
...
<Dec 18, 2024 12:34:32,608 PM KST> <Warning> <JDBC> <BEA-001594> <Forcibly releasing an already closed connection "weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@5c" back into the data source connection pool "orcl".>
```

<br>

Stale connection이 Testing 되고 정리된다.

```
<Dec 18, 2024 12:34:34,712 PM KST> <Error> <JDBC> <BEA-001112> <Test "ISVALID" set up for pool "orcl" failed with exception: "isValid returns false".>
<Dec 18, 2024 12:34:34,713 PM KST> <Info> <JDBC> <BEA-001128> <Connection for pool "orcl" has been closed.> 
```


<br><br>

<br>

# 3. References

**BEA-001594: Forcibly releasing an already closed connection back into the data source connection pool (Doc ID 3064270.1)**
