---
date: 2023-02-02 08:58:49 +0900
layout: post
title: "[Coherence/Web] How to Monitor Coherence Web 3.X"
tags: [Coherence, Web, Monitoring]
typora-root-url: ..
---

# 1. 개요

Coherence Web 3.X 사용 시, 여러 Monitoring 옵션과 결과물을 확인한다.



# 2. Debug Log

## 2.1 Using Coherence

WLS Instance JVM Options으로 다음과 같이 설정 시, Instance에서 동작하는 Coherence 의 Debug Log가 최대값(9)로 기록된다.



https://docs.oracle.com/cd/E24290_01/coh.371/e22837/gs_debug.htm#COHDG5549



```sh
-Dtangosol.coherence.log.level=9
-Dtangosol.coherence.log=debug.log
```



다음의 사항들을 Log에서 확인할 수 있다.

* Version

  `Oracle Coherence Version 3.7.1.22 Build 86827`

* WLS(Id=1) Member의 정보와 Cache Server(Id=3) Member에 가입했다는 로그

  ```
  This Member(Id=1, Timestamp=2023-01-25 16:59:58.419, Address=10.65.34.245:10002, MachineId=17093, Location=site:,machine:wls,process:1198941, Role=WeblogicServer, Edition=Grid Edition, Mode=Production, CpuCount=4, SocketCount=1) joined cluster "MyCluster" with senior Member(Id=3, Timestamp=2023-01-25 12:42:02.926, Address=10.65.34.245:10000, MachineId=17093, Location=site:,machine:wls,process:1123427, Role=CoherenceServer, Edition=Grid Edition, Mode=Production, CpuCount=4, SocketCount=1)
  ```

* TcpRing 방식으로 연결된 시점과 로그

  ```
  TcpRing connecting to Member(Id=3, Timestamp=2023-01-25 12:42:02.926, Address=10.65.34.245:10000, MachineId=17093, Location=site:,machine:wls,process:1123427, Role=CoherenceServer)
  ```

* Cluster의 총 Member 정보

  ```
  MasterMemberSet(
    ThisMember=Member(Id=1, Timestamp=2023-01-25 16:59:58.419, Address=10.65.34.245:10002, MachineId=17093, Location=site:,machine:wls,process:1198941, Role=WeblogicServer)
    OldestMember=Member(Id=3, Timestamp=2023-01-25 12:42:02.926, Address=10.65.34.245:10000, MachineId=17093, Location=site:,machine:wls,process:1123427, Role=CoherenceServer)
    ActualMemberSet=MemberSet(Size=2
      Member(Id=1, Timestamp=2023-01-25 16:59:58.419, Address=10.65.34.245:10002, MachineId=17093, Location=site:,machine:wls,process:1198941, Role=WeblogicServer)
      Member(Id=3, Timestamp=2023-01-25 12:42:02.926, Address=10.65.34.245:10000, MachineId=17093, Location=site:,machine:wls,process:1123427, Role=CoherenceServer)
      )
    MemberId|ServiceVersion|ServiceJoined|MemberState
      1|3.7.1|2023-01-25 16:59:58.804|JOINED,
      3|3.7.1|2023-01-25 12:42:02.926|JOINED
    RecycleMillis=1200000
    RecycleSet=MemberSet(Size=0
      )
    )
  ```

* 구성된 Session model (아래 값에 의해 Session object가 관리됨)

  ```
  Configured session model "SplitHttpSessionCollection":
    Clustered Session Cache Name=session-storage
    Local Session Cache Name=local-session-storage
    Local Session Attribute Cache Name=local-attribute-storage
    Death Certificate Cache Name=session-death-certificates
    SessionDistributionController Class Name=
    AttributeScopeController Class Name=com.tangosol.coherence.servlet.AbstractHttpSessionCollection$ApplicationScopeController
    Maximum Session Inactive Seconds=10
    Session ID Character Length=52
    Session Locking Enforced=false
    Member Session Locking Enforced=false
    Application Session Locking Enforced=false
    Thread Session Locking Enforced=false
    Session Get Lock Timeout=19
    Suspect Attribute Detection=true
    Strict "Servlet Specification" Exception Handling=true
    Sticky Session Ownership=false
    Sticky Session Ownership Service Name=SessionOwnership
    Assume Session Locality for Reaping=false
    Parallel Session Reaping=true
    Allow Local Attributes=false
    Use Default Session ID Decoding=true
    Use Default Session ID Encoding=false
    Session ID Affinity Token=null
    Session ID Replace Affinity Token=false
    Session Expiry Filter Factory=
    Session Access Debug Logging Enabled=false
    Session Access Debug Logging Filter=
  ```

