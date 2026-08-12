---
date: 2026-07-03 18:06:17 +0900
layout: post
title: "[WebLogic/SSL] SSLWLSWildcardHostnameVerifier가 적용 되지 않음"
tags: [Middleware, WebLogic, SSL, Certificate]
typora-root-url: ../..
---

# 1. Overview

WebLogic Server가 외부 HTTPS를 호출하는 SSL Client로써 동작합니다.

Wildcard CN 또는 SAN Field가 속해 있는 Certificate를 처리하지 못하는 에러가 발생합니다.

```
<Warning> <Security> <BEA-090504> <Certificate chain received from a.test.co.kr - 1.2.3.4 failed hostname verification check. Certificate contained *.test.co.kr but check expected a.test.co.kr> 

...

javax.net.ssl.SSLKeyException: Hostname verification failed: HostnameVerifier=weblogic.security.utils.SSLWLSHostnameVerifier, hostname=a.test.co.kr.
    at weblogic.security.SSL.jsseadapter.JaSSLEngine.doPostHandshake(JaSSLEngine.java:686)
    at weblogic.security.SSL.jsseadapter.JaSSLEngine.doAction(JaSSLEngine.java:757)
    at weblogic.security.SSL.jsseadapter.JaSSLEngine.wrap(JaSSLEngine.java:67)
    at weblogic.socket.JSSEFilterImpl.wrapAndWrite(JSSEFilterImpl.java:771)
    at weblogic.socket.JSSEFilterImpl.doHandshake(JSSEFilterImpl.java:119)
    at weblogic.socket.JSSEFilterImpl.doHandshake(JSSEFilterImpl.java:87)
```

<br><br>


# 2. Descriptions

해결책으로 두 가지 옵션을 사용할 수 있습니다.

<br>

**(1) weblogic.security.SSL.ignoreHostnameVerification**

A Man-in-the-Middle (MitM) attack (중간자 공격) 을 방어하지 못하므로 보안상 운영 서비스에서는 사용하지 않아야 합니다.

Hostname을 검증하지 않으므로 발생하는 에러를 무시할 수 있습니다.

[Disable host name verification 방법](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/wlach/taskhelp/security/DisableHostNameVerification.html)

<br>

**(2) weblogic.security.utils.SSLWLSWildcardHostnameVerifier class 사용**

WebLogic은 인증서의 CN/SAN Field 에서 Wildcard Hostname을 읽고 처리 할 수 있습니다.

[Using Host Name Verification 참고](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/secmg/hostname_verifier.html)

<br>

Wildcard Hostname 을 처리하기 위해서는 weblogic.security.SSL.HostnameVerifier interface에 해당 classname을 지정해야 합니다.

[Configure a custom host name verifier 참고](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/wlach/taskhelp/security/ConfigureACustomHostNameVerifier.html)

<br>

SSLWLSWildcardHostnameVerifier class는 WebLogic Server 사용 시, Admin Console을 통해 MBean에 등록해야 적용됩니다.

Setting To Use SSL Wildcard Hostname Verifier Fails When Using Startup Argument (KB544191) 참고

<br>

또한, 다음과 같이 SSL Client로써 호출을 해야

```jsp
<%@ page import="java.net.*" %>
<%@ page import="java.io.*" %>

<%
	URL url = new URL("https://...");
	URLConnection rawConn = url.openConnection();

	out.println("class = " + rawConn.getClass().getName() + "<br>");

	weblogic.net.http.HttpsURLConnection conn =
		(weblogic.net.http.HttpsURLConnection) rawConn;

	out.println("response = " + conn.getResponseCode() + "<br>");
	out.println("cipher = " + conn.getCipherSuite() + "<br>");
%>
```

<br>

관련 Class 들이 loaded 되고, 이를 로그로 확인할 수 있습니다

```
<Info> <Security> <BEA-090909> <Using the configured custom SSL Hostname Verifier implementation: weblogic.security.utils.SSLWLSWildcardHostnameVerifier.>
```

<br>

JSP 등을 호출하지 않으면 위 log가 확인되지 않습니다.


<br><br>


# 3. References

SSLWLSWildcardHostnameVerifier 가 적용되지 않음 (KB911375)
