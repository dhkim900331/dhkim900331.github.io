---
date: 2025-08-29 12:22:37 +0900
layout: post
title: "[WebLogic/JMS] Creating JMS With WLST"
tags: [Middleware, WebLogic, JMS, WLST]
typora-root-url: ../..
---

# 1. Overview

WLST 스크립트로 JMS Server/Module를 배치한다.

<br><br>


# 2. Descriptions

JMS Server - 클러스터 단위가 아닌 1개 인스턴스 단위로만 배포 가능하다.

JMS Module - 클러스터 단위로 배포가 가능하며,

​	이 Module 안에는 JMS Application이 접근하는 진입점으로 사용하는 ConnectionFactory,

​	메시지를 저장하기 위해 Endpoint를 제공하는 Queue (외 Topic 등),

​	Queue를 JMS Server에 배포하게 하는 Subdeployment 가 있다.

<br>

즉 JMS Server는 물리적인 FIlestore나 JDBCstore에 접근케 하는 배포 형태고,

JMS Module은 JMS Server에 접근하여 어떻게 사용하는지 논리적인 명세를 하는 배포 객체이다.

<br>

아래 WLST 스크립트를 실행하여 기본적인 JMS (Filestore) 를 생성한다.

```python
# create_simple_jms_v3_nofunc.py
# - 함수 없이 WLST 커맨드만 사용 (idempotent: 이미 있으면 건너뛰고/타깃 병합)
# - Cluster 또는 단일 Server 대상
# - Default File Store 사용

# ===== 환경 =====
ADMIN_URL  = 't3://wls.local:8001'
ADMIN_USER = 'weblogic'
ADMIN_PASS = 'weblogic1'

# ===== 대상 (둘 중 하나만 채우세요) =====
TARGET_CLUSTER = 'myCluster'   # 예: 'myCluster'
TARGET_SERVER  = ''            # 예: 'ManagedServer1'

# ===== 리소스 이름/JNDI =====
JMSMODULE_NAME    = 'DemoJMSModule'
SUBDEPLOY_NAME    = 'DemoSubDep'
JMS_SERVER_PREFIX = 'DemoJMSServer'
CF_NAME  = 'DemoConnectionFactory'
CF_JNDI  = 'jms/DemoCF'
UDQ_NAME = 'DemoUDQ'
UDQ_JNDI = 'jms/DemoQueue'

from time import sleep
from jarray import array as jarray_array
from weblogic.management.configuration import TargetMBean as TargetMbean

# 접속
connect(ADMIN_USER, ADMIN_PASS, ADMIN_URL)
serverConfig()

# 대상 판별
targetBean = None
targetKind = None
memberServers = []

if TARGET_CLUSTER and TARGET_CLUSTER.strip():
    clPath = '/Clusters/%s' % TARGET_CLUSTER.strip()
    clusterBean = getMBean(clPath)
    if clusterBean is None:
        raise Exception('Cluster not found: ' + TARGET_CLUSTER)
    targetBean = clusterBean
    targetKind = 'cluster'
    memberServers = list(clusterBean.getServers() or [])
    if not memberServers:
        raise Exception('No members in cluster: ' + TARGET_CLUSTER)

elif TARGET_SERVER and TARGET_SERVER.strip():
    svPath = '/Servers/%s' % TARGET_SERVER.strip()
    serverBean = getMBean(svPath)
    if serverBean is None:
        raise Exception('Server not found: ' + TARGET_SERVER)
    targetBean = serverBean
    targetKind = 'server'
    memberServers = [serverBean]
else:
    raise Exception('Set TARGET_CLUSTER or TARGET_SERVER')

# 편의: JMSServer 이름들 미리 계산
desiredJmsServerNames = []
for s in memberServers:
    desiredJmsServerNames.append('%s_%s' % (JMS_SERVER_PREFIX, s.getName()))

# 편집 모드
edit(); startEdit()

# 1) JMSServer 생성/타깃 (서버별 1개)
for s, jsName in zip(memberServers, desiredJmsServerNames):
    jsPath = '/JMSServers/%s' % jsName
    if getMBean(jsPath) is None:
        cd('/')
        cmo.createJMSServer(jsName)
        sleep(0.2)
    # 타깃 병합
    cd(jsPath)
    curTargets = list(cmo.getTargets() or [])
    names = set([t.getName() for t in curTargets])
    if s.getName() not in names:
        curTargets.append(s)
    cmo.setTargets(jarray_array(curTargets, TargetMbean))
    print 'JMSServer ready: %s -> %s' % (jsName, s.getName())

# 2) JMS Module 생성/타깃 (클러스터 또는 단일 서버)
modPath = '/JMSSystemResources/%s' % JMSMODULE_NAME
if getMBean(modPath) is None:
    cd('/')
    cmo.createJMSSystemResource(JMSMODULE_NAME)
    sleep(0.2)
cd(modPath)
curTargets = list(cmo.getTargets() or [])
names = set([t.getName() for t in curTargets])
if targetBean.getName() not in names:
    curTargets.append(targetBean)
cmo.setTargets(jarray_array(curTargets, TargetMbean))
print 'JMS Module ready: %s -> %s' % (JMSMODULE_NAME, targetBean.getName())

# 3) SubDeployment 생성/타깃 (→ JMSServer들)
subPath = '/JMSSystemResources/%s/SubDeployments/%s' % (JMSMODULE_NAME, SUBDEPLOY_NAME)
if getMBean(subPath) is None:
    cd('/JMSSystemResources/%s' % JMSMODULE_NAME)
    cmo.createSubDeployment(SUBDEPLOY_NAME)
    sleep(0.2)
cd(subPath)
curTargets = list(cmo.getTargets() or [])
names = set([t.getName() for t in curTargets])
# JMSServer MBean들을 타깃으로 병합
for jsName in desiredJmsServerNames:
    jsBean = getMBean('/JMSServers/%s' % jsName)
    if jsBean and jsBean.getName() not in names:
        curTargets.append(jsBean)
cmo.setTargets(jarray_array(curTargets, TargetMbean))
print 'SubDeployment ready: %s targets=%s' % (SUBDEPLOY_NAME, [t.getName() for t in curTargets])

# 4) CF / UDQ 생성
jmsResPath = '/JMSSystemResources/%s/JMSResource/%s' % (JMSMODULE_NAME, JMSMODULE_NAME)

# 4-1) ConnectionFactory
cfPath = jmsResPath + '/ConnectionFactories/%s' % CF_NAME
if getMBean(cfPath) is None:
    cd(jmsResPath)
    cmo.createConnectionFactory(CF_NAME)
    sleep(0.2)
cd(cfPath)
cmo.setJNDIName(CF_JNDI)
cmo.setDefaultTargetingEnabled(True)  # 모듈 타깃을 자동 상속
print 'ConnectionFactory ready: %s (JNDI=%s)' % (CF_NAME, CF_JNDI)

# 4-2) Uniform Distributed Queue
udqPath = jmsResPath + '/UniformDistributedQueues/%s' % UDQ_NAME
if getMBean(udqPath) is None:
    cd(jmsResPath)
    cmo.createUniformDistributedQueue(UDQ_NAME)
    sleep(0.2)
cd(udqPath)
cmo.setJNDIName(UDQ_JNDI)
cmo.setSubDeploymentName(SUBDEPLOY_NAME)
print 'UDQ ready: %s (JNDI=%s, SubDeployment=%s)' % (UDQ_NAME, UDQ_JNDI, SUBDEPLOY_NAME)

# 활성화
save(); activate(block='true')
print '=== DONE (no-func) ==='
```

