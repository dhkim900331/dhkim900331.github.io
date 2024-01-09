---
date: 2022-05-17 20:07:33 +0900
layout: post
title: "[JBoss] Jconsole을 이용하여 JMX 연결하기"
tags: [Middleware, JBoss, Jmx, Jconsole, Mbean]
typora-root-url: ..
---


# 1. 개요

Windows 환경에서 jconsole을 이용하여 JBoss EAP 7.X 의 JMX 모니터링을 위해 연결 방법을 설명한다.

X-Windows 환경의 Linux 에서도 가능하지만, Windows 에서 해보니 문법상 특이점이 많아 Windows 로 가이드한다.
{{ site.content.br_small }}
# 2. 설명

* 우선 나는, JBoss EAP 7.X 버전을 기준으로 삼기 때문에, `jboss-cli-client.jar` 가 필요하여, 설치된 Engine 에서 가져왔다.

* Windows 에서 스크립팅을 자주 해보지 않아, 아래 스크립트를 짜고 실행할 때

  정말 많은 시행착오를 겪었다.

  특히나, Windows에서 path 부분마다 double quotes(`"`)로 묶는 것이 습관화 되어 있어야 하는 것 같다.

  ```shell
  @Echo off
  set JAVA_HOME=
  set CLASSPATH=
  set JAVA_HOME=C:/Program Files/Java/jdk1.8.0_271
  set CLASSPATH=%JAVA_HOME%/lib/jconsole.jar
  set CLASSPATH=%CLASSPATH%;%JAVA_HOME%/lib/tools.jar
  set CLASSPATH=%CLASSPATH%;C:/Users/USER/Downloads/jboss-client.jar
  echo %JAVA_HOME%
  echo %CLASSPATH%
  
  "%JAVA_HOME%/bin/jconsole" -debug -J-Djava.class.path="%CLASSPATH%"
  @rem "%JAVA_HOME%/bin/jconsole" -debug -J-Djava.class.path="%CLASSPATH%" service:jmx:remote+http://ip:port
  ```

  > `1~9 Line` 환경변수를 설정하는 단계
  >
  > `11 Line` jconsole 실행 단계
  >
  > `12 Line` 조금 중요한 부분인데, 맨 뒤에 connect URL을 적으면 자동으로 연결하지만 ID/PWD 부분은 제공하지 않아 에러가 발생한다. 해당 부분은, 방법은 있어 보이나 일반적인(우리가 간편하게 하고 싶어하는) ID/PWD 제공방식과는 달라 아직 방법을 모르겠다.
{{ site.content.br_small }}
* jconsole 화면에서 URL과 ID/PWD 로 접속을 시도한다.

[JconsoleConnect_1](/../assets_copy_1/posts/images/JBoss/JconsoleConnect/JconsoleConnect_1.png)* Debug 옵션에 의해, Debug Log 윈도우와 함께 정상적으로 접속이 되었다.

[JconsoleConnect_2](/../assets_copy_1/posts/images/JBoss/JconsoleConnect/JconsoleConnect_2.png)# 3. 참고문헌

https://access.redhat.com/solutions/2435131

https://access.redhat.com/solutions/962343
