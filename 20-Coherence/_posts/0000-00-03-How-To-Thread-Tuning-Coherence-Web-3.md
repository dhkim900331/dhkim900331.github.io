---
date: 2023-02-02 08:58:49 +0900
layout: post
title: "[Coherence] How to Thread Tuning Coherence Web 3.X"
tags: [Coherence, Thread, Tuning]
typora-root-url: ..
---

# 1. 개요

해당 버전에서, Reaper Thread 성능 개선을 위해 Thread Tuning 을 살펴본다.



# 2. 설명

주기적 Session을 Scan하여 Timeout 된 객체는 invalidate 하여 IsValid=False로 변경하는 Reaper Thread에 대해서, 심플한 부하 테스트를 진행하여 성능 개선이 이뤄지는지 살펴본다.



# 3. 테스트 환경

* OS : Oracle Linux Server release 8.7
* JDK : 1.7.0_80
* WebLogic 11g
* Coherence 3.7.1.22 * WEB SPI



## 3.1 Test #1

* Test 기본 조건

  * Jmeter, 120 Secs, 50 Users
    * Jmeter를 이용하여 120초 동안, 50 Users 동시 접속으로 생성한 세션

  * 평균 MBean 데이터가 있기 때문에, 
    120초 동안 부하 인입이 완료된 후, SessionUpdate(생성된 세션 개수)와, ReapedSessionsTotal(Invalidate 된 세션 개수)이 거의 근접한 경우의 통계치를 얻는다.



### 3.1.1 Case #1

SessionUpdates 13826
ReapedSessionsTotal 13826
MaxReapDuration 18265
AverageReapedSessions 4608
MaxReapedSessions 11733
AverageReapDuration 40136



### 3.1.2 Case #2

SessionUpdates 15274
ReapedSessionsTotal 15273
MaxReapDuration 15173
AverageReapedSessions 5091
MaxReapedSessions 9828
AverageReapDuration 48317



### 3.1.3 Case #3

SessionUpdates 14596
ReapedSessionsTotal 14596
MaxReapDuration 15173
AverageReapedSessions 4865
MaxReapedSessions 8248
AverageReapDuration 56418



## 3.2 Test #2 (테스트 조건 계승)

* Work Manager

  - ```xml
      <self-tuning>
        <min-threads-constraint>
          <name>MinThreadsConstraint-0</name>
          <target>M1</target>
          <count>4</count>
        </min-threads-constraint>
        <max-threads-constraint>
          <name>MaxThreadsConstraint-0</name>
          <target>M1</target>
          <count>4</count>
        </max-threads-constraint>
        <work-manager>
          <name>wm/CoherenceWorkManager</name>
          <target>M1</target>
          <min-threads-constraint>MinThreadsConstraint-0</min-threads-constraint>
          <max-threads-constraint>MaxThreadsConstraint-0</max-threads-constraint>
        </work-manager>
      </self-tuning>
    ```



### 3.2.1 Case #1

SessionUpdates 15412
ReapedSessionsTotal 15412
MaxReapDuration 54821
AverageReapedSessions 3855
MaxReapedSessions 7750
AverageReapDuration 23510



### 3.2.2 Case #2

SessionUpdates 15177
ReapedSessionsTotal 15177
MaxReapDuration 48267
AverageReapedSessions 3794
MaxReapedSessions 7876
AverageReapDuration 21855



### 3.2.3 Case #3

SessionUpdates 16188
ReapedSessionsTotal 16189
MaxReapDuration 39550
AverageReapedSessions 3237
MaxReapedSessions 7870
AverageReapDuration 43719



Case #1, #2와 달리, 수치가 좀 비약적으로 높거나 한데, 당시 시스템에 다음과 같은 에러 메시지가 발생하였다.

```
Exception in thread "[ACTIVE] ExecuteThread: '0' for queue: 'weblogic.kernel.Default (self-tuning)'" java.lang.RuntimeException: MaxThreads constraint 'MaxThreadsConstraint-0' queue for workManager 'wm/CoherenceWorkManager' exceeded maximum capacity of '8192' elements. Max threads constraint count is set to 4
        at weblogic.work.MaxThreadsConstraint.add(MaxThreadsConstraint.java:117)
        at weblogic.work.MaxThreadsConstraint$1.unbox(MaxThreadsConstraint.java:41)
        at weblogic.work.MaxThreadsConstraint$1.unbox(MaxThreadsConstraint.java:22)
        at weblogic.work.CalendarQueue.pop(CalendarQueue.java:200)
        at weblogic.work.RequestManager.executeWorkFromPriorityQueue(RequestManager.java:629)
        at weblogic.work.RequestManager.registerIdle(RequestManager.java:458)
        at weblogic.work.ExecuteThread.run(ExecuteThread.java:224)
```



확인 결과, `MaxThreadsConstraint-0` 의 최대치에 돌입한 경우, 잔여 작업이 Queue에 8192 만큼 도달하는 경우 경고 메시지가 발생하도록 Design 되었다고 한다. (WorkManager 사용 시 단점..?)

해당 에러가 발생하는 시점마다 통계치가 이상하여, 인스턴스 Shutdown 또한 제대로 되지 않는 등의 side-effect 가 있다.

