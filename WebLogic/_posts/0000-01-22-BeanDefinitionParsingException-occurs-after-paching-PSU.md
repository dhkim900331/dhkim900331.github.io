---
date: 2025-11-18 13:53:50 +0900
layout: post
title: "[WebLogic/Spring] BeanDefinitionParsingException occurs after patching PSU"
tags: [Middleware, WebLogic, PSU, Bean, Spring]
typora-root-url: ../..
---

# 1. Overview

WebLogic 12.2.1.4 에 25년 7월 PSU 패치를 적용 후, 변경사항이 없던 고객 Spring App에서 초기화 시점에 `BeanDefinitionParsingException` 가 발생하였다.

<br><br>


# 2. Descriptions

발생한 에러의 원문

```
11:14:38,274 INFO  [XmlBeanDefinitionReader] Loading XML bean definitions from ServletContext resource [/WEB-INF/applicationContext.xml]
11:14:38,520 INFO  [XmlBeanDefinitionReader] Loading XML bean definitions from URL [zip:...jar!/META-INF/beans.xml]
11:14:38,543 INFO  [XmlBeanDefinitionReader] Loading XML bean definitions from URL [zip:...jar!/META-INF/beans.xml]
11:14:38,574 INFO  [XmlBeanDefinitionReader] Loading XML bean definitions from URL [jar:file:${ORACLE_HOME}/oracle_common/modules/org.glassfish.jersey.ext.cdi.jersey-cdi1x-servlet.jar!/META-INF/beans.xml]
11:14:38,592 ERROR [ContextLoader] Context initialization failed
org.springframework.beans.factory.parsing.BeanDefinitionParsingException: Configuration problem: Failed to import bean definitions from URL location [classpath*:META-INF/beans.xml]
Offending resource: ServletContext resource [/WEB-INF/applicationContext.xml]; nested exception is org.springframework.beans.factory.xml.XmlBeanDefinitionStoreException: Line 43 in XML document from URL [jar:file:${ORACLE_HOME}/oracle_common/modules/org.glassfish.jersey.ext.cdi.jersey-cdi1x-servlet.jar!/META-INF/beans.xml] is invalid; nested exception is org.xml.sax.SAXParseException; lineNumber: 43; columnNumber: 9; cvc-elt.1.a: Cannot find the declaration of element 'beans'.
	...
Caused by: org.springframework.beans.factory.xml.XmlBeanDefinitionStoreException: Line 43 in XML document from URL [jar:file:${ORACLE_HOME}/oracle_common/modules/org.glassfish.jersey.ext.cdi.jersey-cdi1x-servlet.jar!/META-INF/beans.xml] is invalid; nested exception is org.xml.sax.SAXParseException; lineNumber: 43; columnNumber: 9; cvc-elt.1.a: Cannot find the declaration of element 'beans'.
Caused by: org.xml.sax.SAXParseException; lineNumber: 43; columnNumber: 9; cvc-elt.1.a: Cannot find the declaration of element 'beans'.
	at com.sun.org.apache.xerces.internal.util.ErrorHandlerWrapper.createSAXParseException(ErrorHandlerWrapper.java:204)
	at com.sun.org.apache.xerces.internal.util.ErrorHandlerWrapper.error(ErrorHandlerWrapper.java:135)
	at com.sun.org.apache.xerces.internal.impl.XMLErrorReporter.reportError(XMLErrorReporter.java:396)
	...
```


<br><br>


위 로그에서 포인트는, Exception이 발생한 지점이 Oracle 공용 모듈(`oracle_common`) 에 있는 `org.glassfish.jersey.ext.cdi.jersey-cdi1x-servlet.jar` 안에 있는 `beans.xml` 에 있다는 것이다.

<br>

분석 결과,

PSU 패치 후 위 Jar 파일에 Sample 용도의 `beans.xml`이 들어왔고,

고객의 Spring Application의 bean 검색 범위가 다음처럼 광범위하게 설정되어 있었다.

```xml
<import resource="classpath*:META-INF/beans.xml" />
<import resource="classpath*:META-INF/beans_${appServerType}.xml" />
<import resource="classpath*:META-INF/beans_${serverMode}.xml" />
<import resource="classpath*:META-INF/beans_node_${nodeId}.xml" />
<import resource="classpath*:META-INF/beans_${serverMode}_${nodeId}.xml" />
```

<br>

두번째 라인부터는 고객 환경에서만 유효하도록 환경변수값에 의존적이지만,

첫번째 라인에 의해 로드 되어 있는 모든 Jar의 `beans.xml` 을 가리키고 있다.

<br>

결국 고객의 Spring App은 Spring Beans만을 대상으로 해야 하는데,

PSU 패치 이후 들어온 CDI Jar 내 CDI Beans를 포함하게 되어 Parsing 에러가 발생하였다.

<br>

해결을 위해, Spring Bean 검색 범위를 광범위하게 설정하지 않고, Spring App내로 명확하게 해야 한다.


<br><br>


# 3. References

**BeanDefinitionParsingException occurs after paching PSU (Doc ID 3108674.1)**
