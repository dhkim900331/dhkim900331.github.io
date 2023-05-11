---
date: 2023-05-11 09:07:29 +0900
layout: post
title: "[WebLogic] Uploading Files with Java Servlet Tech"
tags: [Middleware, WebLogic, Multipart, Upload, Servlet]
typora-root-url: ..
---

# 1. 개요

J2EE 6 의 Servlet 3.0 부터 추가된 Servlet Fileupload 를 사용해본다.

WebLogic 에서 대용량 파일 업로드시에 어떤 처리 과정을 갖는지 살펴본다.



# 2. File upload Implements

[Chapter 16 Uploading Files with Java Servlet Technology](https://docs.oracle.com/javaee/6/tutorial/doc/glrbb.html)

에 따르면, Servlet 3.0 이전에는 File uplaod 시에 외부 라이브러리 등 복잡한 구성 요소를 가져야 했지만

Servlet 자체에서 지원하게 되어, 그럴 필요가 없어졌다는 의미이다.



해당 기능의 App 구현은 [FileUpload]({{ site.url }}/Servlet/FileUpload) 에서 다루었다.





