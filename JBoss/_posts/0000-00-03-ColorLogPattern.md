---
date: 2022-05-17 20:07:33 +0900
layout: post
title: "[JBoss] Color Log Pattern"
tags: [Middleware, JBoss, Log, Pattern]
typora-root-url: ..
---

<br># 1. 개요

JBOSS Log는 기본적으로, LogLevel 에 따른 Color Pattern 기능이 적용되어 있다.

해당 부분을 vi 에디터 등으로 보면, escape character 가 보여지는 현상이 있다.

어떤 내용인지 자세히 알아보고, 제거해보자.

<br>
# 2. 설명

* Log Pattern은 logging.properties와 standalone-ha.xml 에 속성 정의 되어 있다.

  기본적으로 `COLOR-PATTERN` 을 사용하는 Log 파일은 tail , cat 으로 보면 왜 그러한지 문제가 없지만

  vi 에디터 등으로 보면 다음과 같이 escape character가 눈에 띈다.

  제거 하고 싶다.

  ```
  ^[[0m^[[0m14:05:58,463 INFO ...
  ```

  

* configuration/logging.properties

```properties
formatter.PATTERN=org.jboss.logmanager.formatters.PatternFormatter
formatter.PATTERN.properties=pattern
formatter.PATTERN.pattern=%d{yyyy-MM-dd HH\:mm\:ss,SSS} %-5p [%c] (%t) %s%e%n

formatter.COLOR-PATTERN=org.jboss.logmanager.formatters.PatternFormatter
formatter.COLOR-PATTERN.properties=pattern
formatter.COLOR-PATTERN.pattern=%K{level}%d{HH\:mm\:ss,SSS} %-5p [%c] (%t) %s%e%n
```

> `formatter.*PATTERN` 형태로 여러가지를 정의하여, 적절할 때에 사용할 수 있다.
>
> `formatter.COLOR-PATTERN.pattern` 값의 %K{level} 이 문제가 된다.

<br>
* 위 파일의 여러 부분을 수정해도 , 기동하면 복구가 된다.

  확인 해보니, `standalone-ha.xml` 파일에 정의 되어 있어 기동시에 속성의 재정의 되기 때문이다.

<br>
* configuration/standalone*.xml (before)

```xml
        <subsystem xmlns="urn:jboss:domain:logging:8.0">
            <console-handler name="CONSOLE">
                <level name="INFO"/>
                <formatter>
                    <named-formatter name="COLOR-PATTERN"/>
                </formatter>
            </console-handler>
                ...
            <formatter name="PATTERN">
                <pattern-formatter pattern="%d{yyyy-MM-dd HH:mm:ss,SSS} %-5p [%c] (%t) %s%e%n"/>
            </formatter>
            <formatter name="COLOR-PATTERN">
                <pattern-formatter pattern="%K{level}%d{HH:mm:ss,SSS} %-5p [%c] (%t) %s%e%n"/>
            </formatter>
```

> 내 설정의 경우, STDOUT(위에서 `CONSOLE`) 로그 레벨은 `INFO` 이고, Log 포맷으로 `COLOR_PATTERN`을 사용한다.

<br>
* configuration/standalone*.xml (after)

```xml
        <subsystem xmlns="urn:jboss:domain:logging:8.0">
            <console-handler name="CONSOLE">
                <level name="INFO"/>
                <formatter>
                    <!--<named-formatter name="COLOR-PATTERN"/>-->
                    <named-formatter name="PATTERN"/>
                </formatter>
            </console-handler>
```

> 사용할 Log 포맷을 `PATTERN` 으로 변경한다.

<br>
* 재기동 이후 `CONSOLE` 로그는 아래처럼 나온다.

  ```
  2022-05-17 14:07:51,960 INFO
  ```

<br>
# 3. 참고문헌

https://access.redhat.com/documentation/en-us/red_hat_jboss_enterprise_application_platform/7.0/html/configuration_guide/logging_with_jboss_eap#configuring_log_formatters
