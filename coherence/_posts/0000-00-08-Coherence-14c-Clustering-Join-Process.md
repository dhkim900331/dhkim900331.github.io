---
date: 2023-06-16 08:27:25 +0900
layout: post
title: "[Coherence] Coherence 14c Clustering Join Process"
tags: [Coherence, Clustering, Join]
typora-root-url: ..
---

# 1. Overview

Coherence 14c 기동 될 때, Clustering 에 Join 되는 과정을 Log Level 에서 살펴본다.

Log Message의 불필요할 수 있다고 판단되는 부분은 `...` 으로 skip 한다.

Log Message에서 Date/Time Prefix 또한 불필요한 부분은, 임의 삭제한다.


<br><br>


# 2. Environments

OS, Oracle Linux Server release 8.7

JVM, java version "1.8.0_351"

<br>

그리고 다음의 Arguments로 구성된 여러 Instances 를 갖고 있다.

```
-Xms512m -Xmx512m
-Dcoherence.mode=prod
-Dcoherence.cacheconfig=session-cache-config.xml
-Dcoherence.override=tangosol-coherence-${DOMAIN_NAME}.xml
```


Operational Override

```xml
    <unicast-listener>
      <socket-provider system-property="coherence.socketprovider">tcp</socket-provider>
      <address system-property="coherence.localhost">wls.local</address>
      <port system-property="coherence.localport">9000</port>
      <port-auto-adjust system-property="coherence.localport.adjust">9100</port-auto-adjust>

      <well-known-addresses>
        <address id="1" system-property="coherence.wka">wls.local</address>
      </well-known-addresses>
    </unicast-listener>

    <tcp-ring-listener>
      <enabled>true</enabled>
      <ip-timeout system-property="coherence.ipmonitor.pingtimeout">25s</ip-timeout>
      <ip-attempts>5</ip-attempts>
      <listen-backlog>10</listen-backlog>
    </tcp-ring-listener>

    <packet-publisher>
      <packet-delivery>
        <heartbeat-milliseconds>5000</heartbeat-milliseconds>
        <timeout-milliseconds>60000</timeout-milliseconds>
      </packet-delivery>
    </packet-publisher>
  </cluster-config>
```


Cluster Port는 기본값으로 7574를 사용하고 있다.


<br><br>


# 3. Joining

