---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[WebLogic] 다른 JDBC Driver 적용 방법"
tags: [Middleware, WebLogic, JDBC, Driver, Setup]
typora-root-url: ..
---

# 1. Overview

다른 JDBC Driver 적용 방법


<br><br>


# 2. Descriptions

derby.jar로 설명.

<br>

스크립트 쉘에 옵션.

`export EXT_PRE_CLASSPATH=derby.jar`

<br>

데이터 소스 생성 시

드라이버 클래스 이름: `org.apache.derby.jdbc.EmbeddedDriver`

<br>

어때요 참쉽죠?
