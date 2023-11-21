---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[WebLogic] 웹로직 Client IP와 WebServer IP를 얻는 방법"
tags: [Middleware, WebLogic, Plugin, Clientip, Realip]
typora-root-url: ..
---

# 1. 개요

WebLogic AP 단에서 앞단 WebServer IP 또는 L4, 또는 Client IP를 얻어야 하는 경우가 발생한다.

이를 위해 WL-Proxy-Client-IP Header 를 제공한다.
{{ site.content.br_small }}

# 2. 설명

## 2.1 Client Real IP

`콘솔에서 서버 Conf 페이지 -> General -> WebLogic Plug-in Enabled 를 True로 설정`

이렇게 하면 `클라이언트 -> 웹서버 -> 웹로직의 경우` 웹로직에서 웹서버의 헤더가 아닌 클라이언트(브라우저)의 헤더를 가져오므로 클라이언트의 아이피를 얻을 수 있다.

웹로직에서는 `request.getRemoteAddr();` 메서드로 클라이언트 아이피를 얻을 수 있다.
{{ site.content.br_small }}
> 물론 위의 설정은, 앞단 (L4) 에서부터 Client IP를 backend 로 넘겨줄 수 있도록 하는 `X-Forwarded-For` 헤더가 제공되어야 한다.
>
> 아무런 Header가 없는 상황에서 WAS나, WEB의 기능만으로 없던 Client IP를 끄집어내는게 아니다.
