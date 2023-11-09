---
date: 2023-03-27 08:46:20 +0900
layout: post
title: "[WebLogic] Force and Graceful shutdown"
tags: [Middleware, WebLogic, Shutdown, Force, Graceful]
typora-root-url: ..
---

# 1. 개요

WebLogic 14c 기준으로 Force 및 Graceful Shutdown 에 대해서 살펴본다.

WebLogic 14c 기준으로 Force shutdown, Graceful Shutdown 에 대해서 살펴본다.

상세한 내용을 모두 다 옮기지는 않고, 주요내용만 살펴본다.



# 2. Force shutdown

[Diagram of the Server Life Cycle](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/start/server_life.html#GUID-81FFFD04-1CA3-4271-B78F-AA4C748CEC02) 에서 전체적인 State flow를 확인할 수 있다.

[Force Shutdown의 Flow](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/start/server_life.html#GUID-135B6C78-3DB0-4ECC-A22A-6ADCCD6CE927)를 확인할 수 있다.



* RUNNING > FORCE_SUSPENDING > ADMIN > STANDBY > SHUTDOWN
  * FORCE_SUSPENDING : 진행중인 작업(in-flight work)를 강제 종료
  * ADMIN : 관리자 및 접근가능한 Role을 가진 사용자만 Admin Console, App 및 기타 Resource에 접근 가능.
  * STANDBY : Admin Console/Port만 열려 있고, 요청 처리 하지 않음. Lifecycle command만 처리 가능.
  * SHUTDOWN : Instance가 종료되어 있는 상태



# 3. Graceful Shutdown

[Graceful Shutdown의 Flow](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/start/server_life.html#GUID-9E0CCA04-86F2-463B-83F4-B763327EE165)를 확인할 수 있다.

* RUNNING > SUSPENDING > ADMIN > SHUTTING_DOWN > SHUTDOWN
  * SUSPENDING : 진행중인 작업(in-flight work)가 완료되기를 기다림. 신규 요청(new session)은 받지 않음.
  * ADMIN : 상동
  * SHUTTING_DOWN : Admin , App 요청 처리하지 않음. 기타 Resource 중지
  * SHUTDOWN : 상동



# 4. Shutdown command

Shutdown WLST command 를 살펴본다.



[shutdown command](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wlstc/reference.html#GUID-B3EAB96F-A159-4D69-A1A4-1965FD1D5458)의 주요 부분만 살펴본다.

* `shutdown([name], [entityType], [ignoreSessions], [timeOut], [force], [block], [properties], [waitForAllSessions])`
  * ignoreSessions
    * true : 즉시 모든 HTTP session 제거
    * false : HTTP session timeout 후에 제거
  * timeOut : 해당 sec안에 종료되지 않으면 강제 종료 돌입
  * force : 즉시 강제 종료 여부
  * waitForAllSessions
    * true : shutting down 되는 동안 모든 HTTP Session이 완료될 때까지 기다린다.
    * false : non-persisted HTTP Session이 완료될 때까지 기다린다.



> persisted, non-persisted 기준에 대한 설명이 없다
>
> HTTP 1.0,1.1 Spec에서 언급하는 것을 말하는 것인지 사용자 HTTP Session을 말하는 것인지 더 정확하게 확인이 필요하다.
>
> ignoreSessions와 waitForAllSessions가 모호하기 때문이다.



## 4.1 Force Shutdown

즉시 Instance의 모든 작업을 완료하고, 강제 종료를 위해서는

`shutdown(name="<instance>", force="true")`



## 4.2 Graceful Shutdown

Instance에서 처리되고 있는 사용자의 모든 작업을 완료하고,

잔존하는 HTTP Session의 session-timeout으로 invalidate 되면 종료한다.

Suspending State일 때, 신규 사용자는 HTTP Session이 없으므로 HTTP 503 을 Return 받는다.

`shutdown(name="<instance>", force="false", ignoreSessions="false")`



Graceful shutdown 시에 WebLogic Log를 살펴보면,

SUSPENDING State,

```
<Notice> <WebLogicServer> <BEA-000365> <Server state changed to SUSPENDING.>
```



App에 HTTP Session 남아 있다고 알림

```
<Notice> <HTTP> <BEA-101277> <Web application(s) /CustomerApp has 1 non-replicated session(s) respectively.>
```



HTTP Session의 복제본이 없으므로 App에서 설정한 sesson-timeout 60sec 동안 기다림.

실제로, Cluster 환경이 아니므로 이렇게 지연될 수 있다.

Cluster 환경이라면 HTTP Session의 복제본이 JSESSIONID에서 확인되어 즉시 종료된다.

```
<Notice> <HTTP> <BEA-101275> <Server has detected non-replicated sessions while SUSPENDING. Server will wait for non-replicated sessions to either become invalidated or timed out or will wait until a secondary is chosen using the lazy process (meaning if a session does not have a secondary, the server waits until the next request to create the secondary). The current timeout value is 60 seconds. To terminate non-replicated sessions immediately, use the FORCESHUTDOWN option.>
```



여전히 Session이 남아 있음

```
<Notice> <HTTP> <BEA-101276> <Web application(s) /CustomerApp still have non-replicated sessions after 0 minutes of initiating SUSPEND. Waiting for non-replicated sessions to finish.>
<Notice> <HTTP> <BEA-101276> <Web application(s) /CustomerApp still have non-replicated sessions after 1 minutes of initiating SUSPEND. Waiting for non-replicated sessions to finish.>
```



Session이 timeout 으로 제거되어, 종료 수행

```
<Notice> <HTTP> <BEA-101278> <There are no active sessions. The Web service is ready to suspend.>
<Notice> <WebLogicServer> <BEA-000365> <Server state changed to ADMIN.>
<Notice> <WebLogicServer> <BEA-000365> <Server state changed to SHUTTING_DOWN.>
<Info> <WebLogicServer> <BEA-000238> <Shutdown has completed.>
```



[Shutdown process에서 Web container](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/start/server_life.html#GUID-8CD24F14-D3B1-40E3-A118-123FB19985B2)의 설명과 같이, new request는 rejected(HTTP 503)되고, old request만 처리된다.



# 4. References

[Understanding Server Life Cycle](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/start/server_life.html#GUID-2C1BF849-3578-4BB8-A929-B491C10FF365)

[Life Cycle Commands with WLST](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wlstc/reference.html#GUID-C65FED72-3C65-4444-8413-BC24A2987AAF)

[Persisted and non-Persisted HTTP](https://www.webnms.com/snmp/help/gettingstarted/technology_overview/techoverview_http.html)
