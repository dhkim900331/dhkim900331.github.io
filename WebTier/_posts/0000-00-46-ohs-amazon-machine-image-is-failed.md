---
date: 2025-11-18 13:54:05 +0900
layout: post
title: "[WebTier/OHS] ohs amazon machine image starting is failed"
tags: [WebTier, OHS, AMI, Amazon, Image]
typora-root-url: ../..
---

# 1. Overview

OHS 를 Scale-out 하기 위해 AMI(Amazon Machine Image)를 Clone 하여 내부 NM과 Component를 시작했지만, 실패한 사례

<br><br>


# 2. Descriptions

해당 준비된 AMI는 OHS Nodemanager와 Component가 이미 기동(RUNNING)이 되어 있는 상태에서 Snapshot 이 저장되었다.

해당 AMI 로 Scaled-out 시, OS -> NM -> Component 순으로 기동이 되는데, Component 단계에서 실패한다.

NM 측에서 이미 OHS Component의 .lck/.state 파일의 존재를 확인했고, 해당 파일을 통해 이미 기동 중이라는 것이다.

<br>

여기서 고객은 몇개월 간 두가지 사례를 겪었다.

1) NM 측이 이미 Component가 기동중이라는 사실을 깨달았다는 로그와, 그 Component와 정상적인 통신이 되지 않으니 kill -9 를 수행 하고 다시 재기동 하는 Nodemanager의 순기능 이다.
2) NM 측의 Process ID가 Number와 Component.lck 파일의 PID Number가 동일하여, NM 측에서 예상치 못한 Exception을 일으키는 경우다.

<br>

1번 사례의 경우, Exception을 목격하더라도 문제가 없이 기동이 되었으나,

2번의 경우에는 실패하였다.

<br>

해결책으로는, AMI snapshot 을 찍을 때 관련 프로세스들을 모두 종료하여 .lck/.state 와 같은 특수 파일이 없는 상태여야 한다는 것이다.

<br><br>


# 3. References

Oracle Http Server Fails to Start with "exit status = 0" Message (Doc ID 2810054.1)