더 많은 부하가 들어올 것으로 예상되는 운영 환경에서는, MaxThreads를 제거하기에는 부담이 크니, MaxThreads를 더 크게 설정하거나 Queue Size를 늘려주는 방법이 필요하겠다.

Queue Size를 변경하고자 하였으나, 11g 이후로는 8192 Hard conding 된 것으로 확인된다. 

**"Exceeded maximum capacity of '8192' elements" exception When Using MaxThreads Constraint in WLS 10.3.6+ (Doc ID 1470870.1)** 문서를 참고하여 PSU 최신 패치만을 적용하였다.

_queue-size(16384) 또한 config.xml 적용했으나, Exception 없이 8192 제한값에 도달하였다는 메시지는 나오고 있다._

```
<Info> <WorkManager> <BEA-002936> <maximum thread constraint MaxThreadsConstraint-0 is reached>
<Warning> <WorkManager> <BEA-002943> <Maximum Threads Constraint "MaxThreadsConstraint-0" queue for work manager "wm/CoherenceWorkManager" reached maximum capacity of 8,192 elements. Please consider setting a larger queue size for the maximum threads constraint.>
```



Case #4~#5은 패치 이후 테스트이다.



### 3.2.4 Case #4

SessionUpdates 18158
ReapedSessionsTotal 16063
MaxReapDuration 48243
AverageReapedSessions 4539
MaxReapedSessions 8306
AverageReapDuration 48220



### 3.2.5 Case #5

SessionUpdates 16329
ReapedSessionsTotal 16328
MaxReapDuration 49653
AverageReapedSessions 5442
MaxReapedSessions 8284
AverageReapDuration 96043



## 3.3 Test #3 (계승)

* Test #2 에서 WorkManager Queue 이슈로 인한 것인지, 간혹 결과, 특히 AverageReapDuration 이 이상한 경우가 발생을 하여, 추가로 MaxThreads를 대폭 늘린 후 테스트 해본다. (queue-size가 늘어지나지 않으므르...)
  * `MaxThreadsConstraint-0 is 10`



### 3.3.1 Case #1

SessionUpdates 15434
ReapedSessionsTotal 14027
MaxReapDuration 28739
AverageReapedSessions 5145
MaxReapedSessions 8117
AverageReapDuration 17412



### 3.3.2 Case #2

SessionUpdates 16252
ReapedSessionsTotal 13982
MaxReapDuration 20657
AverageReapedSessions 5417
MaxReapedSessions 8363
AverageReapDuration 32363



아래 메시지 발생을 한 시점이며, AvgReapDuration이 치솟았다.

```
<Warning> <WorkManager> <BEA-002943> <Maximum Threads Constraint "MaxThreadsConstraint-0" queue for work manager "wm/CoherenceWorkManager" reached maximum capacity of 8,192 elements. Please consider setting a larger queue size for the maximum threads constraint.>
```



이 환경에서, 동일한 테스튼 의미가 없는 것 같다.

Queue-Size를 늘리는 것을 계속 고민하였지만, 위 테스트 시나리오를 보다시피 대략 2분 동안 항시 1만6천개 정도의 세션을 생성했는데, 이는 1초당 133 개의 세션 생성이 되는 것과 같다.

매우 큰 부하로 가정하면, queue-size를 늘려서 까지 부하 테스트를 하는 것에 의미가 없을 수 있으므로

오히려 접속되는 사용자를 낮추어 queue 이슈를 제거하여 순수 Reaper Thread 성능만 보는것이 맞는것 같다.



## 3.4 Test #4 (계승)

* Test 기본 조건
  * Jmeter, 120 Secs, 20 Users
    * 50 Users가 2분간 1만6천개인것을 감안하면, 20 Users는 Queue-Size를 넘지 않도록 반토막이 안될 것이다.



### 3.4.1 Case #1

SessionUpdates 5484
ReapedSessionsTotal 4578
MaxReapDuration 17161
AverageReapedSessions 1144
MaxReapedSessions 3060
AverageReapDuration 7832



### 3.4.2 Case #2

SessionUpdates 6437
ReapedSessionsTotal 4599
MaxReapDuration 10381
AverageReapedSessions 1533
MaxReapedSessions 2689
AverageReapDuration 13008



## 3.5 Test #5 (계승, 변경)

* `MaxThreadsConstraint-0 is 4` 로 복원하여 진행한다.



### 3.5.1 Case #1

SessionUpdates 5850
ReapedSessionsTotal 4904
MaxReapDuration 14604
AverageReapedSessions 1634
MaxReapedSessions 2678
AverageReapDuration 7244



### 3.5.2 Case #2

SessionUpdates 6596
ReapedSessionsTotal 5921
MaxReapDuration 16638
AverageReapedSessions 1973
MaxReapedSessions 3080
AverageReapDuration 16475





# 4. Outcome

테스트 환경의 조건이 꽤나 조잡한 것 같다.

다시 기회를 가져서, 오랜 시간 running 되는 환경에서 AvgReapDuration, CPU 부하까지 뽑아 내는 것이 의미가 있어 보인다.

그러나, 위 여러 시나리오의 결과를 보면 WorkManager를 구현만 하여도 최소 1.5배 이상은 지연이 개선되는 것으로 보여진다.
