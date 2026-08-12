---
date: 2025-01-31 09:38:02 +0900
layout: post
title: "[WebLogic] Disable Oracle Fast Application Notification With WLS"
tags: [Middleware, WebLogic, Fan, RAC, MDS]
typora-root-url: ../..
---

# 1. Overview

WLS 환경에서 Fast Application Notification(FAN) 을 Disable 하여도 괜찮은지?

<br>


# 2. Descriptions

FAN은 DB 를 사용할 수 없을 때, Notification을 받아 가용 가능한 다른 DB로 연결이 되도록 지원하는 기능이다.

WLS에서 이미 Multidatasource를 통해 유사 기능이 제공되고 있으며,

[Active GridLink Configuration for Database Outages](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/jdbca/jdbc-data-sources-types.html#GUID-4F1BB135-80D6-4B0C-AD5F-8BE69E7683BE) : FAN은 Active GrindLink DS 에서 사용이 가능하다.

그러므로, 기본적으로 활성화 되어 있는 FAN 을 Disabled 할 수 있다.

<br>


# 3. References

[Active GridLink Configuration for Database Outages](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/jdbca/jdbc-data-sources-types.html#GUID-4F1BB135-80D6-4B0C-AD5F-8BE69E7683BE) 

Oracle RAC FAN Support for ASAP ([Doc ID 2367847.1](https://mosemp.us.oracle.com/epmos/faces/ui/km/DocumentDisplay.jspx?id=2367847.1))
