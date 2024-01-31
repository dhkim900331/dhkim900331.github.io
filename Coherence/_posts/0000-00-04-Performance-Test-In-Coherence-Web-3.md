---
date: 2023-02-02 08:58:49 +0900
layout: post
title: "[Coherence/Web] Performance Test In Coherence Web 3.X"
tags: [Coherence, Web, Thread, Tuning, Performance, Test, WLST, Python]
typora-root-url: ..
---

# 1. 개요

[How-To-Thread-Tuning-Coherence-Web-3](How-To-Thread-Tuning-Coherence-Web-3) 에서 몇가지 간단한 부하테스트와 함께, 튜닝에 효과가 있는지 살펴보았는데, 테스트 방식이 조잡하여 이번에 좀 더 정규화 과정으로 스크립트를 사용해본다.



# 2. 설명

주기적 Session을 Scan하여 Timeout 된 객체는 invalidate 하여 IsValid=False로 변경하는 Reaper Thread에 대해서, 오랜시간 부하 테스트를 진행하여 성능 개선이 이뤄지는지 살펴본다.



# 3. 테스트 환경

* OS : Oracle Linux Server release 8.7
* JDK : 1.7.0_80
* WebLogic 11g
* Coherence 3.7.1.22 * WEB SPI



* JMeter
  * 지속적으로 20 Users 부하를 주며, 빠르게 New Sessoin 생성



* Monitoring Script

  * 다음의 Script로 데이터를 추출하여 통계를 내본다.

  * ```python
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
    
    
    gap = 5000
    for idx in range(0, 100):
            ###### print MBeans ######
            ### Attr to Var ###
            # Reaper Cycle
            NextReapCycle = str(get('NextReapCycle'))
            LastReapCycle = str(get('LastReapCycle'))
    
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
    
    
            ### Var to Log ###
            dm = " | "
            writeLogData = str(idx) + dm
            writeLogData += NextReapCycle + dm
            writeLogData += LastReapCycle + dm
    
            writeLogData += AverageReapDuration + dm
            writeLogData += LastReapDuration + dm
            writeLogData += MaxReapDuration + dm
    
            writeLogData += AverageReapedSessions + dm
            writeLogData += MaxReapedSessions + dm
            writeLogData += ReapedSessions + dm
            writeLogData += ReapedSessionsTotal + dm
    
            writeLogData += SessionUpdates
    
            fo.write(writeLogData+"\n")
            fo.flush()
            print(writeLogData)
            Thread.sleep(gap)
    
    fo.close()
    exit()
    
    ```



# 4. Performance Test

Jmeter 20 Users 가 지속적으로 세션을 생성하는 과정에서, 위 스크립트로 자료를 모아 엑셀로 평균을 뽑아 보았다.



![Performance-Test-In-Coherence-Web-3_1](/../assets_copy_final/posts/images/Coherence/Performance-Test-In-Coherence-Web-3/Performance-Test-In-Coherence-Web-3_1.png)





Row 순서대로, `wm/CoherenceWorkManager` 의 Min/MaxThreads를 4, 8, 16 순으로 유사하게 테스트한 결과의 평균치이다.



AverageReapDuraton, Threads가 증가할 수록 전체적으로 Reap Duration이 감소되었다.

LastReapDuration, 가장 최근의 Reap Duration

MaxReapDuration, 가장 높은 Reap Duration

AverageReapedSessions, 평균 Reaped 되는 Session 수, Threads가 늘었음에도 변화가 없다.

MaxReapedSessions, 가장 높은 Reaped 된 Session 수, Threads가 늘었음에도 변화가 없다.

ReapedSessions, 가장 최근에 Reaped 된 Session 수, Threads가 늘었음에도 변화가 없다.

ReapedSessionsTotal, 지금까지 총 Reaped 된 Session 수, Threads가 늘었음에도 변화가 없다.

SessionUpdates, Jmeter로 총 밀어넣은 Session 수



# 5. Outcome

위 스크립트는 5sec마다 수집하고, Reaper Thread의 주기(cycle)은 40초로, 약간 Missmatch 로 보여지는 테스트긴 하지만, Thread가 늘어남에 따라 Reap Duration이 상당히 개선되는 것이 확인된다.

다만, 이 당시에 CPU,MEM 사용률을 체크를 안한 것이 신경은 쓰인다.

또한, 매 테스트 시마다 거의 동일한 Jmeter의 부하량이 들어가므로, `Threads가 늘었음에도 변화가 없다.` 라는 메시지는 정당성이 부여될 수 있을 것 같다.



# 6. References

* **Coherence Web Cache Montoring (Doc ID 2547017.1)**
* **How to Setup "Loop" and "Sleep" Wait in WLST Script (Doc ID 2860336.1)**
