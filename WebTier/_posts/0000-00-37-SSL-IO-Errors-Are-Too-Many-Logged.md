---
date: 2025-03-08 10:18:06 +0900
layout: post
title: "[WebTier/OHS] SSL IO Errors Are Too Many Logged"
tags: [WebTier, OHS, OSSL]
typora-root-url: ..
---

# 1. Overview

SSL IO Error가 너무 많이 기록되어 있습니다.

```
OHS:2079 Client SSL handshake error, nzos_Handshake returned 28862(X.X.X.X:443)
OHS:2171 NZ Library Error: SSL IO error [Hint: the client stopped the connection unexpectedly]
```


<br><br>


# 2. Descriptions

해당 사례는, WAF (Web Application Firewall)을 사용하는 고객에게 발생했습니다.

OHS 와 연결을 하려는 사용자는 먼저 WAF와 1차적으로 세션이 연결 됩니다.

WAF는 이 사용자를 뒷단의 OHS 와 연결을 합니다.

<br>

OHS와 이미 연결된 사용자가 SSL/TLS 1.0 과 같은 1.2 미만의 SSL Procotol 을 사용하여 Handshake를 하려고 시도합니다.

당시 WAF는 TLS 1.2 미만 SSL Protocol을 사용을 Reject 하는 Rule이 적용되어 있었습니다.

이에 따라, WAF는 OHS와 연결이 되어 있는 사용자의 Session을 Drop 시킵니다.

OHS는 이미 사용자와 연결된 후 SSL Handshake를 진행 하던 도중에, Socket 이 닫혀 다음과 같은 발생했습니다.

<br>

```
OHS:2079 Client SSL handshake error, nzos_Handshake returned 28862(X.X.X.X:443)
OHS:2171 NZ Library Error: SSL IO error [Hint: the client stopped the connection unexpectedly]
```

<br>

위와 같은 사례에서 의심이 되는 것은,

클라이언트가 어떻게 WAF를 통해 OHS와 연결된 후에 TLS 1.2 미만 프로토콜을 사용할 수 있는지에 대해 기술적으로 검증되지 않음.

<br>

이는, 고객사 WAF 를 다루는 네트워크 팀에 의하여 의견이 제시된 것임.


<br><br>


# 3. References

<br>

