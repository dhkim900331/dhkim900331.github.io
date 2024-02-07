---
date: 2024-02-07 16:43:22 +0900
layout: post
title: "[WEB/OHS] How to capture SSL Hello Messages"
tags: [WEB, OHS, SSL, Handshake]
typora-root-url: ..
---

# 1. Overview

Oracle HTTP Server 12cR2 (12.2.1.4) 환경에서 Client와 Server의 SSL Handshake 과정 중에 Client/Server 의 Hello Messages 를 Capture 해본다.





# 2. Descriptions

SSL Handshake 과정 중에 Hello Messages 를 Capture 하여,

어떤 CipherSuites, 어떤 SSL Protocol version을 합의되었는지를 확인 해볼 수 있다.

Capture 된 데이터를 통해, Client와 Server간의 SSL Handshake가 실패하는 원인으로 서로 지원하는 메서드가 다를 경우 이를 알 수 있다.





## 2.1 Server가 지원하는 Cipher Suites, SSL Protocol

OHS의 ssl.conf 설정값을 통해 지원하려는 Cipher Suites, SSL Protocol 을 직관적으로 쉽게 알 수 있다.

```
# ssl.conf
<VirtualHost <IP>:<PORT>>
  <IfModule ossl_module>
   SSLProtocol TLSv1.2
   SSLCipherSuite TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256,TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384,TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA,TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256,TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384,TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA,TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA,TLS_RSA_WITH_AES_128_GCM_SHA256,TLS_RSA_WITH_AES_256_GCM_SHA384,TLS_RSA_WITH_AES_128_CBC_SHA256,TLS_RSA_WITH_AES_256_CBC_SHA256,SSL_RSA_WITH_AES_128_CBC_SHA,SSL_RSA_WITH_AES_256_CBC_SHA
   ...
```



기본 로그 파일(`error_log`)는 기동 시에 다음과 같은 Log가 수 회 반복되어 출력된다.

```
[ossl:info] [pid 1596506:tid 140063574840704] OHS:2183 NZ Trace message: Setting ciphers to ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:...

[ossl:info] [pid 1596506:tid 140063574840704] OHS:2183 NZ Trace message: Setting ciphers to ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA256:...
```



Child Process 의 mod_ossl 초기화 시마다 반복되어 출력되는 것으로 보여지며, 이를 통해 Server에서 제공하려는 Cipher Suites 를 알 수 있겠다.



또는, `nmap` 명령으로 확인하는 방법도 있다.

```bash
$ nmap --script ssl-enum-ciphers -p <SSL Port> <Host>
Starting Nmap 7.70 ( https://nmap.org ) at 2024-02-07 13:31 KST
Nmap scan report for *** (***)
Host is up (0.00024s latency).

PORT      STATE SERVICE
***/tcp open  unknown
| ssl-enum-ciphers:
|   TLSv1.2:
|     ciphers:
|       TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA (secp256r1) - A
|       TLS_RSA_WITH_AES_128_GCM_SHA256 (rsa 2048) - A
|       TLS_RSA_WITH_AES_256_GCM_SHA384 (rsa 2048) - A
|       TLS_RSA_WITH_AES_128_CBC_SHA256 (rsa 2048) - A
|       TLS_RSA_WITH_AES_256_CBC_SHA256 (rsa 2048) - A
|       TLS_RSA_WITH_AES_128_CBC_SHA (rsa 2048) - A
|       TLS_RSA_WITH_AES_256_CBC_SHA (rsa 2048) - A
|     compressors:
|       NULL
|     cipher preference: server
|_  least strength: A

Nmap done: 1 IP address (1 host up) scanned in 0.59 seconds
```







## 2.2 Client가 지원하는 Cipher Suites, SSL Protocol

OHS의 다음 옵션을 적용하고,

```
# ssl.conf
SSLTraceLogLevel ssl

# httpd.conf
LogLevel info
OraLogMode apache
```



HTTPS 요청이 있을 때, 기본 로그 파일(`error_log`)은 아래처럼 기록된다.

