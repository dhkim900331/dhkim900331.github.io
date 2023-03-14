---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WAS/WebLogic] nostage와 stage 배포 흐름"
tags: [WAS, WebLogic]
typora-root-url: ..
---


# 1. 개요

Staing Mode는 stage와 nostage로 분류



# 2. 설명

## 2.1 stage

* 모든 instance가 AdminServer의 장비에서 file donwload 하기 때문에, instance startup이 지연되는 단점이 있다.
* webapp을 배포해야 하는 많은 장비가 있을 경우에는, source update가 편리해지는 장점이 있다.
* 또한, download 받은 webapp은 domain_home/servers/{instances} 아래에 모두 복사한다.



## 2.2 nostage

* 모든 instance는 자신의 장비에 webapp이 있기 때문에, stage와 달리 file download 와 같은 작업이 필요 없다.
* 많은 수의 장비에서는 변경된 source를 장비마다 다시 업로드해야하는 단점
* domain_home/servers/{instances} 아래에는 컴파일된 jsp, servlet 등만 위치한다. jsp_servlet 디렉토리가 생성되어 있음.



## 2.3 기타

* stage와 nostage 모두 새로운 소스를 배포하고자 할때는, servers를 지우고 배포하는게 정신건강에 좋다.
* 새로운 소스가 servers의 소스보다 이전 날짜면 새로운 소스 날짜를 touch 로 갱신해야 한다.

* 새로운 소스를 올렸는데도, 이전 버전의 어플리케이션이 보인다고하면 관련 디렉토리의 변경 날짜를 잘 살피자.
