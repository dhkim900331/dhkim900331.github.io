---
date: 2022-05-30 10:24:20 +0900
layout: post
title: "[JBoss] Cluster Protocol Type"
tags: [Middleware, JBoss, Cluster, Protocol, TCP, PING, TCPPING, Member, Session]
typora-root-url: ..
---


# 1. 개요

JBOSS EAP 7.X 의 Unicast Cluster 구성 방식 중에 Protocol Type에 대한 내용을 요약한다.



# 2. Protocol Type

* FRAG 또는 FRAG2
송신자는 큰 메시지를 쪼개어, 수신자에게 전달한다.
수신자는 작은 메시지를 조합하여, 원본 큰 메시지로 만든다.
frag_size 보다 큰 메시지를 쪼갠다.



* TCP
  송신자 정보, 연결 만료 시간, 버퍼 크기 등 소켓 채널과 관련



* FORK
  Piggyback 이라는 방식의 통신 방법을 의미하는 것으로 보임.
  send/ack 와 같이 주고받는 통신 형식이 아니라, 수신자가 나중에 보낼 데이터가 있을 때
  응답을 껴서 보낸 다는 방식 같음.
  기본값이 config=null 이라 사용하지 않아 중요해보이지 않음.



* MFC 또는 UFC
  FC는 Flowcontrol (흐름제어)라고 하여, 수신자가 발신자보다 메시지 받는 속도가 느릴 경우 발신자를 수신자의 속도에 맞추도록 한다.
  수신자가 메시지를 빠르게 받다가, Queue가 꽉차서 Drop msg 를 다시 요청하는 경우를 피하기 위함.
  MFC는 멀티캐스트. UFC는 유니캐스트. 각 캐스트 방식에 따라 나누어 놓았다.



* GMS
  Group MemberShip.
  클러스터 멤버 구성에 관여.
  max_join_attempts 기본값이 10인데, 10회 실패하면 싱글톤(스탠드얼론)의 의미인가? 테스트가 가능한가?



* MERGE2 또는 MERGE3
  클러스터 전체를 관리하는 리더가 있다.
  클러스터 전체 멤버는 주기적으로 INFO 메시지를 수신받고 잘못된 멤버를 제거 하는 등의 병합 관리가 된다.
  max_interval=30000 (30초) 마다 INFO 메시지 전송.



* UNICAST2 또는 UNICAST3
  두(2) 개의 구성원들 간의 메시지를 손실없이 정렬하여 메시지 통신을 수행한다.
  두(2) 개라는 부분이 정확히 어떤 의미인지 확인이 필요하다.
  중요한 부분 같다.



* NAKACK 또는 NAKACK2
  메시지를 정확히 순서대로, 보내주는 FIFO 기능을 제공



* VERIFY_SUSPECT

  문제가 발생한 것으로 보여지는 클러스터 멤버를 다시 재확인 하는 프로토콜

* 

* FD_SOCK
  클러스터 멤버들은 ring 형태로 연결되어 있고, 이웃 멤버가 비정상적으로 닫히면
  (아마도; 내 생각에는) VERIFY_SUSPECT 에서 감지한다.
  하지만, 정상적으로 닫히는 경우 이웃에게 이벤트를 전달하여 의심을 피하도록 한다.
  VERIFY_SUSPECT 문서에 설명이 되어 있는 내용 중에,
  떠나려는 멤버가 비정상적이라고 의심되면, 이벤트를 위로(stack 위 라고 표현함) 던진다고 한다.
  그래서 FD_SOCK 의 순서가 아래에 있는게 아닌가 싶다.
  실제로 JBOSS Cluster 구성 시 Protocol 정의 순서가 중요하다고 나와있다.



* STABLE
  메시지가 모든 구성원에 안정적으로 잘 도착했는지 확인되면 메시지를 삭제함.
  모든 구성원에 도착한다는 개념이, 복제 캐시 모드를 뜻하는지 알 수 없음..



* FD_ALL 또는 FD_ALL2
  FD는 실패 감지로, 구성원들이 정상적으로 응답하는지 하트비트로 체크한다.
  구성원들은 이웃(ring형태에서 오른쪽 방향)에게 점차 메시지를 전달하며 모든 구성원이 체크되는 구조.
  ALL 은, 모든 구성원이 멀티캐스트로 체크됨.



* TCPPING
  정확히 설정된(initial_hosts)에 ping을 던져 멤버 구성



# 3. 참고 문헌

http://www.jgroups.org/manual/html/protlist.html
