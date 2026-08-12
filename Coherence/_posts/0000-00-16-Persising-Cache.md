---
date: 2026-02-23 13:44:30 +0900
layout: post
title: "[Coherence/Cache] Persisting Cache for HttpSession"
tags: [Coherence, Cache, Session]
typora-root-url: ../..
---


# 1. Overview
Coherence 12.2.1.4 에서 Persisting Cache는 Cache Data를 Local File로 저장 할 수 있게 한다.
HttpSession 데이터를 저장하는 가이드를 제공함으로써, Cache 기능을 살펴본다.

Active 방식은, Cache를 지속적으로 File로 저장하는 것이고,
On-Demand 방식은 사용자가 수동으로 요청 시, 그 시점의 Snapshot을 생성하고 불러들여 복구/관리 하는 방식이다.
Active 방식에도 Snapshot 기능은 제공된다.

# 2. Descriptions
`ss-active` id 를 갖는 Active Cache 사용 시, 저장되는 디렉터리를 `tangosol-coherence-base_domain.xml` 와 같은 Operational override 에 지정한다.
기본값은 사용자 계정 디렉터리이다.

```xml
 <cluster-config>

   <persistence-environments>
      <persistence-environment id="ss-active">
         <active-directory
           system-property="coherence.distributed.persistence.active.dir">
           /sw/coherence/12cR2/domains/base_domain/persistence/active</active-directory>
         <snapshot-directory
           system-property="coherence.distributed.persistence.snapshot.dir">
           /sw/coherence/12cR2/domains/base_domain/persistence/snapshot</snapshot-directory>
         <trash-directory
           system-property="coherence.distributed.persistence.trash.dir">
           /sw/coherence/12cR2/domains/base_domain/persistence/trash</trash-directory>
      </persistence-environment>
   </persistence-environments>
    ...
```

사용하는 Cache (`session-cache-config.xml`)에 위 id를 부여한다.
```xml
    ...
    
   <cache-mapping>
     <cache-name>session-storage</cache-name>
     <scheme-name>session-distributed</scheme-name>
   </cache-mapping>
    
    ...
    
   <distributed-scheme>
     <scheme-name>session-distributed</scheme-name>
     <service-name>DistributedSessions</service-name>
     <lease-granularity>member</lease-granularity>
     <local-storage system-property="coherence.session.localstorage">false</local-storage>
     <partition-count>257</partition-count>
     <backup-count>1</backup-count>
     <request-timeout>30s</request-timeout>
     <backing-map-scheme>
       <ramjournal-scheme>
          <high-units system-property="coherence.session.highunits"/>
          <unit-calculator>BINARY</unit-calculator>
       </ramjournal-scheme>
     </backing-map-scheme>
     <persistence>
       <environment>ss-active</environment>        # << added
     </persistence>
     <autostart>true</autostart>
   </distributed-scheme>
```

`-Dcoherence.distributed.persistence.mode=active` 옵션으로 활성화 하고, 아래와 같이 로그가 기록된다.
첫번째 로그는, 내가 지정한 경로에 저장되고 그 외는 두번째 로그처럼 사용자 계정 디렉터리에 저장된다.
```
2026-01-07 12:03:04.436/6.308 Oracle Coherence GE 12.2.1.4.26 <Info> (thread=DistributedCache:oracle.coherence.web:DistributedSessions, member=9): Created persistent store /sw/coherence/12cR2/domains/base_domain/persistence/active/cluster_base_domain/oracle-coherence-web-DistributedSessions/0-9-19b96686720-9 from SafeBerkeleyDBStore(0-8-19b9667bd5d-8, /sw/coherence/12cR2/domains/base_domain/persistence/active/cluster_base_domain/oracle-coherence-web-DistributedSessions/0-8-19b9667bd5d-8)
...

2026-01-07 12:03:04.458/6.330 Oracle Coherence GE 12.2.1.4.26 <Info> (thread=DistributedCache:oracle.coherence.web:DistributedSessionsHeapOnly, member=9): Created persistent store /home/weblogic/coherence/active/cluster_base_domain/oracle-coherence-web-DistributedSessionsHeapOnly/2-c-19b96686802-9 from SafeBerkeleyDBStore(2-b-19b9667be49-8, /home/weblogic/coherence/active/cluster_base_domain/oracle-coherence-web-DistributedSessionsHeapOnly/2-b-19b9667be49-8)
...
```

* partition-count 옵션 (257) 만큼 생성됨
* 첫번째 로그는 ss-active 설정한 경로에 생성되며, 그 외는 두번째 로그와 같이 계정 홈디렉터리가 기본 경로로 잡힘

사용되는 Local disk usage는 JConsole로 모니터링 할 수 있다.
```
JConsole MBean > Coherence > Service > "oracle.coherence.web:DistributedSessions" > {node id} > Attributes
    PersistenceActiveSpaceAvailable
    PersistenceActiveSpaceUsed
    PersistenceActiveSpaceTotal
```

세션이 생성되는 만큼, 세션 크기+ (Overhead) 보다 더 Disk 쓰기가 된다.
세션이 삭제된다고 하여, Disk 공간이 확보되지 않는다.
Cache Server에 파일로 세션이 저장되는 것인데, 세션 타임아웃이 만료되기 전이라면 Cache Server 재시작 후에도 복구되는 것이 확인된다.

```
Peak 시 세션 전체 크기가 최대 2GB 예상된다면, 캐시를 위해서 로컬 디스크는 최소 2GB+ 가 필요하다.
디스크에 저장될 때, 데이터를 위한 메타데이터가 추가로 붙고 jdb 파일이 10MB 단위로 관리되고 사용되지 않았을 때 삭제되는 것까지 고려하면
오버헤드가 꽤 붙는다. (설명에서는 10~30%)

정확한 계산방식이 제공되는 것이 아니고, 디스크 사용량을 보아가며 관리해야 되기 때문에 최대값 예측은 어느정도는 가능하다.

또한, active로 인해 생성되는 캐시들의 파일 삭제가 jdb 파일의 관리방식에 따라 자동으로 진행되므로 사용자의 선택에 의한 삭제가 되지 않다.
```

# 3. References
https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/administer/persisting-caches.html#GUID-4BE79056-182F-4D12-BF6B-4CBA3461C86D
https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/administer/persisting-caches.html#GUID-A73B6C59-2A17-45DB-80EA-56C86C3CEB06
https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/manage/oracle-coherence-mbeans-reference.html#GUID-0C5A3074-50D1-4B15-A4C2-E014E5F4827B
https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/administer/persisting-caches.html#GUID-1848628D-5423-4167-93F0-61196B4C35FE
https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/administer/persisting-caches.html#GUID-5C2FA66A-2A6B-441A-A54E-322196C1E967
