---
date: 2024-05-02 14:41:32 +0900
layout: post
title: "[WebTier/OHS] Nzos Call NzosSetCredential Returned 28791"
tags: [WebTier, OHS, NZOS, Certificate, SSL, Expired]
typora-root-url: ..
---

# 1. Overview
Oracle HTTP Server 12cR2 기준으로 OHS Component가 기동이 되지 않으며,

`Nzos Call NzosSetCredential Returned 28791` Error를 기록한다.

{{ site.content.br_big }}


# 2. Descriptions
OHS Component Runtime Directory 하위 `keystores/default` 에는 Wallet 이 구성되어 있다.

```sh
$ ls ${DOMAIN_HOME}/config/fmwconfig/components/OHS/instances/<WORKER>/keystores/default
cwallet.sso  cwallet.sso.lck
```
{{ site.content.br_small }}
해당 Wallet 은 OHS 기본 구성으로 제공되는 Demo Certificate 이며,

사용자의 HTTPS Service 에서도 사용할 수 있겠지만, (`ssl.conf`)

NodeManager와 Component의 communication 으로도 사용 된다. (`admin.conf`)

>  참고 [Configuring SSL for Admin Port](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/12.2.1.4/administer-ohs/getstart.html#GUID-24E159D9-E7E3-43B5-A4B6-0B29D2B00020)
{{ site.content.br_small }}
다음 명령으로 Wallet Certificate의 Expired date를 확인할 수 있다.

```sh
export ORACLE_HOME=<ORACLE HOME>
export DOMAIN_HOME=<DOMAIN HOME>

$ cd ${DOMAIN_HOME}/config/fmwconfig/components/OHS/instances/<WORKER>/keystores/default
$ ${ORACLE_HOME}/oracle_common/bin/orapki wallet display -wallet .

(Wallet에 포함된 Certificate 출력 log)
Oracle PKI Tool : Version 12.2.1.4.0
Copyright (c) 2004, 2019, Oracle and/or its affiliates. All rights reserved.

Requested Certificates:
User Certificates:
Subject:        CN=localhost,OU=FOR TESTING ONLY,O=FOR TESTING ONLY
Trusted Certificates:
Subject:        CN=localhost,OU=FOR TESTING ONLY,O=FOR TESTING ONLY


$ ${ORACLE_HOME}/oracle_common/bin/orapki wallet export -wallet . -dn 'CN=localhost,OU=FOR TESTING ONLY,O=FOR TESTING ONLY' -cert server.cer

(Wallet에서 Certificate 추출)
Oracle PKI Tool : Version 12.2.1.4.0
Copyright (c) 2004, 2019, Oracle and/or its affiliates. All rights reserved.

Operation is successfully completed.


$ openssl x509 -in server.cer -noout -text
Certificate:
    Data:
        Version: 1 (0x0)
        Serial Number: 0 (0x0)
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: O = FOR TESTING ONLY, OU = FOR TESTING ONLY, CN = localhost
        Validity
            Not Before: Feb 27 08:18:17 2024 GMT
            Not After : Feb 25 08:18:17 2029 GMT
...

```
{{ site.content.br_small }}
추출한 Certificate는 29년에 Expired 된다.

Domain 생성 기준 5년 뒤 Expired 된다.
{{ site.content.br_small }}
Wallet SSL Certificate 가 Expired 되면 Component와 NodeManager가 HTTPS 통신 시 실패하여 OHS Startup 실패하면서 `Nzos Call NzosSetCredential Returned 28791` Error 가 발생할 수 있다.
{{ site.content.br_small }}
이 Expired date를 다시 늘려주기 위해 Wallet을 재생성 해야 한다.

> 참고 12c: How to Recreate the Default Wallet that has Expired from Oracle HTTP Server (Doc ID 2729766.1)

{{ site.content.br_big }}


# 3. References

**How Does Oracle HTTP Server 12c Staging and Runtime Configuration Files Affect OHS Configuration Changes (Doc ID 2335871.1)**

**12c: How to Recreate the Default Wallet that has Expired from Oracle HTTP Server (Doc ID 2729766.1)**

**Oracle HTTP Server Start Failed with "Nzos Call NzosSetCredential Returned 28791" Due to Expired SSL Certificate (Doc ID 2314626.1)**
