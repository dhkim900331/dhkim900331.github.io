---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] OCI Datasource 생성"
tags: [Middleware, WebLogic, OCI, Datasource]
typora-root-url: ..
---


# 1. Overview

OCI(Oracle Call Interface)

SQL*Plus, SQL*Developer와 같은 oracle db 접속 툴이 oci 임.

oci는 native library를 사용하므로, pure java인 thin 방식보다 더 빠르다고 한다.

support.oracle에 oci 사용 시 weblogic jvm crash, not closed 사례와 같은 문서 혹은 패치 내용이 있으며, thin 방식 사용하는 것을 권장한다고 설명한다.

> WLS JDBC Pool - Physical Connections are not closed by Weblogic JDBC Datasource using OCI driver (Doc ID 1928018.1)
>
> WebLogic Server Crash Observed When Using Oracle OCI JDBC Driver (Doc ID 889840.1)


<br><br>


# 2. Descriptions

## 2.1 OCI 를 사용하는 Datasource 생성 방법.

### (1). OCI Library installation

WebLogic 이 설치된 OS에 OCI가 설치되어 있어야 한다.

OCI가 설치되어야 필요한 native library가 설치되며, LD_LIBRARY_PATH와 같은 os 환경 변수에 oci library path가 설정되기 때문이다.

OCI 는 담당자가 사용하는 tool이므로 담당자가 미리 설치를 반드시 해놓아야 하며, 설치를 하지 않은 os의 경우 oci library 파일을 받아 ftp upload 해놓아야 한다.

<br>

[여기](http://www.oracle.com/technetwork/database/features/instant-client/index-097480.html) 에서 oci lib을 다운로드 받는다.

>  예) instantclient-basic-linux.x64-11.2.0.4.0.zip 을 /home/weblogic/was/1213/domains/lib/instantclient_11_2 압축 해제

<br>

여기서는, OCI가 설치되어 있지 않은 서버에 oci library만으로 oci datasource 구성 방법을 설명한다.

<br>

### (2). setup instance

* AdminServer와 OCI를 사용할 ManagedServer 모두 적용한다.

```sh
...skip...

export LD_LIBRARY_PATH="/home/weblogic/was/1213/domains/lib/instantclient_11_2:${LD_LIBRARY_PTH}"

export JAVA_OPTIONS="-Djava.library.path=/home/weblogic/was/1213/domains/lib/instantclient_11_2 ${JAVA_OPTIONS}"

...skip...
```


* 위에서 받은 oci는 11g이므로, ojdbc driver도 11g이어야 한다.

  `/home/weblogic/was/1213/domains/lib/instantclient_11_2/ojdbc6.jar 를 domains/lib 에 복사해둔다.`

<br>

### (3). datasource url

* JDBC 생성 시 connect url은 oci 라는 글자만 들어가고 나머지는 thin 과 모두 동일하다.
  * `jdbc:oracle:oci:host:port:sid `

<br>

### (4). 설정 시 에러가 발생한다면

* 적용하려는 oci 버전과 ojdbc 버전이 동일한지 확인한다. (oci version 11g이면 ojdbc 도 11g이어야 한다. oci library 디렉토리의 ojdbc.jar 를 사용한다면 해결되는 문제)

* LD_LI....와 Djava.lib... 옵션 적용 여부를 확인한다.

* 주로 발생하는 에러와 가이드에 대한 문서는

  > java.lang.UnsatisfiedLinkError: no ocijdbc11 in java.library.path with WebLogic 12c (Doc ID 1914466.1)
  >
  > How To Configure JDBC OCI In Weblogic?(Doc ID 1917164.1)
