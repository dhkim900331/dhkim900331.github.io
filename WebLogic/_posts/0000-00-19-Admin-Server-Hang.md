---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] Admin Server Hang 일 때, MSI Mode socket time out"
tags: [Middleware, WebLogic, Hang, MSI]
typora-root-url: ..
---

<br># 1. 개요

Admin Server Hang 일 때, MSI Mode socket time out

<br>
# 2. 설명

managed server가 admin server에 req 하였지만, admin server의 hang 으로 ack 보내지 못할 때.

`-Dweblogic.http.client.defaultReadTimeout` 으로 MSI mode 를 실행하도록 하자. 
