---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[WebLogic] Windows 환경에서 WebLogic Java Thread Dump 추출 방법"
tags: [Middleware, WebLogic, Java, Thread, Dump, Windows]
typora-root-url: ..
---


# 1. 개요
* WebLogic Console 메뉴에서 Thread Dump 생성
* jdk의 jstack tool 사용하여 Thread Dump 생성

위 방법 외에 WebLogic이 실행중인 cmd.exe에서 Ctrl + Break 키조합으로

Thread Dump 생성 방법입니다.
{{ site.content.br_big }}
# 2. 설명

## 2.1 Scripting

(1). startAdmin.cmd (인스턴스 기동 스크립트)

```shell
...skip...
start /B %DOMAIN_HOME%\bin\startWebLogic.cmd >> %LOG_DIR%\%SERVER_NAME%.out 2>&1
tail -f %LOG_DIR%\%SERVER_NAME%.out
```

> 일반적인 기동 스크립트의 예시일 뿐
{{ site.content.br_small }}
(2). startAdmin.bat (새로운 스크립트 파일)

```shell
C:\Windows\System32\cmd.exe /k startAdmin.cmd
```


(3). startAdmin.bat 실행

![Java-Thread-Dump-On-Windows_1](/../assets/posts/images/WebLogic/Java-Thread-Dump-On-Windows/Java-Thread-Dump-On-Windows_1.png)



(4). `Ctrl + Break` 일괄 작업을 끝내지 않음. `N`

![Java-Thread-Dump-On-Windows_2](/../assets/posts/images/WebLogic/Java-Thread-Dump-On-Windows/Java-Thread-Dump-On-Windows_2.png)



(5). `tail -f LOG 실행` (startAdmin.bat 으로 실행하지 않은 경우, tail 명령어로 다시 log를 띄울 수 없습니다.)

![Java-Thread-Dump-On-Windows_3](/../assets/posts/images/WebLogic/Java-Thread-Dump-On-Windows/Java-Thread-Dump-On-Windows_3.png)



(6). 위 화면에도 일부 보이듯, log에 Dump가 기록되어 있습니다.

* startAdmin.cmd 의 /B 옵션 : 옵션 다음 명령줄을 백그라운드 실행
* startAdmin.bat 의 /K 옵션 : 옵션 다음 명령줄 실행이 끝나도 세션 유지