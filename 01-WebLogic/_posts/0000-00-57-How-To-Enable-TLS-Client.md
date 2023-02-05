---
date: 2022-12-23 08:46:50 +0900
layout: post
title: "[WebLogic] How to Enable TLS-Client"
tags: [WebLogic, TLS, SSL, Certificate]
typora-root-url: ..
---

# 1. 개요

WebLogic Server 14c 기준에서 Client 측에 TLS Protocol을 어떻게 다루는지 알아본다.

[How-To-Enable-TLS-Server](How-To-Enable-TLS-Server) 에서는 Server측 기준이었으나,

[How-To-Enable-TLS-Client ](How-To-Enable-TLS-Client)에서는 WLS가 Client가 되었을 경우를 설명한다.



# 2. Inbound TLS

다음 옵션으로 TLS를 받아들이는 Server측의 Protocol은 TLSv1.2 이상이 된다.

```shell
USER_MEM_ARGS="${USER_MEM_ARGS} -Djava.security.properties=${DOMAIN_HOME}/java.security"
USER_MEM_ARGS="${USER_MEM_ARGS} -Dweblogic.security.SSL.minimumProtocolVersion=TLSv1.2"
```



# 3. Outbound TLS

WLS 가 Client가 되어 Outbound TLS 통신은 여러가지 환경에 따라, 살펴보아야 하는것 같다.



## 3.1 URL openStream

URL class의 openStream으로 Outbound TLS 호출을 할 경우를 살펴본다.



호출 어플리케이션

```jsp
<%@ page import="java.io.*" %>
<%@ page import="java.net.URL" %>
<%@ page import="weblogic.net.http.HttpsURLConnection" %>


<%
    String url = "https://wls.local:8442/testApp/index.jsp";
    URL u = new URL(url);
    HttpsURLConnection httpsUrlConnection = (HttpsURLConnection) u.openConnection();
    System.out.println("Resp Code : " + httpsUrlConnection.getResponseCode());
    System.out.println("Cipher Suite : " + httpsUrlConnection.getCipherSuite());

    // https://docs.oracle.com/javase/tutorial/networking/urls/readingURL.html
    BufferedReader br = new BufferedReader(new InputStreamReader(u.openStream()));
    String inputLine;
    while ((inputLine = br.readLine()) != null) System.out.println(inputLine);
    br.close();
%>

```



Outbound TLSv1.2 를 활성화 해야 한다.

```shell
USER_MEM_ARGS="${USER_MEM_ARGS} -Djdk.tls.client.protocols=TLSv1.2"
```



어플리케이션 호출 시에, 정상적인 경우 아래처럼 표시된다.

```
Resp Code : 200
Cipher Suite : TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
Hello World
```



`-Djdk.tls.client.protocols=TLSv1.1` 설정 시에는 아래처럼 표시된다.

```
javax.net.ssl.SSLHandshakeException: No appropriate protocol (protocol is disabled or cipher suites are inappropriate)
        at sun.security.ssl.HandshakeContext.<init>(HandshakeContext.java:171)
        at sun.security.ssl.ClientHandshakeContext.<init>(ClientHandshakeContext.java:106)
        at sun.security.ssl.TransportContext.kickstart(TransportContext.java:238)
        at sun.security.ssl.SSLEngineImpl.writeRecord(SSLEngineImpl.java:167)
        at sun.security.ssl.SSLEngineImpl.wrap(SSLEngineImpl.java:131)
        Truncated. see log file for complete stacktrace

```