* 다음 Application이 등록됨

  ```
  Registering MBean using object name "type=WebLogicHttpSessionManager,nodeId=1,appId=cohSessionAppcohSessionApp"
  ```




## 2.2 Using JDK

https://docs.oracle.com/cd/E24290_01/coh.371/e22837/gs_debug.htm#COHDG5555



```logging.properties
handlers=java.util.logging.FileHandler, java.util.logging.ConsoleHandler
.level=INFO

java.util.logging.FileHandler.pattern=/sw/weblogic/11g/domains/base_domain/logs/coh_M1_%u.log
java.util.logging.FileHandler.limit=50000
java.util.logging.FileHandler.level=FINEST
java.util.logging.FileHandler.count=1
java.util.logging.FileHandler.formatter=java.util.logging.SimpleFormatter

java.util.logging.ConsoleHandler.formatter=java.util.logging.SimpleFormatter
```



```sh
-Dtangosol.coherence.log=jdk
-Djava.util.logging.config.file=$DOMAIN_HOME/logging.properties
```





# 3. JMX MBean

## 3.1 활성화 방법

JMX MBean 활성화 및 JConsole 또는 JVisualVM으로 모니터링 할 수 있다.



https://docs.oracle.com/cd/E24290_01/coh.371/e22842/jmx.htm#COHMG239



```sh
-Dtangosol.coherence.management=all"
-Dtangosol.coherence.management.remote=true"
-Dcom.sun.management.jmxremote"
-Dcom.sun.management.jmxremote.ssl=false"
-Dcom.sun.management.jmxremote.authenticate=false"

-Djava.rmi.server.hostname=wls.local"
-Dcom.sun.management.jmxremote.port=8999"
```



Jconsole로 접근한다.

![How-To-Monitor-Coherence-Web-3_1](/../assets/posts/images/Coherence/How-To-Monitor-Coherence-Web-3/How-To-Monitor-Coherence-Web-3_1.png)





다음의 `WebLogicHttpSessionManager` - `2 (WLS Member ID)` 하위에서 Session Application 별로 MBean을 모니터링 할 수 있다.

![How-To-Monitor-Coherence-Web-3_2](/../assets/posts/images/Coherence/How-To-Monitor-Coherence-Web-3/How-To-Monitor-Coherence-Web-3_2.png)







## 3.2 MBean 항목 설명

위 MBean 항목은 여러 차례 테스트 및 문서에서 안내하는 내용들로 확인 결과 아래 처럼 정리할 수 있었다.



