---
date: 2023-07-28 08:38:57 +0900
layout: post
title: "[WEB/Apache] MaxConnectionsPerChild Monitoring"
tags: [WEB, Apache, MaxConnectionsPerChild, server-status, ExtendedStatus]
typora-root-url: ..
---

# 1. Overview

Apache MaxConnectionsPerChild 가 정상적으로 동작하는지 살펴본다.

Debug Log를 통해서도 살펴볼 수 있는데, 이 방법은 나중에 작성하고

여기서는 server-status Page를 통해 확인 해본다.

<br><br>
# 2. Descriptions

httpd.conf는 다음과 같이 구성한다.

```
<Location /server-status>
    SetHandler server-status
</Location>

ExtendedStatus On

...

 <IfModule mpm_worker_module>
    StartServers              1
    ServerLimit               1
    MinSpareThreads          25
    MaxSpareThreads          25
    ThreadsPerChild          25
    ThreadLimit              25
    MaxRequestWorkers        25
    MaxConnectionsPerChild   10
    Mutex fcntl:${ORACLE_INSTANCE}/servers/${COMPONENT_NAME}/logs
</IfModule>
```

<br>
worker MPM은 Child Process를 1개만 빈약하게 두도록 하여, Monitoring 이 용이하다.

<br>
Debug log를 잠깐 보면, child process는 slot max가 25로 표현된다.

```
AH00930: initialized pool in child <PID> for (*) min=0 max=25 smax=25
```

<br>
/server-status?refresh=1 호출 시

```
Srv	PID	Acc	M	CPU	SS	Req	Dur	Conn	Child	Slot	Client	Protocol	VHost	Request *This line is HEADER
0-0	2406527	73/73/79	K	0.28	0	2	325	1004.5	0.98	0.99	10.8.125.203	http/1.1	wls.local:10088	GET /server-status?refresh=1 HTTP/1.1
```

<br>
server-status 페이지가 같은 Session 내에서 지속적으로 호출되어,

ACC(73/73/79)

-> 현재 Connection(Keep-Alive)에 73번째 연속 호출

-> 현재 Child Process에 73번째 연속 호출

-> 현재 Child Process내에 같은 Thread(server-status 에서는 slot으로 표현됨)에 79번째 연속 호출

<br>
server-status 페이지 동작 방식상 keep-alive timeout을 유발할 경우는 없으므로
대부분 같은 connection/child/slot 에서 처리되는것이 목격된다.

