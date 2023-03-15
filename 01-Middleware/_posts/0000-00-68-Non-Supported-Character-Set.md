---
date: 2023-03-16 08:54:50 +0900
layout: post
title: "[Middleware/JDBC] Non supported character set"
tags: [Middleware, Driver, JDBC, OJDBC]
typora-root-url: ..
---

# 1. 개요

Non supported character set (add orai18n.jar in your classpath) 에러가 발생할 시 대처 가이드



# 2. 설명

[Globalization Support](https://docs.oracle.com/en/database/oracle/oracle-database/21/jjdbc/globalization-support.html#GUID-CE02B998-DD6A-46FC-8ECF-AD2413F09A97) 문서를 보면, 기본 Char set 외에 다른 세계언어를 사용하기 위해서 orai18n 파일이 필요하다고 설명 한다.

문서의 "Compressing orai18n.jar" 가이드를 확인하여 원하는 Char set만 추출하여 사용할 수 있다.

orai18n.jar 를 그대로 사용하기에는 무겁기 때문에 그렇다.



[OJDBC Download](https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html ) 에서 'Companion Jars' 를 받으면 orai18 파일이 포함되어 있다.



```sh
$ tar -xzf ojdbc8-full.tar.gz
$ cd ojdbc8-full/
$ java -jar orai18n.jar -custom-charsets-jar custom_orai18n_ko16ksc5601.jar -charset ko16ksc5601
Added       Character set : KO16KSC5601

$ ls -al custom_orai18n_ko16ksc5601.jar
-rw-rw-r-- 1 wasadm wasadm 62561 Mar 15 11:09 custom_orai18n_ko16ksc5601.jar
```

