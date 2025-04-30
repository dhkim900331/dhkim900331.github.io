---
date: 2025-04-30 23:47:17 +0900
layout: post
title: "[Coherence] Coehrence Console Application"
tags: [Coherence, Tool, CLI]
typora-root-url: ..
---

# 1. Overview

Coherence 12cR2 Console Application 기본 사용 방법


<br><br>


# 2. Descriptions

client.sh 구성

```sh
#!/bin/sh
JAVA_HOME=/sw/jdk/jdk1.8.0_421
DOMAIN_NAME=base_domain
DOMAIN_HOME=/sw/coherence/12cR2/domains/base_domain

JAVA_OPTS="${JAVA_OPTS} -Dcoherence.mode=prod"
JAVA_OPTS="${JAVA_OPTS} -Dcoherence.cacheconfig=session-cache-config.xml"
JAVA_OPTS="${JAVA_OPTS} -Dcoherence.override=tangosol-coherence-${DOMAIN_NAME}.xml"
export JAVA_OPTS

CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib"
CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib/coherence-web.jar"
CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib/coherence.jar"
export CLASSPATH

${JAVA_HOME}/bin/java -server -showversion $JAVA_OPTS -cp ${CLASSPATH} com.tangosol.net.CacheFactory $1
```

<br>

`session-cache-config.xml` 에 정의된 cache 항목 중 HttpSession 인 다음을 검색할 것이다.

```xml
    <cache-mapping>
      <cache-name>session-storage</cache-name>
      <scheme-name>session-distributed</scheme-name>
    </cache-mapping>
```

<br>

client.sh 실행 하여 기존 클러스터 그룹에 가입한다. (나는 Id=4)

```sh
(thread=main, member=n/a): Loaded operational configuration from "jar:file:/sw/coherence/12cR2/domains/base_domain/lib/coherence.jar!/tangosol-coherence.xml"
(thread=main, member=n/a): Loaded operational overrides from "jar:file:/sw/coherence/12cR2/domains/base_domain/lib/coherence.jar!/tangosol-coherence-override-prod.xml"
(thread=main, member=n/a): Loaded operational overrides from "file:/sw/coherence/12cR2/domains/base_domain/lib/tangosol-coherence-base_domain.xml"

MasterMemberSet(
  ThisMember=Member(Id=4, Timestamp=2025-04-15 16:44:37.077, ...)
  OldestMember=Member(Id=1, Timestamp=2025-04-15 16:30:20.699, ...)
  ActualMemberSet=MemberSet(Size=3
    Member(Id=1, Timestamp=2025-04-15 16:30:20.699, ...)
    Member(Id=2, Timestamp=2025-04-15 16:31:11.432, ...)
    Member(Id=4, Timestamp=2025-04-15 16:44:37.077, ...)
    )
  MemberId|ServiceJoined|MemberState|Version
    1|2025-04-15 16:30:20.699|JOINED|12.2.1.4.0,
    2|2025-04-15 16:31:11.432|JOINED|12.2.1.4.0,
    4|2025-04-15 16:44:37.077|JOINED|12.2.1.4.0
  RecycleMillis=1200000
  RecycleSet=MemberSet(Size=1
    Member(Id=3, Timestamp=2025-04-15 16:42:35.945, Address=10.65.34.108:9003, MachineId=7674)
    )
  )
```

<br>

`session-storage` cache 에 접속

