---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[WAS/WebLogic] 다른 JDBC Driver 적용 방법"
tags: [WebLogic, JDBC, Driver, Setup]
typora-root-url: ..
---

# 1. 개요

다른 JDBC Driver 적용 방법




# 2. 설명

derby.jar로 설명.



스크립트 쉘에 옵션.

`export EXT_PRE_CLASSPATH=derby.jar`



데이터 소스 생성 시

드라이버 클래스 이름: `org.apache.derby.jdbc.EmbeddedDriver`



어때요 참쉽죠?
