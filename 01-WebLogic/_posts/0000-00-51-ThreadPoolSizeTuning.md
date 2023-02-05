---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[WebLogic] 스레드 풀 사이즈 튜닝(조절)"
tags: [WebLogic, Thread, Pool, Size, Tuning]
typora-root-url: ..
---

# 1. 개요

스레드 풀 사이즈 튜닝(조절)




# 2. 설명

(1). 콘솔 설정

`Environment - Servers - select instance - Configuration - Tuning - Self Tuning Thread Minimum/Maximum Pool Size`

>  적용 후 재시작



(2). config.xml 설정

```xml
<server>
     <name>서버이름</name>
          <self-tuning-thread-pool-size-min>50</self-tuning-thread-pool-size-min>
          <self-tuning-thread-pool-size-max>100</self-tuning-thread-pool-size-max>
```

> 적용 후 재시작



(3). 스크립트 설정

`USER_MEM_ARGS="-Dweblogic.threadpool.MinPoolSize=50 -Dweblogic.threadpool.MaxPoolSize=100"`
