---
date: 2024-11-21 10:08:10 +0900
layout: post
title: "[WebLogic/SAML] How To Set SAML 2.0 Services"
tags: [Middleware, WebLogic, SAML, SSO]
typora-root-url: ..
---

# 1. Overview

WebLogic 12.2.1.4 에서 SAML 2.0 Services를 구성하여, SSO 기능을 구현한다.

실제 지원 사례와 동일한 버전을 선택하였다.


<br><br>


# 2. Descriptions

## 2.1 개념
SAML 2.0 에서 지원하는 SSO 개념/기능에 대해서 간단하게 설명하자면,

사용자에게 실 서비스(포털/쇼핑 등)를 제공하는 서비스 제공자. Service Provider. 줄여서 SP가 있다.

사용자에게 시스템 접속 인가 여부를 확인하고 인증 시스템을 제공하는 인증 제공자. Identity Provider. 줄여서 IdP가 있다.

많은 SP들은, IdP와 채널링되어, 하나의 IdP에서 인가되는 것으로도 다른 SP에 별도로 로그인을 하지 않아도 되는 것이다.

<br>

SAML 은 기본적으로 IdP와 SP가 직접적으로 통신하는것이 아니라, 로그인을 하려는 사용자(웹 브라우저)를 통해 **간접적**으로 SAML Request/Response를 주고 받는다.

<br>

SP측에서 최초로, 인가되지 않은 사용자를 IdP 측으로 보내야 할 의무가 있다.

인증 요청만 보내면 되므로, 메세지 자체가 가볍고 간단하기에 일반적으로 IdP 측은 HTTP/Redirect 방식을 사용한다.

GET Method를 의미하며, SP는 사용자에게 `<IdP URL>/ssoRequest.jsp?<Query Strings>` 와 함께 HTTP 302 Redirect 를 요청한다.

사용자는 SAML data를 가지고 IdP 측으로 직접 접근을 한다.

<br>

IdP측에 도착한 사용자가 로그인 과정을 통해 인증이 완료되면,

IdP측은 SAML Response data를 만들고, SP 측에서 원하는 통신 방식으로 보낸다.

일반적으로, SAML Response data는 메세지 크기가 작지 않고, XML Data이며 노출을 꺼리기 때문에 HTTP/POST를 사용한다.

IdP는 사용자에게 `<SP URL>/saml2/acs/sp/post` (ACS URL 이라고 한다.) 으로 POST Data와 함께 가도록 지시한다.

사용자가 직접 SP 에 도착 하는 것으로 마무리 된다.

<br>

아래 SAML Debugging 에서 볼 수 있지만, IdP와 SP측에서 어떻게 Protocol(Redirect? POST?)를 규약하는지 알고 있어야, 흐름을 이해할 수 있다. 


<br><br>

<br>

## 2.2 기능
사용자가 SP에 접근하면, 사용자를 IdP로 보낸다.

IdP에서 사용자가 로그인에 성공하면, SP로 보낸다.

이러한 간단한 설명속에, 각 SP와 IdP가 주고 받는 SAML Data가 있다.

이 SAML Data가 잘 흘러가도록 설정하고, 어떠한 처리가 실제로 이루어지는지 알아야 한다.


<br><br>

<br>

## 2.3 구현
다음 환경을 구성한다.

- WebLogic Domain (IdP_domain , SP_domain)

 - OHS 12cR2 as Proxy


<br><br>


### 2.3.1 IdP domain
IdP_domain (이하 IdP) 측에 다음과 같이 구현한다.

<br>

Security RealmsSecurity Realms - myrealm - Providers - Credential Mapping - New

```
 Name : SAML2_CredentialMapper
 Type : SAML2CredentialMapper
```

<br>

SAML2_CredentialMapper - Configuration - Provider Specific - Save & Activate Changes - Restart AdminServer

```
 Issuer URI : http://idp.wls.local/saml
 Name Qualifier : SAML's IdP Site
```

<br>

Servers - \<Server Name\> - Configuration - Federation Services - SAML 2.0 Identity Provider

```
 Enabled : check
 Preferred Binding : Redirect
```

> IdP 측은 HTTP/Redirect 방식으로 SAML Data를 전달받기를 원한다는 것

<br>

Servers - \<Server Name\> - Configuration - Federation Services - SAML 2.0 General - Save & Activate Changes

```
Replicated Cache Enabled : It depends on using clustering
Published Site URL : http://idp.wls.local/saml2
Entity ID : IdP_domain
```

<br>

Servers - \<Server Name\> - Configuration - Federation Services - SAML 2.0 General - Publish Meta Data

으로 지금까지의 IdP 설정을 File로 게시한다.

```
/path/to/IdP.xml
```


<br><br>


### 2.3.2 SP domain

SP_domain (이하 SP) 측에 다음과 같이 구현한다.

Security Realms - myrealm - Providers - Authentication - New - Save & Activate Changes - Restart AdminServer

```
 Name : SAML2_IdentityAsserter
 Type : SAML2IdentityAsserter
```

<br>

Servers - \<Server Name\> - Configuration - Federation Services - SAML 2.0 Service Provider

```
 Enabled : check
 Preferred Binding : POST
 Default URL : http://sp.wls.local/sampleSaml
```

> SP 측은 HTTP/POST 방식으로 SAML Data를 전달받기를 원한다는 것

<br>

Servers - \<Server Name\> - Configuration - Federation Services - SAML 2.0 General - Save & Activate Changes

```
Replicated Cache Enabled : It depends on using clustering
Published Site URL : http://sp.wls.local/saml2
Entity ID : SP_domain
```

<br>

Servers - \<Server Name\> - Configuration - Federation Services - SAML 2.0 General - Publish Meta Data

으로 지금까지의 IdP 설정을 File로 게시한다.

```
/path/to/SP.xml
```


<br><br>


### 2.3.3 Upload Medadata into each domain

IdP.xml 과 SP.xml 을 각 Domain에 배포한다.

