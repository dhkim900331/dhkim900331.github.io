---
date: 2024-08-01 16:25:22 +0900
layout: post
title: "[WebLogic] No error despite changed datasource password"
tags: [Middleware, WebLogic, Dasasource, Password, DB, Connection]
typora-root-url: ..
---

# 1. Overview
Datasource password를 서비스 도중 변경했음에도, 서비스에 영향이 없다.

{{ site.content.br_big }}

# 2. Descriptions
[Datasource password option](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wlach/pagehelp/JDBCjdbcdatasourcesjdbcdatasourceconfigconnectionpooltitle.html) 설명에 따르면,

Password는 Physical connection이 생성될 때 사용된다.

그러므로, 이미 사용 중인 Datasource connection pool들은 socket 통신으로 연결되어 있으므로 password를 서비스 도중 변경하여도 문제가 없다.



[Test JDBC data sources](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wlach/taskhelp/jdbc/jdbc_datasources/TestDataSources.html) 설명에 따르면,

Datasource connection pool에서 1개 connection을 예약(reserves)하여 Connection을 testing 하는 작업이다.

위 언급처럼 이미 연결이 되어 있는 connection 이므로, password가 변경되어도 socket으로 연결되어 있는 connection은 영향을 받지 않고 DB와 연결이 정상임을 알려올 것이다.

Password를 변경하여도, Testing 작업은 이를 반영하지 않는다.



또한 WebLogic 12.2.1.3 부터는 [12.2.1.3 의 Password MBean](https://docs.oracle.com/middleware/12213/wls/WLACH/pagehelp/JDBCjdbcdatasourcesjdbcdatasourceconfigconnectionpooltitle.html)이 변경 시 즉시 적용 된다.

WebLogic 12.2.1.3 이상 에서 서비스 도중 잘못된 Datasource password 를 변경 후, Connection 부족으로 Physical Connection 을 추가 생성 하게 되면 다음과 같이 Error가 발생한다.

추가적인 Physical Connection 생성만 불가하고, 기존 사용 중인 Connection은 문제가 없다.

```
weblogic.jdbc.extensions.ConnectionDeadSQLException: weblogic.common.resourcepool.ResourceDeadException: 0:
 Could not create connection for datasource '<DATASOURCE NAME>'.

 The returned message is: ORA-01017: invalid username/password; logon denied

 It is likely that the login or password is not valid.
 It is also possible that something else is invalid in
 the configuration or that the database is not available.
        at weblogic.jdbc.common.internal.JDBCUtil.wrapAndThrowResourceException(JDBCUtil.java:274)
        at weblogic.jdbc.pool.Driver.connect(Driver.java:154)
        at weblogic.jdbc.jts.Driver.getNonTxConnection(Driver.java:665)
        at weblogic.jdbc.jts.Driver.connect(Driver.java:129)
        at weblogic.jdbc.common.internal.RmiDataSource.getConnectionInternal(RmiDataSource.java:638)
        at weblogic.jdbc.common.internal.RmiDataSource.getConnection(RmiDataSource.java:594)
        at weblogic.jdbc.common.internal.RmiDataSource.getConnection(RmiDataSource.java:587)
        at jsp_servlet.__sql._jspService(__sql.java:94)
        at weblogic.servlet.jsp.JspBase.service(JspBase.java:35)
        at weblogic.servlet.internal.StubSecurityHelper$ServletServiceAction.run(StubSecurityHelper.java:286)
        at weblogic.servlet.internal.StubSecurityHelper$ServletServiceAction.run(StubSecurityHelper.java:260)
        at weblogic.servlet.internal.StubSecurityHelper.invokeServlet(StubSecurityHelper.java:137)
        at weblogic.servlet.internal.ServletStubImpl.execute(ServletStubImpl.java:350)
        at weblogic.servlet.internal.ServletStubImpl.execute(ServletStubImpl.java:247)
        at weblogic.servlet.internal.WebAppServletContext$ServletInvocationAction.wrapRun(WebAppServletContext.java:3697)
        at weblogic.servlet.internal.WebAppServletContext$ServletInvocationAction.run(WebAppServletContext.java:3667)
        at weblogic.security.acl.internal.AuthenticatedSubject.doAs(AuthenticatedSubject.java:326)
        at weblogic.security.service.SecurityManager.runAsForUserCode(SecurityManager.java:197)
        at weblogic.servlet.provider.WlsSecurityProvider.runAsForUserCode(WlsSecurityProvider.java:203)
        at weblogic.servlet.provider.WlsSubjectHandle.run(WlsSubjectHandle.java:71)
        at weblogic.servlet.internal.WebAppServletContext.doSecuredExecute(WebAppServletContext.java:2443)
        at weblogic.servlet.internal.WebAppServletContext.securedExecute(WebAppServletContext.java:2291)
        at weblogic.servlet.internal.WebAppServletContext.execute(WebAppServletContext.java:2269)
        at weblogic.servlet.internal.ServletRequestImpl.runInternal(ServletRequestImpl.java:1703)
        at weblogic.servlet.internal.ServletRequestImpl.run(ServletRequestImpl.java:1663)
        at weblogic.servlet.provider.ContainerSupportProviderImpl$WlsRequestExecutor.run(ContainerSupportProviderImpl.java:272)
        at weblogic.invocation.ComponentInvocationContextManager._runAs(ComponentInvocationContextManager.java:352)
        at weblogic.invocation.ComponentInvocationContextManager.runAs(ComponentInvocationContextManager.java:337)
        at weblogic.work.LivePartitionUtility.doRunWorkUnderContext(LivePartitionUtility.java:57)
        at weblogic.work.PartitionUtility.runWorkUnderContext(PartitionUtility.java:41)
        at weblogic.work.SelfTuningWorkManagerImpl.runWorkUnderContext(SelfTuningWorkManagerImpl.java:644)
        at weblogic.work.ExecuteThread.execute(ExecuteThread.java:415)
        at weblogic.work.ExecuteThread.run(ExecuteThread.java:355)
```



Datasource password가 connection에 반영되기 위해서는 다음 중 하나의 작업이 필요하다.

 (1) WebLogic Server 재기동 (일반적으로, 모든 서비스를 정리하고 다시 부트업하기 때문에 권장된다.)

 (2) Datasource가 배포된 인스턴스나 클러스터에 재배포 (배포 취소 후 재배포)

 (3) Datasource connection의 [reset](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wlach/taskhelp/jdbc/jdbc_datasources/ResetConnectionsInADataSource.html) 또는 [shutdown](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wlach/taskhelp/jdbc/jdbc_datasources/ShutDownDataSources.html) 후 [start](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wlach/taskhelp/jdbc/jdbc_datasources/StartDataSources.html)

 (4) 마지막으로, 위의 작업을 수행하지 않아도 Datasource가 부족한 physical connection을 생성하면, 그 connection은 변경된 password를 사용한다.



(2) ~ (3) 번의 경우, 사용자 서비스가 socketRead() 와 같은 Native Method Level로 물리 DB와 연결되어 있는 경우,

Native Method는 Blocking IO 이기 때문에 JDBC Datasource 측에서 Connection을 회수할 수가 없다.

회수할 수 없는 시간은, socketRead()가 해제될 때까지 기다려야 하는 것이며 이 시간이 길어질 경우 예상치 못한 상황이 발생할 수 있다.

그러므로, 일반적으로 (1) WebLogic Server 재기동을 권장한다.

{{ site.content.br_big }}

# 3. References
**Datasource password를 변경했지만, 서비스에 문제가 없습니다. (Doc ID 3033845.1)**