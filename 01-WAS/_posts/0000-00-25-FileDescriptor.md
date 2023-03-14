---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WAS/WebLogic] File Descriptor 로그 확인 및 변경"
tags: [WAS, WebLogic]
typora-root-url: ..
---


# 1. 개요

File Descriptor 로그 확인 및 변경



# 2. 설명

## 2.1 현재 웹로직 FD값

도메인/servers/{server}/logs/{server}.log 에 다음처럼 로그가 보인다.



## 2.2 웹로직 FD 변경

```sh
ulimit -Ha # 하드웨어 설정값 확인
ulimit -Sa # 소프트웨어 설정값 확인
```



`commEnv.sh` 에서 resetFd 의 uname -n 4096 을 수정.

(ulimited 으로 된경우에는 수정이필요.)
