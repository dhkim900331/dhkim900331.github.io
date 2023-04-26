---
date: 2022-04-11 12:00:04 +0900
layout: post
title: "[Scripts/Bash] Log 일괄 점검 스크립트"
tags: [Scripts, Shell, Bash, Log, Grep]
typora-root-url: ..
---

# 1. 개요

* 고객사 솔루션(대표적으로 WAS) 로그 점검 시, 일괄 점검할 수 있는 스크립트



# 2. Scripts

## 2.1 run.sh

```bash
#!/bin/bash

LOG_HOME=/WEB/logs
GREP_HOME=/WEB/logs/greplist

START=$(date "+%Y%m010000")
END=$(date "+%Y%m010000" -d 'next month')

touch -t ${START} ${GREP_HOME}/start.txt
touch -t ${END} ${GREP_HOME}/end.txt

echo "##################################"
echo "CPU Usage: $(vmstat 1 2 | tail -1 | awk '{print 100-$15}') % "
echo "MEM Usage: $(free -m | grep "^Mem" | awk '{print (($3-$7)/$2)*100}') % "
echo "Disk Usage: $(df -h ${LOG_HOME} | tail -1 | awk '{print $5}')"
echo "##################################"

find ${LOG_HOME} -type f -name "*out*" ! -name "*.gz" \
-newer ${GREP_HOME}/start.txt \
! -newer ${GREP_HOME}/end.txt \
| xargs grep -f ${GREP_HOME}/grep.list \
| grep -vf ${GREP_HOME}/ignore.list \
| more
```

> 매월 1일 ~ 다음달 01일 까지 쌓인 `*out*` 파일, 그리고 `.gz` 파일을 제외하고 검색한다.
>
> 여기서 `out` 은, 표준출력 로그를 의미하였지만, 공통된 단어를 넣어서 적절히 사용한다.



## 2.2 grep.list

```
Exception
OutOfMemoryError
Dumping heap to
Too many open files
```

> Exception은 WAS, App 모든 로그를 출력하므로 가장 많은 데이터가 나오는 지점이다.
>
> OutOfMemoryError, Dumping heap to는 관련된 하나의 메시지다.



## 2.3 ignore.list

```
Caused by: java.net.SocketException: Connection reset
ORA-00001
Exception handling request to.*java.*Exception
at .*java.*)
\[INFO\]
```

> ignore.list 파일은, 제외할 단어 리스트이다.
>
> 위 설정은 다음의 메시지들을 grep.list에 의해 검색된 내용에서 제외한다.
>
> ```
> Caused by: java.net.SocketException: Connection reset
> ORA-00001
> Exception handling request to <URL>: java.lang.IllegalStateException
> Exception handling request to <URL>: java.lang.IndexOutOfBoundsException
> Exception handling request to <URL>: java.lang.NumberFormatException
> ... 등등 ...
> at com.examples.method(Code.java:356)
> at com.examples.method_2(Sample.java:1)
> ... 등등 ...
> [INFO] ~~ 관련 메시지 들



