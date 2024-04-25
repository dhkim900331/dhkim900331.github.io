---
date: 2022-08-02 14:56:46 +0900
layout: post
title: "[Database/MySQL] Backup & Recovery (백업과 복구)"
tags: [Database, MySQL, Backup, Recovery]
typora-root-url: ..
---

# 1. 개요

아주 심플하게, 바로 써먹을 수 있는 백업과 복구 방법을 알아보자.
{{ site.content.br_small }}
# 2. Backup

부분 백업도 가능하며, 아래 명령줄은 root 계정으로 전체 DB를 ${FILENAME} 으로 백업한다.

```bash
$ FILENAME="full_backup.sql_$(date "+%Y_%m_%d_:_%H:%M:%S")"
$ mysqldump -u root -p --all-databases > ${FILENAME}
```
{{ site.content.br_small }}
# 3. Recovery

다음의 명령으로, 복구할 수 있다.

```bash
$ mysql -u root -p < ${FILENAME}
```
{{ site.content.br_small }}
장애로 인하여 DB데이터를 잃어버린 경우 복구하는게 아니라,

데이터를 이전 백업본으로 돌아가는 경우라면..

위 명령을 수행하면, 덮어씌우는 게 아니라 새로 INSERT를 하게 되어 동일한 data가 삽입될 수 있다고 한다(?).

그럴 경우 복구 하기 전에 아래 명령어들을 모두 수행한다.
{{ site.content.br_small }}
다음을 우선 실행하여, 데이터를 날린다.

```bash
$ mysql -u root -p <DB> -e "drop database <DB>"
```
{{ site.content.br_small }}
DB를 재생성하고, 특정 유저에게 있던 권한도 날라갔으므로 DB권한을 다시 부여한다.

```bash
mysql> CREATE DATABASE <DB> CHARACTER SET utf8 COLLATE utf8_bin;
mysql> GRANT ALL PRIVILEGES ON <DB>.* TO '<USERNAME>'@'%' WITH GRANT OPTION;
mysql> FLUSH PRIVILEGES;
```

