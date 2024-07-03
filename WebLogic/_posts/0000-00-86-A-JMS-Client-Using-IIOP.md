---
date: 2024-07-03 16:39:54 +0900
layout: post
title: "[WebLogic/JMS] A JMS Client using IIOP"
tags: [Middleware, WebLogic, JMS, IIOP, t3, client]
typora-root-url: ..
---

# 1. Overview
WebLogic 12.2.1.4 (12cR2) 환경에서 개발되는 JMS Client는 IIOP Protocol을 사용하여, JMS Resource에 접근할 수 있다.

그러나, 권장되는 것은 T3 Protocol 이다.

{{ site.content.br_big }}

# 2. Descriptions
[Overview of Standalone Clients](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/saclt/basics.html#GUID-9C190A32-C8FF-40AD-8186-33ADAD2E3CCC)에서 WebLogic Server와 독립적으로 사용하는 Standalone client의 전반적인 목차가 소개된다.

[Developing a WebLogic Thin T3 Client](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/saclt/wlthint3client.html#GUID-D352B8F0-1B9D-43E8-A675-BBFE7E4DE1E9)에서 가장 권장되는 Model 인 Thin t3 client 을 소개하며,

t3/t3s protocol을 사용하여 JMS 외에 여러 Resource에 접근하는 Standalone client를 개발할 수 있다.

{{ site.content.br_big }}

# 3. References
위 컨텐츠에 나와있음.