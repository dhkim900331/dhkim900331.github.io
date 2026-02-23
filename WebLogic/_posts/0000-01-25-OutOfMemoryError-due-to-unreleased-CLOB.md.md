---
date: 2026-02-23 13:44:32 +0900
layout: post
title: "[WebLogic/JVM] OutOfMemoryError due to unreleased CLOB"
tags: [Middleware, WebLogic, OOME, JVM, Heap]
typora-root-url: ..
---

# 1. Overview

반복적으로 OOME 가 발생하는 시스템의 Heap dump 분석 시, oracle.sql.CLOB 객체가 지속적으로 누적되는 현상이 보여지고 있다.

해당 사례의 분석 방법과 해결 과정에 대해 기록한다.

<br><br>


# 2. Descriptions

## 2.1 고객 사례

CLOB 객체가 그 시점에 정상적으로 해제되어야 하는 데이터가 맞는지,

고객 어플리케이션에서 CLOB 객체의 자원 반환을 위해 명시적으로 close/free 등과 같은 메서드를 호출하고 있는지 등이 사전 조사되어야 하는데

해당 고객의 경우 자체적으로 분석을 하였지만, 위와 같은 관점에서는 분석이 되지 않은 것으로 보인다.

<br>

오로지 반복적으로 발생하는 OOME 현상 때문에 매번 Heap dump를 분석 하였고,

CLOB 객체가 자주 목격되어 (사용하는 객체이므로 당연한 것인데도) 해당 객체가 사라지지 않아서 이러한 문제가 발생했다고 의심하고 있으며,

<br>

특히 Heap dump 에 ConnectionPoolProfiler 객체가 Heap dump 분석 시 보여지는데, 

WebLogic Datasource Connection Pool의 Connection Leak 현상을 추적하기 위해 활성화하는 Connection Leak Profiling 기능으로 인해,

이 객체가 Heap 에 상시 부유하고 있고 이 객체 때문에 GC 가 되지 않는 원인을 제공하는게 아닌가 하는 부수적인 질문을 하였다.

<br>

그래서 두 가지를 중점적으로 분석하였다.

- CLOB 객체가 Heap에서 사라지지 않는 원인
- ConnectionPoolProfiler 객체가 원인이 될 수 있는지에 대한 것


<br><br>


## 2.2 Heap dump 분석

Eclipse MAT으로 분석하였다.

아래는 java.lang.Object의 outgoing references를 추적했다.

outgoing refs. 는 해당 객체에 포함되어 있는 데이터를 조사한다.

(반대로 incoming refs. 는 해당 객체를 포함하는 데이터를 조사한다.)

<br>

java.lang.Object는 21079 배열길이를 가지고 있고, 8174번째 위치에 oracle.sql.CLOB이 있다.

Object 배열의 각 element가 CLOB 인스턴스였다.

```
Class Name                                                                                                     | Shallow Heap | Retained Heap
----------------------------------------------------------------------------------------------------------------------------------------------
java.lang.Object[21079] @ 0x759c678f8                                                                          |       84,336 |   104,522,712
'- [8174] oracle.sql.CLOB @ 0x6d2256e08                                                                        |           40 |         8,208
   |- ojiOracleClob, target, targetDatumWithConnection, targetDatum oracle.jdbc.driver.OracleClob @ 0x6d2256e68|           72 |         8,112
   |- <class> class oracle.sql.CLOB @ 0x6d8fcf920                                                              |           40 |           304
   |- data byte[40] @ 0x6d2256e30  .&................G#.i..................                                    |           56 |            56
   '- Total: 3 entries                                                                                         |              |              
----------------------------------------------------------------------------------------------------------------------------------------------
```


<br><br>


동일 java.lang.Object 객체에 대한 Path to GC Roots exclude all phantom/weak/soft etc. references를 추적했다.

해당 객체와 연결된 GC Roots를 추적하여, GC가 되지 않는 원인 제공자를 조사한다.

<br>

읽는 방법 소개를 위해 부연 설명을 덧붙이자면,

`ArrayList @ 0x6d9240ad8` 객체는 elementData 변수를 통해 `Object[21079] @ 0x759c678f8`를 가리킨다.

`T4CConnection @ 0x6d923dba8` 클래스 객체는 temporaryLobs 변수를 통해 위 ArrayList를 가리킨다.