```sh
Map (?): cache session-storage

(thread=main, member=5): Loaded cache configuration from "file:/sw/coherence/12cR2/domains/base_domain/lib/session-cache-config.xml"
(thread=main, member=5): Created cache factory com.tangosol.net.ExtensibleConfigurableCacheFactory
(thread=DistributedCache:oracle.coherence.web:DistributedSessions, member=5): Service oracle.coherence.web:DistributedSessions joined the cluster with senior service member 1

Cache Configuration: session-storage
  SchemeName: session-distributed
  AutoStart: true
  ScopeName: oracle.coherence.web
  ServiceName: DistributedSessions
  ServiceDependencies
    EventDispatcherThreadPriority: 10
    RequestTimeoutMillis: 30000
    ThreadPriority: 10
    WorkerThreadsMax: 2147483647
    WorkerThreadsMin: 1
    WorkerPriority: 5
    ActionPolicyBuilder
      RulesArray (ArrayList of QuorumRule)
        [0]
          RuleElementName: distribution-quorum
          RuleMask: 1
        [1]
          RuleElementName: restore-quorum
          RuleMask: 2
        [2]
          RuleElementName: recover-quorum
          RuleMask: 16
        [3]
          RuleElementName: read-quorum
          RuleMask: 4
        [4]
          RuleElementName: write-quorum
          RuleMask: 8
    Backups: 1
    DistributionAggressiveness: 20
    DistributionSynchronized: true
    Partitions: 257
    BldrsPartitionListener
    AssignmentStrategyBuilder
      Strategy: simple
    TransferThreshold: 524288
    DepsPersistence
      PersistenceBuilder: Mode: on-demand
        Active Location: /home/weblogic/coherence/active
        Snapshot Location:/home/weblogic/coherence/snapshots
        Trash Location:/home/weblogic/coherence/trash
    LeaseGranularity: 1
    StrictPartitioning: true
  BackingMapScheme
    ScopeName: oracle.coherence.web
    InnerScheme (RamJournalScheme)
      ScopeName: oracle.coherence.web
      UnitCalculatorBuilder
        Calculator: BINARY
      UnitFactor: 1

Map (session-storage):
```

<br>

다음 명령으로 cache 목록 확인도 가능하다. (overflow는 큰 객체 사이즈만 저장되는 공간)

```sh
Map (session-storage): maps
oracle.coherence.web:DistributedSessions:session-storage
oracle.coherence.web:DistributedSessions:session-overflow
```


<br><br>


두 명의 사용자가 Session.jsp 등을 실행하여 각기 세션을 만들면, size 명령을 통해서 객체 갯수 확인

```
Map (session-storage): size
2
```


<br><br>


CohQL 을 사용하는 것이 효율적으로 보이는데, HttpSession 객체의 value() 는 보여지지가 않는다.

원래 그러한지, 잘못된 테스트 방식인지 모르겠다.

우선 나중을 위해 정리하면

<br>

아래의 client로 실행

```
#!/bin/sh
JAVA_HOME=/sw/jdk/jdk1.8.0_421
DOMAIN_NAME=base_domain
DOMAIN_HOME=/sw/coherence/12cR2/domains/base_domain

JAVA_OPTS="${JAVA_OPTS} -Dcoherence.mode=prod"
JAVA_OPTS="${JAVA_OPTS} -Dcoherence.cacheconfig=session-cache-config.xml"
JAVA_OPTS="${JAVA_OPTS} -Dcoherence.override=tangosol-coherence-${DOMAIN_NAME}.xml"
export JAVA_OPTS

CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib"
CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib/coherence-web.jar"
CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib/coherence.jar"
CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib/jline.jar"
export CLASSPATH

${JAVA_HOME}/bin/java -server -showversion $JAVA_OPTS -cp ${CLASSPATH} com.tangosol.coherence.dslquery.QueryPlus $1
```

<br>

다음의 명령어들로 cache 접속 및 cache 검색

```
> ensure cache 'session-storage'
> services info (서비스 목록 보는 방법)
> select * from 'session-storage'
> select key(), value() from 'session-storage'

```

<br>

key() 는 잘나오나, value() 가 안나옴. 에러 debug log 를 보면 알려나?

사례도 ㄱ거의 없음. RFA 열어야 하나?

<br>

# 3. References

How To Use Coherence Client Application To Backup and Restore A Cache? (Doc ID 2344741.1)

How Can Large HTTP Sessions Be Identified In The Coherence\*Web Session Management For An Application Server, WebLogic? (Doc ID 1980732.1)	
How to Query the Coherence*Web session-storage cache in the 12.2.1.x.x versions (Doc ID 2323536.1)	
