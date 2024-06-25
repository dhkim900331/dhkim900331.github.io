---
date: 2023-04-19 08:56:19 +0900
layout: post
title: "[Coherence/Web] How to install Coherence Web 14c"
tags: [Coherence, Web, Installation]
typora-root-url: ..
---

# 1. Overview

Coherence 14c 테스트 환경을 위해 기본 설치 환경을 집약한다.
{{ site.content.br_small }}
# 2. Descriptions

다음 환경을 구성하도록 한다.

- cluster-base_domain
  - Coherence Server, TCP 9000 ~ 9100
  - Managed Coherence Server, TCP 9000
  {{ site.content.br_small }}

아래 문서에서는 Coherence-Server를 Cache-Server,

Managed Coherence Server(WLS+Coherence Module)를 Cache-Client 라고 표현하기도 했다.

WLS 또한 자기 자신이 Cache-Server가 될 수 있으나, Coherence을 사용하는 목적은 WLS 에서는 Data를 처리하지 않는 것이기 때문이다.
{{ site.content.br_small }}

## 2.1 Downloads

[Oracle Software Delivery Cloud](https://edelivery.oracle.com) 에서 Download 할 List

- Oracle Coherence 14.1.1.0.0 (124.3 MB)





# 3. Script

## 3.1 Engine

```sh
BASEDIR=/sw/installFiles
OS_USERNAME=$(id --user --name)
OS_GROUPNAME=$(id --group --name)

COH_INSTALL_FILE=${BASEDIR}/fmw_14.1.1.0.0_coherence.jar
JAVA_HOME=/sw/jdk/jdk1.8.0_351

COH_INSTALL_PATH=/sw/coherence/14c
INVENTORY_PATH=/sw/coherence/inventories/14c
INVENTORY_GROUP=${OS_GROUPNAME}

DOMAIN_NAME=base_domain
DOMAIN_HOME=${COH_INSTALL_PATH}/domains/${DOMAIN_NAME}

CS_ADDR=wls.local
CS_PORT=9000
CS_PORT_ADJUST=100


# (1) ResponseFile
# https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/ouirf/sample-response-files-silent-installation-and-deinstallation.html#GUID-65B11C03-B559-41F1-B9B4-B7276491E580
# INSTALL_TYPE is one of fmw_14.1.1.0.0_coherence.jar:/Disk1/stage/distributions/Coherence_14.1.1.0.0.xml

cat << EOF > ${BASEDIR}/rsp
[ENGINE]
Response File Version=1.0.0.0.0
 
[GENERIC]
DECLINE_AUTO_UPDATES=true
ORACLE_HOME=${COH_INSTALL_PATH}
INSTALL_TYPE=Typical
EOF


# (2) Inventory
# https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/ouirf/using-oracle-universal-installer-silent-mode.html#GUID-756E3FD9-4094-412F-9BEB-72C5FD51056B
# * inventory.loc 파일 샘플은 문서에 없음

cat << EOF > ${BASEDIR}/loc
inventory_loc=${INVENTORY_PATH}
inst_group=${INVENTORY_GROUP}
EOF


# (3) Installation
# https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/ouirf/using-oracle-universal-installer-silent-mode.html#GUID-5F06D02F-6D71-45B9-BF41-5D5759D31958

${JAVA_HOME}/bin/java -jar ${COH_INSTALL_FILE} -silent -responseFile ${BASEDIR}/rsp -invPtrLoc ${BASEDIR}/loc
```
{{ site.content.br_small }}
## 3.2 Cache Configuration

Cluster 내에서 유지할 Cache 에 대한 기본 속성을 정의할 수 있다.

해당 파일은 Cache-Server, Cache-Client 모두에서 사용된다.

XML 파일은 한 번만 정의되고 쓰이면 모두가 만족해야 될 것으로 이해했는데, 공식 가이드를 따라가보면 Server와 Client, 그리고 Client(WLS)에 배포된 App 내에서도 사용된다.

여기저기서 사용되는 것이 맞는지에 대한 것 때문에 혼동이 좀 있었는데,

App에서 생성하는 Cache는 Cache-Server에서도, Cache-Client에서도 모두 유지되기 위해서 기본 Cache 구성에 대한 정의가 있어야 되기 때문에 양쪽에 동일한 파일이 있어야 하는 것으로 ~~그냥~~ 이해했다.
{{ site.content.br_small }}
* [Overview of Coherence*Web](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/administer-http-sessions/using-coherenceweb-weblogic-server.html#GUID-24BDEA82-1E53-47F2-BD2B-E573639DADB5)

  * coherence.jar, coherence-web.jar 파일이 공유 라이브러리로 배포되거나, Web application lib에 위치해야 한다.

    > Web-App 아래에 배포되는 경우, Heap resource 낭비도 있거니와 Operational XML 파일을 Load하는데도 문제가 있으므로 사실상 Shared Library($DOMAIN_HOME/lib)에 배포해야 한다.

  * 기본 Cache 구성 파일은, coherence-web.jar 에 default-session-cache-config.xml 가 있다.
  
    ```sh
    $ jar -xf coherence-web.jar default-session-cache-config.xml
    $ mv default-session-cache-config.xml session-cache-config.xml
    ```
  
    > 해당 파일을 추출하여, Coherence , WLS, App 내에서 다양하게 사용된다.
  
  * [Using a Custom Session Cache Configuration File](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/administer-http-sessions/using-coherenceweb-weblogic-server.html#GUID-16EF76E3-D55A-4823-8035-81873199E796))에 따라 기본 Cache 구성 파일을 변경할 수 있다.
  
  * 기본 Cache 구성 파일은, WEB-INF/classes 에 배치한다. 없으면, coherence-web.jar에서 default-session-cache-config.xml 을 로드한다.
  
    > coherence-web.jar 를 App/lib 내에 배포하지 않으면 Cache 구성 파일을 Load 하지 않아 에러가 있다, xml 을 반드시 배포하거나, jar 파일을 Shared Library 가 아닌, App/lib 에 배포 해야 한다.
  
  * 위 설명에서, 기본 Cache 구성 파일 이름 변경(session-cache-config.xml 이름이 아닌)하여 web.xml 에서 경로를 입력 가능하다고 하지만 문서 버그인지 방법이 나타나 있지 않다. Option 으로 설정할 수 있다.
  
    ```sh
    coherence.cache.configuration.path=xml
    ```
  
    > 배포한 App이 한 개 뿐이라면 유용하겠으나, 일반적으로 그렇지 않으니 classes 에 session-cache-config.xml 넣는 것이 강제될 수 있겠다.
  
  * 기본적으로 local-storage가 false로 설정되어 있기 때문에, XML을 수정하거나 Option을 설정한다. Cache-Client에서는 false를 사용하면 되겠다.
  
    ````sh
    coherence.session.localstorage=true
    ````
{{ site.content.br_small }}
여기서 언급한 coherence.jar, coherence-web.jar, session-cache-config.xml 파일은 Cache-Server, Cache-Client 에서 모두 사용되므로 각 디렉토리로 적절히 복사가 되어야 한다.

아래는, 앞으로 우리가 구축할 WLS와 Coherence Domain 디렉토리에 복제될 파일 목록들이다.

> [3.2.1 Cluster](#h-321-cluster)을 먼저 수행한다.

```sh
# Cache-Client가 될 WLS 에 복사
$ ls -al <WEBLOGIC-DOMAIN-HOME>/lib/*
-rw-r----- 1 wasadm wasadm 13763107 Apr 20 15:29 coherence.jar
-rw-r----- 1 wasadm wasadm   241893 Apr 20 15:29 coherence-web.jar
-rw-rw-r-- 1 wasadm wasadm     4337 Apr 20 15:38 session-cache-config.xml

# Cache-Server가 될 Coherence 에 복사
$ cd <COHERENCE-DOMAIN-HOME>/lib/
$ ls -al coherence.jar coherence-web.jar session-cache-config.xml
-rw-r----- 1 wasadm wasadm 13763107 Mar 26  2020 coherence.jar
-rw-r----- 1 wasadm wasadm   241893 Mar 26  2020 coherence-web.jar
-rw-rw-r-- 1 wasadm wasadm     4337 Apr 20 15:24 session-cache-config.xml
```
{{ site.content.br_small }}
## 3.2 Cache-Server

### 3.2.1 Cluster

Coherence 구성을 위해서는 많은 설정 값이 필요하지만, [Using the Default Operational Override File](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/develop-applications/understanding-configuration.html#GUID-8387E29A-EE03-4075-B4E7-D92779335965) 방식을 사용하여, 일부분 설정값만 override 하도록 한다.
{{ site.content.br_small }}
[Specifying an Operational Override File](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/develop-applications/understanding-configuration.html#GUID-1C518560-021D-4F55-ACC4-C0E10133D45A) 에 설명된 `-Dcoherence.override` 옵션으로 아래 설정 파일을 사용할 것이다.
{{ site.content.br_small }}
```sh
# (4) Cluster Member
# Cache Server에는 WLS Domain과 같은 개념이 없으나, 임의로 만듬

mkdir -p ${DOMAIN_HOME}/logs
cp -pR ${COH_INSTALL_PATH}/coherence/lib ${DOMAIN_HOME}

# https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/develop-applications/setting-cluster.html#GUID-E3DCA888-1155-4E95-BDC7-668719C86F69

cat << EOF > ${DOMAIN_HOME}/lib/tangosol-coherence-${DOMAIN_NAME}.xml
<?xml version='1.0'?>
<coherence xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://xmlns.oracle.com/coherence/coherence-operational-config" xsi:schemaLocation="http://xmlns.oracle.com/coherence/coherence-operational-config.xsd">
   
  <cluster-config>
    <member-identity>
      <cluster-name system-property="coherence.cluster">cluster_${DOMAIN_NAME}</cluster-name>
      <site-name    system-property="coherence.site">site_${DOMAIN_NAME}</site-name>
      <rack-name    system-property="coherence.rack">rack_${DOMAIN_NAME}</rack-name>
      <machine-name system-property="coherence.machine">machine_${DOMAIN_NAME}</machine-name>
      <process-name system-property="coherence.process">process_${DOMAIN_NAME}</process-name>
      <member-name  system-property="coherence.member">member_${DOMAIN_NAME}</member-name>
      <role-name    system-property="coherence.role">CoherenceServer</role-name>
      <priority     system-property="coherence.priority">5</priority>
    </member-identity>
  
    <unicast-listener> 
      <address system-property="coherence.localhost">${CS_ADDR}</address>
      <port system-property="coherence.localport">${CS_PORT}</port>
      <port-auto-adjust system-property="coherence.localport.adjust">$((CS_PORT+CS_PORT_ADJUST))</port-auto-adjust>

      <well-known-addresses> 
        <address id="1" system-property="coherence.wka">${CS_ADDR}</address> 
        <!--<address id="2" system-property="coherence.wka2">${CS_ADDR}</address>-->
      </well-known-addresses>
    </unicast-listener>
     
    <tcp-ring-listener>
      <enabled>true</enabled>
      <ip-timeout system-property="coherence.ipmonitor.pingtimeout">25s</ip-timeout>
      <ip-attempts>5</ip-attempts>
      <listen-backlog>10</listen-backlog>
    </tcp-ring-listener>

    <packet-publisher>
      <packet-delivery>
        <heartbeat-milliseconds>5000</heartbeat-milliseconds>
      </packet-delivery>
    </packet-publisher>
  </cluster-config>
</coherence>
EOF
```
{{ site.content.br_small }}
[3.2.2 Startup Cache-Server](#h-322-startup-cache-server)에서 설명하듯이, 우리가 생성한 `tangosol-coherence-${DOMAIN_NAME}.xml` 파일은 다음 처럼 Option이 설정되어야 한다.

```sh
-Dcoherence.override=tangosol-coherence-override-${DOMAIN_NAME}.xml
CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib
```
{{ site.content.br_small }}
CLASSPATH 에 있는 xml 파일을 override 할 수 있다.
{{ site.content.br_small }}
### 3.2.2 Startup Cache-Server

* [Start a Cache Server](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/administer-http-sessions/using-coherenceweb-weblogic-server.html#GUID-D8120C85-FCD3-491E-8618-03B691279797)
  * Coherence 는 기본적으로 WLS 하위 subsystem으로 (즉 같은 JVM) 유지되면, WLS와 같은 lifecycle을 공유한다. 이러한 경우 Managed Coherence Server 라고 부른다.
  {{ site.content.br_small }}
* [To Start a Standalone Coherence Cache Server](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/administer-http-sessions/using-coherenceweb-weblogic-server.html#GUID-E65D5FAC-B517-4F59-8AF7-8458AE1216C1)

  * Cache Server를 독립 실행, 아래에서 이 방식을 사용하는 Script를 설명했다.

  * 문서 상에는, `coherence.cacheconfig` 파일의 절대경로를 사용하라고 되어 있지만, CLASSPATH 에서 가져오는 것으로 테스트 되므로 아래와 같이 조치해야 한다.

    ```sh
    -Dcoherence.cacheconfig=session-cache-config.xml
    CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib
    ```

    

아래 스크립트는 Cache-Server 2개를 생성한다.

```sh
# (5) Create Cache-Server Script
# https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/administer-http-sessions/using-coherenceweb-weblogic-server.html#GUID-ECE861D6-450C-494C-8DD7-E9AA15AFF6E3

cat << "EOF" > ${DOMAIN_HOME}/startCS.sh
#!/bin/sh
JAVA_HOME=#JAVA_HOME#
DOMAIN_NAME=#DOMAIN_NAME#
DOMAIN_HOME=#DOMAIN_HOME#
SERVER_NAME=#SERVER_NAME#

LOG_HOME=${DOMAIN_HOME}/logs
NOHUP_LOG=${LOG_HOME}/nohup
GC_LOG=${LOG_HOME}/gc
HEAPDUMP_DIR=${LOG_HOME}/heapdump
LOG_TIME=$(date +%y%m%d_%H%M)

##### Make Path #####
mkdir -p ${LOG_HOME} ${NOHUP_LOG} ${GC_LOG} ${HEAPDUMP_DIR}
###################

##### User Check #####
USER=#OS_USERNAME#
if [ "$USER" != $(/usr/bin/whoami) ]; then
     echo "* you do not have permission. *"
     exit;
fi
####################

## Process Check ##
COH_PID=$(${DOMAIN_HOME}/ps${SERVER_NAME}.sh)
if [ "$COH_PID" != "" ]; then
     echo "Server already Started."
     exit;
fi
###################

##### gc log rotation #####
mv ${GC_LOG}/gc_${SERVER_NAME}.out ${GC_LOG}/gc_${SERVER_NAME}.out.${LOG_TIME}
USER_MEM_ARGS="${USER_MEM_ARGS} -verbose:gc -Xloggc:${GC_LOG}/gc_${SERVER_NAME}.out"
######################

##### Heap dump #####
USER_MEM_ARGS="${USER_MEM_ARGS} -XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=${HEAPDUMP_DIR}"
####################

USER_MEM_ARGS="${USER_MEM_ARGS} -server"
USER_MEM_ARGS="${USER_MEM_ARGS} -D${SERVER_NAME}"
USER_MEM_ARGS="${USER_MEM_ARGS} -Xms1024m -Xmx1024m -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=128m"
USER_MEM_ARGS="${USER_MEM_ARGS} -Djava.net.preferIPv4Stack=true -Djava.net.preferIPv6Addresses=false"
export USER_MEM_ARGS

COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.mode=prod"
COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.cacheconfig=session-cache-config.xml"
COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.override=tangosol-coherence-${DOMAIN_NAME}.xml"
COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.session.localstorage=true"
COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.management.remote=true"
export COHERENCE_ARGS

CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib"
CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib/coherence-web.jar"
CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib/coherence.jar"
export CLASSPATH

mv ${NOHUP_LOG}/${SERVER_NAME}.out ${NOHUP_LOG}/${SERVER_NAME}.out.${LOG_TIME}
nohup ${JAVA_HOME}/bin/java ${USER_MEM_ARGS} ${COHERENCE_ARGS} -cp ${CLASSPATH} com.tangosol.net.DefaultCacheServer > ${NOHUP_LOG}/${SERVER_NAME}.out 2>&1 &
EOF


cat << "EOF" > ${DOMAIN_HOME}/psCS.sh
#!/bin/sh
DOMAIN_HOME=#DOMAIN_HOME#
SERVER_NAME=#SERVER_NAME#

ps -ef | grep "java" | grep "com.tangosol.net.DefaultCacheServer" | grep "${DOMAIN_HOME}" | grep "D${SERVER_NAME}"
EOF


cat << "EOF" > ${DOMAIN_HOME}/stopCS.sh
#!/bin/sh
DOMAIN_HOME=#DOMAIN_HOME#
SERVER_NAME=#SERVER_NAME#

##### User Check #####
USER=#OS_USERNAME#
if [ "$USER" != $(/usr/bin/whoami) ]; then
     echo "* you do not have permission. *"
     exit;
fi
####################

## Process Check ##
COH_PID=$(${DOMAIN_HOME}/ps${SERVER_NAME}.sh)
if [ "$COH_PID" == "" ]; then
     echo "Server already Stopped."
     exit;
fi
###################

kill -9 $(${DOMAIN_HOME}/ps${SERVER_NAME}.sh | awk '{print $2}')
EOF


cat << "EOF" > ${DOMAIN_HOME}/logCS.sh
#!/bin/sh
DOMAIN_NAME=#DOMAIN_NAME#
DOMAIN_HOME=#DOMAIN_HOME#
SERVER_NAME=#SERVER_NAME#

LOG_HOME=${DOMAIN_HOME}/logs
NOHUP_LOG=${LOG_HOME}/nohup
tail -10f ${NOHUP_LOG}/${SERVER_NAME}.out
EOF


cp ${DOMAIN_HOME}/startCS.sh ${DOMAIN_HOME}/startCS1.sh
cp ${DOMAIN_HOME}/stopCS.sh ${DOMAIN_HOME}/stopCS1.sh
cp ${DOMAIN_HOME}/logCS.sh ${DOMAIN_HOME}/logCS1.sh
cp ${DOMAIN_HOME}/psCS.sh ${DOMAIN_HOME}/psCS1.sh

cp ${DOMAIN_HOME}/startCS.sh ${DOMAIN_HOME}/startCS2.sh
cp ${DOMAIN_HOME}/stopCS.sh ${DOMAIN_HOME}/stopCS2.sh
cp ${DOMAIN_HOME}/logCS.sh ${DOMAIN_HOME}/logCS2.sh
cp ${DOMAIN_HOME}/psCS.sh ${DOMAIN_HOME}/psCS2.sh

sed -i "s|#OS_USERNAME#|${OS_USERNAME}|g" ${DOMAIN_HOME}/*CS1.sh
sed -i "s|#JAVA_HOME#|${JAVA_HOME}|g" ${DOMAIN_HOME}/*CS1.sh
sed -i "s|#DOMAIN_NAME#|${DOMAIN_NAME}|g" ${DOMAIN_HOME}/*CS1.sh
sed -i "s|#DOMAIN_HOME#|${DOMAIN_HOME}|g" ${DOMAIN_HOME}/*CS1.sh
sed -i "s|#SERVER_NAME#|CS1|g" ${DOMAIN_HOME}/*CS1.sh

sed -i "s|#OS_USERNAME#|${OS_USERNAME}|g" ${DOMAIN_HOME}/*CS2.sh
sed -i "s|#JAVA_HOME#|${JAVA_HOME}|g" ${DOMAIN_HOME}/*CS2.sh
sed -i "s|#DOMAIN_NAME#|${DOMAIN_NAME}|g" ${DOMAIN_HOME}/*CS2.sh
sed -i "s|#DOMAIN_HOME#|${DOMAIN_HOME}|g" ${DOMAIN_HOME}/*CS2.sh
sed -i "s|#SERVER_NAME#|CS2|g" ${DOMAIN_HOME}/*CS2.sh

chmod 700 ${DOMAIN_HOME}/*.sh
rm ${DOMAIN_HOME}/*CS.sh
```
{{ site.content.br_small }}
Cache-Server를 기동하면, 표준출력 log에서 몇가지를 확인할 수 있다. 우리가 커스텀한 설정 파일대로 생성이 된다.

* Loaded operational configuration from "jar:file:/sw/coherence/14c/domains/base_domain/lib/coherence.jar!/tangosol-coherence.xml"
* Loaded operational overrides from "jar:file:/sw/coherence/14c/domains/base_domain/lib/coherence.jar!/tangosol-coherence-override-**prod.xml**"
  * 기본값 `-Dcoherence.mode=prod` 가 적용되어 있는 모습
* Loaded operational overrides from "file:/sw/coherence/14c/domains/base_domain/lib/**tangosol-coherence-base_domain.xml**"
* Loaded cache configuration from "file:/sw/coherence/14c/domains/base_domain/lib/**session-cache-config.xml**"
* Created a new cluster "cluster_base_domain" with Member(Id=1, Timestamp=2023-04-24 11:43:24.509, Address=**10.65.34.245:9000**, MachineId=7674, Location=site:site_base_domain,rack:rack_base_domain,machine:machine_base_domain,process:process_base_domain,member:member_base_domain, Role=CoherenceServer, Edition=Grid Edition, **Mode=Production**, CpuCount=4, SocketCount=1)
* PartitionedCache{Name=oracle.coherence.web:**DistributedSessions**, State=(SERVICE_STARTED), Id=4, OldestMemberId=1, **LocalStorage=enabled**, PartitionCount=257, BackupCount=1, AssignedPartitions=0, BackupPartitions=0, CoordinatorId=1}
{{ site.content.br_small }}
## 3.3 Cache-Client

Cache-Client로 WebLogic Managed Server를 사용할 것이다.

사실상, WebLogic 또한 Cache Server로 띄우는 것이므로 위에서 언급한 Managed Coherence Server가 된다.
{{ site.content.br_small }}
다음의 옵션을 WLS Instance에서 사용한다.

```sh
-Dcoherence.mode=prod
-Dcoherence.override=tangosol-coherence-${DOMAIN_NAME}.xml
-Dcoherence.session.localstorage=false
-Dcoherence.management.remote=true


# lib 아래 jar는 자동 등록되므로 필요 없다, xml 을 위해 사용한다.
CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib
#CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib/coherence-web.jar
#CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib/coherence.jar
```
{{ site.content.br_small }}
`-Dcoherence.cacheconfig=session-cache-config.xml` 옵션은 제거하였고, 해당 파일은 앞으로 배포할 Web App/WEB-INF/classes 아래에 직접 넣었다.

Application 마다 Cache 구성이 다를 수 있기 때문이다.
{{ site.content.br_small }}
그리고 `coherence.override` 으로 읽어들이는 파일은, 위에서 언급하였는데, CLASSPATH 에서 읽으므로 `Web App/WEB-INF/lib` 에 넣을 경우, 검색하는 CLASSLOAD와 관련된 문제 인지 읽을 수 없다, 어차피 Server 배포 파일이므로 App에 넣는 경우도 없을 것이다.
{{ site.content.br_small }}
인스턴스 기동 시에, 별다른 Log가 기록되지 않는다.

[3.4 Web-App 배포](#h-34-web-app-배포) 시에 Log가 출력되었다.
{{ site.content.br_small }}
## 3.4 Web-App 배포

* session-cache-config.xml 배치 구성도.

  ```sh
  $ tree <WEB-APP>/WEB-INF/
  <WEB-APP>/WEB-INF/
  ├── classes
  │   └── session-cache-config.xml
  ├── weblogic.xml
  └── web.xml
  ```
  
  
  
* weblogic.xml 구성
  * timeout-secs : Weblogic Session의 유효 기간
  * invalidation-interval-secs : Coherence Session Reaper Thread가 60초마다 실행된다.
  * persistent-store-type : coherence-web

```xml
    <container-descriptor>
        <servlet-reload-check-secs>1</servlet-reload-check-secs>
        <resource-reload-check-secs>1</resource-reload-check-secs>
    </container-descriptor>

    <jsp-descriptor>
        <page-check-seconds>1</page-check-seconds>
    </jsp-descriptor>

    <session-descriptor>
        <timeout-secs>30</timeout-secs>
        <invalidation-interval-secs>60</invalidation-interval-secs>
        <persistent-store-type>coherence-web</persistent-store-type>
    </session-descriptor>
</weblogic-web-app>
```
{{ site.content.br_small }}
App을 Deploy 시에 Log

```sh
<Module coh14cApp of application coh14cApp is transitioning from STATE_NEW to STATE_PREPARED on server M1.>

... Loaded operational configuration from "jar:file:/sw/weblogic/14c/coherence/lib/coherence.jar!/tangosol-coherence.xml"

... Loaded operational overrides from "jar:file:/sw/weblogic/14c/coherence/lib/coherence.jar!/tangosol-coherence-override-prod.xml"

... Loaded operational overrides from "file:/sw/weblogic/14c/domains/base_domain/lib/tangosol-coherence-base_domain.xml"

Oracle Coherence Version 14.1.1.0.0 Build 77467
 Grid Edition: Production mode
Copyright (c) 2000, 2020, Oracle and/or its affiliates. All rights reserved.

... Loaded cache configuration from "file:/sw/app/coh14cApp/WEB-INF/classes/session-cache-config.xml"
```
{{ site.content.br_small }}
App을 Runtime Service로 시작시에 Log.

기존(Senior) Member으로 Joined 되는 과정

```sh
<Module coh14cApp of application coh14cApp is transitioning from STATE_PREPARED to STATE_ADMIN on server M1.>

...  Member(Id=1, Timestamp=2023-04-24 11:43:24.509, Address=10.65.34.245:9000, MachineId=7674, Location=site:site_base_domain,rack:rack_base_domain,machine:machine_base_domain,process:process_base_domain,member:member_base_domain, Role=CoherenceServer) joined Cluster with senior member 1
 
... This Member(Id=2, Timestamp=2023-04-24 12:05:26.569, Address=10.65.34.245:9002, MachineId=7674, Location=site:site_base_domain,rack:rack_base_domain,machine:machine_base_domain,process:process_base_domain,member:member_base_domain, Role=CoherenceServer, Edition=Grid Edition, Mode=Production, CpuCount=4, SocketCount=1) joined cluster "cluster_base_domain" with senior Member(Id=1, Timestamp=2023-04-24 11:43:24.509, Address=10.65.34.245:9000, MachineId=7674, Location=site:site_base_domain,rack:rack_base_domain,machine:machine_base_domain,process:process_base_domain,member:member_base_domain, Role=CoherenceServer, Edition=Grid Edition, Mode=Production, CpuCount=4, SocketCount=1)

... Service TransportService is bound to tmb://10.65.34.245:9002.47964

... Service TransportService joined the cluster with senior service member 1

... Connection established with tmb://10.65.34.245:9000.44385
```
{{ site.content.br_small }}
Cache Config가 구성 되었다는 Log

```sh
<Configured session model "SplitHttpSessionCollection":
  Clustered Session Cache Name=session-storage
  Local Session Cache Name=local-session-storage
  Local Session Attribute Cache Name=local-attribute-storage
  SessionDistributionController Class Name=
  AttributeScopeController Class Name=com.tangosol.coherence.servlet.AbstractHttpSessionCollection$ApplicationScopeController
  Maximum Session Inactive Seconds=30
  Session ID Character Length=52
  Session Get Lock Timeout=300
  Suspect Attribute Detection=true
  Strict "Servlet Specification" Exception Handling=true
  Sticky Session Ownership=false
  Sticky Session Ownership Service Name=SessionOwnership
  Assume Session Locality for Reaping=false
  Parallel Session Reaping=false
  Allow Local Attributes=false
  Use Default Session ID Decoding=true
  Use Default Session ID Encoding=false
  Session ID Affinity Token=null
  Session ID Replace Affinity Token=false
  Session Expiry Filter Factory=
  Session Access Debug Logging Enabled=false
  Session Access Debug Logging Filter=
  Session Locking Mode=none
  Session Reaping Mechanism=Default>
```
{{ site.content.br_small }}
MBean 에 등록된다.

```sh
INFO: Registering MBean using object name "type=WebLogicHttpSessionManager,nodeId=2,appId=coh14cAppcoh14cApp"
2023-04-24 12:05:28.831/473.137 Oracle Coherence GE 14.1.1.0.0 <Info> (thread=[STANDBY] ExecuteThread: '3' for queue: 'weblogic.kernel.Default (self-tuning)', member=2): Registering MBean using object name "type=WebLogicHttpSessionManager,nodeId=2,appId=coh14cAppcoh14cApp"
```

