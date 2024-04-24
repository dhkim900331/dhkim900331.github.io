---
date: 2024-04-24 17:36:33 +0900
layout: post
title: "[WebLogic/JDBC] JDBC Driver Certifications"
tags: [Middleware, WebLogic, JDBC, Certification]
typora-root-url: ..
---

# 1. Overview
Oracle JDBC Driver 의 Certifications 문서 확인 방법에 대한 설

{{ site.content.br_big }}

# 2. Descriptions
[Frequently Asked Questions](https://www.oracle.com/database/technologies/faq-jdbc.html)에 JDBC Driver와 JDK 그리고 Oracle DB 버전간의 상호 호환성을 위한 페이지가 있다.



**Which version of JDBC drivers are supported ?**

지원되는 JDBC 버전들에 대한 소개.



**What is the JDBC and RDBMS interoperability matrix or the certification matrix?**

JDBC driver와 Oracle DB 버전간의 인증 테이블.

JDBC driver의 최신 기능 활용을 위해서는 Oracle DB 버전과 동일하거나, 더 높은 버전을 권고

> 예시. JDBC 19.X 는 Oracle DB 19.X 와 인증됨



**What are the Oracle JDBC releases Vs JDK versions?**

Oracle DB 버전과 사용이 권장되는 각 JDBC Jar files 소개.

각 JDBC Jar files 들에서 최신 JDK 버전을 사용하는 것을 권장.

시스템에서 사용하는 JDK 버전에 따라 JDBC Jar file을 선택.



> 예로, Oracle DB 19.X는 아래와 같은데, ojdbc8.jar 를 사용할 경우 JDK17 을 권장 한다는 의미.
>
> 하지만, 시스템에서 JDK 11을 사용한다면, 우선 둘 다 사용 가능.
>
> * ojdbc10.jar with JDK11, JDK17, and JDK19
> * ojdbc8.jar with JDK8, JDK11, and JDK17



**What are the Oracle JDBC releases Vs JDBC specifications?**

JDBC Driver와 JDBC specification 간의 매핑 소개.



> 예로, Oracle DB 19.X는 아래와 같은데, JDBC Spec에 따라, JDBC Jar file의 선택지가 나뉜다.
>
> * JDBC 4.3 in ojdbc10.jar
> * JDBC 4.2 in ojdbc8.jar



**Are the Oracle JDBC drivers certified against OpenJDK?**

Oracle JVM(Sun JVM)에서만 호환 인증되었으며, OpenJDK 또는 다른 JVM(IBM 등)은 그렇지 않음.

물론 사용할 수 있지만, Oracle Suppot 지원을 받을 때, Oracle JVM 에서도 재현되는지 증명해야 될 수 있음.



고객이 Oracle JDK 11.X, Oracle DB 19.X 인 경우

What are the Oracle JDBC releases Vs JDBC specifications? 에 따라 살펴보면

Oracle DB 19.x 는 JDBC 4.3 in ojdbc10.jar , JDBC 4.2 in ojdbc8.jar 두 선택지가 있다.



What are the Oracle JDBC releases Vs JDK versions? 에 따라 살펴보면

Oracle DB 19.x 는 ojdbc10.jar(with JDK11, JDK17, JDK19) 와 ojdbc8.jar(with JDK8, JDK11, and JDK17) 가 있다.

JDK11 은 둘 다 지원되므로, 고객이 원하는 대로 ojdbc8.jar 또는 ojdbc10.jar 를 사용하면 된다.



{{ site.content.br_big }}

# 3. References

[Frequently Asked Questions](https://www.oracle.com/database/technologies/faq-jdbc.html)

https://half.tistory.com/20
