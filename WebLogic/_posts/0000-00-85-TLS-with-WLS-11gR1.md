---
date: 2024-06-25 16:09:26 +0900
layout: post
title: "[WebLogic/TLS] TLS with WLS 11gR1"
tags: [Middleware, WebLogic, TLS]
typora-root-url: ..
---

# 1. Overview
WLS 11gR1 에서 TLS 활성화 방법





# 2. Descriptions
WLS 10.3.6 (JDK 1.7) 환경에서 Inbound 또는 Outbound SSL 설정 방법.



아래 내용에 따라, JDK 1.7 update 1 이상 에서 TLS 1.2 를 사용 가능.

[Transport Layer Security (TLS) Support](https://docs.oracle.com/middleware/11119/wls/NOTES/whatsnew.htm#CHDEECCD)

> WebLogic Server supports the use of TLS V1.2 when using the JSSE provider in JDK 7 update 1 (or later JDK 7 releases).



JDK 1.7 Cipher suites

> [Cipher Suites](https://docs.oracle.com/javase/7/docs/technotes/guides/security/SunProviders.html#SunJSSEProvider)



Inbound/Outbound 활성화 방법

>  How to Configure SSL/TLS Protocols in Oracle WebLogic Server - Disable SSL 2.0/3.0 and Enable TLS 1.2 / TLS 1.3 (Doc ID 2162789.1)
>
> Section. "SSL / TLS Protocol Configuration for Oracle WebLogic Server"
>
> Secion. "Web Services and Client Applications (Outbound Connections)"



JSSE 활성화 방법

> [Enabling and Disabling the JSSE-Based SSL Implementation](https://docs.oracle.com/cd/E23943_01/web.1111/e13707/ssl.htm#BABIJEJD)





# 3. References

본문에 링크되어 있음.