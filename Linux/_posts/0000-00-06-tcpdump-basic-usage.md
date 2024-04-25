---
date: 2024-01-11 12:11:25 +0900
layout: post
title: "[Linux] tcpdump basic usage"
tags: [Linux, OS, tcpdump]
typora-root-url: ..
---

# 1. Overview

tcpdump의 사용법은 Google 에 매우 많다.

여기서는 더 간략한 내용만 포스팅한다.
{{ site.content.br_big }}
# 2. Descriptions

`sudo tcpdump -i any -vvv -nn -w /tmp/tcpdump.bin port 443` 명령으로 System에 있는 여러 interface(ifconfig) 에서 port 443 을 추적하여 file에 binary 로 기록한다.
{{ site.content.br_small }}
`sudo tcpdump -r /tmp/tcpdump.bin` 명령으로 tcpdump.bin 바이너리 기록된 데이터를 ASCII 로 변환하여 사람이 읽을 수 있다.
{{ site.content.br_small }}
어떻게 이걸 분석하는지에 대한 내용은 `-vvv` 옵션으로 기록된 Log 를 google 또는 gpt 에 질의하면 쉽게 알 수 있다.
