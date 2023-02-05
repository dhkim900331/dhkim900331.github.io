---
date: 2022-02-15 12:26:08 +0900
layout: post
title: "[JBoss] EAP Patch 명령어"
tags: [WAS, JBoss]
typora-root-url: ..
---


# 1. 개요

JBOSS EAP 대상으로, Patch 명령어 가이드

> 상위 patch는 하위 patch를 모두 포함한다.
>
> 7.3.10 , 7(major), 3(minor), 10(micro release) 를 의미한다.



# 2. Patch 구문별 명령어 설명

## 2.1 patch apply

```bash
./jboss-cli.sh "patch apply /tmp/jboss-eap-7.3.10-patch.zip"
```



## 2.1 patch info

```bash
./jboss-cli.sh "patch info"
Version:             7.3.10.GA
Cumulative patch ID: jboss-eap-7.3.10.CP
One-off patches:     none
```

[여기 참고](https://access.redhat.com/solutions/64981)
