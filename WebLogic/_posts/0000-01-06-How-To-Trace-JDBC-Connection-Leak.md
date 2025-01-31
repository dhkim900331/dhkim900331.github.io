---
date: 2025-01-31 09:38:02 +0900
layout: post
title: "[WebLogic/JDBC] How To Trace JDBC Connection Leak"
tags: [Middleware, WebLogic, JDBC, Connection, Leak]
typora-root-url: ..
---

# 1. Overview

JDBC Connection Leak이 발생하는 상황에서의 추적 방법


<br><br>



# 2. Descriptions

일반적인 이야기(Connection의 close 선언부 확인, WLS의 inactive-connection-timeout 설정, 진단 이미지 캡쳐 기능 사용, DS의 connection leak profiling 옵션 활성화) 등은 많은 구글링 자료가 있다.

여기서는, 로그를 기반으로 하여 추적해본다.

<br>

다음과 같이 문제가 발생하지 않는, sql.jsp 를 준비하고,

```jsp
<%@ page import="java.sql.*, javax.naming.*, javax.sql.DataSource" %>
<%

	Connection conn = null;
	
	try {
		Context initContext = new InitialContext();
		DataSource ds = (DataSource) initContext.lookup("ORCLPDB");
		conn = ds.getConnection(); // 데이터베이스 연결
		System.out.println("[testApp:debug] [connection.getConnection()] " + conn);
    } catch (Exception e) {
        e.printStackTrace();
    } finally {
        try {
            if (conn != null) conn.close();
			if (conn.isClosed()) System.out.println("[testApp:debug] [connection.close()] " + conn);
        } catch (SQLException e) {
           e.printStackTrace();
        }
    }
%>
```

<br>

WLS Debug 항목을 활성화 한다.

```
Debug - weblogic - jdbc
 DebugJDBCConn, DDebugJDBCSQL
```

<br>

sql.jsp 호출 시에, 로그는 아래와 같다.

```
<Jan 23, 2025 9:51:59,127 AM KST> <Debug> <JDBCConn> <BEA-000000> <JTS/JDBC Connect: url = jdbc:weblogic:jts:orcl, tx = null, props = {EmulateTwoPhaseCommit=false, connectionPoolID=orcl, jdbcTxDataSource=true, LoggingLastResource=false, dataSourceName=orcl}>
<Jan 23, 2025 9:51:59,128 AM KST> <Debug> <JDBCConn> <BEA-000000> <Transaction = null. Returning an ordinary JDBC conn>
<Jan 23, 2025 9:51:59,128 AM KST> <Debug> <JDBCSQL> <BEA-000000> <[oracle.jdbc.driver.T4CConnection@166ea370] beginRequest()>
<Jan 23, 2025 9:51:59,128 AM KST> <Debug> <JDBCSQL> <BEA-000000> <[oracle.jdbc.driver.T4CConnection@166ea370] beginRequest returns>
<Jan 23, 2025 9:51:59,129 AM KST> <Debug> <JDBCSQL> <BEA-000000> <[weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@b] isClosed()>
<Jan 23, 2025 9:51:59,129 AM KST> <Debug> <JDBCSQL> <BEA-000000> <[weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@b] isClosed returns false>
[testApp:debug] [connection.getConnection()] weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@b
<Jan 23, 2025 9:51:59,129 AM KST> <Debug> <JDBCSQL> <BEA-000000> <[weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@b] close()>
<Jan 23, 2025 9:51:59,132 AM KST> <Debug> <JDBCSQL> <BEA-000000> <[oracle.jdbc.driver.T4CConnection@166ea370] endRequest()>
<Jan 23, 2025 9:51:59,133 AM KST> <Debug> <JDBCSQL> <BEA-000000> <[oracle.jdbc.driver.T4CConnection@166ea370] endRequest returns>
<Jan 23, 2025 9:51:59,133 AM KST> <Debug> <JDBCConn> <BEA-000000> <ConnectionEnv.cleanup, jconn=oracle.jdbc.driver.T4CConnection@166ea370, isXA=false, isJTS=false, jconn.isolationLevel=2, initialIsolationLevel=2, dirtyIsolationLevel=false>
<Jan 23, 2025 9:51:59,133 AM KST> <Debug> <JDBCSQL> <BEA-000000> <[weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@b] close returns>
[testApp:debug] [connection.close()] weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@b
```

