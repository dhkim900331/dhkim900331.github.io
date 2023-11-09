---
date: 2022-08-05 14:41:19 +0900
layout: post
title: "[JBoss] Application Deployment"
tags: [Middleware, JBoss, Deploy, War, App]
typora-root-url: ..
---


# 1. 개요

Application Deployment 명령어를 학습한다.

* 압축된 Unexploded WAR 파일의 배포 및 관리
* 압축해제된 Exploded WAR 파일의 배포 및 관리



# 2. Deploy CLI

기본적으로 배포 시에는 다음의 Syntax를 유념해야한다.

> `jboss-cli > deploy --help` 명령을 통해 확인하면 되겟으며, 여기서는 필요한 요소만 확인한다.



```syntax
deploy \
--name=baseApp \
--runtime-name=baseApp.war \
--url=file://.../baseApp.war \
--unmanaged \
--force
```

* --name : 어플리케이션 배포 단위마다 유니크한 이름
* --runtime-name : 지정하지 않아도 되는 옵션이며, \<name> 자동 지정된다. 그러나 확장자를 .war로 지정해야 Context-Root 호출이 가능하기 때문에 사실상 필수 옵션이다.
* --url : 어플리케이션 위치
* --unmanaged : 어플리케이션을 `-Djboss.server.deploy.dir` 에 복사하지 않는다.
* --force : 이미 배포된 어플리케이션을 덮어 씌운다.



위의 Syntax에서 크게 벗어나지 않는 것만 알아도

대부분의 어플리케이션 배포에는 문제가 없다.



아래에서 여러가지 파라메터로 실행하고 확인한다.



# 3. Unexploded WAR 배포

Application 배포 디렉토리를 `-Djboss.server.deploy.dir=<PATH>/appDeployHome` 으로 지정하였다.

지정하지 않으면, 기본적으로 인스턴스 아래, 즉 다음과 같은 경로가 된다. `/usr/ssw/jboss/servers/base_domain/baseSvr1_1/data/content`



아래 명령으로, baseApp.war 파일을 배포한다.

```jboss-cli
deploy \
--name=baseApp \
--runtime-name=baseApp.war \
<PATH>
```



`--unmanaged` 옵션이 없으므로, 아래 위치에 복제된다.

```
Content added at location /usr/ssw/jboss/servers/base_domain/baseSvr1_1/appDeployHome/28/c76586c599e9cf1c2f2e2f87269fcf377d351b/content
```



baseApp.war 배포 정보 및 등록된 Context-Root 도 친절히 알려준다.

```
WFLYSRV0027: Starting deployment of "baseApp.war" (runtime-name: "baseApp.war")
WFLYUT0021: Registered web context: '/baseApp' for server 'default-server'
WFLYSRV0010: Deployed "baseApp.war" (runtime-name : "baseApp.war")
```



standalone*xml 파일 확인

```xml
    <deployments>
        <deployment name="baseApp.war" runtime-name="baseApp.war">
            <content sha1="28c76586c599e9cf1c2f2e2f87269fcf377d351b"/>
        </deployment>
    </deployments>
```



배포 상태 확인

```
jboss-cli > deployment info
NAME        RUNTIME-NAME PERSISTENT ENABLED STATUS
baseApp.war baseApp.war  true       true    OK
```

http://IP:PORT/baseApp/indexjsp 로 서비스 호출 할 수 있다.



# 4. Exploded WAR 배포

아래 명령으로, baseApp.war 파일을 배포한다.

```jboss-cli
deploy \
--name=baseApp \
--runtime-name=baseApp.war \
--unmanaged \
/usr/ssw/jboss/servers/base_domain/baseSvr1_1/baseApp
```



압축 해제된 디렉터리 배포의 경우에는 `--unmanaged` 옵션을 적용해야 한다. (`jboss-cli> deploy --help`)

해당 옵션은 디렉터리 배포의 경우에도 사용되지만, WAR 배포에도 사용된다.

