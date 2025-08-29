---
date: 2025-04-11 00:21:07 +0900
layout: post
title: "[WebTier/OHS] All of OHS instances have been shutdown due to an expired certificate"
tags: [WebTier, OHS, SSL, mod_dms]
typora-root-url: ..
---

# 1. Overview

특정 시점에 OHS 인스턴스가 모두 종료되었다.

당시 특이점은, 관리자는 특별한 작업을 하지 않았다는 것이고 Default wallet 인증서가 만료되었다는 것이다.

인증서가 만료되면 OHS 인스턴스가 종료될 수 있는것인가?


<br><br>


# 2. Descriptions

고객은 OHS SSL 서비스가 업무에 필요치 않아 활용하고 있지 않았다.

다만, OHS 인스턴스의 Health check를 하는 admin.conf 구성 요소 때문에 기본적으로 SSL 기능이 활성화 되어 있다.

> OHS 12.2.1.4 의 특정 minor release 부터 HTTP -> HTTPS 로 변경된 것으로 보인다.

<br>

admin.conf에는 mod_dms 모듈이 OHS Instance와 Nodemanager간의 Health check에 응답하는 역할을 수행하는데,

이때 SSL Protocol을 사용한다.

<br>

처음 설명대로 고객은 SSL 서비스가 필요 없지만, admin.conf에서 Default Wallet을 사용하고 있으며,

Wallet에 포함된 기본 인증서가 만료가 되는 시점이 마침 도래했다.

<br>

이후 SSL Handshake failure due to the expired certificate 이슈로 인해, Nodemanager는 해당 OHS instance가 응답을 제때 하지 못한다고 인식.

Nodemanager의 기본 동작인, OHS instance를 restart 한다.

<br>

이는 쉽게 예상할 수 없지만, 운영 서버에서 만료될 수 있는 기본 인증서를 방치 및 관리하지 못한 사용자의 책임에 있다.

<br>

이러한 동작은 다음의 히스토리가 있다.

```
NM과 AH간 통신이 SSL로 변경되었습니다.
OHS 12.2.1.3은 BP July 2019부터 -> 이 경우 별도 SSL 구성 필요
OHS 12.2.1.4는 default로 구성되어 있습니다.
```

<br><br>

## 2.1 Verificiation

nodemanager.out 로그 파일에 인증서가 만료되어 SSL Handshake Exception으로 통신하지 못하는 worker 가 감지된다.

그리고, 그 workerd의 httpd.pid 파일에 의거하여 종료를 시도한다.

