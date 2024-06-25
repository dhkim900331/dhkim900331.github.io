---
date: 2024-06-25 16:09:26 +0900
layout: post
title: "[WebLogic/JTA] JTA Timeout and EJB Timeout"
tags: [Middleware, WebLogic, EJB, Timeout, JTA]
typora-root-url: ..
---

# 1. Overview
JTA Timeout과 EJB Timeout의 상관관계

{{ site.content.br_big }}

# 2. Descriptions

## 2.1 JTA Timeout

[JTA Timeout 의 설명](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wlmbr/mbeans/JTAMBean.html#TimeoutSeconds)

> Specifies the maximum amount of time, in seconds,
>
> an active transaction is allowed to be in the first phase of a two-phase commit transaction.
>
> If the specified amount of time expires, the transaction is automatically rolled back. 
{{ site.content.br_small }}
JTA는 2PC 를 지원하며, JTA Timeout은 전체 트랜잭션(2PC 까지의 모든 작업이 Commit 되는 것 또는 반대로 모든 변경 사항이 Rollback 되는 것) 중 작업 기간이 초과하지 않도록 보장한다.
{{ site.content.br_big }}
## 2.2 JTA Timeout 과 EJB Timeout 설정간의 우선순위

EJB는 CMT나 BMT냐에 따라 다르며

CMT일 경우 WebLogic domain에 설정하는 JTA Timeout(기본값 30초) 설정의 영향을 받으며

BMT는 개발자가 JTA APIT를 사용하여 EJB Transaction 간에 Timeout을 직접 지시한다.

둘 다 JTA API 영향을 받지만 CMT는 컨테이너(WLS)가 관리하는 Transaction 의미이므로,

JTA Timeout 설정에 globally 하게 영향을 받는 다는 의미이다.
{{ site.content.br_small }}
[JTA API Overview 참고](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wljta/jtaapi.html#GUID-F1E79DA6-7A95-4FB5-B341-839D7A2D30AE)

> You use this interface as part of a Java client program or within an EJB as part of a bean-managed transaction.
{{ site.content.br_small }}
[10 Transactions in EJB Applications 참고](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wljta/trxejb.html#GUID-357B74F6-6D08-45B3-B203-3EE0DEB00D46)

>  10 Transactions in EJB Applications
>
> * The EJB specification allows for distributed transactions that span multiple resources (such as databases) and supports the two-phase commit protocol for both EJB CMP 2.1 and EJB CMP 1.1.
> * the transaction attribute specifies whether transactions are demarcated by the WebLogic Server EJB container (container-managed transactions) or by the EJB itself (bean-managed transactions).
> * he setting of the transaction-type element in the deployment descriptor determines whether an EJB is container-managed or bean-managed.
>
> 
>
> * Setting Transaction Timeouts
>   * Container-managed transactions: The Bean Provider configures the trans-timeout-seconds attribute in the weblogic-ejb-jar.xml deployment descriptor.
>   * Bean-managed transactions: An application calls the UserTransaction.setTransactionTimeout method. 
{{ site.content.br_big }}
# 3. References

위 컨텐츠에 직접 소개되어 있음.
