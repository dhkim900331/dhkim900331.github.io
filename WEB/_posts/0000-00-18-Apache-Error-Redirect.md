---
date: 2023-07-25 09:33:29 +0900
layout: post
title: "[WEB/Apache] Error Redirect"
tags: [WEB, Apache, ErrorDocument, Rewrite, Redirect]
typora-root-url: ..
---

# 1. Overview

ErrorDocument 로 접수되는 Http Status Code를 Redirection 할 수 있다.





# 2. Descriptions

```
ErrorDocument 404 /error/404.html
ErrorDocument 500 /error/500.html

RewriteEngine on
RewriteCond %{REQUEST_URI} /error/404.html
RewriteRule ^/.* - [R=500]
```



사용자의 요청이 HTTP 400 를 유발하는 경우, /error/404.html 을 호출하게 된다.

RewirteRule 에 의하여 HTTP 500 으로 Redirect 하게 되고, 최종적으로 사용자는 HTTP 500 Code와 함께

/error/500.html 을 보게 된다.





## 3. References

https://serverfault.com/questions/974324/apache-httpd-rewrite-backend-proxy-http-error-500-to-503
