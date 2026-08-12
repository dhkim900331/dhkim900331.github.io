---
date: 2022-12-23 08:46:50 +0900
layout: post
title: "[WebLogic] How to Enable TLS-Client"
tags: [Middleware, WebLogic, TLS, SSL, Certificate]
typora-root-url: ../..
---

# 1. Overview

WebLogic Server 14c 기준에서 Client 측에 TLS Protocol을 어떻게 다루는지 알아본다.

[How-To-Enable-TLS-Server](How-To-Enable-TLS-Server) 에서는 Server측 기준이었으나,

[How-To-Enable-TLS-Client ](How-To-Enable-TLS-Client)에서는 WLS가 Client가 되었을 경우를 설명한다.


<br><br>


# 2. Descriptions


## 2.1 Inbound TLS

다음 옵션으로 TLS를 받아들이는 Server측의 Protocol은 TLSv1.2 이상이 된다.

```shell
USER_MEM_ARGS="${USER_MEM_ARGS} -Djava.security.properties=${DOMAIN_HOME}/java.security"
USER_MEM_ARGS="${USER_MEM_ARGS} -Dweblogic.security.SSL.minimumProtocolVersion=TLSv1.2"
```


<br><br>

<br>

## 2.2 Outbound TLS

WLS가 Client가 될 때에는, 세가지 유형이 있다.

* javax.net.ssl.HttpsURLConnection
* java.net.URL
* Apache HttpClient (주로 사용)

<br>

세가지 방법 모두 JSSE 구현체다.


<br><br>


## 2.3 URL openStream

```jsp
<%@ page contentType="text/html; charset=UTF-8" %>
<%@ page import="java.io.*" %>
<%@ page import="java.net.*" %>

<%
String urlString = "https://...";

try {
    URL url = new URL(urlString);

    // openStream()만 사용
    BufferedReader br =
        new BufferedReader(new InputStreamReader(url.openStream()));

    String line;
    while ((line = br.readLine()) != null) {
        out.println(line + "<br/>");
    }
    br.close();

} catch (Exception e) {
    out.println("ERROR : " + e + "<br/>");
    e.printStackTrace(new PrintWriter(out));
}
%>
```

<br>

Outbound TLSv1.2 를 활성화 해야 한다. (위에서 Inbound TLS 설정했으면)

```shell
USER_MEM_ARGS="${USER_MEM_ARGS} -Djdk.tls.client.protocols=TLSv1.2"
```

<br>

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

<br>