```
[ossl:info] [pid 1559019:tid 139777974175488] [client 10.65.39.5:54114] AH01964: Connection to child 208 established (server wls.local:20443)
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: nzos_SetCertChain
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: Setting cert chain:
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: nzos_Create_Ctx
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: nz ctx create status: 0
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: nzos_Handshake
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: entry
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: SSL_Info
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: Handshake before/accept initialization (TLSv12 protocol)
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: nzbioread:  read 11/11 bytes
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message:      0: 16030100 c7010000 c30303-- --------       |...........     |
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: nzbioread:  read 193/193 bytes
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message:      0: 3597a87d 0d56aa1b 56a49ad0 c58c2af5       |5..}.V..V.....*.|
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: SSL_Info
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: SSLv3 process tls extension (TLSv11 protocol)
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: SSL_Info
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: SSLv3 write server hello A (TLSv11 protocol)
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: SSL_Info
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: SSLv3 write certificate A (TLSv11 protocol)
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: SSL_Info
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: SSLv3 write certificate B (TLSv11 protocol)
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: SSL_Info
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: SSL3 status request A (TLSv11 protocol)
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: SSL_Info
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: SSLv3 write key exchange A (TLSv11 protocol)
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: SSL_Info
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: SSLv3 write server done A (TLSv11 protocol)
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: nzosp_bio_write
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: processed=1226, ret=0
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: nzbiowrite:  write 1226/1226 bytes
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message:      0: 16030200 51020000 4d030265 c3044ba8       |....Q...M..e..K.|
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message:    944: 856369b8 f1d6f248 50ec7125 3cfaf001       |.ci....HP.q.<...|
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: SSL_Info
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: SSLv3 flush data (TLSv11 protocol)
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: SSL_Info
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: SSLv3 read client certificate A (TLSv11 protocol)
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: nzbioread:  read 5/5 bytes
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message:      0: 15030300 02------ -------- --------       |.....           |
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: SSL_Info
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: error in SSLv3 read client key exchange A
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: SSL_Info
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: error in SSLv3 read client key exchange A
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: nzos_Handshake
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: Handshake returned failure code -1
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: nzos_Handshake
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: Handshake error(cb=0,rc=-1,rer=1,ser=336130315) - error:1408F10B:SSL routines:SSL3_GET_RECORD:wrong version number
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: nzos_Handshake
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: exit
[ossl:error] [pid 1559019:tid 139777974175488] [client 10.65.39.5:54114] OHS:2079 Client SSL handshake error, nzos_Handshake returned 29019(server wls.local:20443)
[ossl:error] [pid 1559019:tid 139777974175488] OHS:2171 NZ Library Error: Unknown error
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: SSL_Alert
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: write - warning - close notify
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: SSL_Alert
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: write - warning - close notify
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: nzos_DestroyCtx
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: entry
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2182 NZ Trace function: nzos_DestroyCtx
[ossl:info] [pid 1559019:tid 139777974175488] OHS:2183 NZ Trace message: exit
```



Client(openssl; TLSv1.2)가 Server(OHS; TLSv1.1) 에 Hello messages 를 교환하지만, Protocol이 성립되지 않아 `wrong version number` 메시지와 함께 실패한 샘플이다.



위 Log 구문에 대해 자세하게 정리된 내용이 없어 더 Deep 하게 분석하는것에는 무리가 있고,

언뜻 보아도 Hello messages 에 대한 자세한 내용이 나오지 않는다.





## 2.3 Fiddler 를 이용한 Messages debugging 방법

Fiddler Classic for Windows 설치 > Tools > Options > HTTPS 에서 `Capture HTTPS CONNECTs` 를 활성화.

HTTPS 호출 시, Fiddler 에서 Captured Data 의 TextView를 확인한다.



상단의 TextView는 Client의 Hello Message

