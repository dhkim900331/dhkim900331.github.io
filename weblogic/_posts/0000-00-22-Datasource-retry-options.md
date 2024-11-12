---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] 데이터소스 커넥션 풀 시도 횟수 관련 옵션"
tags: [Middleware, WebLogic, Datasource, Connection Pool]
typora-root-url: ..
---


# 1. Overview

데이터소스 커넥션 풀 시도 횟수 관련 옵션


<br><br>


# 2. Descriptions

![Datasource-retry-options_1](/../assets/posts/images/WebLogic/Datasource-retry-options/Datasource-retry-options_1.png)

<br>

Connection Reserve Timeout 기본값 10초.

Reached maximum data... 와 같이 Pool connection이 모두 사용되는 경우, Connection Reserve Timeout 동안 Free connection pool 찾음.

이후 없으면 503 error.

해당 Connection Reserve Timeout 초 내에 몇번의 요청을 하는 구조인지는 모르겠다.
