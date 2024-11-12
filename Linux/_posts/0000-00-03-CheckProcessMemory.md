---
date: 2022-10-06 17:15:38 +0900
layout: post
title: "[Linux/Memory] Check the process memory"
tags: [OS, Linux, Process, RSS]
typora-root-url: ..
---

# 1. Overview

시스템 점검 중 가용가능한 메모리가 얼마 없어, 메모리-과점유 프로세스 점검 차 간단하게 짜보았다.


<br><br>


# 2. Descriptions

```sh
PID=$(jps -v | grep "Standalone" | awk '{print $1}')
PID_SED=$(echo ${PID} | sed 's| |\||g')
ps -eo start,user,pid,rss,vsize,pmem,pcpu --sort -rss | egrep "${PID_SED}"
```


당시 점검 대상 시스템은 WAS-Middleware 시스템이라, jps 명령으로 실행중인 java 프로세스의 PID 값을 따왔다.

PID값은 줄바꿈으로 정렬되어 있으나, echo 를 통해 한줄로 정리할 수 있고, 정리된 값을 sed 로 다음에서 egrep 을 위해 파이프라인(|)을 삽입한다.

프로세스를 실제 메모리 점유량(rss)으로 정렬한다.

<br>

실제 값은 아래처럼 나타난다.

```sh
  Aug 19 switch   31247 2668532 4218988  8.1 1.5
  May 13 jboss     6954 2238932 4077136  6.8 0.1
  Aug 25 jboss     3340 2124324 3681156  6.5 0.4
  Jun 16 jboss    15222 1510080 3027452  4.6 0.1
  Jun 16 jboss     2671 1457564 2999848  4.4 0.1
  Feb 04 mcats    31023 1446812 3009620  4.4 0.3
  Feb 04 jboss    28590 1439460 2982388  4.4 0.1
  Feb 04 jboss    28047 1417532 2964584  4.3 0.1
  Jun 09 jboss    17321 1322156 2966276  4.0 0.1
  Feb 04 jboss    22411 1195116 4085684  3.6 0.1
  Jun 16 rdsbody  12274 1147092 3064844  3.5 0.1
  Aug 26 jboss    30700 1127772 3085192  3.4 0.1
  Jun 30 jboss      928 1104764 2659132  3.3 0.1
  Jun 02 jboss    16172 924408 3009404  2.8 0.1
  Sep 02 jboss    25325 916912 2916160  2.8 0.1
  Aug 05 jboss    16687 901736 2949308  2.7 0.1
  Jun 26 jboss    25803 877012 2947896  2.6 0.1
  Feb 16 jboss    11689 867604 2420524  2.6 0.1
  Jul 07 jboss    17189 794748 2976704  2.4 0.1
  Jun 10 jboss    23112 771880 3025428  2.3 0.1
  Feb 04 jboss    13343 695800 2942740  2.1 0.1
  Feb 04 jboss    20783 639492 2626272  1.9 0.1
  Feb 04 jboss    30022 626352 2611116  1.9 0.1
13:47:41 jboss    16111  1928 102704  0.0  0.0
```

