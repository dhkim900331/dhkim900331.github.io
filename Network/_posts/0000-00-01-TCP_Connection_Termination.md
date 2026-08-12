---
date: 2026-04-13 09:30:29 +0900
layout: post
title: "[Network/TCP] TCP Connection Termination (4-Way Handshake)"
tags: [Network, TCP, Linux, FIN, ACK, TIME_WAIT, CLOSE_WAIT]
typora-root-url: ../..
---

# 1. Overview

아래 애니메이션은 서로 연결된 A와 B의 TCP Connection 종료 과정을 단계별로 보여준다.

![TCP Connection 종료 과정 애니메이션](/assets/posts/images/Network/TCP_Connection_Termination/TCP_Connection_Termination.gif)


<br><br>


# 2. Descriptions

서로 연결된 A와 B의 TCP Connection 종료 과정에 대한 간략한 설명

**A	:** A측 TCP stack / OS kernel 관점의 상태

**A.app:** A측 application

<br>

**B	:** B측 TCP stack / OS kernel 관점의 상태

**B.app:** B측 application

<br>

## 2.1 A.app.close

A측 app에서 socket 연결 종료를 명시적으로 호출하면,

A측 은 B측에게 종료를 원한다는 FIN 을 전송하고,

A측 은 FIN_WAIT_1 이 된다.

`A.ESTABLISHED -> A.FIN_WAIT_1`


<br><br>


## 2.2 B측의 자동 응답

B측은 A측으로부터 FIN을 수신하면 Kernel이 ACK를 자동 전송한다.

동시에 B.app에는 EOF(read=0)가 전달된다.

이때 애플리케이션은 read() 결과를 통해 연결 종료를 인지하며,

언어/구현에 따라 EOFException 또는 read=0 형태로 표현될 수 있다.

`B.ESTABLISHED -> B.CLOSE_WAIT`


<br><br>


## 2.3 A측에서 B.ACK 수신

A가 보낸 FIN에 대해 B가 ACK를 보냈으므로,

A는 자신의 종료 요청이 정상적으로 전달되었음을 확인하고

이후 B의 FIN을 기다리는 상태가 된다.

`A.FIN_WAIT_1 -> A.FIN_WAIT_2`


<br><br>


## 2.4 B.app.close

B측 App 또한 close를 호출하고 A측에게 FIN을 보낸다.

`B.CLOSE_WAIT -> B.LAST_ACK`


<br><br>


## 2.5 A측에서 B.FIN 수신

'A측 또한 B측에서 종료 수순에 들어갔다는 사실을 알게 되었다.'

B.FIN을 잘 받았다고 마지막 ACK를 보낸다.

`A.FIN_WAIT_2 -> A.TIME_WAIT`


<br><br>


## 2.6 B측에서 마지막 ACK 수신

`B.LAST_ACK -> CLOSED`


<br><br>


## 2.7 기타

### (1) "2.2" 단계에서의 B측 Application의 역할과 책임

2번 단계에서 B application은 A 측의 종료 진행(FIN 수신)을 인지하게 된다.

이때 B측 Kernel은 자동으로 ACK를 전송하며,

동시에 B.app에는 EOF(read=0)가 전달된다.

<br>

B application은 이를 통해 상대방이 더 이상 데이터를 보내지 않음을 인지하고,

자신이 추가로 보낼 데이터가 있는지 확인한 후,

적절한 시점에 B.app.close()를 명시적으로 호출해야 한다.

<br>

만약 B.app이 close()를 호출하지 않고

예외를 삼키거나 로직이 종료되어 버리면,
B측은 CLOSE_WAIT 상태에 머무르게 되고,
A측은 FIN_WAIT_2 상태에서 B의 종료(FIN)를 계속 기다리게 된다.

<br>

바로 위의 내용을 다시 정리하면,

TCP 연결 종료는 단순히 한쪽에서 close()를 호출한다고 즉시 완료되는 것이 아니라,

양측 애플리케이션이 각각 자신의 종료 책임을 수행해야 정상적으로 마무리된다.

<br>

특히 한쪽이 FIN을 수신한 뒤에도 애플리케이션이 적절한 시점에 close()를 호출하지 않으면,

수신 측은 CLOSE_WAIT, 송신 측은 FIN_WAIT_2 상태에 장시간 머무를 수 있으며,

이는 대표적인 애플리케이션 종료 처리 버그 패턴이다.


<br><br>


### (2) A측이 TIME_WAIT으로 머무는 이유

TCP 연결 종료 과정에서 마지막 ACK의 신뢰성을 보장하기 위함이다.

TCP에서는 FIN을 전송한 측이 해당 FIN에 대한 ACK을 수신하지 못하면

RTO에 따라 FIN을 재전송한다.

<br>

특히 2.5 단계에서 A는 B의 FIN을 수신한 뒤 마지막 ACK을 전송하고

TIME_WAIT 상태에 진입한다.

<br>

이때 만약 해당 ACK이 유실되면,

B는 자신의 FIN에 대한 ACK을 받지 못했기 때문에 FIN을 재전송하게 되고,

TIME_WAIT 상태에 있는 A는 이를 수신하여 다시 ACK을 전송한다.

<br>

이와 같이 TIME_WAIT 상태는 마지막 ACK 유실 상황에서도

연결 종료가 정상적으로 완료되도록 보장하는 역할을 한다.


<br><br>

<br>

# 3. References

없음
