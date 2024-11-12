---
date: 2024-11-05 14:25:03 +0900
layout: post
title: "[WebTier/OHS] iPlanet Error Page To OHS"
tags: [WebTier, OHS, iPlanet, ErrorDocument]
typora-root-url: ..
---

# 1. Overview
iPlanet 에 정의된 Error page 설정을 OHS로 Migration 하는 방법


<br><br>

<br>

# 2. Descriptions
iPlanet에 정의된 Error page 설정은 다음과 같이 HTTP Response Status Code가 정의되지 않고, Status Text로 정의되어 있다.
```
# in Ipalnet
Error fn="send-error" reason="Bad Request" path="/error/error_page.html"
```

<br>

OHS에서 ErrorDocument 설정은, [<3-digit code>](https://httpd.apache.org/docs/current/mod/core.html#errordocument) 가 필요하다.

```
# in OHS
ErrorDocument 400 "/error/bad-request.html"
```

<br>

iPlanet에 정의된 `reason` 값을 [HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)를 제공하는 사이트에서 Code 값을 확인하여, OHS에 정의할 수 있다.


<br><br>


# 3. References
iPlanet 에 정의된 Error page 설정을 OHS로 Migration 하는 방법 (Doc ID 3057285.1)