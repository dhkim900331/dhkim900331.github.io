---
date: 2026-09-30 16:00:00 +0900
layout: post
title: "[WebTier/OHS] ProxyPassMatch matchable worker로 인한 ProxyPass 404"
tags: [WebTier, OHS, Apache, mod_proxy, ProxyPass]
typora-root-url: ../..
---

# 1. Overview

OHS 패치 후 일부 `ProxyPass` 경로가 backend로 전달되지 않고 404로 처리될 수 있다.

이는 Apache HTTP Server의 [Commit 17770c2](https://github.com/apache/httpd/commit/17770c2)에서 변경된 matchable worker 처리와, 포괄 `ProxyPassMatch` 및 개별 `ProxyPass`가 같은 backend를 사용하는 구성의 상호작용으로 발생할 수 있다.

<br><br>


# 2. Descriptions

## 2.1 `$1`과 matchable worker

다음 설정에서 `$1`은 요청마다 달라지는 backreference다.

```apache
ProxyPassMatch "^/(.*\.gif)$" "http://backend:8000/$1" timeout=30
```

과거에는 설정 시 등록된 `http://backend:8000/$1` worker와 실제 요청의 `http://backend:8000/a.gif` worker가 정확히 일치하지 않았다.

```text
Configured worker : http://backend:8000/$1
Request worker    : http://backend:8000/a.gif
```

따라서 `$1`에 들어간 값에 대응하는 configured worker를 찾지 못하면, `timeout=30`이 설정된 worker 대신 default reverse-proxy worker가 선택될 수 있었다.

Commit 17770c2는 `$1`을 고정 문자열이 아닌 가변 매칭 영역으로 처리하는 matchable worker를 도입했다. 이제 `/a.gif`, `/b.gif`와 같이 `$1` 값이 달라도 동일 configured worker를 찾아 설정값을 적용할 수 있다.

## 2.2 Worker hierarchy와 설정 등록 충돌

mod_proxy는 같은 backend에 대한 중복 worker 생성을 피하기 위해 backend URL의 공통 부모를 기준으로 worker를 관리한다.

```text
http://backend:8000/          <- parent worker
|- http://backend:8000/app-a  <- child worker
`- http://backend:8000/app-b  <- child worker
```

이 구조는 connection pool 등의 backend 자원을 불필요하게 중복 생성하지 않도록 한다.

다음처럼 포괄 `ProxyPassMatch`가 먼저 선언된 구성을 보자.

```apache
ProxyPassMatch "^/(?!app-a|app-b)" "http://backend:8000/"

ProxyPass /app-a http://backend:8000/app-a
ProxyPass /app-b http://backend:8000/app-b
```

OHS 기동 중 첫 번째 규칙은 root URL에 matchable worker를 만든다. 이후 일반 `ProxyPass`를 읽으면 mod_proxy는 기존 root worker를 같은 hierarchy의 worker로 찾는다.

Commit 17770c2 이후 이 기존 worker가 matchable worker이고 새 worker가 일반 worker이면 둘을 이전 방식으로 병합하지 않는다. 이 코드 경로에서는 일반 worker를 별도로 생성하는 대신, 후속 `ProxyPass` alias 등록을 rollback할 수 있다.

즉, OHS가 기동된 뒤 `/app-a` 또는 `/app-b`의 유효한 proxy alias가 남지 않을 수 있다. 이 경우 요청은 backend로 전달되지 않고 OHS의 로컬 경로 처리로 넘어가 404가 발생한다.

## 2.3 Resolution

구체적인 `ProxyPass`를 먼저 선언하고, 포괄 `ProxyPassMatch`를 마지막에 선언한다.

```apache
ProxyPass /app-a http://backend:8000/app-a
ProxyPassReverse /app-a http://backend:8000/app-a

ProxyPass /app-b http://backend:8000/app-b
ProxyPassReverse /app-b http://backend:8000/app-b

ProxyPassMatch "^/(?!app-a|app-b)" "http://backend:8000/"
```

문제는 runtime request matching이 아니라 OHS 기동 시 configuration 등록 단계에서 발생한다. 패치 후 일부 proxy 경로가 사라진 경우에는 `ProxyPassMatch`와 개별 `ProxyPass`의 선언 순서 및 backend URL hierarchy를 함께 확인한다.

<br><br>


# 3. References

[Apache HTTP Server Commit 17770c2](https://github.com/apache/httpd/commit/17770c2)

[mod_proxy ProxyPass Directive](https://httpd.apache.org/docs/2.4/mod/mod_proxy.html#proxypass)