이와 같은 순서로 아래 계층을 이해하면 된다.

<br>

아래 내용 중, `<Java Local> ... ExecuteThread: '66'` 등이 있는데,

66번 Thread가 살아 있는 동안 connection 객체가 살아 있고,

connection 객체 내부의 temporaryLobs가 CLOB을 보유하고 있는 구조이다.

66번 Thread 뿐만 아니라 `Total: 3 entries` 모두가 연관되어 있다.

<br>

즉 3개 (66번 Thread, connection, currentConnection) 모두 CLOB 객체에 대한 strong references로써, GC 가 되지 않는 원인 제공자로 식별할 수 있다.

<br>

```
Class Name                                                                                                                                                      | Shallow Heap | Retained Heap
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
java.lang.Object[21079] @ 0x759c678f8                                                                                                                           |       84,336 |   104,522,712
'- elementData java.util.ArrayList @ 0x6d9240ad8                                                                                                                |           24 |   104,522,736
   '- temporaryLobs oracle.jdbc.driver.T4CConnection @ 0x6d923dba8                                                                                              |        1,432 |   105,462,600
	  |- delegateConn, vendorObj weblogic.jdbc.wrapper.PoolConnection_oracle_jdbc_driver_T4CConnection @ 0x7c59e6c28                                            |           80 |           296
	  |  |- connection aries.runtime.tracer.sql.Connection @ 0x7c59e6d90                                                                                        |           40 |            64
	  |  |  '- realConnection net.sf.log4jdbc.ConnectionSpy @ 0x7c59e6e40                                                                                       |           32 |            32
	  |  |     |- <Java Local> weblogic.work.ExecuteThread @ 0x7c548dd78  [ACTIVE] ExecuteThread: '66' for queue: 'weblogic.kernel.Default (self-tuning)' Thread|          248 |       165,376
	  |  |     |- connection org.mybatis.spring.transaction.SpringManagedTransaction @ 0x7c6294ec8                                                              |           24 |            24
	  |  |     |- currentConnection org.springframework.jdbc.datasource.ConnectionHolder @ 0x7c59e6e90                                                          |           48 |            64
	  |  |     '- Total: 3 entries                                                                                                                              |              |              
	  |  |- conn weblogic.jdbc.wrapper.PreparedStatement_oracle_jdbc_driver_OraclePreparedStatementWrapper @ 0x7ced0c5a0                                        |           96 |           184
	  |  '- Total: 2 entries                                                                                                                                    |              |              
	  |- jconn weblogic.jdbc.common.internal.ConnectionHolder @ 0x6d923db40                                                                                     |          104 |           120
	  '- Total: 2 entries                                                                                                                                       |              |              
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```


<br><br>


그리고 Profile Connection Leak 기능을 enable 또는 disable 하여 Heap dump 조사 시, 아래 처럼 항상 객체가 부유함을 알 수 있고,

```sh
$ jcmd <pid> GC.class_histogram | grep "ConnectionPoolProfiler"
2717:             2             96  weblogic.connector.outbound.ConnectionPoolProfiler
2838:             1             88  weblogic.jdbc.common.internal.ConnectionPoolProfiler
```

<br>

또한, Path to GC Roots 상에서 CLOB으로 이어지는 reference chain에 존재하지 않음을 확인하였다.


<br><br>


## 2.3 코드 테스트

Heap Dump 분석을 통해, ConnectionPoolProfiler 객체는 이제 의논 대상이 아니고,

JAVA, Oracle JDBC Driver 등의 Known issue가 있는지 살펴봤으나 해당 되지 않으므로

<br>

고객 어플리케이션 자체(App 및 Framework 등)에 문제가 있다고 가정을 하였다.

CLOB 객체가 사라지지 않는 원인을 유추할 만한 가정을 세우기 위해 간단한 샘플 코드로 테스트를 진행했다.

<br>

1000개 CLOB를 생성하고, HttpSession에 저장하여 GC 가 되지 않도록 의도했으며, CLOB.freeTemporary()를 호출하지 않았다.

(Heap dump 추출 시 Full GC가 선행될 수 있으므로)

```
Class Name     | Objects | Shallow Heap | Retained Heap
--------------------------------------------------------
oracle.sql.CLOB|   1,000 |       40,000 |    >= 168,248
--------------------------------------------------------
```

