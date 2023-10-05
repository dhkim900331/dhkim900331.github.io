---
date: 2023-10-05 14:49:59 +0900
layout: post
title: "[WebLogic] Connection Filter"
tags: [Middleware, WebLogic, Connection, Filter]
typora-root-url: ..
---

# 1. Overview

과거에 [Security-Filter]({{ site.url }}/Security-Filter) 를 Post 한 바 있다.

많이들 활용하는 기능은 아닌데 반해, 낮은 이해도로 접근 할시에 많은 위험을 초래할 수 있는 옵션이기에

다시 한 번, 자세하게 소개한다.

<br><br>
# 2. Descriptions

## 2.1 Syntax

기본적인 Syntax는 `targetAddress destAddress destPort Action Protocols` 로 구성되어 있다.

외부에서 인입되는 요청의 IP를 `targetAddress` 이다.

왜, targetAddress 이냐면, Connection Filter를 적용시킬 target 이기 때문이다.

<br><br>
그리고, target이 접근할 목적지는 `destAddress`, `destPort` 이다.

Filter를 적용할 시에, AdminServer는 작성한 `destAddress`, `destPort` 가 모두 유효한지 검증을 하므로,

당연하지만 WLS Instances 만 기입할 수 있다.

<br><br>
target을 dest이 Allow/Deny 할 지를 정하는 것은, `Action` 이다.

`Protocols` 는 어떤 Protocols 에 대해서 적용할지를 나타낸다.

<br><br>
그리고 Rule은, 위에서 부터 아래로 수행된다.

요청이 인입되면, 맨 위의 Rule 부터 판별하고 Allow에 해당되면 더 이상 Rule에 대해 검증되지 않고 종료된다.

마지막 까지 Rule이 진행되었지만 해당되는 Rule이 없더라도 Allow와 동일하게 동작한다.

<br><br>
그래서 보통, 여러 라인의 Allow를 통해 필요한 접근을 나열하고

마지막에 전체 Deny를 통해 불필요한 접근을 일괄 거부할 수 있다.

이 부분들에서 의도치 않게 접근 거부되어 서비스 장애가 발생하지 않도록 하는 것이 매우 중요하다.

<br><br>
## 2.2 Behavior

Filter Rule의 Deny에 의해서 거부되면, 다음과 같이 Log에 남는다. (Connection Logger Enabled 활성화 필요)

```
<Notice> <Socket> <BEA-000445> <Connection rejected, filter blocked Socket[addr=10.8.120.59,port=53260,localport=8002,protocol=http], weblogic.security.net.FilterException: [Security:090220]rule 5>
```

해당 Log가 발생한 곳은 Managed Server(8002 Port) 였다.

인입되는 `targetAddress` 가 10.8.120.59:53260 이고, `Protocol`은 http 이다.

rule 5 의해 차단되었다. Filter Rule 에서 주석을 제외한, 순수 Rule Text 에서 5번째 Line이다.

<br><br>
Allow 되면, 다음과 같이 매번 Log에 남는다.

Filter가 건전한지 확인하기 위해, 초반에만 Logger 를 활성화하자.

```
<Info> <Socket> <BEA-000431> <Accepted connection: filtering is set to: "true", remote address: "/10.8.120.59", remote port: "53141", local address: "/10.65.34.245", local port: "8002", protocol: "http">
```

<br><br>
## 2.3 Use Case

### 2.3.1 Startup Managed

여기서 설명하는 Filter는, 다음의 환경을 가지고 진행한다.

```
Windows Client(Chrome) : 10.8.120.59
Weblogic Box(Machine) : 10.65.34.256
Admin * Managed Server Ports : 8001 ~ 8003
```

<br><br>
다음의 Rule은,

```
# Managed Server > Admin Server
10.65.34.245 10.65.34.245 8001 allow t3 ldap http
```

Managed Server가 MSI Mode가 아닌 이상, 필요한 Rule이다.

동일한 Weblogic Box 하나에 Admin과 Managed가 모두 있기 때문에,

`targetAddress` 와 `destAddress` 가 동일하다.

<br><br>
기동 시 `-Dweblogic.management.server` 로 보통 t3 protocol을 사용하기 때문에,

Managed(target)이 Admin(dest)에 t3 를 허용하도록 한다.

<br><br>
접근 인증을 위해 ldap 또한 필요하다.

http protocol은 어떤 것때문에 필요한지는 구체적으로 확인이 되지 못했지만,

config.xml 반영에 필요한 것으로 보아, 필수 요소로 보여진다.

<br><br>
또한 해당 Rule은 Admin이 있는 Box 내에서 Admin을 Shutdown 하는데에도

t3, ldap Protocol이 필요하기 때문에 필수이다.

<br><br>
위의 Rule이 활성화 되면, 다음과 같은 Log를 기동 시에 Admin Server에서 확인할 수 있다.

```
<Info> <Socket> <BEA-000431> <Accepted connection: filtering is set to: "true", remote address: "/10.65.34.245", remote port: "56196", local address: "/10.65.34.245", local port: "8001", protocol: "http">

<Info> <Socket> <BEA-000431> <Accepted connection: filtering is set to: "true", remote address: "/10.65.34.245", remote port: "14542", local address: "/10.65.34.245", local port: "8001", protocol: "t3">

<Info> <Socket> <BEA-000431> <Accepted connection: filtering is set to: "true", remote address: "/10.65.34.245", remote port: "58186", local address: "/10.65.34.245", local port: "8001", protocol: "ldap">

```