https://docs.oracle.com/cd/E24290_01/coh.371/e22620/manageapps.htm#CIHCBHIG



 (1) Reaper 주기 지표
  - NextReapCycle : 다음 reaper 주기 (date)
  - LastReapCycle : 최근 reaper 시간 (date)
   * 위 두개는, invalidation-interval-secs 설정임

 (2) Reaper 성능 지표
  - AverageReapDuration : 평균 reap 시간 (millis)
  - MaxReapDuration : 문서에 설명없지만, 최대 reap 시간 (millis) 으로 보여짐
  - LastReapDuration : 마지막 reap 에 걸린 시간 (millis)

 (3) Reaper에 의해 회수된 세션 갯수 지표
  * 일부는 [여기 메뉴얼](https://docs.oracle.com/cd/E24628_01/install.121/e24215/coherence_monitor.htm#GSSOA11024)에 설명이 있음
  - MaxReapedSessions : 최대치로 회수된 세션 수 (ReapedSessionsTotal와 다르다. NextReapCycle 시에 한번에 회수된 세션이 최대 몇개인지 알려준다)
  - ReapedSessionsTotal : 지금까지 회수된 세션 수 총합
  - AverageReapedSessions : 회수된 평균 세션 수 (MaxReapedSessions와 유사한 의미로 보여짐. NextReapCycle 시에 한번에 회수된 세션이 많을 수록 평균치가 증가할 것으로 보여짐)

 (4) 세션 객체에 대한 지표
  - SessionUpdates : OverflowThreshold 크기 미만에 대한 세션 생성 수를 기록하는 것으로 추측했으나, 그렇지 않고 업데이트된 모든 세션 수로 보여짐
  - SessionAverageLifetime : 세션 평균 활성화된 시간 (만료되지 않고 얼마나 오랫동안 Update 되었는지, SessionTimeout, NextReapCycle 에 의해 변할 수 있음)
  - SessionTimeout : xml 등 어플리케이션에 설정한 session timeout과 같음
  - SessionMinSize,SessionMaxSize,SessionAverageSize : 세션 객체의 최소,최대,평균 크기 이며 Overflow Session 객체가 아니라면 여기에 포함되지 않는다.
  - OverflowAverageSize, OverflowMaxSize : 세션 객체의 최소,최대,평균 크기 이며 Overflow Session 객체에 해당한다.
  - OverflowUpdates : OverflowThreshold 크기 보다 큰 객체로 만들어진 세션이 얼마나 생성 또는 업데이트 되었는지 지표
  - OverflowThreshold : Default로 보여짐 -> 1024 (좀 더 테스트가 필요하지만,  기본값 1024 bytes로 되어있는 경우, session 객체 크기가 해당 bytes보다 크면 Overflow 로 통계치 분리 저장됨)

  ** Overflow : 특별히 큰 세션 객체에 대한 속성들



# 4. Report

Reporter 를 구성하여 보고서를 기록할 수 있다.



https://docs.oracle.com/cd/E24290_01/coh.371/e22620/manageapps.htm#COHCW283



Reports XML 추출 [보고서의 종류](https://docs.oracle.com/cd/E24290_01/coh.371/e22842/analyze_report.htm#COHMG245)

```sh
$ jar -xvf ${COHERENCE_HOME}/lib/coherence.jar reports
  created: reports/
 inflated: reports/report-all.xml
 inflated: reports/report-cache-effectiveness.xml
 inflated: reports/report-cache-size.xml
 inflated: reports/report-flashjournal.xml
 inflated: reports/report-group.xml
 inflated: reports/report-management.xml
 inflated: reports/report-memory-status.xml
 inflated: reports/report-network-health-detail.xml
 inflated: reports/report-network-health.xml
 inflated: reports/report-node.xml
 inflated: reports/report-proxy.xml
 inflated: reports/report-ramjournal.xml
 inflated: reports/report-service.xml
 inflated: reports/report-web-cache-overflow.xml
 inflated: reports/report-web-cache-sessions.xml
 inflated: reports/report-web-group.xml
 inflated: reports/report-web-service.xml
 inflated: reports/report-web-sessions.xml
 inflated: reports/report-web.xml
```



Instance에 JVM Option을 설정한다. [메뉴얼](https://docs.oracle.com/cd/E24290_01/coh.371/e22842/reporter.htm#COHMG5536)

```sh
-Dtangosol.coherence.management.report.configuration=${COHERENCE_HOME}/lib/reports/report-web.xml"
```



Instance의 Coherence Log에 기록된다.

```
2023-01-26 10:15:18.586/16.785 Oracle Coherence GE 3.7.1.22 <Info> (thread=[ACTIVE] ExecuteThread: '0' for queue: 'weblogic.kernel.Default (self-tuning)', member=n/a): Loaded Reporter configuration from "file:/sw/coherence/3.7.1.22/lib/reports/report-web.xml"
```



이후, 자동으로 Report가 남지 않아 MBean에서 확인해본 결과,

* Reporter - \<Member ID>
  * Attributes
    * IntervalSeconds : 60
    * ConfigFile : ${COHERENCE_HOME}/lib/reports/report-web.xml
    * AutoStart : false ([메뉴얼](https://docs.oracle.com/cd/E24290_01/coh.371/e22842/reporter.htm#COHMG5536))
    * OutputPath : /sw/weblogic/11g/domains/base_domain
  * Operations
    * start, stop, runReport ...



AutoStart가 true가 아닌지라, 직접 start 실행을 했고, 매 60초마다 실행되는것으로 보이게끔 Coherence Log에 남았다.

```
2023-01-26 10:21:20.491/378.690 Oracle Coherence GE 3.7.1.22 <Info> (thread=RMI TCP Connection(8)-10.191.18.100, member=2): Management Reporting -  Started
```



이후 보고서는 잘 나오는것이 확인되나, 내가 원하는 web-session Service만 Report를 실행하고 싶어 설정해본다.

아래와 같이 `myreport-web.xml` Group List을 만들어 `report-web.xml` 단독 보고서만 실행을 하고 싶으나, 해당 파일은 보고서를 생성하지 않았다. 원인은 알 수가 없다.

```sh
$ cat myreport-web.xml
<report-group xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
              xmlns="http://xmlns.oracle.com/coherence/coherence-report-group-config"
              xsi:schemaLocation="http://xmlns.oracle.com/coherence/coherence-report-group-config coherence-report-group-config.xsd">

  <frequency>1m</frequency>
  <output-directory>/sw/weblogic/11g/domains/base_domain/logs/report/</output-directory>
  <report-list>
    <report-config>
      <location>/sw/coherence/3.7.1.22/lib/reports/report-web.xml</location>
    </report-config>
  </report-list>
</report-group>

```



위에서 내가 일부 편집한 보고서는 동작이 되지 않으므로... 다시 맨 처음 잘 되던 보고서를 사용할 수밖에 없는 듯 하다.

[Date Format](https://docs.oracle.com/cd/E24290_01/coh.371/e22842/reporter.htm#COHMG5555) 옵션과 함께, 기본으로 제공되는 `report-all.xml` Group List 파일을 실행하도록 옵션을 구성해본다.

```sh
-Dtangosol.coherence.management.report.configuration=${COHERENCE_HOME}/lib/reports/report-all.xml"
-Dtangosol.coherence.management.report.autostart=true"
-Dtangosol.coherence.management.report.timezone=Asia/Seoul"
-Dtangosol.coherence.management.report.timeformat=hh:mm:ss"
```



WLS Instance 기동 후 얼마 지나지 않아, Reporter 실행될 때마다 반복적으로 로깅된다.

`Loaded Reporter configuration from "jar:file:/sw/weblogic/11g/domains/base_domain/lib/coherence.jar!/reports/<report-all.xml 내의 List>"`



`output-directory` (끝에 slash 있어야 함) 내에 시간 단위 파일이 생성되고, 1분 단위로 append 된다.

```sh
ls -al /sw/weblogic/11g/domains/base_domain/logs/report
total 60
drwxrwxr-x 2 wasadm wasadm 4096 Jan 26 11:25 .
drwxrwxr-x 6 wasadm wasadm   82 Jan 26 11:34 ..
-rw-r----- 1 wasadm wasadm 1396 Jan 26 11:33 2023012611-cache-session-overflow.txt
-rw-r----- 1 wasadm wasadm 1387 Jan 26 11:33 2023012611-cache-session-storage.txt
-rw-r----- 1 wasadm wasadm 1736 Jan 26 11:33 2023012611-cache-size.txt
-rw-r----- 1 wasadm wasadm 4717 Jan 26 11:33 2023012611-cache-usage.txt
-rw-r----- 1 wasadm wasadm  530 Jan 26 11:33 2023012611-Management.txt
-rw-r----- 1 wasadm wasadm 3739 Jan 26 11:33 2023012611-memory-status.txt
-rw-r----- 1 wasadm wasadm 1400 Jan 26 11:33 2023012611-network-health-detail.txt
-rw-r----- 1 wasadm wasadm  428 Jan 26 11:33 2023012611-network-health.txt
-rw-r----- 1 wasadm wasadm 1644 Jan 26 11:33 2023012611-nodes.txt
-rw-r----- 1 wasadm wasadm 2101 Jan 26 11:33 2023012611-service.txt
-rw-r----- 1 wasadm wasadm 1454 Jan 26 11:33 2023012611-web-session-service.txt
-rw-r----- 1 wasadm wasadm 4620 Jan 26 11:33 2023012611-web-sessions.txt
```



위 파일들이 보고서 갯수에 비해 적어 보이는데... 시간이 더 지나니 아래와 같이 늘어났다..?

```sh
ls -al
total 268
drwxrwxr-x 2 wasadm wasadm  4096 Jan 26 12:00 .
drwxrwxr-x 6 wasadm wasadm    82 Jan 26 12:50 ..
-rw-r----- 1 wasadm wasadm  4421 Jan 26 11:59 2023012611-cache-session-overflow.txt
-rw-r----- 1 wasadm wasadm  4387 Jan 26 11:59 2023012611-cache-session-storage.txt
-rw-r----- 1 wasadm wasadm  6411 Jan 26 11:59 2023012611-cache-size.txt
-rw-r----- 1 wasadm wasadm 17067 Jan 26 11:59 2023012611-cache-usage.txt
-rw-r----- 1 wasadm wasadm  1705 Jan 26 11:59 2023012611-Management.txt
-rw-r----- 1 wasadm wasadm 13705 Jan 26 11:59 2023012611-memory-status.txt
-rw-r----- 1 wasadm wasadm  4745 Jan 26 11:59 2023012611-network-health-detail.txt
-rw-r----- 1 wasadm wasadm  1187 Jan 26 11:59 2023012611-network-health.txt
-rw-r----- 1 wasadm wasadm  5919 Jan 26 11:59 2023012611-nodes.txt
-rw-r----- 1 wasadm wasadm  7501 Jan 26 11:59 2023012611-service.txt
-rw-r----- 1 wasadm wasadm  5004 Jan 26 11:59 2023012611-web-session-service.txt
-rw-r----- 1 wasadm wasadm 16745 Jan 26 11:59 2023012611-web-sessions.txt
-rw-r----- 1 wasadm wasadm  6226 Jan 26 12:52 2023012612-cache-session-overflow.txt
-rw-r----- 1 wasadm wasadm  6177 Jan 26 12:52 2023012612-cache-session-storage.txt
-rw-r----- 1 wasadm wasadm  9193 Jan 26 12:52 2023012612-cache-size.txt
-rw-r----- 1 wasadm wasadm 24471 Jan 26 12:52 2023012612-cache-usage.txt
-rw-r----- 1 wasadm wasadm  2393 Jan 26 12:52 2023012612-Management.txt
-rw-r----- 1 wasadm wasadm 19609 Jan 26 12:52 2023012612-memory-status.txt
-rw-r----- 1 wasadm wasadm  6812 Jan 26 12:52 2023012612-network-health-detail.txt
-rw-r----- 1 wasadm wasadm  1929 Jan 26 12:52 2023012612-network-health.txt
-rw-r----- 1 wasadm wasadm  8470 Jan 26 12:52 2023012612-nodes.txt
-rw-r----- 1 wasadm wasadm 10634 Jan 26 12:52 2023012612-service.txt
-rw-r----- 1 wasadm wasadm  7064 Jan 26 12:52 2023012612-web-session-service.txt
-rw-r----- 1 wasadm wasadm 23966 Jan 26 12:52 2023012612-web-sessions.txt
```





# 5. Plugin (JVisualVM)

https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/tutorial-install-coh-visualvm/