<br>

CLOB 객체를 상위 레벨에서 포함하고 있는 데이터를 조사하기 위해,

Incomong references를 살펴보면 아래와 같다.

HttpSession와 연관되는 Servlet Internal 클래스와 T4CConnection 클래스가 확인된다.

```
Class Name                                                           | Shallow Heap | Retained Heap
----------------------------------------------------------------------------------------------------
oracle.sql.CLOB @ 0x825e8968                                         |           40 |           168
|- [15] java.lang.Object[1000] @ 0x84379170                          |        4,016 |         4,016
|  '- object weblogic.servlet.internal.AttributeWrapper @ 0x84a6b070 |           56 |         4,072
|     '- val java.util.concurrent.ConcurrentHashMap$Node @ 0x84a6b050|           32 |         4,104
|- [15] java.lang.Object[1234] @ 0x84a5abd0                          |        4,952 |         4,952
|  '- elementData java.util.ArrayList @ 0x825e8950                   |           24 |         4,976
|     '- temporaryLobs oracle.jdbc.driver.T4CConnection @ 0x82504778 |        1,336 |       126,184
'- Total: 2 entries                                                  |              |              
oracle.sql.CLOB @ 0x825e8a10                                         |           40 |           168
oracle.sql.CLOB @ 0x825e8ab8                                         |           40 |           168
...
Total: 30 of 1,000 entries; 970 more
----------------------------------------------------------------------------------------------------
```

<br>

CLOB 객체에 대해 freeTemorary() 호출하여 명시적으로 정리를 하면,

아래처럼 HttpSession의 strong references 만 보여지고, T4CConnection 클래스에서는 정리된 것이 확인된다.

(테스트 시마다 객체를 새로 생성했기 때문에, 위 분석 로그에 나타나는 객체의 주소값과 다를 수 있다.)

```
Class Name                                                          | Shallow Heap | Retained Heap
---------------------------------------------------------------------------------------------------
oracle.sql.CLOB @ 0x8472a7f8                                        |           40 |           168
'- [228] java.lang.Object[1000] @ 0x84729848                        |        4,016 |       171,960
   '- object weblogic.servlet.internal.AttributeWrapper @ 0x847713e8|           56 |       172,016
oracle.sql.CLOB @ 0x8472a8a0                                        |           40 |           168
oracle.sql.CLOB @ 0x8472a948                                        |           40 |           168
...
Total: 30 of 1,000 entries; 970 more
---------------------------------------------------------------------------------------------------
```

<br>

1000개 CLOB을 생성하되, Session 에도 저장하지 않고, 즉시 freeTemporary()를 호출 하면 모두 정리된다.

```
Class Name     | Objects | Shallow Heap | Retained Heap
--------------------------------------------------------
oracle.sql.CLOB|       0 |            0 |        >= 304
--------------------------------------------------------
```


<br><br>


## 2.4 결론

Incoming/Outgoing refs. 또는 Path to GC Roots 기능을 통해 해당 객체(여기서는 CLOB)가 누구에게 속해 있는지 분석해야 하고

왜 GC가 되지 않는지 확인을 했다.

<br>

종료될 수 없는 66번 Background thread 등이 확인되었기에 고객 어플리케이션에서 CLOB 객체를 정상적 반납의 의무를 다하지 않는다고 가정하여 코드 테스트를 실시했으며,

명시적으로 freeTemporary를 호출하는것으로 증명했다.

<br>

고객은 Connection.close 만으로도 CLOB 객체가 해제 되는 것으로 알고 있었지만,

pooled connection은 hard close가 아니라 Datasource에 반환되는 soft close 이고,

[14.3 Temporary LOBs](https://docs.oracle.com/en/database/oracle/oracle-database/21/jjdbc/jdbc-developers-guide.pdf) 에서 다음을 설명하고 있다.

```
14.3 Temporary LOBs
	
	Freeing a Temporary LOB
	
		You free a temporary LOB using the freeTemporary method.
```

<br>

결론적으로, 이후 해당 고객 어플리케이션에 CLOB 객체에 대해 명시적으로 freeTemporary()를 사용하여 이번 이슈가 해결되었다.


<br><br>


# 3. References

N/A