```
A SSLv3-compatible ClientHello handshake was found. Fiddler extracted the parameters below.

Version: 3.3 (TLS/1.2)
Random: D1 F9 ED A1 71 99 C3 DB 3B 5F 07 BF 92 E6 AC 95 2F 0C F1 71 CD A7 01 D5 1C 43 9F 05 A1 F2 D5 1C
"Time": 2056-02-02 오후 11:36:01
SessionID: 0D 96 2E 63 A6 FB 50 DD 04 67 A5 35 79 D1 9D 53 08 A2 84 B2 45 D4 1D 8D 00 4F 8A 79 24 58 8C 5D
Extensions: 
	grease (0x2a2a)	empty
	supported_versions	grease [0xdada], Tls1.3, Tls1.2
	psk_key_exchange_modes	01 01
	renegotiation_info	00
	0xfe0d		00 00 01 00 01 18 00 20 CF 05 D4 3A D5 8E 18 61 7B FF 8B E5 26 54 1B 43 33 8C 03 AF 20 19 81 13 02 E9 AD AD CD 1B 63 1B 00 B0 4E 85 DA 73 5A 76 B6 62 21 A7 86 3A 30 74 70 95 C6 FD 36 74 EA 25 01 8D B8 B4 AF 84 57 39 BD CF 0C 7D 69 24 AA 43 BA AA 0B 0F C1 D8 E5 AD 16 F9 88 19 ED E0 5E 1B 2B 32 AE 9A 73 BC F1 CB 32 85 9B 2F 81 CC 50 E0 9C 84 6B 41 EB B5 4A 89 D1 B5 42 72 71 7D CF E0 A2 04 2D A6 24 A7 7B 04 4B 36 E8 3C 3B 82 D6 76 2D 47 B8 99 CE 83 01 7F 95 9B FE 5A D2 B2 61 59 AD 04 DF 5A CF 7A 15 4B EA 3A DD A6 51 65 59 2E 61 65 57 78 19 9F 7D A7 44 05 6E 4F 6C A2 61 CE 82 E6 8A A0 BA CE 52 E8 2A 60 CB 45 5A 64 4B 1C 54 1A B6 2A 52 11 51 60 73 91
	status_request	OCSP - Implicit Responder
	ALPN		h2, http/1.1
	0x4469		00 03 02 68 32
	key_share	00 29 2A 2A 00 01 00 00 1D 00 20 DD 5E D8 0F 1F 89 FC 89 AC 09 A1 49 0E EF 9F B5 AC B5 96 23 C3 7D 94 47 99 57 54 B1 0A DE 76 1D
	supported_groups	grease [0x2a2a], x25519 [0x1d], secp256r1 [0x17], secp384r1 [0x18]
	SessionTicket	empty
	ec_point_formats	uncompressed [0x0]
	extended_master_secret	empty
	signature_algs	ecdsa_secp256r1_sha256, rsa_pss_rsae_sha256, rsa_pkcs1_sha256, ecdsa_secp384r1_sha384, rsa_pss_rsae_sha384, rsa_pkcs1_sha384, rsa_pss_rsae_sha512, rsa_pkcs1_sha512
	SignedCertTimestamp (RFC6962)	empty
	0x001b		02 00 02
	server_name	***
	grease (0xbaba)	00
Ciphers: 
	[FAFA]	Unrecognized cipher - See https://www.iana.org/assignments/tls-parameters/
	[1301]	TLS_AES_128_GCM_SHA256
	[1302]	TLS_AES_256_GCM_SHA384
	[1303]	TLS_CHACHA20_POLY1305_SHA256
	[C02B]	TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
	[C02F]	TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
	[C02C]	TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
	[C030]	TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
	[CCA9]	TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256
	[CCA8]	TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
	[C013]	TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA
	[C014]	TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA
	[009C]	TLS_RSA_WITH_AES_128_GCM_SHA256
	[009D]	TLS_RSA_WITH_AES_256_GCM_SHA384
	[002F]	TLS_RSA_WITH_AES_128_CBC_SHA
	[0035]	TLS_RSA_WITH_AES_256_CBC_SHA

Compression: 
	[00]	NO_COMPRESSION
```



하단의 TextView는 Server의 Hello Message 이다.

```
This is a CONNECT tunnel, through which encrypted HTTPS traffic flows.
To view the encrypted sessions inside this tunnel, enable the Tools > Options > HTTPS > Decrypt HTTPS traffic option.

A SSLv3-compatible ServerHello handshake was found. Fiddler extracted the parameters below.

Version: 3.3 (TLS/1.2)
SessionID:	EC 26 8E AC 8A 5C A0 CD C0 68 B6 E4 00 31 FD 36 4B 2A F1 AA AE B2 A1 E0 4C 78 63 2A 16 4F 9F C9
Random:		65 C3 08 EF 89 E6 8B DB 31 EE F5 1B F7 55 B3 55 35 F3 09 F8 81 B8 1D D2 1A A1 6B C7 D3 4C EE A7
Cipher:		TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 [0xC02F]
CompressionSuite:	NO_COMPRESSION [0x00]
Extensions:
		renegotiation_info	00
```



Client가 제시한 값들 중에서, Server가 선택한 값들이 Response(TextView data)로 확인된다.