IdP > Security Realms - myrealm - Providers - Credential Mapping - SAML2_CredentialMapper - Management - New - WebService Service Provider Partner

```
Name : SAML_SSO_SP01
File : /path/to/SP.xml (* No IdP.xml) 
```

<br>

SAML_SSO_SP01

```
Enabled : check
Description : SAML_SSO_SP01
Key Info Included : check
```

<br>

SP > Security Realms - myrealm - Providers - Authentication - SAML2_IdentityAsserter - Management - New - Web Single Sign-On Identity Provider Partner

```
Name : SAML_SSO_IDP01
File : /path/to/IdP.xml (* No SP.xml) 
```

<br>

SAML_SSO_IDP01 

```
Enabled : check
Description : SAML_SSO_IDP01
Redirect URIs : /sampleSaml/restricted/services.jsp
```


<br><br>


### 2.3.4 Deploy SAML App

SAML 샘플 어플리케이션을 SP 에 배포 한다.

<br>

전체 구조

```sh
$ tree sampleSaml/
sampleSaml/
├── fail_login.htm
├── index.jsp
├── login.jsp
├── restricted
│   └── services.jsp
└── WEB-INF
    ├── weblogic.xml
    └── web.xml

2 directories, 6 files
```

<br>

파일 별 내용

```
$ cat sampleSaml/fail_login.htm
Your Login Failed.  <a href="/sampleSaml/restricted/services.jsp">Try Again</a>


$ cat sampleSaml/index.jsp
<head>
        <meta HTTP-EQUIV="Refresh" content="1;URL=/sampleSaml/restricted/services.jsp">
</head>


$ cat sampleSaml/login.jsp
<h4>Please enter your user name and password to login to SAML Destination Site Application, <B>SamlDestinationApp</B>:</h4>
<form method="POST" action="j_security_check">
<table border=1>
        <tr>
                <td>Username:</td>
                <td><input type="text" name="j_username"></td>
        </tr>
        <tr>
                <td>Password:</td>
                <td><input type="password" name="j_password"></td>
        </tr>
        <tr>
                <td colspan=2 align=right><input type=submit value="Submit"></td>
        </tr>
</table>
</form>


$ cat sampleSaml/restricted/services.jsp
<a href="http://idp.wls.local/sampleSaml/restricted/services.jsp" >Go to IdP domain </a><br>
<a href="http://sp.wls.local/sampleSaml/restricted/services.jsp" >Go to SP domain </a>


$ cat sampleSaml/WEB-INF/web.xml
<?xml version="1.0" encoding="UTF-8"?>
<web-app id="WebApp_ID" version="2.4" xmlns="http://java.sun.com/xml/ns/j2ee"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://java.sun.com/xml/ns/j2ee http://java.sun.com/xml/ns/j2ee/web-app_2_4.xsd">
    
    <display-name>SAML Destination Site Application</display-name>
    <welcome-file-list>
        <welcome-file>index.jsp</welcome-file>
    </welcome-file-list>
    
    <security-constraint>
        <web-resource-collection>
            <web-resource-name>SecurePages</web-resource-name>
            <description>These pages are only accessible by authorized users.</description>
            <url-pattern>/restricted/*</url-pattern>
            <http-method>GET</http-method>
        </web-resource-collection>
        
        <auth-constraint>
            <description>These are the roles who have access.</description>
                <role-name>SamlTrainee</role-name>
        </auth-constraint>
        
        <user-data-constraint>
            <description>This is how the user data must be transmitted.</description>
            <transport-guarantee>NONE</transport-guarantee>
        </user-data-constraint>
    </security-constraint>
    
    <login-config>
        <auth-method>CLIENT-CERT,BASIC</auth-method>
        <realm-name>myrealm</realm-name>
    </login-config>
    
    <security-role>
        <description>These are the roles who have access.</description>
        <role-name>SamlTrainee</role-name>
    </security-role>
</web-app>


$ cat sampleSaml/WEB-INF/weblogic.xml
<?xml version='1.0' encoding='UTF-8'?>
<weblogic-web-app xmlns="http://www.bea.com/ns/weblogic/90"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    
    <security-role-assignment>
        <role-name>SamlTrainee</role-name>
        <principal-name>Administrators</principal-name>
    </security-role-assignment>
    
    <session-descriptor>
        <persistent-store-type>replicated_if_clustered</persistent-store-type>
        <cookie-name>JSESSIONID</cookie-name>
        <cookie-secure>false</cookie-secure>
    </session-descriptor>

    <container-descriptor>
        <servlet-reload-check-secs>1</servlet-reload-check-secs>
        <resource-reload-check-secs>1</resource-reload-check-secs>
    </container-descriptor>

    <jsp-descriptor>
        <page-check-seconds>1</page-check-seconds>
    </jsp-descriptor>

</weblogic-web-app>
```


<br><br>


### 2.3.5 Setup OHS as Proxy

중간에 OHS가 Proxy를 수행한다.

mod_wl_ohs.conf

```
# to IdP
LoadModule weblogic_module   "${PRODUCT_HOME}/modules/mod_wl_ohs.so"

# to IdP
<VirtualHost idp.wls.local:80>
 ServerName idp.wls.local:80

 <Location />
  WLSRequest On
  WebLogicCluster idp.wls.local:10002
 </Location>

</VirtualHost>


# to SP
<VirtualHost sp.wls.local:80>
 ServerName sp.wls.local:80

 <Location />
  WLSRequest On
  WebLogicCluster sp.wls.local:20002
 </Location>

</VirtualHost>
```


<br><br>


### 2.3.6 Access to SAML App

OHS Proxy를 통하는 아래 URL을 호출한다.
```
http://sp.wls.local/sampleSaml/index.jsp
```

<br>

SP URL을 접속 시에는, 사용자의 로그인을 위해 IdP로 보낸다.

IdP에서 로그인이 완료되면, 다시 SP로 돌아오는 간단한 구조다.


<br><br>

<br>

## 2.4 SAML Debugging
SAML 호출 시, WLS Log를 통해 어떤 흐름을 생성하는지 구체적으로 이해해본다.

