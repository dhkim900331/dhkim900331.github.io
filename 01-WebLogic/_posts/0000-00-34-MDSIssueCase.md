---
layout: post
title: "[WebLogic] 금융권 MultiDataSource 이슈 사례"
tags: [WebLogic, Issues, MultiDataSource]
date: 2022-02-07 17:42:10 +0900
---


# 1. 개요
Multidatasource 사용 중인 고객사에서 발생한 장애


# 2. 현상
데이터소스 이름과 설정 내용
```
ADataSource_1 (MultiDataSource; Failover, DB#1, DB#2)
ADataSource_2 (MultiDataSource; Failover, DB#2, DB#1)
```

(1). 고객사 물리 DB는 2대이며, DB#2번 스토리지 장애 발생.

(2). DB#2번 장애로 인해, WebLogic ADataSource_1 Multi DataSource force disabled 및
모든 세션이 DB#1번으로 연결되는 ADataSource_2 으로 쏠림.

(3). ORA-12520 에러 발생

ADataSource_1 번에 모든 세션이 몰리면서 DB#1번 Max Process 도달하였음.

```
ADatSource_1 disabled.
```

(4). 시간이 지나 DB#2번 정상화 되어,

```
ADataSource_2 re-enabled.
```

(5). 그러나 ADataSource_1 번은 re-enabled 되지 않고, 다음날 오전까지 disabled 상태.

(6). 더 이상 재현되지 않고, 의심가는 부분이 발견되지 않아 가진 로그만으로 해결 불가능.


# 3. 해결
## 3.1 해결을 위해 참고한 문서들
### (1). MultiDatasource에서 장애를 인지하고, Failover 시키는 메커니즘.

> _"BEA-000639","BEA-001584","BEA-001117" Printed in Server Log Repeatedly ( Doc ID 2474159.1 )_
>
> 문서에서는 **Multi Data Source Fail-Over Limitations and Requirements** 를 참고하면 됨.

Test Connections on Reserve to Enable Fail-Over : 테스트 커넥션 기능으로 감지.

No Fail-Over for In-Use Connections : Connection은 AP와 직접 할당되므로, 중간에 이를 생성/할당해준 DataSource는 문제의 Connection을 강제로 회수할 수가 없음. (정확히는 사용중인 커넥션)

AP(Logic)에서 문제의 Connection을 close(con.close();) 하고 새로운 연결을 시도해야 한다는 의미.

여기서 No Fail-Over for In-Use Connections 부분을 좀 유심히 봐야될 필요가 있었는데,
고객사는 MultiDatasource 구성이었다.
여기서 더 나은 환경을 위해 Generic DataSource + TAF 구성을 가져가면, No Fail-Over for In-Use Connections 이슈를 회피할 수 있는지에 관심을 가졌다.

그러나, TAF 구성으로 가더라도, Connection 자체는 AP와 DB가 직접적으로 관계를 맺고 있기 때문에
여전히 No Fail-Over for In-Use Connections 문제는 발생할 수 있다.
다만 TAF 기능을 통해 DB-tier에서의 Failover(rac) 를 기대해볼 수만 있다.


### (2). MultiDataSource 의 Failover 동작 메커니즘

> _<https://docs.oracle.com/middleware/1213/wls/JDBCA/jdbc_multidatasources.htm#JDBCA220>_
> Connection Request Routing Enhancements When a Generic Data Source Fails : 일반 데이터소스 실패 시, Disabled 하여 서비스 라우팅 성능 향상이라는 원론적인 설명
>
> Automatic Re-enablement on Recovery of a Failed Generic Data Source within a Multi Data Source : Disabled 일반 데이터소스 주기적으로 테스트하여 재복구한다는 것
>
> Enabling Failover for Busy Generic Data Sources in a Multi Data Source : Failover 기능 사용시, Max Capacity 초과해서 오는 Request는 다음 DataSource에 전달 한다는 기능
>
> Controlling Multi Data Source Failover with a Callback : CallBack Handler 설명 (AP 로직에서 쓸경우..)