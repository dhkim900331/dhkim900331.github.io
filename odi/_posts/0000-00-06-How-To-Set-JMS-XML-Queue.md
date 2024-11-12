---
date: 2024-10-30 14:36:54 +0900
layout: post
title: "[ODI] How To Set JMS XML Queue"
tags: [ODI, ]
typora-root-url: ..
---

# 1. Overview
ODI 12c 에서 JMS XML Queue 정의 방법


<br><br>


# 2. Descriptions

Topology 에서 JMS XML Queue Architecture 를 정의하고, JMS JNDI URL을 정의시에, studio.log에 아래와 같이 확인된다.

`JDBC:SNPS:JMSXML:jndi:<URL>` 

<br>

앞 부분의 Prefix(`JDBC:SNPS:JMSXML`) 부분은 SNPS Driver로 인해 정의되는 것이다.

때로 JNDI URL을 올바르게 설정하여도, 다음과 같은 Error를 마주할 수 있다.

```
java.sql.SQLException: ODI-40105: URL JDBC:SNPS:JMSXML:jndi:t3://...
Caused by: java.sql.SQLException: ODI-40105: URL JDBC:SNPS:JMSXML:jndi:t3://IP:PORT?d=C:/study/sample.dtd&s=JMS&JMS_DESTINATION=Queue&factory.initial=weblogic.jndi.WLInitialContextFactory&jndi_ressource=CF&security.authentication=none&security.principal=weblogic&security.credentials=****isTopic=False을(를) 사용하여 JMS 접속 실패
Caused by: java.sql.SQLException: java.sql.SQLException: Cannot load connection class because of underlying exception: 'javax.jms.JMSException: ODI-40201: 초기 JNDI 컨텍스트를 생성할 수 없습니다.)'.
Caused by: java.sql.SQLException: Cannot load connection class because of underlying exception: 'javax.jms.JMSException: ODI-40201: 초기 JNDI 컨텍스트를 생성할 수 없습니다.)'.
Caused by: javax.naming.CommunicationException: Failed to initialize JNDI context, tried 2 time or times totally, the interval of each time is 0ms. 
[Login failed for an unknown reason: HTTP/1.0 500 handshakefailed] [Root exception is weblogic.socket.UnrecoverableConnectException: [Login failed for an unknown reason: HTTP/1.0 500 handshakefailed]]
Caused by: weblogic.socket.UnrecoverableConnectException: [Login failed for an unknown reason: HTTP/1.0 500 handshakefailed]
```

<br>

t3 protocol 사용에는 문제가 없어야 하나, 근본적인 원인은 확인이 되지 않았다.

JMS module을 배포한 WebLogic Server의 Protocol Tunneling을 활성화 했고,

다음의 JNDI URL로 문제 없이 동작한다.

`http://IP:PORT`


<br><br>


# 3. References
**ODI Data Server Test Fails with ODI-40105 Error when Using Virtual IP Hostname (Doc ID 2759369.1)**

**How To Write to a JMS XML Queue from Relational Tables Using Oracle Data Integrator 11g (Doc ID 1311394.1)**

https://www.youtube.com/watch?v=RWjm0oUE1EM

https://docs.oracle.com/en/middleware/fusion-middleware/data-integrator/12.2.1.4/odikm/xml-files.html#GUID-AA840013-0905-4E11-9038-151A98151D19

https://www.oracle.com/webfolder/technetwork/tutorials/obe/fmw/odi/odi_12c/odi12c_exp_flat_2_tbl/odi12c_exp_flat_2_tbl.html