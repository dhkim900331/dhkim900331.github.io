---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[WebLogic] 다른 JDBC Driver 적용 방법"
tags: [Middleware, WebLogic, JDBC, Driver, Setup]
typora-root-url: ..
---

# 1. 개요

다른 JDBC Driver 적용 방법
{{ site.content.br_big }}
# 2. 설명

derby.jar로 설명.
{{ site.content.br_small }}
스크립트 쉘에 옵션.

`export EXT_PRE_CLASSPATH=derby.jar`
{{ site.content.br_small }}
데이터 소스 생성 시

드라이버 클래스 이름: `org.apache.derby.jdbc.EmbeddedDriver`
{{ site.content.br_small }}
어때요 참쉽죠?
