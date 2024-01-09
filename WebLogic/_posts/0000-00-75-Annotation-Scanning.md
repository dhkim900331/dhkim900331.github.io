---
date: 2024-01-09 11:55:47 +0900
layout: post
title: "[WebLogic] Annotation Scanning"
tags: [Middleware, WebLogic, Annoation, Scanning]
typora-root-url: ..
---

# 1. Overview
WLS 11g 부터 도입된 Admin Server에 의한 배포된 App의 Annotation Scanning 기능.

{{ site.content.br_big }}

# 2. Descriptions
수 많은 Files/Dirs 를 갖는 App을 AdminServer가 EJB/RAR 구성 요소가 있는지 Scan 한다.

File 하나하나는 매우 빠른 속도로 Scan 을 완료하지만,

Files/Dirs 수가 매우 많거나, NAS로 연결된 경우 Files 목록 gathering 에 지연이 발생하여

Scan 완료가 늦어진다.

Scan 기능은 쓸 수 없고, 다음의 옵션들로 Debugging 할 수 있다. (Admin Server에 적용)

```sh
-Dweblogic.log.StdoutSeverity=Debug
-Dweblogic.debug.DebugAppContainer=true
```

{{ site.content.br_big }}



이러한 Scan은 화장자를 가리지 않고 모든 대상에 수행되며, WAR 로 패키징된 App은 Scan 하지 않는다.

JAR 또한 Scan 하는 것처럼 Logging 되지만 실제로는 Scan 되지 않는 것으로 보인다.

Scan은 EJB 1번, RAR 1번 검사를 위해 총 모든 Files/Dirs를 2회씩 Scan 한다.



Scan 에 의해 발생하는 지연 현상을 위한 WorkAround 는 ...

 - WAR 로 패키징 (권장)
 - 많은 Files/Dirs 정리
 - 많은 Files와 Dirs를 Symbolic link 로 분리하여도 Scan은 Symbolic link 를 타고 들어가므로, 의미없음.
 - linux의 경우 actimeo=N 옵션으로 NAS Cache time 옵션 튜닝 (검증된 적 없음)

{{ site.content.br_big }}

# 3. References

SR 3-35205319421: XXXX

SR 3-33737967991: XXXX
