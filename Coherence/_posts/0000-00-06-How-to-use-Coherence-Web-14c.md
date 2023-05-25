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



# 2. Death Detection

[Configuring Death Detection](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/develop-applications/setting-cluster.html#GUID-FE185358-AE38-4436-9179-73E0D4CAAD13) 을 하여, ClusterMember 이탈 여부를 확인한다.



## 2.1 TCP-RING

Member들은 하나의 Ring으로 연결된다.

25초 동안 HeartBeat 응답을 주지 않은 Member를 5회 실시하여, Member를 제거한다.

`java.net.InetAddress.isReachable` 를 시도하며, 이 Method는 Process가 아니라 Host에 Port 7(Echo)를 전송하여 응답을 받으려고 시도한다.

Port 7(Echo) 가 방화벽에 예외 처리 되어 있어야 한다.

listen-backlog는 이러한 HeartBeat 감지를 받을 때, 최대 backlog 로 보여진다.



```xml
    <tcp-ring-listener>
      <enabled>true</enabled>
      <ip-timeout system-property="coherence.ipmonitor.pingtimeout">25s</ip-timeout>
      <ip-attempts>5</ip-attempts>
      <listen-backlog>10</listen-backlog>
    </tcp-ring-listener>
```



최대 2분 5초 동안 응답을 하지 않은 Member가 발견되면 아래와 같이 Logging 된다.

```
tmb://10.65.34.245:9003.34707 initiating connection migration with tmb://10.65.34.245:9001.43859 after 2m5s ack timeout health(read=true, write=false), receiptWait=null: peer=tmb://10.65.34.245:9001.43859
```

9003 Port Member가 응답하지 않는다.



tcp-ring-listener 를 사용하지 않으면, 인스턴스가 Shutdown 될 시에 매우 늦게 감지가 된다.

반드시 사용한다.

> tcp-ring-listener false 시에 Member shutdown 을 하면 2분 5초 뒤에 파악이 된다.



## 2.2 HeartBeat

Cluster Member들 간에는 HeartBeat를 주고 받는다.

이 HeartBeat 간격은 기본값 1초 이며, Member가 많을 경우 Traffic이 증대할 것이며, 평소 Network 신뢰성이 높은 경우, 불필요하게 많은 Traffic을 유발하지 않도록 설정값을 변경하는 것도 고려해볼 만 하다.



문서 상에는, HeartBeat를 매 간격마다 보내지 않고, 내부 평가 프로세스에 따라 그러하다고 하는데 어떤 프로세스를 가지는지는 문서상에 보이지 않는다.



```xml
    <packet-publisher>
      <packet-delivery>
        <heartbeat-milliseconds>5000</heartbeat-milliseconds>
      </packet-delivery>
    </packet-publisher>
```



# 3. Firewall

* Cluster Port (Default 7574) 는 Multicast/Unicast 에서 모두 사용되고, UDP/TCP 로 쓰인다. Coherence에 Proxy를 구성하고, Client에서 Naming Service로 Proxy를 이용할 때 Name을 검색하는 Port.
* Death Detection 을 위해 TCP 7 (Echo port)를 사용한다.
* 위 외에 메뉴얼상 필요한 Port는 없고, Member간의 통신 방식에 사용하는 Port를 열어주면 된다.





# 4. MBean Monitoring

다음 옵션을 추가하여, WLST MBean 을 Monitoring 할 수 있다.

```sh
-Djavax.management.builder.initial=weblogic.management.jmx.mbeanserver.WLSMBeanServerBuilder
```



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



Coherence Cluster를 사용하는 WebApp 이 배포된 Managed Coherence Server에 설정 후 JConsole을 통해 MBean 을 읽을 수 있다.



<img src="/../assets/posts/images/How-to-use-Coherence-Web-14c/image-20230424145943477.png" alt="image-20230424145943477" style="zoom: 33%;" />



Coherence - WebLogicHttpSessionManager - \<Member ID> - \<Web App> - Attributes 에서 처리되는 Session 통계를 알 수 있다.



Member ID는 Node의 각 Attributes 에서 MemberName이나 ProcessName 으로 획득하면 수월하겠다.

![image-20230424151956264](/../assets/posts/images/How-to-use-Coherence-Web-14c/image-20230424151956264.png)



예시 화면에서는 Unique 하게 되어 있지 않은데, Operational Override File에서 지정하면 된다.

```xml
      <process-name system-property="coherence.process">process_base_domain</process-name>
      <member-name  system-property="coherence.member">member_base_domain</member-name>
```





# 6. Session Reaper Thread

App 에서 생성된 HTTP Session은 timeout-secs 만큼 유효하다.

invalidation-internal-secs 마다 All HTTP Session을 Scan하여 invalid 한 session을 삭제하여 Memory를 확보한다.



[4. MBean Monitoring](#h-4-mbean-monitoring) 을 이용하여 아래의 Code를 작성하고,

Session 부하를 발생 시킬 때, Reaper Thread가 어떻게 동작하는지 알아본다.



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
for idx in range(0, 100):
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



Session 을 원하는 Size만큼 생성 시키는 Application은 [Coherence-Session-Test-Application]({{ site.url }}/Coherence-Session-Test-Application) 을 사용한다.



Apache JMeter는 다음과 같이 설정했다.

* Thread Group
  * Number of Threads (users): 100
  * Ramp-up period (seconds): 1
  * Loop Count: Infinite
  * Use KeepAlive: X (No)

1초 이내에 100명의 사용자가 준비되며, 지속적으로 신규 사용자처럼 유입된다.





## 6.1 Test #1

종합적으로, 다음의 환경에서 Test가 진행된다.

* RHEL 8.7, 2 physical core (4 logic core with hyperthreading), JDK 1.8.0_351

* Coherence Server 1 EA
  * `-Xms1024m -Xmx1024m`
* Managed Coherence Server 1 EA
  * `-Xms3096m -Xmx3096m`
  * `coherence.session.localstorage=false`
  * Deployed 'cohSessionApp'
    * Session Timeout Secs : 30
    * Invalidation Interval Secs : 60





