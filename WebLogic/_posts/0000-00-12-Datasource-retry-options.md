---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] 데이터소스 커넥션 풀 시도 횟수 관련 옵션"
tags: [Middleware, WebLogic, Datasource, Connection Pool]
typora-root-url: ..
---

<br># 1. 개요

데이터소스 커넥션 풀 시도 횟수 관련 옵션

<br>
# 2. 설명

![Datasource_retry_options_1](/../assets/posts/images/01-WebLogic/Datasource_retry_options/Datasource_retry_options_1.png)

<br>
Connection Reserve Timeout 기본값 10초.

사진상 3 초일 경우,

<br>
Reached maximum data... 에러의 경우

3초 동안 Free connection pool 찾음.

<br>
없으면 503 error.

<br>
해당 3초 내에 몇번의 요청을 하는 구조인지는 모르겠다.
