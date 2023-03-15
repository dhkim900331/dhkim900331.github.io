---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[Middleware/WebLogic] JDBC 스펙에 의해, AutoCommit 이 실행되는 경우"
tags: [Middleware, WebLogic]
typora-root-url: ..
---


# 1. 개요

JDBC 스펙에 의해, AutoCommit 이 실행되는 경우



# 2. 설명

어플리케이션에서 쿼리를 auto commit 하지 않는 상태 = setAutoCommit(false)



위의 경우에,

commit 또는 rollback 실행하지 않고 connection.close()를 호출하면

해당 쿼리는 setAutoCommit(true)를 호출하여, 자동으로 commit 되게 한다.



이것은, JDBC 스펙에 따라 commit 을 보장하기 위함이다.

하지만 몇몇 드라이버(Oracle 10.x, 11.x)에서는 commit이 자동으로 실행되지 않는다.



이러한 동작으로 인해,

commit 또는 rollback 되어야 하는 작업이 다음에 실행되도록 예약된다.

즉 원치 않는 시점에, commit 또는 rollback 된다.



이러한 상황을 방지하기 위해 웹로직 데이터소스는 connection 이 pool에 반환될 때 commit을 호출한다.



setAutoCommit(true) 선언 하거나,

connection.close() 전에 commit 또는 rollback을 항상 정확하게 호출하고 있다면,

system property에 `weblogic.datasource.endLocalTxOnNonXaConWithCommit=false` 를 적용하여

불필요한 자동 commit 보장을 제거 할 수 있다.

> 요약: JDBC 스펙에 따라, 자동 commit 을 할 필요 없으므로 `weblogic.datasource.endLocalTxOnNonXaConWithCommit=false` 옵션을 적용할 필요가 있다.



위는, Non-XA 이며,

XA connection에서는 commit 또는 rollback을 호출하지 않으면

항상 connection.close 될 때 무조건 rolled back 한다.



roll back 대신 commit 되게 하려면 아래 옵션을 추가한다.

`weblogic.datasource.endLocalTxOnXaConWithCommit=true`



[참고 문서](https://docs.oracle.com/middleware/1212/wls/JDBCA/transactions.htm#JDBCA152)

> 관련 문서 : Doc ID 2129810.1
