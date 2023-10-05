---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[WebLogic] 플러그인 정보, 플러그인 버전 보는 방법"
tags: [Middleware, WebLogic, Plugin]
typora-root-url: ..
---

# 1. 개요

플러그인 정보, 플러그인 버전 보는 방법



# 2. 설명

오라클 권장은 플러그인 1.1 이상은 웹로직 버전에 크게 상관없이 최신으로 유지

오라클 권장사항은 12c 최신 플러그인 안되면 11g최신 플러그인, 그래도 안되면 10g용 플러그인 사용 하도록



## 2.1 WebLogic Proxy Plug-in 12.1.2

* A WebLogic Server 12.1.2 Web server plug-in can proxy to the latest Patch Set release of a 9.x, 10.0, and 10.3.x server.
* [참고](http://www.oracle.com/technetwork/middleware/webtier/downloads/index.html)



## 2.2 WebLogic Proxy Plug-Ins 12.1.3

* A WebLogic Proxy Plug-In can proxy to the latest patch set release of a 10.0, 10.3.x, 12.1.1, and 12.1.2 server.
* [참고](http://www.oracle.com/technetwork/middleware/webtier/downloads/index.html)



## 2.3 플러그인 버전 확인 방법

* WLS 10g 플러그인(1.0 이라 부르는) 이하들은 `BridgeConfigInfo 옵션`으로만 Build Date Time 확인 가능
* WLS 11g 플러그인(1.1 이라 부르는) 이상들은 `strings mod_wl.so | grep -i wlsplugins` 로 확인 가능
