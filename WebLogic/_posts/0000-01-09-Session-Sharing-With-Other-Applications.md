---
date: 2025-03-08 10:18:05 +0900
layout: post
title: "[WebLogic/Session] Session Sharing With Other Applications"
tags: [Middleware, WebLogic, Session, EAR]
typora-root-url: ..
---

# 1. Overview

서로 다른 Application 간의 Http Session 공유 방법

<br>


# 2. Descriptions

Application이 같지만, 서로 다른 인스턴스 등에 배포된 경우에는

- 서비스 되는 도메인이 다른 경우 : `<cookie-domain>` 또는 `<cookie-path>` 등의 사용

<br>

그러나 Application의 Context-root가 서로 다른 경우에는, 분리된 별도의 각기 App이므로,

- EAR 구조로 패키징 하고, `<sharing-enabled>` 를 사용해야 한다.


<br><br>


## 2.1 integratedApp (EAR)

EAR 형식의 integratedApp 의 구조

```
/sw/app/integratedApp
├── META-INF
│   ├── application.xml
│   └── weblogic-application.xml
├── contentApp.war
└── portalApp.war
```

<br>

META-INF/application.xml

```xml
<application>
  <module>
    <web>
      <web-uri>portalApp.war</web-uri>
      <context-root>portalApp</context-root>
    </web>
  </module>
  <module>
    <web>
      <web-uri>contentApp.war</web-uri>
      <context-root>contentApp</context-root>
    </web>
  </module>
</application>
```

<br>

META-INF/weblogic-application.xml

```xml
<weblogic-application>
    <session-descriptor>
        <persistent-store-type>coherence-web</persistent-store-type>
        <sharing-enabled>true</sharing-enabled>
    </session-descriptor>
</weblogic-application>
```


<br><br>


## 2.2 portalApp / contentApp

두 App은 안의 내용물은 같으나, 각기 서로 다른 App으로 테스트하기 위해 Context-root를 다르게 한 것이다.

<br>

```
/sw/app/contentApp (또는 portalApp)
├── session.jsp
└── WEB-INF
    ├── classes
    │   └── session-cache-config.xml (Coherence 환경이라 있는 파일)
    ├── weblogic.xml
    └── web.xml
```

<br>

WEB-INF/weblogic.xml

```xml
<weblogic-web-app>

    <session-descriptor>
        <persistent-store-type>coherence-web</persistent-store-type>
                <cookie-name>JSESSIONID_CONTENT</cookie-name>
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

서로 다른 App이므로 cookie-name 또한 다르게 설정되어 있다.


<br><br>


## 2.3 sharing-enabled

portalApp과 contentApp은 서로 다른 Context-root를 가지고 있고, weblogic.xml에서도 cookie-name이 다르다.

즉, 완벽히 서로는 분리된 Application으로 동작한다.

<br>

이 둘을, EAR 로 패키징 및 sharing-enabled **True** 설정되어, 서로의 Application 끼리 Session을 공유하게 된다.

다음 모든 접속 간에 생성되는 Session은 공유 된다.

- http://../portalApp/session.jsp
- http://../contentApp/session.jsp

<br>

특히, 여기서는 Coherence*Web 등으로 Http Session Clustering을 구현하였기 때문에 **서로 다른 인스턴스\*서로 다른 Application** 상에서도 공유된다.

<br>

sharing-enabled **False** 인 경우에는, 같은 Context-root를 갖는 Application 간에서만 Session이 공유되므로 portalApp과 contentApp 간에는 공유되지 않는다.


<br><br>

<br>

# 3. References

https://blog.naver.com/ks900331/221505443322
