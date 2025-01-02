---
date: 2024-12-05 16:08:27 +0900
layout: post
title: "[WebLogic/WRC] How To Use WebLogic Remote Console?"
tags: [Middleware, WebLogic, WRC, Remote, Console, REST, OpenSource]
typora-root-url: ..
---

# 1. Overview

WebLogic Remote Console(이하 WRC) 를 상세하게 다룬다.


<br><br>

<br>

# 2. Descriptions

## 2.1 What Is It?

WRC는 Oracle Cloud, K8S, Container 환경, VM, On-Prem 와 같은 다양한 환경에 있는 WebLogic Domain 에 접근하여 관리할 수 있도록 하는, 가벼운 OpenSource.

기존의 WebLogic Admin Console과 다르게, WRC은 WebLogic Server Domain에 배치 되어 있지 않아도 된다.

WebLogic REST APIs 를 활용하는 WRC는 어디에서나, 손쉽게 Destktop Application으로 설치하여 Domain의 Admin Server에 연결할 수 있다.

WRC는 WebLogic Server 12.2.1.3, 12.2.1.4, 그리고 14.1.1.0 에서 모든 기능을 지원 한다.


<br><br>


## 2.2 Key Features of the WRC

WRC는 현대의 Cloud Native Trends에 따라, WebLogic Management Information에 접근하기 위해 REST 기반을 사용하는 WebLogic Server administration GUI 대체제이다.

WRC를 사용하여, WebLogic Domain에 접근하면 다음을 활용할 수 있다.

- WLS Instance와 Cluster 구성
- WDT Metadata Model 생성 및 수정
- JDBC, JMS와 같은 WLS Services 항목 구성
- Application 배포 관리
- Instance와 App의 시작과 정지
- Instance와 App의 Monitoring


<br><br>


## 2.3 Get Started

### 2.3.1 Installation

