---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[WebLogic] WEB-INF(web.xml, weblogic.xml) 의 버전 업그레이드"
tags: [Middleware, WebLogic, Upgraded, WebInf]
---


# 1. Overview
WEB-INF(web.xml, weblogic.xml) 의 버전 업그레이드


<br><br>


# 2. Descriptions

`java -cp "$WL_HOME/server/lib/weblogic.jar" weblogic.DDConverter -d /path/newConfig /applications/webapp`

> /applications/webapp/WEB-INF/web.xml과 weblogic.xml을 해당 웹로직 버전으로 업그레이드 하여, /path/newConfig 디렉토리에 저장한다.