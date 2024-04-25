---
date: 2024-01-31 13:27:29 +0900
layout: post
title: "[WebLogic] WLDF uses cpu resources highly"
tags: [Middleware, WebLogic, WLDF, cpu]
typora-root-url: ..
---

# 1. Overview
WLDF(WebLogic Server Diagnostic Framework)가 cpu resources를 많이 사용하는 이슈

{{ site.content.br_big }}

# 2. Descriptions
CPU resources 사용률이 높을 때 Thread dump 분석을 하면 아래와 같은 Thread가 문제점으로 확인된다.

```
"Thread-21" #60 prio=5 os_prio=0 tid=0x00007f7c500c3000 nid=0x875c9 runnable [0x00007f7c792e1000]
   java.lang.Thread.State: RUNNABLE
	at sun.misc.Unsafe.park(Native Method)
	- parking to wait for  <0x00000000f34895a0> (a java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject)
	at java.util.concurrent.locks.LockSupport.park(LockSupport.java:175)
	at java.util.concurrent.locks.AbstractQueuedSynchronizer$ConditionObject.await(AbstractQueuedSynchronizer.java:2039)
	at java.util.concurrent.LinkedBlockingQueue.take(LinkedBlockingQueue.java:442)
	at weblogic.utils.concurrent.JDK15ConcurrentBlockingQueue.take(JDK15ConcurrentBlockingQueue.java:89)
	at weblogic.store.internal.PersistentStoreImpl.getOutstandingWork(PersistentStoreImpl.java:879)
	at weblogic.store.internal.PersistentStoreImpl.synchronousFlush(PersistentStoreImpl.java:1279)
	at weblogic.store.internal.PersistentStoreImpl.run(PersistentStoreImpl.java:1271)
	at java.lang.Thread.run(Thread.java:750)
 

"[ACTIVE] ExecuteThread: '6' for queue: 'weblogic.kernel.Default (self-tuning)'" #30 daemon prio=5 os_prio=0 tid=0x00007f7c9065f000 nid=0x875a1 in Object.wait() [0x00007f7c7b5f8000]
   java.lang.Thread.State: BLOCKED (on object monitor)
	at java.lang.Object.wait(Native Method)
	at java.lang.Object.wait(Object.java:502)
	at weblogic.common.CompletionRequest.getResult(CompletionRequest.java:115)
	- locked <0x00000000e78d3918> (a weblogic.common.CompletionRequest)
	at weblogic.diagnostics.archive.wlstore.PersistentStoreDataArchive.readRecord(PersistentStoreDataArchive.java:714)
	- locked <0x00000000faf92ab8> (a weblogic.diagnostics.archive.wlstore.HarvestedPersistentStoreDataArchive)
	at weblogic.diagnostics.archive.wlstore.PersistentStoreDataArchive.readRecord(PersistentStoreDataArchive.java:681)
	at weblogic.diagnostics.archive.wlstore.PersistentStoreDataArchive.deleteDataRecords(PersistentStoreDataArchive.java:1323)
	- locked <0x00000000faf92ab8> (a weblogic.diagnostics.archive.wlstore.HarvestedPersistentStoreDataArchive)
	at weblogic.diagnostics.archive.wlstore.PersistentStoreDataArchive.retireOldestRecords(PersistentStoreDataArchive.java:1246)
	at weblogic.diagnostics.archive.DataRetirementByQuotaTaskImpl.performDataRetirement(DataRetirementByQuotaTaskImpl.java:92)
	at weblogic.diagnostics.archive.DataRetirementByQuotaTaskImpl.run(DataRetirementByQuotaTaskImpl.java:49)
	at weblogic.diagnostics.archive.DataRetirementTaskImpl.run(DataRetirementTaskImpl.java:276)
	at weblogic.work.SelfTuningWorkManagerImpl$WorkAdapterImpl.run(SelfTuningWorkManagerImpl.java:681)
	at weblogic.invocation.ComponentInvocationContextManager._runAs(ComponentInvocationContextManager.java:352)
	at weblogic.invocation.ComponentInvocationContextManager.runAs(ComponentInvocationContextManager.java:337)
	at weblogic.work.LivePartitionUtility.doRunWorkUnderContext(LivePartitionUtility.java:57)
	at weblogic.work.PartitionUtility.runWorkUnderContext(PartitionUtility.java:41)
	at weblogic.work.SelfTuningWorkManagerImpl.runWorkUnderContext(SelfTuningWorkManagerImpl.java:655)
	at weblogic.work.ExecuteThread.execute(ExecuteThread.java:420)
	at weblogic.work.ExecuteThread.run(ExecuteThread.java:360) 
```
{{ site.content.br_small }}
Thread dump에서 특정 Thread가 CPU resources를 많이 사용하는 것을 찾기 위해서는

Unexpected High CPU Usage with WebLogic Server (WLS) Support Pattern (Doc ID 779349.1) 문서를 참고한다.
{{ site.content.br_small }}
WLDF는 WLS Instance에서 제공되는 Applications 들의 진단 정보를 수집하기 위해 기본적으로 활성화 되어 있다.

WLDF에 의해 생성되는 DAT 파일이 점점 커짐에 따라 내부 record indexing 에서 CPU resources를 많이 사용한다.

(예, servers/data/store/diagnostics/WLS_DIAGNOSTICS000000.DAT)
{{ site.content.br_small }}
WLS*.DAT 파일을 삭제하고 재기동하면 CPU resources 부하 상황을 1차적으로 해결할 수 있다.
{{ site.content.br_small }}
WLDF 데이터 수집을 위해 동작하는 저 Threads 는 다음의 JVM Arguments 로 수집되는 WLDF 데이터 양을 줄일 수 있고, 데이터 Indexing 을 비활성화하여 부하를 감소시킬 수 있다.

```
-D_Offline_FileDataArchive=true
-Dcom.bea.wlw.netui.disableInstrumentation=true
-Dweblogic.connector.ConnectionPoolProfilingEnabled=false
```
{{ site.content.br_small }}
위 옵션은 WLDF 자체를 비활성화하지 않기 때문에 계속해서 WLS*.DAT 파일은 생성될 수 있기 때문에, 근본적으로 비활성화하기 위해서는 <Console - Diagnostics - Built-in Diagnostic Modules - {Server} - Low 값을 None> 적용을 한다.

{{ site.content.br_big }}

# 3. References

**SOA 12c: Admin Server thread at startup accesses the persistent store through PersistentStoreImpl.getOutstandingWork method (Doc ID 2378825.1)**

**AdminServer Hangs on Thread "weblogic.diagnostics.archive.wlstore.PersistentStoreDataArchive.readRecord" (Doc ID 2897235.1)**

**How to Prevent the 'WLS_DIAGNOSTICSxxxxxx.DAT' file (under the DOMAIN_NAME/servers/SERVER_NAME/data/store/diagnostics folder) From Growing Too Large (Doc ID 965416.1)**