- [시스템 요구 사항](https://oracle.github.io/weblogic-remote-console/setup/#sys_reqs) 확인

- [여기](https://github.com/oracle/weblogic-remote-console/releases)에서 최신 Release 를 받고, Desktop Application으로 손쉽게 설치한다.

- 추가로 WRC Extension File(`console-rest-ext-X.X.X.war`)을 WebLogic Server Domain에 배포하여, 추가적인 기능을 사용할 수 있다. 이는 권장되며 사용자의 선택 사항이다.

  - `${DOMAIN_HOME}/management-services-ext/console-rest-ext-X.X.X.war`
    WRC Extension File을 위와 같이 배치하고,
    Admin Server를 재시작 하는 것만으로도 배포가 완료 된다.
    Latest version으로 Old version을 덮어 씌우는 것만으로도 Update가 된다.

<br><br>


### 2.3.2 Connect to a provider

기본적인 내용은 [여기](https://oracle.github.io/weblogic-remote-console/setup/#connect)에서 확인.

<br>

Provider type으로 제공되는 항목은,

- Administration Server : `-> 2.3.3 Provider : Administration Server` 참고
- Property List
- WDT Model File
- WDT Composite Model File


<br><br>

### 2.3.3 Provider: Administration Server

[여기](https://oracle.github.io/weblogic-remote-console/userguide/providers/administration-server/)에서 본문 확인

WebLogic Admin Server에 연결되어, Domain의 구성을 편집한다. 기존의 WebLogic Admin Console의 대체.

기존의 Admin Console과 어떤 [차이점](https://oracle.github.io/weblogic-remote-console/setup/admin-console-diff)이 있냐면,

- Oracle Redwood Theme와, [Oracle JET(Javascript Extension Toolkit)](https://www.oracle.com/application-development/technologies/jet/oracle-jet.html)으로 구성
- 기존의 Console에서는 Configuration 항목과 Monitoring 항목이 하나의 Page에 구성된 것에 반해,
  WRC에서는 별도로 분리되어 Tree 탐색이 더욱 명확해짐.
- WRC 에서 변경한 구성 요소들은, 이제 Shopping Cart 에 Item으로 담긴다.
  Commit 된 변경 사항들로 인해, 재시작이 필요한 Server는 Monitoring Tree 에서 확인할 수 있다.


<br><br>


#### 2.3.1.1 Understand access discrepancies

[Understand access discrepancies](https://oracle.github.io/weblogic-remote-console/userguide/role-access/)에서 설명하는 내용은, security realm 에 정의된 사용자 계정에 부여된 권한에 따라 WebLogic Remote Console 에서도 이를 반영하듯, 동작한다.

특정 사용자는 대폭적인 권한으로 더 많은 것을 관리할 수 있는 반면에, 그렇지 않은 사용자는 일부 화면을 볼 수 없는 등의 권한 제어가 가능하다.


<br><br>


#### 2.3.1.2 HTTPS Connection

[Connect to a WebLogic domain using SSL/TLS](https://oracle.github.io/weblogic-remote-console/userguide/advanced-settings/#ssl) 참고

Weblogic Console이 HTTPS 로 보호 받고 있다면,

`파일 - 설정 - 네트워킹` 에서 `보안 저장소 유형` 을 JKS 입력 시, 그 아래에 `보안 저장소 경로`가 나타나고, 여기서 Trust 인증서 파일을 선택하여 저장한다.

`보안 저장소 키`에는 JKS 패스워드를 입력한다.

<br>

인증서가 만료된 경우에는, `비보안 접속하기`를 사용할 수 있다.


<br><br>


#### 2.3.1.3 Proxy Server

[Configure a proxy server](https://oracle.github.io/weblogic-remote-console/userguide/advanced-settings/#proxy) 참고

여러 Provider에 전역적으로 영향을 미치는 글로벌 또는, 개별 Provider에 영향을 미치는 Proxy Server를 설정한다.


<br><br>


#### 2.3.1.4 The 4 Perspectives

Admin Server Provider는, 사용자에게 최대 4개의 관점을 제공한다.

<br>

- Edit Tree : Domain 설정 변경
- Configuration Tree : Domain을 Read-Only 권한으로 살펴보고, 현재 그 순간에 적용되어 있는 설정값을 확인할 수 있다. Shopping Cart에 아직 적용하지 않은 설정은 여기에 포함되지 않는다.
- Monitoring Tree : 실행중인 도메인의 런타임 통계를 제공한다. 여기서 인스턴스/어플리케이션의 시작/중지 또한 가능하다.
- Security Data Tree : `WRC Extension File` 배포 후 보여진다. Security realm을 제어할 수 있다.


<br><br>


#### 2.3.1.5 Edit a WebLogic Administration Server

[Edit a WebLogic Administration Server](https://oracle.github.io/weblogic-remote-console/userguide/providers/administration-server/#changes_adminserver) 참고

<br>

기존의 Admin console의 Editing과 유사하다.

Extension WAR가 배포되어 있는 경우와 그렇지 않은 경우, (좌/우 이미지)

Commit이 필요한 변경사항에 대해 쉽게 확인이 된다.

![image-20241216102842507](/../../../../../AppData/Roaming/Typora/typora-user-images/image-20241216102842507.png)


<br><br>


#### 2.3.1.6 Control Operations

[Control Operations](https://oracle.github.io/weblogic-remote-console/userguide/providers/administration-server/#controls) 참고

<br>

Monitoring Tree - Servers 에서 손쉽게 인스턴스 제어가 가능하며, NodeManger가 필요하다.


<br><br>


#### 2.3.1.7 Create MBeans

[Create MBeans](https://oracle.github.io/weblogic-remote-console/userguide/providers/administration-server/#create) 참고

<br>

Admin Console보다 간소화된 App 배포, JDBC Resource 생성 등에 대한 기능이 있다.

Admin Console과 달리, MBean을 만들 때 추가적으로 필요한 부모 MBean 이 있는 경우 미리 작업을 완료해야 한다.

<br>

예를 들어, 새로운 Server를 만들면서, 동시에 새로운 Cluster에 할당하려는 경우.

Admin Console은 새로운 Server를 만드는 페이지에서 Cluster를 만드는 메뉴를 제공하지만,

WRC에서는 새로운 Cluster를 미리 만들고, 새로운 Server를 만드는 과정을 수행해야 한다.

<br>

또 다른 예로, JDBC Datasource를 생성하는 경우.

Admin Console은 만들기 단계에서 구성 요소들을 단계적으로 채워나가지만,

WRC에서는 기본 MBean 객체를 만든 다음 세부 구성요소를 편집할 수 있다.


<br><br>


#### 2.3.1.8 Editing Security Data

[EDITING SECURITY DATA](https://oracle.github.io/weblogic-remote-console/userguide/providers/administration-server/security-data) 참고

<br>

Extenstion WAR 가 배포된 경우, Domain의 Security Data/Provider를 관리할 수 있다.

Security Data 관점에서 변경하는 사항들은, 재시작 필요없이 즉시 적용된다.

<br>

이미 있거나, 여기서 새로 만드는 사용자로 WRC 로그인을 하면 사용자에게 부여된 권한(Admin, Developer, Monitor 등등)에 따라서 Tree가 제한적으로 보여진다.

<br>

내용 다 해봐야 할듯


<br><br>


### 2.3.4 Provider: Property List

[Property lists](https://oracle.github.io/weblogic-remote-console/userguide/providers/property-list) 참고

<br>

이게 뭔지 요약은 나중에 작성

지금 이해한 바로는, 아래 WDT model file에 key:value 형식으로 손쉽게 값을 넘겨주기 위한 파일임.


<br><br>


#### 2.3.4.1 Create/Upload/Edit/Delete a property list

- Create Provider for New Property List(새 속성 목록으로 새로운 제공자 생성).

  Property List Filename 에 FULLPATH 로 기입을 하거나,

  Property List Filename에 Filename만 입력하고 Directory Icon을 선택하면, 경로가 완성되며 저장된다.

- 


<br><br>


### 2.3.5 Provider: WDT Model File

[WDT Model File](https://oracle.github.io/weblogic-remote-console/userguide/providers/wdt-model) 참고

<br>

WDT(Weblogic Deploy Tooling) 이해하기로는,

지금까지 WLS 복잡한 작업을 위해 WLST scripting등을 사용해왔는데

이제 yaml 형식으로 손쉽게 선언하는 방식의 메타파일을 만들고

WDT 실행파일로 실행하면, WLST 보다 간소화되었지만 많은 동작을 실행가능

도메인 생성부터 여러가지 업데이트 까지..?

WLST는 python까지 접목해야 하니, 실제로 이게 편해보임.

그리고 위 Property file과 연계하여 사용 가능


<br><br>


### 2.3.6 Provider: WDT Composite Model FIle

WDT Model file을 여러 개로 병합한 모델 파일이라는데.. WDT model file이 선행되어야 가능할 것으로 보임


<br><br>


2.3.7. Generate Dashboards


<br><br>


2.3.8 Customize settings

<br>

2.3.9 Upgrade the WebLogic Remote Console

<br>

2.3.10 Check log files

<br>

2.3.10 Understand access discrepancies


<br><br>

<br>

<br>

# 3. References

