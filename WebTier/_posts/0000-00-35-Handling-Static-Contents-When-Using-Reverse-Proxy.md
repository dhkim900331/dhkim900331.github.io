---
date: 2025-03-08 10:18:06 +0900
layout: post
title: "[WebTier] Handling Static Contents When Using Reverse Proxy"
tags: [WebTier, OHS, Apache, Reverse, Proxy]
typora-root-url: ..
---

# 1. Overview

Reverse Proxy 환경에서 정적 컨텐츠를 Web Server의 Document Root 에 제공하는 방법

<br>

# 2. Descriptions

다음의 a.png를 제공하는 index.jsp

```jsp
<html lang="ko">
<body>
    <h1>Welcome to Index Page</h1>
    <img src="/images/a.png"/>
</body>
</html>
```

<br>

방법 하나, images 디렉터리를 제외하는 방식의 Proxy 사용

```
<VirtualHost *:80>
	ServerName wls.local
	ProxyPreserveHost On
	ProxyRequests Off
	ProxyPass /images !
	ProxyPass / http://wls.local:8002/
	ProxyPassReverse / http://wls.local:8002/
</VirtualHost>
```

<br>

방법 둘, images 디렉터리를 우선 처리하는 방식의 Proxy 사용

```
<VirtualHost *:80>
	ServerName wls.local
	ProxyPreserveHost On
	ProxyRequests Off
	
	RewriteEngine On
	RewriteRule ^/images/(.+)$ /images/$1

	ProxyPass / http://wls.local:8002/
	ProxyPassReverse / http://wls.local:8002/
</VirtualHost>
```

<br>

이외에도 LocationMatch/ProxyPassMatch 등의 방법이 있겠지만, 가장 간단한 두 사례다.


<br><br>


# 3. References

https://stackoverflow.com/questions/27443742/how-to-server-static-files-proxy-context

