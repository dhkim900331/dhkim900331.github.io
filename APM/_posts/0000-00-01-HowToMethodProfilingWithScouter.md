---
date: 2022-04-11 12:00:04 +0900
layout: post
title: "[APM/Scouter] Method Profiling"
tags: [APM, Scouter, Method, Profling, XView]
typora-root-url: ..
---

# 1. 개요

* Scouter APM에서 Method Profiling 방법

<br>
# 2. 설명

* 가령, 다음과 같은 구조를 갖는 Application이 있다고 해보자.
  * org.apache.catalina.session 패키지 아래의 class와 method 들이 수두룩~
  * com.athena.dolly 아래에도 수두룩~
  * org.infinispan 아래에도 수두룩~
  * com.example.parent Class 아래에는 child 라는 method 1개

<br>
## 2.1 hook_method_patterns

* 특정 Method만 Profiling

  ```
  com.example.parent.child
  ```

* 특정 Class 아래에 모든 Method Profiling

  ```
  org.apache.catalina.session.<Class
  ```

<br>* 특정 Pkg 아래 모든 Class 및 모든 Method Profiling

  ```
  com.athena.dolly.*.*
  ```

  * 대부분 이 설정을 쓸 것으로 예상이 된다.
  * `hook_method_patterns` 는 Method 까지 언급을 해야 하므로, 반드시 마지막 *(asterik)는 Method 까지 도달해야 한다.

* A_Pkg.B_Pkg.C_Pkg.D.class 내에 여러 Method 가 있다고 할때를 가정해서 여러가지 상황을 보면

  * (1). A_Pkg 밑에 모든 것을 출력

    ```
    A_Pkg.*.*
    ```

  * (2). B_Pkg 디렉토리에서 "dhkim" 이름을 갖는 Package 가 공통으로 있을 때 모든 Method 출력

    ```
    *.dhkim.*.*
    ```

* Pkg의 depth 가 깊던 안깊던, 최대 2개의 *(asterik)만 사용하면 된다.

  * 해당 내용은 Scouter 가이드문서 등으로 확인되지 않지만, 필드 및 로컬 테스트로 검증됨

* syntax

  * ```
    hook_method_patterns=org.apache.catalina.session.*.*,com.athena.dolly.*.*,org.infinispan.client.hotrod.*.*,java.*.*
    ```

<br><br>
## 2.2 hook_method_access

* 기본값은 아래처럼 적용된다.

  ```
  hook_method_access_public_enabled=true
  hook_method_access_private_enabled=false
  hook_method_access_protected_enabled=false
  hook_method_access_none_enabled=false
  ```

  * 모든 접근제어자를 보려면 위 값을 모두 true 로 설정하면 된다.
