---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] JSSE 및 SSL 관련"
tags: [Middleware, WebLogic, JSSE, SSL]
typora-root-url: ..
---


# 1. 개요

JSSE 및 SSL 관련
{{ site.content.br_big }}
# 2. 설명

~ WebLogic 10.3.2 : Certicom SSL + SHA1 만 가능.

WebLogic 10.3.3 ~ : Use JSEE Enabled를 통해 SHA2 가능.  SHA2 가 JSSE 환경에서만 동작.

WebLogic 12c : JSSE가 Default로 Enabled되어 있음.