SP 외에도 IdP 또한 WLS 이므로 IdP 의 Debug log도 살펴볼 수도 있기 때문에, 이미 IdP 의 Debug log를 분석했었다.

그러나, 여기 SAML 에서는 IdP 측을 일반적으로 WLS 으로 구현하지 않는 경우가 많아 특별히 볼 필요가 없으며,

당장 여기에 IdP 측의 Log를 넣으면, 얻는 정보보다, 복잡함이 증대하므로 넣지 않기로 한다.

<br>

Debug options.

```sh
JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.StdoutDebugEnabled=true"
JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.log.StdoutSeverity=Debug"
JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.log.LogSeverity=Debug"
JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.log.LoggerSeverity=Debug"
JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.debug.DebugSecuritySAML2Service=true"
JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.debug.DebugSecuritySAML2CredMap=true"
JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.debug.DebugSecuritySAML2Atn=true"
JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.debug.DebugSecuritySAML2Lib=true"
JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.debug.DebugHttpSessions=true"
JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.debug.DebugHttp=true"
JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.debug.DebugSecurityAtn=true"
export JAVA_OPTIONS
```

<br>

사용자가 SP 에 배포된 Application 호출

```
<Nov 21, 2024 9:40:47,054 AM KST> <Debug> <Http> <BEA-000000> <Request received from: /10.65.34.108, Secure: false, Request: weblogic.servlet.internal.ServletRequestImpl@7c5faa31[
GET /sampleSaml/index.jsp HTTP/1.1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
ECID-Context: 1.0069q64QGrLEoIXElvtlWJ006cRj00002H;kXjE
Connection: Keep-Alive
X-Forwarded-For: 10.191.6.128
X-WebLogic-KeepAliveSecs: 30
X-WebLogic-Request-ClusterInfo: true
x-weblogic-cluster-hash: FEPGdeZsDkQ3rvaVUMpxl28vaiA

]>
```

<br>

JSESSIONID 를 부여 하는 일반적인 동작

```
<Nov 21, 2024 9:40:47,060 AM KST> <Debug> <Http> <BEA-000000> <weblogic.servlet.internal.ServletRequestImpl@7c5faa31 - /sampleSaml/index.jsp: Wrote cookie: JSESSIONID=grVMKhbSmNP0uHik2GiROtQtOUrWdwm4cZRThFNciygDr4Mn3CO3!-644932965!NONE; path=/; HttpOnly>
```

<br>

사용자가 호출한 `index.jsp`는 내부적으로 `restricted/services.jsp` 를 호출 하도록 되어 있다.

```
<Nov 21, 2024 9:40:48,275 AM KST> <Debug> <Http> <BEA-000000> <Request received from: /10.65.34.108, Secure: false, Request: weblogic.servlet.internal.ServletRequestImpl@3a139a6c[
GET /sampleSaml/restricted/services.jsp HTTP/1.1
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://sp.wls.local/sampleSaml/index.jsp
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Cookie: JSESSIONID=grVMKhbSmNP0uHik2GiROtQtOUrWdwm4cZRThFNciygDr4Mn3CO3!-644932965!NONE
ECID-Context: 1.0069q64UuuVEoIXElvtlWJ006cRj00002J;kXjE
Connection: Keep-Alive
X-Forwarded-For: 10.191.6.128
X-WebLogic-KeepAliveSecs: 30
X-WebLogic-Request-ClusterInfo: true
x-weblogic-cluster-hash: FEPGdeZsDkQ3rvaVUMpxl28vaiA

]>
```

<br>

인가되지 않은 사용자는 열어볼 수 없도록 `web.xml`에 정의 했기 때문에, SAML 이 Triggered 된다.

`put: item with key` 는 이 SAML Request를 추적하기 위한 Key.

```
<Nov 21, 2024 9:40:48,280 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <SAML2Filter: Processing request on URI '/sampleSaml/restricted/services.jsp'>
<Nov 21, 2024 9:40:48,280 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <getServiceTypeFromURI(): request URI is '/sampleSaml/restricted/services.jsp'>
<Nov 21, 2024 9:40:48,280 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <getServiceTypeFromURI(): request URI is not a service URI>
<Nov 21, 2024 9:40:48,280 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <getServiceTypeFromURI(): returning service type 'SPinitiator'>
<Nov 21, 2024 9:40:48,280 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <SP initiating authn request: processing>
<Nov 21, 2024 9:40:48,284 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <SP initiating authn request: partner id is null>
<Nov 21, 2024 9:40:48,290 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <put: item with key _3bc4e93f-119b-4aad-809a-f1b3b2e89b46 is saved in cache.>
```

<br>

앞서, IdP 는 HTTP/Redirect 를 설정했기 때문에, 

SP 측이 QueryString을 만들고 있다.

