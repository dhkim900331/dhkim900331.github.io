---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[WebLogic/WLS8] 웹로직 8버전 USER_MEM_ARGS 기능 넣기"
tags: [Middleware, WebLogic, WLS8, USER_MEM_ARGS]
typora-root-url: ..
---

# 1. 개요

웹로직 8버전만 사용자 정의 메모리 아규먼트 기능이 없다.

사실 기능이라고 하기에는 단순한 문자열 치환이다...
{{ site.content.br_small }}

# 2. 설명

startA.sh 과 같이 사용자 스크립트에 `export USER_MEM_ARGS` 한다면

이 startA.sh은 결국 startWeblogic.sh 을 노헙으로 실행.

startWeblogic.sh에서는 하위 프로세스로 실행되므로 앞에서 export된 USER_MEM_ARGS 변수를 내부적으로 사용가능.

echo 등으로 찍히진 않는다. (물론 startWeblogic.sh을 실행시키면 찍힌다)
{{ site.content.br_small }}
여튼 프로그래밍하여 startWeblogic.sh 하단쯤에 `if USER_MEM_ARGS != ""` 등 조건을 부여하여 `MEM_ARGS = USER_MEM_ARGS` 하자.
{{ site.content.br_small }}
```bash
if [ "${USER_MEM_ARGS}" != "" ]; then
	MEM_ARGS="${USER_MEM_ARGS}"
fi
export MEM_ARGS
```
