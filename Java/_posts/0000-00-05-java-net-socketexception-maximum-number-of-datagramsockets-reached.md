---
date: 2026-07-15 20:04:12 +0900
layout: post
title: "[Java/Datagram socket] java.net.SocketException: maximum number of DatagramSockets reached"
tags: [Java, JVM, UDP]
typora-root-url: ../..
---

# 1. Overview

`java.net.SocketException: maximum number of DatagramSockets reached` 발생 원인과 해결책


<br><br>


# 2. Descriptions

`java.net.DatagramSocket.createImpl()` 을 통해 Datagram Socket을 과도하게 생성 시 발생한다.

```
java.net.SocketException: maximum number of DatagramSockets reached
       at sun.net.ResourceManager.beforeUdpCreate(ResourceManager.java:73)
       at java.net.AbstractPlainDatagramSocketImpl.create(AbstractPlainDatagramSocketImpl.java:83)
       at java.net.DatagramSocket.createImpl(DatagramSocket.java:337)
       at java.net.DatagramSocket.<init>(DatagramSocket.java:239)
       at java.net.DatagramSocket.<init>(DatagramSocket.java:196)
       at ...
```

<br>

고객은 Oracle JDK 1.8 환경이지만 Open JDK 1.8 에서도 동일 소스 코드 구간을 확인할 수 있다.

[ResourceManager.java](https://github.com/openjdk/jdk8u/blob/master/jdk/src/share/classes/sun/net/ResourceManager.java) 의 코드 중 73 라인을 주목하면,

```java
public class ResourceManager {

	...
	
    private static final int DEFAULT_MAX_SOCKETS = 25;
    private static final int maxSockets;
    private static final AtomicInteger numSockets;

    static {
        String prop = java.security.AccessController.doPrivileged(
            new GetPropertyAction("sun.net.maxDatagramSockets")
        );
        int defmax = DEFAULT_MAX_SOCKETS;
        try {
            if (prop != null) {
                defmax = Integer.parseInt(prop);
            }
        } catch (NumberFormatException e) {}
        maxSockets = defmax;
        numSockets = new AtomicInteger(0);
    }

    public static void beforeUdpCreate() throws SocketException {
        if (System.getSecurityManager() != null) {
            if (numSockets.incrementAndGet() > maxSockets) {
                numSockets.decrementAndGet();
                throw new SocketException("maximum number of DatagramSockets reached");		<<< 73 line
            }
        }
    }
```

<br>

SecurityManager가 활성화된 환경에서는 최대 25개의 Datagram socket을 생성 제한이 존재한다.

혹은 `-Dsun.net.maxDatagramSocket` 옵션을 통해 이를 무시하고 더 많은 Datagram socket을 생성할 수 있다.


<br><br>


# 3. References

java.net.SocketException: maximum number of DatagramSockets reached - KB918981