<br><br>
### 2.3.2 Admin to Managed

다음의 Rule은,

```
# Admin Server > Managed Server (주기적으로 요청..)
10.65.34.245 10.65.34.245 8002 allow http
10.65.34.245 10.65.34.245 8003 allow http
```

<br><br>
Admin Server가 RUNNING 일 때에만, 1분 간격으로 Managed에 http Traffic이 유입된다.

어떤 목적(Data gathering 등)으로 실행되는지는 알 수 없지만, 유의미 할 것이므로 필요하다.

<br><br>
단순한 Test 시에는 Deny 되더라도 문제점은 보이지 않았다.

<br><br>
### 2.3.3 Managed to themselves

다음의 Rule은,

```
# Managed Server > themselves
10.65.34.245 10.65.34.245 8002 allow ldap
```

<br><br>
Managed Server가 자기 자신들에게 ldap 인증을 수행하는 것으로 보이기 때문에 필요하다.

활성화 되지 않으면 Shutdown 할 수 없다.

<br><br>
### 2.3.4 Admin Console

다음 Rule은,

```
# Windows Client > Admin Console
10.8.120.59 10.65.34.245 8001 allow http
```

<br><br>
Windows 사용자가 Chrome 브라우저 등을 통해 Admin Console에 접근하기 위해 필요하다.

<br><br>
### 2.3.5 Managed App

다음 Rule은,

```
# Windows Client > Managed Web app
10.8.120.59 10.65.34.245 8002 allow http
10.8.120.59 10.65.34.245 8003 allow http
```

<br><br>
보통은 앞단의 Web server에서 Managed에 배포된 App에 접근하기 위한 Rule로 필요할 것이다.

여기서는, Web 대신 Client 만 있다.

<br><br>
### 2.3.6 Other - Deny

다음 Rule은,

```
# Other - Deny
0.0.0.0/0  *  *  deny
```

<br><br>
모든 `targetAddress` 를 절대적으로 접근 거부하는 것이다.

`0.0.0.0` 과 같은 표현은 모든 IP를 표현하는 기본 예약어 이므로,

잘못 사용하면 의도치 않는 접근 거부가 발생할 수 있다.

<br><br>
### 2.3.7 Finally

종합적으로, Rule은 위에서 설명했듯이 위에서, 아래 흐름을 갖는다.

다음의 Rule은,

위에서 설명한 것을 하나로 합친 것이다.

참고로 주석(#) 사용 가능하다.

<br><br>
```
################################
# Windows Client : 10.8.120.59 #
# Weblogic Box : 10.65.34.245  #
# Adm/Mgd Ports : 8001 ~ 8003  #
################################

# Managed Server > Admin Server
10.65.34.245 10.65.34.245 8001 allow t3 ldap http

# Admin Server > Managed Server (주기적으로 요청..)
10.65.34.245 10.65.34.245 8002 allow http

# Managed Server > themselves
10.65.34.245 10.65.34.245 8002 allow ldap

# Windows Client > Admin Console
10.8.120.59 10.65.34.245 8001 allow http

# Windows Client > Managed Web app
10.8.120.59 10.65.34.245 8002 allow http
10.8.120.59 10.65.34.245 8003 allow http

# Other - Deny
0.0.0.0/0  *  *  deny
```

<br><br>
반드시 필요한 Rule을 허용해 두지 않으면,

마지막 Rule 7번(주석을 제외한 순수 Rule Text line)에서 위험한 장애가 발생할 수 있다.

<br><br>
예를 들어, `# Windows Client > Managed Web app` 가 포함되어 있지 않았다면,

외부(WEB)에서 유입되는 요청들 중 http Protocol이 Managed로 가는 Rule이 없는 것과 마찬가지이기 때문에

서비스 불가 장애를 일으킬 수 있다.

<br><br>
`0.0.0.0` 은 들어오는 모든 `targetAddress` 를 의미하고, 이러한 표현식을 쓰면 오로지 `Action` 만 동작한다.

즉, 무조건적으로 누가 들어오는지 상관없이 deny 한다는 것이다.

<br><br>
이러한 특징 때문에, 광범위하게 Deny 할 수 있는 장점을 갖지만 의도치 않은 실수를 할 수 있으니

`0.0.0.0` 보다는 `*` 를 쓰는 것이 좋겠다.

`*` 는 다른 Condition 도 Check 한다.

<br><br>
다음의 Rule은,

```
# Other - Deny
#0.0.0.0/0  *  *  deny
* 10.65.34.245 8001 deny
* 10.65.34.245 8002 deny
* 10.65.34.245 8003 deny
```

그 외 허용하지 않는 여러 `targetAddress` 를 각 Instance 마다 거부하는 것이다.

<br><br>
# 3. References

[Guidelines for Writing Connection Filter Rules](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/scprg/con_filtr.html#GUID-A312878D-EC41-48DF-B318-E1E0D5A9307E)

[[WebLogic] 접근 허용 아이피 설정](https://blog.naver.com/ks900331/221897167716)

WebLogic Admin Console Shows Application in Prepared State Although the same Application can be Accessed Without any Issue (Doc ID 2778265.1)

"[Deployer:149150]An IOException Occurred While Reading the Input : with Response Code '403' : with Response Message 'Forbidden' " (Doc ID 2750004.1) 