**최초 Cache Server(이하 #1) 기동 시, TCMP(Tangosol Cluster Management Protocol) 로 Listen을 위해 Bound한 Address 가 확인된다.**

```
Oracle Coherence Version 14.1.1.0.0 Build 77467
 Grid Edition: Production mode
Copyright (c) 2000, 2020, Oracle and/or its affiliates. All rights reserved.
...
<Info> (thread=main, member=n/a): TCMP bound to /10.65.34.245:9000 using TCPDatagramSocketProvider[Delegate: DemultiplexedSocketProvider(com.oracle.common.internal.net.MultiplexedSocketProvider@19b89d4)]
<Info> (thread=NameService:TcpAcceptor, member=n/a): TcpAcceptor now listening for connections on wls.local:9000.3
<Info> (thread=Cluster, member=n/a): NameService now listening for connections on wls.local:7574.3
<Info> (thread=Cluster, member=n/a): Created a new cluster "cluster_base_domain" with Member(Id=1, Timestamp=2023-06-14 14:27:27.664, Address=10.65.34.245:9000, MachineId=7674, Location=site:site_base_domain,rack:rack_base_domain,machine:machine_base_domain,process:process_base_domain,member:member_base_domain, Role=CoherenceServer, Edition=Grid Edition, Mode=Production, CpuCount=4, SocketCount=1)
<D5> (thread=Transport:TransportService, member=n/a): Service TransportService is bound to tmb://10.65.34.245:9000.39212
<Info> (thread=Transport:TransportService, member=n/a): Service TransportService joined the cluster with senior service member 1
<Info> (thread=main, member=n/a): Started cluster Name=cluster_base_domain, ClusterPort=7574


WellKnownAddressList(
  10.65.34.245
  )

```

사전 정의한 WKA List로 확인되며, Cluster 생성되어 `Created a new cluster "cluster_base_domain"` 메시지도 확인할 수 있다.

Cluster Port (Default 7574) Log도 확인된다.

<br>

**#1 - 정상 구성된 Member에 대한 Information 확인**

```
MasterMemberSet(
  ThisMember=Member(Id=1, Timestamp=2023-06-14 14:27:27.664, Address=10.65.34.245:9000, MachineId=7674, Location=site:site_base_domain,rack:rack_basee_domain,process:process_base_domain,member:member_base_domain, Role=CoherenceServer)
  OldestMember=Member(Id=1, Timestamp=2023-06-14 14:27:27.664, Address=10.65.34.245:9000, MachineId=7674, Location=site:site_base_domain,rack:rack_baase_domain,process:process_base_domain,member:member_base_domain, Role=CoherenceServer)
  ActualMemberSet=MemberSet(Size=1
    Member(Id=1, Timestamp=2023-06-14 14:27:27.664, Address=10.65.34.245:9000, MachineId=7674, Location=site:site_base_domain,rack:rack_base_domain,mprocess:process_base_domain,member:member_base_domain, Role=CoherenceServer)
    )
  MemberId|ServiceJoined|MemberState|Version
    1|2023-06-14 14:27:27.664|JOINED|14.1.1.0.0
  RecycleMillis=240000
  RecycleSet=MemberSet(Size=0
    )
  )

```

최초 구성인 만큼, 현재(ThisMember, Id=1)이 원로(oldestMember) 이기도 하다.

ActualMemberSet을 통해 현재 실제 구성을 알 수 있겠다.

Join 된 시점과 Coherence Version을 알 수 있다.

<br>

**#1 - TcpRing**

```
TcpRing{Connections=[]}
IpMonitor{Addresses=0, Timeout=2m5s}
```

Timeout은 ip-timeout * ip-attempts 정의한 대로, 2m5s 이며

TcpRing은 Cluster Member들을 엮는 것이나 Single 이므로 값이 없는 것으로 보인다.

<br>

**Second Cache Server(이하 #2) Startup**

```
<Info> (thread=main, member=n/a): TCMP bound to /10.65.34.245:9002 using TCPDatagramSocketProvider[Delegate: DemultiplexedSocketProvider(com.oracle.common.internal.net.MultiplexedSocketProvider@30b6ffe0)]
```

<br>


**#2 - Latency 보정**

```
<Info> (thread=Cluster, member=n/a): Failed to satisfy the variance: allowed=16, actual=58
<Info> (thread=Cluster, member=n/a): Increasing allowable variance to 21
```

물리적으로 같은 VM 이지만, 통신 시 Latency 지연이 있어, 둘 Member에서 인지하는 System Clock 에 차이가 있다며 이후 Message (Member간 주고받는 Data 를 의미하는 것으로 보임) 에 더 여유있게 Timeout을 주는 것으로 보인다.

[Failed to satisfy the variance: allowed=%n1 actual=%n2](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/administer/log-message-glossary.html#GUID-EA76C216-0977-44D5-92D1-E9561FF0D44B)

<br>

**#2 - Cluster 합류**

```
<Info> (thread=Cluster, member=n/a): Member(Id=1, Timestamp=2023-06-14 14:27:27.664, Address=10.65.34.245:9000, ...
<Info> (thread=Cluster, member=n/a): This Member(Id=2, Timestamp=2023-06-14 15:55:26.448, Address=10.65.34.245:9002, ...
```

기존 Member, 그리고 현재 합류하는 신규 Member Log가 확인된다.

<br>

```
<Info> (thread=Transport:TransportService, member=n/a): Service TransportService joined the cluster with senior service member 1
<Info> (thread=SelectionService(channels=5, selector=MultiplexedSelector(sun.nio.ch.EPollSelectorImpl@471a9022), id=231311211), member=n/a): Connection established with tmb://10.65.34.245:9000.39212
```

Senior  (Leader Member) 와 ESTABLISHED 되어, Cluster에 Joined

<br>

```
MasterMemberSet(
  ThisMember=Member(Id=2, Timestamp=2023-06-14 15:55:26.448, Address=10.65.34.245:9002, ...)
  OldestMember=Member(Id=1, Timestamp=2023-06-14 14:27:27.664, Address=10.65.34.245:9000, ...)
  ActualMemberSet=MemberSet(Size=2
    Member(Id=1, Timestamp=2023-06-14 14:27:27.664, Address=10.65.34.245:9000, ...)
    Member(Id=2, Timestamp=2023-06-14 15:55:26.448, Address=10.65.34.245:9002, ...)
    )
  MemberId|ServiceJoined|MemberState|Version
    1|2023-06-14 14:27:27.664|JOINED|14.1.1.0.0,
    2|2023-06-14 15:55:26.448|JOINED|14.1.1.0.0
  RecycleMillis=240000
  RecycleSet=MemberSet(Size=0
    )
  )
  
TcpRing{Connections=[1]}
IpMonitor{Addresses=0, Timeout=2m5s}
```

이전에 본 Log 형태와 같이, 현재(ThisMember)가 합류되었다.

TcpRing의 Array.Length 와 같이 확인된다.

<br>

**#1과 #2 - Socket LISTEN**

```sh
$ sudo netstat -anp | egrep "9000|9002" | grep "LISTEN"
tcp        0      0 192.168.122.1:9000      0.0.0.0:*               LISTEN      <#1 PID>/java
tcp        0      0 127.0.0.1:9000          0.0.0.0:*               LISTEN      <#1 PID>/java
tcp        0      0 10.65.34.245:9000       0.0.0.0:*               LISTEN      <#1 PID>/java
tcp        0      0 192.168.122.1:9002      0.0.0.0:*               LISTEN      <#2 PID>/java
tcp        0      0 127.0.0.1:9002          0.0.0.0:*               LISTEN      <#2 PID>/java
tcp        0      0 10.65.34.245:9002       0.0.0.0:*               LISTEN      <#2 PID>/java
```

#1, #2 Cache Server 의 Port가 모든 NIC에서 열린다.

이는, **Coherence Process Listens On All Interfaces Of The Machine, Why? (Doc ID 2143520.1)** 참고하여 Discovery-Address 를 지정해야 한다.

<br>

**#1과 #2 - Socket ESTABLISHED**

```sh
$ sudo netstat -anp | egrep "9000|9002" | grep "ESTABLISHED"

--- below is connected #1 to #2 ---
tcp        0      0 10.65.34.245:9000       10.65.34.245:29850      ESTABLISHED <#1 PID>/java
tcp        0      0 10.65.34.245:29850      10.65.34.245:9000       ESTABLISHED <#2 PID>/java

tcp        0      0 10.65.34.245:9000       10.65.34.245:29852      ESTABLISHED <#1 PID>/java
tcp        0      0 10.65.34.245:29852      10.65.34.245:9000       ESTABLISHED <#2 PID>/java


--- below is connected #2 to #1 ---
tcp        0      0 10.65.34.245:9002       10.65.34.245:58602      ESTABLISHED <#2 PID>/java
tcp        0      0 10.65.34.245:58602      10.65.34.245:9002       ESTABLISHED <#1 PID>/java

tcp        0      0 10.65.34.245:9002       10.65.34.245:58614      ESTABLISHED <#2 PID>/java
tcp        0      0 10.65.34.245:58614      10.65.34.245:9002       ESTABLISHED <#1 PID>/java


tcp        0      0 10.65.34.245:9002       10.65.34.245:58628      ESTABLISHED <#2 PID>/java
tcp        0      0 10.65.34.245:58628      10.65.34.245:9002       ESTABLISHED <#1 PID>/java

tcp        0      0 10.65.34.245:9002       10.65.34.245:58636      ESTABLISHED <#2 PID>/java
tcp        0      0 10.65.34.245:58636      10.65.34.245:9002       ESTABLISHED <#1 PID>/java
```

Understanding TCMP 의 Protocol Resource Utilization Section에 따라 TCP/IP 기반의 이점과 그 자체로 인해 ESTABLISHED가 많이 목격 될 수 있을 것이다. 

**Observing High Number of Unicast Connections in Coherence (Doc ID 2799453.1)** 참고

<br>

**Third Cache Server(이하 #3) Startup**

```
  MemberId|ServiceJoined|MemberState|Version
    1|2023-06-14 14:27:27.664|JOINED|14.1.1.0.0,
    2|2023-06-14 15:55:26.448|JOINED|14.1.1.0.0,
    3|2023-06-14 17:34:54.898|JOINED|14.1.1.0.0
  RecycleMillis=240000
  RecycleSet=MemberSet(Size=0
    )
  )

TcpRing{Connections=[2]}
IpMonitor{Addresses=0, Timeout=2m5s}
```

익숙한 Log 중에 하나로써, #1 ~ #3 Member Listup 을 알 수 있다.

<br>

**#1 - TcpRing Disconnected to maintain ring**

```
<Info> (thread=Cluster, member=1): TcpRing disconnected from Member(Id=2, Timestamp=2023-06-14 15:55:26.448, Address=10.65.34.245:9002, ...) to maintain ring
```

TcpRing 은 이름 그대로, Member의 첫 부분부터 끝까지 Ring 형태로 이루어진 듯 싶다. 그래서 구조가 변경된다.

이후 #4에 해당하는 Fourth 기동을 해보니, 구조가 변경된다. TcpRing 의 Array Alignment는 위 Table 과 같다.


<br><br>


# 3. HeartBeat

HeartBeat 통신이 진행될 때 남는 로그들, 잘 안될때 로그들


<br><br>


# 4. TcpRing

TcpRing 메시지를 log 살피고,, 통신에 어떤 문제가 있을 때 어떻게 되는지?


<br><br>


# 5. GC

짧은/매우 긴/혹은 짧더라도 자주 반복되는? GC 와 같은 상황이 발생하면 어떤 변화가? Leader 에 문제가 생기는 경우? Leader는 어떤 패턴으로 누가 후임자가 되는지?


<br><br>

<br>

# 5. References

**How to Specify Unicast WKA Address and WKA Port in Coherence 12.2.1.4 or 14c Cluster Operational Override File (Doc ID 2820437.1)**

**Coherence Process Listens On All Interfaces Of The Machine, Why? (Doc ID 2143520.1)**

**Observing High Number of Unicast Connections in Coherence (Doc ID 2799453.1)**

[Specifying a Cluster's Multicast Address and Port](https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/develop-applications/setting-cluster.html#GUID-D3FDEDBF-B97A-4C8D-BEFF-AB54C9D94CB5)

[Understanding TCMP](https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/develop-applications/introduction-coherence-clusters.html#GUID-318CDF30-5B40-4E87-98F2-9C5F1E428B6E)

[Log Message Glossary](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/administer/log-message-glossary.html#GUID-EA76C216-0977-44D5-92D1-E9561FF0D44B)
