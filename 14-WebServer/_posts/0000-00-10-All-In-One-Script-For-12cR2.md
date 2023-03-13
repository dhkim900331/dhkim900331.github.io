---
date: 2023-03-10 08:59:30 +0900
layout: post
title: "[WebServer/OHS] All In One Script For 12cR2"
tags: [Apache, OHS, Installation, WLST, Jython]
typora-root-url: ..
---

# 1. 개요

Oracle HTTP Server 12cR2 테스트 환경을 자동 재구축을 위해 모든 기본 설치 환경을 집약한다.



# 2. 설명

All-In-One-Script-For-12cR2.sh 실행으로 다음 환경을 구성하도록 한다.

- base_domain
- NodeManager (SecureListner=false, TCP 5556)
- Worker 2ea



# 3. Script

## 3.1 Engine

```sh
BASEDIR=/sw/installFiles_2
OHS_INSTALL_FILE=fmw_12.2.1.4.0_ohs_linux64.bin

ENGINE_PATH=/sw/webtier/12cR2
INVENTORY_PATH=/sw/webtier/inventories/12cR2
INVENTORY_GROUP=$(id --group --name)

DOMAIN_NAME=base_domain
DOMAIN_HOME=${ENGINE_PATH}/domains/${DOMAIN_NAME}

HOSTNAME=wls.local
NM_USERNAME=webtier
NM_PASSWORD=webtier1
NM_ADDR=${HOSTNAME}
NM_PORT=5556

WORKER_NAME_1=worker1
WORKER_ADDR_1=${HOSTNAME}
WORKER_PORT_1=10080
WORKER_SSL_1=10443
WORKER_ADMIN_ADDR_1=${HOSTNAME}
WORKER_ADMIN_PORT_1=10099

WORKER_NAME_2=worker2
WORKER_ADDR_2=${HOSTNAME}
WORKER_PORT_2=10180
WORKER_SSL_2=10543
WORKER_ADMIN_ADDR_2=${HOSTNAME}
WORKER_ADMIN_PORT_2=10199


# (1) ResponseFile
# https://docs.oracle.com/middleware/1213/core/WTINS/standalone_domain.htm
# https://docs.oracle.com/middleware/1212/core/OUIRF/response_file.htm#OUIRF390
# https://dhkim900331.github.io/14-webserver/Install-OHS-12cR2

cat << EOF > ${BASEDIR}/rsp
[ENGINE]
#DO NOT CHANGE THIS.
Response File Version=1.0.0.0.0
 
[GENERIC]
#The oracle home location. This can be an existing Oracle Home or a new Oracle Home
ORACLE_HOME=${ENGINE_PATH}
 
#Set this variable value to the Installation Type selected. e.g. WebLogic Server, Coherence, Complete with Examples.
INSTALL_TYPE=Standalone HTTP Server (Managed independently of WebLogic server)
 
#Set this to true if you wish to decline the security updates. Setting this to true and providing empty string for My Oracle Support username will ignore the Oracle Configuration Manager configuration
DECLINE_SECURITY_UPDATES=true
 
#Set this to true if My Oracle Support Password is specified
SECURITY_UPDATES_VIA_MYORACLESUPPORT=false
EOF


# (2) Inventory
# https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/ouirf/using-oracle-universal-installer-silent-mode.html#GUID-756E3FD9-4094-412F-9BEB-72C5FD51056B
# * inventory.loc 파일 샘플은 문서에 없음

cat << EOF > ${BASEDIR}/loc
inventory_loc=${INVENTORY_PATH}
inst_group=${INVENTORY_GROUP}
EOF


# (3) Installation
# Ref 찾을 수 없음

${BASEDIR}/${OHS_INSTALL_FILE} -silent -responseFile ${BASEDIR}/rsp -invPtrLoc ${BASEDIR}/loc
```





## 3.2 Domain

```sh
# (4) Domain
# https://dhkim900331.github.io/14-webserver/Install-OHS-12cR2#h-33-domain
# https://dhkim900331.github.io/14-webserver/Install-OHS-12cR2#h-34-nodemanager

${ENGINE_PATH}/oracle_common/common/bin/wlst.sh << EOF
selectTemplate('Oracle HTTP Server (Standalone)', '12.2.1.3.0')
loadTemplates()
writeDomain('${DOMAIN_HOME}') 
exit()
EOF
```



## 3.3 NodeManager

```sh
# (5) NodeManager
# https://dhkim900331.github.io/14-webserver/Install-OHS-12cR2#h-34-nodemanager

${ENGINE_PATH}/oracle_common/common/bin/wlst.sh << EOF
readDomain('${DOMAIN_HOME}')
cd('/SecurityConfiguration/${DOMAIN_NAME}')
set('NodeManagerUsername','${NM_USERNAME}')
set('NodeManagerPasswordEncrypted','${NM_PASSWORD}')

cd('/Machine/localmachine/NodeManager/localmachine')
set('ListenAddress','${NM_ADDR}')
set('ListenPort',${NM_PORT})

cd('/NMProperties')
set('SecureListener',false)
updateDomain()
exit()
EOF


# (6) NodeManager SSL disabled
# WLST 으로 update 되지 않아 추가로 해야 한다. 실질적으로 아래가 필수
sed -i 's/SecureListener=true/SecureListener=false/g' ${DOMAIN_HOME}/nodemanager/nodemanager.properties
```