```
javax.net.ssl.SSLHandshakeException: java.security.cert.CertificateExpiredException: NotAfter: Sat Nov 17 11:43:08 KST 2029
        at sun.security.ssl.Alert.createSSLException(Alert.java:131)
        at sun.security.ssl.TransportContext.fatal(TransportContext.java:377)
        at sun.security.ssl.TransportContext.fatal(TransportContext.java:320)
        at sun.security.ssl.TransportContext.fatal(TransportContext.java:315)
        at sun.security.ssl.CertificateMessage$T12CertificateConsumer.checkServerCerts(CertificateMessage.java:652)
        at sun.security.ssl.CertificateMessage$T12CertificateConsumer.onCertificate(CertificateMessage.java:471)
        at sun.security.ssl.CertificateMessage$T12CertificateConsumer.consume(CertificateMessage.java:367)
        at sun.security.ssl.SSLHandshake.consume(SSLHandshake.java:376)
        at sun.security.ssl.HandshakeContext.dispatch(HandshakeContext.java:479)
        at sun.security.ssl.HandshakeContext.dispatch(HandshakeContext.java:457)
        at sun.security.ssl.TransportContext.dispatch(TransportContext.java:200)
        at sun.security.ssl.SSLTransport.decode(SSLTransport.java:155)
        at sun.security.ssl.SSLSocketImpl.decode(SSLSocketImpl.java:1320)
        at sun.security.ssl.SSLSocketImpl.readHandshakeRecord(SSLSocketImpl.java:1233)
        at sun.security.ssl.SSLSocketImpl.startHandshake(SSLSocketImpl.java:417)
        at sun.security.ssl.SSLSocketImpl.startHandshake(SSLSocketImpl.java:389)
        at sun.net.www.protocol.https.HttpsClient.afterConnect(HttpsClient.java:558)
        at sun.net.www.protocol.https.AbstractDelegateHttpsURLConnection.connect(AbstractDelegateHttpsURLConnection.java:201)
        at sun.net.www.protocol.https.HttpsURLConnectionImpl.connect(HttpsURLConnectionImpl.java:167)
        at oracle.ohs.plugin.nodemanager.OhsAdminRequest.run(Unknown Source)
        at oracle.ohs.plugin.nodemanager.OhsProcessHandler.isResponding(Unknown Source)
        at oracle.ohs.plugin.nodemanager.OhsProcessManagementPlugin$ProcessImpl.isAlive(Unknown Source)
        at weblogic.nodemanager.server.DecoratedSystemComponentManager$DecoratedProcess.isAlive(DecoratedSystemComponentManager.java:150)
        at weblogic.nodemanager.server.ServerMonitor.runMonitor(ServerMonitor.java:527)
        at weblogic.nodemanager.server.ServerMonitor.run(ServerMonitor.java:487)
        at java.lang.Thread.run(Thread.java:750)
Caused by: java.security.cert.CertificateExpiredException: NotAfter: Sat Nov 17 11:43:08 KST 2029
        at sun.security.x509.CertificateValidity.valid(CertificateValidity.java:277)
        at sun.security.x509.X509CertImpl.checkValidity(X509CertImpl.java:671)
        at sun.security.x509.X509CertImpl.checkValidity(X509CertImpl.java:644)
        at oracle.security.pki.ssl.OracleSSLX509CertTrustManagerImpl.a(Unknown Source)
        at oracle.security.pki.ssl.OracleSSLX509CertTrustManagerImpl.b(Unknown Source)
        at oracle.security.pki.ssl.OracleSSLX509TrustManager14.checkServerTrusted(Unknown Source)
        at sun.security.ssl.AbstractTrustManagerWrapper.checkServerTrusted(SSLContextImpl.java:1248)
        at sun.security.ssl.CertificateMessage$T12CertificateConsumer.checkServerCerts(CertificateMessage.java:636)
        ... 21 more
<May 8, 2035 3:30:00 PM KST> <INFO> <saml_domain> <worker1> <The server 'worker1' with process id 330792 is no longer alive; waiting for the process to die.>
May 08, 2035 3:31:00 PM oracle.ohs.plugin.nodemanager.OhsProcessManagementPlugin$ProcessImpl waitForProcessDeath
WARNING: Server worker1 is in an inconsistent state -- the process could not be stopped or killed. This issue must be manually resolved
javax.net.ssl.SSLHandshakeException: java.security.cert.CertificateExpiredException: NotAfter: Sat Nov 17 11:43:08 KST 2029
        at sun.security.ssl.Alert.createSSLException(Alert.java:131)
        at sun.security.ssl.TransportContext.fatal(TransportContext.java:377)
        at sun.security.ssl.TransportContext.fatal(TransportContext.java:320)
        at sun.security.ssl.TransportContext.fatal(TransportContext.java:315)
        at sun.security.ssl.CertificateMessage$T12CertificateConsumer.checkServerCerts(CertificateMessage.java:652)
        at sun.security.ssl.CertificateMessage$T12CertificateConsumer.onCertificate(CertificateMessage.java:471)
        at sun.security.ssl.CertificateMessage$T12CertificateConsumer.consume(CertificateMessage.java:367)
        at sun.security.ssl.SSLHandshake.consume(SSLHandshake.java:376)
        at sun.security.ssl.HandshakeContext.dispatch(HandshakeContext.java:479)
        at sun.security.ssl.HandshakeContext.dispatch(HandshakeContext.java:457)
        at sun.security.ssl.TransportContext.dispatch(TransportContext.java:200)
        at sun.security.ssl.SSLTransport.decode(SSLTransport.java:155)
        at sun.security.ssl.SSLSocketImpl.decode(SSLSocketImpl.java:1320)
        at sun.security.ssl.SSLSocketImpl.readHandshakeRecord(SSLSocketImpl.java:1233)
        at sun.security.ssl.SSLSocketImpl.startHandshake(SSLSocketImpl.java:417)
        at sun.security.ssl.SSLSocketImpl.startHandshake(SSLSocketImpl.java:389)
        at sun.net.www.protocol.https.HttpsClient.afterConnect(HttpsClient.java:558)
        at sun.net.www.protocol.https.AbstractDelegateHttpsURLConnection.connect(AbstractDelegateHttpsURLConnection.java:201)
        at sun.net.www.protocol.https.HttpsURLConnectionImpl.connect(HttpsURLConnectionImpl.java:167)
        at oracle.ohs.plugin.nodemanager.OhsAdminRequest.run(Unknown Source)
        at oracle.ohs.plugin.nodemanager.OhsProcessHandler.isResponding(Unknown Source)
        at oracle.ohs.plugin.nodemanager.OhsProcessManagementPlugin$ProcessImpl.isAlive(Unknown Source)
        at weblogic.nodemanager.server.DecoratedSystemComponentManager$DecoratedProcess.isAlive(DecoratedSystemComponentManager.java:150)
        at weblogic.nodemanager.server.ServerMonitor.log(ServerMonitor.java:765)
        at weblogic.nodemanager.server.ServerMonitor.log(ServerMonitor.java:777)
        at weblogic.nodemanager.server.ServerMonitor.fine(ServerMonitor.java:787)
        at weblogic.nodemanager.server.ServerMonitor.runMonitor(ServerMonitor.java:539)
        at weblogic.nodemanager.server.ServerMonitor.run(ServerMonitor.java:487)
        at java.lang.Thread.run(Thread.java:750)
Caused by: java.security.cert.CertificateExpiredException: NotAfter: Sat Nov 17 11:43:08 KST 2029
        at sun.security.x509.CertificateValidity.valid(CertificateValidity.java:277)
        at sun.security.x509.X509CertImpl.checkValidity(X509CertImpl.java:671)
        at sun.security.x509.X509CertImpl.checkValidity(X509CertImpl.java:644)
        at oracle.security.pki.ssl.OracleSSLX509CertTrustManagerImpl.a(Unknown Source)
        at oracle.security.pki.ssl.OracleSSLX509CertTrustManagerImpl.b(Unknown Source)
        at oracle.security.pki.ssl.OracleSSLX509TrustManager14.checkServerTrusted(Unknown Source)
        at sun.security.ssl.AbstractTrustManagerWrapper.checkServerTrusted(SSLContextImpl.java:1248)
        at sun.security.ssl.CertificateMessage$T12CertificateConsumer.checkServerCerts(CertificateMessage.java:636)
        ... 24 more
```

