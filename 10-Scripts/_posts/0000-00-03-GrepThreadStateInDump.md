---
date: 2022-04-11 12:00:04 +0900
layout: post
title: "[script/bash] Thread Dump 파일들 비교 분석"
tags: [bash, thread, dump]
typora-root-url: ..
---

# 1. 개요

* Tomcat Thread Dump 분석을 하다가, 수 많은 Dump 파일에서 수 많은 Thread 상태를 추적해야 될 필요가 있었다.
* 여러 파일을 열어, 특정 내용들을 추출하는 스크립트를 짰다.
  * 수 많은 덤프의 유연하게 변화하는 내용을 단순 스크립트로 볼 수 없다.
  * 그냥 참고용이다~




# 2. 설명

```bash
# Thread Dump파일명* 으로 일괄 검색
FILE=/tmp/??*
FILE_LIST=$(ls -al ${FILE} | awk '{print $NF}')
echo "${FILE_LIST}" | \
while read FILE;
do
		# Thread Dump 파일 1개마다, 내용 검색
        echo
        echo "#############################"
        echo "########## ${FILE} ##########"
        echo "#############################"
        echo

        grep -n "catalina-exec" ${FILE} | \
        cut -d ':' -f1 | \
        while read TXT;
        do
                sed -n "${TXT},$((TXT+1))p" ${FILE}
        done

done
```

> Line 2. 수 많은 Dump 파일들을 한번에 조회하기 위해 파일명* 으로 지정한다.
>
> Line 3-5. 수 많은 Dump 파일들을 1개씩 조회하기 위해 while read 로 넘긴다.
>
> Line 14-16. 1개 Dump 파일에서 `catalina-exec` Thread 명을 검색하고, 해당 Line number를 while read 로 넘긴다.
>
> Line 18. `catalina-exec` Thread 명 밑에 Thread `State` 가 나오므로 +1 하여 본다.





---



Thread Dump 를 자동으로 뜨려면...

```bash
$ while true; \
do \
sleep 1 && \
JAVA_HOME=/usr/java/jdk-8u292-ojdkbuild-linux-x64 && \
PID=$(${JAVA_HOME}/bin/jps -v | grep "wasDocker" | awk '{print $1}') && \
${JAVA_HOME}/bin/jstack -l ${PID} > /tmp/${PID}.$(date "+%Y-%m-%d_%H:%M:%S")
done
```
