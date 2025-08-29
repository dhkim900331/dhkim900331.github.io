---
date: 2025-01-02 23:04:36 +0900
layout: post
title: "[WebLogic/Deployment Plan] How To Override Element In DD Of Application"
tags: [Middleware, WebLogic, Plan, Deployer, Override]
typora-root-url: ..
---

# 1. Overview

Application 배포 설명자 파일 (Deployment Descriptor) 의 구성 요소를 외부에서 변경하기 위한, Deployment Plan 의 간단한 사용 예시.

해당 방식을 사용할 시, 개발자에게 WebLogic의 구성 요소의 종속성을 탈피할 수 있다.


<br><br>

<br>

# 2. Descriptions

다음의 `defaultApp`은

```sh
$ tree /sw/app/defaultApp
/sw/app/defaultApp
├── custom-error
│   └── 404.html
├── META-INF
└── WEB-INF
    ├── weblogic.xml
    └── web.xml

3 directories, 3 files
```

<br>

`web.xml` 에 다음으로 지정되어 있다.

```xml
<web-app>
 <error-page>
  <error-code>404</error-code>
  <location>/error/404.html</location>
 </error-page>
</web-app>
```

<br>

`defaultApp`에 존재하지 않는 Page를 호출하면, `/error/404.html`이 보여진다.

<br>

다음을 `/sw/app/plan/plan.xml` 으로 저장한다.

```xml
<deployment-plan xmlns="http://xmlns.oracle.com/weblogic/deployment-plan">
 <application-name>plan</application-name>
  <variable-definition>
   <variable>
    <name>errorCode404</name>
    <value>404</value>
   </variable>

   <variable>
    <name>errorPage404</name>
    <value>/custom-error/404.html</value>
   </variable>
  </variable-definition>

 <module-override>
  <module-name>defaultApp</module-name>
  <module-type>war</module-type>
  <module-descriptor external="true">
   <root-element>web-app</root-element>
   <uri>WEB-INF/web.xml</uri>

   <variable-assignment>
    <name>errorCode404</name>
    <xpath>/web-app/error-page[error-code='404']/error-code</xpath>
   </variable-assignment>

   <variable-assignment>
    <name>errorPage404</name>
    <xpath>/web-app/error-page[error-code='404']/location</xpath>
   </variable-assignment>
  </module-descriptor>
 </module-override>
 <config-root>/sw/app/plan</config-root>
</deployment-plan>
```

<br>

`defaultApp`이 이미 WLS에 배포가 되어 있던, 신규 배포를 하던간에 `plan.xml`을 다음의 명령어로 적용할 수 있다.

```sh
java weblogic.Deployer \
 -adminurl t3://<ADMIN_URL> \
 -user <USERNAME> -password <PASSWORD> \
 -deploy -name defaultApp \
 -source /sw/app/defaultApp \
 -plan /sw/app/plan/plan.xml
```

<br>

이제, defaultApp은 HTTP 404 Found 시에 `/custom-error/404.html` 을 보여준다.


<br><br>

<br>

# 3. References

[4 Configuring Applications for Production Deployment](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/depgd/config.html)
