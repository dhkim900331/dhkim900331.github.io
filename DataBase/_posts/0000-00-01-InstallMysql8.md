---
date: 2022-05-31 11:38:35 +0900
layout: post
title: "[Database/MySQL] MySQL 8.X 설치 (Source Compile)"
tags: [Database, MySQL, Source, Compile, Build]
typora-root-url: ..
---

# 1. 개요

고객사에 MySQL 설치가 필요하게 된 상황이 생겨서, `rpm` 설치 또는 `source build` 설치 등을 확인하고 있다. (정말 별의별 업무를 다하게 된다 ㅠㅠ)

여튼, `rpm`은 차후, 기록하고, 폐쇄망 타겟으로 `source build` 를 진행해본다.
{{ site.content.br_small }}
# 2. 문서 작성 기준이 되는 테스트 환경

1core/8gb mem/CentOS Stream release 8
{{ site.content.br_small }}
# 3. 사전 준비사항

## 3.1 설치 파일

### 3.1.1 Boost

MySQL Build 하기 위해서 Boost 라는 C++ Library 집합이 필요하다. 

작성일 기준 1.79.0 이 최신이나, MySQL 최신버전 8.0.29 설치시에는 Boost 1.77.0 을 필요로 한다.
{{ site.content.br_small }}
https://www.boost.org 에서 boost_1_77_0.tar.gz 을 다운로드 한다.

URL : https://sourceforge.net/projects/boost/files/boost/1.77.0
{{ site.content.br_small }}
다운로드 받은 파일은, 특정 경로에 압축을 해제한다.
`Path : /usr/ssw/mysql/installFiles/boost_1_77_0`
{{ site.content.br_small }}
### 3.1.2 MySQL

https://dev.mysql.com/downloads/mysql ->

Source Code ->

All Operating Systems (Generic) (Architecture Independent) ->

Compressed TAR Archive, Includes Boost Headers

- mysql-boost-8.0.29.tar.gz 파일을 다운로드 받는다.
{{ site.content.br_small }}
다운로드 받은 파일은, 특정 경로에 압축을 해제한다.

`Path : /usr/ssw/mysql/installFiles/mysql-8.0.29`
{{ site.content.br_small }}
## 3.2 Compiler & Packages

 - cmake
 - make 3.75 이상
 - 최소 GCC 7.1 또는 Clang 5
 - ncurses.x86_64
 - rpcgen

rpcgen은 CentOS 8 Default Repository 에서 찾을 수 없고,

다음과 같은 PowerTools 에서 찾을 수 있다.

URL : https://centos.pkgs.org/8/centos-powertools-x86_64/rpcgen-1.3.1-4.el8.x86_64.rpm.html
{{ site.content.br_small }}
```bash
$ sudo yum install -y cmake.x86_64 make.x86_64 gcc.x86_64 ncurses-devel.x86_64 
$ sudo yum localinstall -y rpcgen-1.3.1-4.el8.x86_64.rpm
```
{{ site.content.br_small }}
공식 가이드로 요구하는 위 목록 외에, 설치 시 에러로 다음을 요구한다.

```bash
$ sudo yum install -y gcc-toolset-11-gcc gcc-toolset-11-gcc-c++ gcc-toolset-11-binutils libtirpc-devel.x86_64
```
{{ site.content.br_small }}
# 4. 설치

## 4.1 MySQL

```bash
$ cd /usr/ssw/mysql/installFiles/mysql-8.0.29
$ rm -f CMakeCache.txt && cmake . \
-DFORCE_INSOURCE_BUILD=on \
-DCMAKE_INSTALL_PREFIX=/usr/ssw/mysql \
-DMYSQL_DATADIR=/logs/mysql \
-DMYSQL_TCP_PORT=3306 \
-DDEFAULT_CHARSET=utf8 \
-DDEFAULT_COLLATION=utf8_general_ci \
-DWITH_BOOST=/usr/ssw/mysql/installFiles/boost_1_77_0 \
-DDOWNLOAD_BOOST=off

$ make clean && make && make install
```