[weblogic.security.SSL.minimumProtocolVersion 시스템 속성 사용](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/secmg/ssl_version.html#GUID-CAC4495F-B8A1-4F62-A9C2-358DC717A830) 의 아래 메모에 따르면, `weblogic.security.SSL.minimumProtocolVersion`옵션과, `jdk.tls.client.protocols` 옵션은 같이 적용할 수 없다고 나와 있다. 

그렇기 때문에, 인스턴스를 2개로 분리하여 테스트 해야 한다.



[오라클 diagnosing-tls-ssl-and-https 게시물](https://blogs.oracle.com/java/post/diagnosing-tls-ssl-and-https) 의 "**JSSE 조정 매개변수**" 에 따르면,

HttpsURLConnection 클래스, URL 클래스의 openStream 을 사용할 때는 `https.protocols` 옵션을 사용을 안내한다.

위 URL 클래스의 openStream 테스트시 `jdk.tls.client.protocols` 옵션에 영향이 미쳤다.

~~이러한 부분은, 블로그 작성 중에도 정확히 파악이 안된다.~~

다시 살펴보니, Java 7 이전 버전에서 Client의 Outbound TLS 통신일 경우에 적용하는 옵션으로 보여진다.



내 테스트 환경에 따른, [JDK 8 Security Enhancements](https://docs.oracle.com/javase/8/docs/technotes/guides/security/enhancements-8.html) 문서를 보면 Java SE 8 부터 `jdk.tls.client.protocols` 옵션을 가이드하고 있다. 그러므로 위 블로그의 내용이 아니라 공식 문서에 의견대로 옵션을 사용하는것이 올바라 보인다.



## 3.2 HttpsUrlConnection (SSLContext)

해당 부분은 URL openStream과 동일할 것이므로,

SSLContext 부분옵션으로 테스트 한다.



HTTPS URL은 호출 시마다 독립적인 채널(?)이 사용된다고 한다.

이 채널마다 서로 다른 TLS protocol을 적용하기 위하여 SSLContext를 이번 테스트에 녹여보았다.

_다만, 맨 아래에서 설명하겠지만 SSLContext에 원하는 protocol이 사실상 구현되지 않았다._



다음의 [어플리케이션](https://goddaehee.tistory.com/268)을 사용하고,

SSLContext 를 사용하여 특정 TLS version을 강제 지정한다.

```
<%@ page import="java.io.*" %>
<%@ page import="java.net.*" %>
<%@ page import="javax.net.ssl.SSLContext" %>
<%@ page import="javax.net.ssl.HttpsURLConnection" %>
<%@ page import="javax.net.ssl.SSLSession" %>
<%@ page import="javax.net.ssl.HostnameVerifier" %>

<%

String urlString = "https://wls.local:8442/testApp/index.jsp";
String line = null;
InputStream in = null;
BufferedReader reader = null;
HttpsURLConnection httpsConn = null;

String protocol=request.getParameter("protocol");

try {
	// Get HTTPS URL connection
	URL url = new URL(urlString);
	httpsConn = (HttpsURLConnection) url.openConnection();

	httpsConn.setHostnameVerifier(new HostnameVerifier() {
		@Override
		public boolean verify(String hostname, SSLSession session) {
			// Ignore host name verification. It always returns true.
			return true;
		}
			});

	int responseCode = httpsConn.getResponseCode();
	System.out.println("Resp Code : " + responseCode);
	System.out.println("Resp Msgs : " + httpsConn.getResponseMessage());

	// SSL setting
	SSLContext context = SSLContext.getInstance(protocol);
	context.init(null,null,null);
	httpsConn.setSSLSocketFactory(context.getSocketFactory());
	System.out.println("getProtocol() : " + context.getProtocol());

	// Connect to host
	httpsConn.connect();
	httpsConn.setInstanceFollowRedirects(true);

	// Print response from host
	if (responseCode == HttpsURLConnection.HTTP_OK) { // 정상 호출 200
			in = httpsConn.getInputStream();
	} else { // 에러 발생
			in = httpsConn.getErrorStream();
	}
	reader = new BufferedReader(new InputStreamReader(in));
	while ((line = reader.readLine()) != null) {
			System.out.printf("%s\n", line);
	}

	reader.close();
} catch (Exception e) {
	System.out.println("error : " + e);
	e.printStackTrace();
}

%>

```



[Java 공식 언급 - Enabling TLSv1.3 by default on the client](https://www.java.com/en/configure_crypto.html) 에 따르면 HttpsUrlConnection과 URL.openStream() 사용 시에 어떤 옵션을 사용해야 하는지를 알려주고 있다.

~~그러나, 해당 설명과 다르게 정상/비정상 동작을 보이고 있어 더 확인이 필요한 상황이다.~~



위 어플리케이션으로 테스트시에, `url.openConnection()` Return으로 `weblogic.net.http.SOAPHttpsURLConnection`을 반환하여 에러가 발생했다. 

```
java.lang.ClassCastException: weblogic.net.http.SOAPHttpsURLConnection cannot be cast to javax.net.ssl.HttpsURLConnection
```



위 해결책으로 다음의 공식 자료가 Google snipets 으로 나오나

> **java.lang.ClassCastException: weblogic.net.http.SOAPHttpsURLConnection을 javax.net.ssl.HttpsURLConnection으로 캐스트할 수 없음(Doc ID 2332805.1)**

여기에 그 내용을 온전히 옮길 수 없다.

다만 그 외 자료를 통틀어보면 , 대게 다음의 해결책이 거론되었다.

```shell
-DUseSunHttpHandler=true
```



위 옵션으로 실행 시, 추가로 인증서 옵션이 필요하였다.

아래는 전체 옵션이다.

```shell
-Djdk.tls.client.protocols=TLSv1.2
-DUseSunHttpHandler=true
-Djavax.net.ssl.trustStore=trust.jks
-Djavax.net.ssl.trustStorePassword=***
-Djavax.net.ssl.keyStoreType=JKS
```



`jdk.tls.client.protocols` 값이 Outbound Target인 Server의 TLS Version과 맞지 않으면 다음과 같이 에러가 발생한다.

* Client WAS is TLSv1.1
* Server WAS is TLSv1.3

```
javax.net.ssl.SSLHandshakeException: No appropriate protocol (protocol is disabled or cipher suites are inappropriate)
```



`jdk.tls.client.protocols` 값이 Outbound Target인 Server의 TLS Version과 교집합으로 설정될 경우.

* Client WAS is TLSv1.1 ~ 1.3
* Server WAS is TLSv1.3

위 상황에서, 어플리케이션을 `https.jsp?protocol=TLSv1.1` 으로 호출할 경우, 현재 URL 호출에 대해서만 특별히 TLSv1.1 으로 강제 지정하길 원하였지만, 어플리케이션 문제인지, 혹은 지금 알지 못하는 다른 환경에 대한 문제인지...



위 어플리케이션 통신 시 정상적인 경우 `javax.net.debug=all` 을 살펴보면

* Client Hello

아래와 같이 JDK 1.8의 기본값 TLSv1.2 가 사용되고 있다.

다시 언급하자면, SSLContext에 직접 TLSv1.3 강제 설정 후 호출하였는데, 아래 로그가 그와 연관이 있는게 맞다면 테스트 어플리케이션 또는 환경의 문제가 있으리라 생각된다.

```
"ClientHello": {
  "client version"      : "TLSv1.2"
```



Client Hello의 지원되는 버전이 확인된다.

`jdk.tls.client.protocols` 값으로 설정한 TLSv1.1 은 안보인다...

```
    "supported_versions (43)": {
      "versions": [TLSv1.3, TLSv1.2]
```



Server Hello는

```
"ServerHello": {
  "server version"      : "TLSv1.2"
```

```  
    "supported_versions (43)": {
      "selected version": [TLSv1.3]
```



# 4. Outcome

Outbound SSL 통신시, WAS 솔루션마다 지원하는 옵션이 있음이 확인된다.

여기서는 대부분 기본(SunHandler) 를 사용하게 되어, 그쪽으로 옵션이 안내되었다.
