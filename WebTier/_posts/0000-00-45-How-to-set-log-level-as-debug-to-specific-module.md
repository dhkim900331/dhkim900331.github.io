---
date: 2025-08-29 12:22:38 +0900
layout: post
title: "[WebTier/Apache] How to set log level as debug to specific module"
tags: [WebTier, OHS, Apache, LogLevel, Debug]
typora-root-url: ..
---

# 1. Overview

Apache/OHS 의 LogLevel 지시어로 특정 모듈만 수준을 지정하는 방법

<br><br>

# 2. Descriptions

```
# 전체 모듈 디버그
LogLevel debug
```

<br>

위 설정 시, 모든 모듈이 아래 처럼 로깅된다.

```
[Thu Aug 28 12:59:54.561070 2025] [weblogic:debug] ...
[Thu Aug 28 12:59:59.193258 2025] [ossl:debug] ...
[Thu Aug 28 13:00:18.293794 2025] [ossl:info] ...
[Thu Aug 28 13:00:18.297455 2025] [socache_shmcb:debug] ...
```


<br><br>


```
# weblogic(mod_wl_ohs) 모듈만 디버그
LogLevel warn weblogic:debug
```

<br>

이후, WebLogic Proxy Module만 Debug 기록된다.

<br><br>


# 3. References

