---
date: 2022-08-02 14:56:46 +0900
layout: post
title: "[WebTier/Apache] Http Proxy (mod_proxy+)"
tags: [WEB, OracleHTTPServer, OHS, Apache, mod_proxy, LB, Rewirterule, Loadbalaner]
typora-root-url: ..
---

# 1. 개요

Apache 에서 Forward, Reverse Proxy 사용 방법에 대해 알아보자.



# 2. Forward/Reverse Proxy

사용자의 요청을 적절한 목적지로 보내주기 위해서는 Apache와 같은 중간 전달자(Proxier)가 있어야 한다.

> Proixer 없는 단어인걸 지금 알았다, 구글 번역에서는 대리인으로 나오긴 하는데.. 어쨋든 문맥상.. 이해만..



Middleware 엔지니어가 아니라도, 이러한 개념은 어디서나 알고 사용해야 하는데,

사회 초년생 때에는 이 개념을 잡기가 너무 어려웠다.

지금도 Proxy 에 대해서 검색을 해보면, Forward(정방향)과 Reverse(역방향) Proxy 설명글이 매우 많으면서도

내가 알던 개념과 다르게 설명되어 있는 글들이 일부 있었다.

내가 쓰는 내용이 맞는 것이 아닐지라도 이해한 바는 아래와 같다.



## 2.1 Forward Proxy

(주)동현 업체에 근무하는 나는, 네이버 사이트에 접근하기 위해서는 다음 정보를 알고 있어야 한다.

- (존재할 것이므로) 외부 인터넷망에 접근할 수 있는 Windows PC
- 사이트 주소 : https://naver.com



업체는 보안이 철저하여, 외부망과의 일반적인 통신을 막아 두었고

부득이하게 외부사이트를 이용하려면 전용 PC에서 접근을 해야 한다.

- 간혹 전용 PC가 없더라도 바로 사용할 수도 있겠다..



그러면 사용자의 입력은 (주)동현 업체측에 설치되어 있는 Apache 웹서버에 전달이 된다.

* 이 글을 올리면 블로그 포스트 위치가 Apache라서 그렇지, 굳이 Apache 웹서버가 아니더라도 proxy 기능이 있는 모든 제품에 해당한다.



Apache 웹서버는 사용자의 목적지 '네이버' 에 대신(proxy) 가서, 결과값을 가져온다.

* 가져오는 리소스가 반복적이고 정적인 파일들이면 캐싱으로 반응속도/트래픽을 효율적으로 관리한다.



Forward Proxy는 내부망 에서 열린 외부망으로 가는 방향을 뜻하며, 이 과정을 Proxy 기능을 제공하는 웹서버 등이 수행한다.



## 2.2 Reverse Proxy

위에서는 (주)동현 업체에 설치된 웹서버 (정확히는 Proxy 기능을 제공하는 솔루션) 의 입장에서 살펴보았다.

여기서는 반대로 '네이버' 의 입장에서 살펴보아야 이해를 하기 수월할 것 같다.



'네이버' 측 입장에서는, 사용자(사실상 사용자 본인이 아니라, 사용자의 요청에 의해 들어온 대리인-Proxier)가

자사 시스템에 접속을 하게 된 상황이다.



네이버 로그인.. 쇼핑.. 뉴스 등 사용자가 원하는 페이지에 접속하려고 할 때마다,

해당하는 업무를 제공하는 미들웨어(보통 WAS)가 있을 것이다.

특히나 네이버의 경우는 대국민 서비스이므로 엄청나게 많은 접속자 수를 받아들이기 위해서는

수 많은 미들웨어 서버를 가지고 있을 것이다.



그러면, 접속한 사용자를 조금 더 한산한, Resource 여유가 있는 미들웨어 서버로 인도하기 위해서

네이버 웹서버가 Proxy 모듈을 사용해서 사용자를 인도할 것이다.



여기까지의 내용으로는 사용자는 다음의 정보를 알고 있어야 네이버의 미들웨어 시스템에 접근할 수 있다.

* 사이트 주소 : https://naver.com
* (알 수 없는 정보지만 네이버에 의해서 제공되는 것) 네이버 뉴스 페이지를 제공하는 미들웨어 서버의 IP Address 및 Port



Reverse Proxy는 서비스 실 제공을 담당하는 서버(여기서는 미들웨어)로 인도하는 것을 의미한다.



## 2.3 정리하자면..

