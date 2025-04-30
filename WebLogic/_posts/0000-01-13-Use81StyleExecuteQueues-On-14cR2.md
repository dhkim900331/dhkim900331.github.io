---
date: 2025-04-30 23:47:19 +0900
layout: post
title: "[WebLogic/Thread Management] Use81StyleExecuteQueues On 14cR2"
tags: [Middleware, WebLogic, Thread, Pool, WorkManager, Queue]
typora-root-url: ..
---

# 1. Overview

WebLogic 14.1.2 에서 Use81StyleExecuteQueues 옵션의 적용 방법에 대해 설명한다.

WebLogic 14.1.2 부터는.. 적용 방법 자체는 이전 WLS 버전과 거의 유사하지만 Remote Console 화면 구성상 메뉴들의 위치가 약간 다를 수 있다.


<br><br>


# 2. Descriptions

WLS 8.1 Version에서는 WLS에서 발생하는 모든 작업이 각각의 Queue를 가지고 처리되었다.

그러니까, WLS 내에서 `weblogic.kernel.default`, `weblogic.admin.HTTP`, `weblogic.admin.RMI` 와 같이 시스템에서 필요로 하는 작업이 저 이름의 Queue로 분배되어 처리되는 방식이었다.

<br>

이 Queue 라는 것은 고정된 최소/최대 스레드 갯수를 가지고 있기 때문에,

어느 한쪽의 부하량이 예기치 않게 많아 지는 경우, 다른쪽의 Queue가 Resource 확보에 어려움을 겪을 수 있다.

또한, 중요한 Queue를 위해 높은 가중치(스레드를 더 많이) 주었지만, Peak time이 아닌 경우에는 불필요한 자원 낭비도 발생하는 셈이다.

<br>

이후 WLS 9.1 Version 부터는, Queue로 분리하던 것을, 모두 하나의 공통된 Thread pool을 사용하도록 했다.

이것은 Self-tuning thread model 이라는 이름을 갖는다.

Self-tuing thread pool에는 WLS의 모든 작업이 여기서 처리되고, 사용자 Application 또한 여기서 처리된다.

<br>

Work Manager (이하 w/m) 은 단순히, 공통된 Self-Tuning Thread Pool을 어떻게 나누어서 작업 분배를 효율적으로 할 것인가에 대한 것이다.

<br>

`Monitoring Tree - 일정 잡기 - 작업 관리자 런타임` 을 보면, 매우 많은 Work Manager가 실행중인데,

각각의 Thread pool 을 보유한게 아니다.

모두 공통적인 큰 하나의 Thread pool를 공유하여 사용한다는 것이다.

<br>

사용자 App을 위한 w/m을 만들고, 독립적으로 사용하도록 부여하면, App에 부하가 높아져도 최소한의 처리량을 보장하도록 할 수 있다는 것이 Work Manager의 핵심으로 얻을 수 있는 사례 중 하나이다.

<br>

위는 Self-tuning thread pool model 과 Work Manager에 대한 간단한 설명이다.

이 포스팅에서 주요 설명은, Self-tuning thread pool model 을 비활성화 하고, 이전 WLS 8.1 때의 단일 Queue 모델을 사용하는 방법을 설명한다.

<br>

단일 Queue 모델로 전환하면, 모든 동작들이 별도의 Queue로 분리되고 사용자의 App 또한 반드시 잘 Tuning된 Queue를 가지게끔 해야 한다.


<br><br>


## 2.1 적용 방법

```sh
-Dweblogic.Use81StyleExecuteQueues=true
```

<br>

적용 시, 기동 시점 확인됨 (WLS 12cR2 도 동일한 로그)

```
<Notice> <Kernel> <BEA-000805> <The self-tuning thread pool is disabled. An execute queue will be created for each Work Manager definition.>
```

<br>

비적용 (기본값)

```
<Info> <WorkManager> <BEA-002900> <Initializing self-tuning thread pool.>
```


<br><br>


## 2.2 기본 동작 정리

