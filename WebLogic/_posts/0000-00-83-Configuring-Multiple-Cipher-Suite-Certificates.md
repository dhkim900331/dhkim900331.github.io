---
date: 2024-06-25 16:09:26 +0900
layout: post
title: "[WebLogic/SSL] Configuring Multiple Cipher Suite Certificates"
tags: [Middleware, WebLogic, SSL, TLS, Keystore, cipher, suite, JSSE]
typora-root-url: ..
---

# 1. Overview
WebLogic Server 14.1 (14cR1) 및 JDK 1.8 환경에서

하나의 단일 HTTPS Port에 다양한 Cipher Suite Certificates 구성 방법을 살펴본다.

{{ site.content.br_big }}

# 2. Descriptions
결론적으로, WLS 에서는 단일 HTTPS Port에 단 하나의 Keystore Alias만 설정할 수 있기 때문에

다양한 Cipher Suite의 Client와 Handshake 할 수 없다.



WLS 에서 SSL 구성 단계 과정 중, Keystore 에 있는 인증서 중 단 하나의 Alias만 Load 하도록 설정한다.

이로 인해, 단일 HTTPS Port 별로 1개의 Certificate만 Load 되고,

Load 된 Certificate 가 어떤 Cipher suite를 사용하는지에 따라 SSL Handshake 대상이 되는 Client가 정해진다.



JSSE(Java Secure Socket Extension) API로 구현하는 Java socket program 을 통해서는

KeyManager package에서 여러 Keystore, Alias를 하나의 HTTPS Port에서 사용 가능하다.



위 두 내용을 직접 테스트를 통해 검증한다.



> WLS 또한 JSSE 를 구현하지만, 단일 Alias 선택이 가능한 점 때문에 차이가 발생한다.





## 2.1 WLS 에서 SSL 구성

### 2.1.1 인증서 생성

[How-to-make-a-self-signed-certificate]({{ site.url }}/ssl/How-to-make-a-self-signed-certificate) 을 참고하여 인증서를 생성한다.

아래와 같이, keystore.jks 내에 RSA 및 ECDSA cipher suite 인증서 2개가 포함되어 있다.

>  (.p12 파일은 여러 인증서를 하나에 집약할 수 있는 PKCS12 표준 포맷이며, 권장되나 여기 포스트에서는 사용하지 않을 것이다.)

```
$ ls
ec_cert.cer  keystore.jks  keystore.jks.p12  rsa_cert.cer  trust.jks
```





### 2.1.2 생성한 JKS를 WLS 도메인에 등록

* {Server} - Configuration
  * General - **SSL Listen Port Enabled** and **SSL Listen Port**
  * Keystore : keystore.jks 와 trust.jks 를 등록한다.
  * SSL : Private Key Alias 는 1개만 등록이 가능하기 때문에, **여기서 단일 HTTPS Port에 단 하나의 Certificate만 사용 가능한점이 확인 된다.** 진행을 위해 keystore.jks 에 등록된 "key-rsa" 를 입력한다.





### 2.1.3 SSL Debugging Log

* {Server} - Logging - General 에서 Standard out 의 Log level을 Debug
* {Server} - Debug 에서 weblogic.security.ssl 을 Enabled



`nmap` 또는 `openssl` 등으로 SSL Handshake를 요청하면 WLS Debug log가 아래의 내용을 포함한다.

```
# 일반적으로 기록되는 Logs
<Debug> <SecuritySSL> <BEA-000000> <[Thread[weblogic.socket.ServerListenThread,5,Pooled Threads]]weblogic.security.SSL.jsseadapter: SSLCONTEXT: Expected SSLContext service protocol: TLS>
<Debug> <SecuritySSL> <BEA-000000> <[Thread[weblogic.socket.ServerListenThread,5,Pooled Threads]]weblogic.security.SSL.jsseadapter: SSLCONTEXT: Got SSLContext, protocol=TLS, provider=SunJSSE>
<Debug> <SecuritySSL> <BEA-000000> <Using TLSv1.2 as the default minimum TLS protocol.>
<Debug> <SecuritySSL> <BEA-000000> <supportedProtocolVersions=TLSv1.3,TLSv1.2,TLSv1.1,TLSv1,SSLv3,SSLv2Hello>
<Debug> <SecuritySSL> <BEA-000000> <given minimumProtocolVersion=TLSv1.2>

# JDK 수준.
<Debug> <SecuritySSL> <BEA-000000> <[Thread[weblogic.socket.ServerListenThread,5,Pooled Threads]]weblogic.security.SSL.jsseadapter: SSLENGINE: SSLEngine.setEnabledCipherSuites(String[]): value=TLS_AES_256_GCM_SHA384,TLS_AES_128_GCM_SHA256,...,TLS_EMPTY_RENEGOTIATION_INFO_SCSV.>
```



