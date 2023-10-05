---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[WebLogic] 기동이 느린 경우"
tags: [Middleware, WebLogic, Slow, Startup]
typora-root-url: ..
---

# 1. 개요

기동이 느린 경우




# 2. 설명

config.xml에 `listen-address`가 blank라면 아이피 주소를 기입한다.

또는, `-Djava.net.preferIPv4Stack=true -Djava.net.preferIPv6Addresses=false`
