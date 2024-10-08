---
layout: post
title: "[WebLogic] Redeploy App With Removing Cache"
tags: [Middleware, WebLogic, Deploy, Cache]
typora-root-url: ..
---

# 1. Overview

Nostage mode App의 Redeploy를 단순히 Cache 삭제하여 수행하는 방법
{{ site.content.br_big }}

# 2. Descriptions

App은 배치 시에, `${DOMAIN_HOME}/servers/<SERVER>/tmp/_WL_user` 아래에 생성되고,

첫 호출되는 JSP는 class compile 되어 위치한다.
{{ site.content.br_small }}
(1) Instance 종료

(2) `_WL_user` 아래 App 삭제

(3) Instance 시작

단순한 세가지 단계만으로 App 재배포가 완료된다.
{{ site.content.br_big }}

# 3. References

**How To Clear The Server Cache Directories (cache, stage, tmp) (Doc ID 1323602.1)**

**How to Achieve Auto Compile of Updated JSPs in WebLogic Server (Doc ID 1358621.1)**
