---
date: 2022-12-06 08:53:52 +0900
layout: post
title: "[WebTier/OHS] Proxy Plugin 12cR2"
tags: [WebTier, Apache, OHS, Proxy, Plugin]
typora-root-url: ..
---

# 1. 개요

WLS Proxy Plugin 12cR2 의 주요 옵션들에 대해서 살펴본다.

OHS 제품에 적용될 수 있는 (`Applies to: Oracle HTTP Server`) 항목만 살펴본다.

또한, 자세한 동작의 알고리즘을 알아야 되는 옵션들 위주로 먼저 문서를 작성하므로

Index는 존재하지만 내용은 Empty 할 수 있다.
{{ site.content.br_small }}
# 2. Connections

Connect 관련 옵션들에 대해서 살펴본다.

해당 부분은, 워낙에 대중적으로 잘 알려져있고 공식 메뉴얼에서 명확하게 설명하므로

추후 필요시에 업데이트한다.
{{ site.content.br_small }}
# 3. Debugging

## 3.1 DebugConfigInfo

참고, [6. Proxy Plugin](Configure-OHS-12cR2#h-6-proxy-plugin)
{{ site.content.br_small }}
# 4. FileCaching

POST 데이터 전송 시 (보통 파일업로드),

FileSize가 2048Bytes를 초과하는 경우에 동작을 설정한다.

공식 메뉴얼에 잘 나와 있으나, 실제로 어떻게 동작하는지 Debug Log로 살펴본다.
{{ site.content.br_small }}
## 4.1 FileCaching OFF

Plugin 옵션을 다음과 같이 설정한다.

```mod_wl_ohs.conf
FileCaching OFF
WLTempDir <path>/WLTempDir
```
{{ site.content.br_small }}
* 100 Bytes 크기의 파일을 POST 전송

  ```
  Going to get the post data of size=296 clength=0
  Post data length: 296 (in memory)
  ```

  File(100 Bytes) + Unknown(196~7) 이 추가된다.

  File뿐만 아니라, POST Header 등과 같은 기타 크기가 추가되었을 것으로 추측을 할뿐이다.

  **2048 Bytes 보다 작아 `in memory` 로 Plugin 에서 처리한다.**
{{ site.content.br_small }}
* 1000 Bytes

  ```
  Going to get the post data of size=1197 clength=0
  Post data length: 1197 (in memory)



* 1851 Bytes

  ```
  Going to get the post data of size=2048 clength=0
  Post data length: 2048 (in memory)
  ```



* 1852 Bytes

  ```
  Going to get the post data of size=2049 clength=0
  FileCaching is turned OFF, postponing read of POST data
  Post data length: 2049 (not in memory)
  FileCache turned off reading and writing POST in chunks
  ```

  2048 Bytes를 초과하여, `not in memory` 로 처리된다.

  다만, Disk에 쓰기를 하지 않도록 `FileCaching OFF` 되어 있으므로, 

  Chunk Size인 8192 Bytes로 나누어서 전송한다. (postponing?)



## 4.2 FileCaching ON

Plugin 옵션을 다음과 같이 설정한다.

```mod_wl_ohs.conf
FileCaching ON
WLTempDir <path>/WLTempDir
```



* 1852 Bytes

  ```
  Going to get the post data of size=2049 clength=0
  getWLFilePath: Complete File name = [.../WLTempDir/_wl_proxy/_post_674040_0]
  Read 2049 of expected 2049 bytes of request body
  ```

  WLTempDir에 임시로 파일을 쓰기 후, 전송한다.

  `674040`은 확인 결과, httpd worker의 PID 이다.

  `_post_674040_0` 파일의 전송과 삭제 주기가 워낙 빨라 파일 확보를 할 수가 없다.



* 16384 Bytes

  ```
  Going to get the post data of size=16582 clength=0
  getWLFilePath: Complete File name = [.../WLTempDir/_wl_proxy/_post_674040_1]
  Read 16582 of expected 16582 bytes of request body
  ```

  문서에서 Chunk Size는 8192 bytes 이므로

  16384 Bytes POST 전송 시, 최소 2번 으로 나눌 것으로 예상했으나,

  그렇게 동작하지는 않은 것 같다.



* 10 MB

  ```
  Going to get the post data of size=10485952 clength=0
  getWLFilePath: Complete File name = [/sw/webtier/12cR2/domains/base_domain/config/fmwconfig/components/OHS/worker1/WLTempDir/_wl_proxy/_post_674040_3]
  Read 10485952 of expected 10485952 bytes of request body
  Post data length: 10485952 (not in memory)
  ```

  

* 128 MB

  ```
  Going to get the post data of size=102400193 clength=0
  getWLFilePath: Complete File name = [/sw/webtier/12cR2/domains/base_domain/config/fmwconfig/components/OHS/worker1/WLTempDir/_wl_proxy/_post_673765_0]
  Read 102400193 of expected 102400193 bytes of request body
  ```

  

FileCaching ON의 경우, WLTempDir에 임시 파일이 생성 된다는 로그만 확인이 된다.

혹은 [테스트 방식](https://www.theserverside.com/news/1365153/HttpClient-and-FileUpload)이 잘못되었을 수 있다.



# 5. Idemponent

멱등성; 항상 언제든지 결과가 같은 성질을 갖는다는 사전적인 의미가 있다.

WLIOTimeoutSecs 를 초과하는 작업 또는 READ_ERROR_FROM_SERVER 코드를 받게 될 경우,

실패한 작업으로 간주하여 다른 Alive instance로 Failover 할 수 있다.



## 5.1 Idempotent OFF

```mod_wl_ohs.conf
Idempotent OFF
WLIOTimeoutSecs 11
```



* Thread.sleep(11000) 실행

  ```
  *******Exception type [READ_TIMEOUT] (no read after 11 seconds) raised at line 284 of Reader.cpp
  caught exception in readStatus: READ_TIMEOUT [os error=0,  line 284 of Reader.cpp]: no read after 11 seconds at line 764
  PROTOCOL_ERROR: Backend Server not responding - isRecycled:0
  Marking 10.65.34.245:8002 as bad
  got exception in sendRequest phase: READ_TIMEOUT [os error=0,  line 284 of Reader.cpp]: no read after 11 seconds at line 579
  *NOT* failing over after sendRequest() exception: READ_TIMEOUT
  
  
  ```

  11초 동안 Backend Server가 Not responding 하다는 메시지와, 해당 인스턴스를 bad marked 하였다.

  

  ```
  ap_proxy: trying GET /testApp/sleep.jsp at backend host 10.65.34.245/8002; got exception 'READ_TIMEOUT [os error=0,  line 284 of Reader.cpp]: no read after 11 seconds'; state: reading status line or response headers from WLS (wrote? Y read? N); not failing over
  ```

  이후 Failover에 대해서는 Idempotent OFF 이므로 Ignored 되었다.



## 5.2 Idempotent ON

```mod_wl_ohs.conf
Idempotent OFF
WLIOTimeoutSecs 11
```



* Thread.sleep(11000) 실행

  ```
  attempt #0 out of a max of 5
  created a new connection to preferred server '10.65.34.245/8002' for '/testApp/sleep.jsp?cnt=11', Local port:28622
  Marking 10.65.34.245:8002 as bad
  Failing over after sendRequest() exception: READ_TIMEOUT as Idempotent is ON, method is idempotent
  no read after 11 seconds'; state: reading status line or response headers from WLS (wrote? Y read? N); failing over
  ```

  처음(0 of 5) 시도에 TIMEOUT으로 bad marked 및 Failover 동작이 확인됩니다.

  

  ```
  attempt #1 out of a max of 5
  general list: created a new connection to '10.65.34.245'/8003 for '/testApp/sleep.jsp?cnt=11', Local port:24870
  Marking 10.65.34.245:8003 as bad
  Failing over after sendRequest() exception: READ_TIMEOUT as Idempotent is ON, method is idempotent
  no read after 11 seconds'; state: reading status line or response headers from WLS (wrote? Y read? N); failing over
  ```

  다음(1 of 5) 시도도 마찬가지입니다.

  

  ```
  attempt #2 out of a max of 5
  general list: created a new connection to '10.65.34.245'/8002 for '/testApp/sleep.jsp?cnt=11', Local port:46456
  Marking 10.65.34.245:8002 as bad
  Failing over after sendRequest() exception: READ_TIMEOUT as Idempotent is ON, method is idempotent
  no read after 11 seconds'; state: reading status line or response headers from WLS (wrote? Y read? N); failing over
  ```

  세번째(2 of 5) 시도에서도 실패 및 Failover 를 합니다.

  여기서 유의해야 될 점이 있습니다.

  처음(0 of 5) 단계에서 bad marked 한 인스턴스 (8002)에 시도하고 있습니다.

  이는, bad skip time 10초 설정이 되어 있기 때문입니다.

  또한, 0 of 5 의 의미는 ConnectTimeoutSecs 설정과 관련이 있습니다.



# 6. MaxPostSize

```
MaxPostSize 1048576
```



* 1MB Post

  ```shell
  $ curl -v -X POST -F "file=@./1MB" http://wls.local:10100/testApp/
  HTTP/1.1 100 Continue
  ```



* 10MB Post

  ```shell
  $ curl -v -X POST -F "file=@./10MB" http://wls.local:10100/testApp/
  HTTP/1.1 413 Request Entity Too Large
  ```

  