[weblogic.security.SSL.minimumProtocolVersion 시스템 속성 사용](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/secmg/ssl_version.html#GUID-CAC4495F-B8A1-4F62-A9C2-358DC717A830) 의 아래 메모에 따르면, `weblogic.security.SSL.minimumProtocolVersion`옵션과, `jdk.tls.client.protocols` 옵션은 같이 적용할 수 없다고 나와 있다. 

그렇기 때문에, 인스턴스를 2개로 분리하여 테스트 해야 한다.

> Inbound TLS 설정한 A 인스턴스, Outbound 호출을 하는 App이 있는 B 인스턴스

<br>

[오라클 diagnosing-tls-ssl-and-https 게시물](https://blogs.oracle.com/java/post/diagnosing-tls-ssl-and-https) 의 "**JSSE 조정 매개변수**" 에 따르면,

HttpsURLConnection 클래스, URL 클래스의 openStream 을 사용할 때는 `https.protocols` 옵션을 사용을 안내한다.

위 URL 클래스의 openStream 테스트시 `jdk.tls.client.protocols` 옵션에 영향이 미쳤다.

두 Class 모두 JSSE 구현체이므로 그러한 것이다.

<br>

내 테스트 환경에 따른, [JDK 8 Security Enhancements](https://docs.oracle.com/javase/8/docs/technotes/guides/security/enhancements-8.html) 문서를 보면 Java SE 8 부터 `jdk.tls.client.protocols` 옵션을 가이드하고 있다. 그러므로 위 블로그의 내용이 아니라 공식 문서에 의견대로 옵션을 사용하는것이 올바라 보인다.


<br><br>


## 2.4 HttpsURLConnection

```jsp
<%@ page contentType="text/html; charset=UTF-8" %>
<%@ page import="java.io.*" %>
<%@ page import="java.net.*" %>
<%@ page import="javax.net.ssl.*" %>

<%
String urlString = "https://...";

try {
    URL url = new URL(urlString);

    HttpsURLConnection conn =
        (HttpsURLConnection) url.openConnection();

    // JSSE 명시 (UseSunHttpHandler와 무관)
    SSLContext ctx = SSLContext.getInstance("TLS");
    ctx.init(null, null, null);
    conn.setSSLSocketFactory(ctx.getSocketFactory());

    // 테스트용 HostnameVerifier
    conn.setHostnameVerifier((host, sess) -> true);

    int code = conn.getResponseCode();
    out.println("Resp Code : " + code + "<br/>");
    out.println("Cipher    : " + conn.getCipherSuite() + "<br/><br/>");

    InputStream in =
        (code == HttpsURLConnection.HTTP_OK)
            ? conn.getInputStream()
            : conn.getErrorStream();

    BufferedReader br =
        new BufferedReader(new InputStreamReader(in));

    String line;
    while ((line = br.readLine()) != null) {
        out.println(line + "<br/>");
    }
    br.close();

} catch (Exception e) {
    out.println("ERROR : " + e + "<br/>");
    e.printStackTrace(new PrintWriter(out));
}
%>
```

<br>

[Java 공식 언급 - Enabling TLSv1.3 by default on the client](https://www.java.com/en/configure_crypto.html) 에 따르면 HttpsUrlConnection과 URL.openStream() 사용 시에 어떤 옵션을 사용해야 하는지를 알려주고 있다.

~~그러나, 해당 설명과 다르게 정상/비정상 동작을 보이고 있어 더 확인이 필요한 상황이다.~~

<br>

위 어플리케이션으로 테스트시에, `url.openConnection()` Return으로 `weblogic.net.http.SOAPHttpsURLConnection`을 반환하여 에러가 발생했다. 

```
java.lang.ClassCastException: weblogic.net.http.SOAPHttpsURLConnection cannot be cast to javax.net.ssl.HttpsURLConnection
```

<br>

다음은 그 해결책.

> **java.lang.ClassCastException: weblogic.net.http.SOAPHttpsURLConnection을 javax.net.ssl.HttpsURLConnection으로 캐스트할 수 없음(Doc ID 2332805.1)**

<br>

HttpsURLConnection이 javax.net.ssl이 아니라 `weblogic.net.http.SOAPHttpsURLConnection` 를 WLS 측에서 반환한다.

WLS SSL 또한 JSSE 구현을 하였는데, Class 가 다르므로 CastException이 발생한다.

다음의 옵션을 적용하면 WLS Class가 아닌 `javax.next.ssl.HttpsURLConnection` 이 반환되기 때문에 문제가 해결된다.

```shell
-DUseSunHttpHandler=true
```

<br>

위 옵션으로 실행 시, 추가로 인증서 옵션이 필요하였다.

아래는 전체 옵션이다.

```shell
-Djdk.tls.client.protocols=TLSv1.2
-DUseSunHttpHandler=true
-Djavax.net.ssl.trustStore=trust.jks
-Djavax.net.ssl.trustStorePassword=***
-Djavax.net.ssl.keyStoreType=JKS
```


<br><br>


## 2.5 Apache HttpClient

여기서는 [HttpClient 4.5.14 (GA)](https://hc.apache.org/downloads.cgi) 를 다운로드하였다.

다음을 WEB-INF/lib에 배치한다.

*  commons-codec-1.11.jar
*  commons-logging-1.2.jar
*  httpclient-4.5.14.jar
*  httpcore-4.4.16.jar

<br>

```jsp
<%@ page contentType="text/plain; charset=UTF-8" %>
<%@ page import="org.apache.http.client.methods.HttpGet" %>
<%@ page import="org.apache.http.impl.client.CloseableHttpClient" %>
<%@ page import="org.apache.http.impl.client.HttpClients" %>
<%@ page import="org.apache.http.client.methods.CloseableHttpResponse" %>
<%@ page import="org.apache.http.util.EntityUtils" %>

<%
    String url = request.getParameter("url");
    if (url == null) {
        url = "https://wls.local:1443";
    }

    try (CloseableHttpClient client = HttpClients.createDefault()) {
        HttpGet get = new HttpGet(url);

        try (CloseableHttpResponse resp = client.execute(get)) {
            String body = EntityUtils.toString(resp.getEntity(), "UTF-8");
            out.print(body);
        }
    } catch (Exception e) {
        e.printStackTrace(new java.io.PrintWriter(out));
    }
%>
```

<br>

HttpClient library는 가장 널리 사용되는 library 이며 내부적으로 JSSE 구현체이다.

그러므로 Outbound SSL 구현 시 다른 외부 영향에 간섭받지 않는다.


<br><br>


## 2.6 Debugging

다음의 Debugging option을 사용하면 all 보다는 낮은 레벨이지만 충분히 디버깅할 만한 로그들을 확인할 수 있다.

```sh
USER_MEM_ARGS="${USER_MEM_ARGS} -Dweblogic.log.StdoutSeverity=Debug"
USER_MEM_ARGS="${USER_MEM_ARGS} -Djavax.net.debug=ssl,handshake,record,trustmanager"
USER_MEM_ARGS="${USER_MEM_ARGS} -Dweblogic.security.SSL.verbose=true"
```


<br><br>


### 2.5.1 Mismatch protocols

`jdk.tls.client.protocols` 값이 Outbound Target인 Server의 TLS Version과 맞지 않으면 다음과 같이 에러가 발생한다.

* Client WAS is TLSv1.1
* Server WAS is TLSv1.3

```
javax.net.ssl.SSLHandshakeException: No appropriate protocol (protocol is disabled or cipher suites are inappropriate)
```

<br>

`jdk.tls.client.protocols` 값이 Outbound Target인 Server의 TLS Version과 교집합으로 설정될 경우.

* Client WAS is TLSv1.1 ~ 1.3
* Server WAS is TLSv1.3

<br>

<br>

위 어플리케이션 통신 시 정상적인 경우 `javax.net.debug=all` 을 살펴보면

아래와 같이 JDK 1.8의 기본값 TLSv1.2 가 사용되고 있다.

Client Hello의 지원되는 버전이 확인된다.

* Client Hello

```
"ClientHello": {
  "client version"      : "TLSv1.2"
```


<br><br>


`jdk.tls.client.protocols` 값으로 설정한 TLSv1.1 은 안보인다...

```
    "supported_versions (43)": {
      "versions": [TLSv1.3, TLSv1.2]
```

<br>

Server Hello는

```
"ServerHello": {
  "server version"      : "TLSv1.2"
```

```  
    "supported_versions (43)": {
      "selected version": [TLSv1.3]
```


<br><br>

<br>

# 4. Outcome

WLS에서는 과거 Certicom 이었으나 어느 버전부터 JSSE 구현을 따라 SSL 을 제공하고 있다.

<br>

사용자의 App에서 Outbound SSL 호출 시, JSSE 구현을 따라가게 되는데 HttpsURLConnection 사용 시 WebLogic Class가 반환될 때 CastException이 발생되는 것 말고 크게 신경 쓸게 없다.

<br>

이외에는 JSSE 구현을 상속하므로 `javax.net.ssl.trustStore` 옵션이 필요한것만 인지하면 된다.

일부 고객은 WLS의 DemoIdentity/DemoTrust 인증서 등과 같이 WLS내에 인증서가 사용되는것으로 오해를 하는 경우가 있다.
