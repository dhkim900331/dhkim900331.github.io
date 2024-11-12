---
date: 2024-11-11 14:17:56 +0900
layout: post
title: "[ODI] Size limit exception with ODI studio when reading queue"
tags: [ODI, Studio, JMS, XML, Queue, MaxMessageSize]
typora-root-url: ..
---

# 1. Overview
JMS Queue로 부터 Data를 읽으면, 임시로 생성된 ODI Studio in-memory table에 load 된다.
Queue data가 너무 큰 경우 Exception이 발생한다.


<br><br>

<br>

# 2. Descriptions
JMS XML Queue 에서 Big data를 가정하기 위해서, 다음의 Data를 생성한다.
단순히 id가 1인 single user에 email string이 매우 크도록 한 것이다.
```java
    // StringBuilder를 사용하여 큰 XML 문자열 생성
    StringBuilder xmlDataBuilder = new StringBuilder("<?xml version='1.0' encoding='UTF-8'?>");
    xmlDataBuilder.append("<users>");
    xmlDataBuilder.append("<user>");
    xmlDataBuilder.append("<id>1</id>");
    xmlDataBuilder.append("<name>donghyun.kim</name>");
    xmlDataBuilder.append("<email>");

    // 반복 횟수를 설정하여 10MB 이상의 데이터를 구성합니다.
    int repeatCount = 50000; // 반복 횟수는 필요에 따라 조정 가능
    for (int i = 0; i < repeatCount; i++) {
        xmlDataBuilder.append("dong-hyun.kim@oracle.com");
    }
    xmlDataBuilder.append("</email>");
    xmlDataBuilder.append("</user>");    
    xmlDataBuilder.append("</users>");
```

<br>

JMS XML Queue 가져오기를 시도하면 다음과 같이 EMAIL column 의 data가 너무 커, ODI Studio in-memory로 가져오지 못한다.

```
ODI-1228: Task Procedure-PRC.FARCRQ.LOAD-Load JMS fails on the target connection JMQX_FARCRQ.
Caused By: java.sql.SQLException: class java.sql.SQLException
java.sql.BatchUpdateException: data exception: string data, right truncation ; size limit: 255 table: FARCRQ_USER_ column: EMAIL
	at com.sunopsis.jdbc.driver.xml.SnpsXmlFile.readDocument(SnpsXmlFile.java:508)
	at com.sunopsis.jdbc.driver.xml.SnpsXmlFile.readDocument(SnpsXmlFile.java:453)
	at com.sunopsis.jdbc.driver.xml.SnpsXmlConnection.readStream(SnpsXmlConnection.java:1621)
	at com.sunopsis.jdbc.driver.JMSXMLStatement.loadJMS(JMSXMLStatement.java:693)
	at com.sunopsis.jdbc.driver.JMSXMLStatement.execute(JMSXMLStatement.java:147)
	at oracle.odi.runtime.agent.execution.sql.SQLCommand.execute(SQLCommand.java:271)
	at oracle.odi.runtime.agent.execution.sql.SQLExecutor.execute(SQLExecutor.java:142)
Caused by: java.sql.SQLException: java.sql.BatchUpdateException: data exception: string data, right truncation ; size limit: 255 table: FARCRQ_USER_ column: EMAIL
Caused by: java.sql.BatchUpdateException: data exception: string data, right truncation ; size limit: 255 table: FARCRQ_USER_ column: EMAIL
```

<br>

JMS Queue(또는 XML Queue) 의 Datasource 설정에, 다음의 두 옵션이 기본값 255로 설정되어 있다.
해당 값을 크게 키워 시도해본다.

```
default_length_varchar = 255
dp_varchar_length = 255
```

<br>

동일한 현상이 발생한다.

```
Caused by: java.sql.BatchUpdateException: data exception: string data, right truncation ; size limit: 99999 table: FARCRQ_USER_ column: EMAIL
	at org.hsqldb.jdbc.JDBCPreparedStatement.executeBatch(Unknown Source)
	at com.sunopsis.jdbc.driver.xml.SnpsXmlPreparedStatementRedirector.executeBatch(SnpsXmlPreparedStatementRedirector.java:376)
	at com.sunopsis.jdbc.driver.xml.SnpsXmlPreparedStatement.executeBatch(SnpsXmlPreparedStatement.java:16)
	at com.sunopsis.rdb.manager.SnpsRDBDataInserterBatchUpdate.insertionFinished(SnpsRDBDataInserterBatchUpdate.java:118)
	at com.sunopsis.jdbc.driver.xml.mappers.SnpsXmlModelMapperLinks.endLoadElements(SnpsXmlModelMapperLinks.java:751)
	at com.sunopsis.jdbc.driver.xml.data.AbstractXmlLoader.loadFile(AbstractXmlLoader.java:209)
	... 23 more
```

<br>

이 근본적인 문제 해결을 위해, 다음과 같은 data를 생성하도록 코드를 변경한다.
특정 column 자체는 작지만, 많은 user structures 를 갖도록 구성했다.
30만 loop 기준, 20MB 이상의 Queue message가 생성이 된다.

```java
    // StringBuilder를 사용하여 큰 XML 문자열 생성
    StringBuilder xmlDataBuilder = new StringBuilder("<?xml version='1.0' encoding='UTF-8'?>");
    xmlDataBuilder.append("<users>");

    // 반복 횟수를 설정하여 10MB 이상의 데이터를 구성합니다.
    int repeatCount = 300000; // 반복 횟수는 필요에 따라 조정 가능
    for (int i = 0; i < repeatCount; i++) {
        xmlDataBuilder.append("<user><id>" + i + "</id><name>donghyun.kim</name><email>dong-hyun.kim@oracle.com</email></user>");
    }
    xmlDataBuilder.append("</users>");
```

<br>

문제 없이 JMS XML Queue load를 수행한다.
특정 고객은, 아래와 같이 Message Limit Exception이 발생하였는데, 나와 어떤 것들이 달라 차이점이 있는지는 확인되지 않는다.
고객은, -Dweblogic.MaxMessageSize 옵션 기본값 10MB 를 더 키워 문제를 해결한 상황.

```
  JMSTopicConnection.openFileForResultSet():JMSException while fetching message :weblogic.messaging.dispatcher.DispatcherException: weblogic.rjvm.PeerGoneException: ; nested exception is: [[
  weblogic.socket.MaxMessageSizeExceededException: Incoming message of size: '10000080' bytes exceeds the configured maximum of: '10000000' bytes for protocol: 't3'
  ]]
```