Proxy는 어디에나 존재한다.

WEB 서버는 반드시 Proxy 역할을 할 수 밖에 없다. 

물론 정적 컨텐츠(HTML, img) 등을 일방적으로 제공하는 서비스라면 순수하게 WEB 서버라고 볼 수 있겠지만..



어찌되었든, 사용자의 요청을 내부에서 외부로 전달할때는 Forward.

그 반대인, 외부에서 내부로 갈때는 Reverse 라고 보면 되겠다.



좀 더 이해하기 쉽게 다르게 풀어내면,

Proxy 서버가 요청을 하는 사용자 측에 (내부망에) 있다면, Forward.

Proxy 서버가 요청을 하는 사용자와 관계없이, 외부에 있다면 Reverse Proxy 라고 이해해도 좋을 것이다.



# 3. Proxy Modules

Apache 사용자 기준에서 사용할 수 있는 관련된 Proxy 모듈들에 대해 알아보자.

기본적으로 다음의 모듈들을 친숙하게 다룰 수 있어야 한다.

* mod_jk
* mod_proxy (with RewriteRule)



모듈을 심플하게 2개만 언급하였는데, 핵심 모듈만을 언급한 것이고, 사실상

mod_proxy_balancer, mod_proxy_ajp 등등 더 많은 것을 Load 하고 사용해야 한다.



## 3.1 mod_jk

Tomcat 연결을 위해 Apache와 같은 웹서버에서 사용하는 범용적인 모듈이다.

최근 추세에는 Proxy 모듈이 일반적으로 사용되고 있어, 개인적으로도 지양하는 편이다.



httpd.conf 파일 : 모듈을 로딩하고, mod_jk 모듈 주요 옵션 설정파일을 참조하도록 한다.

```httpd.conf
LoadModule jk_module modules/mod_jk.so
Include ${SRVROOT}/conf/modjk/mod_jk.conf
```



참고로, mod_jk.so 버전은 다음처럼 확인한다.

```bash
$ strings mod_jk.so | grep -i "mod_jk"
mod_jk/1.2.46
```



mod_jk.conf 에는 mod_jk 모듈의 기본적인 옵션을 적용한다.

```mod_jk.conf
JkWorkersFile   ${SRVROOT}/conf/modjk/workers.properties
JkLogFile       "|${APACHEHOME}/bin/rotatelogs -l -L ${SRVROOT}/logs/mod_jk.log ${LOGBASE}/mod_jk.log.%Y%m%d 86400"
JkShmFile       ${SRVROOT}/logs/mod_jk.shm
JkOptions       +ForwardKeySize +ForwardURICompatUnparsed -ForwardDirectories

JkLogLevel      info
JkLogStampFormat "[%a %b %d %H:%M:%S %Y] "
JKRequestLogFormat      "%w %R %V %T %U %s"
```



다음의 worker.proeprties 내용은 방대하다.

연결할 WAS 인스턴스들을 Pool 로 구현하고, Pool 튜닝까지 지정한다.

