---
date: 2024-11-21 10:08:10 +0900
layout: post
title: "[Java/Crash] Where is hs_err_pid file?"
tags: [Java, JVM, ]
typora-root-url: ../..
---

# 1. Overview
JVM Core dumped 시, hs_err_pid 파일의 위치

<br>


# 2. Descriptions
`-XX:ErrorFile` 지시어가 가리키는 위치에, 파일을 쓸 수 없으면 기본값으로 대체된다.
Runtime JVM에 지시어 자체를 쓰지 않더라도, 기본값으로 대체된다.

기본값은, 실행중인 프로세스의 Working Directory 이다.
Working Directory는 다음의 명령으로 조회 한다.
```sh
$ sudo lsof -p 664406 | grep cwd
 
 lsof: WARNING: can't stat() fuse.gvfsd-fuse file system /run/user/8001/gvfs
       Output information may be incomplete.
 java    664406 weblogic  cwd       DIR               8,17      4096 537292990 /sw/weblogic/12cR2/domains/base_domain
---
```

# 3. References
[B.1.5 Other -XX Options](https://www.oracle.com/java/technologies/javase/clopts.html)
[C.1 Location of Fatal Error Log](https://www.oracle.com/java/technologies/javase/felog.html#gbwcy)
[-XX:ErrorFile doesn't work](https://bugs.openjdk.org/browse/JDK-8189672)
