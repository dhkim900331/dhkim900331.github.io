---
date: 2023-11-03 08:57:37 +0900
layout: post
title: "[WebLogic] How To Load Balancing Without Proxy?"
tags: [Middleware, WebLogic, Load Balancing, Plugin, Proxy]
typora-root-url: ..
---

# 1. Overview

WebLogic 앞단에 Proxy Plugin이나 Load Balancer 없이 어떻게 Load Balancing 을 할 수 있는가?

<br><br>

# 2. Descriptions

WL Proxy Plugin을 사용하는 Web server에서는 기본적으로 다음의 목적을 달성 할 수 있다.

- 여러 Weblogic Instances를 하나의 Pool로 만들고, 항상 가용 가능한 목록만 제공하므로 사용자는 Weblogic의 System Down을 알 수 없는 투명성 제공
  - DynamicServerList 기능을 쓰지 않더라도 Plugin은 문제가 있는 Instance를 MaxSkipTime(기본값 10초) 만큼 보류하여 건강한 Pool을 유지한다.
- 최초 접근하는(HTTP Session이 아직 없는) 사용자의 요청을 Round Robin 방식으로 Instances에 제공하므로, 균등한 부하 분산 가능
  - 최초 접근시에만 RR 이며, 즉시 이후부터는 Header의 JSESSIONID 값의 Primary Instance로 요청한다.
- 이미 HTTP Session이 있는 요청은 Session을 가지고 있는 Instance로 요청이 고정될 수 있도록 Session Sticky 가능
  - HTTP Session이 없으면, Secondary Instance에서 Session을 복제해 오는 것은 Cluster 의 기능이며, 이것은 Weblogic Cluster의 Failover 기능
- Post data 전송 이후 장애가 발생하여도, Cached Post data로 Failover 가능
- Web과 WAS간의 SSL 구현 가능
- 기타(Websocket, Monitoring, Keepalive, Debugging)



이처럼, Plugin을 쓰는 경우에 얻는 이점이 많으며 Plugin을 쓰지 않더라도 기본적인 Round Robin 또는 Session Sticky 는 구현할 수 있다.

`mod_proxy` 또는 기타 LoadBalancer 기능을 제공하는 소프트웨어/하드웨어를 통해서 Weblogic Instances를 대상으로 Round Robin 및 Session Sticky 를 수행할 수 있다는 것이다.



다만, Plugin의 DynamicServerList와 같은 기능이 없기 때문에 잦은 Weblogic Instance의 System Down이 발생하면 가용 가능한 Instances 인식이 느리다.

DynamicServerList는 Plugin의 재시작(프로세스 재기동) 없이도 Weblogic Instance를 추가/삭제 할 수 있는 역동적인 기능을 제공하는 이점 또한 가지고 있다. (Weblogic Clustering 구현을 해야 가능한 부분)



또한 도중에 중단된 Post 요청 서비스를 다시 다른 Instance에서 재개할 수 있도록 FileCaching 기능 또한 제공한다.

Plugin이 없다면, 다시 처음부터 Post data를 전송해야 한다는 것이다.



결론은, JSP/Servlet 요청들에 대해서는 Proxy Plugin 또는 유사 기능을 수행하는 환경이 반드시 있어야 Load Balancing이 가능하다.

<br><br>

# 3. References

[What are Oracle WebLogic Server Proxy Plug-Ins?](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/develop-plugin/overview.html#GUID-C5274793-DD8C-4BEF-84A4-E64A528C4BA2)

[DynamicServerList](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/develop-plugin/plugin_params.html#GUID-EBAC8454-5785-4675-B74F-AAD93CFA2A1F)

[MaxSkipTime](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/develop-plugin/plugin_params.html#GUID-1B6B24C3-608A-4A1D-9A59-A215C8DCB013)

[FileCaching](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/develop-plugin/plugin_params.html#GUID-FC5A898C-7767-40CB-8480-A27E14507C3B)
