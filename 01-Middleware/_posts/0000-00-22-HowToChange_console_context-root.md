---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[Middleware/WebLogic] consoleapp context-root 다르게 변경 방법"
tags: [Middleware, WebLogic]
typora-root-url: ..
---


# 1. 개요

consoleapp context-root 다르게 변경 방법



# 2. 설명

## 2.1 consoleapp 다른 이름으로 복제

```sh
cp ${WL_HOME}/server/lib/consoleapp ${WL_HOME}/server/lib/consoleapp_gtplus
```



## 2.2 consoleapp_gtplus context-root 변경

```sh
# ${WL_HOME}/server/lib/consoleapp_gtplus/META-INF/application.xml 파일 편집
... skip ...

<module>
    <web>
      <web-uri>webapp</web-uri>
      <context-root>console_gtplus</context-root>
    </web>
  </module>
</application>
```

> consolehelp 모듈은 지우고, console 모듈의 context-root를 변경.



## 2.3 consoleapp_gtplus 를 AdminServer에 deploy

http://ip:port/console_gtplus 접속



## 2.4 기타

어드민 콘솔 페이지가, http://../console  ,  http://../console_gtplus 두개 이므로..

기존 console url을.. http://../console_gftplus 등으로 유사하게 바꿀 필요가 있어 보입니다.
