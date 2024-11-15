---
date: 2023-05-11 09:07:29 +0900
layout: post
title: "[WebLogic] Uploading Files with Java Servlet Tech"
tags: [Middleware, WebLogic, Multipart, Upload, Servlet]
typora-root-url: ..
---

# 1. Overview

J2EE 6 의 Servlet 3.0 부터 추가된 Servlet Fileupload 를 사용해본다.

WebLogic 에서 대용량 파일 업로드시에 어떤 처리 과정을 갖는지 살펴본다.


<br><br>


# 2. File upload Implements

[Chapter 16 Uploading Files with Java Servlet Technology](https://docs.oracle.com/javaee/6/tutorial/doc/glrbb.html)

에 따르면, Servlet 3.0 이전에는 File uplaod 시에 외부 라이브러리 등 복잡한 구성 요소를 가져야 했지만

Servlet 자체에서 지원하게 되어, 그럴 필요가 없어졌다는 의미이다.

<br>

해당 기능의 App 구현은 [FileUpload]({{ site.url }}/servlet/FileUpload) 에서 다루었다.


<br><br>


# 3. Uploading Test

MultipartConfig annoation은 다음과 같이 하였다.

```java
@MultipartConfig(
  location="/tmp/fileUploadTemp",
  fileSizeThreshold = 1024 * 1024 * 10,     // 10 MB
  maxFileSize = 1024 * 1024 * 1024 * 10,    // 10 GB
  maxRequestSize = 1024 * 1024 * 1024 * 10  // 10 GB
)
```

<br>


> 2023-12-21 위 MultiPartConfig annoation에 문제가 없어 보이는데, 적용되지 않는 현상이 WLS 14.1 (Servlet 4.0)에서 목격되어 아래와 같이 변경하였다. (줄바꿈 등으로 인한 문제인 것인지..)
>
> ```java
> @MultipartConfig(fileSizeThreshold=1024*1024*10,  // 10 MB
>                  maxFileSize=1024*1024*50,       // 50 MB
>                  maxRequestSize=1024*1024*100,    // 100 MB
>                                  location="/tmp/fileUploadTemp")
> ```
>

<br>

`fileSizeThreshold` 를 초과하는 경우, 임시로 `location`에 파일을 작성한다.

하나의 업로드 파일은 `maxFileSize`를 초과할 수 없다. (예외 처리)

다중 업로드된 파일의 전체 크기는 `maxRequestSize`를 초과할 수 없다. (예외 처리)

<br>

위와 같이 1개 파일 10GB 를 전송 가능하도록 설정하였다.

<br>

대용량 (10GB) 파일을 Uploading 한다.

```sh
$ mkdir /tmp/fileUploadTemp && cd "$_"
$ dd if=/dev/zero of=test.txt bs=1 count=0 seek=10G
$ curl -F 'file=@/tmp/fileUploadTemp/test.txt' http://wls.local:8002/fileUpload/fileuploadservlet
```


WebLogic Log에 예외가 발생한다.

```
The field file exceeds its maximum permitted  size of -2147483648 characters
```


WebLogic 프로토콜 maxPostSize는 -1 무제한이기 때문에, 추측되는 원인으로는, MultipartConfig annotation 설정에 문제가 있을 것이라 예상되었다.

Field 설정한 수치가 type을 벗어난것이 아닐까? (에러가 negative 이므로)

다음과 같이 재변경 하였다.

```java
@MultipartConfig(
  location="/tmp/fileUploadTemp",
  fileSizeThreshold = 1024 * 1024 * 10,     // 10 MB
  maxFileSize = -1 // unlimited
  maxRequestSize = -1 // unlimited
)
```


이 상황에서는 10GB 의 대용량 파일에도 문제 없이 WebLogic이 처리를 하였다.


<br><br>


# 4. Resource Monitoring

대용량 파일을 전송 시에, `fileSizeThreshold` 크기를 넘어서는 파일을 어떻게 처리하며, 그 사이에 Java Heap Resource는 어떤지 살펴본다.

<br>

5GB 파일을 전송하며,

```sh
$ dd if=/dev/zero of=test.txt bs=1 count=0 seek=5G
$ curl -F 'file=@/tmp/fileUploadTemp/test.txt' http://wls.local:8002/fileUpload/fileuploadservlet
```


아래 스크립트로 WebLogic 의 CPU/MEM 사용률을 확인한다.

```sh
$ sh << "EOF"
while true
do
 ps -p <WASPID> -o %cpu,%mem | tail -1 && sleep 1
done
EOF
```


파일 전송 전 평균 CPU 사용률은 40.25% 에서, 파일을 전송하면서 53.0% 까지 점차 올라갔다.

파일 전송 전 평균 Memory 사용류은 5.2% 에서, 변화가 전혀 없었다.

`fileSizeThreshold` 크기 만큼 Heap Memory에 담아 두는지 확인이 필요해보인다.

<br>

또한, `fileSizeThreshold` 크기를 넘어, `location`에 다음과 같이 파일이 생성되고 있었다.

```
upload_6a7e572a_18808acfaa3__7ffd_00000000.tmp
```


모두 전송이 완료될 때까지, 해당 파일에 쓰기 작업이 진행되었고, 전송이 완료된 후에는 제거되었다.

전송이 완료된 파일은 `location`에 저장되기도 한다. (target과 temp 공간이 같은 셈)

<br>

다음과 MultipartConfig에서 fileSizeThreshold 만 변경 하였다.

```java
@MultipartConfig(
  location="/tmp/fileUploadTemp",
  fileSizeThreshold = 1024 * 1024 * 1000,     // 1000 MB
  maxFileSize = -1 // unlimited
  maxRequestSize = -1 // unlimited
)
```


위 환경에서, 테스트하면 Java Heap memory 사용을 급격하게 하여, OOME 가 발생하였다.


<br><br>


# 5. References

**Servlet 3.0에서 도입된 Servlet File upload가 WebLogic Server에 미치는 영향 (Doc ID 2950552.1)**
