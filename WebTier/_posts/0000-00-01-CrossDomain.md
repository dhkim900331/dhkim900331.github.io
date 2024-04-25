---
date: 2022-04-30 14:19:33 +0900
layout: post
title: "[WebTier/OHS] Cross Domain (Access Control Allow Origin)"
tags: [WebTier, OHS, Apache, CORS]
typora-root-url: ..
---

# 1. 개요

CORS 설정 방법.
{{ site.content.br_small }}
# 2. 설명

```bash
LoadModule headers_module modules/mod_headers.so

# 모든 URL
<IfModule mod_headers.c>
    Header add Access-Control-Allow-Origin *
    Header set Access-Control-Allow-Credentials true
</IfModule>

# 다음 URL
<IfModule mod_headers.c>
    SetEnvIf Origin "http(s)?://(abc|def\.)?(test.com|beta.com)$" AccessControlAllowOrigin=$0$1
    Header add Access-Control-Allow-Origin %{AccessControlAllowOrigin}e env=AccessControlAllowOrigin
    Header set Access-Control-Allow-Credentials true
</IfModule>
```

> 다음 URL은 
>
> http://abc.test.com
>
> http://abc.beta.com
>
> https://abc.test.com
>
> https://abc.beta.com
>
> http://def.test.com
>
> http://def.beta.com
>
> https://def.test.com
>
> https://def.beta.com