<br>
curl 명령을 이용해 connection close 되므로 항상 새로운 요청으로 유입되는 경우,
(명령어는 curl --head http://wls.local:10088/MaxConnectionPerChild/Test 를 사용한다.)

<br>
child process가 새로 만들어진 직후에는, Acc의 Slot은 예전 누적치가 기록되어 있겠지만, Child(가운데 숫자)는 0으로 한번도 사용되지 않은 Slot임을 보여준다.

```
Srv	PID	Acc	M	CPU	SS	Req	Dur	Conn	Child	Slot	Client	Protocol	VHost	Request
0-0	2415459	0/0/40	W	0.00	0	0	132	0.0	0.00	0.24	10.8.125.203	http/1.1	wls.local:10088	GET /server-status?refresh=1 HTTP/1.1
0-0	2415459	0/0/5	_	0.00	2	1	11	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415459	0/0/32	_	0.00	2	1	86	0.0	0.00	0.14	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415459	0/0/17	_	0.00	0	1	45	0.0	0.00	0.09	10.8.125.203	http/1.1	wls.local:10088	GET /server-status?refresh=1 HTTP/1.1
0-0	2415459	0/0/5	_	0.00	2	1	13	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415459	0/0/21	_	0.00	2	1	65	0.0	0.00	0.11	10.8.125.203	http/1.1	wls.local:10088	GET /server-status?refresh=1 HTTP/1.1
0-0	2415459	0/0/5	_	0.00	2	1	26	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415459	0/0/6	_	0.00	2	1	15	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415459	0/0/6	_	0.00	2	2	23	0.0	0.00	0.01	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415459	0/0/7	_	0.00	2	6	18	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415459	0/0/3	_	0.00	2	2	10	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415324	1/1/2	C	0.12	6	0	2	0.0	0.00	0.00	127.0.0.1	http/1.1	localhost:10099	HEAD /dms/ HTTP/1.1    <<<< 과거 child process 로 보여짐
0-0	2415459	0/0/4	_	0.00	2	1	9	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
```

<br>
curl 로 호출했으므로, 모든 slot이 점점 1로 채워진다.

```
0-0	2415459	0/2/42	_	0.05	29	1	139	0.0	0.01	0.25	10.8.125.203	http/1.1	wls.local:10088	GET /server-status?refresh=1 HTTP/1.1
0-0	2415459	12/12/17	W	0.10	0	0	50	81.3	0.08	0.08	10.8.125.203	http/1.1	wls.local:10088	GET /server-status?refresh=1 HTTP/1.1
0-0	2415459	1/1/33	C	0.07	6	0	87	0.0	0.00	0.14	127.0.0.1	http/1.1	localhost:10099	HEAD /dms/ HTTP/1.1
0-0	2415459	0/0/17	_	0.00	30	1	45	0.0	0.00	0.09	10.8.125.203	http/1.1	wls.local:10088	GET /server-status?refresh=1 HTTP/1.1
0-0	2415459	0/1/6	_	0.07	6	1	16	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415459	0/1/22	_	0.08	4	1	68	0.0	0.00	0.11	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415459	0/1/6	_	0.08	3	9	37	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415459	0/1/7	_	0.09	2	1	17	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415459	0/1/7	_	0.11	1	0	24	0.0	0.00	0.01	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415459	0/0/7	_	0.00	32	6	18	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415459	0/0/3	_	0.00	32	2	10	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415459	0/0/2	_	0.00	29	0	2	0.0	0.00	0.00	127.0.0.1	http/1.1	localhost:10099	HEAD /dms/ HTTP/1.1
0-0	2415459	0/0/4	_	0.00	32	1	9	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
```

<br>
slot 1이 모두 10개가 된 직후에는 바로, child proces 재생성 된 것으로 보여진다.

```
0-0	2415632	0/0/42	W	0.00	0	0	139	0.0	0.00	0.25	10.8.125.203	http/1.1	wls.local:10088	GET /server-status?refresh=1 HTTP/1.1
0-0	2415632	0/0/19	_	0.00	2	1	56	0.0	0.00	0.09	10.8.125.203	http/1.1	wls.local:10088	GET /server-status?refresh=1 HTTP/1.1
0-0	2415632	0/0/33	_	0.00	2	0	87	0.0	0.00	0.14	127.0.0.1	http/1.1	localhost:10099	HEAD /dms/ HTTP/1.1
0-0	2415632	0/0/17	_	0.00	2	1	45	0.0	0.00	0.09	10.8.125.203	http/1.1	wls.local:10088	GET /server-status?refresh=1 HTTP/1.1
0-0	2415632	0/0/6	_	0.00	2	1	16	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415632	0/0/22	_	0.00	2	1	68	0.0	0.00	0.11	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415632	0/0/6	_	0.00	2	9	37	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415632	0/0/7	_	0.00	2	1	17	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415632	0/0/7	_	0.00	2	0	24	0.0	0.00	0.01	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415632	0/0/14	_	0.00	1	1	40	0.0	0.00	0.05	10.8.125.203	http/1.1	wls.local:10088	GET /server-status?refresh=1 HTTP/1.1
0-0	2415632	0/0/5	_	0.00	2	1	14	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
0-0	2415632	0/0/2	_	0.00	2	0	2	0.0	0.00	0.00	127.0.0.1	http/1.1	localhost:10099	HEAD /dms/ HTTP/1.1
0-0	2415632	0/0/5	_	0.00	2	1	11	0.0	0.00	0.00	10.65.34.245	http/1.1	wls.local:10088	HEAD /MaxConnectionPerChild HTTP/1.1
```

<br>
server-status 호출과, 내부적으로 관리를 위해 호출되는 dms(Dynamic Monitoring Service) 에 의해 좀 더 일찍 slot이 채워질 수 있겠다. (순수 Apache가 아니라 OHS 12cR2 이다.)

<br>
Keep-Alive가 아닌 요청이 유입된다는 가정하에, Slot이 모두 1로 채워진 뒤, PID가 바뀔 것이다.
