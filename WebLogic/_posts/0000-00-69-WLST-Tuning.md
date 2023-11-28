---
date: 2023-05-11 09:07:29 +0900
layout: post
title: "[WebLogic/WLST] WLST Tuning"
tags: [Middleware, WebLogic, WLST, Tuning, CPU, Usage]
typora-root-url: ..
---

# 1. 개요

weblogic.WLST Class 의 동작 속도의 지연을 줄여보자.
{{ site.content.br_big }}
# 2. 설명

weblogic.WLST Class 를 사용할 때마다, 이 답답한 동작 속도를 개선해보자.

개선해보기 위해서 여러 자료들을 찾아보았다.

JVM Compiler 옵션 조정을 통해서 효과가 있을 것으로 보였다.
{{ site.content.br_small }}
참고한 문서로는, 크게 두가지가 있다.
{{ site.content.br_small }}
하나는, [Tiered Compilation in JVM](https://www.baeldung.com/jvm-tiered-compilation) 에서 JVM Compiler 동작 방식에 대해서 이해를 도왔다.

두번째로는, [4 Compilation Optimization](https://docs.oracle.com/javacomponents/jrockit-hotspot/migration-guide/comp-opt.htm#JRHMG117) 에서 JVM Compiler 개념이며, 여기서 `For example, the client compiler would probably be a better fit for a command line administration tool like WLST.` 와 같은 메시지도 발견했다.
{{ site.content.br_small }}
Compiler 옵션을 변경해가며 weblogic.WLST 가 체감이 될 정도로 빨라질 수 있는지 몇가지 Test를 진행해본다.
{{ site.content.br_big }}
# 3. 환경 및 테스트

다음의 시스템 환경에서 테스트 했다.

```
Red Hat Enterprise Linux release 8.7
CPU 2 core (Hyperthreading 으로 인해 논리적으로 4 core)
16 GB Memory
Java 1.8.0_351
WebLogic 14.1.1.0.0 (PSU Oct 2022 Applied)
```


다음의 단순한 WLST connect script를 실행하고, start/end date 값으로 평균을 계산했다.

```sh
echo start $(date)

java weblogic.WLST << EOF
connect(url='${SERVER_ADDR}:${SERVER_PORT}')
exit()
EOF

echo end $(date)
```


다음의 명령으로, WLST CPU/MEM 사용률만 1초 단위로 뽑아 평균을 계산했다.

```sh
sh << "EOF"
while true
do
  PID=$(ps -ef | grep weblogic.WLST | grep -v grep | awk '{print $2}')
  if [ "x$PID" == "x" ]; then
    continue
  fi
  
  ps -p ${PID} -o %cpu,%mem,cmd | tail -1 && sleep 1
done
EOF
```
{{ site.content.br_small }}

## 3.1 C2 Compiler (Default)

Default는 다음과 같다.

```
-server -XX:+TieredCompilation
```


첫 시도에, 실행 시 WLST script는 아래와 같은 Log를 얻는다.

```
start Wed May 10 12:28:06 KST 2023
end Wed May 10 12:28:32 KST 2023
```


ps script는 아래와 같은 Log를 얻는다.

```
109  0.6 java weblogic.WLST
132  0.9 java weblogic.WLST
...
237  4.3 java weblogic.WLST
```


이러한 방법으로 세번의 시도를 했고, 평균을 내보면

* WLST Connect 까지 평균 27초
* WLST 실행부터 종료까지 CPU 평균 220%
* WLST 실행부터 종료까지 MEM 평균 2.7%

가 계산된다.
{{ site.content.br_big }}
## 3.2 C2 + Tiered Off

적용된 옵션은 다음과 같다.

```
-server -XX:-TieredCompilation
```
{{ site.content.br_small }}
평균은,

* 32초
* 164%
* 2.4%
{{ site.content.br_big }}
## 3.3 C1 Compiler

적용된 옵션은 다음과 같다.

```
-client -XX:+TieredCompilation
```
{{ site.content.br_small }}
평균은,

* 27초
* 218%
* 2.6%
{{ site.content.br_small }}
C1 Compiler 옵션을 쓰면 괜찮을 것이라는 공식 문서 내용이 있지만, 마법같은 변화는 없다.
{{ site.content.br_big }}
## 3.4 C1 + Tiered Off

적용된 옵션은 다음과 같다.

```
-client -XX:-TieredCompilation
```


평균은,

* 31초
* 169%
* 2.4%
{{ site.content.br_small }}
중간 계층의 최적화 Compiler 기능을 끄므로써, Sec는 늘어났지만, 소요되는 OS Resource가 절약 되었다.
{{ site.content.br_big }}
## 3.5 Just Interpreter

모든 Compile 기능은 끄고, Interpreter Mode로만 적용한다.

```
-Xint
```


평균은,

* 95초
* 101%
* 1.4%
{{ site.content.br_small }}
OS Resource 가 상당량 절약 되었다.

그러나 Runtime이 매우 길다.
{{ site.content.br_big }}
# 4. Outcome

Compiler Mode를 간략히 살펴보면 HotSpot JVM은 `-client (C1)` 와 `-server (C2)` 가 있다.

C1은 Method를 빠르게 Compile 하여 덜 최적화되지만, Startup이 빠른 장점이 있다.

C2는 비교적 그렇지 않지만 자주 실행되는 Method (`-XX:CompileThreshold`) 를 Byte code 에서 Native code로 변환한다. 이러한 최적화를 오랜 시간 수행되는 Enterprise App에 필요로 한다.
{{ site.content.br_small }}
위 내용을 좀 더 이해하게 되었으며,

이번 Post에서 다룬 weblogic.WLST 는 대부분 단순 일회성으로 처음과 끝을 반복 실행하는 Client Program의 성격이며,

CPU Resource에 매우 민감하다면, [3.5 Just Interpreter](#-35-just-interpreter) (그러나 너무 느리다)

CPU Resource에 조금 민감하다면, [3.2 C2 + Tiered Off](#h-32-c2+tiered-off) 중에 선택해야 할 것으로 보인다.
{{ site.content.br_small }}
Runtime 기준에서 살펴보자면, [3.1 C2 Compiler (Default)](#h-31-c2-compiler-(default)) 와 [3.3 C1 Compiler](#h-33-c1-compiler) 가 동일하지만, 약간의 Resource 차이가 있으므로 후자를 선택하면 될 것으로 보인다.
{{ site.content.br_small }}
이번 테스트는 매우 심플/협소하기도 했고, 평균의 평균이라 데이터에 약간의 오류가 있었다.
{{ site.content.br_big }}
# 5. References

[Tiered Compilation in JVM](https://www.baeldung.com/jvm-tiered-compilation) 

[4 Compilation Optimization](https://docs.oracle.com/javacomponents/jrockit-hotspot/migration-guide/comp-opt.htm#JRHMG117)

**E-WL: WLST Script Spikes Up CPU To More Than 300% (Doc ID 2903838.1)**