<br>

'[testApp:debug] [connection.getConnection()]' 로그는 App에서 connection 을 얻은 시점의, 주소값을 알 수 있고
'[testApp:debug] [connection.close()]' 로그는 App에서 close 한 connection 주소값을 알 수 있음으로, pair가 되는지 확인 되며,
부가적으로 debug 로그로 동일한 주소값의 처리가 기록된다.

<br>

sql.jsp 에서 conn.close() 를 skip 하는 경우, sysout과 debug 로그에서 'close returns, ConnectionEnv.cleanup' 와 같은 로그가 확인되지 않는다.

```
<Jan 23, 2025 9:56:40,274 AM KST> <Debug> <JDBCConn> <BEA-000000> <JTS/JDBC Connect: url = jdbc:weblogic:jts:orcl, tx = null, props = {EmulateTwoPhaseCommit=false, connectionPoolID=orcl, jdbcTxDataSource=true, LoggingLastResource=false, dataSourceName=orcl}>
<Jan 23, 2025 9:56:40,275 AM KST> <Debug> <JDBCConn> <BEA-000000> <Transaction = null. Returning an ordinary JDBC conn>
<Jan 23, 2025 9:56:40,275 AM KST> <Debug> <JDBCSQL> <BEA-000000> <[oracle.jdbc.driver.T4CConnection@166ea370] beginRequest()>
<Jan 23, 2025 9:56:40,275 AM KST> <Debug> <JDBCSQL> <BEA-000000> <[oracle.jdbc.driver.T4CConnection@166ea370] beginRequest returns>
<Jan 23, 2025 9:56:40,275 AM KST> <Debug> <JDBCSQL> <BEA-000000> <[weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@d] isClosed()>
<Jan 23, 2025 9:56:40,275 AM KST> <Debug> <JDBCSQL> <BEA-000000> <[weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@d] isClosed returns false>
[testApp:debug] [connection.getConnection()] weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@d
<Jan 23, 2025 9:56:40,277 AM KST> <Debug> <JDBCSQL> <BEA-000000> <[weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@d] isClosed()>
<Jan 23, 2025 9:56:40,277 AM KST> <Debug> <JDBCSQL> <BEA-000000> <[weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection@d] isClosed returns false> 
```

<br>

WLS DS의 'Connection Leak Profile' 및, 'Inactive connection timeout' 을 설정하여 주기적으로 수집되면 datasource.log에 Leak 정보가 기록이 된다.

datasource.log에는 Connection을 요청한 최초 stack trace와 시간값(lastSuccessfulConnectionUse) 이 기록된다.

DS는 App이 요청한 Connection을 생성한 뒤, App으로 넘겼기 때문에, 이 후 Connection의 흐름을 추적하지 못한다.

그러므로 'Inactive connection timeout' 을 설정할 때는, 충분히 많은 시간. 즉 Leak으로 의심될 수 밖에 없는 큰 값을 설정하는 것이다.

<br>

App 코드 수준의 sysout과 WLS debug 를 설정하여, 최초 Connection 생성부터 파괴까지 주소값을 로그 기반으로 추적한다.


<br><br>



# 3. References

How To Detect a Connection Leak Using Diagnostic JDBC Dumps (Doc ID 1502054.1)

Diagnosing Connection Leaks in an ADF Application Running in WebLogic (Doc ID 2726546.1)

Avoiding Application JDBC Connection and Other Resource Leaks with WebLogic Server (Doc ID 1185013.1)

How to Use "Leaked Connection Count" to Monitor the Application (Doc ID 1539273.1

