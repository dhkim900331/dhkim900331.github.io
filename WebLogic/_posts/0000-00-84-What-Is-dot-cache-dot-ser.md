---
date: 2024-01-31 13:27:29 +0900
layout: post
title: "[WebLogic] What Is .cache.ser"
tags: [Middleware, WebLogic, Deploy, Cache]
typora-root-url: ..
---

# 1. Overview
App 배포 시 META-INF 내부에 생성되는 .cache.ser 파일


<br><br>


# 2. Descriptions
App 배포 시 working-dir을 별도로 설정되어 있지 않다면, 다음과 같은 .cache.ser 파일이 생성된다.

- ${DOMAIN_HOME}/servers/M1/tmp/_WL_user/testApp/59ezjo/META-INF/.WL_internal/cache/testApp/.classinfos/**.cache.ser**
 - ${APP-ROOT}/META-INF/.WL_internal/cache/testApp/.classinfos/**.cache.ser** 

<br>

.cache.ser 파일은, 배포되는 Application에서 Annotation scan을 수행하고,

그 결과(class list; metadata)를 직렬화하여 기록한 캐시 파일이다.

인스턴스 재기동 시에 .cache.ser 를 다시 읽어 들여 성능을 높이고자 사용된다.

<br>

.cache.ser 파일은 다음과 같은 경우에 업데이트 된다. (Weblogic 12.2.1.4 버전 기준으로 확인됨)

- App 배포 시 .cache.ser 은 다음의 경로에 생성됨
  - ${DOMAIN_HOME}/servers/M1/tmp/_WL_user/testApp/59ezjo/META-INF/.WL_internal/cache/testApp/.classinfos/.cache.ser
  - ${APP-ROOT}/META-INF/.WL_internal/cache/testApp/.classinfos/.cache.ser 

<br>

- 인스턴스 재기동 시에 다음의 경로만 업데이트됨
   - ${DOMAIN_HOME}/servers/M1/tmp/_WL_user/testApp/59ezjo/META-INF/.WL_internal/cache/testApp/.classinfos/.cache.ser

<br>

- App 정지 시 두 경로 변경 사항 없음

<br>

* App 배포 삭제 시 다음의 경로 삭제됨
   - ${DOMAIN_HOME}/servers/M1/tmp/_WL_user/testApp/59ezjo/META-INF/.WL_internal/cache/testApp/.classinfos/.cache.ser


<br><br>


# 3. References

**OutOfMemoryError Occurs When Deploying a WAR File Due to Corrupted Cache.ser File ([Doc ID 2293479.1](https://mosemp.us.oracle.com/epmos/faces/ui/km/DocumentDisplay.jspx?id=2293479.1))**
