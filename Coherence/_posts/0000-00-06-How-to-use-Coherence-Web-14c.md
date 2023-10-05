---
date: 2023-04-25 09:00:13 +0900
layout: post
title: "[Coherence/Web] How to use Coherence Web 14c"
tags: [Coherence, Web, Manual, Use]
typora-root-url: ..
---

# 1. 개요

[How-to-install-Coherence-Web-14c](How-to-install-Coherence-Web-14c) 에서 설치를 완료 했다.

여기서는 실제 환경에서 쓰일 수 있게 다음의 항목들을 확인한다.

- Death Detection
- F/W
- Session Reaper Thread Tuning

<br>
# 2. Death Detection

[Configuring Death Detection](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/develop-applications/setting-cluster.html#GUID-FE185358-AE38-4436-9179-73E0D4CAAD13) 을 하여, ClusterMember 이탈 여부를 확인한다.

<br>
## 2.1 TCP-RING

Member들은 하나의 Ring으로 연결된다.

25초 동안 HeartBeat 응답을 주지 않은 Member를 5회 실시하여, Member를 제거한다.

`java.net.InetAddress.isReachable` 를 시도하며, 이 Method는 Process가 아니라 Host에 Port 7(Echo)를 전송하여 응답을 받으려고 시도한다.

Port 7(Echo) 가 방화벽에 예외 처리 되어 있어야 한다.

listen-backlog는 이러한 HeartBeat 감지를 받을 때, 최대 backlog 로 보여진다.

<br>
```xml
    <tcp-ring-listener>
      <enabled>true</enabled>
      <ip-timeout system-property="coherence.ipmonitor.pingtimeout">25s</ip-timeout>
      <ip-attempts>5</ip-attempts>
      <listen-backlog>10</listen-backlog>
    </tcp-ring-listener>
```

<br>
최대 2분 5초 동안 응답을 하지 않은 Member가 발견되면 아래와 같이 Logging 된다.

```
tmb://10.65.34.245:9003.34707 initiating connection migration with tmb://10.65.34.245:9001.43859 after 2m5s ack timeout health(read=true, write=false), receiptWait=null: peer=tmb://10.65.34.245:9001.43859
```

9003 Port Member가 응답하지 않는다.

<br>
tcp-ring-listener 를 사용하지 않으면, 인스턴스가 Shutdown 될 시에 매우 늦게 감지가 된다.

반드시 사용한다.

> tcp-ring-listener false 시에 Member shutdown 을 하면 2분 5초 뒤에 파악이 된다.

<br>
## 2.2 HeartBeat

Cluster Member들 간에는 HeartBeat를 주고 받는다.

이 HeartBeat 간격은 기본값 1초 이며, Member가 많을 경우 Traffic이 증대할 것이며, 평소 Network 신뢰성이 높은 경우, 불필요하게 많은 Traffic을 유발하지 않도록 설정값을 변경하는 것도 고려해볼 만 하다.

<br>
문서 상에는, HeartBeat를 매 간격마다 보내지 않고, 내부 평가 프로세스에 따라 그러하다고 하는데 어떤 프로세스를 가지는지는 문서상에 보이지 않는다.

<br>
```xml
    <packet-publisher>
      <packet-delivery>
        <heartbeat-milliseconds>5000</heartbeat-milliseconds>
      </packet-delivery>
    </packet-publisher>
```

<br>
# 3. Firewall

* Cluster Port (Default 7574) 는 Multicast/Unicast 에서 모두 사용되고, UDP/TCP 로 쓰인다. Coherence에 Proxy를 구성하고, Client에서 Naming Service로 Proxy를 이용할 때 Name을 검색하는 Port.
  * Cluster Port가 Unicast 에서 사용되는 시기는, WKA(Well-Known-Addresses) 를 사용할 때다. WKA 멤버를 찾을 때, Cluster Port를 사용한다.

* Death Detection 을 위해 TCP 7 (Echo port)를 사용한다.
* 위 외에 메뉴얼상 필요한 Port는 없고, Member간의 통신 방식에 사용하는 Port를 열어주면 된다.

<br><br>
# 4. MBean Monitoring

다음 옵션을 추가하여, WLST MBean 을 Monitoring 할 수 있다.

```sh
-Djavax.management.builder.initial=weblogic.management.jmx.mbeanserver.WLSMBeanServerBuilder
```

<br>
MBean Coherence Tree를 찾아가려면, 아래와 같은 핵심코드가 필요하다.

```sh
# connect to server
connect(username, password, url)
    
# get LocalMemberId
cd('custom:/Coherence/Coherence:type=Cluster')
localMemberId = str(get('LocalMemberId'))
    
# change dir to cohSessionApp
cd('custom:/Coherence/Coherence:type=WebLogicHttpSessionManager,nodeId=' + localMemberId + ',appId=<app-name>')
```

<br><br>
# 5. JMX Monitoring

[Allowing Remote Access to Oracle Coherence MBeans](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/manage/using-jmx-manage-oracle-coherence.html#GUID-844DAAE6-6F00-4B15-AA44-47C3F595A6C5)

```sh
-Dcoherence.management=all
-Dcoherence.management.remote=true
-Dcom.sun.management.jmxremote.port=<JMX port>
-Dcom.sun.management.jmxremote.authenticate=false
-Dcom.sun.management.jmxremote.ssl=false
-Djava.rmi.server.hostname=wls.local
```

<br>
Coherence Cluster를 사용하는 WebApp 이 배포된 Managed Coherence Server에 설정 후 JConsole을 통해 MBean 을 읽을 수 있다.

<br>
<img src="/../assets/posts/images/How-to-use-Coherence-Web-14c/image-20230424145943477.png" alt="image-20230424145943477" style="zoom: 33%;" />

<br>
Coherence - WebLogicHttpSessionManager - \<Member ID> - \<Web App> - Attributes 에서 처리되는 Session 통계를 알 수 있다.

<br>
Member ID는 Node의 각 Attributes 에서 MemberName이나 ProcessName 으로 획득하면 수월하겠다.

![image-20230424151956264](/../assets/posts/images/How-to-use-Coherence-Web-14c/image-20230424151956264.png)

<br>
예시 화면에서는 Unique 하게 되어 있지 않은데, Operational Override File에서 지정하면 된다.

```xml
      <process-name system-property="coherence.process">process_base_domain</process-name>
      <member-name  system-property="coherence.member">member_base_domain</member-name>
```

<br><br>
# 6. Session Reaper Thread

App 에서 생성된 HTTP Session은 timeout-secs 만큼 유효하다.

invalidation-internal-secs 마다 All HTTP Session을 Scan하여 invalid 한 session을 삭제하여 Memory를 확보한다.

<br><br>
## 6.1 Ready For Test

### (1) WLST

[4. MBean Monitoring](#h-4-mbean-monitoring) 을 이용하여 아래의 Code를 작성하고,

Session 부하를 발생 시킬 때, Reaper Thread가 어떻게 동작하는지 알아본다.

<br>
WLST MBean code

```py
java -Djava.security.egd=file:/dev/urandom weblogic.WLST << EOF
# import
import os
import sys
import time

# log file
fo = open("/tmp/coh.log", "wb+")

# connection information
username = 'weblogic'
password = 'weblogic1'
url = 'wls.local:8002'

# connect to server
connect(username, password, url)

# get LocalMemberId
cd('custom:/Coherence/Coherence:type=Cluster')
localMemberId = str(get('LocalMemberId'))

# change dir to cohSessionApp
cd('custom:/Coherence/Coherence:type=WebLogicHttpSessionManager,nodeId=' + localMemberId + ',appId=cohSessionAppcohSessionApp')

sleep_in_ms = 5000
for idx in range(0, 200):
  ###### print MBeans ######
  ### Attr to Var ###
  # Reaper Cycle
  LastReapCycle = str(get('LastReapCycle'))
  NextReapCycle = str(get('NextReapCycle'))
  
  # Reap Duration
  AverageReapDuration = str(get('AverageReapDuration'))
  LastReapDuration = str(get('LastReapDuration'))
  MaxReapDuration = str(get('MaxReapDuration'))
  
  # Reaped Sessions
  AverageReapedSessions = str(get('AverageReapedSessions'))
  MaxReapedSessions = str(get('MaxReapedSessions'))
  ReapedSessions = str(get('ReapedSessions'))
  ReapedSessionsTotal = str(get('ReapedSessionsTotal'))
  
  # Sessions
  SessionUpdates = str(get('SessionUpdates'))
  OverflowUpdates = str(get('OverflowUpdates'))
  
  ### Var to Log ###
  dm = " | "
  writeLogData = ""
  
  # Print Init Header
  if idx == 0:
    writeLogData += "LastReapCycle" + dm
    writeLogData += "NextReapCycle" + dm
    
    writeLogData += "AverageReapDuration" + dm
    writeLogData += "LastReapDuration" + dm
    writeLogData += "MaxReapDuration" + dm
    
    writeLogData += "AverageReapedSessions" + dm
    writeLogData += "MaxReapedSessions" + dm
    writeLogData += "ReapedSessions" + dm
    writeLogData += "ReapedSessionsTotal" + dm
    
    writeLogData += "SessionUpdates" + dm
    writeLogData += "OverflowUpdates" + "\n"
  
  writeLogData += str(idx) + dm
  writeLogData += LastReapCycle + dm
  writeLogData += NextReapCycle + dm
  
  writeLogData += AverageReapDuration + dm
  writeLogData += LastReapDuration + dm
  writeLogData += MaxReapDuration + dm
  
  writeLogData += AverageReapedSessions + dm
  writeLogData += MaxReapedSessions + dm
  writeLogData += ReapedSessions + dm
  writeLogData += ReapedSessionsTotal + dm
  
  writeLogData += OverflowUpdates + dm
  writeLogData += SessionUpdates
  
  fo.write(writeLogData+"\n")
  fo.flush()
  print(writeLogData)
  Thread.sleep(sleep_in_ms)

fo.close()
exit()
EOF
```

<br><br>
### (2) Test Application

Session 을 원하는 Size만큼 생성 시키는 Application은 [Coherence-Session-Test-Application]({{ site.url }}/coherence/Coherence-Session-Test-Application) 을 사용한다.

<br><br>
### (3) Apache JMeter

Apache JMeter는 다음과 같이 설정했다.

* Thread Group
  * Number of Threads (users): 50
  * Ramp-up period (seconds): 1
  * Loop Count: Infinite
  * Use KeepAlive: X (No)
  * Specify Thread lifetime
    * Duration(Seconds) : 300

1초 이내에 50명의 사용자가 준비되며, 지속적으로 신규 사용자처럼 유입된다.

이 작업은 300 secs 동안 지속된다. TPS로 환산할 수 없으나, 성능이 좋지 않은 Local 에서 작업하기에는 꽤 클 것이다.

<br>
성능이 좋지 않은 Local Test System 에서 작업하니, 사용자를 더 크게 늘릴 수 없었다.

늘리는 경우, Coherence에 쌓이는 Cache 가 매우 많아 Reaper가 동작하지 않는 문제가 있었다.

<br><br>
### (4) Cache Server/Client

Cache Server(Coherence Web), Cache Client(WebLogic Server; MCS)는 물리적으로 같은 Node이며

기본적으로 다음의 초기 환경을 구성하였다.

<br>
* RHEL 8.7, 2 physical core (4 logic core with hyperthreading), JDK 1.8.0_351

* Coherence Server 1 EA
  * `-Xms2048m -Xmx2048m`
* Managed Coherence Server 1 EA
  * `-Xms3096m -Xmx3096m`
  * `coherence.session.localstorage=false`
  * `coherence.reaperdaemon.parallel=true`
  * `wm/CoherenceWorkManager` : Min(2) / Max(2)
  * Deployed 'cohSessionApp'
    * Session Timeout Secs : 30
    * Invalidation Interval Secs : 60

<br><br>
## 6.2 50 Users

기본 환경 구성한대로, 50 Users 반복 요청 시에 쌓이는 Session Data와,

30 Secs 마다 Session은 Invalid 된다.

Invalid 된 Session을 정리하는 Reaper Thread가 어떻게 작업을 이루어 냈는지 Data를 뽑아내었다.

<br>
JMeter로 부하를 인입하고, WLST로 Coherence에 Session이 적재된 것이 관측된 최초 지점부터 Data를 Grep해보면 대략 아래와 같이 쌓인다.

<br>
```
LastReapCycle | NextReapCycle | AverageReapDuration | LastReapDuration | MaxReapDuration | AverageReapedSessions | MaxReapedSessions | ReapedSessions | ReapedSessionsTotal | SessionUpdates | OverflowUpdates

...

1 | Tue May 30 16:02:33 KST 2023 | Tue May 30 16:03:33 KST 2023 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 278 | 275
2 | Tue May 30 16:02:33 KST 2023 | Tue May 30 16:03:33 KST 2023 | 0 | 0 | 0 | 0 | 0 | 0 | 

...

71 | Tue May 30 16:08:43 KST 2023 | Tue May 30 16:09:43 KST 2023 | 11485 | 5898 | 20649 | 6243 | 9865 | 5381 | 37458 | 37303 | 37289

...
```

<br>
JMeter로 300 Secs 동안 요청이 인입되고 난뒤에는 종료될 것이다.

초기, Session Data가 관측되지 않는 (SessionUpdates 가 0) Data는 제외.

말기, Session Data가 더 이상 정리될 것이 없는 (ReapedSessionsTotal이 SessionUpdates 에 가까움) Data 까지만 수집한다.

<br>
평균 또는 수집된 데이터를 보면,

| AverageReapDuration | LastReapDuration | MaxReapDuration | AverageReapedSessions | MaxReapedSessions | ReapedSessions | ReapedSessionsTotal | SessionUpdates | OverflowUpdates |
| ------------------- | ---------------- | --------------- | --------------------- | ----------------- | -------------- | ------------------- | -------------- | --------------- |
| 4520.352113         | 9164.901408      | 12129           | 2680.43662            | 9631              | 6347.28169     | 38257               | 38123          | 38078           |

<br>
AverageReapDuration : Reap에 소요된 평균 시간 (평균값)

LastReapDuration : 가장 마지막 Reap에 소요된 시간 (평균값)

MaxReapDuration : Reap에 소요된 최대 시간 (최대값)

AverageReapedSessions : Reaped Session의 평균 갯수, 평균적으로 Reap 1 Cycle 당 몇개의 Session이 Reaped 되는지를 나타냄 (평균값)

MaxReapedSessions : Reaped Session의 최대 갯수, 한번에 최대 몇개의 Session이 Reaped 되었는지를 나타냄 (최대값)

ReapedSessions : Reap 1 Cycle 당 한번에 몇개의 Session이 Reaped 되었는지 나타냄 (평균값)

ReapedSessionTotal : 지금까지 총합 Reaped Session 갯수 (최대값)

SessionUpdates : Session이 만들어지거나, Touched 되었을 때 집계 됨 (최대값)

OverflowUpdates : Overflow는 큰 Session Data를 저장할 때 사용되는 Model이며, OverflowThreshold(default 1024) 크기를 넘어서는 Session의 총 Updates 갯수가 집계됨. (최대값)

<br>
평균에 의미가 없는 값들은, 최대값으로 수집했다.

<br><br>
## 6.3 50 Users / 4 Threads

앞서, WebLogic WorkManager에 의해 Min/Max가 2 Threads로 환경을 구성하여 테스트했다면,

이번에는 4 Threads로 구성하여 개선되는지 살펴본다.

<br>
```xml
  <self-tuning>
    <min-threads-constraint>
      <name>MinThreadsConstraint-0</name>
      <target>myCluster</target>
      <count>4</count>
    </min-threads-constraint>
    <max-threads-constraint>
      <name>MaxThreadsConstraint-0</name>
      <target>myCluster</target>
      <count>4</count>
    </max-threads-constraint>
    <work-manager>
      <name>wm/CoherenceWorkManager</name>
      <target>myCluster</target>
    </work-manager>
```

<br>
평균은,

| AverageReapDuration | LastReapDuration | MaxReapDuration | AverageReapedSessions | MaxReapedSessions | ReapedSessions | ReapedSessionsTotal | SessionUpdates | OverflowUpdates |
| ------------------- | ---------------- | --------------- | --------------------- | ----------------- | -------------- | ------------------- | -------------- | --------------- |
| 4446.315068         | 8821.205479      | 13252           | 2884.260274           | 9754              | 6474.520548    | 37743               | 37582          | 37551           |

<br>
검증을 위해, 동일하게 한번 더 테스트하였는데 아래와 같다.

| AverageReapDuration | LastReapDuration | MaxReapDuration | AverageReapedSessions | MaxReapedSessions | ReapedSessions | ReapedSessionsTotal | SessionUpdates | OverflowUpdates |
| ------------------- | ---------------- | --------------- | --------------------- | ----------------- | -------------- | ------------------- | -------------- | --------------- |
| 3637.561644         | 10007.67123      | 14751           | 2068.520548           | 9829              | 6447.589041    | 38384               | 38203          | 38255           |

<br>
이외에도 여러번의 테스트를 해보았는데, 결과마다 편차가 조금 심한 편이지만 대체적으로 Reaper Thread를 늘려 개선이 되는 것은 확인이 된다.

<br><br>
## 6.4 50 Users / 8 Threads

평균은,

| AverageReapDuration | LastReapDuration | MaxReapDuration | AverageReapedSessions | MaxReapedSessions | ReapedSessions | ReapedSessionsTotal | SessionUpdates | OverflowUpdates |
| ------------------- | ---------------- | --------------- | --------------------- | ----------------- | -------------- | ------------------- | -------------- | --------------- |
| 4944.534247         | 9499.547945      | 13958           | 2801.657534           | 9838              | 6346.931507    | 37692               | 37577          | 37579           |

<br>
재차 테스트 시에,

| AverageReapDuration | LastReapDuration | MaxReapDuration | AverageReapedSessions | MaxReapedSessions | ReapedSessions | ReapedSessionsTotal | SessionUpdates | OverflowUpdates |
| ------------------- | ---------------- | --------------- | --------------------- | ----------------- | -------------- | ------------------- | -------------- | --------------- |
| 6347.72             | 9040.72          | 16162           | 3886.213333           | 9784              | 6437.76        | 38259               | 38072          | 38081           |

<br>
오히려 감소하기도 하고, 특별히 드라마틱한 변화가 없다.

<br><br>
## 6.5 50 Users / 12 Threads

평균은,

| AverageReapDuration | LastReapDuration | MaxReapDuration | AverageReapedSessions | MaxReapedSessions | ReapedSessions | ReapedSessionsTotal | SessionUpdates | OverflowUpdates |
| ------------------- | ---------------- | --------------- | --------------------- | ----------------- | -------------- | ------------------- | -------------- | --------------- |
| 3344.381579         | 8949.065789      | 22647           | 1913.447368           | 9654              | 6253.592105    | 38098               | 37919          | 37915           |

<br>
재차 테스트,

| AverageReapDuration | LastReapDuration | MaxReapDuration | AverageReapedSessions | MaxReapedSessions | ReapedSessions | ReapedSessionsTotal | SessionUpdates | OverflowUpdates |
| ------------------- | ---------------- | --------------- | --------------------- | ----------------- | -------------- | ------------------- | -------------- | --------------- |
| 6243.068493         | 9646.287671      | 13999           | 3526.219178           | 9837              | 6268.753425    | 37427               | 37278          | 37320           |

<br><br>
## 6.6 OverflowUpdates

OverflowUpdates : Overflow는 큰 Session Data를 저장할 때 사용되는 Model이며, OverflowThreshold(default 1024) 크기를 넘어서는 Session의 총 Updates 갯수가 집계됨.

<br>
Test App에서 생성하는 Session Data의 Size를 1024 bytes 보다 작게 만들 경우,

SessionUpdates는 증가하되, OverflowUpdates는 증가하지 않을 것으로 보이는데,

이 부분을 검증하기 위해서 Session Data 의 정확한 Size를 Inspect 해야 한다.

<br>
JFR, Heap Dump, Instrumentation.getObjectSize 등등 여러가지를 확인해보고 있으나,

껍데기 Size만 확인되는 등 정확한 수치가 나오질 않아 좀 더 확인해봐야 하는 부분이다.

<br>
이후에, 여러날에 걸쳐 확인을 해보았는데 openjdk 의 JOL(Java Object Layout) Library 를 활용하여 Object Size를 측정할 수 있었다.

[Java-Object-Layout]({{ site.url }}/programming/Java-Object-Layout) Post 에서 다루었다.

<br>
Post에 따르면, _obj Byte Array를 정확히 실제 크기 1024 Bytes에 맞추기 위해서는

* Header bytes 16 를 빼고
* Gap 8bytes 의 배수에 맞게끔

설정하면 된다고 했다.

<br>
그러므로 _obj Byte Array 갯수는 정확히 1008 개를 만들면, 실제 JVM Heap Memory에 올라가는 Object Size는 1024 Bytes가 된다.

`byte[] _obj = new byte[1008];`

<br>
이제 Coherence Session Data를 Update 하고 MBean을 살펴보면

* OverflowThreshold : 1024
* OverflowUpdates : 0
* OverflowMaxSize : 0

Session Data가 1024 bytes 보다 작기 때문에, 1회 호출 시에는 Overflow cache 가 아닌 것이 확인된다.

<br>
연속 2회 호출하여, Session Data 크기를 증분 시키면,

* OverflowThreshold : 1024
* OverflowUpdates : 1
* OverflowMaxSize : 2019

예상값 2032 Bytes 보다 작은 2019 Bytes로 확인되며, Overflow 가 update 되었다.

<br>
연속 호출을 더 여러번 해보았는데, 항상 JVM Heap memory 에 적재되는 실제 Size보다 항상 13 Bytes가 적게 측정되었다.

Coherence 의 Session을 다루는 Object를 JOL로 확인해보고 싶으나, Object 를 특정짓지 못하였다.

<br><br>
# 7. Outcomes

성능이 좋지 않은 Local Test 환경에서는 4 Reaper Thread 환경 부터 그나마 Tuning 의 결과가 확인이 된다.

그럼에도 반복 수행 시 Local Test 환경의 영향인지, 들쑥 날쑥하고 드라마틱한 결과를 보여주지는 않는다.

<br>
Test 결과 또한 좋았으면 했지만 그렇지 않았으므로

MBean 항목에 대한 이해를 얻은 것으로 마무리 해야 할 듯 싶다.

<br>
그 외에도, JOL 을 이용하여 Overflowupdate 기준을 실제 추적하는 Test도 진행할 수 있었다.

<br><br>
# 8. References

[Overflow 관련](https://docs.oracle.com/en//middleware/standalone/coherence/14.1.1.0/administer-http-sessions/monitoring-applications.html#GUID-93AB0B53-6335-4E55-B66C-8CA566EEE8A0)

[WLST로 수집되는 MBean 항목 부연 설명 관련 자료](https://dhkim900331.github.io/coherence/How-To-Monitor-Coherence-Web-3#h-32-mbean-%ED%95%AD%EB%AA%A9-%EC%84%A4%EB%AA%85)

[Java-Object-Layout]({{ site.url }}/programming/Java-Object-Layout)

[Specifying a Cluster's Multicast Address and Port](https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/develop-applications/setting-cluster.html#GUID-D3FDEDBF-B97A-4C8D-BEFF-AB54C9D94CB5)

**Recommended Thread-count-min And Thread-count-max Values in Coherence (Doc ID 2294067.1)**

**Explanation Of Meaning For Coherence Threadpool Error Message (Doc ID 2728051.1)**
