---
date: 2025-11-18 13:52:47 +0900
layout: post
title: "[Coherence] ClassNotFoundException GetElasticMaxValueSizeProcessor"
tags: [Coherence, Session, Split]
typora-root-url: ..
---

# 1. Overview

Coherence 12.2.1.4.10 -> 12.2.1.4.26 패치 후

WebLogic (Cache Client)에 배포된 사용자 App에서

간단한 로그인 업무만 수행하여도 ClassNotFoundException GetElasticMaxValueSizeProcessor이 발생


<br><br>


# 2. Descriptions

고객 App에서 발생하는 Exception 아래 전문

```
Class: com.tangosol.coherence.servlet.GetElasticMaxValueSizeProcessor
ClassLoader: sun.misc.Launcher$AppClassLoader@7852e922
ContextClassLoader: sun.misc.Launcher$AppClassLoader@7852e922
2025-08-21 17:11:38.179/88539.372 Oracle Coherence GE 12.2.1.4.26 <Warning> (thread=[ACTIVE] ExecuteThread: '45' for queue: 'weblogic.kernel.Default (self-tuning)', member=n/a): Splitting large attribute value is not enabled due invoke call to get the maximum value size for journal scheme returned an exception: (Wrapped) java.io.IOException: Class initialization failed: java.lang.ClassNotFoundException: com.tangosol.coherence.servlet.GetElasticMaxValueSizeProcessor
	at java.net.URLClassLoader.findClass(URLClassLoader.java:382)
	at java.lang.ClassLoader.loadClass(ClassLoader.java:418)
	at sun.misc.Launcher$AppClassLoader.loadClass(Launcher.java:355)
	at java.lang.ClassLoader.loadClass(ClassLoader.java:351)
	at java.lang.Class.forName0(Native Method)
	at java.lang.Class.forName(Class.java:264)
	at com.tangosol.util.ExternalizableHelper.loadClass(ExternalizableHelper.java:4016)
	at com.tangosol.util.ExternalizableHelper.readExternalizableLite(ExternalizableHelper.java:2501)
	at com.tangosol.util.ExternalizableHelper.readObjectInternal(ExternalizableHelper.java:2935)
	at com.tangosol.util.ExternalizableHelper.readObject(ExternalizableHelper.java:2846)
	at com.tangosol.io.DefaultSerializer.deserialize(DefaultSerializer.java:66)
	at com.tangosol.coherence.component.net.extend.Channel.deserialize(Channel.CDB:15)
	at com.tangosol.io.pof.PofBufferReader.readAsObject(PofBufferReader.java:3619)
	at com.tangosol.io.pof.PofBufferReader.readObject(PofBufferReader.java:2890)
	at com.tangosol.coherence.component.net.extend.messageFactory.NamedCacheFactory$InvokeRequest.readExternal(NamedCacheFactory.CDB:5)
	at com.tangosol.coherence.component.net.extend.Codec.decode(Codec.CDB:29)
	at com.tangosol.coherence.component.util.daemon.queueProcessor.service.Peer.decodeMessage(Peer.CDB:25)
	at com.tangosol.coherence.component.util.daemon.queueProcessor.service.Peer.onNotify(Peer.CDB:54)
	at com.tangosol.coherence.component.util.Daemon.run(Daemon.CDB:54)
	at java.lang.Thread.run(Thread.java:748)
```

<br>

이때 발생하는 여러가지 의문들이 있었는데,

- WLS 에서 발생하는 Error log인데 Stacktrace는 독립적인 Coherence Thread
- GetElasticMaxValueSizeProcessor 클래스는 패치 이후 WLS에 잘 로드 되었음을 '-verbose:class' 로 확인됨.
- Coherence Server측은 별다른 Exception이 기록되지 않았으며, 패치 이후 GetElasticMaxValueSizeProcessor 클래스가 존재함을 확인 ('-verbose:class 는 확인하지 않음')

<br>

GetElasticMaxValueSizeProcessor 클래스는 12.2.1.4.16 부터 추가되었다. [클래스 설명](https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/java-reference/com/tangosol/coherence/servlet/GetElasticMaxValueSizeProcessor.html)

> An EntryProcessor that returns the configured Elastic Data maximum value size if the cache is backed by Elastic Data; 0 otherwise.

<br>

Coherence에서 Session object가 coherence-attribute-overflow-threshold (기본값 1KB) 보다 크면, Session object를 분할(split) 하여 저장하게 된다. [해당 옵션 설명](https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/administer-http-sessions/coherenceweb-context-parameters.html)

이때, Coherence가 off-heap/Journal 로 Session data를 저장케 하는 Elastic Data가 구현되어 있다면, [Elastic Data 설명](https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/develop-applications/implementing-storage-and-backing-maps.html#GUID-BDC8612E-B3FB-46CD-96C9-3552DDDC175D)

GetElasticMaxValueSizeProcessor 클래스를 호출하여 각 저장소(Elastic data)의 단일 객체 최대 저장 크기를 조회하여 세션을 Split 해야 할지 말지를 판단해야 한다.

<br>

그러나 Coherence Server측에 coherence-web.jar가 Classpath에 올라와 있지 않아 ClassNotFoundException이 발생했고,

이를 WLS App측에서 `<Warning...` 으로 감싼 메시지를 받은 것이다.

<br>

애초에 Coherence Server측에서 ClassNotFoundException 메시지가 로그에 있었다면 더 빠르게 해결 되었을 것이나 그렇지 않았고,

지금 보니 위 에러 메시지 전문에 다음의 Classloader, Context 등이 어디에 속해있는지를 알려주는 것이 어느정도는 힌트가 되었을 것이다.

```
Class: com.tangosol.coherence.servlet.GetElasticMaxValueSizeProcessor
ClassLoader: sun.misc.Launcher$AppClassLoader@7852e922
ContextClassLoader: sun.misc.Launcher$AppClassLoader@7852e922
```

<br>

Coherence Server에 coherence-web.jar를 Classpath로 추가하여 문제가 해결되었다.


<br><br>


# 3. References

**ClassNotFoundException: GetElasticMaxValueSizeProcessor after upgrading coherence (Doc ID 3105534.1)**

이외 내용에 직접 링크함
