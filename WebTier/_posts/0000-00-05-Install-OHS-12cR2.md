---
date: 2022-12-05 08:54:01 +0900
layout: post
title: "[WebTier/OHS] Oracle HTTP Server 12cR2 Installation"
tags: [WebTier, OHS, Install]
typora-root-url: ..
---

# 1. 개요

Oracle HTTP Server 12cR2 Installation
{{ site.content.br_small }}
# 2. 설치 전 확인사항

[여기](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/wtins/preparing-install-and-configure-product.html#GUID-35030871-A1A0-435C-8094-A74CCD42EAD1)에서 전체적으로 확인할 사항이 나열되어 있다.

아래에서는 일반적으로 살펴보는 부분만 나열한다.
{{ site.content.br_small }}
## 2.1 OS Requirements

[여기](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/sysrs/system-requirements-and-specifications.html#GUID-880D655D-F9FB-439B-8001-10AA78D0FC57)에서 설치 대상 운영체제별로 요구사항을 준수한다.
{{ site.content.br_small }}
**_RHEL 8 Section에는 `ksh` 언급이 없으나, 문서상 누락이 된 것 같다. 필요하다!_**
{{ site.content.br_small }}
## 2.1 Certification Matrix

[여기](https://www.oracle.com/middleware/technologies/fusion-certification.html)에서 **System Requirements and Supported Platforms for Oracle Fusion Middleware 12c (12.2.1.4.0)** 를 확인한다.
{{ site.content.br_small }}
## 2.2 Download

[여기](https://www.oracle.com/middleware/technologies/webtier-downloads.html) 에서 **Oracle HTTP Server 12.2.1.4** 다운로드 한다.
{{ site.content.br_small }}
# 3. 설치

이 게시물에서는, [Silent Mode](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/ouirf/using-oracle-universal-installer-silent-mode.html)로 설치를 진행한다.
{{ site.content.br_small }}
## 3.1 설치에 앞서...

Oracle Fusion Middleware 제품군 설치는 [Oracle Universal Installer](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/ouirf/using-oracle-universal-installer.html) 를 사용하여 설치를 한다.

WebLogic Server와 같이 Jar Generic 배포판을 설치하기 위해서는, JDK가 필요하지만,

Oracle HTTP Server와 같이 Platform Specific 배포판은 JDK가 내장되어 있다.
{{ site.content.br_small }}
## 3.2 Engine

Oracle HTTP Server는 WebLogic에 의해 Managed 되지 않는

Standalone Mode로 설치를 할 것이며, 관련 내용은 [여기](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/wtins/preparing-install-and-configure-product.html#GUID-0EB99887-F782-4FB4-A03E-12EC5451AA3E)에서 확인할 수 있다.
{{ site.content.br_small }}
Response File

```shell
[ENGINE]
 
#DO NOT CHANGE THIS.
Response File Version=1.0.0.0.0
 
[GENERIC]
 
#Set this to true if you wish to skip software updates
DECLINE_AUTO_UPDATES=true

#My Oracle Support User Name
MOS_USERNAME=

#My Oracle Support Password
MOS_PASSWORD=<SECURE_VALUE>

#If the Software updates are already downloaded and available on your local system,
#then specify the path to the directory where these patches are available and
#set SPECIFY_DOWNLOAD_LOCATION to true
AUTO_UPDATES_LOCATION=

#Proxy Server Name to connect to My Oracle Support
SOFTWARE_UPDATES_PROXY_SERVER=

#Proxy Server Port
SOFTWARE_UPDATES_PROXY_PORT=

#Proxy Server Username
SOFTWARE_UPDATES_PROXY_USER=

#Proxy Server Password
SOFTWARE_UPDATES_PROXY_PASSWORD=<SECURE_VALUE>

#The oracle home location. This can be an existing Oracle Home or a new Oracle Home
ORACLE_HOME=/sw/webtier/12cR2
 
#Set this variable value to the Installation Type selected. 
#e.g. Fusion Middleware Infrastructure, Fusion Middleware Infrastructure With Examples.
INSTALL_TYPE=Standalone HTTP Server (Managed independently of WebLogic server)
```
{{ site.content.br_small }}
Inventory Pointer

해당 Sample 은 제품 공식 메뉴얼에서 찾을 수 없었다.

```shell
inventory_loc=/sw/webtier/inventories/12cR2
inst_group=wasadm
```
{{ site.content.br_small }}
## 3.3 Domain

Oracle HTTP Server 제품은 기본적으로 두 가지의 [Domain Type](https://docs.oracle.com/en/middleware/fusion-middleware/web-tier/12.2.1.4/administer-ohs/intro_ohs.html#GUID-C5D8A85F-91C5-453B-B9E0-96F9FA31E14E)이 존재한다.

여기서는 WebLogic Server Domain으로 구성되지 않고, 독립실행되는 Standalone Mode를 사용한다.

Domain Type간의 차이점은, Admin/Managed Server가 없으며,

Domain/NodeManager/OHS-Component로 이루어져 있다.
{{ site.content.br_small }}
domain.py

```python
selectTemplate('Oracle HTTP Server (Standalone)', '12.2.1.3.0')
loadTemplates()
writeDomain('/sw/webtier/12cR2/domains/base_domain') 
exit()
```
{{ site.content.br_small }}
domain을 생성하는 스크립트에는 함정이 있다.

기본적으로 `readTemplate`는 Deprecated되어 `selectTemplate`를 권고하지만,

help page는 없어, [Oracle Docs](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/wlstg/domains.html#GUID-260F4A16-9713-4D49-91FD-18DEF9AF848A)에 의지해야한다.

```shell
wls:/offline> help('selectTemplate')
No help for selectTemplate found. Please try help() for available options.

wls:/offline> help('loadTemplates')
No help for loadTemplates found. Please try help() for available options.
```
{{ site.content.br_small }}
그리고 `readTemplate`는 실제 사용할 Template Jar 파일을 사용하는 반면,

`selectTemplate` 파일은 Template Name과 Version을 알아야 한다.

이 OHS 버전은, Release 당시 수정을 하지 않았는지

/sw/webtier/12cR2/ohs/common/templates/wls/ohs_standalone_template.jar:template-info.xml 파일이 잘못 되어있었다.

```shell
$ cat template-info.xml
<!--
      Copyright (c) 2014, 2019, Oracle and/or its affiliates. All rights reserved.
-->
<domain-template-info
            name="Oracle HTTP Server (Standalone)"
            category="Oracle HTTP Server"
            version="12.2.1.3.0"
            type="Domain Template"
            author="Oracle Corporation"
            description="standalonetemplateinfo.desc"
            iconName="Integration.gif"
            selectable="true"
            server-type="wls"
            cam-environment="standalone"
            xmlns:fo="http://www.w3.org/1999/XSL/Format"
            xmlns="http://xmlns.oracle.com/weblogic/domain-template">
  <comp-ref name="oracle.ohs2"/>
  <cam-component type="OHS"/>
</domain-template-info>
```
{{ site.content.br_small }}
그러므로 실 제품버전이 아니라, 위 XML 정보에 근거하여 domain.py 를 작성해야 한다.

**_[GUI 메뉴얼](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/wtins/configuring-standalone-domain.html#GUID-7D84990B-00CB-47D5-888B-94B726CAEEF3)을 보고 따라했지만, 되지 않아 헤맸다._**
{{ site.content.br_small }}
도메인 생성 명령어

```shell
/sw/webtier/12cR2/oracle_common/common/bin/wlst.sh domain.py
```
{{ site.content.br_small }}
## 3.4 NodeManager

두번째 필수 요소인 NodeManager를 생성해야 한다.
{{ site.content.br_small }}
Domain 생성 직후에는, NodeManager의 Account 가 임의 설정되어 있는 것을 조회할 수 있다.

```shell
/sw/webtier/12cR2/oracle_common/common/bin/wlst.sh \
readDomain('/sw/webtier/12cR2/domains/base_domain')
cd('/SecurityConfiguration/base_domain')
get('NodeManagerUsername')
get('NodeManagerPasswordEncrypted')
```
{{ site.content.br_small }}
다음과 같이 실행하여, 수정한다.

```shell
readDomain('/sw/webtier/12cR2/domains/base_domain')
cd('/SecurityConfiguration/base_domain')
set('NodeManagerUsername','webtier')
set('NodeManagerPasswordEncrypted','webtier1')
updateDomain()
exit()
```
{{ site.content.br_small }}
이외 NodeManager 사용을 위해 대체로 적용하는 설정값이다.

/sw/webtier/12cR2/domains/base_domain/nodemanager/nodemanager.properties

- `ListenAddress` localhost를 사용하지 않도록 한다.
- `ListenPort` 기본 5556
- `SecureListener` False 권장
{{ site.content.br_small }}
/sw/webtier/12cR2/domains/base_domain/config/config.xml

```
<node-manager>
  <name>localmachine</name>
  <listen-address>wls.local</listen-address>
  <listen-port>5556</listen-port>
```
{{ site.content.br_small }}
## 3.5 Components

실제 worker를 생성하는 단계다.
{{ site.content.br_small }}
기본 ohs1 Component는 지우고 worker1, worker2 를 생성한다.

```python
readDomain('/sw/webtier/12cR2/domains/base_domain')

delete('ohs1','SystemComponent')
create('worker1','SystemComponent')
create('worker2','SystemComponent')

cd('/OHS/worker1')
set('ListenAddress','wls.local')
set('ListenPort','10100')
set('SSLListenPort','10143')
set('AdminHost', '127.0.0.1')
set('AdminPort', '10177')

cd('/OHS/worker2')
set('ListenAddress','wls.local')
set('ListenPort','10200')
set('SSLListenPort','10243')
set('AdminHost', '127.0.0.1')
set('AdminPort', '10277')

updateDomain()
exit()
```
{{ site.content.br_small }}
~~Enterprise Manager Fusion Middleware Control (FMC EM) 에서 OHS 와 통신하기 위해 사용하는 Admin Port 는 Disabled 한다.~~

No admin.conf Listen directive 메시지와 함께 진행이 되지 않아, 잠시 보류한다.

```shell
$ vi base_domain/config/fmwconfig/components/OHS/worker1
$ vi base_domain/config/fmwconfig/components/OHS/worker2
...
# Include the admin virtual host (Proxy Virtual Host) related configuration
#include "admin.conf"
```
{{ site.content.br_small }}
Components는 Node Manager에 접속하여 실행한다.
{{ site.content.br_small }}
# 4. Start/Stop

## 4.1 NodeManager

startNM.sh

```shell
#!/usr/bin/bash

BASEDIR=$(realpath $(dirname $0))

SERVER_NAME="nodemanager"
DOMAIN_HOME=${BASEDIR}
LOG_HOME=${DOMAIN_HOME}/logs/${SERVER_NAME}

##### User Check #####
USER=wasadm
if [ "$USER" != `/usr/bin/whoami` ]; then
     echo "* you do not have permission. *"
     exit;
fi
####################

## Process Check ##
WEB_PID=$(${DOMAIN_HOME}/psNM.sh)
if [ "$WEB_PID" != "" ]; then
     echo "Server already Started."
     exit;
fi
###################

mkdir -p ${LOG_HOME}

nohup ${BASEDIR}/bin/startNodeManager.sh >> ${LOG_HOME}/${SERVER_NAME}.out 2>&1 &
sleep 1
tail -5 ${LOG_HOME}/${SERVER_NAME}.out
```
{{ site.content.br_small }}
stopNM.sh

```shell
#!/usr/bin/bash

BASEDIR=$(realpath $(dirname $0))

SERVER_NAME=nodemanager
DOMAIN_HOME=${BASEDIR}
LOG_HOME=${DOMAIN_HOME}/logs/${SERVER_NAME}

##### User Check #####
USER=wasadm
if [ "$USER" != `/usr/bin/whoami` ]; then
     echo "* you do not have permission. *"
     exit;
fi
####################

## Process Check ##
WEB_PID=$(${DOMAIN_HOME}/psNM.sh)
if [ "$WEB_PID" == "" ]; then
     echo "Server already Stopped."
     exit;
fi
###################

${DOMAIN_HOME}/bin/stopNodeManager.sh >> ${LOG_HOME}/${SERVER_NAME}.out
tail -5 ${LOG_HOME}/${SERVER_NAME}.out
```
{{ site.content.br_small }}
psNM.sh

```shell
#!/usr/bin/bash

BASEDIR=$(realpath $(dirname $0))
DOMAIN_HOME=${BASEDIR}

ps -ef | grep "weblogic.NodeManager -v" | grep "${DOMAIN_HOME}"
```
{{ site.content.br_small }}
## 4.2 Worker

start-worker1.sh

```shell
#!/usr/bin/bash

BASEDIR=$(realpath $(dirname $0))

WORKER=worker1
DOMAIN_NAME=base_domain
DOMAIN_HOME=${BASEDIR}

WL_HOME="/sw/webtier/12cR2/wlserver"

##### User Check #####
USER=wasadm
if [ "$USER" != `/usr/bin/whoami` ]; then
     echo "* you do not have permission. *"
     exit;
fi
####################

## Process Check ##
WEB_PID=$(${DOMAIN_HOME}/ps-worker1.sh)
if [ "$WEB_PID" != "" ]; then
     echo "Server already Started."
     exit;
fi
###################

cat << EOF > ${DOMAIN_HOME}/.start-${WORKER}.py
nmConnect('webtier', 'webtier1', 'wls.local', '5556', '${DOMAIN_NAME}', '${DOMAIN_HOME}','plain')
nmStart(serverName='${WORKER}', serverType='OHS')
nmServerStatus(serverName='${WORKER}', serverType='OHS')
nmDisconnect()
exit()
EOF

${WL_HOME}/../oracle_common/common/bin/wlst.sh ${DOMAIN_HOME}/.start-${WORKER}.py 2>&1
rm ${DOMAIN_HOME}/.start-${WORKER}.py
```
{{ site.content.br_small }}
stop-worker1.sh

```shell
#!/usr/bin/bash

BASEDIR=$(realpath $(dirname $0))

WORKER=worker1
DOMAIN_NAME=base_domain
DOMAIN_HOME=${BASEDIR}

WL_HOME="/sw/webtier/12cR2/wlserver"

##### User Check #####
USER=wasadm
if [ "$USER" != `/usr/bin/whoami` ]; then
     echo "* you do not have permission. *"
     exit;
fi
####################

## Process Check ##
WEB_PID=$(${DOMAIN_HOME}/ps-worker1.sh)
if [ "$WEB_PID" == "" ]; then
     echo "Server already Stopped."
     exit;
fi
###################

cat << EOF > ${DOMAIN_HOME}/.stop-${WORKER}.py
nmConnect('webtier', 'webtier1', 'wls.local', '5556', '${DOMAIN_NAME}', '${DOMAIN_HOME}','plain')
nmKill(serverName='${WORKER}', serverType='OHS')
nmServerStatus(serverName='${WORKER}', serverType='OHS')
nmDisconnect()
exit()
EOF

${WL_HOME}/../oracle_common/common/bin/wlst.sh ${DOMAIN_HOME}/.stop-${WORKER}.py 2>&1
rm ${DOMAIN_HOME}/.stop-${WORKER}.py
```
{{ site.content.br_small }}
ps-worker1.sh

```shell
#!/usr/bin/bash

BASEDIR=$(realpath $(dirname $0))
DOMAIN_HOME=${BASEDIR}

ps -ef | grep httpd | grep worker1 | grep "${DOMAIN_HOME}"
```

