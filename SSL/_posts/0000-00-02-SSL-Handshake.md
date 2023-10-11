---
date: 2023-10-11 13:11:07 +0900
layout: post
title: "[SSL] SSL Handshake"
tags: [SSL, Handshake]
typora-root-url: ..
---

# 1. Overview

SSL/TSL Handshake에 대하여 간단히 살펴본다, 이미 더 자세하게 설명된 자료들이 구글링 되지만 여기서는 오로지 비대칭키, 대칭키가 왜 같이 사용되는지, Handshake 안에서 일어나는 순서적인 개념을 되짚는다.

<br><br>

# 2. What Is Questions?

일반적으로 비대칭키의 일부분만 요약하면, 누출되면 안되는 개인키와 공개되어도 되는 공개키의 조합으로 만들어지는 암호이며, 상대방이 나의 공개키로 보낼 Data를 암호화하여 보내면 나의 개인키로 복호화할 수 있다는 이상적인 방법이다.

장단점은, CPU Resource가 많이 필요하다는 것이며, 개인키가 누출되면 매우 위험하다는 것이다.



또, 대칭키의 경우에는 서로가 단 하나의 암호를 공유하고, 이 암호로 암/복호화를 한다는 것이다.

장단점은, 가벼우나 매우 위험하다는 것이다.



SSL/TLS에서는 비대칭,대칭의 장점만을(?) 차용한 보안 통신 방식이다.

구체적으로 알려면 [RFC-5246](https://datatracker.ietf.org/doc/html/rfc5246)을 참고해야 하고, RFC을 통해서는 생각보다 구체적으로 이해를 얻기 쉽지 않아 구글링 또한 병행해야 하는데, 여기 글에서는 대략적으로 핵심 흐름만 이해하도록 한다.





# 3. SSL/TLS Handshake flow

## (1) ClientHello

Client가 Server에 보내는 ClientHello 메시지는 다음과 같다.

```
struct {
    ProtocolVersion client_version;
    Random random;
    SessionID session_id;
    CipherSuite cipher_suites<2..2^16-2>;
    CompressionMethod compression_methods<1..2^8-1>;
    select (extensions_present) {
        case false:
            struct {};
        case true:
            Extension extensions<0..2^16-1>;
    };
} ClientHello;
```



 - ProtocolVersion : 클라이언트가 지원할 수 있는 가장 최신의 TLS 프로토콜 버전
 - CipherSuite : 클라이언트가 선호하고, 지원할 수 있는 알고리즘 리스트 (가장 좋아하는 것부터 순서대로 정렬되어)
 - CompressionMethod : 클라이언트가 지원하는 압축 알고리즘 목록이 포함되고, 클라이언트 기본 설정에 따라 정렬된다.
 - Random 은 다음의 구조체를 갖는다.
    
     ```
     struct {
  uint32 gmt_unix_time;
  opaque random_bytes[28];
    } Random;
  ```
  
  - gmt_unix_time : 현재 일자 및 시각
  - random_bytes : Secure Random Generator에 의해 생성된 28바이트 길이의 데이터
  





## (2) ServerHello

Server가 Client에 보내는 ServerHello 메시지는 다음과 같다.

```
struct {
    ProtocolVersion server_version;
    Random random;
    SessionID session_id;
    CipherSuite cipher_suite;
    CompressionMethod compression_method;
    select (extensions_present) {
        case false:
            struct {};
        case true:
            Extension extensions<0..2^16-1>;
    };
} ServerHello;
```

 - 기본적으로 ClientHello와 같으며, Client가 제공한 값에서 선택하여 채워넣는다.





## (3) Server Certificate

ServerHello Message와 함께 Server Certificate(인증서)를 Client에 보낸다.

Client는 Server의 인증서를 통해, Server를 식별한다.

반대로 Server의 요구에 따라, Client의 인증서가 Server에 보내져 식별될 수 있다. (Optional)
이는 2-way SSL/TLS Handshake의 일부 과정이다.





## (4) Pre-Master Secret Key

Client측에서는 ClientHello.Random와 ServerHello.Random 그리고 Client측에서 제공되는 임의의 값으로 Pre-Master Secret Key를 만든다.
여기서, Client측에서 제공되는 임의의 값은 구체적으로 어떤 Struct/Field/Type인지 확인되지 않는다.

또한 이렇게 만들어진 Pre-Master Secret Key는 Server의 인증서에서 확인된 공개키로 암호화화여 Server로 보낸다.
Server는 자신의 개인키로 이를 복호화함으로 써, 서로가 동일한 Pre-Master Secret Key를 가지게 된다.





## (5) Master Secret Key

Client/Server가 모두 알고 있는
 - Pre-Master Secret Key,
 - ClientHello.Random,
 - ServerHello.Random
값을 가지고 각자 계산하여 48 bytes의 [Master Secret Key](https://datatracker.ietf.org/doc/html/rfc5246#section-8.1)를 만든다.
교환할 필요 없이 정확한 값이 계산된다.





## (6) Session Key

Client와 Server는 PRF 함수라는 것을 이용하여
 - Master Secret Key,
 - ClientHello.Random,
 - ServerHello.Random
값을 가지고 [Session Key](https://datatracker.ietf.org/doc/html/rfc5246#section-6.3)를 만든다.
서로가 교환할 필요가 없다.



이로써, Client와 Server는 서로 SSL/TLS 통신에서 주고받는 Data를 암/복호화할 ***대칭키***로 Session Key를 가지게 되었다.

***대칭키***는 누출되지 않도록 각자에서 계산되었으며, 항상 새로운 통신이 게시될 때마다 다르므로 과거 시점과 분리된다.



# 4. References

[RFC-5246](https://datatracker.ietf.org/doc/html/rfc5246)

[SSL Handshake의 Flow](https://datatracker.ietf.org/doc/html/rfc5246#section-7.4.1)

[Master Secret Key](https://datatracker.ietf.org/doc/html/rfc5246#section-8.1)

[Session Key](https://datatracker.ietf.org/doc/html/rfc5246#section-6.3)
