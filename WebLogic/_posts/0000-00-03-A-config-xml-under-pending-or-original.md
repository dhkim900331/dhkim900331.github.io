---
date: 2024-06-25 16:09:26 +0900
layout: post
title: "[WebLogic] A config.xml under pending or original directory"
tags: [Middleware, WebLogic, backup, archive, original, pending]
typora-root-url: ..
---

# 1. Overview
DOMAIN_HOME 아래 original/pending 디렉터리에 생성되는 config.xml 의 용도를 설명한다.

추가로 config.xml의 archiving 도 간략 설명한다.


<br><br>


# 2. Descriptions

## 2.1 original/config.xml

* original directory는 공식 메뉴얼에 소개되어 있지 않기 때문에 일련의 테스트를 통해 확인된다.
* Admin console 에서 편집 모드를 활성화 하면 `DOMAIN_HOME/original/config.xml` 생성된다.
* 재차 편집 모드로 들어설 때마다, overwrite 한다.
* AdminServer 재시작으로 기동이 완료되면 삭제된다.
* 해당 파일은, 공식 자료로 기술되어 있지 않지만 내부 로직에 의해 사용되는 임시 파일로 보여진다.
* 편집 모드가 활성화 되어 있는 상태에서 재시작을 하면, Console login 시점에 다시 생성된다.


<br><br>


## 2.2 pending/config.xml

* 설정을 수정하면 반영 전에 생성되는 임시 파일이다.
* `2.1 original/config.xml` 마지막 설명에, 재시작 이후 Console login 시점에 다시 생성된다고 하였는데, `pending/config.xml`이 있다면 두 파일이 동기화 된다.


<br><br>


### 2.3 config.xml의 archiving

[Configuration File Archiving](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/domcf/config_files.html#GUID-43B51552-2AFB-4B17-A95E-D502B2C42EA0)
