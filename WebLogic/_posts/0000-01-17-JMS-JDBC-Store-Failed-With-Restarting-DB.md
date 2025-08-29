---
date: 2025-08-29 12:22:37 +0900
layout: post
title: "[WebLogic/JMS] JMS JDBC Store Failed With Restarting DB"
tags: [Middleware, WebLogic, ]
typora-root-url: ..
---

# 1. Overview

DB 유지보수 작업의 일환으로 3분여간 재기동이 진행되었다.

JDBC Store를 사용하는 JMS Server는 Failed 되었다.

<br><br>


# 2. Descriptions

JMS Server는 Queue message를 저장하고 읽기 위해 기본으로 File store를 사용하고,

DB를 대상으로 하는 JDBC Store를 사용할 수 있다.

<br>

DB Restarting으로 인해 `Datasource는 DB 끊김 감지 -> 주기적으로 회복 시도 -> DB 정상화로 Datasource 다시 정상 준비 완료`의 단계를 자체적으로 가능하다.

이 Datasource를 바라보는 JMS JDBC Store는 Datasource가 회복되어도 Failed 상태로 남아 있을 수 있다.

관련 옵션은 `ReconnectRetryIntervalMillis`과 `ReconnectRetryPeriodMillis` 이다.

[공식 문서 참고](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/store/jdbc.html#GUID-35567842-57E0-4B6E-ADAF-9B802807270E)

<br>

WebLogic 12.2.1.4 기준으로 다음의 스크립트를 통해 JMS JDBC Store에 설정된 값을 확인한다.

```python
# -*- coding: utf-8 -*-
# 심플 WLST: JMSServer의 Store 재연결값 / CF send-timeout / 도메인 JDBC Store 재연결값
# - 함수/헬퍼 없음. WLST 기본 커맨드 + 루프만 사용

ADMIN_URL  = 't3://wls.local:8001'
ADMIN_USER = 'weblogic'
ADMIN_PASS = 'weblogic1'

# 빈 리스트([])면 전체 조회
JMSSERVER_FILTERS = ['DemoJMSServer_M1', 'DemoJMSServer_M2']  # [] -> all
JMSMODULE_FILTERS = ['DemoJMSModule']                          # [] -> all

connect(ADMIN_USER, ADMIN_PASS, ADMIN_URL)
serverConfig()

print '\n=== [JMSServer → PersistentStore (ReconnectRetry*)] ==='
jmsServers = cmo.getJMSServers() or []
for js in jmsServers:
    name = js.getName()
    if JMSSERVER_FILTERS and name not in JMSSERVER_FILTERS:
        continue
    store = js.getPersistentStore()  # None => Default File Store
    if store is None:
        print 'JMSServer=%s  Store=DEFAULT_FILE_STORE  Interval=N/A  Period=N/A' % name
    else:
        # 타입/값 출력(있으면)
        try:
            stype = store.getClass().getName()
        except:
            stype = 'Unknown'
        try:
            interval = store.getReconnectRetryIntervalMillis()
        except:
            interval = 'N/A'
        try:
            period = store.getReconnectRetryPeriodMillis()
        except:
            period = 'N/A'
        print 'JMSServer=%s  Store=%s  Type=%s  Interval=%s  Period=%s' % (
            name, store.getName(), stype, str(interval), str(period)
        )

print '\n=== [JMSModule / ConnectionFactory → send-timeout(ms)] ==='
mods = cmo.getJMSSystemResources() or []
for mod in mods:
    mname = mod.getName()
    if JMSMODULE_FILTERS and mname not in JMSMODULE_FILTERS:
        continue
    res = mod.getJMSResource()
    if res is None:
        print 'JMSModule=%s  (no JMSResource)' % mname
        continue
    cfs = res.getConnectionFactories() or []
    if not cfs:
        print 'JMSModule=%s  (no ConnectionFactories)' % mname
    for cf in cfs:
        jndi = ''
        try:
            jndi = cf.getJNDIName()
        except:
            pass
        # send-timeout은 DefaultDeliveryParams 아래에 있음
        send_to = 'N/A'
        try:
            ddp = cf.getDefaultDeliveryParams()
            if ddp is not None:
                send_to = ddp.getSendTimeout()
        except:
            # (드물게) 구버전 호환
            try:
                send_to = cf.getSendTimeout()
            except:
                pass
        print 'JMSModule=%s  CF=%s  JNDI=%s  send-timeout(ms)=%s' % (
            mname, cf.getName(), jndi, str(send_to)
        )

print '\n=== [Domain-level JDBC Stores (not only those attached to JMSServer)] ==='
jdbcStores = cmo.getJDBCStores() or []
for st in jdbcStores:
    sname = st.getName()
    try:
        ival = st.getReconnectRetryIntervalMillis()
    except:
        ival = 'N/A'
    try:
        pval = st.getReconnectRetryPeriodMillis()
    except:
        pval = 'N/A'
    print 'JDBCStore=%s  Interval=%s  Period=%s' % (sname, str(ival), str(pval))

print '\n=== DONE ==='
```

<br>

확인 결과, JDBC Store의 두 옵션은 각각 200ms / 1000ms 이다.

공식 문서 내용을 보면 알겠지만, JDBC Store에 재연결 시도 간격은 200ms, 총 기간은 1000ms 이다.

DB가 1000ms 이상 Shutdown 이라면 JDBC Store와 JDBC TLOG Store는 Failed 되어 복구되지 않는다.

> TLOG(Transaction Log)는 File store 및 JDBC store 모두에 구성 가능하다.
>
> Store가 사용 불가능할 것을 대비해, 백업 데이터를 남겨두는 곳이라고 생각하면 된다.
>
> JMS Filestore, TLOG Filestore의 경우 내 물리 디스크에만 저장되므로 Migration이 되지 않는다.
>
> 또한 File 기반 store에는 위의 옵션이 없다.

<br>

고객은 DB 재기동 이후 Datasource는 복구되었는데, 왜 JMS는 복구되지 않고 관련 Stuck Thread가 생겨나 있는지에 대한 질의가 있었다.

<br>

아래 스크립트로 설정값을 변경할 수 있다.

```python
# set_and_check_jdbcstore_reconnect.py
# - 특정 JDBC Store에 ReconnectRetry* 설정
# - 설정 전/후 값 출력으로 검증
# - WLST 온라인 모드

# ===== 접속 정보 =====
ADMIN_URL  = 't3://wls.local:8001'
ADMIN_USER = 'weblogic'
ADMIN_PASS = 'weblogic1'

# ===== 대상 JDBC Store 이름 & 설정 값(ms) =====
JDBCSTORE_NAME = 'JDBCStore-0'      # <-- 대상 JDBC Store 이름
NEW_INTERVAL_MS = 5000              # 예: 5초 간격
NEW_PERIOD_MS   = 300000            # 예: 5분 동안 재시도

# 접속
connect(ADMIN_USER, ADMIN_PASS, ADMIN_URL)
serverConfig()

# 대상 존재 확인 + 현재값 출력
storePath = '/JDBCStores/%s' % JDBCSTORE_NAME
storeBean = getMBean(storePath)
if storeBean is None:
    raise Exception('JDBC Store not found: %s' % JDBCSTORE_NAME)

cd(storePath)
try:
    curInterval = cmo.getReconnectRetryIntervalMillis()
except:
    curInterval = 'N/A'
try:
    curPeriod = cmo.getReconnectRetryPeriodMillis()
except:
    curPeriod = 'N/A'

print '\n[BEFORE] JDBCStore=%s  Interval(ms)=%s  Period(ms)=%s' % (JDBCSTORE_NAME, str(curInterval), str(curPeriod))

# 편집 시작 및 값 설정
edit(); startEdit()

cd(storePath)
cmo.setReconnectRetryIntervalMillis(NEW_INTERVAL_MS)
cmo.setReconnectRetryPeriodMillis(NEW_PERIOD_MS)

save(); activate(block='true')

# 재조회로 검증
serverConfig()
cd(storePath)
newInterval = cmo.getReconnectRetryIntervalMillis()
newPeriod   = cmo.getReconnectRetryPeriodMillis()

print '[AFTER ] JDBCStore=%s  Interval(ms)=%s  Period(ms)=%s' % (JDBCSTORE_NAME, str(newInterval), str(newPeriod))
print '\n=== DONE ==='

```


<br><br>


# 3. References

https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/store/jdbc.html#GUID-39B42AC6-3D93-451C-9888-3CE99B88E1CE

https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/wlach/taskhelp/jta/ConfigureTheTLogStore.html