주요 목적은, 옵션 적용 시 컨텐츠가 특정 디렉토리(appDeployHome)에 배포되어 유지되지만,

실제 배포는 해당 디렉터리에서 직접 된다.

또한, baseApp 어플리케이션 수정 시 핫디플로이 된다.

```
Content added at location /usr/ssw/jboss/servers/base_domain/baseSvr1_1/appDeployHome/28/c76586c599e9cf1c2f2e2f87269fcf377d351b/content
```



standalone*xml 파일 확인

```xml
    <deployments>
        <deployment name="baseApp" runtime-name="baseApp.war">
            <fs-exploded path="/usr/ssw/jboss/servers/base_domain/baseSvr1_1/baseApp"/>
        </deployment>
    </deployments>
```



# 5. 기존 배포 업데이트

어플리케이션 변경에 대응 하기 위해,

동일한 어플리케이션 업데이트를 할 수 있다.

```
deploy \
--name=baseApp \
--runtime-name=baseApp.war \
--unmanaged \
--force \
/usr/ssw/jboss/servers/base_domain/baseSvr1_1/baseApp
```



baseApp 의 모든 컨텐츠를 `--force` 옵션으로 인해 재배포한다.



배포 중단

```
WFLYUT0022: Unregistered web context: '/baseApp' from server 'default-server'
WFLYSRV0028: Stopped deployment baseApp (runtime-name: baseApp.war) in 11ms
```



새로운 배포의 시작 (중단한 배포 삭제)

```
WFLYSRV0027: Starting deployment of "baseApp" (runtime-name: "baseApp.war")
WFLYUT0021: Registered web context: '/baseApp' for server 'default-server'
WFLYSRV0016: Replaced deployment "baseApp.war" with deployment "baseApp.war"
WFLYDR0009: Content /usr/ssw/jboss/servers/base_domain/baseSvr1_1/appDeployHome/c0/4764af6fe95a9863599ad6ecbcae79106d3938 is obsolete and will be removed
WFLYDR0002: Content removed from location /usr/ssw/jboss/servers/base_domain/baseSvr1_1/appDeployHome/c0/4764af6fe95a9863599ad6ecbcae79106d3938/content
```



# 6. 어플리케이션 버저닝

동일한 어플리케이션 여럿 등록하여 버저닝을 할 수도 있다.



`--unmanaged` 를 제거해야, 컨텐츠를 복제하여 별도로 관리하기 때문에 버저닝이 된다.

```
deploy \
--name=baseApp \
--runtime-name=baseApp.war \
/usr/ssw/jboss/servers/base_domain/baseSvr1_1/baseApp.war
```



baseApp.war 를 수정하여 version#2 를 릴리즈 할 경우.

```
deploy \
--name=baseApp_v2 \
--runtime-name=baseApp_v2.war \
/usr/ssw/jboss/servers/base_domain/baseSvr1_1/baseApp.war
```



baseApp.war 는 각 명령어 배포 시점에 고유한 디렉토리에 복제되어 배포되기 때문에

변경된 동일 어플리케이션을 버저닝 관리하듯이 배포할 수 있다.



각각 접속 URL은

http://IP:PORT/baseApp/index.jsp

http://IP:PORT/baseApp_v2/index.jsp 가 된다.



# 7. 어플리케이션 배포 삭제

```
jboss-cli> deployment info
NAME       RUNTIME-NAME   PERSISTENT ENABLED STATUS
baseApp    baseApp.war    true       true    OK
baseApp_v2 baseApp_v2.war true       true    OK
```



```
deployment undeploy baseApp
```

또는

```
undeploy *
```



# 8. 참고 문헌

https://access.redhat.com/documentation/en-us/red_hat_jboss_enterprise_application_platform/6.4/html/administration_and_configuration_guide/define_a_custom_directory_for_deployed_content

https://access.redhat.com/solutions/2978491

https://access.redhat.com/solutions/2181751
