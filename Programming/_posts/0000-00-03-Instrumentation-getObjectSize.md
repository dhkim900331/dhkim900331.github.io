---
date: 2023-06-01 08:58:38 +0900
layout: post
title: "[Java/Instrumentation] Instrumentation.getObjectSize()"
tags: [Programming, Java, Instrumentation, getObjectSize]
typora-root-url: ..
---

# 1. Overview

Instrumentation 의 getObjectSize를 통해 Object 의 Size를 조사하는 방법

Java bytecode에 개입할 수 있는 Instrumentation Class의 getObjectSize method를 통해서 Object의 Size를 조사하는 방법을 소개한다.
{{ site.content.br_big }}
# 2. ObjectSizeAgent

getObjectSize 를 수행하는 ObjectSizeAgent App은 javaagent 로 심어져야 한다.

App은 다음과 같은 구조로 개발된다.

```sh
$ tree /sw/app/ObjectSizeAgent/
/sw/app/ObjectSizeAgent/
├── compile.sh
├── MANIFEST.MF
├── ObjectSizeAgent.class
├── ObjectSizeAgent.jar
└── ObjectSizeAgent.java
```
{{ site.content.br_small }}
## 2.1 compile.sh

편의를 위해 compile script를 만들었다.

```sh
javac ObjectSizeAgent.java
jar cvfm ObjectSizeAgent.jar MANIFEST.MF ObjectSizeAgent.class
```
{{ site.content.br_small }}
java 를 compile 하고 ObjectSizeAgent.jar 에 MANIFEST.MF와 class를 packaging 한다.
{{ site.content.br_big }}
## 2.2 MANIFEST.MF

생략가능하다.

```
Premain-Class: ObjectSizeAgent
```
{{ site.content.br_big }}
## 2.3 ObjectSizeAgent.java

```java
import java.lang.instrument.Instrumentation;

public class ObjectSizeAgent {
    private static volatile Instrumentation instrumentation;

    public static void premain(String agentArgs, Instrumentation inst) {
        instrumentation = inst;
    }

    public static long getObjectSize(Object object) {
        if (instrumentation == null) {
            throw new IllegalStateException("Java agent not initialized");
        }
        return instrumentation.getObjectSize(object);
    }
}
```
{{ site.content.br_big }}
# 3. My App

javaagent로 등록된 ObjectSizeAgent.jar 에서 getObjectSize method를 호출하여 특정 Object의 Size를 알 수 있다.

나에게는 Session을 다루는 Servlet 이 있으며, 여러 Size를 계산할 필요가 있었다.
{{ site.content.br_small }}
## 3.1 SessionServlet.java

Servlet code는 아래와 같다.

```java
import javax.servlet.http.*;
import javax.servlet.annotation.WebServlet;

import javax.servlet.ServletException;
import java.io.IOException;

import  java.util.ArrayList;

@WebServlet("/SessionServlet")
public class SessionServlet extends HttpServlet {
  protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {

    ArrayList<byte[]> list = new ArrayList<byte[]>();
    int addedNum = 500;
    int addedByte = 1;

    byte[] objectInSession = new byte[addedByte];
    for(int i=0; i<addedNum; i++){
      list.add(objectInSession);
    }

    HttpSession session = request.getSession(true);
    ArrayList<byte[]> sList = (ArrayList<byte[]>)session.getAttribute("listSession");

    if (sList == null){
      sList = list;
    }
    else{
      sList.addAll(list);
    }

    session.setAttribute("listSession", sList);
    String log = "";
    log += "list.size() = " + list.size() + "\r\n";
    log += "sList.size = " + sList.size() + "\r\n";
    log += "session.getMaxInactiveInterval() = " + session.getMaxInactiveInterval() + "\r\n";
    log += "session.getClass().getName() = " + session.getClass().getName() + "\r\n";
    log += "ObjectSizeAgent.getObjectSize(list) = " + ObjectSizeAgent.getObjectSize(list) + "\r\n";
    log += "ObjectSizeAgent.getObjectSize(sList) = " + ObjectSizeAgent.getObjectSize(sList) + "\r\n";
    log += "ObjectSizeAgent.getObjectSize(session) = " + ObjectSizeAgent.getObjectSize(session) + "\r\n";
    System.out.println(log);


    final long  MEGABYTE = 1024L * 1024L;
    long heapSize = Runtime.getRuntime().totalMemory() / MEGABYTE;
    long heapMaxSize = Runtime.getRuntime().maxMemory() / MEGABYTE;
    long heapFreeSize = Runtime.getRuntime().freeMemory() / MEGABYTE;

    log = "";
    log += "heapSize (MB) = " + heapSize + "\r\n";
    log += "heapMaxSize (MB) = " + heapMaxSize + "\r\n";
    log += "heapSize (MB) = " + heapFreeSize + "\r\n";
    System.out.println(log);

  }
}
```
{{ site.content.br_small }}
ObjectSizeAgent.getObjectSize() method를 통해서 Size를 inspect 하고 있다.
{{ site.content.br_big }}
## 3.2 compile.sh

여기서도 편의를 위해 compile script를 사용하고 있다.

```sh
. /sw/weblogic/14c/domains/base_domain/bin/setDomainEnv.sh

CLASSPATH="${CLASSPATH}:/sw/app/ObjectSizeAgent/ObjectSizeAgent.jar"

cd /sw/app/cohSessionApp/WEB-INF
javac src/*.java -d classes/
```
{{ site.content.br_small }}
Weblogic 14c에 배포되는 특성이 있으며, classpath에 Agent jar가 있다.
{{ site.content.br_big }}
# 4. Weblogic

Weblogic에 javaagent를 등록하여 기동한다.

```sh
-javaagent:/sw/app/ObjectSizeAgent/ObjectSizeAgent.jar
```
{{ site.content.br_small }}
이외 별달리 할 것은 없다.
{{ site.content.br_big }}
# 5. Test

App을 호출하면 Session에 담기려는 Size, Session data 자체의 Size가 return 된다.
{{ site.content.br_small }}
호출 예시

```
list.size() = 500
sList.size = 1000
session.getMaxInactiveInterval() = 30
session.getClass().getName() = weblogic.servlet.internal.session.CoherenceWebSessionData
ObjectSizeAgent.getObjectSize(list) = 24
ObjectSizeAgent.getObjectSize(sList) = 24
ObjectSizeAgent.getObjectSize(session) = 128

heapSize (MB) = 2967
heapMaxSize (MB) = 2967
heapSize (MB) = 2307
```
{{ site.content.br_small }}
특이사항으로는, 나의 App은 반복 호출 시 더 큰 Object를 Session에 저장하는데

getObjectSize로 확인해도 항상 24bytes 를 유지하는 모습이 관찰된다.
{{ site.content.br_small }}
이는 getObjectSize는 Object의 [shallow size](https://www.baeldung.com/jvm-measuring-object-sizes)를 return 하기 때문이라며,,

공식자료는 찾지 못했다.
{{ site.content.br_small }}
deep size 확인을 위해서는, JOL(Java Object Layout) 3rd library 를 활용해야 될 것으로 보인다.

