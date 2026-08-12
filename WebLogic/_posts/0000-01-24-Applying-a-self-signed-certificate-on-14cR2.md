---
date: 2026-02-23 13:44:32 +0900
layout: post
title: "[WebLogic/TLS/SSL] Applying a self-signed certificate on 14cR2"
tags: [Middleware, WebLogic, TLS, SSL, Certificate]
typora-root-url: ../..
---

# 1. Overview

14.1.2 (JDK 17+) 기준에서 Self-signed 적용 방법에 대한 스크립트 정리.

<br>

<br><br>


# 2. Descriptions

Self-signed 생성 방법은 'How-to-make-a-self-signed-certificate' 게시물을 참고하여 PKCS12 로 준비하면 된다.
Admin Console에서 `keystore.p12`와 `trust.p12` 적용은 별달리 설명할 것이 없다.
이후 Admin Server나 Managed Server 접근을 위한 trust store 적용은 다음과 같이 설정하면 된다.

```sh
# stopA_ssl.sh 예시
...
WLST_PROPERTIES="${WLST_PROPERTIES} -Dweblogic.security.SSL.ignoreHostnameVerification=true"
WLST_PROPERTIES="${WLST_PROPERTIES} -Dweblogic.security.TrustKeyStore=CustomTrust"
WLST_PROPERTIES="${WLST_PROPERTIES} -Dweblogic.security.CustomTrustKeyStoreFileName=/tmp/ssl/keystore/trust.p12"
WLST_PROPERTIES="${WLST_PROPERTIES} -Dweblogic.security.CustomTrustKeyStoreType=PKCS12"
WLST_PROPERTIES="${WLST_PROPERTIES} -Dweblogic.security.CustomTrustKeyStorePassPhrase=samepwd_is_recommended"

java ${WLST_PROPERTIES} weblogic.WLST << INNER_EOF
connect(url='t3s://${SERVER_ADDR}:${SERVER_PORT}')
shutdown(force='true')
exit()
INNER_EOF
```


# 3. References

https://docs.oracle.com/en/middleware/fusion-middleware/14.1.2/wlstg/wlst_faq.html#GUID-012AD767-09E5-445F-96E7-64B08B5CC2A6
	"java -Dweblogic.security.SSL.ignoreHostnameVerification=true -Dweblogic.security.TrustKeyStore=DemoTrust weblogic.WLST"
	
	
Stopping Admin/Managed Server from Command Line in a Secure Production Mode Fails with the Error "java.security.InvalidAlgorithmParameterException" and "trustAnchors parameter must be non-empty" (Doc ID 3065439.1)	


The SSL Communication Between Node Manager and Admin Server is Failing When Self Signed Certificate is Configured (Doc ID 2689785.1)	

