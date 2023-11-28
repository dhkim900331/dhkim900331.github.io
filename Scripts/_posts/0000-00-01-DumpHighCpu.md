---
date: 2022-04-11 11:39:37 +0900
layout: post
title: "[Scripts/Bash] High Cpu Process의 분석을 위한 Dump"
tags: [Scripts, Shell, Bash, Thread, Dump, CPU]
typora-root-url: ..
---

# 1. 개요

* 커피 브랜드 프로모션 지원 중에, High CPU Thread 추적을 위해 만든 스크립트
{{ site.content.br_small }}

# 2. 설명

```bash
#!/bin/bash

LOG_DIR=/tmp/2022-03-31_OSC_Monitoring
#SERVER=mobile
#SERVER=mobile2
SERVER=mobile3
PID=$(ps -ef | grep java | grep -w "\-DSERVER=${SERVER}" | awk '{print $2}')
DT=$(date "+%Y%m%d_%H%M%S")

ps -eLo pid,ppid,tid,pcpu,comm | grep ${PID} | awk '{ print "pccpu: "$4" pid: "$1" ppid: "$2" ttid: "$3" comm: "$5}' | sort -n > ${LOG_DIR}/${PID}_cpu.out_${DT}
/usr/lib/jvm/java-1.8.0/bin/jstack -l ${PID} > ${LOG_DIR}/${PID}_thread.out_${DT}
```

> ${PID}_cpu.out 파일에서 ttid 를 계산기로 16진수 변환 후, ${PID}\_thread.out 에서 찾는다.
