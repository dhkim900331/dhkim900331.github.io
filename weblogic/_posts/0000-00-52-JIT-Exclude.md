---
date: 2024-02-27 13:38:15 +0900
layout: post
title: "[WebLogic] JIT Exclude"
tags: [Middleware, WebLogic, JIT]
typora-root-url: ..
---

# 1. Overview
Just-In-Time (JIT) 의 Method Exclude 방법


<br><br>


# 2. Descriptions
결론을 언급하면, [Advanced JIT Compiler Options](https://docs.oracle.com/javase/8/docs/technotes/tools/unix/java.html#BABDDFII)의 설명대로 `-XX:CompileCommand=exclude,java/lang/String.indexOf` 와 같이 설정하여 java/lang/String Class의 indexOf method를 JIT에서 제외할 수 있다.

<br>

특정 장애 사례에서,

어느 Thread가 다음과 같은 복잡하지 않은 Stack Trace를 갖는데,

```
J 33516  java.net.Inet4AddressImpl.lookupAllHostAddr(Ljava/lang/String;)[Ljava/net/InetAddress; (0 bytes) @ 0x00007f502bb8e38c [0x00007f502bb8e340+0x4c]
J 39642 C2 java.net.InetAddress$2.lookupAllHostAddr(Ljava/lang/String;)[Ljava/net/InetAddress; (10 bytes) @ 0x00007f502ab495f4 [0x00007f502ab495a0+0x54]
J 34720 C2 java.net.InetAddress.getAllByName(Ljava/lang/String;Ljava/net/InetAddress;)[Ljava/net/InetAddress; (387 bytes) @ 0x00007f5029641b3c [0x00007f5029640a60+0x10dc]
J 87033 C2 weblogic.net.http.HttpClient.openServer(Ljava/lang/String;I)V (379 bytes) @ 0x00007f5027ce7a48 [0x00007f5027ce7900+0x148]
J 49601 C2 weblogic.net.http.HttpClient.openServer()V (372 bytes) @ 0x00007f502df150a4 [0x00007f502df14be0+0x4c4]
J 51396 C2 weblogic.net.http.HttpURLConnection.getInputStream()Ljava/io/InputStream; (994 bytes) @ 0x00007f502eb894e8 [0x00007f502eb88580+0xf68]
J 44814 C2 weblogic.net.http.HttpURLConnection.getResponseCode()I (150 bytes) @ 0x00007f502e0ebba8 [0x00007f502e0ebb40+0x68]
J 51380 C2 <Customer's App>.outbound.OutboundConnection.send(L***/framework/core/util/ByteArrayWrap;I)[B (34 bytes) @ 0x00007f502f6cd44c [0x00007f502f6cca00+0xa4c]
J 52915 C2 <Customer's App>.outbound.OutboundSender.send(L***/common/OutboundTarget;L***/common/OutboundHeader;L***/framework/core/util/ByteArrayWrap;Ljava/lang/String;)V (609 bytes) @ 0x00007f502eca36bc [0x00007f502eca3060+0x65c]
J 46698 C2 <Customer's App>.resolver.OutboundResolver.handleQueue(L***/framework/core/asyncqueue/IAsyncQueueContext;)Ljava/lang/Object; (45 bytes) @ 0x00007f502e07e718 [0x00007f502e07e620+0xf8]
J 36322% C2 <Customer's App>.core.asyncqueue.internal.AsyncQueueProcessor$QueueWorker._run()V (529 bytes) @ 0x00007f502c6c0a58 [0x00007f502c6c0280+0x7d8]
j  <Customer's App>.core.asyncqueue.internal.AsyncQueueProcessor$QueueWorker.run()V+8
```


가장 최근 `lookupAllHostAddr` 구간에서 잘못된 메모리 접근이 발생하여 Crash 가 발생했다.

```
#  SIGSEGV (0xb) at pc=0x00007f503c7a0366, pid=520072, tid=0x00007f4da18e2700
```


Crash가 발생한 지점인 thread_in_native.

```
C  [libc.so.6+0x86366]  __libc_malloc+0x136
```


libc는 OS Kernel libraries 중 하나인 GBLIC에 속해있으며,

libc의 문제로 인해 이러한 현상이 발생할 수도 있지만,

대게 공통 모듈이므로 일반적으로 JDK/WLS 에 Known issue가 있는지 살펴보아야 한다.

<br>

RHEL 8.X / JDK 8 환경에서 Known issue는 없었고,

이러한 Crash 문제는 처음 발생을 했기 때문에,

다음과 같은 Solutions 을 제공할 수 있다.

<br>

1. JDK Minor update

JDK 8 에서 유사한 형태의 Known issue는 검색되지 않았지만, 그동안의 Minor 코드 수정으로 인해서 잠재적으로 문제가 해소되었을 가능성도 있기 때문에, 최신 JDK 8 Minor update를 고려할 수 있다.

<br>

2. JIT Disable

JIT는 자주 사용되는 Method를 ByteCode compile 하는 것이다.

[5.2.1 Working Around Crashes in the HotSpot Compiler Thread or Compiled Code](https://docs.oracle.com/javase/8/docs/technotes/guides/troubleshoot/crashes002.html#CIHDIBJA)에서 설명하는 바와 같이, 잘못 Compiled 된 Byte Code 문제로 인해 발생할 것이 예상된다면, JIT를 Disable 하여 재현될 때 방지해볼 수 있다.


<br><br>


# 3. References

본문에 언급된 링크들을 기반으로 함.
