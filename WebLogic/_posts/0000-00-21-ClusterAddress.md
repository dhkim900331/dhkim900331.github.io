---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] Cluster Address(클러스터 주소), Number Of Servers In Cluster Address(클러스터 주소의 서버 수)"
tags: [Middleware, WebLogic, Cluster]
typora-root-url: ..
---

<br># 1. 개요

Cluster Address(클러스터 주소), Number Of Servers In Cluster Address(클러스터 주소의 서버 수)

<br>
# 2. 설명

Cluster Address와 Number Of Servers In Cluster Address 항목은 EJB 환경에서만 유효한 옵션입니다.

Entity Beans와 EJB Handles에 대하여 Failover 처리시에 Cluster Address에 나열된 매니지드 서버들을 호출하게 됩니다.

<br>
Number Of Servers In Cluster Address 는 Cluster Address를 설정하지 않고, Dynamic Cluster 기능을 위한 옵션입니다.

Cluster에 매니지드를 추가하면, Cluster Address도 실시간으로 변경해야 되지만, Number Of Servers In Cluster Address 옵션을 3으로 설정하면

랜덤으로 Cluster로 묶인 매니지드 서버 3개를 선택하여 Cluster Address에 자동으로 주소를 완성하는 기능입니다.

<br>
EJB 를 사용하지 않으면, Cluster Address와 Number Of Servers In Cluster Address 옵션은 설정하지 않습니다.

오라클에서 진행된 SR 검색 시 :  SR 3-14878490191
