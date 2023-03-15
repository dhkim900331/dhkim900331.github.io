---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[Middleware/WebLogic] 아이디, 비밀번호 변경하기"
tags: [Middleware, WebLogic, Change, ID, PWD, boot.properties]
typora-root-url: ..
---

# 1. 개요

WLS 8 이상에서 ID/PWD 변경 방법 가이드




# 2. 설명

## 2.1 WebLogic 8

(1). 모든 인스턴스 종료

(2). 도메인/각각 서버/ldap 디렉토리 삭제

(3). boot.properties 삭제

(4). `call setEnv.cmd`

(5). `java weblogic.security.utils.AdminAccout <변경할 아이디> <변경할 비밀번호> .`

> 맨 뒤에 dot(.) 필요

(6). 서버 재시작

> "(5)"번 항목을 실행하면 도메인/DefaultAuthenticatormyrealmInit이 생성되고, 서버 재시작 할 때 이 파일을 참조로 각각 서버/ldap 디렉토리가 재 생성된다.

(7). boot.properties 생성 후 적용



[참고 사이트](http://peoplesoft.ittoolbox.com/groups/technical-functional/peopletools-l/weblogic-81-administrator-password-reset-2765106)

* 콘솔에서 비밀번호 변경은 `콘솔 - Realm` 메뉴 이용하면 된다.



## 2.2 WebLogic 9 <=

(1). 모든 인스턴스 종료

(2). `cd <도메인>/bin`

(3). `. ./setDomainEnv.sh`

> 맨 앞에 dot(.) 필요

(4). `cd <도메인>/servers`

(5). `rm -rf 명령으로 인스턴스 디렉토리 모두 삭제`

(6). `cd <도메인>`

(7). `rm ./boot.properties`

> boot.properties 가 외부의 경로로 설정되어 사용한다는 가정

(8). `vi ./boot.properties`

```
username=밑에서 변경될 아이디
password=밑에서 변경될 패스워드
```

(9). cd <도메인>/security

(10). `mv ./DefaultAuthenticatorInit.ldift ./DefaultAuthenticatorInit.ldift_backup`

(11). `java weblogic.security.utils.AdminAccount <변경될 아이디> <변경될 패스워드> .

> 맨 뒤에 dot(.) 필요

(12). 인스턴스 모두 기동
