---
date: 2024-04-25 13:48:55 +0900
layout: post
title: "[WebTier/OHS] 한글 파일명 호출 시 HTTP 404 Not Found"
tags: [WebTier, OHS, Apache, Encoding]
typora-root-url: ..
---

# 1. Overview

OHS(Oracle HTTP Server) 에서 한글 파일명을 호출 시, HTTP 404 Not Found Error가 발생한다.

FS(File System) 에는 한글 파일명이 올바르게 존재하고 있다.

이러한 경우 어떻게 문제를 해결해야 하는지 살펴본다.
{{ site.content.br_big }}
# 2. Descriptions

## 2.1 Problem and Solution

FS 내에 다음과 같이 한글로 된 파일명이 존재한다.

```sh
$ ls -al ./config/fmwconfig/components/OHS/instances/worker1/htdocs
-rw-rw-r-- 1 weblogic weblogic    0  4월 24 14:24 한글파일
```
{{ site.content.br_small }}
Web Browser 에서 호출 시에 resource를 가져오지 못한다.

![Korean-Filename-With-404-Not-Found_1](/../assets/posts/images/WebTier/Korean-Filename-With-404-Not-Found/Korean-Filename-With-404-Not-Found_1.png)
{{ site.content.br_small }}
OHS access_log는 다음과 같이 인코딩된 String으로 resource를 찾고 있다.

```
[24/Apr/2024:14:29:18 +0900] 0065h3nkzGPEoIXElvtlWJ00Bn1v000003 "GET /%ED%95%9C%EA%B8%80%ED%8C%8C%EC%9D%BC HTTP/1.1" 404 210
```
{{ site.content.br_small }}
[Unicode converter 와 같은 사이트](https://r12a.github.io/app-conversion/) 에서 %ED%95%9C%EA%B8%80%ED%8C%8C%EC%9D%BC 을 변환해보면 '한글파일' 로 우리가 Web Browser 에 요청한 resource를 제대로 찾고 있는 것은 분명하다.

![Korean-Filename-With-404-Not-Found_2](/../assets/posts/images/WebTier/Korean-Filename-With-404-Not-Found/Korean-Filename-With-404-Not-Found_2.png)
{{ site.content.br_big }}
FS에 존재하는 '한글파일' resource를 정확하게 Web Browser에 요청하였고,

이 요청을 받는 Web Server의 Access Log에 기록된 UTF8 인코딩의 결과를 보면 문제가 없어 보인다.
{{ site.content.br_small }}
조사 결과,

해당 '한글파일' **파일명**이 UTF8 이 아닌 eucKR 로 인코딩이 되어 있다는 점이다.

```sh
$ echo $LANG
ko_KR.euckr
```
{{ site.content.br_small }}
UTF-8 Locale을 설정하고, 다시 살펴보면 '한글파일' 파일명이 전혀 다른 인코딩 결과물로 확인된다.

(여기서 간과할 수 있는 부분은, SSH Client Program의 encoding 또한 UTF-8 에서 확인해야 한다.)

```sh
$ LANG=en_US.UTF-8
$ ls -al ./config/fmwconfig/components/OHS/instances/worker1/htdocs
-rw-rw-r-- 1 weblogic weblogic    0 Apr 24 14:24 ''$'\307''畸'$'\333\306\304\300\317'
```
{{ site.content.br_small }}
Web Server는 UTF-8 로 resource를 찾지만,

FS에는 eucKR 로 인코딩된 결과물만 있기 때문에, HTTP 404 Not Found가 발생한 것이다.
{{ site.content.br_small }}
이를 해결 하기 위해서, 파일의 인코딩을 변경한다.

```sh
$ convmv -f euc-kr -t utf-8 --notest <PATH>/한글파일
```
{{ site.content.br_small }}
그리고, 접속한 Client Program(putty 등)의 encoding 또한 euc-kr 을 utf-8 로 변환해주면,

모든 것(SSH Client, OS Envs, File)이 UTF-8 인 환경에서 제대로된 파일을 확인할 수 있다.

```sh
$ echo $LANG
en_US.UTF-8

$ ls -al ./config/fmwconfig/components/OHS/instances/worker1/htdocs/
-rw-rw-r-- 1 weblogic weblogic    0 Apr 24 14:24 한글파일
```
{{ site.content.br_small }}
동시에, Web Browser에서도 문제 없이 파일을 얻을 수 있다.

![Korean-Filename-With-404-Not-Found_3](/../assets/posts/images/WebTier/Korean-Filename-With-404-Not-Found/Korean-Filename-With-404-Not-Found_3.png)
{{ site.content.br_big }}
## 2.2 So Why?

이 문제를 설명하기 위해 약간의 배경 지식을 설명한다.

영어 이외의 대부분의 문자들은 ASCII 로 표기할 수 없기 때문에, Unicode 로 정의되어 있다.

Unicode 로 정의되어 있는 문자들은, UTF(Unicode Transformation Format) 로 인코딩 된다.

한글은 대게 3bytes 로 이루어져 있으며, 이를 UTF-8(8 bit) 인코딩을 하는 것이다.
{{ site.content.br_small }}
또한, [Uniform Resource Identifier (URI): Generic Syntax](https://datatracker.ietf.org/doc/html/rfc3986) 에서 소개하는 [2.1.  Percent-Encoding](https://datatracker.ietf.org/doc/html/rfc3986#section-2.1)에 따라, `%ED%95%9C%EA%B8%80%ED%8C%8C%EC%9D%BC` 와 같은 인코딩 결과물을 생성 한다.

이 인코딩 된 URL 값으로 Web Server 에서 Resource를 처리하려고 하며,

그렇게 되면 어떤 파일명(한글 등)을 가지고 있어도 처리할 수 있게 된다.
{{ site.content.br_small }}
위에서 한차례 설명하였듯이,

표준 인코딩 방식인 UTF-8 로 Resource를 찾으려고 하지만,

목표 결과물은 UTF-8이 아니기 때문에 이러한 문제가 생긴것이다.
{{ site.content.br_big }}
# 3. References

[Uniform Resource Identifier (URI): Generic Syntax](https://datatracker.ietf.org/doc/html/rfc3986)

[한글은 어떻게 전산화되었을까? 아스키코드와 유니코드](https://blog.naver.com/with_msip/222009981690)

[https://namu.wiki/w/유니코드](https://namu.wiki/w/%EC%9C%A0%EB%8B%88%EC%BD%94%EB%93%9C)

[유니코드와 UTF 이해하기](https://velog.io/@goggling/%EC%9C%A0%EB%8B%88%EC%BD%94%EB%93%9C%EC%99%80-UTF-%EC%9D%B4%ED%95%B4%ED%95%98%EA%B8%B0)

[유니코드 변환기 온라인](https://unicode.codethoi.com/ko/index.html)

**한글파일 요청 시 404 Not Found 발생 (Doc ID 3019045.1)**
