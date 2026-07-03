---
date: 2026-07-03 18:06:17 +0900
layout: post
title: "[WebLogic/Clustering] Multicast Clustering Is Not Working"
tags: [Middleware, WebLogic, Cluster, Multicast, UDP]
typora-root-url: ..
---

# 1. Overview

앞단 L4 작업 후 운영시스템 Multicast 사용하는 Clustering 간에 메시지 교환이 되지 않는 문제 발생

<br><br>


# 2. Descriptions

정상적인 경우, 각 시스템에서 MulticastTest 실행 시 메시지를 주고 받아야 한다.

<br>

1번 시스템에서 `test123` 이름으로 메시지를 전송한다.

```sh
$ java utils.MulticastTest -N test123 -A 239.192.0.0 -P 7001
***** WARNING ***** WARNING ***** WARNING *****
Do NOT use the same multicast address as a running WLS cluster.


Starting test.  Hit any key to abort


Bound socket to 0.0.0.0/0.0.0.0:7001
Using multicast address 239.192.0.0:7001
       Joined Group with InetAddress /239.192.0.0
Will send messages under the name test123 every 2 seconds
Will print warning every 600 seconds if no messages are received

               I (test123) sent message num 1
New Neighbor ����"�srweblogic.rj found on message number 1997043800
Duplicate message from ����"�srweblogic.rj: 1997043800
               I (test123) sent message num 2
Received message 2 from test123
               I (test123) sent message num 3
Received message 3 from test123
               I (test123) sent message num 4
Received message 4 from test123
Received message 5 from test123
               I (test123) sent message num 5
               I (test123) sent message num 6
Received message 6 from test123
...
```

<br>

2번 시스템에서 `test456` 이름으로 메시지를 전송한다.

```sh
$ java utils.MulticastTest -N test456 -A 239.192.0.0 -P 7001
***** WARNING ***** WARNING ***** WARNING *****
Do NOT use the same multicast address as a running WLS cluster.


Starting test.  Hit any key to abort


Bound socket to 0.0.0.0/0.0.0.0:7001
Using multicast address 239.192.0.0:7001
       Joined Group with InetAddress /239.192.0.0
Will send messages under the name test456 every 2 seconds
Will print warning every 600 seconds if no messages are received

New Neighbor test123 found on message number 6
               I (test456) sent message num 1
New Neighbor ����"�srweblogic.rj found on message number 1997043800
Duplicate message from ����"�srweblogic.rj: 1997043800
Received message 7 from test123
               I (test456) sent message num 2
Received message 2 from test456
Received message 8 from test123
               I (test456) sent message num 3
Received message 3 from test456
Received message 9 from test123
               I (test456) sent message num 4
Received message 4 from test456
Received message 10 from test123
               I (test456) sent message num 5
Received message 5 from test456
Received message 11 from test123
               I (test456) sent message num 6
Received message 6 from test456
...
```

<br>

운영 시스템에서 사용하는 Multicast IP:Port와 같은 것을 사용하여 테스트하면,

위 테스트 메시지가 실제 서비스에 전송되어 문제를 발생시킬 수 있으므로,

우선 다른 IP:Port로 네트워크 문제가 있는지를 점검한다.

<br>

또한, tcpdump 로 주고받는 메시지를 관찰할 수 있다.

```sh
# 각 노드에서 사용한 명령어
$ tcpdump -i enp0s3 udp port 7001 -A


# 1번 시스템 로그
15:09:36.637942 IP <xxxx>.afs3-callback > 239.192.0.0.afs3-callback:  rx type 115 (1472)
E..... .....
A"l.....Y.Y.......$..............test123aaaaaaaaaaaaaaaaaaaaa ...



# 2번 시스템 로그
15:09:38.391229 IP <xxxx>.afs3-callback > 239.192.0.0.afs3-callback:  rx type 115 (1472)
E..... .....
A"l.....Y.Y.......(..............test456aaaaaaaaaaaaaaaaaaaaa ...
```

<br>

위와 같이 Multicast 문제를 점검할 수 있고,

이 사례의 고객은 앞단 L4 의 IGMP 관련 설정 변경 후 문제가 해소되었다.

<br>

# 3. References

없음
