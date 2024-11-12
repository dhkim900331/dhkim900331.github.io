---
date: 2024-01-31 13:27:29 +0900
layout: post
title: "[WebLogic] ClassNotFoundException com.bea.xml.stream.MXParserFactory"
tags: [Middleware, WebLogic, ]
typora-root-url: ..
---

# 1. Overview
Admin Console 을 통해서 반영 작업을 진행할 때, `Caused By: java.lang.ClassNotFoundException: com/bea/xml/stream/MXParserFactory` 발생하는 에러에 대해서 살펴본다.


<br><br>


# 2. Descriptions
문제가 재현되는 시스템에서는, Admin Console을 통해서 반영 작업을 적용하려고 시도할 때 마다, 다음과 같은 Exception이 기록된다.

```
<2023. 12. 20 오후 1시 55분 02초 KST> <Warning> <Deployer> <BEA-149078> <Stack trace for message 149004
weblogic.management.provider.UpdateException: [Management:141191]The prepare phase of the configuration update failed with an exception:
	at weblogic.management.provider.internal.RuntimeAccessDeploymentReceiverService.updateDeploymentContext(RuntimeAccessDeploymentReceiverService.java:670)
	at weblogic.deploy.service.internal.targetserver.DeploymentReceiverCallbackDeliverer.doUpdateDeploymentContextCallback(DeploymentReceiverCallbackDeliverer.java:147)
	at weblogic.deploy.service.internal.targetserver.DeploymentReceiverCallbackDeliverer.updateDeploymentContext(DeploymentReceiverCallbackDeliverer.java:28)
	at weblogic.deploy.service.internal.statemachines.targetserver.ReceivedPrepare.callDeploymentReceivers(ReceivedPrepare.java:203)
	at weblogic.deploy.service.internal.statemachines.targetserver.ReceivedPrepare.handlePrepare(ReceivedPrepare.java:112)
	at weblogic.deploy.service.internal.statemachines.targetserver.ReceivedPrepare.receivedPrepare(ReceivedPrepare.java:52)
	at weblogic.deploy.service.internal.targetserver.TargetRequestImpl.run(TargetRequestImpl.java:211)
	at weblogic.deploy.service.internal.transport.CommonMessageReceiver$1.run(CommonMessageReceiver.java:457)
	at weblogic.work.SelfTuningWorkManagerImpl$WorkAdapterImpl.run(SelfTuningWorkManagerImpl.java:550)
	at weblogic.work.ExecuteThread.execute(ExecuteThread.java:263)
	at weblogic.work.ExecuteThread.run(ExecuteThread.java:221)
Caused By: java.lang.ClassNotFoundException: com/bea/xml/stream/MXParserFactory
	at java.lang.Class.forName0(Native Method)
	at java.lang.Class.forName(Class.java:278)
	at javax.xml.stream.FactoryFinder.getProviderClass(FactoryFinder.java:124)
	at javax.xml.stream.FactoryFinder.newInstance(FactoryFinder.java:179)
	at javax.xml.stream.FactoryFinder.newInstance(FactoryFinder.java:148)
	at javax.xml.stream.FactoryFinder.find(FactoryFinder.java:254)
	at javax.xml.stream.FactoryFinder.find(FactoryFinder.java:215)
	at javax.xml.stream.XMLInputFactory.newInstance(XMLInputFactory.java:154)
	at weblogic.descriptor.DescriptorReader.<init>(DescriptorReader.java:22)
	at weblogic.management.provider.internal.ConfigReader.<init>(ConfigReader.java:70)
	at weblogic.management.provider.internal.ConfigReader.<init>(ConfigReader.java:64)
	at weblogic.management.provider.internal.RuntimeAccessDeploymentReceiverService.handleExternalTreeLoad(RuntimeAccessDeploymentReceiverService.java:1021)
	at weblogic.management.provider.internal.RuntimeAccessDeploymentReceiverService.updateDeploymentContext(RuntimeAccessDeploymentReceiverService.java:597)
	at weblogic.deploy.service.internal.targetserver.DeploymentReceiverCallbackDeliverer.doUpdateDeploymentContextCallback(DeploymentReceiverCallbackDeliverer.java:147)
	at weblogic.deploy.service.internal.targetserver.DeploymentReceiverCallbackDeliverer.updateDeploymentContext(DeploymentReceiverCallbackDeliverer.java:28)
	at weblogic.deploy.service.internal.statemachines.targetserver.ReceivedPrepare.callDeploymentReceivers(ReceivedPrepare.java:203)
	at weblogic.deploy.service.internal.statemachines.targetserver.ReceivedPrepare.handlePrepare(ReceivedPrepare.java:112)
	at weblogic.deploy.service.internal.statemachines.targetserver.ReceivedPrepare.receivedPrepare(ReceivedPrepare.java:52)
	at weblogic.deploy.service.internal.targetserver.TargetRequestImpl.run(TargetRequestImpl.java:211)
	at weblogic.deploy.service.internal.transport.CommonMessageReceiver$1.run(CommonMessageReceiver.java:457)
	at weblogic.work.SelfTuningWorkManagerImpl$WorkAdapterImpl.run(SelfTuningWorkManagerImpl.java:550)
	at weblogic.work.ExecuteThread.execute(ExecuteThread.java:263)
	at weblogic.work.ExecuteThread.run(ExecuteThread.java:221)
> 
```


