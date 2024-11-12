---
date: 2024-10-30 14:41:56 +0900
layout: post
title: "[WebTier/OHS] How To DNS Lookup?"
tags: [WebTier, OHS, ]
typora-root-url: ..
---

# 1. Overview
OHS/Apache 에서 DNS Lookup 에 관한 설명


<br><br>

<br>

# 2. Descriptions
[The "main server" Address ](https://httpd.apache.org/docs/trunk/dns-caveats.html) 설명과 같이, OS의 기본 Kernel 구현을 따른다.
`gethostname` 의 호출과 동일하다는 것이다.

<br>

Kernel 설명을 참고하면, [/etc/nsswitch.conf](https://man7.org/linux/man-pages/man5/nsswitch.conf.5.html) 에서 hosts: 로 우선순위가 지정된다.
files는 `/etc/hosts` 를 의미하고, dns는 [/etc/resolv.conf](https://man7.org/linux/man-pages/man5/resolv.conf.5.html) 를 의미한다.


<br><br>

<br>

# 3. References
본문에 포함되어 있음.