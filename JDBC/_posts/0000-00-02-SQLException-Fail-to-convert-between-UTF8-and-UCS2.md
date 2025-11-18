---
date: 2025-11-18 13:52:51 +0900
layout: post
title: "[JDBC] java.sql.SQLException: Fail to convert between UTF8 and UCS2"
tags: [JDBC, UTF8]
typora-root-url: ..
---

# 1. Overview

오래된 시스템(DB 10g, JDK 1.4) 환경에서 잘 실행되던 AP가 SQL Query 실행 시 다음의 에러가 발생한다.

```
java.sql.SQLException: UTF8과 UCS2 간에 서로 변환할 수 없습니다: failUTF8Conv
        at oracle.jdbc.dbaccess.DBError.throwSqlException(DBError.java:134)
        at oracle.jdbc.dbaccess.DBError.throwSqlException(DBError.java:179)
        at oracle.jdbc.dbaccess.DBError.check_error(DBError.java:1130)
        at oracle.jdbc.dbaccess.DBConversion.failUTF8Conv(DBConversion.java:2261)
        at oracle.jdbc.dbaccess.DBConversion.utf8BytesToJavaChars(DBConversion.java:2061)
        at oracle.jdbc.dbaccess.DBConversion.utf8BytesToString(DBConversion.java:1976)
        at oracle.jdbc.dbaccess.DBConversion.CharBytesToString(DBConversion.java:543)
        at oracle.jdbc.ttc7.TTIoer.processWarning(TTIoer.java:334)
        at oracle.jdbc.ttc7.O3log.receive2nd(O3log.java:523)
        at oracle.jdbc.ttc7.TTC7Protocol.logon(TTC7Protocol.java:279)
        at oracle.jdbc.driver.OracleConnection.<init>(OracleConnection.java:360)
        at oracle.jdbc.driver.OracleDriver.getConnectionInstance(OracleDriver.java:521)
        at oracle.jdbc.driver.OracleDriver.connect(OracleDriver.java:325)
        at java.sql.DriverManager.getConnection(DriverManager.java:512)
        at java.sql.DriverManager.getConnection(DriverManager.java:171)
        at JdbcTest.main(JdbcTest.java:36)
```

<br>

위 Stack은 문제 재현을 위해 Standardalone Java program을 통해 재현되었다.

SQLPlus 와 같은 접속 프로그램으로는 문제가 발생하지 않는다.


<br><br>


# 2. Descriptions

위 문제를 겪는 고객은 JDK 1.4 / ojdbc14.jar 로 Oracle 10g 에 접속하는 AP 환경을 갖고 있다.

매우 오래된 구성이나, AP 및 DB에 영향을 주지 않는 보안취약점 (고객의 의견) 조치 후, 기존 변경 없던 AP에서 문제가 발생하였다.

특이사항으로, JDK 및 ojdbc driver를 한단계씩 높여 JDK 1.8 / ojdbc8.jar 까지 테스트 했을 때는, 문제가 발생하지 않았다.

<br>

다음 두 문서에 따라, 실제 컬럼 조사까지 이루어졌지만 문제가 없었다.

- Oracle Waveset "Fail to convert between UTF8 and UCS2: failUTF8Conv" Exception During Full Reconciliation ([Doc ID 1323694.1](https://mosemp.us.oracle.com/epmos/faces/ui/km/DocumentDisplay.jspx?id=1323694.1))

- Determining If The Data Is Valid UTF-8 ([Doc ID 162608.1](https://mosemp.us.oracle.com/epmos/faces/ui/km/DocumentDisplay.jspx?id=162608.1))

<br>

ojdbc14.jar MANIFEST.MF 확인 결과, Oralce DB 10g 보다 낮은 JDBC 9i version으로 mismatch configurations 였다.

<br>

다음 두 문서에 따라, Oracle DB 10g 와 JDBC Driver 9i 는 서로 호환되지 않는것으로 확인되는 것이고,

Oracle DB 디렉터리에 포함되어 있는 JDBC Driver 10g 를 사용하여 문제가 해결되었다.

- Client / Server Interoperability Support Matrix for Different Oracle Versions ([Doc ID 207303.1](https://mosemp.us.oracle.com/epmos/faces/ui/km/DocumentDisplay.jspx?id=207303.1))
- Starting With Oracle JDBC Drivers - Installation, Certification, and More! ([Doc ID 401934.1](https://mosemp.us.oracle.com/epmos/faces/ui/km/DocumentDisplay.jspx?id=401934.1))


<br><br>



# 3. References

**java.sql.SQLException: Fail to convert between UTF8 and UCS2 (Doc ID 3109392.1)**