```worker.properties
###### Define template ######
worker.template.type=ajp13

# 부하분산 1배
worker.template.lbfactor=1

# Connect mode (연결된 이후 1회 정상 여부 확인)
# Prepost mode (연결된 이후 요청 전달 시마다 정상 여부 확인되면 request 전달)
worker.template.ping_mode=CP

# milliseconds. 각 모드별 타임아웃
worker.template.connect_timeout=2000
worker.template.prepost_timeout=1000

# seconds. worker로 전달된 요청이 해당 시간내에 완료되어야 한다.
worker.template.socket_timeout=300

# milliseconds. worker->web으로 보내는 첫 패킷이 해당 시간을 넘어서면 클라이언트에게 오류를 보내고 끊는다.
# 패킷 간격에 대해서 튜닝을 하는 경우, 난해한 부분이 많기 때문에 socket_timeout과 동일하게 설정.
worker.template.reply_timeout=300000

# 중간에 방화벽이, inactive 소켓을 끊는 경우 keepalive false가 필요한 경우가 있을 수 있다.
# 방지하려면, ping_mode의 interval 을 쓸 수도 있겠다.
worker.template.socket_keepalive=false

# 최소 유지 개수
worker.template.connection_pool_minsize=2

# httpd.worker 프로세스 개수당 AJP13 연결 스레드 갯수.
# Total = (MaxClient / ThreadPerChild) * pool_size
# Total 값이 worker의 maxThreads 보다 크면,
# 초과하는 Thread에서 AJP13 을 계속 연결하려는 hang이 유발된다.
worker.template.connection_pool_size=15

# seconds. 해당 초 동안, inactive 하면 minsize 까지 줄여나간다.
worker.template.connection_pool_timeout=180

# seconds. 연결된 모든 worker를 해당 초마다, re-scan.
worker.template.maintain=60

# seconds. 오류 발생한 worker를 해당 시간동안 사용하지 않음. --> 오류라면.. 503 Service Unavailble 인듯.
# maintain 마다 re-scan 이 될때, 오류 노드의 recover_time 을 확인함.
# 1 web - 1 was 구조의 경우, maintain, recovery_time 시간을 줄이는 것이 좋다.
worker.template.recover_time=60

# worker와 communication error 발생하면, 재시도 횟수
worker.template.retries=1

# milliseconds. 재시도 간의 간격.
worker.template.retry_interval=1000

# bit연산. 7은 worker와 communcation error 발생하면, 재시도 하지 않음.
# retires 관련 옵션이 무시됨.
# 금융권 등을 예로, 중복 거래 발생할 수 있으니 이러한 failover 기능은 사용하지 않는 것이 좋다.
worker.template.recovery_options=7

#############################


##### Define Worker #####
worker.list=status, mo, api
worker.status.type=status
worker.mo.type=lb
worker.api.type=lb

# balance_workers 은 worker.list로 정의할 필요 없음.
# primary worker로 전달. worker 이름과 jvmRoute값은 동일해야함.
# primary worker 에러 발생 시, secondary worker 에서 수행 하려면 false.
# 참고. http://tomcat.apache.org/connectors-doc/common_howto/loadbalancers.html
worker.mo.balance_workers=tomcat1
worker.mo.sticky_session=true
worker.mo.sticky_session_force=false

worker.tomcat1.reference=worker.template
worker.tomcat1.host=192.168.0.16
worker.tomcat1.port=18009


worker.api.balance_workers=tomcat2
worker.api.sticky_session=true
worker.api.sticky_session_force=false

worker.tomcat2.reference=worker.template
worker.tomcat2.host=192.168.0.16
worker.tomcat2.port=28009
#########################
```

> mo 를 호출하면 tomcat1(192.16.0.16:18009) 를 프록시 하고
>
> api 를 호출하면 tomcat2(192.168.0.16:28009) 를 프록시한다.



다음처럼 VirtualHost 를 간략하게 생성하면,

각 도메인에서 발생하는 모든 요청이, 위에서 생성한 mo 또는 api 각각 서비스로 연결된다.

```httpd.conf
<VirtualHost *:80>
  ServerName mo.dhkim.co.kr

  JkMount /* mo
</VirtualHost>


<VirtualHost *:80>
  ServerName api.dhkim.co.kr

  JkMount /* api
</VirtualHost>
```



여기까지 내용만 알아도, mod_jk 로 실무는 지장이 없으나

RewriteRule 을 활용해야 하는 다양한 URL 패턴에서는 한계가 있다.

아래에서 설명할 Proxy 들을 활용해야 한다.



## 3.2 mod_proxy_ajp

mod_proxy를 먼저 설명하려 했으나, 위 mod_jk 에서 사용하는 ajp 프로토콜과 관련이 있는 내용이기 때문에

순서를 앞당겼다.



다음의 모듈들이 필요하다.

```httpd.conf
LoadModule slotmem_shm_module modules/mod_slotmem_shm.so
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_ajp_module modules/mod_proxy_ajp.so
LoadModule proxy_balancer_module modules/mod_proxy_balancer.so
LoadModule lbmethod_byrequests_module modules/mod_lbmethod_byrequests.so
```



VirtualHost를 다음과 같이 구성한다.

`3.1 mod_jk` 에서 `worker.properties` 구성과 같이 튜닝한 부분은 내용이 지저분하게 많아져 삭제했다.

튜닝은 아래 `3.3 mod_proxy_loadbalaner` 에서 소개한다.

