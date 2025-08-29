---
date: 2025-06-18 14:55:33 +0900
layout: post
title: "[Coherence/Web] How To Integrate WebLogic And Tomcat?"
tags: [Coherence, WebLogic, Tomcat, HttpSession]
typora-root-url: ..
---

# 1. Overview

WebLogic과 Tomcat 등 이기종 Middleware의 Http Session 공유 방법에 대해 테스트된 자료

<br>

# 2. Descriptions

Coherence / WebLogic 12cR2 and Tomcat 8.5.XX

[외부 게시물](https://with-kami.tistory.com/1534856) 을 통해 많은 도움이 되었고, 공식 메뉴얼에서도 자세하게 알려주고 있으니 기본 가이드는 앞에서 확인.

<br>

WebLogic에 배포되는 Application과 Tomcat에 배포되는 Application은 다음과 같이 동일하다.

```sh
$ tree /sw/app/coherenceApp
/sw/app/coherenceApp
├── session.jsp
└── WEB-INF
    ├── weblogic.xml
    └── web.xml

1 directory, 3 files
```

<br>

Tomcat `web.xml` 은 다음의 요소가 중요.

```xml
  <context-param>
    <param-name>coherence-servletcontext-clustered</param-name>
    <param-value>true</param-value>
  </context-param>

  <context-param>
    <param-name>coherence-enable-sessioncontext</param-name>
    <param-value>true</param-value>
  </context-param>

  <context-param>
    <param-name>coherence-session-cookie-path</param-name>
    <param-value>/</param-value>
  </context-param>

  <context-param>
    <param-name>coherence-scopecontroller-class</param-name>
    <!--<param-value>com.tangosol.coherence.servlet.AbstractHttpSessionCollection$ApplicationScopeController</param-value>-->
    <param-value>com.tangosol.coherence.servlet.AbstractHttpSessionCollection$GlobalScopeController</param-value>
  </context-param>

  <context-param>
    <param-name>coherence-session-affinity-token</param-name>
    <param-value>!</param-value>
  </context-param>

  <context-param>
    <param-name>coherence-application-name</param-name>
    <param-value>coherenceApp</param-value>
  </context-param>
  <distributable/>
```

<br>

`coherence-servletcontext-clustered`, `coherence-enable-sessioncontext` : 서로 다른 App의 Context에서 생성된 Session 공유를 위하여 활성화 하는 것이나 구체적으로 살펴본것은 아니므로 추가 조사는 필요하다.

<br>

`coherence-session-cookie-path` : Tomcat의 경우 Cookie 저장 장소가 App의 Context-Root 아래 이므로, 기본값 /(root)인 Weblogic과 동일하게 맞추기 위함.

<br>

`coherence-scopecontroller-class` :`GlobalScopeController`설정 시 여러 Application이 Session을 공유하는데, `ApplicationScopeController` 를 쓰려는 경우 아래의 `coherence-application-name` 를 모든 곳에서 맞추어야 한다. 다만 WebLogic에서 동일하게 맞추었지만 Session 공유가 되지 않아 GlobalScope를 가져가게 되었다. 예상 되는 원인으로는, Weblogic App 측에서 `sharing-enabled` 와 같은 옵션의 테스트가 필요해보인다.

<br>

`coherence-session-affinity-token` : WebLogic은 Session 뒤에 `!<JVMID>` 를 추가하는데, 이는 Coherence에 실제 저장이 되지는 않는다. 다만 Browser cookie를 Tomcat이 이를 그대로 parse하여 올바른 Session 유지가 되지 않는다. Tomcat에서는 이 옵션을 통해 `!<JVMID>` 를 빼고 읽도록 한다.

<br>

WebLogic `web.xml` 의 경우, `coherence-session-affinity-token` 을 제외한 모든 설정이 동일하다.

<br>

이렇게 테스트 한 결과로, 이기종 MW간의 세션 공유가 확인되었다.


<br><br>


# 3. References

https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/administer-http-sessions/coherenceweb-context-parameters.html

https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/administer-http-sessions/using-coherenceweb-other-application-servers.html#GUID-B9C84803-E998-4988-8267-E84A6A916D6F

https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/administer-http-sessions/introduction-coherenceweb.html#GUID-4202FA59-819E-445C-8BCA-2648510914A3