<br>

오래 지나지 않아, shutdown이 강제로 수행된 worker의 재시작을 시도하지만, 만료된 인증서를 허용하지 않은 worker 쪽의 구성상의 오류로 완료되지 않는다.

```
<May 8, 2035 3:31:00 PM KST> <INFO> <saml_domain> <worker1> <Server failed so attempting to restart (restart count = 1)>
May 08, 2035 3:31:00 PM oracle.ohs.plugin.nodemanager.OhsProcessManagementPlugin$ProcessImpl start
INFO: Starting server worker1
May 08, 2035 3:31:00 PM oracle.ohs.plugin.nodemanager.OhsRunCommand execute
INFO: Running /sw/webtier/12cR2/wlserver/../ohs/bin/launch httpd -DOHS_MPM_EVENT -d /sw/webtier/12cR2/domains/saml_domain/config/fmwconfig/components/OHS/instances/worker1 -k stop -f /sw/webtier/12cR2/domains/saml_domain/config/fmwconfig/components/OHS/instances/worker1/httpd.conf
...

INFO: /sw/webtier/12cR2/wlserver/../ohs/bin/launch httpd -DOHS_MPM_EVENT -d /sw/webtier/12cR2/domains/saml_domain/config/fmwconfig/components/OHS/instances/worker1 -k stop -f /sw/webtier/12cR2/domains/saml_domain/config/fmwconfig/components/OHS/instances/worker1/httpd.conf: exit status = 0
...

INFO: /sw/webtier/12cR2/wlserver/../ohs/bin/launch httpd -DOHS_MPM_EVENT -d /sw/webtier/12cR2/domains/saml_domain/config/fmwconfig/components/OHS/instances/worker1 -k start -f /sw/webtier/12cR2/domains/saml_domain/config/fmwconfig/components/OHS/instances/worker1/httpd.conf: exit status = 0
...

<May 8, 2035 3:31:02 PM KST> <SEVERE> <saml_domain> <worker1> <Unexpected error while monitoring server>
java.io.IOException: Failed to start the server worker1
Check log file /sw/webtier/12cR2/domains/saml_domain/system_components/OHS/ohs_nm.log
Check log file /sw/webtier/12cR2/domains/saml_domain/servers/worker1/logs/worker1.log
        at oracle.ohs.plugin.nodemanager.OhsProcessManagementPlugin$ProcessImpl.buildIoException(Unknown Source)
        at oracle.ohs.plugin.nodemanager.OhsProcessManagementPlugin$ProcessImpl.start(Unknown Source)
        at weblogic.nodemanager.server.DecoratedSystemComponentManager$DecoratedProcess.start(DecoratedSystemComponentManager.java:129)
        at weblogic.nodemanager.server.ServerMonitor.startProcess(ServerMonitor.java:664)
        at weblogic.nodemanager.server.ServerMonitor.runMonitor(ServerMonitor.java:607)
        at weblogic.nodemanager.server.ServerMonitor.run(ServerMonitor.java:487)
        at java.lang.Thread.run(Thread.java:750)

May 08, 2035 3:31:02 PM oracle.ohs.plugin.nodemanager.OhsProcessManagementPlugin$SystemComponentManagerImpl log
SEVERE: Unexpected error while monitoring server
java.io.IOException: Failed to start the server worker1
Check log file /sw/webtier/12cR2/domains/saml_domain/system_components/OHS/ohs_nm.log
Check log file /sw/webtier/12cR2/domains/saml_domain/servers/worker1/logs/worker1.log
        at oracle.ohs.plugin.nodemanager.OhsProcessManagementPlugin$ProcessImpl.buildIoException(Unknown Source)
        at oracle.ohs.plugin.nodemanager.OhsProcessManagementPlugin$ProcessImpl.start(Unknown Source)
        at weblogic.nodemanager.server.DecoratedSystemComponentManager$DecoratedProcess.start(DecoratedSystemComponentManager.java:129)
        at weblogic.nodemanager.server.ServerMonitor.startProcess(ServerMonitor.java:664)
        at weblogic.nodemanager.server.ServerMonitor.runMonitor(ServerMonitor.java:607)
        at weblogic.nodemanager.server.ServerMonitor.run(ServerMonitor.java:487)
        at java.lang.Thread.run(Thread.java:750)
```

<br>

admin.conf에 `SSLEngine off` 시에 다음의 로그가 nodemanager에 기록되지만 인증서 만료로 인한 이슈는 해결될 수 있다.

```
WARNING: SSL is not enabled for the admin port of worker1. Thus, the connection between NodeManager and the admin port of worker1 is not secure. SSL must be enabled for this connection. For more information on how to enable SSL for this connection, refer to OHS documentation
```


<br><br>

<br>

# 3. References

<br>

