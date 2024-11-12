---
date: 2023-04-06 08:54:37 +0900
layout: post
title: "[WebLogic] security-constraint in web.xml"
tags: [Middleware, WebLogic, web.xml, Security, J2EE]
typora-root-url: ..
---

# 1. 개요

web.xml J2EE Spec에서 security-constraint 기술 사용법에 대해서 간략하게 설명한다.


<br><br>


# 2. HTTP-METHOD 제한

```xml
<web-app>
  <security-constraint>
    <web-resource-collection>
        <web-resource-name>Secured</web-resource-name>
        <url-pattern>/secured/*</url-pattern>
        <http-method>POST</http-method>
		<http-method>GET</http-method>
    </web-resource-collection>
	<auth-constraint />
  </security-constraint>
</web-app>
```


`curl -X GET/POST` 호출에 대해서는 `HTTP 403 Forbidden` 발생한다.

<br>

`/secured/*` URI에 대해서는 POST/GET method를 아무도 접근하지 못하도록 `<auth-constraint />` 설정한다.

중요한 포인트는 `auth-constraint` 이다.


<br><br>


# 3. HTTPS으로 Redirect

```xml
<web-app>
  <security-constraint>
    <web-resource-collection>
        <web-resource-name>Secured</web-resource-name>
        <url-pattern>/secured/*</url-pattern>
        <http-method>POST</http-method>
		<http-method>GET</http-method>
    </web-resource-collection>
    <user-data-constraint>
        <!--<transport-guarantee>CONFIDENTIAL</transport-guarantee>-->
        <transport-guarantee>INTEGRAL</transport-guarantee>
    </user-data-constraint>
  </security-constraint>
</web-app>
```


`transport-guarantee` 옵션이 CONFIDENTIAL 또는 INTEGRAL 일 경우, HTTPS 로 Redirect(302) 처리 된다.

이때, WAS에 SSL 수신 포트가 활성화되어 있어야 한다.

<br>

`curl -X POST/GET` 요청에 대해서는 HTTPS 로 전환된다.

그 외 요청들은 전환되지 않는다.

<br>

중요한 포인트는 `auth-constraint` 가 없다는 것이다. METHOD를 제한하지 않으니, TRACE,OPTIONS,DELETE,HEAD 등.. 모든 METHOD를 허용한다.


<br><br>


# 4. 결합 옵션

```xml
<web-app>
  <security-constraint>
    <web-resource-collection>
        <web-resource-name>Secured</web-resource-name>
        <url-pattern>/secured/*</url-pattern>
        <http-method>POST</http-method>
		<http-method>GET</http-method>
    </web-resource-collection>
    <user-data-constraint>
        <transport-guarantee>CONFIDENTIAL</transport-guarantee>
    </user-data-constraint>
  </security-constraint>
  
  <security-constraint>
    <web-resource-collection>
        <web-resource-name>Secured_Method_Restrict</web-resource-name>
        <url-pattern>/secured/*</url-pattern>
        <http-method>HEAD</http-method>
        <http-method>DELETE</http-method>
        <http-method>PUT</http-method>
        <http-method>OPTIONS</http-method>
        <http-method>TRACE</http-method>
        <http-method>PATCH</http-method>
        <http-method>COPY</http-method>
        <http-method>MOVE</http-method>
    </web-resource-collection>
    <auth-constraint />
  </security-constraint>
</web-app>
```


POST/GET 은 HTTPS 전환되어 보호되고,

그 외 METHOD는 접근 거부된다.


<br><br>


# 5. References

**http-method 와 transport-guarantee 으로 애플리케이션 요청을 보호하는 방법 (Doc ID 2947435.1)**

HTTP 사용자 요청을 HTTPS로 리다이렉트하는 방법 (Doc ID 1557741.1)

[web.xml Deployment Descriptors](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/scprg/thin_client.html#GUID-ED32AA9B-6BB4-4B61-A68E-84659B7947D7)

[Restricting the use of HTTP methods](https://www.ibm.com/docs/en/odm/8.10?topic=methods-restricting-use-http)

[웹 모듈 보안 설정](https://technet.tmaxsoft.com/upload/download/online/jeus/pver-20150722-000001/security/chapter_application_module_security_setup.html#sect_webmodule_security_setup)

[Java EE Security Essentials](https://dzone.com/refcardz/getting-started-java-ee)

[Warning: JACC: For the URL pattern xxx, all but the following methods were uncovered: POST, GET](https://stackoverflow.com/questions/27431243/warning-jacc-for-the-url-pattern-xxx-all-but-the-following-methods-were-uncov)

[웹취약점 Tomcat http-method 처리..TRACE](https://hulbo.tistory.com/36)

[Tomcat SSL 적용 + HTTP METHODS제한](https://junjunrecord.tistory.com/97)

[[Spring & Tomcat ] Https 설정하기](https://hellowk1.blogspot.com/2015/04/spring-tomcat-https.html)