## 3.4 Component

```sh
# (7) Component
${ENGINE_PATH}/oracle_common/common/bin/wlst.sh << EOF
readDomain('${DOMAIN_HOME}')

create('${WORKER_NAME_1}','SystemComponent')
create('${WORKER_NAME_2}','SystemComponent')
delete('ohs1','SystemComponent')

cd('/OHS/${WORKER_NAME_1}')
set('ListenAddress','${WORKER_ADDR_1}')
set('ListenPort','${WORKER_PORT_1}')
set('SSLListenPort','${WORKER_SSL_1}')
set('AdminHost', '${WORKER_ADMIN_ADDR_1}')
set('AdminPort', '${WORKER_ADMIN_PORT_1}')
set('ServerName', 'http://${HOSTNAME}:${WORKER_PORT_1}')

cd('/OHS/${WORKER_NAME_2}')
set('ListenAddress','${WORKER_ADDR_2}')
set('ListenPort','${WORKER_PORT_2}')
set('SSLListenPort','${WORKER_SSL_2}')
set('AdminHost', '${WORKER_ADMIN_ADDR_2}')
set('AdminPort', '${WORKER_ADMIN_PORT_2}')
set('ServerName', 'http://${HOSTNAME}:${WORKER_PORT_2}')

updateDomain()
exit()
EOF
```



## 3.5 Create NodeManager Scripts (start, stop, log, ps)

```sh
# (8) Create NodeManager Scripts (start, stop, log, ps)
cat << "EOF" > ${DOMAIN_HOME}/startNM.sh
#!/usr/bin/bash
BASEDIR=$(realpath $(dirname $0))
SERVER_NAME=nodemanager
DOMAIN_HOME=${BASEDIR}
LOG_HOME=${DOMAIN_HOME}/logs/${SERVER_NAME}
LOG_TIME=$(date +%y%m%d_%H%M)

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
mv ${LOG_HOME}/${SERVER_NAME}.out ${LOG_HOME}/${SERVER_NAME}.out.${LOG_TIME}
nohup ${BASEDIR}/bin/startNodeManager.sh >> ${LOG_HOME}/${SERVER_NAME}.out 2>&1 &
EOF


cat << "EOF" > ${DOMAIN_HOME}/stopNM.sh
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
sleep 1
tail -5 ${LOG_HOME}/${SERVER_NAME}.out
EOF


cat << "EOF" > ${DOMAIN_HOME}/logNM.sh
#!/usr/bin/bash
BASEDIR=$(realpath $(dirname $0))
SERVER_NAME=nodemanager
DOMAIN_HOME=${BASEDIR}
LOG_HOME=${DOMAIN_HOME}/logs/${SERVER_NAME}
tail -10f ${LOG_HOME}/${SERVER_NAME}.out
EOF


cat << "EOF" > ${DOMAIN_HOME}/psNM.sh
#!/usr/bin/bash
BASEDIR=$(realpath $(dirname $0))
DOMAIN_HOME=${BASEDIR}
ps -ef | grep "java" | grep "weblogic.NodeManager -v" | grep "${DOMAIN_HOME}"
EOF
```



## 3.6 Create Component Scripts (start, stop, ps)