```httpd.conf
<VirtualHost *:80>
  ServerName mo.dhkim.co.kr
  Header add Set-Cookie "ROUTEID=.%{BALANCER_WORKER_ROUTE}e; path=/" env=BALANCER_ROUTE_CHANGED
  <Proxy "balancer://mo">
      BalancerMember "ajp://192.168.0.16:18009" route=mo
      ProxySet stickysession=ROUTEID
  </Proxy>
  <Proxy "balancer://api">
      BalancerMember "ajp://192.168.0.16:28009" route=api
      ProxySet stickysession=ROUTEID
  </Proxy>
  ProxyRequests off
  ProxyPreserveHost off

  ProxyPass        /api balancer://api/
  ProxyPassReverse /api balancer://api/

  ProxyPass        / balancer://mo/
  ProxyPassReverse / balancer://mo/
</VirtualHost>


<VirtualHost *:80>
  ServerName api.dhkim.co.kr
  Header add Set-Cookie "ROUTEID=.%{BALANCER_WORKER_ROUTE}e; path=/" env=BALANCER_ROUTE_CHANGED
  <Proxy "balancer://api">
      BalancerMember "ajp://192.168.0.16:28009" route=api
      ProxySet stickysession=ROUTEID
  </Proxy>
  ProxyRequests off
  ProxyPreserveHost off

  ProxyPass        /api balancer://api/
  ProxyPassReverse /api balancer://api/
</VirtualHost>
```



위 내용을 잘 보면, VirtualHost Section마다 'balancer' 가 있다. (mod_proxy_balaner.so 필요)

이 balaner를 호출하면, Request를 LB가 처리하듯 한다.



`mo.dhkim.co.kr/api` 를 호출하면, `balancer://api` 에 의해, `192.168.0.16:28009` 가 서비스를 처리한다.

`api.dhkim.co.kr/api` 를 호출해도 마찬가지이다.



이 부분을 설명하는 이유는,

mo.dhkim.co.kr VirtualHost Section 내에서 `3.1 mod_jk` 방식만을 이용해서는,

같은 Context-Root 를 가리키는 서비스를 호출/분배할 수가 없다는걸 설명하기 위해서다



자료를 찾아보니, [Redhat 자료](https://access.redhat.com/solutions/29660) 또는 [구글링](https://stackoverflow.com/questions/5404024/how-to-use-mod-rewrite-with-apache-mod-jk-tomcat-setup) 와 같이 PT(Passthrough Flag)를 이용하는 방법이 나와 있지만,

역시나 Context-Root 가 동일하면 이를 분리할 수가 없어 보인다.



여기까지 내용으로는, mod_jk 만으로도 AJP 로드밸런서를 만들 수 있지만, WAS 풀만을 의미하고,

balancer까지 이용하면 더 강력한 로드밸런서를 만들 수 있음을 알 수 있겠다.





## 3.3 mod_proxy_loadbalaner

위에서 언급한 튜닝 부분을 여기서 언급하기로 했는데..

역시나 내용이 길어 [여기](https://blog.naver.com/ks900331/222303166071) 링크에서 보여주기로 한다.



다음의 모듈이 필요하다.

```httpd.conf
LoadModule slotmem_shm_module modules/mod_slotmem_shm.so
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
LoadModule proxy_balancer_module modules/mod_proxy_balancer.so
LoadModule lbmethod_byrequests_module modules/mod_lbmethod_byrequests.so
```



VirtualHost 설정

```httpd.conf
<VirtualHost *:80>
  ServerName mo.dhkim.co.kr
  Header add Set-Cookie "ROUTEID=.%{BALANCER_WORKER_ROUTE}e; path=/" env=BALANCER_ROUTE_CHANGED
  <Proxy "balancer://mo">
      BalancerMember "http://192.168.0.16:18080" route=mo
      ProxySet stickysession=ROUTEID
  </Proxy>
  ProxyRequests off
  ProxyPreserveHost off

  ProxyPass        / balancer://mo/
  ProxyPassReverse / balancer://mo/
</VirtualHost>


<VirtualHost *:80>
  ServerName api.dhkim.co.kr
  Header add Set-Cookie "ROUTEID=.%{BALANCER_WORKER_ROUTE}e; path=/" env=BALANCER_ROUTE_CHANGED
  <Proxy "balancer://api">
      BalancerMember "http://192.168.0.16:28080" route=api
      ProxySet stickysession=ROUTEID
  </Proxy>
  ProxyRequests off
  ProxyPreserveHost off

  ProxyPass        /api balancer://api/
  ProxyPassReverse /api balancer://api/
</VirtualHost>
```



AJP 에서 한것과 크게 다른것이 없어, 더 이상의 설명은 생략한다.