> charset, collation은 https://dev.mysql.com/doc/refman/8.0/en/charset-mysql.html 참고
>
> 2~4시간 소요
{{ site.content.br_small }}
# 5. 환경 구성

## 5.1 데이터 디렉토리 초기화

초기 설치 후 반드시 데이터 디렉토리를 초기화 해야 한다.

공식 가이드에서 `mysql-files` 디렉토리는 `LOAD DATA INFILE "text.txt" INTO table mytable;` 와 같은 Query를 실행 할 때, `mysql-files/test.txt` 파일을 읽는 위치이다.

기본값은, `CMAKE_INSTALL_PREFIX/mysql-files` 이고, `mysqld --initialize --secure_file_priv=...path...` 와 같이 변경할 수 있다.
{{ site.content.br_small }}
```bash
$ mysqld --initialize --user=dhkim
2022-05-31T00:27:32.156756Z 0 [System] [MY-013169] [Server] /usr/ssw/mysql/bin/mysqld (mysqld 8.0.29) initializing of server in progress as process 2378
2022-05-31T00:27:32.157288Z 0 [Warning] [MY-013242] [Server] --character-set-server: 'utf8' is currently an alias for the character set UTF8MB3, but will be an alias for UTF8MB4 in a future release. Please consider using UTF8MB4 in order to be unambiguous.
2022-05-31T00:27:32.157292Z 0 [Warning] [MY-013244] [Server] --collation-server: 'utf8_general_ci' is a collation of the deprecated character set UTF8MB3. Please consider using UTF8MB4 with an appropriate collation instead.
2022-05-31T00:27:32.223269Z 1 [System] [MY-013576] [InnoDB] InnoDB initialization has started.
2022-05-31T00:27:33.031946Z 1 [System] [MY-013577] [InnoDB] InnoDB initialization has ended.
2022-05-31T00:27:33.779099Z 6 [Note] [MY-010454] [Server] A temporary password is generated for root@localhost: SP12Kr.a7K*_
```

> A temporary password is generated for root@localhost: SP12Kr.a7K*_
{{ site.content.br_small }}
위 작업을 다시 수행하려면, `-DMYSQL_DATADIR` 모든 파일을 삭제해야 한다.
{{ site.content.br_small }}
## 5.2 패스워드 정책 변경

아래 단계에서 root로 로그인 시에 위에서 확인된 임시 패스워드를 입력하면 root 패스워드를 변경 할 수 있다.

이후 해당 포스팅을 참고할 때, 소스 컴파일 설치가 아니라 다른 형태의 설치를 하고 패스워드 부분에서 애로 사항을 겪을 경우를 위하여

작성한다.
{{ site.content.br_small }}
임시 패스워드로 로그인 후 패스워드 정책 확인

```mysql
$ mysql -u root -p
mysql> SHOW VARIABLES LIKE 'validate_password%';
+--------------------------------------+--------+
| Variable_name                        | Value  |
+--------------------------------------+--------+
| validate_password_check_user_name    | ON     |
| validate_password_dictionary_file    |        |
| validate_password_length             | 8      |
| validate_password_mixed_case_count   | 1      |
| validate_password_number_count       | 1      |
| validate_password_policy             | MEDIUM |
| validate_password_special_char_count | 1      |
+--------------------------------------+--------+
```

> 결과가 위와 유사하게 출력된다.
{{ site.content.br_small }}
/etc/my.cnf 에 옵션을 추가하고 재기동한다.

```
# vi /etc/my.cnf
validate_password.policy=LOW
default_password_lifetime=0
validate_password.length=3
validate_password.special_char_count=0
validate_password.mixed_case_count=0
validate_password.number_count=0
```
{{ site.content.br_small }}
패스워드 정책이 변경되었다.

