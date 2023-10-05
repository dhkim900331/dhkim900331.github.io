---
layout: post
title: "[WebLogic] UDDI Explorer 보안 취약점"
tags: [Middleware, WebLogic, UDDI, Explorer]
date: 2022-02-07 17:43:10 +0900
---


# 1. 개요
WebLogic UDDI Explorer 보안 취약점 제거 방법을 소개한다.


# 2. UDDI Explorer ?
UDDI Explorer는 WebService 를 구현하실 때 편의를 위해 제공하는 라이브러리.


# 3. UDDI Explorer 제거 방법
UDDI Explorer는 WebService 를 구현하실 때 편의를 위해 제공하는 라이브러리로
따로 API를 가지고 구현해서 사용하지 않으시면 해당 라이브러리를 삭제하셔도 됩니다.
오라클에서도 보안쪽 advisories 로 공지한 부분으로,
10.3 이전버전에서는 패치가 제공되며 이후 버전은 실제 파일을 삭제해야합니다.
삭제하시는 방법은 다음과 같습니다.

```
1. Shut down running WLS servers.
2. Remove uddi.properties, uddi.war & uddiexplorer.war files under the <WL_HOME>/server/lib/ folder.
   *Steps 3 and 4 only required if the server server had be started before and tmp directory had been created
3. Clear <DOMAIN_HOME>/servers/<SERVER_NAME>/tmp/.internal/ folder.
4. Remove the two folders under <DOMAIN_HOME>/servers/<SERVER_NAME>/tmp/_WL_internal/uddi*;
5. Restart the WLS admin server You should see warning messages like these in your startup log (and/or sysout):.
```


# 4. 정상 적으로 제거 하였는지 확인 방법
로그상에 다음과 같은 메시지가 떠야 정상적으로 disable 설정됨.
```
<Nov 07, 2011 3:02:31 PM EST> <Warning> <Deployer> <BEA-149617> <Non-critical internal application uddi was not deployed. Error: [Deployer:149158]No application files exist at 'C:\Oracle\Middleware\wls103\WEBLOG~1\server\lib\uddi.war'.>

<Nov 07, 2011 3:02:31 PM EST> <Warning> <Deployer> <BEA-149617> <Non-critical internal application uddiexplorer was not deployed. Error: [Deployer:149158]No application files exist at 'C:\Oracle\Middleware\wls103\WEBLOG~1\server\lib\uddiexplorer.war'.>
```