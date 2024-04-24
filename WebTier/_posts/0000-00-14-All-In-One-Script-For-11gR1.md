---
date: 2023-05-19 08:37:17 +0900
layout: post
title: "[WebTier/OHS] All In One Script For 11gR1"
tags: [WebTier, OHS, Apache, Install, WLST, Jython]
typora-root-url: ..
---

# 1. 개요

Oracle HTTP Server 11gR1 테스트 환경을 자동 재구축을 위해 모든 기본 설치 환경을 집약한다.





# 2. 설명

All-In-One-Script-For-11gR1.sh 실행으로 다음 환경을 구성하도록 한다.

- baseInstance
- Worker 2ea





# 3. Script

## 3.1 Engine

```sh
BASEDIR=/sw/installFiles
OS_USERNAME=$(id --user --name)
OS_GROUPNAME=$(id --group --name)

OHS_INSTALL_FILE=ofm_webtier_linux_11.1.1.9.0_64_disk1_1of1.zip
ENGINE_PATH=/sw/webtier/11gR1/Oracle_WT1
INVENTORY_PATH=/sw/webtier/inventories/11gR1
INVENTORY_GROUP=${OS_GROUPNAME}

INSTANCE_NAME=baseInstance
INSTANCE_HOME=${ENGINE_PATH}/../instances/${INSTANCE_NAME}

COMP_NAME_1=worker1
COMP_PORT_1=10080
COMP_SSL_1=10443
COMP_ADMIN_1=10099

COMP_NAME_2=worker2
COMP_PORT_2=10180
COMP_SSL_2=10543
COMP_ADMIN_2=10199


# (1) ResponseFile
cat << EOF > ${BASEDIR}/rsp
[ENGINE]
Response File Version=1.0.0.0.0

[GENERIC]
INSTALL AND CONFIGURE TYPE=false
INSTALL AND CONFIGURE LATER TYPE=true

ORACLE_HOME=${ENGINE_PATH}
MIDDLEWARE_HOME=${ENGINE_PATH}/..

DECLINE_SECURITY_UPDATES=true
SECURITY_UPDATES_VIA_MYORACLESUPPORT=true
SKIP_SOFTWARE_UPDATES=true
EOF


# (2) Inventory
cat << EOF > ${BASEDIR}/loc
inventory_loc=${INVENTORY_PATH}
inst_group=${INVENTORY_GROUP}
EOF


# (3) Installation
cd ${BASEDIR} && jar -xf ${OHS_INSTALL_FILE}
chmod 700 ${BASEDIR}/Disk1/runInstaller
chmod 700 ${BASEDIR}/Disk1/install/*/runInstaller
chmod 700 ${BASEDIR}/Disk1/install/*/unzip

${BASEDIR}/Disk1/runInstaller -silent -responseFile ${BASEDIR}/rsp -invPtrLoc ${BASEDIR}/loc
```





## 3.2 Instance

```sh
# (4) Instance
${ENGINE_PATH}/opmn/bin/opmnctl createinstance -oracleInstance ${INSTANCE_HOME} -instanceName ${INSTANCE_NAME} -adminRegistration OFF
```





## 3.3 Component

```sh
# (5) Component
${ENGINE_PATH}/opmn/bin/opmnctl createcomponent -oracleInstance ${INSTANCE_HOME} -componentName ${COMP_NAME_1} -listenPort ${COMP_PORT_1} -sslPort ${COMP_SSL_1} -proxyPort ${COMP_ADMIN_1} -componentType OHS

${ENGINE_PATH}/opmn/bin/opmnctl createcomponent -oracleInstance ${INSTANCE_HOME} -componentName ${COMP_NAME_2} -listenPort ${COMP_PORT_2} -sslPort ${COMP_SSL_2} -proxyPort ${COMP_ADMIN_2} -componentType OHS

## delete command ##
# ${ENGINE_PATH}/opmn/bin/opmnctl deletecomponent -oracleInstance ${INSTANCE_HOME} -componentName <componentName> -componentType OHS
```





## 3.4 Create Component Scripts (start, stop, ps)

```sh
# (6) Create Component Scripts (start, stop, ps)
cat << "EOF" > ${INSTANCE_HOME}/start.sh
#!/usr/bin/bash
BASEDIR=$(realpath $(dirname $0))
${BASEDIR}/bin/opmnctl startall
EOF


cat << "EOF" > ${INSTANCE_HOME}/stop.sh
#!/usr/bin/bash
BASEDIR=$(realpath $(dirname $0))
${BASEDIR}/bin/opmnctl stopall
EOF


cat << "EOF" > ${INSTANCE_HOME}/status.sh
#!/usr/bin/bash
BASEDIR=$(realpath $(dirname $0))
${BASEDIR}/bin/opmnctl status -l
EOF

chmod 700 ${INSTANCE_HOME}/*.sh
```
