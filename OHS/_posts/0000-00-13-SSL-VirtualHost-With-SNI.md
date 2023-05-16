---
date: 2023-05-17 08:16:07 +0900
layout: post
title: "[OHS/OSSL] SSL VirtualHost With SNI"
tags: [OracleHTTPServer, OHS, Apache, mod_ossl, HTTPS, SSL]
typora-root-url: ..
---

# 1. 개요

Oracle HTTP Server 12.2.1.4 에서 SNI 가 지원되는지, SSL VirtualHost 사용 시 유의할 점을 살펴보자.





# 2. SNI

SNI(Server Name Indication).

사용자의 HTTP Request 내에는 Host Header가 있으며, 여기에 사용자가 도달하려는 ServerName이 있다.

이것을 가지고, Web server는 Any Virtual Host section에 사용자를 할당할 수 있다.

HTTPS Request 는 암호화된 Packet을 추출해야, Host Header를 볼 수 있으나, Packet을 추출한다는 건, SSL Handshake 과정의 이후에 가능한 일이다.

SSL Virtual Host section에 사용자를 할당해야, SSL Handshake 과정이 이루어지는데, 그 전에 Host header를 알 수가 없으니, SSL Virtual Host section에 할당을 하지 못한다. ~~(말장난 같으나)~~

이를 위해, SSL Handshake 이전, 즉. Client Hello 와 관계 없이 SNI 라는 제공되는 Field 를 통해서 ServerName을 추출할 수 있다.

최근에는 이 값 또한 암호화 되어야 한다고 논의 중인 것으로 알고 있다.



어찌되었든, SNI 는 그런 종류의 Data이다.





# 3. SNI with OHS

OHS 에서는 SNI 기능을 공식적으로 지원하지 않는다.

mod_ossl 모듈에서 SNI 기능을 제공하지 않는다는 의미이다.



내부적으로는, 제한적으로 SNI 기능을 지원한다.

자세한 내용은, Internal Docs 이므로 공개할 수 없지만, NZ library (mod_ossl 구현체) 의 SSL 지갑인 NZ Wallet은 Single Listener (same IP:PORT) 에서는 모두 동일해야 한다는 것이다.

즉 시스템에 IP:Port가 모두 동일한 Virtual Host는 단일(Single) Listener 로 보는 것이며,

단일 Listner는 모두 공통된 NZ Wallet에 상속되는 것이다.

NZ Wallet 뿐만 아니라, SSL/TLS Protocol set 또한 단일 Listener 에 동일해야 한다.



NZ Library 으로 구현된 NZ Wallet (OWM; Oracle Wallet Manager) 에 의해 이러한 제약조건 또는 보안취약점을 해소하기 위한 기능상의 이유로 단일 Listner를 갖는 Virtaul Host 에서는 제한적으로 SNI를 지원하게 된 것이다.



Apache와 자주 비교하게 되는데, Apache의 SNI를 이용한 Name-Based Virtual Host가 OHS에서는 지원되지 않는 이유다.



> Apache는 Apache 2.22 에서 SNI 지원이 내장된 mod_ssl을 사용하여 Name-Based VH가 제공되고 있다.
>
> SNI는 단순히, SSL Client Hello 전에 알 수 있는 Data로 알고 있는데... NZ Library에서 SNI를 부분적으로 지원한다는거에 관련한 정확한 의미를 이해하지 못하기도 했다.





# 4. SSL Virtual Host with Apache

Apache 2.4.37 에서 SSL Virtual Host 개별로 SSLProtocol 지정 시 첫번째 VirtualHost Section의 SSLProtocol이 전역적으로 정의되는 것으로 [Bug](https://bz.apache.org/bugzilla/show_bug.cgi?id=55707)가 등록되었다.

Apache 의 SSL인 OpenSSL 에도 관련 [Bug](https://github.com/openssl/openssl/issues/4301)가 등록되었으나, Apache issue로 closed 되었다.



다음과 같은 코드가 Apache 에 구현되고, A와 B가 동일한 IP:Port로 Single Listener인 경우 TLS Protocol 1.2 가 전역 설정된다는 것이다.

```
<vhost A>
  SSLProtocol TLSv1.2
</vhost>

<vhost B>
  SSLProtocol TLSv1.3
</vhost>
```



해당 Bug는 Apache 2.4.42 에서 [Fixed](https://downloads.apache.org/httpd/CHANGES_2.4) 되었다.





# 5. SSL Virtual Host with OHS

Apache와 다른 SSL Library인 NZ 를 사용하는 OHS 에서는,

Single Listner 의 사용 시 SNI를 지원하지 않는 점으로 인해 SSL Virtual Host에서 Apache bug와 동일한 동작이 발생한다.



다만, NZ 구현에 따르면, 

즉. Wilcard 인증서를 보안에 취약한 것을 근거로 들며 SNI 를 지원하지 않는 OHS 에서는

다음과 같이 구성하는 것을 권장한다.



```
Listen A:2443
Listen B:3443


<VirtualHost A:2443>
  <IfModule ossl_module>
   SSLProtocol TLSv1.2
...


<VirtualHost B:3443>
  <IfModule ossl_module>
   SSLProtocol TLSv1.1
...
```



다른 A와 B Listner 를 구현하므로, NZ Wallet이 서로 다르게 적용될 수 있고 SSL/TLS Protocol set 또한 개별적으로 적용될 수 있다는 것이다.



그러므로, 서로 다른 SSLProtocol 를 적용 받게 된다.





# 5. References

**Support Status for Wildcard, SNI and SAN SSL Certificates for Oracle HTTP Server and Web Cache 11g/12c (Doc ID 2225494.1)**

[Using SAN Certificates with Oracle HTTP Server](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/12.2.1.4/administer-ohs/workwith.html#GUID-31D9DE0F-FBC0-4035-BCF4-3E08EDEE37BD)
