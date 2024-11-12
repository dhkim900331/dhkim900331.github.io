---
date: 2024-11-11 14:17:56 +0900
layout: post
title: "[ODI] How to create a JMS XML Queue dataserver"
tags: [ODI, Studio, Topology, JMS, XML, Queue]
typora-root-url: ..
---

# 1. Overview
ODI Studio JMS XML Queue dataserver topology를 생성하는 방법


<br><br>

<br>

# 2. Descriptions
1. Topology - Physical Architecture - JMS Queue XML - <Created Object> - JNDI

```
JNDI Authentication : <Undefined>
JNDI User/Password
JNDI Protocol : <Undefined>
JNDI Driver : weblogic.jndi.WLInitialContextFactory
JNDI URL : http://<IP>:<PORT>?d=<REALPATH of XSD FILE>&re=<ROOT ELEMENT NAME>&s=<SCHEMA NAME>&JMS_DESTINATION=<QUEUE NAME>
JNDI Resource : <Connection Factory JNDI NAME>
```

 - enable tunneling인 경우, http 를 사용할 수 있다. t3 protocol 로 연결 시도에 문제가 있는 경우, 시도해볼 필요가 있다.
 - XSD file은 Queue에 저장되는 XML data의 schema 구조다.
 - Root element는 XML data의 최상위 element를 의미한다.
 - Schema name은 임의로 설정하고, 다른 Object에서 해당 Architecture 를 호출하는 Alias이다.
 - JMS_DESTINATION은 WebLogic 기준, JNDI Name 그대로 기술하면 된다.
 - JNDI Resource는 Connection factory 의 JNDI Name이고 그대로 기술하면 된다.

<br>

2. Topology - Physical/Logical Architecture - JMS Queue XML - <Created Object or Not> - Create Physical/Logical Schema