```
<Nov 21, 2024 9:40:48,290 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <SP initiating authn request: use partner binding HTTP/Redirect>
<Nov 21, 2024 9:40:48,294 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <signature algorithm of saml object: null>
<Nov 21, 2024 9:40:48,297 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <URL encoded saml message:fZDLasMwEEV%2FRczeL8UttogdAiEQaCE0aRfdBNmeNAJZcjVy2s%2Bv4qY03RRmM497L3Pmi89eszM6UtZUkMUpMDSt7ZR5q%2BB5v44KWNRzkr3mg1iO%2FmSe8H1E8iwIDYnvTQWjM8JKUiSM7JGEb8Vu%2BfggeJyKwVlvW6uBrYJQGemnsJP3g0gS1Q3xh6ZY21bqZPK7zBIimzjslMPWA1tb1%2BKUX8FRakJgm1UFh1nT5ljOjlGWlU2US9lFRVrK6Jg1s4ZjUTb5fTilrSRSZ%2FwVE424MeSl8RXwlOfBIeLZPk1FHqqIeXH3CuzlB014BK4gxCR2twT%2BBxCy0V2ehnq3PXS2l8rMk1uv%2Btr%2BZVx%2FAQ%3D%3D>
<Nov 21, 2024 9:40:48,297 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <URL encoded relay state:null>
<Nov 21, 2024 9:40:48,297 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <QueryString without signature:SAMLRequest=fZDLasMwEEV%2FRczeL8UttogdAiEQaCE0aRfdBNmeNAJZcjVy2s%2Bv4qY03RRmM497L3Pmi89eszM6UtZUkMUpMDSt7ZR5q%2BB5v44KWNRzkr3mg1iO%2FmSe8H1E8iwIDYnvTQWjM8JKUiSM7JGEb8Vu%2BfggeJyKwVlvW6uBrYJQGemnsJP3g0gS1Q3xh6ZY21bqZPK7zBIimzjslMPWA1tb1%2BKUX8FRakJgm1UFh1nT5ljOjlGWlU2US9lFRVrK6Jg1s4ZjUTb5fTilrSRSZ%2FwVE424MeSl8RXwlOfBIeLZPk1FHqqIeXH3CuzlB014BK4gxCR2twT%2BBxCy0V2ehnq3PXS2l8rMk1uv%2Btr%2BZVx%2FAQ%3D%3D>
<Nov 21, 2024 9:40:48,297 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <URL:http://idp.wls.local/saml2/idp/sso/redirect?SAMLRequest=fZDLasMwEEV%2FRczeL8UttogdAiEQaCE0aRfdBNmeNAJZcjVy2s%2Bv4qY03RRmM497L3Pmi89eszM6UtZUkMUpMDSt7ZR5q%2BB5v44KWNRzkr3mg1iO%2FmSe8H1E8iwIDYnvTQWjM8JKUiSM7JGEb8Vu%2BfggeJyKwVlvW6uBrYJQGemnsJP3g0gS1Q3xh6ZY21bqZPK7zBIimzjslMPWA1tb1%2BKUX8FRakJgm1UFh1nT5ljOjlGWlU2US9lFRVrK6Jg1s4ZjUTb5fTilrSRSZ%2FwVE424MeSl8RXwlOfBIeLZPk1FHqqIeXH3CuzlB014BK4gxCR2twT%2BBxCy0V2ehnq3PXS2l8rMk1uv%2Btr%2BZVx%2FAQ%3D%3D>
```

<br>

SP측은 사용자에게 HTTP 302 Redirect 를 요청한다.

사용자가 직접 IdP로 SAML Data를 가지고 간다.

```
<Nov 21, 2024 9:40:48,299 AM KST> <Debug> <Http> <BEA-000000> <Response committed. request: 'weblogic.servlet.internal.ServletRequestImpl@3a139a6c - /sampleSaml/restricted/services.jsp' response: weblogic.servlet.internal.ServletResponseImpl@10528dd[
HTTP/1.1 302 Moved Temporarily
Cache-Control: : no-cache, no-store
Date: : Thu, 21 Nov 2024 00:40:48 GMT
Pragma: : no-cache
Location: : http://idp.wls.local/saml2/idp/sso/redirect?SAMLRequest=fZDLasMwEEV%2FRczeL8UttogdAiEQaCE0aRfdBNmeNAJZcjVy2s%2Bv4qY03RRmM497L3Pmi89eszM6UtZUkMUpMDSt7ZR5q%2BB5v44KWNRzkr3mg1iO%2FmSe8H1E8iwIDYnvTQWjM8JKUiSM7JGEb8Vu%2BfggeJyKwVlvW6uBrYJQGemnsJP3g0gS1Q3xh6ZY21bqZPK7zBIimzjslMPWA1tb1%2BKUX8FRakJgm1UFh1nT5ljOjlGWlU2US9lFRVrK6Jg1s4ZjUTb5fTilrSRSZ%2FwVE424MeSl8RXwlOfBIeLZPk1FHqqIeXH3CuzlB014BK4gxCR2twT%2BBxCy0V2ehnq3PXS2l8rMk1uv%2Btr%2BZVx%2FAQ%3D%3D
Content-Length: : 1193
Content-Type: : text/html
X-ORACLE-DMS-ECID: 0069q64UuuVEoIXElvtlWJ006cRj00002J
X-ORACLE-DMS-RID: 0:1
]>
```

<br>

IdP 측에서 사용자의 로그인이 완료되면, SP로 사용자가 POST Data를 가지고 도착한다.

앞서서, HTTP/POST 로 설정했기 때문이며, JSESSIONID 가 동일하다.

```
<Nov 21, 2024 9:40:52,254 AM KST> <Debug> <Http> <BEA-000000> <Request received from: /10.65.34.108, Secure: false, Request: weblogic.servlet.internal.ServletRequestImpl@3a139a6c[
POST /saml2/sp/acs/post HTTP/1.1
Content-Length: 9623
Cache-Control: max-age=0
Origin: http://idp.wls.local
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://idp.wls.local/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Cookie: JSESSIONID=grVMKhbSmNP0uHik2GiROtQtOUrWdwm4cZRThFNciygDr4Mn3CO3!-644932965!NONE
ECID-Context: 1.0069q64i6ZsEoIXElvtlWJ006cRj00002K;kXjE
Connection: Keep-Alive
X-Forwarded-For: 10.191.6.128
X-WebLogic-KeepAliveSecs: 30
X-WebLogic-Request-ClusterInfo: true
x-weblogic-cluster-hash: FEPGdeZsDkQ3rvaVUMpxl28vaiA

]>
```

<br>

SP가 받은 SAML Response를 받았다는 것을 알게 되고,

```
<Nov 21, 2024 9:40:52,259 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <SAML2Servlet: Processing request on URI '/saml2/sp/acs/post'>
<Nov 21, 2024 9:40:52,259 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <getServiceTypeFromURI(): request URI is '/saml2/sp/acs/post'>
<Nov 21, 2024 9:40:52,259 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <getServiceTypeFromURI(): service URI is '/sp/acs/post'>
<Nov 21, 2024 9:40:52,259 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <getServiceTypeFromURI(): returning service type 'ACS'>
```

<br>

SAML Response 를 처리하기 위해,

