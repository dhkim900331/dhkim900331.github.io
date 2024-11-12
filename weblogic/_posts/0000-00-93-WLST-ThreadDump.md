---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] WLST으로 Thread Dump"
tags: [Middleware, WebLogic, WLST, ThreadDump]
---


# 1. Overview

WLST로 Thread dump를 뜨는 스크립트


<br><br>


# 2. Descriptions

```bash
java -cp wlfullclient.jar weblogic.Admin -url t3://ip:port -username weblogic -password weblogic1 THREAD_DUMP
```

> nohup에 기록된다.
>
> wlfullclient.jar는 _https://docs.oracle.com/cd/E13222_01/wls/docs103/client/jarbuilder.html#wp1078098_ 를 참고하여 생성한다.
