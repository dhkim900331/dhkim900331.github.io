---
date: 2025-03-08 10:18:05 +0900
layout: post
title: "[WebLogic/Clustering] MulticastTest Utility On Production Clustering Environment"
tags: [Middleware, WebLogic, ]
typora-root-url: ..
---

# 1. Overview

MulticastTest 유틸리티의 운영계 클러스터링 환경에서의 사용

<br>


# 2. Descriptions

MulticastTest 유틸리티는 WebLogic Multicast Clustering 환경에서 UDP Traffic 테스트를 위해 사용되는 도구다.

이 도구는, 실제로 UDP Traffic 을 생성하여 통신에 문제가 없는지 검증하기 때문에 실 운영 서비스에서 사용을 금지한다.

<br>

[MulticastTest](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/admrf/utils.html#GUID-E6BE2C6E-3E7D-405A-8BE1-82305F57E2A2) 의 주의점 참고

> Do NOT run the `MulticastTest` utility by specifying the same multicast address (the `-a` parameter) as that of a currently running WebLogic Cluster. The utility is intended to verify that multicast is functioning properly before starting your clustered WebLogic Servers.

<br>

고객은, 운영계 서비스 환경에서 이 도구를 사용하였고, 이후로 정상 서비스되던 WLS 인스턴스들이 Clustering 에서 Removed 되었다.

이로 인해, DynamicServerList On 옵션을 사용하는 OHS 에서는 Removed 된 WLS 인스턴스들로 요청을 전달하지 못하는 장애가 발생했다.

해소 방법으로는, 잘못된 도구 사용에 의한 원인이 있으므로 WLS 재기동을 해야 한다.


<br><br>

<br>

# 3. References

**MulticastTest Utility 사용 후 WebLogic Clustering Member들이 Removed (Doc ID 3073507.1)**
