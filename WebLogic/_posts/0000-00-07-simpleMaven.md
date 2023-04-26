---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] Maven 간단히 해볼까..?"
tags: [Middleware, WebLogic, Mavel]
typora-root-url: ..
---


# 1. 개요

Maven 아주 진짜 너무 간단하게..



# 2. Version 별 문서

[웹로직 11g 메이븐 문서](http://docs.oracle.com/cd/E17904_01/web.1111/e13702/maven_deployer.htm#DEPGD383)

[웹로직 12c 메이븐 문서](http://docs.oracle.com/middleware/1213/wls/WLPRG/maven.htm#WLPRG585)



# 3. Maven

Phase를 실행하면, Phase에 속한 모든 goal가 실행된다.

Table 3.1 Maven Lifecycle Phases은 maven의 기본 라이프 사이클 테이블을 보여주는 것이고,

Table 3.2 Common Mapping of Goals to Phases는 웹로직에서 사용하는 단계와 골 들을 보여주는 정보이다.



즉 메이븐에서 제공하는 Table3.1을 웹로직에 맞는 Table3.2로 오라클이 maven 프로젝트를 개발하였다.



```bash
# mvn package -DpomFile=pom.xml
```

> 위 명령은 package Phase를 실행 시키는 것으로써, 해당하는 Goal은 appc만 있다.
>
> (-DpomFile 생략시 현재 위치 pom.xml)



```bash
# mvn validate
```

> 위 명령은 validate Phase를 실행하고, ws-clientgen과 ws-wsdlc를 차례대로 실행한다.



```bash
# mvn weblogic:ws-wsdlc
```

> 위 명령은 validate Phase에서 ws-clientgen 을 실행시키지 않고 ws-wsdlc만 실행시키는 방법이다.



[여기 참고](http://addio3305.tistory.com/32)
