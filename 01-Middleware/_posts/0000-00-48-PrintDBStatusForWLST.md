---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[Middleware/WebLogic] WLST로 DB 상태 출력"
tags: [Middleware, WebLogic, WLST, DB Status]
typora-root-url: ..
---

# 1. 개요

DB 상태 출력하는 WLST Script




# 2. 설명

```python
출처:  http://middlewaremagic.com/weblogic/?p=4917

#############################################################################
#
# @author Copyright (c) 2010 - 2011 by Middleware Magic, All Rights Reserved.
#
#############################################################################
 
connect('weblogic','weblogic','t3://localhost:7001')
allServers=domainRuntimeService.getServerRuntimes();
if (len(allServers) > 0):
  for tempServer in allServers:
    jdbcServiceRT = tempServer.getJDBCServiceRuntime();
    dataSources = jdbcServiceRT.getJDBCDataSourceRuntimeMBeans();
    if (len(dataSources) > 0):
        for dataSource in dataSources:
            print 'ActiveConnectionsAverageCount      '  , dataSource.getActiveConnectionsAverageCount()
            print 'ActiveConnectionsCurrentCount      '  , dataSource.getActiveConnectionsCurrentCount()
            print 'ActiveConnectionsHighCount         '  , dataSource.getActiveConnectionsHighCount()
            print 'ConnectionDelayTime                '  , dataSource.getConnectionDelayTime()
            print 'ConnectionsTotalCount              '  , dataSource.getConnectionsTotalCount()
            print 'CurrCapacity                       '  , dataSource.getCurrCapacity()
            print 'CurrCapacityHighCount              '  , dataSource.getCurrCapacityHighCount()
            print 'DeploymentState                    '  , dataSource.getDeploymentState()
            print 'FailedReserveRequestCount          '  , dataSource.getFailedReserveRequestCount()
            print 'FailuresToReconnectCount           '  , dataSource.getFailuresToReconnectCount()
            print 'HighestNumAvailable                '  , dataSource.getHighestNumAvailable()
            print 'HighestNumUnavailable              '  , dataSource.getHighestNumUnavailable()
            print 'LeakedConnectionCount              '  , dataSource.getLeakedConnectionCount()
            print 'ModuleId                           '  ,  dataSource.getModuleId()
            print 'Name                               '  ,  dataSource.getName()
            print 'NumAvailable                       '  , dataSource.getNumAvailable()
            print 'NumUnavailable                     '  , dataSource.getNumUnavailable()
            print 'Parent                             '  ,  dataSource.getParent()
            print 'PrepStmtCacheAccessCount           '  , dataSource.getPrepStmtCacheAccessCount()
            print 'PrepStmtCacheAddCount              '  , dataSource.getPrepStmtCacheAddCount()
            print 'PrepStmtCacheCurrentSize           '  , dataSource.getPrepStmtCacheCurrentSize()
            print 'PrepStmtCacheDeleteCount           '  , dataSource.getPrepStmtCacheDeleteCount()
            print 'PrepStmtCacheHitCount              '  , dataSource.getPrepStmtCacheHitCount()
            print 'PrepStmtCacheMissCount             '  , dataSource.getPrepStmtCacheMissCount()
            print 'Properties                         '  ,  dataSource.getProperties()
            print 'ReserveRequestCount                '  , dataSource.getReserveRequestCount()
            print 'State                              '  ,  dataSource.getState()
            print 'Type                               '  ,  dataSource.getType()
            print 'VersionJDBCDriver                  '  , dataSource.getVersionJDBCDriver()
            print 'WaitingForConnectionCurrentCount   '  , dataSource.getWaitingForConnectionCurrentCount()
            print 'WaitingForConnectionFailureTotal   '  , dataSource.getWaitingForConnectionFailureTotal()
            print 'WaitingForConnectionHighCount      '  , dataSource.getWaitingForConnectionHighCount()
            print 'WaitingForConnectionSuccessTotal   '  , dataSource.getWaitingForConnectionSuccessTotal()
            print 'WaitingForConnectionTotal          '  , dataSource.getWaitingForConnectionTotal()
            print 'WaitSecondsHighCount               '  , dataSource.getWaitSecondsHighCount()
```

