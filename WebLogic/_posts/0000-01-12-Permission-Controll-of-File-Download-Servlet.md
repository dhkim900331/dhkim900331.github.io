---
date: 2025-04-11 00:21:07 +0900
layout: post
title: "[WebLogic/Servlet] Permission Control of File Download Servlet"
tags: [Middleware, WebLogic, ]
typora-root-url: ..
---

# 1. Overview

Local의 File 을 다운로드 하는 Servlet의 권한 제어

<br>


# 2. Descriptions

File을 download 하는 구현 방식은 apache common lib를 포함해서 몇가지가 있다.

특정 고객이, 원하는 경로(예, domain_home 아래 config.xml 등)를 지정할 때 다운로드가 되어 이슈가 되었는데,

Servlet 을 그렇게 의도적으로 구현했으므로 예상 가능한 문제다.

<br>

Servlet code를 수정해야 한다.

예를 들어, Web application directory 아래에서만 download 할 resource를 찾도록 해야 하고,

더 넓은 Access 범위를 갖도록 원한다면 가장 좋은 대안은, Symbolic link를 사용하는 것이다.

<br>

Web app이 배포되어 기동되는 JVM의 실행 유저의 권한이, local disk의 resource에 접근가능하다면 위와 같은 문제가 발생할 수 있기 때문에,

Code를 수정해주어야 한다.


<br><br>

<br>

# 3. References

