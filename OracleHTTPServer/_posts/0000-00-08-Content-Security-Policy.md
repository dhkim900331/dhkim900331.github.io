---
date: 2023-03-03 08:54:19 +0900
layout: post
title: "[OracleHTTPServer] Content Security Policy Header"
tags: [OracleHTTPServer, OHS, Apache, Header, CSP]
typora-root-url: ..
---

# 1. 개요

Content Security Policy Header를 테스트한다.

default-src 개념만 알면, 나머지 XXX-src 는 동일하므로 default/script-src 만 테스트한다.



# 2. 설명

## 2.1 default-src

아래와 같이 설정 시에, 모든 동작(img, css, media, script, connect)이 수행되지 않는다.

```
<IfModule mod_headers.c>
Header always set Content-Security-Policy: "default-src 'none';"
</IfModule>
```



예시로 Javascript 동작 과정에서 default-src를 살펴보자.

다음의 Inline Script , HTML 로 구성된 경우,

```html
<html>
	<head>
		<meta charset="UTF-8">
		<title>Welcome</title>
	</head>
<body>
	<button onclick="alert('Hello World')">Button</button>
</body>
</html>
```



Button 이 동작하지 않으며 Browser Console에 log가 있다.

```
Refused to apply inline style because it violates the following Content Security Policy directive: "default-src 'self'". Either the 'unsafe-inline' keyword, a hash ('sha256-biLFinpqYMtWHmXfkA1BPeCY0/fNt46SAZ+BBk5YUog='), or a nonce ('nonce-...') is required to enable inline execution. Note that hashes do not apply to event handlers, style attributes and javascript: navigations unless the 'unsafe-hashes' keyword is present. Note also that 'style-src' was not explicitly set, so 'default-src' is used as a fallback.
```





self(나 자신 허용, 하위 도메인은 아님) 설정을 하거나, `wls.local:80` 도메인은 허용 설정 할 수 있다.

그러나 아래와 같은 설정에도, script 는 동작하지 않는다.

```
Header always set Content-Security-Policy: "default-src 'self';"
또는
Header always set Content-Security-Policy: "default-src wls.local:80;"
```



그 이유는, 위 Browser Console log에도 나와 있는데,

최소한 아래와 같이 `unsafe-inline` 으로 inline javascript 허용을 해야 한다.

```
Header always set Content-Security-Policy: "default-src 'self' 'unsafe-inline';"
또는
Header always set Content-Security-Policy: "default-src 'none' 'unsafe-inline';"
```



## 2.2 script-src

script-src를 self(나 자신 허용, 하위 도메인 불가) 설정 시에는 `unsafe-inline` 등의 설정이 없어도 된다.

```
Header always set Content-Security-Policy: "default-src 'none'; script-src 'self';"
```



다음과 같이 외부 도메인의 External Script 설정이 있다.

```html
<html>
    <head>
        <meta charset="UTF-8">
        <title>Welcome</title>
        <script src="http://child.wls.local/scripts/button.js"></script>
    </head>
<body>
    <button>Button</button>
</body>
</html>
```



아래와 같이 `self` 뿐만 아니라 하위 도메인도 별개로 추가 해야 한다.

```
Header always set Content-Security-Policy: "default-src 'none'; script-src 'self' child.wls.local;"
```



# 3. 참고

- https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
- https://cyberx.tistory.com/171
- https://velog.io/@taylorkwon92/%EC%98%A4%EB%8A%98%EC%9D%98-TIL