<br>

아래 스크립트로 서버에 배치된 모든 JMS Objects를 조회한다.

```python
# show_all_jms.py
# - 함수 없이 절차형으로 전체 JMS 리소스 구조 출력
# - AdminServer RUNNING 상태에서 실행

ADMIN_URL  = 't3://wls.local:8001'
ADMIN_USER = 'weblogic'
ADMIN_PASS = 'weblogic1'

connect(ADMIN_USER, ADMIN_PASS, ADMIN_URL)
serverConfig()

print '\n=== [JMSServers] ==='
for js in (cmo.getJMSServers() or []):
    print 'JMSServer =', js.getName()
    try:
        tgs = [t.getName() for t in (js.getTargets() or [])]
    except:
        tgs = []
    print '  targets =', tgs
    st = js.getPersistentStore()
    if st is None:
        print '  store  = DEFAULT_FILE_STORE'
    else:
        try:
            stype = st.getClass().getName()
        except:
            stype = 'Unknown'
        print '  store  = %s  (type=%s)' % (st.getName(), stype)

print '\n=== [JMS System Resources (Modules)] ==='
for mod in (cmo.getJMSSystemResources() or []):
    mname = mod.getName()
    print '\n[JMS Module] ', mname

    # Module targets
    cd('/JMSSystemResources/%s' % mname)
    try:
        mtgs = [t.getName() for t in (cmo.getTargets() or [])]
    except:
        mtgs = []
    print '  module targets =', mtgs

    # SubDeployments (name + targets)
    print '  SubDeployments:'
    try:
        subs = cmo.getSubDeployments() or []
        if subs:
            for sd in subs:
                try:
                    sdtgs = [t.getName() for t in (sd.getTargets() or [])]
                except:
                    sdtgs = []
                print '    - %s  targets=%s' % (sd.getName(), sdtgs)
        else:
            print '    (none)'
    except:
        print '    (none)'

    # JMS resources in module
    res = mod.getJMSResource()

    # Connection Factories
    try:
        cfs = res.getConnectionFactories() or []
        if cfs:
            print '  ConnectionFactories:'
            for cf in cfs:
                try: jndi = cf.getJNDIName()
                except: jndi = ''
                try: dte = cf.isDefaultTargetingEnabled()
                except: dte = 'N/A'
                send_to = 'N/A'
                try:
                    ddp = cf.getDefaultDeliveryParams()
                    if ddp is not None:
                        send_to = ddp.getSendTimeout()
                except:
                    try: send_to = cf.getSendTimeout()
                    except: pass
                print '    - %s  jndi=%s  defaultTargeting=%s  send-timeout(ms)=%s' % (
                    cf.getName(), jndi, str(dte), str(send_to))
        else:
            print '  ConnectionFactories: (none)'
    except:
        print '  ConnectionFactories: (error)'

    # Uniform Distributed Queues
    try:
        udqs = res.getUniformDistributedQueues() or []
        if udqs:
            print '  UniformDistributedQueues:'
            for q in udqs:
                print '    - %s  jndi=%s  subdeployment=%s' % (
                    q.getName(), q.getJNDIName(), q.getSubDeploymentName())
        else:
            print '  UniformDistributedQueues: (none)'
    except:
        print '  UniformDistributedQueues: (error)'

    # Uniform Distributed Topics
    try:
        udts = res.getUniformDistributedTopics() or []
        if udts:
            print '  UniformDistributedTopics:'
            for t in udts:
                print '    - %s  jndi=%s  subdeployment=%s' % (
                    t.getName(), t.getJNDIName(), t.getSubDeploymentName())
        else:
            print '  UniformDistributedTopics: (none)'
    except:
        print '  UniformDistributedTopics: (error)'

    # Classic Queues
    try:
        qs = res.getQueues() or []
        if qs:
            print '  Queues:'
            for q in qs:
                print '    - %s  jndi=%s  subdeployment=%s' % (
                    q.getName(), q.getJNDIName(), q.getSubDeploymentName())
        else:
            print '  Queues: (none)'
    except:
        print '  Queues: (error)'

    # Classic Topics
    try:
        ts = res.getTopics() or []
        if ts:
            print '  Topics:'
            for t in ts:
                print '    - %s  jndi=%s  subdeployment=%s' % (
                    t.getName(), t.getJNDIName(), t.getSubDeploymentName())
        else:
            print '  Topics: (none)'
    except:
        print '  Topics: (error)'

print '\n=== DONE ==='

```


<br><br>


# 3. References

