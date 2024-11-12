---
date: 2022-05-09 15:45:29 +0900
layout: post
title: "[Putty] Putty Connect Host With CLI"
tags: [Putty, SSH, CLI]
typora-root-url: ..
---

# 1. Overview

포스트하기에도 매우 심플한 내용... 고객사 등등 여러 호스트에 접속을 시도할 때마다,

Putty.exe 에 세션을 저장하는 등의 불편한 환경이라면 사용할만 하다.


<br><br>


# 2. Descriptions

```shell
putty.exe -ssh -P port user@host -pw pwd
# putty.exe -ssh -P 22 dhkim@192.168.56.2 -pw dhkim
```

바로가기.exe 를 활용하거나, cmd 내에서 바로 명령만 입력하여도 자동 접속을 수행한다.

