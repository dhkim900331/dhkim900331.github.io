---
date: 2022-11-26 14:25:51 +0900
layout: post
title: "[Scripts/Shell] Log를 Compress 및 Backup"
tags: [Scripts, Shell, Bash, Tar, Rotation, Find]
typora-root-url: ..
---

# 1. 개요

Log를 Tar 압축하여 분리/삭제 해본다.



# 2. 전체 Script

전체 Script 부터 공개를 하면

```shell
#!/usr/bin/bash

# 백업하려는 로그의 원본 위치
LOG_HOME=/sw/weblogic/14c/domains/base_domain/logs
LOG_HOME_NOHUP=${LOG_HOME}/nohup
LOG_HOME_GCLOG=${LOG_HOME}/gc

# 압축해서 보관할 위치
BACK_LOG_HOME=/sw/weblogic/14c/domains/base_domain/backup
BACK_LOG_HOME_NOHUP=${BACK_LOG_HOME}/nohup
BACK_LOG_HOME_GCLOG=${BACK_LOG_HOME}/gc


# 압축 보관할 디렉토리 생성
mkdir -p ${BACK_LOG_HOME_NOHUP} ${BACK_LOG_HOME_GCLOG}

### 수정 1일 지난 파일 검색 및 while loop로 압축
# NOHUP
find ${LOG_HOME_NOHUP} -type f -name "*out*" -mtime +1 |
while read LINE
do
	/usr/bin/tar -czf ${BACK_LOG_HOME_NOHUP}/$(basename ${LINE}).tar.gz ${LINE}
	/usr/bin/rm ${LINE}
done

# GCLOG
find ${LOG_HOME_GCLOG} -type f -name "*out*" -mtime +1 |
while read LINE
do
	/usr/bin/tar -czf ${BACK_LOG_HOME_GCLOG}/$(basename ${LINE}).tar.gz ${LINE}
	/usr/bin/rm ${LINE}
done
```



`백업하려는 로그의 원본 위치` 는 원본 Log가 쌓이는 위치이다.

여기서는 `LOG_HOME` 아래에 `nohup` 과 `gc` 디렉토리에 많은 Log가 쌓인다고 가정한다.



`압축해서 보관할 위치` 는 원본 Log가 압축되어 보관될 위치이다.

여기에서는, 각각 대응하여 보관하기 위해 `BACK_LOG_HOME_...` 가 있다.



`수정 1일 지난 파일 검색 및 while loop로 압축` 아래에는 `while loop` Section이 두번 나타난다.

각각 `nohup`과 `gc` 의 하루 지난 파일(`-mtime +1`)을 찾아 `tar` 와 `rm` 명령어를 실행한다.



