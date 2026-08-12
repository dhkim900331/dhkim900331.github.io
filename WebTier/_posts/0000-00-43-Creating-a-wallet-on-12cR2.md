---
date: 2025-08-29 12:22:37 +0900

layout: post
title: "[WebTier/OHS] Creating a wallet on 12cR2"
tags: [WebTier, OHS, Wallet, SSL, Certificate]
typora-root-url: ../..
---

# 1. Overview

OHS 12cR2 에 Wallet 생성 템플릿

<br><br>


# 2. Descriptions

```sh
# 기본 변수
export ORACLE_HOME=/sw/webtier/12cR2
export PATH=$ORACLE_HOME/oracle_common/bin:$PATH
export JAVA_HOME=/sw/jdk/jdk1.8.0_421

# 인증서 변수
KEYSTOREPATH=/sw/webtier/12cR2/domains/saml_domain/mykeystore
KEYSTOREFILE=keystore.jks
KEYPASS=keypass
STOREPASS=storepass

# RSA 인증서 생성
mkdir ${KEYSTOREPATH}
cd ${KEYSTOREPATH}
keytool -genkeypair -alias key-RSA -keyalg RSA -keysize 2048 -sigalg SHA256withRSA -keypass ${KEYPASS} -keystore ${KEYSTOREPATH}/${KEYSTOREFILE} -storepass ${STOREPASS} -validity 365 -dname "CN=CommonName, OU=OrgUnit, O=Org, L=City, ST=State, C=CountryCode"
keytool -export -alias key-RSA -file ${KEYSTOREPATH}/rsa_cert.cer -keystore ${KEYSTOREPATH}/${KEYSTOREFILE} -storepass ${STOREPASS} -noprompt
keytool -import -alias key-RSA -file ${KEYSTOREPATH}/rsa_cert.cer -keystore ${KEYSTOREPATH}/trust.jks -storepass ${STOREPASS} -noprompt

# 필요시 PKCS12 형식으로 변환 (keypass 직접 입력)
keytool -importkeystore -srckeystore ${KEYSTOREPATH}/${KEYSTOREFILE} -srcstorepass ${STOREPASS} -destkeystore ${KEYSTOREPATH}/${KEYSTOREFILE}.p12 -destkeypass ${KEYPASS} -deststorepass ${STOREPASS} -deststoretype PKCS12



# WALLET 변수
WALLETPATH=/sw/webtier/12cR2/domains/saml_domain/mywallet
WALLETPASS=weblogic1

# WALLET 생성
mkdir ${WALLETPATH}
cd ${WALLETPATH}
${ORACLE_HOME}/oracle_common/bin/orapki wallet create -wallet ${WALLETPATH} -auto_login -pwd ${WALLETPASS}

# PKCS12 -> WALLET
${ORACLE_HOME}/oracle_common/bin/orapki wallet import_pkcs12 -wallet ${WALLETPATH} -pwd ${WALLETPASS} -pkcs12file ${KEYSTOREPATH}/${KEYSTOREFILE}.p12 -pkcs12pwd storepass
```

<br><br>


# 3. References

https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/12.2.1.4/administer-ohs/getstart.html#GUID-C811E333-EC96-44B9-820B-7EAADBEC62BB__SECTION_A33_M34_CJB

https://dhkim900331.github.io/ssl/How-to-make-a-self-signed-certificate