```mysql
mysql> SHOW VARIABLES LIKE 'validate_password%';
+--------------------------------------+-------+
| Variable_name                        | Value |
+--------------------------------------+-------+
| validate_password.check_user_name    | ON    |
| validate_password.dictionary_file    |       |
| validate_password.length             | 3     |
| validate_password.mixed_case_count   | 0     |
| validate_password.number_count       | 0     |
| validate_password.policy             | LOW   |
| validate_password.special_char_count | 0     |
+--------------------------------------+-------+
```
{{ site.content.br_small }}
패스워드 정책에서 길이제한만 '3' 로 있고, 모두 풀렸다.

```mysql
mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';
ERROR 1819 (HY000): Your password does not satisfy the current policy requirements

mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY 'root1';
Query OK, 0 rows affected (0.06 sec)
```

> 패스워드 길이 정책이 동작하지 않은 듯하지만.. 원인을 구글링으로 찾을 수 없었다.
{{ site.content.br_big }}
# 6. 실행 및 종료

### 6.1 실행

초기 실행 후, 프로세스 확인 결과.

```bash
$ mysqld_safe --user=dhkim &
$ ps -ef | grep mysqld | grep -v grep
dhkim       2477    1727  0 09:33 pts/0    00:00:00 /bin/sh bin/mysqld_safe --user=dhkim
dhkim       2565    2477  0 09:33 pts/0    00:00:01 /usr/ssw/mysql/bin/mysqld --basedir=/usr/ssw/mysql --datadir=/logs/mysql --plugin-dir=/usr/ssw/mysql/lib/plugin --log-error=dhkim.err --pid-file=dhkim.pid
```
{{ site.content.br_small }}
초기 로그인에는, `5.1 데이터 디렉토리 초기화` 시에 생성된 임시 패스워드(`SP12Kr.a7K*_`)로 로그인하고 앞으로 사용할 패스워드로 변경해야 한다.

```bash
$ mysql -u root -p
Enter password: (SP12Kr.a7K*_)

mysql> ALTER USER 'root'@'localhost' IDENTIFIED BY 'root';
Query OK, 0 rows affected (0.01 sec)

mysql> quit;
```
{{ site.content.br_small }}
패스워드는 프롬프트로 입력하고, version 확인하는 예시.

```bash
$ mysqladmin -u root -p version
Enter password: (root)
mysqladmin  Ver 8.0.29 for Linux on x86_64 (Source distribution)
Copyright (c) 2000, 2022, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Server version          8.0.29
Protocol version        10
Connection              Localhost via UNIX socket
UNIX socket             /tmp/mysql.sock
Uptime:                 1 min 12 sec

Threads: 2  Questions: 5  Slow queries: 0  Opens: 117  Flush tables: 3  Open tables: 36  Queries per second avg: 0.069
```
{{ site.content.br_big }}
## 6.2 종료

```bash
$ mysqladmin -u root -p shutdown
Enter password: (root)
2022-05-31T00:49:47.300509Z mysqld_safe mysqld from pid file /logs/mysql/dhkim.pid ended
[1]+  Done                    bin/mysqld_safe --user=dhkim
```
{{ site.content.br_small }}
# 7. 참고 문헌

[지원 플랫폼](https://www.mysql.com/support/supportedplatforms/database.html)

[사전 필요사항](https://dev.mysql.com/doc/refman/8.0/en/source-installation-prerequisites.html)

[설치 시 옵션 구성](https://dev.mysql.com/doc/refman/8.0/en/source-configuration-options.html)

[데이터 디렉토리 초기화](https://dev.mysql.com/doc/refman/8.0/en/data-directory-initialization.html)

[서버 시작](https://dev.mysql.com/doc/refman/8.0/en/starting-server.html)

[패스워드 초기화](https://dev.mysql.com/doc/refman/8.0/en/default-privileges.html)

[서버 종료 등등 서버 테스팅 명령어](https://dev.mysql.com/doc/refman/8.0/en/testing-server.html)

