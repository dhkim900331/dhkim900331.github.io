---
date: 2022-05-30 10:24:20 +0900
layout: post
title: "[Servlet/JSP] Fail over Test를 위한 JSP"
tags: [JSP, Servlet, Session, Failover, Clustering]
typora-root-url: ..
---

# 1. 개요

기본적으로 session clustering 환경 구성 후, Failover Test를 위해 사용하는 JSP

다른 포스트에서도 webapp.zip 등으로 첨부파일 업로드 한 것이 있으나, 좀 더 깔끔한 것으로 업데이트



# 2. 설명

다음의 어플리케이션의 구조이며, 해당 소스는 `infinispan`에서 사용되어 `distributable` 태그를 갖는다.

```bash
$ tree /usr/app/testapp.war
/usr/app/testapp.war
├── WEB-INF
│   ├── classes
│   │   └── example
│   │       └── sessionObject.class
│   ├── run_compile.sh
│   ├── src
│   │   └── example
│   │       └── sessionObject.java
│   └── web.xml
└── session.jsp

5 directories, 5 files
```



* 주요 스크립트

  * session.jsp

    ```jsp
    <%@ page language="java" contentType="text/html;charset=UTF-8" pageEncoding="UTF-8" %>
    <%@ page import="java.io.Serializable" %>
    <%@ page import="example.sessionObject" %>
    <%
            session = request.getSession(true);
            sessionObject so = (sessionObject) session.getAttribute("so");
    
            if (so == null) so = new sessionObject();
            else so.incCnt();
    
            session.setAttribute("so", so);
            out.println("[TEST] so.getCnt() : " + so.getCnt());
            out.println("<br>");
    
            out.println("[TEST] session.getId() : " + session.getId());
            out.println("<br>");
            out.println("[TEST] system.getProperty(\"jboss.node.name\") : " + System.getProperty("jboss.node.name"));
            out.println("<br>");
    %>
    ```

    

  * sessionObject.java

    ```java
    package example;
    
    import java.io.Serializable;
    public class sessionObject implements Serializable{
            private static final long serialVersionUID = 1234567L;
            private int cnt;
    
            public sessionObject(){
                    cnt = new Integer(1);
            }
    
            public int getCnt(){
                    return cnt;
            }
    
            public void incCnt(){
                    cnt++;
            }
    }
    ```

    

  * web.xml

    ```xml
    <web-app>
            <distributable/>
    </web-app>
    ```

    

  * run_compile.sh

    ```bash
    #!/bin/bash
    JAVA_HOME=/usr/java/jdk-8u312-ojdkbuild-linux-x64
    ${JAVA_HOME}/bin/javac -d ./classes src/example/sessionObject.java
    ```

    
