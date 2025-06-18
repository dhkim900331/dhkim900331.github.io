---
date: 2025-06-18 14:55:42 +0900
layout: post
title: "[WebLogic/LDAP] Troubleshooting with WebLogic and External LDAP"
tags: [Middleware, WebLogic, LDAP]
typora-root-url: ..
---

# 1. Overview

WebLogic 12cR2 (12.2.1.4) 에서 Embedded LDAP 이 아닌, External LDAP Server 연결을 위해 기본 구성 가이드와

구성 이후 몇가지 Debugging Test Case를 진행하여 WebLogic의 LDAP Procedure 이해도를 높인다.

<br><br>


# 2. Descriptions

## 2.1 Apache Directory Server 구성

[Apache DS](https://directory.apache.org/) 최신 버전 (당시 ApacheDS 2.0.0.AM27)를 설치.

JDK 11 버전 이상도 요구된다.

<br>

Apache DS 실행 후, Ctrl + E 또는 LDAP Server 패널에서 New Server로 'ApacheDS 2.0.0' 를 생성한다.

IP Address와 Port만 정의하면 된다.

여기서는 ADDR:10389 로 Apache DS를 Socket Bind 하도록 구성했다.

<br>

LDAP Browser에서 다음의 구조로 생성한다.

```
dc=example,dc=com
 > ou=groups
   > cn=weblogic-admins
     > uniqueMember=uid=testuser1,ou=people,dc=example,dc=com
 > ou=people
   > uid=testuser1
     > cn=Test User
     > sn=User
     > uid=testuser1
     > userPassword=<패스워드> (SSHA Encryption)
```

<br>

간단히, LDAP Servers 패널에서 Start,Stop 제어


<br><br>


## 2.2 WebLogic LDAP Configurations

Security Realm - myrealm - Providers - Authentication - New

- Name : ApacheDSAuthenticator

- Type : LDAPAuthenticator

<br>

ApacheDSAuthenticator - Configuration - Provider Specific

- Host : Apache DS Addr
- Port : Apache DS Port
- Principal : uid=admin,ou=system
  - Apache DS에 접속하는데 사용되는 고유이름(Distinguished Name (DN))
- Credential : secret
  - Apache DS의 LDAP 초기 비밀번호 'secret' 이다.
  - 의도적인지 모르겠지만, 'ApacheDSAuthenticator' 설정을 변경하여 적용 시마다 재입력해줘야 한다.
- User Base DN : ou=people,dc=example,dc=com
- All Users Filter : (&(objectClass=inetOrgPerson))
- User From Name Filter : (&(uid=%u)(objectClass=inetOrgPerson))
- Group Base DN : ou=groups,dc=example,dc=com
- All Groups Filter : (&(objectClass=groupOfUniqueNames))
- Group From Name Filter : (&(cn=%g)(objectClass=groupOfUniqueNames))
- Group Membership Searching : limited
- Max Group Membership Search Level : 1
- Static Group Object Class : groupOfUniqueNames
- Static Member DN Attribute : uniqueMember
- Static Group DNs from Member DN Filter : (&(uniquemember=%M)(objectclass=groupofuniquenames))

위와 같이 설정 하면 되나, 검토는 GPT 통해서 하길...


<br><br>


## 2.3 Troubleshooting with test cases

WebLogic debug: security: atn (All enabled) 로 debugging 을 하며 여러가지 상황에 대해 테스트 한다.

설정 값 일부를 변경하고, LDAP Server의 상태를 변경해가며 debugging 로그를 통해 동작 흐름을 이해 한다.


<br><br>


***WebLogic에 구성된 LDAP Provider의 Connection 옵션을 다음과 같이 조정한다.***

```
Connection Pool Size: 1
Connect Timeout: 30
Connection Retry Limit:	0
Results Time Limit:	10000
```

> 이 옵션들은 변경 시 즉시 재적용된다고 나와있지만, 테스트 결과 WebLogic을 재기동 해야 한다.

> 예상으로는, MBean은 즉시 적용이지만 In-use connection 등에서는 적용되지 않으므로 재기동을 해야 하는게 아닌지.


<br><br>


***WebLogic 기동 시 LDAP Server 와 초기 연결 시도 시점의 Debug log***

```
<2025. 6. 17 오후 12시 06분 32,788초 KST> <Notice> <Security> <BEA-090946> <Security pre-initializing using security realm: myrealm>
...
<2025. 6. 17 오후 12시 06분 33,136초 KST> <Debug> <SecurityAtn> <BEA-000000> <Initialized LDAP authentication>
<2025. 6. 17 오후 12시 06분 33,137초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 06분 33,141초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 06분 33,154초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 06분 33,165초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 06분 33,281초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection succeeded>
<2025. 6. 17 오후 12시 06분 33,281초 KST> <Debug> <SecurityAtn> <BEA-000000> <getConnection return conn:LDAPConnection {ldaps://10.73.139.210:10389 ldapVersion:3 bindDN:"uid=admin,ou=system"}>
<2025. 6. 17 오후 12시 06분 33,475초 KST> <Debug> <SecurityAtn> <BEA-000000> <returnConnection conn:LDAPConnection {ldaps://10.73.139.210:10389 ldapVersion:3 bindDN:"uid=admin,ou=system"}>
<2025. 6. 17 오후 12시 06분 33,476초 KST> <Debug> <SecurityAtn> <BEA-000000> <Group case sensitivity is false>
<2025. 6. 17 오후 12시 06분 33,477초 KST> <Debug> <SecurityAtn> <BEA-000000> <Group membership hierarchy caching is enabled 100>
<2025. 6. 17 오후 12시 06분 33,478초 KST> <Debug> <SecurityAtn> <BEA-000000> <com.bea.common.security.internal.legacy.service.PrincipalValidationProviderImpl.init>
<2025. 6. 17 오후 12시 06분 33,478초 KST> <Debug> <SecurityAtn> <BEA-000000> <Creating principal validator>
<2025. 6. 17 오후 12시 06분 33,479초 KST> <Debug> <SecurityAtn> <BEA-000000> <Principal validator cache enabled: true>
<2025. 6. 17 오후 12시 06분 33,479초 KST> <Debug> <SecurityAtn> <BEA-000000> <Principal validator cache size: 500>
<2025. 6. 17 오후 12시 06분 33,482초 KST> <Debug> <SecurityAtn> <BEA-000000> <Default Authentication loading LDIF template>
<2025. 6. 17 오후 12시 06분 33,499초 KST> <Debug> <SecurityAtn> <BEA-000000> <Looking for C:\sw\weblogic\12cR2\domains\base_domain\servers\AdminServer\data\ldap\DefaultAuthenticatormyrealmInit.initialized>
<2025. 6. 17 오후 12시 06분 33,503초 KST> <Debug> <SecurityAtn> <BEA-000000> <Found C:\sw\weblogic\12cR2\domains\base_domain\servers\AdminServer\data\ldap\DefaultAuthenticatormyrealmInit.initialized>
<2025. 6. 17 오후 12시 06분 33,503초 KST> <Debug> <SecurityAtn> <BEA-000000> <Authenticator version 41>
<2025. 6. 17 오후 12시 06분 33,504초 KST> <Debug> <SecurityAtn> <BEA-000000> <Authenticator is up to date at version 41.>
<2025. 6. 17 오후 12시 06분 33,505초 KST> <Info> <Security> <BEA-090516> <The Authenticator provider has pre-existing LDAP data.>
```

> 아래에서 반복적으로 debug log를 살펴볼 것이므로, 그전에 기본적인 표준 동작 흐름의 debug log를 소개했다.


<br><br>


***LDAP 계정 'testuser1' 로 console 로그인 시, 일반적인 debug log***

```
<2025. 6. 17 오후 12시 07분 32,019초 KST> <Debug> <SecurityAtn> <BEA-000000> <com.bea.common.security.internal.service.CallbackHandlerWrapper.handle got username from callbacks[0], UserName=testuser1>
<2025. 6. 17 오후 12시 07분 32,019초 KST> <Debug> <SecurityAtn> <BEA-000000> <LDAP Atn Login username: testuser1>
<2025. 6. 17 오후 12시 07분 32,019초 KST> <Debug> <SecurityAtn> <BEA-000000> <authenticate user:testuser1>
<2025. 6. 17 오후 12시 07분 32,023초 KST> <Debug> <SecurityAtn> <BEA-000000> <getConnection return conn:LDAPConnection {ldaps://10.73.139.210:10389 ldapVersion:3 bindDN:"uid=admin,ou=system"}>
<2025. 6. 17 오후 12시 07분 32,026초 KST> <Debug> <SecurityAtn> <BEA-000000> <getDNForUser search("ou=people,dc=example,dc=com", "(&(uid=testuser1)(objectClass=inetOrgPerson))", base DN & below)>
<2025. 6. 17 오후 12시 07분 32,078초 KST> <Debug> <SecurityAtn> <BEA-000000> <DN for user testuser1: uid=testuser1,ou=people,dc=example,dc=com>
<2025. 6. 17 오후 12시 07분 32,079초 KST> <Debug> <SecurityAtn> <BEA-000000> <returnConnection conn:LDAPConnection {ldaps://10.73.139.210:10389 ldapVersion:3 bindDN:"uid=admin,ou=system"}>
<2025. 6. 17 오후 12시 07분 32,079초 KST> <Debug> <SecurityAtn> <BEA-000000> <authenticate user:testuser1 with DN:uid=testuser1,ou=people,dc=example,dc=com>
<2025. 6. 17 오후 12시 07분 32,096초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 07분 32,107초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 07분 32,108초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 07분 32,109초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 07분 32,138초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection succeeded>
<2025. 6. 17 오후 12시 07분 32,138초 KST> <Debug> <SecurityAtn> <BEA-000000> <getConnection return conn:LDAPConnection {ldaps://10.73.139.210:10389 ldapVersion:3 bindDN:"uid=admin,ou=system"}>
<2025. 6. 17 오후 12시 07분 32,141초 KST> <Debug> <SecurityAtn> <BEA-000000> <authentication succeeded>
```

> ㅣLDAP Server에 connection을 만들고, 그것을 통해 조회를 수행하고 인증에 성공한다.


<br><br>


***LDAP Server shutdown 시 로그인 시도는, connect 가 안되므로 즉시 실패***

```
<2025. 6. 17 오후 12시 10분 18,400초 KST> <Debug> <SecurityAtn> <BEA-000000> <com.bea.common.security.internal.service.CallbackHandlerWrapper.handle got username from callbacks[0], UserName=testuser1>
<2025. 6. 17 오후 12시 10분 18,400초 KST> <Debug> <SecurityAtn> <BEA-000000> <LDAP Atn Login username: testuser1>
<2025. 6. 17 오후 12시 10분 18,400초 KST> <Debug> <SecurityAtn> <BEA-000000> <authenticate user:testuser1>
<2025. 6. 17 오후 12시 10분 18,400초 KST> <Debug> <SecurityAtn> <BEA-000000> <getConnection return conn:LDAPConnection {ldaps://10.73.139.210:10389 ldapVersion:3 bindDN:"uid=admin,ou=system"}>
<2025. 6. 17 오후 12시 10분 18,400초 KST> <Debug> <SecurityAtn> <BEA-000000> <getDNForUser search("ou=people,dc=example,dc=com", "(&(uid=testuser1)(objectClass=inetOrgPerson))", base DN & below)>
<2025. 6. 17 오후 12시 10분 18,401초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 10분 20,441초 KST> <Warning> <Security> <BEA-099117> <The LDAP authentication provider named "ApacheDSAuthenticator" failed to make a connection to LDAP server at ldap://10.73.139.210:10,389, the error cause is: Connection refused: connect.>
<2025. 6. 17 오후 12시 10분 20,446초 KST> <Debug> <SecurityAtn> <BEA-000000> <destroy LDAP connection LDAPConnection {ldaps://10.73.139.210:10389 ldapVersion:3 bindDN:"uid=testuser1,ou=people,dc=example,dc=com"}>
<2025. 6. 17 오후 12시 10분 20,451초 KST> <Debug> <SecurityAtn> <BEA-000000> <[Security:090294]could not get connection>
<2025. 6. 17 오후 12시 10분 20,454초 KST> <Debug> <SecurityAtn> <BEA-000000> <weblogic.security.providers.authentication.LDAPAtnLoginModuleImpl.login exception:
java.security.PrivilegedActionException: weblogic.security.providers.authentication.LoginServerUnavailableException: Connection refused: connect
...
Caused By: weblogic.security.providers.authentication.LoginServerUnavailableException: Connection refused: connect
```

> LDAP Server를 중지(shutdown) 한 뒤, 로그인을 시도하면 socket 단계에서 connect 되지 않으므로 즉시 실패한다.


<br><br>


***LDAP Server process를 MS의 Process Explorer로 Suspending 하고 로그인 시도 시 'Client Timelimit exceeded' 으로 실패, 대략 'Results Time Limit' 과 유사***

```
<2025. 6. 17 오후 12시 11분 39,858초 KST> <Debug> <SecurityAtn> <BEA-000000> <com.bea.common.security.internal.service.CallbackHandlerWrapper.handle got username from callbacks[0], UserName=testuser1>
<2025. 6. 17 오후 12시 11분 39,858초 KST> <Debug> <SecurityAtn> <BEA-000000> <LDAP Atn Login username: testuser1>
<2025. 6. 17 오후 12시 11분 39,858초 KST> <Debug> <SecurityAtn> <BEA-000000> <authenticate user:testuser1>
<2025. 6. 17 오후 12시 11분 39,859초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 11분 39,859초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 11분 39,868초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 11분 39,874초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 11분 50,385초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Time to complete operation exceeded (85); Client Timelimit exceeded>
<2025. 6. 17 오후 12시 11분 50,385초 KST> <Debug> <SecurityAtn> <BEA-000000> <getConnection return conn:null>
<2025. 6. 17 오후 12시 11분 50,385초 KST> <Debug> <SecurityAtn> <BEA-000000> <getDNForUser search("ou=people,dc=example,dc=com", "(&(uid=testuser1)(objectClass=inetOrgPerson))", base DN & below)>
<2025. 6. 17 오후 12시 11분 50,386초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 11분 50,386초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 11분 50,386초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 11분 50,387초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 12분 00,906초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Time to complete operation exceeded (85); Client Timelimit exceeded>
<2025. 6. 17 오후 12시 12분 00,907초 KST> <Debug> <SecurityAtn> <BEA-000000> <getConnection return conn:null>
```

> Results Time Limit 옵션은 위에서 10000(10초) 설정했었다.


<br><br>


***Results Time Limit=20000(20초) , Connection Retry Limit=5 설정***

***LDAP Server와 연결이 되지만 20초 이내 응답을 받지 못하면, 아래처럼 옵션만큼 재시도한다.***

***5 X 20초 의 수행 시간***

```
<2025. 6. 17 오후 12시 36분 32,051초 KST> <Debug> <SecurityAtn> <BEA-000000> <Initialized LDAP authentication>
<2025. 6. 17 오후 12시 36분 32,055초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 36분 32,073초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 36분 32,077초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 36분 32,084초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 36분 52,606초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Time to complete operation exceeded (85); Client Timelimit exceeded>

<2025. 6. 17 오후 12시 36분 52,606초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 36분 52,606초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 36분 52,608초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 36분 52,615초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 37분 13,144초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Time to complete operation exceeded (85); Client Timelimit exceeded>

<2025. 6. 17 오후 12시 37분 13,146초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 37분 13,146초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 37분 13,148초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 37분 13,154초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 37분 33,670초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Time to complete operation exceeded (85); Client Timelimit exceeded>

<2025. 6. 17 오후 12시 37분 33,672초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 37분 33,674초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 37분 33,697초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 37분 33,699초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 37분 54,209초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Time to complete operation exceeded (85); Client Timelimit exceeded>

<2025. 6. 17 오후 12시 37분 54,209초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 37분 54,212초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 37분 54,212초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 37분 54,231초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 38분 14,746초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Time to complete operation exceeded (85); Client Timelimit exceeded>
<2025. 6. 17 오후 12시 38분 14,769초 KST> <Debug> <SecurityAtn> <BEA-000000> <Unable to determine group case sensitivity from schema, defaulting to case sensitive caching>
```

<br>

***Results Time Limit=20000(20초) , Connection Retry Limit=5 설정***

***바로 위 장애 재현한 케이스를 해제하기 위하여 LDAP Server를 Resume하고 testuser1 로 로그인을 성공시킨다.***

> 그러면 여기 단계에서, connection이 만들어져있다.

<br>

***다시 Suspend 하고, 로그아웃 및 로그인을 시도하면 기존에 가지고 있던 getConnection으로 반환된 객체를 사용하지만, 20초 초과하여 실패한다.***

***실패 이후, 재시도 하는 단계는 없다. 즉 Connection Retry Limit은 초기 connection이 없는 init 단계에서 적용된다.***

```
<2025. 6. 17 오후 12시 42분 07,724초 KST> <Debug> <SecurityAtn> <BEA-000000> <com.bea.common.security.internal.service.CallbackHandlerWrapper.handle got username from callbacks[0], UserName=testuser1>
<2025. 6. 17 오후 12시 42분 07,724초 KST> <Debug> <SecurityAtn> <BEA-000000> <LDAP Atn Login username: testuser1>
<2025. 6. 17 오후 12시 42분 07,725초 KST> <Debug> <SecurityAtn> <BEA-000000> <authenticate user:testuser1>
<2025. 6. 17 오후 12시 42분 07,725초 KST> <Debug> <SecurityAtn> <BEA-000000> <getConnection return conn:LDAPConnection {ldaps://10.73.139.210:10389 ldapVersion:3 bindDN:"uid=admin,ou=system"}>
<2025. 6. 17 오후 12시 42분 07,725초 KST> <Debug> <SecurityAtn> <BEA-000000> <DN for user testuser1: uid=testuser1,ou=people,dc=example,dc=com>
<2025. 6. 17 오후 12시 42분 07,738초 KST> <Debug> <SecurityAtn> <BEA-000000> <returnConnection conn:LDAPConnection {ldaps://10.73.139.210:10389 ldapVersion:3 bindDN:"uid=admin,ou=system"}>
<2025. 6. 17 오후 12시 42분 07,744초 KST> <Debug> <SecurityAtn> <BEA-000000> <authenticate user:testuser1 with DN:uid=testuser1,ou=people,dc=example,dc=com>
<2025. 6. 17 오후 12시 42분 07,748초 KST> <Debug> <SecurityAtn> <BEA-000000> <getConnection return conn:LDAPConnection {ldaps://10.73.139.210:10389 ldapVersion:3 bindDN:"uid=testuser1,ou=people,dc=example,dc=com"}>
<2025. 6. 17 오후 12시 42분 28,279초 KST> <Debug> <SecurityAtn> <BEA-000000> <destroy LDAP connection LDAPConnection {ldaps://10.73.139.210:10389 ldapVersion:3 bindDN:"uid=admin,ou=system"}>
<2025. 6. 17 오후 12시 42분 28,790초 KST> <Debug> <SecurityAtn> <BEA-000000> <[Security:090294]could not get connection>
<2025. 6. 17 오후 12시 42분 28,790초 KST> <Debug> <SecurityAtn> <BEA-000000> <weblogic.security.providers.authentication.LDAPAtnLoginModuleImpl.login exception:
java.security.PrivilegedActionException: weblogic.security.providers.authentication.LoginServerUnavailableException: Time to complete operation exceeded
Caused By: weblogic.security.providers.authentication.LoginServerUnavailableException: Time to complete operation exceeded
```

> 이를 뒷바침하는 근거로, **Connect Timeout** 옵션의 설명 문구로 'Specifies the number of times to attempt to connect to the LDAP server if the initial connection failed.'


<br><br>


***Results Time Limit=20000(20초) , Connection Retry Limit=5 설정***

***WebLogic 재기동 이후로, weblogic 계정으로 로그인 하였던 적이 없는 상황에서, weblogic 계정으로 로그인을 처음 시도한다.***

***weblogic 계정에 대한 LDAP connection이 없어, connection 생성을 최초 시도하는데,***

***LDAP Server로 부터 제때 응답을 받지 못하여, 이전에 보았던 사례처럼 옵션만큼 재시도 후 실패한다.***

```
<2025. 6. 17 오후 12시 45분 41,917초 KST> <Debug> <SecurityAtn> <BEA-000000> <com.bea.common.security.internal.service.CallbackHandlerWrapper.handle got username from callbacks[0], UserName=weblogic>
<2025. 6. 17 오후 12시 45분 41,917초 KST> <Debug> <SecurityAtn> <BEA-000000> <LDAP Atn Login username: weblogic>
<2025. 6. 17 오후 12시 45분 41,917초 KST> <Debug> <SecurityAtn> <BEA-000000> <authenticate user:weblogic>
<2025. 6. 17 오후 12시 45분 41,917초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 45분 41,917초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 45분 41,919초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 45분 41,920초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 46분 02,444초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Time to complete operation exceeded (85); Client Timelimit exceeded>

<2025. 6. 17 오후 12시 46분 02,444초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 46분 02,444초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 46분 02,446초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 46분 02,446초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 46분 22,955초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Time to complete operation exceeded (85); Client Timelimit exceeded>

<2025. 6. 17 오후 12시 46분 22,955초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 46분 22,955초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 46분 22,955초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 46분 22,955초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 46분 43,472초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Time to complete operation exceeded (85); Client Timelimit exceeded>

<2025. 6. 17 오후 12시 46분 43,478초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 46분 43,478초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 46분 43,480초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 46분 43,480초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 46분 52,622초 KST> <Info> <WorkManager> <BEA-002959> <Self-tuning thread pool contains 1 running threads, 2 idle threads, and 10 standby threads>
<2025. 6. 17 오후 12시 47분 03,986초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Time to complete operation exceeded (85); Client Timelimit exceeded>

<2025. 6. 17 오후 12시 47분 03,988초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 47분 03,988초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 47분 03,989초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 47분 03,990초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 47분 24,504초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Time to complete operation exceeded (85); Client Timelimit exceeded>
<2025. 6. 17 오후 12시 47분 24,504초 KST> <Debug> <SecurityAtn> <BEA-000000> <[Security:090294]could not get connection>
```

> 바로 이전 테스트 에서 언급한대로 Init connection creation 단계이므로 여러번 시도 된 것이다.

<br>

***(위의 내용에 이어서)***

***하지만 weblogic 계정은, 원래 부터 Embedded LDAP에 있으므로 로그인에 성공하여, connection 생성을 성공한다.***

***WebLogic Provider 우선순위에서 LDAP Server가 가장 높아 외부 Server에서 우선 검색한 것이고, 모든 재시도 작업이 끝난 후 그 다음 우선순위인 Embedded LDAP 에서 완료된 것이다.***

```<2025. 6. 17 오후 12시 47분 24,507초 KST> <Debug> <SecurityAtn> <BEA-000000> <com.bea.common.security.internal.service.CallbackHandlerWrapper.handle did not get username or IDD user from a callback>
<2025. 6. 17 오후 12시 47분 24,507초 KST> <Debug> <SecurityAtn> <BEA-000000> <LDAP Atn Login username: weblogic>
<2025. 6. 17 오후 12시 47분 24,507초 KST> <Debug> <SecurityAtn> <BEA-000000> <authenticate user:weblogic>
<2025. 6. 17 오후 12시 47분 24,507초 KST> <Debug> <SecurityAtn> <BEA-000000> <getConnection return conn:LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 47분 24,507초 KST> <Debug> <SecurityAtn> <BEA-000000> <getDNForUser search("ou=people,ou=myrealm,dc=base_domain", "(&(uid=weblogic)(objectclass=person))", base DN & below)>
<2025. 6. 17 오후 12시 47분 24,510초 KST> <Debug> <SecurityAtn> <BEA-000000> <Retrieved guid:0DA922724B1511F0AF1E83C75D537E0F>
<2025. 6. 17 오후 12시 47분 24,511초 KST> <Debug> <SecurityAtn> <BEA-000000> <DN for user weblogic: uid=weblogic,ou=people,ou=myrealm,dc=base_domain>
<2025. 6. 17 오후 12시 47분 24,512초 KST> <Debug> <SecurityAtn> <BEA-000000> <returnConnection conn:LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 47분 24,512초 KST> <Debug> <SecurityAtn> <BEA-000000> <authenticate user:weblogic with DN:uid=weblogic,ou=people,ou=myrealm,dc=base_domain>
<2025. 6. 17 오후 12시 47분 24,512초 KST> <Debug> <SecurityAtn> <BEA-000000> <getConnection return conn:LDAPConnection { ldapVersion:2 bindDN:""}>
```


<br><br>


***Results Time Limit=0(무한대) 설정***

***WebLogic 재기동 시, LDAP Server에 연결이 되어도 응답을 받지 못하면 무한대로 기다리느라 재기동 중 Stuck***

```
<2025. 6. 17 오후 12시 52분 22초 KST> <Notice> <WebLogicServer> <BEA-000365> <Server state changed to STARTING.>
...
<2025. 6. 17 오후 12시 52분 23,736초 KST> <Debug> <SecurityAtn> <BEA-000000> <Created LDAPAtnDelegate = LDAPAtnDelegate: null, realm = null
		user: person,uid,null
		userDN: ou=people,dc=example,dc=com, scope: subtree
		userFilters: (&(uid=%u)(objectClass=inetOrgPerson)) ,(&(objectClass=inetOrgPerson))
		groupDN: ou=groups,dc=example,dc=com, scope: subtree
		groupFilters: (&(cn=%g)(objectClass=groupOfUniqueNames)) ,(&(objectClass=groupOfUniqueNames))
		sgroup: groupOfUniqueNames,cn,uniqueMember
		sgroupFilters: (&(uniquemember=%M)(objectclass=groupofuniquenames))
		dgroup: null,null,null
com.bea.common.security.utils.LDAPServerInfo@41dbdbb0>
<2025. 6. 17 오후 12시 52분 23,739초 KST> <Debug> <SecurityAtn> <BEA-000000> <Initialized LDAP authentication>
<2025. 6. 17 오후 12시 52분 23,739초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 12시 52분 23,745초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 12시 52분 23,749초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 12시 52분 23,784초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
```


<br><br>


***Results Time Limit=0(무한대), Connection Retry Limit=5 설정***

***LDAP Server를 shutdown 하여 connect 조차 되지 못하게 하였고,***

***weblogic 또는 testuser1 접속 시 External LDAP(Apache DS) 우선순위가 가장 높게 설정되어 있어, 항상 LDAP Server를 먼저 검색하려고 한다.***

***LDAP Server와 연결 되지 않아, 옵션 만큼 재시도하는 로그가 확인된다.***

```
<2025. 6. 17 오후 1시 00분 37,384초 KST> <Debug> <SecurityAtn> <BEA-000000> <com.bea.common.security.internal.service.CallbackHandlerWrapper.handle got username from callbacks[0], UserName=testuser1>
<2025. 6. 17 오후 1시 00분 37,384초 KST> <Debug> <SecurityAtn> <BEA-000000> <LDAP Atn Login username: testuser1>
<2025. 6. 17 오후 1시 00분 37,384초 KST> <Debug> <SecurityAtn> <BEA-000000> <authenticate user:testuser1>
<2025. 6. 17 오후 1시 00분 37,384초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 1시 00분 37,384초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 1시 00분 37,385초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 1시 00분 39,425초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Connection refused: connect (91); Cannot connect to the LDAP server>
<2025. 6. 17 오후 1시 00분 39,426초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 1시 00분 39,426초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 1시 00분 39,427초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 1시 00분 41,466초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Connection refused: connect (91); Cannot connect to the LDAP server>
<2025. 6. 17 오후 1시 00분 41,466초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 1시 00분 41,466초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 1시 00분 41,468초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 1시 00분 43,502초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Connection refused: connect (91); Cannot connect to the LDAP server>
<2025. 6. 17 오후 1시 00분 43,502초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 1시 00분 43,502초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 1시 00분 43,502초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 1시 00분 44,501초 KST> <Info> <WorkManager> <BEA-002959> <Self-tuning thread pool contains 1 running threads, 1 idle threads, and 10 standby threads>
<2025. 6. 17 오후 1시 00분 45,536초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Connection refused: connect (91); Cannot connect to the LDAP server>
<2025. 6. 17 오후 1시 00분 45,536초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 1시 00분 45,536초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 1시 00분 45,538초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 1시 00분 47,576초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Connection refused: connect (91); Cannot connect to the LDAP server>
<2025. 6. 17 오후 1시 00분 47,576초 KST> <Debug> <SecurityAtn> <BEA-000000> <[Security:090294]could not get connection>
```

> 또 한번 언급하지만, Init connection creation 단계이므로 옵션만큼 재시도 한것이다.


<br><br>


***Results Time Limit=0(무한대), Connection Retry Limit=5 설정***

***LDAP 을 정상적인 상황에서 다음처럼 로그인 시, connection이 생성된다.***

```
<2025. 6. 17 오후 1시 05분 18,411초 KST> <Debug> <SecurityAtn> <BEA-000000> <com.bea.common.security.internal.service.CallbackHandlerWrapper.handle got username from callbacks[0], UserName=testuser1>
<2025. 6. 17 오후 1시 05분 18,411초 KST> <Debug> <SecurityAtn> <BEA-000000> <LDAP Atn Login username: testuser1>
<2025. 6. 17 오후 1시 05분 18,411초 KST> <Debug> <SecurityAtn> <BEA-000000> <authenticate user:testuser1>
<2025. 6. 17 오후 1시 05분 18,411초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 1시 05분 18,411초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 1시 05분 18,412초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 1시 05분 18,412초 KST> <Debug> <SecurityAtn> <BEA-000000> <Successfully connected to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 1시 05분 18,452초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection succeeded>
```

<br>

***(위에 이어서) 'getConnection' 에서 return 받은 connection을 가지고 인증을 수행하는데, 실패하여 'destroy LDAP connection LDAPConnection'.***

***LDAP과 연결 자체가 되지 않으므로, 'Results Time Limit' 은 적용되지 않았고,***

***새로운 Connection을 만드는 단계가 아니라 이전에 사용된 Connection을 재활용하여 시도하므로 'Connection Retry Limit' 또한 적용되지 않은 것으로 보인다.***

```
<2025. 6. 17 오후 1시 06분 36,565초 KST> <Debug> <SecurityAtn> <BEA-000000> <com.bea.common.security.internal.service.CallbackHandlerWrapper.handle got username from callbacks[0], UserName=testuser1>
<2025. 6. 17 오후 1시 06분 36,565초 KST> <Debug> <SecurityAtn> <BEA-000000> <LDAP Atn Login username: testuser1>
<2025. 6. 17 오후 1시 06분 36,565초 KST> <Debug> <SecurityAtn> <BEA-000000> <authenticate user:testuser1>
<2025. 6. 17 오후 1시 06분 36,565초 KST> <Debug> <SecurityAtn> <BEA-000000> <getConnection return conn:LDAPConnection {ldaps://10.73.139.210:10389 ldapVersion:3 bindDN:"uid=admin,ou=system"}>
<2025. 6. 17 오후 1시 06분 36,565초 KST> <Debug> <SecurityAtn> <BEA-000000> <getDNForUser search("ou=people,dc=example,dc=com", "(&(uid=testuser1)(objectClass=inetOrgPerson))", base DN & below)>
<2025. 6. 17 오후 1시 06분 36,572초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 1시 06분 38,613초 KST> <Debug> <SecurityAtn> <BEA-000000> <destroy LDAP connection LDAPConnection {ldaps://10.73.139.210:10389 ldapVersion:3 bindDN:"uid=testuser1,ou=people,dc=example,dc=com"}>
<2025. 6. 17 오후 1시 06분 38,613초 KST> <Debug> <SecurityAtn> <BEA-000000> <[Security:090294]could not get connection>
```

<br>

***(위에 이어서) 여전히 LDAP Server와 연결이 되지 않는 위 환경에서, 다시 로그인을 반복 시도하면***

***이미 파괴된 connection 이후라 아무것도 없으므로 다시 Conenction을 최초 만드는 단계에서 시작된다.***

***그로 인해, 옵션만큼 재시도 하는 현상이 관찰된다.***

```
<2025. 6. 17 오후 1시 09분 10,440초 KST> <Debug> <SecurityAtn> <BEA-000000> <com.bea.common.security.internal.service.CallbackHandlerWrapper.handle got username from callbacks[0], UserName=testuser1>
<2025. 6. 17 오후 1시 09분 10,440초 KST> <Debug> <SecurityAtn> <BEA-000000> <LDAP Atn Login username: testuser1>
<2025. 6. 17 오후 1시 09분 10,440초 KST> <Debug> <SecurityAtn> <BEA-000000> <authenticate user:testuser1>
<2025. 6. 17 오후 1시 09분 10,440초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 1시 09분 10,441초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 1시 09분 10,441초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 1시 09분 12,473초 KST> <Warning> <Security> <BEA-099117> <The LDAP authentication provider named "ApacheDSAuthenticator" failed to make a connection to LDAP server at ldap://10.73.139.210:10,389, the error cause is: Connection refused: connect.>
<2025. 6. 17 오후 1시 09분 12,477초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Connection refused: connect (91); Cannot connect to the LDAP server>

<2025. 6. 17 오후 1시 09분 12,479초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 1시 09분 12,479초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 1시 09분 12,480초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 1시 09분 14,526초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Connection refused: connect (91); Cannot connect to the LDAP server>

<2025. 6. 17 오후 1시 09분 14,528초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 1시 09분 14,528초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 1시 09분 14,528초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 1시 09분 16,572초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Connection refused: connect (91); Cannot connect to the LDAP server>

<2025. 6. 17 오후 1시 09분 16,572초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 1시 09분 16,572초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 1시 09분 16,572초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 1시 09분 18,602초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Connection refused: connect (91); Cannot connect to the LDAP server>

<2025. 6. 17 오후 1시 09분 18,602초 KST> <Debug> <SecurityAtn> <BEA-000000> <new LDAP connection to host 10.73.139.210 port 10389 use local connection is false>
<2025. 6. 17 오후 1시 09분 18,602초 KST> <Debug> <SecurityAtn> <BEA-000000> <created new LDAP connection LDAPConnection { ldapVersion:2 bindDN:""}>
<2025. 6. 17 오후 1시 09분 18,602초 KST> <Debug> <SecurityAtn> <BEA-000000> <Connecting to host=10.73.139.210, port=10389>
<2025. 6. 17 오후 1시 09분 20,636초 KST> <Debug> <SecurityAtn> <BEA-000000> <connection failed netscape.ldap.LDAPException: Connection refused: connect (91); Cannot connect to the LDAP server>
<2025. 6. 17 오후 1시 09분 20,636초 KST> <Debug> <SecurityAtn> <BEA-000000> <[Security:090294]could not get connection>
```


<br><br>


## 2.4 Outcomes

"2.3 Troubleshooting with test cases" 에서 중간 중간 코멘트로 언급했지만, 여기서 정리한다.

<br>

다음의 옵션들에 대해 더 이해하고자 Debugging test case를 수행한 것인데,

```
Connection Pool Size
Connect Timeout
Connection Retry Limit
Results Time Limit
```

<br>

지금 보니 Pool Size의 경우에는 별다른 테스트를 수행하지 않았다.

기본값(6) 으로 진행했더라면, 아마 더 많은 접속 유저들이 있다는 가정하에 테스트 해야 뚜렷한 차이점이 보이지 않았을까 싶다.

<br>

Connect Timeout은 옵션명 그대로, External LDAP Server와 연결이 완료되어야 하는 seconds인데, 여기 테스트 환경에서는 LDAP Server를 외부에 설치하지 못하여 WebLogic과 동일한 local machine에 설치하였고, Windows 방화벽 차단 규칙이 동작하지 않는 문제로 단순히 MS사의 Process Explorer를 통한 Process의 Suspend 재현 밖에 하지 못했다. 

테스트를 하지 못했다고 해서, Connect Timeout이 다르게 동작할 것이라는 별다른 의심은 들지 않는다.

<br>

Connection Retry Limit의 경우, Connection을 생성 실패하면 몇번을 더 할까에 대한 것인데, 중간에 언급했고 Console Help에도 있지만

> if the initial connection failed.

Connection이 아예 없는 최초 상태. 그러니까 최초로 로그인 하는 계정에 대해 LDAP Server에서 조회를 수행하기 위해 connection을 만드는데, 이때 실패하면 옵션만큼 재시도를 수행한다.

또한, 문제가 없는 정상 상태에서 LDAP Server와 연결이 되어 정상 connection이 만들어진 이후에, 다시 실패하는 상황이 재현되면 해당 connection은 파괴되는 것이 확인되었다.

connection이 파괴되었으므로, 다시 생성을 시도할 때(로그인 재시도) 이 옵션은 적용 되는 것 또한 확인되었다.

<br>

Results Time Limit 옵션은, LDAP Server와 Socket 연결이 되어 정상적인 Connection이 있는 경우.

그 Connection으로 LDAP Server로 부터 질의한 내용에 대해 응답을 기다리는 동안의 Timeout 값이다.

Connected 되지 않은 상황에서는 적용되지 않는다.

<br>

어느 고객사에서 LDAP Server가 비정상적인데, 접속을 여러번 자꾸 수행하는 것이, WebLogic의 의도된 동작인지에 대한 문의가 있었다.

위 나열한 4개의 옵션의 기본값을 사용중이였는데, 옵션에 대한 이해도만 고려하면 여러번 시도 하지 않아야 할 것으로 보였지만,

테스트 해보니, 초기 생성 단계인지, 중간에 파괴된 Connection인지, 다시 그걸 만들어야 하는 초기 생성 단계로 돌아가는 것인지.

복잡한 흐름에 따라 로그가 다양하였다.


<br><br>


# 3. References

How to Enable LDAP Debug on a Weblogic Server (Doc ID 1076242.1)
https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/secmg/ldap_atn.html#GUID-C1478BFB-A1FF-46F0-8931-627A00B7945A
https://nightlies.apache.org/directory/studio/2.0.0.v20210717-M17/userguide/apacheds/gettingstarted_configuration_editor_partitions.html