```
<Nov 21, 2024 9:40:52,259 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <Assertion consumer service: processing>
<Nov 21, 2024 9:40:52,259 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <get SAMLResponse from http request:PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZ ...
```

<br>

Base64 decoded 한다.

```
<Nov 21, 2024 9:40:52,260 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <BASE64 decoded saml message:<?xml version="1.0" encoding="UTF-8"?><saml2p:Response xmlns:saml2p="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:xsd="http://www.w3.org/2001/XMLSchema" Destination="http://sp.wls.local/saml2/sp/acs/post" ID="_7dc88823-91f4-4e57-97a1-87163e3135f2" InResponseTo="_3bc4e93f-119b-4aad-809a-f1b3b2e89b46" IssueInstant="2024-11-21T00:40:52.040Z" Version="2.0"><saml2:Issuer xmlns:saml2="urn:oasis:names:tc:SAML:2.0:assertion">IdP_domain</saml2 ...
```

<br>

decoded 된 값에는 다음과 같은 주요 항목이 있다.

- `Destination` : IdP 에서 SP 로 사용자를 보낼 때, URL (ACS URL 이라고 함)

- `<saml2:Issuer>IdP_domain</saml2:Issuer>` : 발급자, IdP 측
- `InResponseTo="_3bc4e93f-119b-4aad-809a-f1b3b2e89b46"` : SP측에서 Cache한 Key 값과 동일, 사용자 추적 용도
- `NotBefore="2024-11-21T00:40:47.032Z"` : 이 시간 전으로는 사용할 수 없는 세션. +9 시간의 Offset
- `NotOnOrAfter="2024-11-21T00:42:47.032Z"` : 이 시간 이후로는 만료되는 세션. +9 시간의 offset.
  - Before/After의 120 seconds는 `IdP - myrealm - ... - SAML2_CredentialMapper - Configuration - Provider Specific - Default Time To Live` 에 정의된 기본값이다.

<br>

Destination은 IdP 에서 SP를 호출하는 URL 이며, SP 측 SAML 설정 값 중 `Published Site URL` 값과 동일한 구조여야 한다.

IdP 측에서 설정하는 Destination과 SP측의 `Published Site URL` 의 Prefix 가 다른 경우, 다음과 같은 Error가 발생한다.

이는, `Federation Services - SAML 2.0 General - Recipient Check Enabled` 을 Unchecked 하는 것으로 우회할 수 있다.

```
<Debug> <SecuritySAML2Service> <BEA-000000> <[Security:096552]Illegal destination: http://sp.wls.local/saml2/sp/acs/post of assertion response.> 
<Debug> <SecuritySAML2Service> <BEA-000000> <exception info
org.opensaml.saml.common.SAMLException: [Security:096552]Illegal destination: http://sp.wls.local/saml2/sp/acs/post of assertion response.
 at com.bea.security.saml2.service.acs.AssertionConsumerServiceImpl$ResponseValidator.validateDestination(AssertionConsumerServiceImpl.java:384)
 at com.bea.security.saml2.service.acs.AssertionConsumerServiceImpl$ResponseValidator.validate(AssertionConsumerServiceImpl.java:368)
 at com.bea.security.saml2.service.acs.AssertionConsumerServiceImpl.verifyAttrAndEle(AssertionConsumerServiceImpl.java:333)
 at com.bea.security.saml2.service.acs.AssertionConsumerServiceImpl.process(AssertionConsumerServiceImpl.java:128)
 at com.bea.security.saml2.cssservice.SAML2ServiceImpl.process(SAML2ServiceImpl.java:146)
 at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method) 
 ...
```

<br>

InResponseTo 값은 SP 에서 Cached 한 Key 값(위에서 언급한)과 동일하다.

이 값을 통해 어느 사용자의 인증인지 추적할 수 있게 된다.

마지막으로, Key를 삭제한다.

```
<Nov 21, 2024 9:40:52,295 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <remove: key _3bc4e93f-119b-4aad-809a-f1b3b2e89b46 and associated item have been removed from cache.>
```

<br>

인증이 완료된 사용자는, 처음 접속을 하려는(index.jsp에서 요청한) 곳으로 이동한다.

```
<Nov 21, 2024 9:40:52,297 AM KST> <Debug> <Http> <BEA-000000> <Response committed. request: 'weblogic.servlet.internal.ServletRequestImpl@3a139a6c - /saml2/sp/acs/post' response: weblogic.servlet.internal.ServletResponseImpl@10528dd[
HTTP/1.1 302 Moved Temporarily
Date: : Thu, 21 Nov 2024 00:40:52 GMT
Location: : http://sp.wls.local:80/sampleSaml/restricted/services.jsp
Content-Length: : 311
Content-Type: : text/html
]>
```


<br><br>


## 2.5 SAML JSESSIONID

SAML Application과 OHS Proxy에서 Cookie Name을 JSESSIONID가 아닌, XSESSIONID 와 같이 사용하는 경우를 예로 든다.

<br>

위에서 살펴본 흐름처럼, Set-Cookie를 통해 XSESSIONID 를 부여하고 있다.

```
<Nov 20, 2024 2:34:43,918 PM KST> <Debug> <Http> <BEA-000000> <Response committed. request: 'weblogic.servlet.internal.ServletRequestImpl@215fb805 - /sampleSaml/index.jsp' response: weblogic.servlet.internal.ServletResponseImpl@1d944986[
HTTP/1.1 200 OK
Date: : Wed, 20 Nov 2024 05:34:43 GMT
Content-Length: : 99
Content-Type: : text/html; charset=ISO-8859-1
X-ORACLE-DMS-ECID: 0069p61mP6HEoIXElvtlWJ006blw000001
X-ORACLE-DMS-RID: 0:1
X-WebLogic-JVMID: -644932965
Set-Cookie: XSESSIONID=7zhIENjLiCMQ_fB-9MkLduDKbTYVhaCVxPsALX3C3NF9OxVfwtGw!-644932965!NONE; path=/; HttpOnly
X-WebLogic-Cluster-List: -644932965!wls.local!20002!-1
X-WebLogic-Cluster-Hash: FEPGdeZsDkQ3rvaVUMpxl28vaiA
]>
```