JDK 수준이라고 설명하는 log는 WLS 상위 JDK 에서 허용하는 Cipher suites 를 WLS 에서도 지원된다는 것을 보여준다.

[JDK 1.8 에서 지원하는 Cipher Suites 목록](https://docs.oracle.com/javase/8/docs/technotes/guides/security/SunProviders.html#SunJSSEProvider) 에서 WLS 자체적으로 취약점으로 제외한 것을 빼면 모두 언급되어 있다.



> 참고로, nmap 과 openssl 은 Target Server에서 지원하는 Cipher Suites 를 조회하는데 유용한 도구임에 틀림 없지만, Third party tool 의 결과이므로 온전히 신뢰할 수 없다. 직접 WLS의 Debugging Log를 통해 어떤 Cipher Suites 가 지원되는지 확인하는 것이 올바르다.



> WLS 수준에서 지원되는 Cipher Suites 목록을 조정하려면 WLST를 이용해 수정할 수 있다.
>
> ```python
> connect('username', 'password', 'ADM_URL')
> edit()
> startEdit()
> 
> # AdminServer의 SSL 설정을 가져옴
> server = cmo.lookupServer('{Server}')
> ssl = server.getSSL()
> 
> # 설정할 cipher suite 목록
> ciphers = [
>     'TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256',
>     'TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256',
>     'TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384',
>     'TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384',
>     'TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256'
> ]
> 
> # 설정 적용
> ssl.setCiphersuites(ciphers)
> 
> # 설정 저장 및 활성화
> save()
> activate()
> disconnect()
> exit()
> ```





### 2.1.4 Cipher Suites That Available

다음의 Java code로 WLS 에서 지원가능한 Cipher Suites를 받아올 수 있다.

```sh
cat << EOF > SSLClient.java
import javax.net.ssl.*;
import java.io.*;
import java.net.Socket;
import java.util.Arrays;

public class SSLClient {
    public static void main(String[] args) throws Exception {
        String host = "{HOSTNAME}";
        int port = {PORT};

        // Create a trust manager that does not validate certificate chains
        TrustManager[] trustAllCerts = new TrustManager[]{
            new X509TrustManager() {
                public java.security.cert.X509Certificate[] getAcceptedIssuers() {
                    return null;
                }

                public void checkClientTrusted(java.security.cert.X509Certificate[] certs, String authType) {
                }

                public void checkServerTrusted(java.security.cert.X509Certificate[] certs, String authType) {
                }
            }
        };

        // Install the all-trusting trust manager
        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(null, trustAllCerts, new java.security.SecureRandom());

        // Create socket factory with the all-trusting manager
        SSLSocketFactory factory = sslContext.getSocketFactory();
        SSLSocket socket = (SSLSocket) factory.createSocket(host, port);

        socket.startHandshake();

        System.out.println("Enabled Cipher Suites:");
        for (String cipherSuite : socket.getEnabledCipherSuites()) {
            System.out.println(cipherSuite);
        }

        System.out.println("Supported Cipher Suites:");
        for (String cipherSuite : socket.getSupportedCipherSuites()) {
            System.out.println(cipherSuite);
        }

        socket.close();
    }
}
EOF
javac -cp . SSLClient.java
java -cp . SSLClient
```



확인해보면, 결과는 `2.1.3 SSL Debugging Log` 와 같다.

이 Cipher Suites 목록에는 RSA 및 ECDSA 등등 다양한 서명 알고리즘이 포함되어 있다.





### 2.1.5 SSL Handshake to WLS

앞서 우리는 RSA 및 ECDSA 서명 알고리즘을 사용한 두 개의 인증서를 하나의 Keystore file로 저장했다.

물론 WLS 에서는 하나의 Private Key Alias 만을 허용하고, 이때문에 RSA 인증서만 Load 해둔 상태다.



이 상황에서, 아래 Java code를 이용하여 RSA 와 ECDSA 인증서를 사용하는 Client가 SSL Handshake를 시도해볼 수 있다.

```sh
cat << EOF > SSLClient.java
import javax.net.ssl.*;
import java.io.*;
import java.net.Socket;
import java.util.Arrays;

public class SSLClient {
    public static void main(String[] args) throws Exception {
        String host = "{HOSTNAME}";
        int port = {PORT};

        // Specify the desired cipher suite
        String[] desiredCipherSuites = {
          "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
          "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256",
          "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
          "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
          "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
        };

        // Create a trust manager that does not validate certificate chains
        TrustManager[] trustAllCerts = {
            new X509TrustManager() {
                public java.security.cert.X509Certificate[] getAcceptedIssuers() {
                    return null;
                }

                public void checkClientTrusted(java.security.cert.X509Certificate[] certs, String authType) {
                }

                public void checkServerTrusted(java.security.cert.X509Certificate[] certs, String authType) {
                }
            }
        };

        // Install the all-trusting trust manager
        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(null, trustAllCerts, new java.security.SecureRandom());

        // Create socket factory with the all-trusting manager
        SSLSocketFactory factory = sslContext.getSocketFactory();

        // Create the SSLSocket
        SSLSocket socket = null;
        for (String cipherSuite : desiredCipherSuites) {
            try {
                // Create a new socket with the desired cipher suite
                socket = (SSLSocket) factory.createSocket(host, port);
                socket.setEnabledCipherSuites(new String[]{cipherSuite});

                // Start SSL/TLS handshake
                socket.startHandshake();

                // Get the enabled cipher suite negotiated during the handshake
                String negotiatedCipherSuite = socket.getSession().getCipherSuite();

                // Print negotiated cipher suite
                System.out.println("Negotiated Cipher Suite:");
                System.out.println(negotiatedCipherSuite);
            } catch (Exception e) {
                // If the handshake fails, try the next cipher suite
                System.out.println("Failed to negotiate using cipher suite: " + cipherSuite);
                e.printStackTrace();
            } finally {
                // Close the socket if it was created
                if (socket != null) {
                    try {
                        socket.close();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
            }
        }
    }
}
EOF
javac -cp . SSLClient.java
java -cp . SSLClient
```



ECDSA 3개 Cipher suites를 사용할 시, Java code는 아래와 같이 exception이 발생했다.

```
Failed to negotiate using cipher suite: <ECDSA cipher suite name>
javax.net.ssl.SSLHandshakeException: Received fatal alert: handshake_failure
        at sun.security.ssl.Alert.createSSLException(Alert.java:131)
        at sun.security.ssl.Alert.createSSLException(Alert.java:117)
        at sun.security.ssl.TransportContext.fatal(TransportContext.java:364)
        at sun.security.ssl.Alert$AlertConsumer.consume(Alert.java:293)
        at sun.security.ssl.TransportContext.dispatch(TransportContext.java:203)
        at sun.security.ssl.SSLTransport.decode(SSLTransport.java:155)
        at sun.security.ssl.SSLSocketImpl.decode(SSLSocketImpl.java:1320)
        at sun.security.ssl.SSLSocketImpl.readHandshakeRecord(SSLSocketImpl.java:1233)
        at sun.security.ssl.SSLSocketImpl.startHandshake(SSLSocketImpl.java:417)
        at sun.security.ssl.SSLSocketImpl.startHandshake(SSLSocketImpl.java:389)
        at SSLClient.main(SSLClient.java:51)
```



동시에 WLS 에서도 exception이 발생했다.

```
<Debug> <SecuritySSL> <BEA-000000> <[Thread[ExecuteThread: '2' for queue: 'weblogic.socket.Muxer',5,Thread Group for Queue: 'weblogic.socket.Muxer']]weblogic.security.SSL.jsseadapter: SSLENGINE: Exception occurred during SSLEngine.wrap(ByteBuffer,ByteBuffer).
javax.net.ssl.SSLHandshakeException: no cipher suites in common
        at sun.security.ssl.Alert.createSSLException(Alert.java:131)
        at sun.security.ssl.Alert.createSSLException(Alert.java:117)
        at sun.security.ssl.TransportContext.fatal(TransportContext.java:364)
        at sun.security.ssl.TransportContext.fatal(TransportContext.java:320)
        at sun.security.ssl.TransportContext.fatal(TransportContext.java:311)
        at sun.security.ssl.ServerHello$T12ServerHelloProducer.chooseCipherSuite(ServerHello.java:460)
        ...
        
<Debug> <SecuritySSL> <BEA-000000> <[Thread[ExecuteThread: '2' for queue: 'weblogic.socket.Muxer',5,Thread Group for Queue: 'weblogic.socket.Muxer']]weblogic.security.SSL.jsseadapter: SSLENGINE: SSLEngine.wrap(ByteBuffer,ByteBuffer) called: result=Status = CLOSED HandshakeStatus = NOT_HANDSHAKING
```



반면, RSA Handshake에는 아래처럼 정상 수행이 되었다. (WLS Log)

```
<Debug> <SecuritySSL> <BEA-000000> <[Thread[ExecuteThread: '2' for queue: 'weblogic.socket.Muxer',5,Thread Group for Queue: 'weblogic.socket.Muxer']]weblogic.security.SSL.jsseadapter: SSLENGINE: negotiatedCipherSuite: <RSA cipher suite name>>

<Debug> <SecuritySSL> <BEA-000000> <[Thread[ExecuteThread: '0' for queue: 'weblogic.socket.Muxer',5,Thread Group for Queue: 'weblogic.socket.Muxer']]weblogic.security.SSL.jsseadapter: SSLENGINE: SSLEngine.wrap(ByteBuffer,ByteBuffer) called: result=Status = OK HandshakeStatus = FINISHED
```



이로써, 다양한 Cipher suites를 사용하는 Client를 지원하기 위한 요구가 있지만 WLS에서 지원하지 않는 한계가 있다는 것을 검증하였다.

WLS 만 구성한 시스템일 경우, 가장 광범위하게 사용되는 RSA 인증서를 사용하면 될 것이며,

가장 권장 되는 케이스로는 앞단에 다양한 Cipher 를 지원하는 LB 또는 Web server를 두는 것이다.





## 2.2 JSSE API 에서 SSL 구성

### 2.2.1 인증서 생성

`2.1.1 인증서 생성`과 동일하다.





### 2.2.2 Start SSL Server Socket

다음의 Java code로 SSL Server를 생성한다.

```sh
cat << EOF > SSLServer.java
import javax.net.ssl.*;
import java.io.*;
import java.security.*;
import java.security.cert.CertificateException;

public class SSLServer {
    public static void main(String[] args) {
        int port = <HTTPS PORT>;
        
        try {
            // Load keystore
            String keystorePath = "FULLPATH of keystore.jks";
            char[] keystorePassword = "<Keystore Password>".toCharArray();
            char[] keyPassword = "<Key Password>".toCharArray();
            
            KeyStore keyStore = KeyStore.getInstance("JKS");
            FileInputStream inputStream = new FileInputStream(keystorePath);
            keyStore.load(inputStream, keystorePassword);
            
            // Initialize key manager factory
            KeyManagerFactory keyManagerFactory = KeyManagerFactory.getInstance("SunX509");
            keyManagerFactory.init(keyStore, keyPassword);

            // Initialize SSL context
            SSLContext sslContext = SSLContext.getInstance("TLS");
            sslContext.init(keyManagerFactory.getKeyManagers(), null, null);

            // Create SSL server socket factory
            SSLServerSocketFactory sslServerSocketFactory = sslContext.getServerSocketFactory();

            // Create SSL server socket
            SSLServerSocket sslServerSocket = (SSLServerSocket) sslServerSocketFactory.createServerSocket(port);

            // Accept incoming connections
            while (true) {
                SSLSocket sslSocket = (SSLSocket) sslServerSocket.accept();
                SSLSession sslSession = sslSocket.getSession();
                System.out.println("SSL handshake successful with:");
                System.out.println("   Protocol: " + sslSession.getProtocol());
                System.out.println("   Cipher suite: " + sslSession.getCipherSuite());
                sslSocket.close();
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
EOF
javac -cp . SSLServer.java
java -cp . SSLServer
```





### 2.2.3 SSL Handshake to Java

`2.1.5 SSL Handshake to WLS` 의 Java code를 실행하여 Java SSL Server와 Handshake를 수행하면,

다음과 같이 RSA 및 ECDSA 복합적인 Cipher Suites 를 모두 소화한다.

```sh
SSL handshake successful with:
   Protocol: TLSv1.2
   Cipher suite: TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
   
SSL handshake successful with:
   Protocol: TLSv1.2
   Cipher suite: TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256
   
SSL handshake successful with:
   Protocol: TLSv1.2
   Cipher suite: TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
   
SSL handshake successful with:
   Protocol: TLSv1.2
   Cipher suite: TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
   
SSL handshake successful with:
   Protocol: TLSv1.2
   Cipher suite: TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
```



JSSE API(여기서는 `KeyManagerFactory` 사용) 으로 SSL Server Socket 를 구현하면 여러 Keystore 및 여러 Alias 를 Load 할 수 있기 때문에, 다양한 Cipher suite를 갖는 Client에 대한 제약이 없다.
