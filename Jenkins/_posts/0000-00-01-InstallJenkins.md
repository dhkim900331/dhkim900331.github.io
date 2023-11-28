---
date: 2022-02-15 12:26:08 +0900
layout: post
title: "[Jenkins] 설치"
tags: [Jenkins, CICD]
typora-root-url: ..
---


# 1. 개요
Tomcat 에 Jenkins 설치
Jenkins 는 기본적으로 jetty 로 구성되어 패키지 제공되고 있으나,
war를 Tomcat에 배포하는 것으로 설치해보기로 한다.
{{ site.content.br_small }}
# 2. 설치
## 2.1 다운로드
[여기 클릭](https://www.jenkins.io/download/)

![InstallJenkins_1](/../assets/posts/images/Jenkins/InstallJenkins/InstallJenkins_1.png)

위 LTS 항목을 다운로드 받았다.
{{ site.content.br_small }}
## 2.2 Tomcat 환경변수 설정
JEKINS_HOME만 세팅하였다.

```bash
export JENKINS_HOME="your path"
```
{{ site.content.br_small }}
## 2.3 war를 배포

```bash
/app/servers/tomcat1/webapps/jenkins.war
```
여기까지가 아주 심플하게 설치는 완료되었다.
{{ site.content.br_small }}
# 3. Tomcat (jenkins) 시작
## 3.1 기동 시 로그에 아래처럼 초기 패스워드가 확인된다.

```bash
*************************************************************
*************************************************************
*************************************************************

Jenkins initial setup is required. An admin user has been created and a password generated.
Please use the following password to proceed to installation:

1c0cba1ae6ef4b8a812978b4f578443e

This may also be found at: /app/servers/tomcat1/jekins_home/secrets/initialAdminPassword

*************************************************************
*************************************************************
*************************************************************
```

http://tomcat-addr/jekins 에서 위 패스워드로 접속을 한다.
{{ site.content.br_small }}
## 3.2 플러그인 설치
여기 시스템은 폐쇄망이 아니므로 제안하는 권장 플러그인 리스트를 설치한다.
플러그인은 hpi 파일을 받아 JENKINS_HOME/plugins 에 넣고 재기동해도 된다.
{{ site.content.br_small }}
## 3.3 로그인
플러그인 설치가 마무리되면, 기본 설치 과정은 모두 끝났다.
계정을 생성하고 로그인한다.
