---
date: 2023-05-25 09:55:14 +0900
layout: post
title: "[Coherence/App] Coherence Session Test Application"
tags: [Coherence, App, Session]
typora-root-url: ..
---

# 1. 개요

Coherence 14.1 기준에서 Test 용 Application

<br><br>


# 2. 어플리케이션

## 2.1 구조

```sh
$ tree /sw/app/cohSessionApp/
/sw/app/cohSessionApp/
├── META-INF
├── session.jsp
└── WEB-INF
    ├── classes
    │   └── session-cache-config.xml
    ├── weblogic.xml
    └── web.xml

3 directories, 4 files
```


<br><br>

<br>

## 2.2 Servlet

```jsp
<%@ page import="java.util.ArrayList" %>

<%
  ArrayList<byte[]> list = new ArrayList<byte[]>();
  int addedNum = 1024;
  int addedByte = 512;

  byte[] objectInSession = new byte[addedByte];
  for(int i=0; i<addedNum; i++){
    list.add(objectInSession);
  }

  session = request.getSession(true);
  ArrayList<byte[]> sList = (ArrayList<byte[]>)session.getAttribute("listSession");

  if (sList == null){
    sList = list;
  }
  else{
    /*for(int i=0; i<addedNum; i++){
      sList.add(objectInSession);
    }*/
    sList.addAll(list);
  }

  session.setAttribute("listSession", sList);
  String log = "";
  log += "list.size() = " + list.size() + "<br>";
  log += "sList.size = " + sList.size() + "<br>";
  log += "session.getMaxInactiveInterval() = " + session.getMaxInactiveInterval() + "<br>";
  log += "session.getClass().getName() = " + session.getClass().getName() + "<br>";
  out.println(log);

  final long  MEGABYTE = 1024L * 1024L;
  long heapSize = Runtime.getRuntime().totalMemory() / MEGABYTE;
  long heapMaxSize = Runtime.getRuntime().maxMemory() / MEGABYTE;
  long heapFreeSize = Runtime.getRuntime().freeMemory() / MEGABYTE;

  log = "";
  log += "heapSize (MB) = " + heapSize + "<br>";
  log += "heapMaxSize (MB) = " + heapMaxSize + "<br>";
  log += "heapSize (MB) = " + heapFreeSize + "<br>";
  out.println(log);

%>
```


addedByte 크기의 Bytes Array Object를 addedNum 갯수만큼 ArrayList 로 만들고, listSession 명명의 Session 객체로 저장한다.

재호출 시마다, Session 객체가 동일한 과정으로 점차 커지게 된다.


<br><br>


## 2.3 Deployment Descriptor

web.xml

```xml
<web-app>

<resource-ref>
    <res-ref-name>wm/CoherenceWorkManager</res-ref-name>
    <res-type>commonj.work.WorkManager</res-type>
    <res-auth>Container</res-auth>
    <res-sharing-scope>Shareable</res-sharing-scope>
</resource-ref>

</web-app>
```

<br>

`wm/CoherenceWorkManager` 를 WebLogic WorkManager로 등록해야 한다.

```xml
  <self-tuning>
    <min-threads-constraint>
      <name>MinThreadsConstraint-0</name>
      <target>myCluster</target>
      <count>2</count>
    </min-threads-constraint>
    <max-threads-constraint>
      <name>MaxThreadsConstraint-0</name>
      <target>myCluster</target>
      <count>2</count>
    </max-threads-constraint>
    <work-manager>
      <name>wm/CoherenceWorkManager</name>
      <target>myCluster</target>
    </work-manager>
  </self-tuning>
```

<br>

weblogic.xml

```xml
<weblogic-web-app>
        <container-descriptor>
                <servlet-reload-check-secs>1</servlet-reload-check-secs>
                <resource-reload-check-secs>1</resource-reload-check-secs>
        </container-descriptor>

        <jsp-descriptor>
                <page-check-seconds>1</page-check-seconds>
        </jsp-descriptor>

    <session-descriptor>
        <timeout-secs>30</timeout-secs>
        <invalidation-interval-secs>60</invalidation-interval-secs>
        <persistent-store-type>coherence-web</persistent-store-type>
    </session-descriptor>
</weblogic-web-app>
```

<br><br>

## 2.4 Cache Config

session-cache-config.xml 파일은 coherence-web.jar 에서 기본값을 Loaded