위 에러가 발생하는 시스템과 문제가 발생하지 않는 다른 시스템 둘 다에서 `-verbose:class` 옵션을 적용하여 비교/조사하였는데,

ClassNotFoundException 에러가 가리키는 `com/bea/xml/stream/MXParserFactory` 를 어디에서도 Loaded 되지 않았다.

<br>

또한, 문제가 발생하지 않는 시스템에서 또한 `MXParserFactory` 를 Loaded 되지 않았다.

즉, Admin Console 반영 작업에 있어, `com/bea/xml/stream/MXParserFactory` Class는 필요하지 않다는 것이며,

`com/bea/xml/stream/MXParserFactory` Class는 `com.bea.core.xml.stax_1.1.0.0.jar` 에 포함되어 있지만, 사용되지 않으므로 Loaded 되지 않은 것이다.

<br>

이러한 내용을 뒷바침 하는 문서는 **How to Configure WebLogic Server to Use JDK's StAX Implementation (Doc ID 1566056.1)** 에서도 확인할 수 있다.

WebLogic에서 사용하도록 구현된 StAX library는 `com.bea.core.weblogic.stax_x.x.x.x.jar` 이다.

<br>

문제가 재현되는 시스템의 특이사항으로는,

Windows Server 2012 R2 환경에서 WebLogic Server 10.3.6 및 Oracle JDK 1.7.0_171 을 사용중인데

[Fusion Middleware certification matrix](https://www.oracle.com/technetwork/middleware/downloads/fmw-11gr1certmatrix.xls) 에 따르면,

최소한 Oracle JDK 1.7.0_201 이상으로 Upgrade를 해야 Certification Matrix에 부합한다.

<br>

발견된 다음 문서와 유사하게, Certification 에 부합하지 않는 환경에서 동일한 `com/bea/xml/stream/MXParserFactory` Class Exception이 발견되었다.

**WebLogic Server 12.2.1.4 Installation Fails with "java.lang.reflect.InvocationTargetException" (Doc ID 2708587.1)**

문제의 시스템 또한 JDK Version을 Upgrade 해야 한다.


<br><br>


# 3. References

**How to Configure WebLogic Server to Use JDK's StAX Implementation (Doc ID 1566056.1)**

**WebLogic Server 12.2.1.4 Installation Fails with "java.lang.reflect.InvocationTargetException" (Doc ID 2708587.1)**
