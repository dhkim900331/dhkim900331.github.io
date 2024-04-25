---
date: 2023-11-21 15:39:45 +0900
layout: post
title: "[Programming/Batch] VPN Command Line Interface"
tags: [Programming, Batch, Cisco, Anyconnect, VPN]
typora-root-url: ..
---

# 1. Overview

내 근무처는 Cisco AnyConnect Secure Mobility Client (version 4.10.05111) 로 VPN을 활성화해야 업무를 볼 수 있다.

매번, PC boot 후 GUI Tool로 활성화 하는 것이 불편하여 vpncli.exe CLI 로 활성화 하는 것을 정리한다.
{{ site.content.br_big }}
# 2. Description

`C:\Program Files (x86)\Cisco\Cisco AnyConnect Secure Mobility Client\vpncli.exe` 를 제어할 수 있기 때문에, 다음과 같은 batch 를 작성했다.
{{ site.content.br_small }}
Relogin.cmd 는 작업 스케쥴러에 등록하여, PC boot 시에, 또는 매일 아침에 실행하도록 하여 VPN 재접속을 수행한다.

vpncli.exe는 vpnui.exe(GUI)가 종료되어 있어야 한다.
{{ site.content.br_small }}
env.cmd

```bash
@echo off

rem 변수 설정
set ScriptHome=%~dp0
set LoginCmd=%ScriptHome%\Login.cmd
set LogoffCmd=%ScriptHome%\Logoff.cmd
set ipconfigCmd=%ScriptHome%\ipconfig.cmd

set vpnExe=C:\Program Files (x86)\Cisco\Cisco AnyConnect Secure Mobility Client\vpncli.exe
set vpnHost=<vpnHost>
set vpnUsername=<vpnUsername>
set vpnPassword=<vpnPassword>
set vpnResponseFile=%ScriptHome%\rsp.txt
```
{{ site.content.br_small }}
Login.cmd

```bash
@echo off

call "%~dp0\env.cmd"

rem 파일에 저장될 사용자 이름과 비밀번호
(
    echo %vpnUsername%
    echo %vpnPassword%
) > "%vpnResponseFile%"

"%vpnExe%" connect %vpnHost% -s < "%vpnResponseFile%"

rem 파일 삭제
del "%vpnResponseFile%"
```
{{ site.content.br_small }}
Logoff.cmd

```bash
@echo off

call "%~dp0\env.cmd"

rem 프로그램 실행
"%vpnExe%" disconnect
```
{{ site.content.br_small }}
ipconfig.cmd

```bash
@echo off

call "%~dp0\env.cmd"

echo %date% %time% > "%ipconfigRsp%"
ipconfig >> "%ipconfigRsp%"
```
{{ site.content.br_small }}
Relogin.cmd

```bash
@echo off

call "%~dp0\env.cmd"

call "%LogoffCmd%"
timeout /t 5 >nul
call "%LoginCmd%"
timeout /t 5 >nul
rem Must run as Administator
call "%ipconfigCmd%"
exit
```