<br>

Key를 Cached 한다.

```
<Nov 20, 2024 2:34:45,229 PM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <put: item with key _81d31ccf-8c38-472b-928a-3bb4922267c4 is saved in cache.>\
```

<br>

IdP로 부터 ACS 응답과 함께 POST Data를 받는다.

```
<Nov 20, 2024 2:34:49,890 PM KST> <Debug> <Http> <BEA-000000> <Request received from: /10.65.34.108, Secure: false, Request: weblogic.servlet.internal.ServletRequestImpl@215fb805[
POST /saml2/sp/acs/post HTTP/1.1
Content-Length: 9623
Cache-Control: max-age=0
Origin: http://idp.wls.local
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://idp.wls.local/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Cookie: XSESSIONID=7zhIENjLiCMQ_fB-9MkLduDKbTYVhaCVxPsALX3C3NF9OxVfwtGw!-644932965!NONE
ECID-Context: 1.0069p62AWG9EoIXElvtlWJ006blw000006;kXjE
Connection: Keep-Alive
X-Forwarded-For: 10.191.6.10
X-WebLogic-KeepAliveSecs: 30
X-WebLogic-Request-ClusterInfo: true
x-weblogic-cluster-hash: FEPGdeZsDkQ3rvaVUMpxl28vaiA

]>
```

<br>

POST Data를 Base64 decoded 하면, InResponseTo가 이전에 Cached 한 Key 값과 동일한 것이 확인된다.

```
Destination="http://sp.wls.local/saml2/sp/acs/post" ID="_bc02a672-0c89-4938-8564-de51cd070ece" InResponseTo="_81d31ccf-8c38-472b-928a-3bb4922267c4" 
```

<br>

그러나, 이후 동작은 정상적이지 않다.

사용자의 입장에서는 최종 목적지에 도착 하지 못하고,

이전처럼 SP 와 IdP 간의 인증 흐름 회귀에 빠져 나오지 못한다.

이는 JSESSIONID 를 XSESSIONID 로 바꾼것과 관련이 있다.

<br>

