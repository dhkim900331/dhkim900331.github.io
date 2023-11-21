---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[WebLogic] 커넥션 풀 강제 반환"
tags: [Middleware, WebLogic, Harvest, Connection, Pool]
typora-root-url: ..
---

# 1. 개요

사용 가능한 커넥션 풀의 갯수가 어떤 조건보다 적을 때 얼마 만큼의 커넥션을 강제로 풀로 반납시킬 수 있다.
{{ site.content.br_small }}

# 2. 설명

(1). Console > Services > DataSource > Configuration > Connection Pool > Advanced

* Connection Harvest Max Count: 5

* Connection Harvest Trigger Count: 8
{{ site.content.br_small }}
(2). Test

* 현재 Connection Pool 은 10개
* 사용중인 Connection은 5개
* `사용중인 커넥션 > Connection Harvest Trigger Count == True`가 되면
  사용중인 커넥션에서 `한번에 5개의 커넥션을 강제 반환`시킨다.
* 결과적으로 사용중인 커넥션은 9개가 전혀 될 수 없고, 수집 되면 4개로 줄어든다.
