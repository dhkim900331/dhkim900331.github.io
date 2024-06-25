---
date: 2024-06-25 16:09:26 +0900
layout: post
title: "[SSL/Certificate] How to make a self-signed certificate?"
tags: [SSL, Certificate]
typora-root-url: ..
---

# 1. Overview

JAVA SSL 테스트를 위해 수없이 생성하는 self-signed certificate의 생성 방법에 대한 간략한 정리

여기서는 JDK 1.8 기준에서 사용 가능한 RSA 와 ECDSA cipher suite를 가정한다.
{{ site.content.br_big }}
# 2. Descriptions

```sh
# JAVA 환경변수
export PATH=/sw/jdk/jdk1.8.0_381/bin:${PATH}

# 인증서 변수
KEYSTOREPATH=/tmp/ssl/keystore
KEYSTOREFILE=keystore.jks
KEYPASS=keypass
STOREPASS=storepass

# RSA 인증서 생성
keytool -genkeypair -alias key-RSA -keyalg RSA -keysize 2048 -sigalg SHA256withRSA -keypass ${KEYPASS} -keystore ${KEYSTOREPATH}/${KEYSTOREFILE} -storepass ${STOREPASS} -validity 365 -dname "CN=CommonName, OU=OrgUnit, O=Org, L=City, ST=State, C=CountryCode"
keytool -export -alias key-RSA -file ${KEYSTOREPATH}/rsa_cert.cer -keystore ${KEYSTOREPATH}/${KEYSTOREFILE} -storepass ${STOREPASS} -noprompt
keytool -import -alias key-RSA -file ${KEYSTOREPATH}/rsa_cert.cer -keystore ${KEYSTOREPATH}/trust.jks -storepass ${STOREPASS} -noprompt

# ECDSA 인증서 생성
keytool -genkeypair -alias key-EC -keyalg EC -keysize 256 -sigalg SHA256withECDSA -keypass ${KEYPASS} -keystore ${KEYSTOREPATH}/${KEYSTOREFILE} -storepass ${STOREPASS} -validity 365 -dname "CN=CommonName, OU=OrgUnit, O=Org, L=City, ST=State, C=CountryCode"
keytool -export -alias key-EC -file ${KEYSTOREPATH}/ec_cert.cer -keystore ${KEYSTOREPATH}/${KEYSTOREFILE} -storepass ${STOREPASS} -noprompt
keytool -import -alias key-EC -file ${KEYSTOREPATH}/ec_cert.cer -keystore ${KEYSTOREPATH}/trust.jks -storepass ${STOREPASS} -noprompt

# 필요시 PKCS12 형식으로 변환
keytool -importkeystore -srckeystore ${KEYSTOREPATH}/${KEYSTOREFILE} -destkeystore ${KEYSTOREPATH}/${KEYSTOREFILE}.p12 -deststoretype PKCS12 -srcstorepass ${STOREPASS} -deststorepass ${STOREPASS}

# 인증서 파일 확인
keytool -list -v -keystore ${KEYSTOREPATH}/${KEYSTOREFILE} -storepass ${STOREPASS}
keytool -list -v -keystore ${KEYSTOREPATH}/${KEYSTOREFILE}.p12 -storetype PKCS12 -storepass ${STOREPASS}
```