[Use of Non-default Cookie Name](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/secmg/saml20.html#GUID-A459E341-4552-4793-9C71-DEAF22919234) 에서 설명하는 것이 그 이유다.

IdP 로 부터 도착한 ACS 요청은, JSESSIONID 를 생성하여, App으로 Redirect 되는데,

JSESSIONID 를 쓰지 않는 경우, Redirect 되지 않는 동작이 발생하고,

결과적으로 사용자는 여전히 인증되지 않아 SP 에서 다시 IdP 로 인증을 요청한다.

<br>

## 2.6 Session Timeout

web.xml 의 session-timeout 를 최소값 1분 설정 시, IdP 에서 지연될 경우 SP의 Session 이 만료되어 인증이 불가할 것으로 예상했다.

<br>

Session이 60초 만료로 생성되었다.

```
<Nov 20, 2024 3:55:52,542 PM KST> <Debug> <HttpSessions> <BEA-000000> <Session ID=1xVIWyLdMncjBYH_gsIRjn71F421RG8EbU-I7T_w8_nn2Zi34Awu, maxInactiveInterval=60, activeRequestCount=0, sessionInUse=false>
```

<br>

해당 Session이 Set-Cookie 로 Header에 추가 된다.

```
<Nov 20, 2024 3:55:52,544 PM KST> <Debug> <Http> <BEA-000000> <Response committed. request: 'weblogic.servlet.internal.ServletRequestImpl@7100da9f - /sampleSaml/index.jsp' response: weblogic.servlet.internal.ServletResponseImpl@6f26a8e7[
HTTP/1.1 200 OK
Date: : Wed, 20 Nov 2024 06:55:52 GMT
Content-Length: : 99
Content-Type: : text/html; charset=ISO-8859-1
X-ORACLE-DMS-ECID: 0069pA^020REoIXElvtlWJ006cT700001p
X-ORACLE-DMS-RID: 0:1
Set-Cookie: JSESSIONID=1xVIWyLdMncjBYH_gsIRjn71F421RG8EbU-I7T_w8_nn2Zi34Awu!-644932965!NONE; path=/; HttpOnly
]>
```

<br>

Key는 Cached 된다.

```
<Nov 20, 2024 3:55:53,851 PM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <put: item with key _8833e94b-835a-4b86-b22f-371b78058000 is saved in cache.>
```

<br>

IdP 응답이 아직 돌아오지 않는 가운데,

invalidation-interval-secs 로 인해 Session이 만료된다.

```
<Nov 20, 2024 3:57:27,837 PM KST> <Debug> <HttpSessions> <BEA-000000> <Session ID=1xVIWyLdMncjBYH_gsIRjn71F421RG8EbU-I7T_w8_nn2Zi34Awu, maxInactiveInterval=60, activeRequestCount=0, sessionInUse=false>

<Nov 20, 2024 3:57:27,837 PM KST> <Debug> <HttpSessions> <BEA-000000> <[HTTP Session:100035]The timer invalidated session ID: 1xVIWyLdMncjBYH_gsIRjn71F421RG8EbU-I7T_w8_nn2Zi34Awu, Web application: /sampleSaml, because it expired.>
```

<br>

지연되어 돌아온 IdP 응답에 만료된 JSESSIONID 가 확인된다.

```
<Nov 20, 2024 3:57:48,487 PM KST> <Debug> <Http> <BEA-000000> <Request received from: /10.65.34.108, Secure: false, Request: weblogic.servlet.internal.ServletRequestImpl@137b54ad[
POST /saml2/sp/acs/post HTTP/1.1
Content-Length: 9623
Cache-Control: max-age=0
Origin: http://idp.wls.local
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://idp.wls.local/
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9
Cookie: JSESSIONID=1xVIWyLdMncjBYH_gsIRjn71F421RG8EbU-I7T_w8_nn2Zi34Awu!-644932965!NONE
ECID-Context: 1.0069pAeuLWYEoIXElvtlWJ006cT700001y;kXjE
Connection: Keep-Alive
X-Forwarded-For: 10.191.6.10
X-WebLogic-KeepAliveSecs: 30
X-WebLogic-Request-ClusterInfo: true
x-weblogic-cluster-hash: FEPGdeZsDkQ3rvaVUMpxl28vaiA

]>
```

<br>

Browser Header에 있는 JSESSIONID 는 만료되어, 찾을 수 없는 상태에 놓인다.

```
<Nov 20, 2024 3:57:48,488 PM KST> <Debug> <Http> <BEA-000000> <weblogic.servlet.internal.ServletRequestImpl@137b54ad - /saml2/sp/acs/post: SessionID: 1xVIWyLdMncjBYH_gsIRjn71F421RG8EbU-I7T_w8_nn2Zi34Awu!-644932965!NONE found in cookie header>
<Nov 20, 2024 3:57:48,488 PM KST> <Debug> <Http> <BEA-000000> <weblogic.servlet.internal.ServletRequestImpl@137b54ad - /saml2/sp/acs/post: SessionID= 1xVIWyLdMncjBYH_gsIRjn71F421RG8EbU-I7T_w8_nn2Zi34Awu found for WASC=ServletContext@1633298321[app:saml2 module:saml2.war path:/saml2 spec-version:3.1]>
<Nov 20, 2024 3:57:48,489 PM KST> <Debug> <Http> <BEA-000000> <weblogic.servlet.internal.ServletRequestImpl@137b54ad - /saml2/sp/acs/post: Trying to find session: 1xVIWyLdMncjBYH_gsIRjn71F421RG8EbU-I7T_w8_nn2Zi34Awu!-644932965!NONE>
<Nov 20, 2024 3:57:48,489 PM KST> <Debug> <Http> <BEA-000000> <weblogic.servlet.internal.ServletRequestImpl@137b54ad - /saml2/sp/acs/post: Trying other contexts to find valid session for id: 1xVIWyLdMncjBYH_gsIRjn71F421RG8EbU-I7T_w8_nn2Zi34Awu!-644932965!NONE>
<Nov 20, 2024 3:57:48,489 PM KST> <Debug> <Http> <BEA-000000> <weblogic.servlet.internal.ServletRequestImpl@137b54ad - /saml2/sp/acs/post: Couldn't find valid session for id: 1xVIWyLdMncjBYH_gsIRjn71F421RG8EbU-I7T_w8_nn2Zi34Awu!-644932965!NONE>
```

<br>

그러나, 이후 SAML 응답에 대해 정상 처리가 되어 사용자 입장에서는 문제가 없었다.

Cached Key는 삭제되고, 3600초 라는 세션이 강제적(?)으로 할당되었다.

```
<Nov 20, 2024 3:57:48,527 PM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <remove: key _8833e94b-835a-4b86-b22f-371b78058000 and associated item have been removed from cache.>

<Nov 20, 2024 3:57:48,519 PM KST> <Debug> <HttpSessions> <BEA-000000> <[HTTP Session:100046]Creating new session with ID: 33hIXOfn3-_QVwIfiSYAknMY1SUlFDAuP7T8X6TNc3_AnUZcGwjm for Web application: /saml2.>
<Nov 20, 2024 3:57:48,528 PM KST> <Debug> <HttpSessions> <BEA-000000> <Session ID=33hIXOfn3-_QVwIfiSYAknMY1SUlFDAuP7T8X6TNc3_AnUZcGwjm, maxInactiveInterval=3600, activeRequestCount=0, sessionInUse=false>
```

<br>

Session에 Cached Key가 있을 것으로 예상하고, 진행한 테스트였으나 그렇지 않았다.


<br><br>


## 2.7 Expired Certificate

IdP측와 SP측은 서로 간에 SAML Request/Response Data를 주고 받을 때,

상대방의 메타데이터(이미 서로 가지고 있음) 안에 있는 상대방의 인증서의 공개키로 암호화를 하여 전달한다.

다시, 서로 간에 주고 받는 SAML Data를 각자가 가지고 있는 개인키로 복호화 하는, 일반적인 SSL 기반과 동일하다.

이 과정 가운데, IdP 측의 인증서가 만료된 경우에 대하여 재현한다.

<br>

다음의 명령어로, IdP Metadata xml file에 포함된 인증서의 유효기간을 알 수 있다.

```
# IDP Metadata xml file에서 '<ds:X509Certificate>' 와 '</ds:X509Certificate>' 사이의 내용을
# 아래와 같이 certificate.pem 으로 저장

cat << EOF > certificate.pem
-----BEGIN CERTIFICATE-----
...<here, write key down>
-----END CERTIFICATE-----
EOF

# 아래 명령어의 결과로, Not Before/After를 보면 된다.
$ openssl x509 -in certificate.pem -text -noout
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number:
            3e:10:9e:d3:0c:af:d4:83:a2:7b:d7:e9:47:97:2a:f2
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: C = US, ST = MyState, L = MyTown, O = MyOrganization, OU = FOR TESTING ONLY, CN = CertGenCA
        Validity
            Not Before: Nov 17 01:56:47 2024 GMT
            Not After : Nov 18 01:56:47 2039 GMT
        Subject: C = US, ST = MyState, L = MyTown, O = MyOrganization, OU = FOR TESTING ONLY, CN = wls.local
        ...
```

<br>

> 이 게시물에서는, IdP가 WebLogic 이므로 다음의 문서에 따라 사용되고 있는 Demo 인증서의 유효기간을 확인하면, 위와 같다.
>
> `keytool -list -v -keystore ${DOMAIN_HOME}/security/DemoIdentity.jks -storepass DemoIdentityKeyStorePassPhrase`
>
> **What are the Default Passwords for Demo Identity and Demo Trust Keystores (Doc ID 2886289.1)**

<br>

다음의 명령어로, 의도적으로 만료된 인증서를 생성하고 본래의 시간으로 복귀한다.

idp.jks는 WebLogic(IdP) Keystore/SSL에 등록하고, 메타데이터를 재생산(Publish Meta Data) 한다.

메타데이터 파일을 SP 측에 등록한다.

```sh
sudo date -s '2001-02-03 04:05:06'

openssl req -newkey rsa:2048 -nodes -keyout idp.key -out idp.csr -subj "/CN=wls.local/OU=FOR TESTING ONLY/O=MyOrganization/L=MyTown/ST=MyState/C=US"
openssl x509 -req -in idp.csr -signkey idp.key -out idp.crt -days 365
openssl x509 -in idp.crt -out idp.pem -outform PEM
openssl x509 -in idp.pem -text -noout
openssl pkcs12 -export -in idp.crt -inkey idp.key -out idp.p12 -name idp -passout pass:idp

keytool -importkeystore \
  -srckeystore idp.p12 -srcstoretype PKCS12 -srcstorepass idp \
  -destkeystore idp.jks -deststoretype JKS -deststorepass idppass
keytool -list -v -keystore idp.jks -storepass idppass

sudo date -s '2024-11-30 12:21:25'
```

<br>

SP Initiator로 SP에서 IdP 측으로 SAML Request가 전달된 다음,

IdP측에서 서명을 할 때, 만료된 인증서의 경우 예외가 발생한다.

클라이언트는 IdP 측으로 부터 HTTP 500 Error 를 받는다.

IdP 로 동작하는 WLS 의 Debug log 를 살펴본다.

```
# IdP 측에서 login 처리
<Dec 2, 2024 10:55:18,629 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <SAML2Servlet: Processing request on URI '/saml2/idp/login'>

...

# 만료된 인증서로 서명을 하는 경우에 발생하는 예외
Dec 2, 2024 10:55:18,716 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <Using expired certificate at alias null for signing.>
<Dec 2, 2024 10:55:18,717 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <allow expired cert is false>
<Dec 2, 2024 10:55:18,725 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <[Security:096630]Using expired certificate at alias null for signing.>
<Dec 2, 2024 10:55:18,725 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <Caused by: NotAfter: Sun Feb 03 04:05:06 KST 2002>
<Dec 2, 2024 10:55:18,726 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <exception info
com.bea.security.saml2.service.SAML2Exception: [Security:096630]Using expired certificate at alias null for signing.
        at com.bea.security.saml2.service.AbstractService.checkSSOCertificate(AbstractService.java:122)
        at com.bea.security.saml2.service.sso.SSOServiceProcessor.sendResponse(SSOServiceProcessor.java:359)
        at com.bea.security.saml2.service.sso.SSOServiceProcessor.loginReturn(SSOServiceProcessor.java:236)
        ...
```

<br>

IdP에 `-Dcom.bea.common.security.saml2.allowExpiredCerts=true` 옵션을 적용 후, 만료된 인증서로도 서명을 한다.

```
<Dec 2, 2024 10:51:46,668 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <SAML2Servlet: Processing request on URI '/saml2/idp/login'>

...

<Dec 2, 2024 10:51:46,758 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <allow expired cert is true>
```

<br>

그러나, SP 측에서는 만료된 인증서를 수락하지 않으므로, 예외가 발생한다.

아래는 SP 측 Log

```
# Response 는 서명되었지만, 예외가 발생하는 경우의 로그
<Dec 2, 2024 11:01:45,683 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <<samlp:Response> is signed.>
<Dec 2, 2024 11:01:45,683 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <NotAfter: Sun Feb 03 04:05:06 KST 2002>
<Dec 2, 2024 11:01:45,683 AM KST> <Debug> <SecuritySAML2Service> <BEA-000000> <exception info
java.security.cert.CertificateExpiredException: NotAfter: Sun Feb 03 04:05:06 KST 2002
        at sun.security.x509.CertificateValidity.valid(CertificateValidity.java:277)
        at sun.security.x509.X509CertImpl.checkValidity(X509CertImpl.java:671)
        at sun.security.x509.X509CertImpl.checkValidity(X509CertImpl.java:644)
        ...
```

<br>

[Configuring SAML 2.0 Services: Main Steps](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/secmg/saml20.html#GUID-C541F7EB-1833-4500-8269-5ADB91E6BB6E) 페이지의 설명으로,

기본적으로 SAML 2.0 에서는 만료/유효하지 않은 인증서를 서명(Singing)에 사용하지 않으며

 `-Dcom.bea.common.security.saml2.allowExpiredCerts=true` 옵션을 사용하여 허용하도록 한다.

여기서 서명은 IdP 측에서 하므로, IdP가 WLS 로 구현된 경우에 사용 가능한 옵션이다.

<br>

SP 에서 만료된 인증서를 수락하는 옵션은 없으므로, IdP 측이 WLS가 아닌 경우 반드시 인증서를 갱신해야 한다.

해당 옵션은, 12.2.1.3.0.0 에서 추가 되었다.


<br><br>

<br>

# 3. References

SAML Assertion Consumer Service (ACS) with Non Default Cookie in WebLogic Server (Doc ID 2960556.1)

WebLogic Admin Console Cookie Name change for SAML based SSO (Doc ID 2903459.1)

Does SAML 1.1 Require The Default JSESSIONID Cookie Name? (Doc ID 1376040.1)

[SAML WebLogic 가이드 #1](https://blogs.oracle.com/blogbypuneeth/post/steps-to-configure-saml-sso-with-azure-as-idp-and-weblogic-server-as-sp)

[SAML WebLogic 가이드 #2](https://blogs.oracle.com/blogbypuneeth/post/steps-to-configure-saml-20-with-weblogic-server-using-embedded-ldap-as-a-security-store-only-for-dev-environment)

What are the Default Passwords for Demo Identity and Demo Trust Keystores (Doc ID 2886289.1)

**WebLogic: [Security:096552]Illegal destination: <URL>/saml2/sp/acs/post of assertion response (Doc ID 3063248.1)**