```sh
# (9) Create Component Scripts (start, stop, ps)
cat << "EOF" > ${DOMAIN_HOME}/start-worker.sh
#!/usr/bin/bash
BASEDIR=$(realpath $(dirname $0))
DOMAIN_HOME=${BASEDIR}
DOMAIN_NAME=$(basename ${DOMAIN_HOME})
WORKER=#WORKER_NAME#
NM_ADDR=#NM_ADDR#
NM_PORT=#NM_PORT#
NM_USERNAME=#NM_USERNAME#
NM_PASSWORD=#NM_PASSWORD#
WL_HOME=${DOMAIN_HOME}/../../wlserver

##### User Check #####
USER=wasadm
if [ "$USER" != `/usr/bin/whoami` ]; then
     echo "* you do not have permission. *"
     exit;
fi
####################

## Process Check ##
WEB_PID=$(${DOMAIN_HOME}/ps-${WORKER}.sh)
if [ "$WEB_PID" != "" ]; then
     echo "Server already Started."
     exit;
fi
###################

${WL_HOME}/../oracle_common/common/bin/wlst.sh << INNER_EOF
nmConnect('${NM_USERNAME}', '${NM_PASSWORD}', '${NM_ADDR}', '${NM_PORT}', '${DOMAIN_NAME}', '${DOMAIN_HOME}','plain')
nmStart(serverName='${WORKER}', serverType='OHS')
nmServerStatus(serverName='${WORKER}', serverType='OHS')
nmDisconnect()
exit()
INNER_EOF
EOF


cat << "EOF" > ${DOMAIN_HOME}/stop-worker.sh
#!/usr/bin/bash
BASEDIR=$(realpath $(dirname $0))
DOMAIN_HOME=${BASEDIR}
DOMAIN_NAME=$(basename ${DOMAIN_HOME})
WORKER=#WORKER_NAME#
NM_ADDR=#NM_ADDR#
NM_PORT=#NM_PORT#
NM_USERNAME=#NM_USERNAME#
NM_PASSWORD=#NM_PASSWORD#
WL_HOME=${DOMAIN_HOME}/../../wlserver

##### User Check #####
USER=wasadm
if [ "$USER" != `/usr/bin/whoami` ]; then
     echo "* you do not have permission. *"
     exit;
fi
####################

## Process Check ##
WEB_PID=$(${DOMAIN_HOME}/ps-${WORKER}.sh)
if [ "$WEB_PID" == "" ]; then
     echo "Server already Stopped."
     exit;
fi
###################

${WL_HOME}/../oracle_common/common/bin/wlst.sh << INNER_EOF
nmConnect('${NM_USERNAME}', '${NM_PASSWORD}', '${NM_ADDR}', '${NM_PORT}', '${DOMAIN_NAME}', '${DOMAIN_HOME}','plain')
nmKill(serverName='${WORKER}', serverType='OHS')
nmServerStatus(serverName='${WORKER}', serverType='OHS')
nmDisconnect()
exit()
INNER_EOF
EOF


cat << "EOF" > ${DOMAIN_HOME}/ps-worker.sh
#!/usr/bin/bash
BASEDIR=$(realpath $(dirname $0))
DOMAIN_HOME=${BASEDIR}
WORKER=#WORKER_NAME#
ps -ef | grep "httpd" | grep "${WORKER}" | grep "${DOMAIN_HOME}"
EOF


cp ${DOMAIN_HOME}/start-worker.sh ${DOMAIN_HOME}/start-${WORKER_NAME_1}.sh
cp ${DOMAIN_HOME}/stop-worker.sh ${DOMAIN_HOME}/stop-${WORKER_NAME_1}.sh
cp ${DOMAIN_HOME}/ps-worker.sh ${DOMAIN_HOME}/ps-${WORKER_NAME_1}.sh

cp ${DOMAIN_HOME}/start-worker.sh ${DOMAIN_HOME}/start-${WORKER_NAME_2}.sh
cp ${DOMAIN_HOME}/stop-worker.sh ${DOMAIN_HOME}/stop-${WORKER_NAME_2}.sh
cp ${DOMAIN_HOME}/ps-worker.sh ${DOMAIN_HOME}/ps-${WORKER_NAME_2}.sh

sed -i "s/#WORKER_NAME#/${WORKER_NAME_1}/g" ${DOMAIN_HOME}/*${WORKER_NAME_1}.sh
sed -i "s/#NM_ADDR#/${NM_ADDR}/g" ${DOMAIN_HOME}/*${WORKER_NAME_1}.sh
sed -i "s/#NM_PORT#/${NM_PORT}/g" ${DOMAIN_HOME}/*${WORKER_NAME_1}.sh
sed -i "s/#NM_USERNAME#/${NM_USERNAME}/g" ${DOMAIN_HOME}/*${WORKER_NAME_1}.sh
sed -i "s/#NM_PASSWORD#/${NM_PASSWORD}/g" ${DOMAIN_HOME}/*${WORKER_NAME_1}.sh
sed -i "s/#NM_ADDR#/${NM_ADDR}/g" ${DOMAIN_HOME}/*${WORKER_NAME_1}.sh

sed -i "s/#WORKER_NAME#/${WORKER_NAME_2}/g" ${DOMAIN_HOME}/*${WORKER_NAME_2}.sh
sed -i "s/#NM_ADDR#/${NM_ADDR}/g" ${DOMAIN_HOME}/*${WORKER_NAME_2}.sh
sed -i "s/#NM_PORT#/${NM_PORT}/g" ${DOMAIN_HOME}/*${WORKER_NAME_2}.sh
sed -i "s/#NM_USERNAME#/${NM_USERNAME}/g" ${DOMAIN_HOME}/*${WORKER_NAME_2}.sh
sed -i "s/#NM_PASSWORD#/${NM_PASSWORD}/g" ${DOMAIN_HOME}/*${WORKER_NAME_2}.sh
sed -i "s/#NM_ADDR#/${NM_ADDR}/g" ${DOMAIN_HOME}/*${WORKER_NAME_2}.sh
```
