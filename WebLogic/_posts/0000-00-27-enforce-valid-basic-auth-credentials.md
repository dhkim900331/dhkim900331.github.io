---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] enforce-valid-basic-auth-credentials"
tags: [Middleware, WebLogic]
typora-root-url: ..
---


# 1. Overview

enforce-valid-basic-auth-credentials


<br><br>


# 2. Descriptions

## 2.1 enforce-valid-basic-auth-credentials

해당 옵션은 웹로직에서 실행중인 어플리케이션에서 HTTP BASIC 

authentication을 사용시 추가적으로 인증을 할 것인지 선택하는 옵션입니다. 

웹보안 중에 http 인증 방식이 여러가지 있는데 

그 중 HTTP BASIC authentication인증방식을 웹로직에서 디폴트로 ‘사용’ 

설정이 되어있습니다. 

예를 들어 enforce-valid-basic-auth-credentials값이 true일 때, 

어플리케이션에서 웹로직의 HTTP BASIC authentication인증 방식을 사용하려면 

웹로직의 id/pw를 입력해야 합니다. 

<br>

해당 옵션을 false로 변경하면, id/pw를 따로 물어보지 않고 HTTP BASIC 

authentication인증 방식을 사용할 수 있습니다. 

어플리케이션에서 자체 인증방식을 구현 할 수도 있고, 웹로직의 HTTP BASIC 

authentication을 사용 할 수도 있습니다. 


<br><br>


## 2.2 적용 방법

config.xml 파일에서 `</security-configuration> `태그 위에 아래 옵션 추가하시고, 웹로직 재기동을 하시면 되겠습니다.

config.xml 에 설정하였기 때문에, 해당 도메인 전체에 적용되는 설정입니다.

<br>

```xml
...skip...
<enforce-valid-basic-auth-credentials>false</enforce-valid-basic-auth-credentials>
 </security-configuration>
...skip...
```

<br>


## 2.3 보안 이슈

오라클 공식 답변에 의하면,

해당 옵션은 보안에 관련한 이슈가 없습니다.

