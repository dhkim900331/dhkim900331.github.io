---
date: 2025-08-29 12:22:37 +0900
layout: post
title: "[WebLogic/LDAP] Using Keep alive for an external ldap"
tags: [Middleware, WebLogic, LDAP]
typora-root-url: ../..
---

# 1. Overview

WebLogic에서 External LDAP Server와 연결 시, 잦은 Connection 생성으로 인한 Port 고갈 현상 발생 해결

<br><br>


# 2. Descriptions

WebLogic에는 기본적으로 Embedded LDAP 에 포함되어 있고, External LDAP Server를 별도로 연결하여 사용할 수 있다.

고객은 WLS Admin Console에서 특정 사용자로 로그인을 시도 하는데, 이때 WLS는 External LDAP Server를 조회한다.

이 과정에서 External LDAP Server와 Connection을 생성하고 이것을 사용하는데, 잦은 사용자 조회로 인하여 AdminServer의 Machine에서 Port 고갈이 발생하였다.

Port 고갈로 인하여 Admin Server는 LDAP Server에 연결 하지 못하며, 다음의 Warning message가 기록되었다.

```
<Warning> <Security> <BEA-099117> <The LDAP authentication provider named "<LDAP Provider Name>" failed to make connection to ldap server at ldap://<LDAP IP>:<LDAP PORT>, the error cause is: Cannot assign requested address.> 
```

<br>

Admin Console에 접근하는 사용자는 많지 않으나, 접근 시도 횟수가 많으므로 Keep alive 옵션을 활성화 하면 사용한 Connection을 재사용하므로 Port 고갈 문제를 해결할 수 있다.

```
Console - Security Realms - Providers - Authentication - <LDAP Provider Name> - Configuration - Common - Provider Specific - Keep Alive Enabled
```


<br><br>


# 3. References

**Admin Server에서 잦은 External LDAP Server 연결로 인해 Port 고갈 (Doc ID 3094164.1)**
