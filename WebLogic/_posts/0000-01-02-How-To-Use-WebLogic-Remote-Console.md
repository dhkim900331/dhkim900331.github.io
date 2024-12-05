---
date: 2024-12-05 16:08:27 +0900
layout: post
title: "[WebLogic/WRC] How To Use WebLogic Remote Console?"
tags: [Middleware, WebLogic, WRC, Remote, Console, REST, OpenSource]
typora-root-url: ..
---

# 1. Overview

WebLogic Remote Console(이하 WRC) 를 상세하게 다룬다.

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


2.3.3 Provider : Administration Server

[여기](https://oracle.github.io/weblogic-remote-console/userguide/providers/administration-server/)에서 본문 확인

WebLogic Admin Server에 연결되어, Domain의 구성을 편집한다. 기존의 WebLogic Admin Console의 대체.

기존의 Admin Console과 어떤 [차이점](https://oracle.github.io/weblogic-remote-console/setup/admin-console-diff)이 있냐면,

- Oracle Redwood Theme와, [Oracle JET(Javascript Extension Toolkit)](https://www.oracle.com/application-development/technologies/jet/oracle-jet.html)으로 구성
- 기존의 Console에서는 Configuration 항목과 Monitoring 항목이 하나의 Page에 구성된 것에 반해,
  WRC에서는 별도로 분리되어 Tree 탐색이 더욱 명확해짐
- WRC 에서 변경한 구성 요소들은, 이제 Shopping Cart 에 Item으로 담긴다.
  Commit 된 변경 사항들로 인해, 재시작이 필요한 Server는 Monitoring Tree 에서 확인할 수 있다.


<br><br>


2.3.4 Property List

2.3.5 WDT Model File

2.3.6 WDT Composite Model FIle


<br><br>




<br><br>


# 3. References

