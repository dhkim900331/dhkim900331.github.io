---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WAS/WebLogic] Serializable Test"
tags: [WAS, WebLogic, Serializable]
typora-root-url: ..
---


# 1. 개요

세션 복제 될 데이터가 직렬화 되어있는 경우와 그렇지 않은 경우를 테스트해보았습니다.

이때 세션 데이터는 직렬화 구현이 필요한 클래스 객체로 구현해보았습니다.



# 2. 테스트 어플리케이션

[webapp.zip](/assets/upload/webapp.zip)

> 첨부파일의 FailoverTest.jsp는 원본입니다.
>
> FailoverTest_class.jsp는 페이지 로드 시 1씩 증가하는 Integer 데이터를 새로 생성한 클래스에 멤버 변수로 선언하여 저장하게 했습니다.
>
> 세션 데이터는 첨부파일의 sessionObject 클래스를 선언하여 멤버 변수에 저장합니다.
>
> package kdh; -> FailoverTest_class.jsp가 클래스 파일을 import 하기 위해서는 패키지화를 꼭 해야 된다고 해서 kdh로 구성하였습니다.
>
> implements Serializable -> Serializable를 구현하여 클래스가 세션 복제 될 수 있도록 하였습니다.
>
> serialVersionUID가 없거나 서로 다르면, 세션 복제는 되더라도 쿠키가 덮어씌워집니다.
>
> 첨부파일의 weblogic.xml에 cookie-domain을 .main.com 으로 설정했습니다.
>
> 윈도우 로컬에서 테스트하였는데, C:\Windows\System32\drivers\etc\hosts 파일에 m1.main.com과 m2.main.com을 등록하였습니다.



# 3. Serializable 가 구현되지 않았을 때

* 웹로직 인스턴스 m1, m2는 이중화 구성이며 클러스터 되었습니다.
* 웹로직 콘솔 -> Env -> Servers -> m1 / m2 -> Logging -> Advanced -> **Standard out의 Severity level을 Debug로 설정**하였습니다.
  * -> Debug -> weblogic -> servlet -> internal -> **session 을 체크하고 Enable** 하였습니다.
  * [참고사이트](https://community.oracle.com/thread/1123562?tstart=0) // 2021.12.20 일 기준 404



```bash
<Debug> <HttpSessions> <BEA-000000> <Session attribute with name:sessionObject class:kdh.sessionObject is not serializable ane will  not be replicated or persisted>

<Debug> <HttpSessions> <BEA-000000> <synchronized on -4561296442252280985 and session is inUse: false and active request count is: 0>

<Debug> <HttpSessions> <BEA-000000> <[HTTP Session:100078]HTTPSession with id: "o3x3KA71JO-6he8QpS7zQL5qKE-c9XLj8FBFrFsLfs9wzWH6pFIr" is of size 1,030 bytes.>

<HttpSessions> <BEA-000000> <The change associated with this SessionData(-4561296442252280985 or weblogic.servlet.internal.session.ReplicatedSessionData@6a648175 ) is: 1017170932>

<Debug> <HttpSessions> <BEA-000000> < SessionData.syncSession() the change is modified: false and the active request count is: 0 for -4561296442252280985 and this is: weblogic.servlet.internal.session.ReplicatedSessionData@6a648175 >
```

> Serializable 구현되지 않았을 때 로그



# 4. Serializable 구현되었을 때

```bash

<Debug> <HttpSessions> <BEA-000000> <[HTTP Session:100046]Creating new session with ID: LLl3LO-KBxD9qlT40AsWbLjP5gJfcf7MB-5C5FBWVUBM8SPXDRzV for Web application: /webapp.>

<Debug> <HttpSessions> <BEA-000000> <[HTTP Session:100050]The current server is becoming the primary server for replicated session ID: LLl3LO-KBxD9qlT40AsWbLjP5gJfcf7MB-5C5FBWVUBM8SPXDRzV.>

<Debug> <HttpSessions> <BEA-000000> <sessionId:LLl3LO-KBxD9qlT40AsWbLjP5gJfcf7MB-5C5FBWVUBM8SPXDRzV associated with roid:-4561296442252280984>

<Debug> <HttpSessions> <BEA-000000> <[HTTP Session:100077]HTTPSession attribute: "sessionObject" is of size 61 bytes.>

<Debug> <HttpSessions> <BEA-000000> <Checksum for attribute 'sessionObject', value: 2071176261>

<Debug> <HttpSessions> <BEA-000000> <synchronized on -4561296442252280984 and session is inUse: false and active request count is: 0>

<Debug> <HttpSessions> <BEA-000000> <[HTTP Session:100078]HTTPSession with id: "LLl3LO-KBxD9qlT40AsWbLjP5gJfcf7MB-5C5FBWVUBM8SPXDRzV" is of size 1,242 bytes.>

<Debug> <HttpSessions> <BEA-000000> <The change associated with this SessionData(-4561296442252280984 or weblogic.servlet.internal.session.ReplicatedSessionData@49221aa7 ) is: 995501008>

<Debug> <HttpSessions> <BEA-000000> < SessionData.syncSession() the change is modified: true and the active request count is: 0 for -4561296442252280984 and this is: weblogic.servlet.internal.session.ReplicatedSessionData@49221aa7 >

<Debug> <HttpSessions> <BEA-000000> <Replicating session : -4561296442252280984 and weblogic.servlet.internal.session.ReplicatedSessionData@49221aa7 >
```



