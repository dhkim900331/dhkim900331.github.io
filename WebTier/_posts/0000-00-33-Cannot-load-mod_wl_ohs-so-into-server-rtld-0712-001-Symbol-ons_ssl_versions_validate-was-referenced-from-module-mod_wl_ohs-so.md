---
date: 2024-12-05 16:08:28 +0900
layout: post
title: "[WebTier/OHS] Cannot load mod_wl_ohs.so into server: rtld: 0712-001 Symbol ons_ssl_versions_validate was referenced from module mod_wl_ohs.so(), but a runtime definition"
tags: [WebTier, OHS, Bundle Patch, PSU, AIX]
typora-root-url: ..
---

# 1. Overview

Oracle HTTP Server 12.2.1.4 (12cR2) 에 DB Client 19c 패치 적용 및 최신 OHS BP 적용 시

OHS Instance 기동 시 예외가 발생한 사례.

```
Cannot load mod_wl_ohs.so into server: rtld: 0712-001 Symbol ons_ssl_versions_validate was referenced from module mod_wl_ohs.so(), but a runtime definition
```


<br><br>


# 2. Descriptions

AIX 환경에서 발생하며, 특정 Symbolic을 export 하지 않아 발생하는 문제로, 이미 Bug fixed 되었다.

Fixed 된 bug은, Back Port로 이미 출시되어 있는 여러 Patch에 One-Off Patch가 나왔다.

<br>

**Critical Patch Update (CPU) Patch Advisor for Oracle Fusion Middleware - Updated for October 2024 (Doc ID 2806740.2)** 문서에서

**Oracle HTTP Server 12.2.1.4 Standalone (w/ Database Client 19c)** 섹션으로 이동을 하여, 나타나는 권고 패치를 모두 적용 한다.

<br>

권고 패치 목록 중에 Patch 36615359 : DATABASE RELEASE UPDATE 19.24 FOR FMW DBCLIENT 항목의 README에 위 언급한 Bug에 대해 서술되어 있다.

<br>

이번 사례는, DB Client 19c 업그레이드를 위한 패치와, OHS 최신 Bundle Patch만 적용만 환경에서 발생한 Known Bug Issue 인데,

권고 패치 목록을 모두 적용 및 README 항목에 충실해야 이러한 문제가 발생하지 않았을 것이다.


<br><br>


# 3. References

위에서 소개됨