### (1) Use81StyleExecuteQueues 활성화

`Use81StyleExecuteQueues` 활성화 시에, 모든 내부 Work Manager들이 별도의 Queue로 분리되어 실행된다.
-> w/m으 Thread pool을 생성한다고 이해하는게 아니라, Self-tuning thread pool 하나를 공통으로 쓰던 모든 프로세스들이 각자의 Thread pool을 갖는 'Queue' 로 전환한다는 것. 그러므로 위 내용 뒷부분은 지워야 할듯?

```
# Monitoring Tree - 일정 잡기 - 실행 대기열 런타임
...
default
weblogic.Rejector
weblogic.admin.RMI
weblogic.jep290.JEP290BroadcasterClient
weblogic.kernel.Non-Blocking
weblogic.kernel.System
weblogic.logging.DomainLogBroadcasterClient
weblogic.logging.LogBroadcaster
weblogic.socket.Muxer
weblogic.unicast.DispatchWorkManager
weblogic.unicast.ForwardingWorkManager
wl_oldBootStrap
wls-internal-parallel-configured-deployments-domain-activate
wls-internal-parallel-configured-deployments-domain-prepare
...
```

<br>

`weblogic.socket.Muxer` 는 원래 Queue이기 때문에, 옵션을 활성화 하지 않아도 항상 보여지는 항목이다.

<br>

이 옵션을 활성화 한다는 의미는, w/m 개념을 사용하지 않는다는 것이다.


<br><br>


### (2) Use81StyleExecuteQueues 비활성화

해당 옵션을 원래 기본값인, 비활성화를 하게 되면

`weblogic.socket.Muxer` 를 제외한 모든 처리는 Self-tuning Thread pool model 에서 처리된다.

`Monitoring Tree - 일정 잡기 - 작업 관리자 런타임` 에서는 각각 분리된 w/m 이름으로 처리량을 확인할 수 있다.

<br>

아래 Thread dump 에 예시는, weblogic.kernel.Default w/m 에서 처리되는 예시인데,

사용자 App 이 여기서 처리 된다.

```
"[ACTIVE] ExecuteThread: 'X' for queue: 'weblogic.kernel.Default (self-tuning)'"
```

<br>

