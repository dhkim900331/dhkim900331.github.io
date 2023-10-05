---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] 12c 버전 네이밍"
tags: [Middleware, WebLogic, Version, 12c]
typora-root-url: ..
---

<br># 1. 개요

12c version naming rule.

<br>
# 2. 설명

12.2.1.0.160719

12.2 => Major version 12.2이다. 12cR2

12.2.1 => Major 12.2에 Minor 1버전

12.2.1.1 => Major 12.2, Minor 1, patch set  1

12.2.1.0.160719 => Major 12.2, Minor 1, patch set 0, PSU(patch set update) 160719

<br>
* patch set이 나올 때 기능추가 및 변화가 존재
* PSU는 기능추가 및 변화는 없음.
* PSU버전에 대해서 기존에는 웹로직 로그 및 `weblogic.version`에 표시되었지만 지금은 표시안되고 무조건 `opatch lsinventory` 해야만 알 수 있음.
