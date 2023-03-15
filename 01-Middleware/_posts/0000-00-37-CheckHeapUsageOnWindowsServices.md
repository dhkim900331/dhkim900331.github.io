---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[Middleware/WebLogic] 윈도우 서비스 Heap Usage 확인"
tags: [Middleware, WebLogic, jmap, Window, Service, Heap Usage]
typora-root-url: ..
---

# 1. 개요

* SR 3-18602337531 : [XXXX] How to get Permgen Space info of Weblogic Server on Windows Service
* 윈도우 서비스 항목으로 등록된 JVM 의 Heap Usage 항목 확인 방법




# 2. 설명

```shell
d:\sw\domains\Domain_10.3.6>sc queryex WLS_10.3.6_Admin

SERVICE_NAME: WLS_10.3.6_Admin
종류 : 10 WIN32_OWN_PROCESS
상태 : 4 RUNNING
(STOPPABLE, NOT_PAUSABLE, ACCEPTS_SHUTDOWN)
WIN32_EXIT_CODE : 0 (0x0)
SERVICE_EXIT_CODE : 0 (0x0)
검사점 : 0x0
WAIT_HINT : 0x0
PID : 2448
플래그 :
```

> sc 명령어를 활용하여, 기동중인 서비스의 JVM PID 추출



```shell
d:\sw\domains\Domain_10.3.6>jmap -heap 2448
Attaching to process ID 2448, please wait..
Debugger attached successfully.
Server compiler detected.
JVM version is 24.80-b11

using thread-local object allocation.
Parallel GC with 4 thread(s)

Heap Configuration:
MinHeapFreeRatio = 0
MaxHeapFreeRatio = 100
MaxHeapSize = 536870912 (512.0MB)
NewSize = 1310720 (1.25MB)
MaxNewSize = 17592186044415 MB
OldSize = 5439488 (5.1875MB)
NewRatio = 2
SurvivorRatio = 8
PermSize = 21757952 (20.75MB)
MaxPermSize = 536870912 (512.0MB)
G1HeapRegionSize = 0 (0.0MB)

Heap Usage:
PS Young Generation
Eden Space:
capacity = 83886080 (80.0MB)
used = 9103272 (8.681556701660156MB)
free = 74782808 (71.31844329833984MB)
10.851945877075195% used
From Space:
capacity = 22020096 (21.0MB)
used = 22005520 (20.986099243164062MB)
free = 14576 (0.0139007568359375MB)
99.93380591982887% used
To Space:
capacity = 47710208 (45.5MB)
used = 0 (0.0MB)
free = 47710208 (45.5MB)
0.0% used
PS Old Generation
capacity = 358088704 (341.5MB)
used = 61632656 (58.77748107910156MB)
free = 296456048 (282.72251892089844MB)
17.211561077335745% used
PS Perm Generation
capacity = 83361792 (79.5MB)
used = 83023384 (79.1772689819336MB)
free = 338408 (0.32273101806640625MB)
99.59404903387873% used

45147 interned Strings occupying 5584000 bytes.
```