[Overriding the Default Work Manager](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/14.1.2/cnfgd/self_tuned.html#GUID-10750E9F-E1E2-49FF-9218-76D1790C8B32) 설명에 따라, `default` w/m 을 재정의 할 수 있다.

`default` w/m 을 생성하고, 최소/최대 스레드를 생성 하고 할당하는 것이다.

`default` 재정의는 w/m 개념하에서 Self-tuning Thread pool 을 건드리는 것이다.

<br>

여전히 Thread dump 상에는 위와 같이 self-tuning Thread pool model 로 확인되지만, 재정의 방식이 적용되는 것으로 보이는데, 구체적으로 이후에 몇가지 테스트를 곁들여 증명해보도록 한다.

* default w/m 변경하여 반영되고 있는지 살펴보기 (최소/최대를 조절하면 exception이 있었음, 안하면 낮아도 발생..)

<br>

그러나, 시스템에 어떠한 부하가 어떤식으로 발생할지 모두 예측하기 어려운데, 이를 위해 [When to Use Work Managers](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/14.1.2/cnfgd/self_tuned.html#GUID-E08AEE2A-3EF9-4511-BA1B-34F845F9CDA8) 을 살펴보아야 할 것으로 보인다.

`default fair share (50)` 에 대한 정확한 이해를 하여 다시 서술하도록 하고, 예상되는 의미로는, "`default` w/m 을 여러 곳에서 공유하므로 더 넉넉히 설정해야 한다." 라는 것이다.


<br><br>


## 2.3 사용자 App에서 w/m 또는 Queue 사용

### (1) w/m 생성

`Edit Tree - 일정 잡기 - 작업 관리자` 에서 w/m 생성 (`default` 이름을 갖지 않도록)

최소/최대 스레드 제약 조건 `MinThreadsConstraint-0 (최소 30개), MaxThreadsConstraint-0 (최대 60개)` 생성 및 할당

인스턴스 재시작 후 적용됨


<br><br>


### (2) App에 적용

[wl-dispatch-policy](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/14.1.2/wbapp/weblogic_xml.html#GUID-56FAD250-E3FA-4DC0-8ACB-A50D7AE1AA1E) 으로 App에서 사용할 w/m 지정

```xml
<weblogic-web-app>
	...
	<wl-dispatch-policy>myWM-0</wl-dispatch-policy>
</weblogic-web-app>
```

<br>

또는 특정 Servlet 처리 건만 지정하려면 아래 참고 (이번 포스팅에서는 적용하지 않음)

[Example 3-2 Referencing the Work Manager in a Web Application](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/14.1.2/cnfgd/self_tuned.html#GUID-9C8BC85F-C61D-4DFA-A46E-9558ADF91735)


<br><br>


### (3) Thread dumping - Use81StyleExecuteQueues Enabled

w/m 과 Self-tuning thread model 이 비활성화 되기 때문에 `-Dweblogic.SelfTuningThreadPoolSizeMin=100 -Dweblogic.SelfTuningThreadPoolSizeMax=150` 옵션과 같은 설정은 적용되지 않는다.

즉 위 옵션 관계 없이, Queue 마다 사전 정의된 (혹은 내부적으로) Thread pool을 갖게 된다.

<br>

사용자 App 에서 독단적으로 사용할 `myWM-0` 을 최소/최대 : 25/50 으로 설정 하고,

Thread dump를 조사하면 아래와 같다.

<br>

```
"ExecuteThread: '0' for queue: 'default'"
"ExecuteThread: '0' for queue: 'weblogic.kernel.Non-Blocking'"
"ExecuteThread: '0' for queue: 'weblogic.kernel.System'"
"ExecuteThread: '0' for queue: 'weblogic.Rejector'"
"ExecuteThread: '0' for queue: 'weblogic.socket.Muxer'"
"ExecuteThread: '0' for queue: 'weblogic.logging.DomainLogBroadcasterClient'"
"ExecuteThread: '0' for queue: 'weblogic.logging.LogBroadcaster'"
"ExecuteThread: '0' for queue: 'ImageWorkManager'"
"ExecuteThread: '0' for queue: 'weblogic.admin.RMI'"
"ExecuteThread: '0' for queue: 'weblogic.unicast.DispatchWorkManager'"
"ExecuteThread: '0' for queue: 'weblogic.unicast.ForwardingWorkManager'"
"ExecuteThread: '0' for queue: 'ClusterMessaging'"
"ExecuteThread: '0' for queue: 'wl_oldBootStrap'"
"ExecuteThread: '0' for queue: 'RJVMMsgRoutingWM'"
"ExecuteThread: '0' for queue: 'FEJmsDispatcher'"
"ExecuteThread: '0' for queue: 'BEJmsDispatcher'"
"ExecuteThread: '0' for queue: 'weblogic.jep290.JEP290BroadcasterClient'"
"ExecuteThread: '0' for queue: 'JmsAsyncQueue'"
"ExecuteThread: '0' for queue: 'JTACoordinatorWM'"
"ExecuteThread: '0' for queue: 'OneWayJTACoordinatorWM'"
"ExecuteThread: '0' for queue: 'myWM-0'"
"ExecuteThread: '0' for queue: 'wls-internal-parallel-configured-deployments-domain-prepare'"
"ExecuteThread: '0' for queue: 'AppContainer:94c86279-6c48-4af7-ad47-752ef9f11636'"
"ExecuteThread: '0' for queue: 'wls-internal-parallel-configured-deployments-domain-activate'"
"ExecuteThread: '0' for queue: 'DataRetirementWorkManager'"
"ExecuteThread: '0' for queue: 'WlsManagementDelegatedRequestWorkManager'"
"ExecuteThread: '0' for queue: 'WlsManagementDispatchWorkManager'"
```

<br>

모두 첫 시작 번호 '0'으로 동일 한 것만 추출하였다.

각각의 Thread pool을 독립적으로 운영한다는 것을 알 수 있고, Thread 합계가 `188` 이었다.

위 항목들은 `Monitoring Tree - 일정 잡기 - 실행 대기열 런타임` 에서도 볼 수 있다.


<br><br>


사용자 Application(이하 App) 에서 `wl-dispatch-policy` 를 적용하지 않으면 `default` w/m 을 사용하기 때문에,

아래와 같이 `myWM-0`은 처리할 요청이 없어 `Object.wait()`

```sh
$ jstack -l <PID> > noQueue.txt
$ grep "myWM-0" noQueue.txt
	"ExecuteThread: '59' for queue: 'myWM-0'" ... in Object.wait() [0x00007f62bc897000]
	...
	"ExecuteThread: '0' for queue: 'myWM-0'" ... in Object.wait() [0x00007f62c03d2000]
```

<br>

App 에서 `Thread.sleep()` 을 처리해야 하는 부하를 받을 때 아래와 같이, `myWM-0`이 아닌 `default` w/m 에서 처리됨

```
"ExecuteThread: 'X' for queue: 'default'" ...
   java.lang.Thread.State: TIMED_WAITING (sleeping)
	at java.lang.Thread.sleep(Native Method)
	at jsp_servlet.__session._jspService(__session.java:101)
	at weblogic.servlet.jsp.JspBase.service(JspBase.java:35)
	...
	at weblogic.servlet.internal.ServletRequestImpl.run(ServletRequestImpl.java:1680)
	at weblogic.servlet.provider.ContainerSupportProviderImpl$WlsRequestExecutor.run(ContainerSupportProviderImpl.java:272)
	at weblogic.work.ExecuteRequestAdapter.execute(ExecuteRequestAdapter.java:21)
	at weblogic.kernel.ExecuteThread.execute(ExecuteThread.java:147)
	at weblogic.kernel.ExecuteThread.run(ExecuteThread.java:119)

   Locked ownable synchronizers:
	- None
```

<br>

wl-dispatch-policy 옵션을 적용하여 `myWM-0` 을 App에서 사용하도록 하고, 위의 스레드 덤프를 다시 추출하여 보면,

App에서 실행한 Thread.sleep() 코드로 인해 waiting 상태에 있는 몇개의 Thread는 `myWM-0` w/m 에서 실행중.

```sh
$ jstack -l <PID> > useQueue.txt
$ grep "myWM-0" useQueue.txt
	"ExecuteThread: '59' for queue: 'myWM-0'" ... waiting on condition [0x00007f62bc897000]
	"ExecuteThread: '58' for queue: 'myWM-0'" ... waiting on condition [0x00007f62bc998000]
	"ExecuteThread: '57' for queue: 'myWM-0'" ... waiting on condition [0x00007f62bca99000]
	"ExecuteThread: '56' for queue: 'myWM-0'" ... waiting on condition [0x00007f62bcb9a000]
	"ExecuteThread: '55' for queue: 'myWM-0'" ... waiting on condition [0x00007f62bcc9b000]
	...
	"ExecuteThread: '0' for queue: 'myWM-0'" ... in Object.wait() [0x00007f62c03d2000]
```

<br>

위의 실제 스레드 스택은 아래와 같다.

```
"ExecuteThread: 'X' for queue: 'myWM-0'" ... waiting on condition [0x00007f62bc897000]
   java.lang.Thread.State: TIMED_WAITING (sleeping)
	at java.lang.Thread.sleep(Native Method)
	at jsp_servlet.__session._jspService(__session.java:101)
	at weblogic.servlet.jsp.JspBase.service(JspBase.java:35)
	...
	at weblogic.servlet.internal.ServletRequestImpl.run(ServletRequestImpl.java:1680)
	at weblogic.servlet.provider.ContainerSupportProviderImpl$WlsRequestExecutor.run(ContainerSupportProviderImpl.java:272)
	at weblogic.work.ExecuteRequestAdapter.execute(ExecuteRequestAdapter.java:21)
	at weblogic.kernel.ExecuteThread.execute(ExecuteThread.java:147)
	at weblogic.kernel.ExecuteThread.run(ExecuteThread.java:119)

   Locked ownable synchronizers:
	- None

```


<br><br>


### (4) Thread dumping - Use81StyleExecuteQueues Disabled

WLS 는 `-Dweblogic.SelfTuningThreadPoolSizeMin=100 -Dweblogic.SelfTuningThreadPoolSizeMax=200` 옵션으로 최소/최대 스레드를 보장한다.

`myWM-0` 은 최소 25개. 최대 50개의 Thread 제약 조건을 갖는다.

<br>

최대 50개 보다 더 많은 부하를 요청하면, Thread dump 상태는 다음과 같다.

```
$ jstack -l <PID> | grep "\[ACTIVE\] ExecuteThread:" | wc -l
100
```

<br>

사용자 App 요청 + 모든 WLS 내부 동작이 최소 100개의 Thread 내에서 충족되므로, 더 이상의 Thread가 생성되지 않았다.

사용자 App은 더 많은 Thread 할당이 필요하지만, 이를 제한했으므로 그러한 것이다.


<br><br>


### (5) Monitoring

WLS 14.1.2 Remote Console(R/C) 과 이전 legacy Console(L/C) 과의 화면이 다르지만, 여기서는 R/C 로 설명한다.

<br>

`Monitoring Tree - 일정 잡기 - 실행 대기열 런타임 - myWM-0`

L/C 는 Monitoring이 해당 객체가 실행되는 인스턴스 페이지에 같이 있는데,

R/C 는 Monitoring 이 하나의 큰 Tree로 분류되었기 때문에 위 메뉴 경로가 된다.

위 메뉴 경로 끝점에서 `myWM-0` 을 사용하는 인스턴스별 스레드 통계를 알 수 있다.

<br>

`실행 대기열 런타임` 자체만 보면, `Use81StyleExecuteQueues` 옵션을 적용 했기 때문에, 모두 각기 Queue로 생성되어 있다.

```
AppContainer:ef987fae-2970-4d9b-879c-ad83bc3042cb
BEJmsDispatcher
ClusterMessaging
DataRetirementWorkManager
FEJmsDispatcher
ImageWorkManager
JTACoordinatorWM
...
weblogic.admin.RMI
weblogic.kernel.System
weblogic.socket.Muxer
..
```


<br><br>


### (6) etc

다음과 같은 config를 14.1.2 기준에서도 여전히 사용 가능하다.

<br>

```xml
...
  <server>
    <name>M1</name>
    <log>
      <rotation-type>byTime</rotation-type>
      <log-file-severity>Info</log-file-severity>
      <stdout-severity>Info</stdout-severity>
      <domain-log-broadcast-severity>Off</domain-log-broadcast-severity>
    </log>
	<execute-queue>
      <name>default</name>
      <queue-length>65536</queue-length>
      <thread-count>100</thread-count>
      <queue-length-threshold-percent>90</queue-length-threshold-percent>
      <threads-increase>0</threads-increase>
      <threads-maximum>400</threads-maximum>
      <threads-minimum>5</threads-minimum>
    </execute-queue>
    <use81-style-execute-queues>true</use81-style-execute-queues>
...
```

<br>

사용자 요청이 처리되는 `default` queue 에 많은 스레드를 보장하는 것.


<br><br>


## 2.4 Outcomes

- WebLogic 8.1 의 Execute Queues 를 사용할 수 있으며, 활성화 시에 w/m 항목들이 별도의 Queue로. 즉 각각의 Thread pool을 갖게 됨.
- `default` w/m 은 재정의 할 수 있다.
- 사용자가 w/m 을 생성할 수 있으나, App에서 사용하도록 지정하지 않으면 `default` w/m 을 사용한다.


<br><br>



# 3. References

내용에 포함됨
