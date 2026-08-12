---
date: 2024-12-05 16:08:27 +0900
layout: post
title: "[WebLogic/WRC] How To Use WebLogic Remote Console?"
tags: [Middleware, WebLogic, WRC, Remote, Console, REST, OpenSource]
typora-root-url: ../..
---

# 1. Overview

WebLogic Remote Console(이하 WRC) 를 상세하게 다룬다.

대부분의 아래 내용은, 24년도 말~25년도 초에 작성되었는데, 시간이 경과함에 따라 Remote Console 공식 메뉴얼 페이지에 리뉴얼되면서 링크가 많이 변경되었다. 보존을 위해 깨진 링크가 있다 하더라도, 기능 자체가 달라지지는 않았으므로 그대로 두었다.

<br>

<br>

# 2. Descriptions

## 2.1 What Is It?

WRC는 Oracle Cloud, K8S, Container 환경, VM, On-Prem 와 같은 다양한 환경에 있는 WebLogic Domain 에 접근하여 관리할 수 있도록 하는, 가벼운 OpenSource.

기존의 WebLogic Admin Console과 다르게, WRC은 WebLogic Server Domain에 배치 되어 있지 않아도 된다.

WebLogic REST APIs 를 활용하는 WRC는 어디에서나, 손쉽게 Destktop Application으로 설치하여 Domain의 Admin Server에 연결할 수 있다.

WRC는 WebLogic Server 12.2.1.2.0 이상 버전에 연결할 수 있고, 14.1.2 에서 모든 기능을 완벽히 지원 한다.


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

- [시스템 요구 사항](https://oracle.github.io/weblogic-remote-console/set-console/#GUID-FFC1F9AC-7CE7-4BC1-9D3D-BD59CC228C6B) 확인

- [여기](https://github.com/oracle/weblogic-remote-console/releases)에서 최신 Release 를 받고, Desktop Application으로 손쉽게 설치한다.

- 추가로 WRC Extension File(`console-rest-ext-X.X.X.war`)을 WebLogic Server Domain에 배포하여, 추가적인 기능을 사용할 수 있다. 이는 권장되며 사용자의 선택 사항이다.

  - `${DOMAIN_HOME}/management-services-ext/console-rest-ext-X.X.X.war`
    WRC Extension File을 위와 같이 배치하고,
    Admin Server를 재시작 하는 것만으로도 배포가 완료 된다.
    Latest version으로 Old version을 덮어 씌우는 것만으로도 Update가 된다.
  - WLS 14.1.2 부터는 자동으로 낮은 버전이 배포가 되고, 최신버전을 받아 위의 단계에 따라 구성하면 업그레이드가 된다.

<br><br>


### 2.3.2 Connect to a provider

기본적인 내용은 [여기](https://oracle.github.io/weblogic-remote-console/set-console/#GUID-82C1C605-D42E-45EA-AC16-5BA3D5853C96)에서 확인.

<br>

Provider type으로 제공되는 항목은,

- Administration Server : `-> 2.3.3 Provider : Administration Server` 참고
- Property List
- WDT Model File
- WDT Composite Model File


<br><br>

### 2.3.3 Provider: Administration Server

[여기](https://oracle.github.io/weblogic-remote-console/administration-server/domain-configuration/#GUID-37C3DE03-B1A7-42AA-B596-83D7A9520D33)에서 본문 확인

WebLogic Admin Server에 연결되어, Domain의 구성을 편집한다. 기존의 WebLogic Admin Console의 대체.

기존의 Admin Console과 어떤 [차이점](https://oracle.github.io/weblogic-remote-console/2.0.0/setup/admin-console-diff/)이 있냐면,

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

[HostnameVertification 을 disable](https://oracle.github.io/weblogic-remote-console/administration-server/domain-configuration/#GUID-85D3E2FF-86EA-49E1-8BAE-5ECB1A9A9E1E) 하려면 설정 - 네트워킹 - 호스트 이름 확인 사용 안함? 에서 '예'를 하면 Certification CN 필드를 검사하지 않는다.

<br>

Administartion Mode가 활성화 된 도메인의 경우에도, `${DOMAIN_HOME}/security/DemoTrust.p12 (14.1.2 예시)` 와 같은 pkcs12 인증서 파일을 Remote Console에 설정하면 연결할 수 있다.

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

<br><br>


### 2.3.4 Provider: Property List

[Property lists](https://oracle.github.io/weblogic-remote-console/userguide/providers/property-list) 참고

<br>

WDT 로 만들어진 JSON 파일로, 이것을 Property file이라고 하며 Remote Console에 Provider 항목으로 추가하면 GUI 환경에서 편집할 수 있다.


<br><br>


#### 2.3.4.1 Create/Upload/Edit/Delete a property list

- Create Provider for New Property List(새 속성 목록으로 새로운 제공자 생성).

  Property List Filename 에 FULLPATH 로 기입을 하거나,

  Property List Filename에 Filename만 입력하고 Directory Icon을 선택하면, 경로가 완성되며 저장된다.

<br><br>


### 2.3.5 Provider: WDT Model File

[WDT Model File](https://oracle.github.io/weblogic-remote-console/userguide/providers/wdt-model) 참고

<br>

WDT 기능 자체는 WebLogic Domain을 YAML/JSON 형태로 편집할 수 있게 한다.

도메인 자체에 대한 편집을 비개발자도 매우 빠르고 쉽게 다룰 수 있게 되는 것이며,

WDT 를 통해 만들어진 Model file(YAML/JSON) 들을 Remote Console 에 Provider로 추가하면

GUI 환경에서 편집할 수 있다.

<br><br>


### 2.3.6 Provider: WDT Composite Model FIle

WDT Model file 을 세분화 하여 다룰 수 있는 부분


<br><br>


2.3.7. Generate Dashboards


<br><br>


2.3.8 Customize settings

<br>

### 2.3.9 Upgrade the WebLogic Remote Console

Desktop App은 Github에서 최신버전을 다운로드 받아 재설치하거나, Remote Console 상단에 최신 버전을 업데이트 하라는 안내가 보이면 따라하면 된다.

Hosted App은 매 분기마다 나오는 PSU 패치를 통해 최신 버전으로 업그레이드 하면 된다.


<br><br>


### 2.3.10 Check log files

Linux, macOs, Windows 플랫폼별로 out.log 가 저장된다.

Windows 의 경우, `%APPDATA%\Roaming\weblogic-remote-console`에 out.log가 날짜별로 로테이션 되어 저장된다.

아직까지 해당 로그에 기록되는 에러 코드 등에 대해서 참고할 문서는 없다.


<br><br>


2.3.10 Understand access discrepancies

<br>

2.3.11 Remote console version naming rule

WRC는 MAJOR.MINOR.PATCH 세개의 Numbering/Naming rule을 갖는다.


<br><br>


### 2.3.12 Oracle Support Policy : WRC

WRC 제품이 릴리즈되면 첫 12개월 동안은, Active(활성) 상태.

12개월 지난 이후부터는 Maintenance(유지보수) 상태.

또 다시 12개월 지나는, 릴리즈 되고 나서 24개월이 지난 시점 부터는 End of Life(수명 종료) 상태.

<br>

각 상태별로 Oracle 지원 정책이 달라진다.

Webcast 확인 또는 최신 문서 확인 필요


<br><br>

<br>

<br>

# 3. References

**Advisor Webcast: WebLogic Console의 혁신, Remote Console을 소개합니다, Mar 19, 2025 [video] (Doc ID 3067753.1)**
