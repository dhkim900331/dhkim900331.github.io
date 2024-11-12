---
date: 2024-10-30 14:46:10 +0900
layout: post
title: "[WebLogic/SAML] How to use expired certificate with SAML"
tags: [Middleware, WebLogic, ]
typora-root-url: ..
---

# 1. Overview

WebLogic 12cR2 에서 SSO Server에 참여하기 위해 Service Provider로 SAML 2.0 Service를 구성한다.

만료된 인증서를 사용해도 되는가?


<br><br>


# 2. Descriptions

기본적으로 만료된 인증서를 쓰는 것은, 보안 취약점을 야기한다.

Client와 Server간의 주고 받는 Data는 여전히 Encrypt 되지만 그럼에도 만료된 인증서를 쓰는 것은,

노후화된 Algorithm을 쓰는 것과 같고, [Identity Provider](https://en.wikipedia.org/wiki/Identity_provider_(SAML)) 의 보안 정책에 위반 될 수 있다.

<br>

만료된 인증서를 사용하기 위해서는, Identity Provider로 동작하는 SSO Server Manager의 Confirm이 필요하다.

WebLogic에서는 SAML 2.0 Service를 사용할 때, 만료된 인증서를 사용하기 위해서는 다음의 Option을 제공하고 있다.

```sh
-Dcom.bea.common.security.saml2.allowExpiredCerts=true
```

> com.bea.common.security.saml2.allowExpiredCerts은 [WebLogic Server 12.2.1.3.0 (Patch Set 3)에서 추가된 SAML Update 사항](https://docs.oracle.com/middleware/12213/wls/NOTES/whatsnew.htm#GUID-5963C8BA-0F93-45C2-9FD2-6BB09B261F44) 입니다.


> - In this release of WebLogic Server, the SAML 2.0 implementation no longer uses certificates that are expired or not yet valid in SAML signing. To allow use of these certificates, set the Java system property com.bea.common.security.saml2.allowExpiredCerts to true. For example, specify the following option in the Java command that starts WebLogic Server:
> 
>   `-Dcom.bea.common.security.saml2.allowExpiredCerts=true`


<br><br>


# 3. References

**WebLogic을 SAML 2.0 Service Provider로 구성 할 때, 만료된 인증서를 사용하는 방법 (Doc ID 3049995.1)**

https://en.wikipedia.org/wiki/Identity_provider_(SAML)

https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/secmg/saml20.html#GUID-C541F7EB-1833-4500-8269-5ADB91E6BB6E
