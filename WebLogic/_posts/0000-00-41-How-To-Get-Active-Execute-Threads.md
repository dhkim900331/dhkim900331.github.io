---
date: 2024-10-30 14:36:54 +0900
layout: post
title: "[WebLogic] How To Get Active Execute Threads"
tags: [Middleware, WebLogic, Execute, Thread]
typora-root-url: ..
---

# 1. Overview
WLS 11gR1 기준에서 Active Execute Threads 의 추이를 모니터링 하는 방법


<br><br>


# 2. Descriptions
How To Get Active Execute Threads (Doc ID 2348749.1) 문서의 안내에 따라 확인을 하면 된다.

위 문서의 설명에 더해, 알아둬야 할 것은,
- Active Thread 는 현재 작업이 실행중인 스레드
- Idle Thread 는 유휴상태로써, 아무런 작업 없이 wait() 상태에 있는 스레드
- Stuck Thread 는 동일한 작업을 기본값 600초 초과하여 실행중인 지연 스레드
- Standby Thread 는 위 항목에 포함되지 않고, 별도로 관리되는 스레드

<br>

11gR1 은 Bug로 인해 Admin console에서 제대로 계산이 반영되지 않았으니, WLST 등으로 수집 후 직접 계산해야 한다.

이는 WLS 12cR2 에서 수정되었다.


<br><br>


# 3. References
How To Get Active Execute Threads (Doc ID 2348749.1)