---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] DataSource Password 변경"
tags: [Middleware, WebLogic, Datasource]
typora-root-url: ..
---

<br># 1. 개요

DataSource Password 변경

<br>
# 2. 설명

웹로직 마이그레이션이나.. 업그레이드 등을 진행할때, 데이터소스(jdbc.xml)등의 패스워드는 직접 다시 수정해야 한다.

또는 패스워드 변경 시 콘솔을 이용하기 보다 직접 config/jdbc/.xml 을 수정하는 편이 편리하다.

<br>
다음 명령어는 $DOMAIN_HOME 에서만 실행된다. (setDomainEnv.sh가 제일속편함)

```sh
. ./$DOMAIN_HOME/bin/setDomainEnv.sh
java weblogic.security.Encrypt {암호입력} 또는 java -cp weblogic.jar weblogic.security.Encrypt {암호입력}
```

