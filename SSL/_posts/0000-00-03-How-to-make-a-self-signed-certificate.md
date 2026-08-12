---
date: 2024-06-25 16:09:26 +0900
layout: post
title: "[SSL/Certificate] How to make a self-signed certificate?"
tags: [SSL, Certificate]
typora-root-url: ../..
---

# 1. Overview

JAVA SSL 테스트를 위해 수없이 생성하는 self-signed certificate의 생성 방법에 대한 간략한 정리

여기서는 WebLogic 14.1.2 (JDK 17) 이상 기준에서 사용 가능한 RSA 와 ECDSA cipher suite를 가정한다.


<br><br>


# 2. Descriptions

```sh
# JAVA 환경변수
export PATH=/sw/jdk/jdk-17.0.14/bin:${PATH}

# 인증서 변수
KEYSTOREPATH=/tmp/ssl/keystore
KEYSTOREFILE=keystore.p12
TRUSTSTOREFILE=trust.p12
KEYPASS=samepwd_is_recommended
STOREPASS=samepwd_is_recommended

# RSA 인증서 생성
keytool -genkeypair -alias key-RSA -keyalg RSA -keysize 2048 -sigalg SHA256withRSA -keypass ${KEYPASS} -keystore ${KEYSTOREPATH}/${KEYSTOREFILE} -storepass ${STOREPASS} -storetype PKCS12 -validity 365 -dname "CN=CommonName, OU=OrgUnit, O=Org, L=City, ST=State, C=CountryCode"
keytool -export -alias key-RSA -file ${KEYSTOREPATH}/rsa_cert.cer -keystore ${KEYSTOREPATH}/${KEYSTOREFILE} -storepass ${STOREPASS} -storetype PKCS12 -noprompt
keytool -import -alias key-RSA -file ${KEYSTOREPATH}/rsa_cert.cer -keystore ${KEYSTOREPATH}/${TRUSTSTOREFILE} -storepass ${STOREPASS} -storetype PKCS12 -noprompt


# 인증서 파일 확인
keytool -list -v -keystore ${KEYSTOREPATH}/${KEYSTOREFILE} -storepass ${STOREPASS}
keytool -list -v -keystore ${KEYSTOREPATH}/${TRUSTSTOREFILE} -storepass ${STOREPASS}
```

<br>

> WLS 14.1.2 (JDK 17) 에서 KEYPASS와 STOREPASS가 다르면 인증서 로딩 에러가 발생하여, 동일하게 맞춘다. 또한 JKS 보다 PKCS12 가 권장된다.
