---
date: 2025-08-29 12:22:37 +0900
layout: post
title: "[WebTier/iPlanet] ERR_SSL_KEY_USAGE_INCOMPATIBLE On iPlanet"
tags: [WebTier, iPlanet, Browser, Certificate, SSL, HTTPS]
typora-root-url: ../..
---

# 1. Overview

iPlanet 7.0.9+ 의 admin-server에 Chrome Browser로 접근 시, ERR_SSL_KEY_USAGE_INCOMPATIBLE 발생

<br><br>


# 2. Descriptions

Chrome 으로 default url 인 `https://<ip>:8989` 접근 시, Browser page에는 `ERR_SSL_KEY_USAGE_INCOMPATIBLE` 가 기록되고

서버 Error에는 다음이 기록된다.

```
[23/Jul/2025:10:54:39] failure (801602): HTTP3068: Error receiving request from 10.73.131.136 (SSL_ERROR_CERTIFICATE_UNKNOWN_ALERT: Client had some unspecified issue with the certificate it received.)
```

<br>

`"..chrome.exe" --ignore-certificate-errors` 의 W/A 가 있으나 해결되지 않았다.

<br>

[certification matrix](https://www.oracle.com/technetwork/middleware/downloads/iplanet709certification-matrix-161591.xls)의 하위 Client Certification 에서 지원하는 Browser list가 있다.

```
	Client Certification							
	Installation Type	Version Supported	Supported Browsers			Exceptions and Additional Information		
	For latest browser support, refer to Oracle Software Web Browser Support Policy							
	Oracle iPlanet Web Server	7.0.9+	Internet Explorer 7.x			n/a		
	Oracle iPlanet Web Server	7.0.9+	Internet Explorer 8.x			n/a		
	Oracle iPlanet Web Server	7.0.9+	Firefox 3.5+			n/a		
	Oracle iPlanet Web Server	7.0.9+	Safari 4.x			No support for  Safari 4.x for using admin console.
```

<br>

Firefox 등의 Browser 를 통해 접근하면 문제가 해결된다.

<br>

또는

<br>

iPlanet admin-server 기본 인증서(Admin-Server-Cert)의 Key Usage Field가 Chrome browser에서 문제가 되는 것이므로, 이를 제거한 자체 서명 인증서를 적용하여 해결할 수 있다.

<br>

다음 명령어로 기본 인증서의 Key Usage field를 확인할 수 있다.

```sh
$ certutil -d dbm:<IPLANET_HOME>/admin-server/config -L -n "Admin-Server-Cert" -a | openssl x509 -noout -text
...
       X509v3 extensions:
           X509v3 Key Usage: critical
               Key Encipherment, Key Agreement
           X509v3 Extended Key Usage: critical
               TLS Web Server Authentication
...
```

<br>

다음 명령어로 자체 서명 인증서 생성

```sh
$ certutil -d dbm:<IPLANET_HOME>/admin-server/config -S -s "CN=<CN>" -n <alias for this cert> -x -t "CT,C,C" -v 120 -m 1234
$ certutil -d dbm:<IPLANET_HOME>/admin-server/config -R -s "CN=<CN>" -o mycert.req
$ certutil -d dbm:<IPLANET_HOME>/admin-server/config -C -c "<alias for this cert>" -i mycert.req -o mycert.crt -m 5678 -v 120 -t "u,u,u"
```

> dbm.. arg를 사용하지 않으면 sql 방식으로 cert9.db, key4.db 가 생성되어 엉뚱한 곳에 인증서와 키가 저장됨

<br>

다음 명령어로 위 명령어로 생성 도중 또는 후에 잘 저장되었는지 확인
```sh
$ certutil -d dbm:<IPLANET_HOME>/admin-server/config -L
$ certutil -d dbm:<IPLANET_HOME>/admin-server/config -K
```

<br>

생성한 인증서의 Key Usage가 없는 것을 확인

```sh
$ certutil -d dbm:<IPLANET_HOME>/admin-server/config -L -n "<alias for this cert>" -a | openssl x509 -noout -text
```

<br>

server.xml 에서 server-cert-nickname 를 `<alias for this cert>`로 적용

```sh
$ vi <IPLANET_HOME>/admin-server/config/server.xml
  ...
  <http-listener>
    <name>admin-ssl-port</name>
    <default-virtual-server-name>admin-server</default-virtual-server-name>
    <ssl>
      <!--<server-cert-nickname>Admin-Server-Cert</server-cert-nickname>-->
      <server-cert-nickname><alias for this cert></server-cert-nickname>
    </ssl>
```

<br>

재기동 이후 errors 로그에 계속 남지만 ERR_SSL_KEY_USAGE_INCOMPATIBLE 발생하지 않음

<br><br>


# 3. References

Chrome browser로 iPlanet Admin GUI Console 접근 시, ERR_SSL_KEY_USAGE_INCOMPATIBLE 발생 (Doc ID 3098714.1)

iPlanet Web Server is Unable to Find Imported Certificate Due to Incorrect Certificate DB Files Created By the Certutil Command ([Doc ID 2956871.1](https://mosemp.us.oracle.com/epmos/faces/ui/km/DocumentDisplay.jspx?id=2956871.1))

'HTTP3068: Error receiving request from HOSTNAME (SSL_ERROR_CERTIFICATE_UNKNOWN_ALERT: Client had some unspecified issue with the certificate it received.)' When Accessing iPlanet Admin Console with Chrome Browser (Doc ID 2790267.1)

https://docs.syteca.com/view/how-to-fix-the-err_ssl_key-usage-incompatible-erro

