---
date: 2026-07-03 18:06:17 +0900
layout: post
title: "[WebLogic] How To Encrypt CustomTrustKeyStorePassPhrase"
tags: [Middleware, WebLogic, Encrypt]
typora-root-url: ..
---

# 1. Overview

SSL Certification을 등록 및 사용하는 WebLogic Instance의 Script 내부에서 Certification PassPhrase Text를 암호화 하는 방법

<br><br>


# 2. Descriptions

PKCS12 Type의 Trust 인증서를 등록하는 환경을 가정하여 설명한다.

TrustKeyStore의 PassPhrase를 암호화 하기 위해서는

Using the weblogic.security.Encrypt or WLST encrypt() Utility to Replace Clear Text Password with an Encrypted Value KB115577 문서를 통해

Plain Text를 암호화 한다.

```sh
$ cd $DOMAIN_HOME
$ . ./bin/setDomainEnv.sh
$ java weblogic.security.Encrypt
    Password: <암호 입력>
```

<br>

출력되는 encrypted string을 `-Dweblogic.security.CustomTrustKeyStorePassPhrase` 인자에서 사용한다.

```sh
-Dweblogic.security.TrustKeyStore=CustomTrust
-Dweblogic.security.CustomTrustKeyStoreFileName=/path/to/trust.p12
-Dweblogic.security.CustomTrustKeyStorePassPhrase={AES256}fKhbArlN...oBk/vR3
-Dweblogic.security.CustomTrustKeyStoreType=PKCS12
```

<br>

# 3. References

Using the weblogic.security.Encrypt or WLST encrypt() Utility to Replace Clear Text Password with an Encrypted Value KB115577

CustomTrustKeyStorePassPhrase 를 암호화 하는 방법 KB916676
