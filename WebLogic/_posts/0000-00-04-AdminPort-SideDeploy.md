---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] Administration Port, Side-By-Side Deploy"
tags: [Middleware, WebLogic, Deploy]
typora-root-url: ..
---


# 1. 개요

Administration Port, Side-By-Side Deploy 기능을 알아보자.



# 2. Administration Port

- SSL 을 사용하여 웹로직 콘솔에 접근 하도록 한다.
- 알려지지 않은 포트로 포워딩 시킴으로써, 보안에 유리하다.
  (원래 7001포트 -> 7200포트 등.. 사용자 정의에 의함)
- 매니지드 서버도 Administration Port를 해서 관리해야되는 단점이 있다.



## 2.1 설정 방법

### 2.1.1 Admin Server

(1). Managed Shutdown

(2). console - domain - configuration - general - Enable Administration Port, Administration Port

(3). https://ip : administration Port로 console을 재접속한다.

![AdminPort_SideDeploy_1](/../assets_copy_final/posts/images/WebLogic/AdminPort-SideDeploy/AdminPort-SideDeploy_1.png)





### 2.1.2 Managed Server

Configuration - General - Advanced - Local Administration Port Override : Administration Port가 Managed Server 마다 Unique해야 된다.

### 2.1.3 Start Server

(1). admin url = t3s://adminIP : administration port

(2). JAVA_OPTIONS="-Dweblogic.security.TrustKeyStore=DemoTrust"

### 2.1.4 Stop Server

(1). exit url = t3s://managed ip : managed administration port

(2). JAVA_OPTIONS="-Dweblogic.security.TrustKeyStore=DemoTrust"

> \* DemoTrust 말고도... 다양하게 설정할 방법이 있을텐데...



# 3. Side-By-Side Deploy

어플리케이션을 서비스 중지없이 업데이트하여 버전 관리가 가능하다.



## 3.1 배포된 어플리케이션의 상태와 커맨드

### 3.1.1 Active State

모든 사용자가 접근 가능한 어플리케이션 상태.

타겟 인스턴스가 기동 중이지 않으면 New state

기동 중이면 Activice state



```bash
java -Dweblogic.security.TrustKeyStore=DemoTrust weblogic.Deployer -adminurl t3://adminServer_Address -user weblogic -password weblogic1 -deploy -name webapp -source D:\weblogic\WLS1036\domains\dm1036\webapp -targets m1 -appversion v1
```

![AdminPort_SideDeploy_2](/../assets_copy_final/posts/images/WebLogic/AdminPort-SideDeploy/AdminPort-SideDeploy_2.png)



> appversion 파라메터가 버전 관리를 위해 잘 관리해줘야 한다.



### 3.1.2 Stop Running State

구 버전 어플리케이션과 신 버전 어플리케이션의 관리



```bash
java -Dweblogic.security.TrustKeyStore=DemoTrust weblogic.Deployer -adminurl t3://adminServer_Address -user weblogic -password weblogic1 -deploy -name webapp -source D:\weblogic\WLS1036\domains\dm1036\webapp -targets m1 -appversion v2
```

![AdminPort_SideDeploy_3](/../assets_copy_final/posts/images/WebLogic/AdminPort-SideDeploy/AdminPort-SideDeploy_3.png)



> webapp(v1)은 아직 사용자가 있어서 stop Running... 다 빠져나가면 retired가 된다.
>
> webapp(v2)로 이후 신규 사용자가 접속된다.



### 3.1.3 ADMIN State

administration port를 사용 중인 admin server 환경에서 어플리케이션의 오픈전 테스트를 위해 사용한다.

ADMIN state 어플리케이션은 웹로직 'myrealm'에 허가된 유저&그룹만 접근가능한데,

administration port를 사용하여 접근하는 행위가 허가된 유저&그룹 인증 절차이기 때문이다.



```bash
java -Dweblogic.security.TrustKeyStore=DemoTrust weblogic.Deployer -adminurl t3s://adminServerIP:administrationPORT -user weblogic -password weblogic1 -adminmode -name webapp -deploy -upload -remote D:\weblogic\WLS1036\domains\dm1036\webapp
```

![AdminPort_SideDeploy_4](/../assets_copy_final/posts/images/WebLogic/AdminPort-SideDeploy/AdminPort-SideDeploy_4.png)



![AdminPort_SideDeploy_5](/../assets_copy_final/posts/images/WebLogic/AdminPort-SideDeploy/AdminPort-SideDeploy_5.png)



> 위 커맨드 실행 결과가 remove Initializing 일 수 있다... admin server restart 하니 admin state이다...
