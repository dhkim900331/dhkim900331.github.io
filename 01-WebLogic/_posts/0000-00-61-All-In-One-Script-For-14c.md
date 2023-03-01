---
date: 2023-02-10 08:06:28 +0900
layout: post
title: "[WebLogic] All In One Script For 14c"
tags: [WebLogic, Installation, WLST, Python]
typora-root-url: ..
---

# 1. 개요

WebLogic 14c 테스트 환경을 자동 재구축을 위해 모든 기본 설치 환경을 집약한다.



# 2. 설명

All-In-One-Script-For-14c.sh 실행으로 다음 환경을 구성하도록 한다.

- AdminServer (TCP 8001 , console account : weblogic, weblogic1)
- Managed M1 (TCP 8002)
- Managed M2 (TCP 8003)
- myCluster (M1, M2)
- /sw/app/testApp, cohSessonApp deployed on myCluster



# 3. Script

## 3.1 Engine

```sh
BASEDIR=/tmp/installFiles_14c
WLS_INSTALL_FILE=fmw_14.1.1.0.0_wls.jar
JAVA_HOME=/sw/jdk/jdk1.8.0_351

ENGINE_PATH=/sw/weblogic/14c
INVENTORY_PATH=/sw/weblogic/inventories/14c
INVENTORY_GROUP=$(id --group --name)

DOMAIN_NAME=base_domain
DOMAIN_HOME=${ENGINE_PATH}/domains/${DOMAIN_NAME}

HOSTNAME=wls.local
CONSOLE_USERNAME=weblogic
CONSOLE_PASSWORD=weblogic1

ADM_SVR_PORT=8001
M1_SVR_NAME=M1
M1_SVR_PORT=8002
M2_SVR_NAME=M2
M2_SVR_PORT=8003
CLUSTER_NAME=myCluster

APP_HOME=/sw/app
APP_1=testApp
APP_2=cohSessionApp


# (1) ResponseFile
# https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/ouirf/sample-response-files-silent-installation-and-deinstallation.html#GUID-65B11C03-B559-41F1-B9B4-B7276491E580

cat << EOF > ${BASEDIR}/rsp
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
ORACLE_HOME=${ENGINE_PATH}
 
#Set this variable value to the Installation Type selected. 
#e.g WebLogic Server, Coherence, Complete with Examples
INSTALL_TYPE=WebLogic Server
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

${JAVA_HOME}/bin/java -jar ${BASEDIR}/${WLS_INSTALL_FILE} -silent -responseFile ${BASEDIR}/rsp -invPtrLoc ${BASEDIR}/loc
```



## 3.2 Domain

```sh
# (4) Domain
# https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wlstg/domains.html#GUID-5FC3AA22-BCB0-4F98-801A-8EBC5E05DC6A

${ENGINE_PATH}/wlserver/common/bin/wlst.sh << EOF
readTemplate('${ENGINE_PATH}/wlserver/common/templates/wls/wls.jar')

# https://docs.oracle.com/middleware/1213/wls/WLSTC/reference.htm#WLSTC314
setOption('JavaHome', '${JAVA_HOME}');
setOption('ServerStartMode', 'prod')
setOption('OverwriteDomain', 'true')

cd('/')
cd('Security/base_domain/User/${CONSOLE_USERNAME}')
cmo.setPassword('${CONSOLE_PASSWORD}')

cd('Servers/AdminServer')
set('ListenAddress','${HOSTNAME}')
set('ListenPort', ${ADM_SVR_PORT})

writeDomain('${DOMAIN_HOME}')
closeTemplate()

exit()
EOF
```



## 3.3 Startup AdminServer

```sh
# (5) Create boot.properties
cat << EOF > ${DOMAIN_HOME}/boot.properties
username=${CONSOLE_USERNAME}
password=${CONSOLE_PASSWORD}
EOF


# (6) Start-up AdminServer
# https://unix.stackexchange.com/questions/405250/passing-and-setting-variables-in-a-heredoc

DATE=$(date +%Y%m%d_%H%M%S)
tmpStdFile=/tmp/AdminServer.${DATE}
nohup ${DOMAIN_HOME}/bin/startWebLogic.sh "-Dweblogic.system.BootIdentityFile=${DOMAIN_HOME}/boot.properties" > ${tmpStdFile} 2>&1 &

bash << EOF
while true
do
 R="\$(grep "RUNNING mode" ${tmpStdFile})"
 if [ "x\${R}" == "x" ]; then
  sleep 3
  echo "Sleeping for 3 Seconds"
  else
  echo "AdminServer has Started"
  break;
 fi
done
EOF
```



## 3.4 Create Managed Server

```sh
# (7) Create Managed Servers
# https://oracle-base.com/articles/web/wlst-create-managed-server

. ${DOMAIN_HOME}/bin/setDomainEnv.sh
java weblogic.WLST << EOF
connect('${CONSOLE_USERNAME}','${CONSOLE_PASSWORD}','${HOSTNAME}:${ADM_SVR_PORT}')
edit()
startEdit()

## Create Managed
NAME="${M1_SVR_NAME}"
PORT="${M1_SVR_PORT}"
cd('/')
cmo.createServer(NAME)
cd('/Servers/' + NAME)
cmo.setListenAddress('${HOSTNAME}')
cmo.setListenPort(int(PORT))

cd('/Servers/' + NAME + '/Log/' + NAME)
cmo.setLogFileSeverity("Info")
cmo.setStdoutSeverity("Info")
cmo.setDomainLogBroadcastSeverity("Off")
cmo.setRotationType("byTime")

cd('/Servers/' + NAME + '/WebServer/' + NAME + '/WebServerLog/' + NAME)
cmo.setNumberOfFilesLimited(True)
cmo.setRotationType("byTime")

NAME="${M2_SVR_NAME}"
PORT="${M2_SVR_PORT}"
cd('/')
cmo.createServer(NAME)
cd('/Servers/' + NAME)
cmo.setListenAddress('${HOSTNAME}')
cmo.setListenPort(int(PORT))

cd('/Servers/' + NAME + '/Log/' + NAME)
cmo.setLogFileSeverity("Info")
cmo.setStdoutSeverity("Info")
cmo.setDomainLogBroadcastSeverity("Off")
cmo.setRotationType("byTime")

cd('/Servers/' + NAME + '/WebServer/' + NAME + '/WebServerLog/' + NAME)
cmo.setNumberOfFilesLimited(True)
cmo.setRotationType("byTime")

save()
activate()
disconnect()
exit()
EOF
```



## 3.5 Cluster

```sh
# (8) Assign Managed Server to Cluster
# https://oracle-base.com/articles/web/wlst-create-managed-server
# https://oracle-base.com/articles/web/wlst-create-cluster

. ${DOMAIN_HOME}/bin/setDomainEnv.sh
java weblogic.WLST << EOF
connect('${CONSOLE_USERNAME}','${CONSOLE_PASSWORD}','${HOSTNAME}:${ADM_SVR_PORT}')
edit()
startEdit()

## Create Cluster
CNAME="${CLUSTER_NAME}"
cd('/')
cmo.createCluster(CNAME)
cd('/Clusters/' + CNAME)
cmo.setClusterMessagingMode('unicast')

## Assign Managed to Cluster
NAME="${M1_SVR_NAME}"
cd('/')
cd('/Servers/' + NAME)
cmo.setCluster(getMBean('/Clusters/' + CNAME))

NAME="${M2_SVR_NAME}"
cd('/')
cd('/Servers/' + NAME)
cmo.setCluster(getMBean('/Clusters/' + CNAME))

save()
activate()
disconnect()
exit()
EOF
```



## 3.6 Deploy App

```sh
# (9) Deploy App
# https://docs.oracle.com/middleware/1213/wls/WLSTC/reference.htm#WLSTC200
. ${DOMAIN_HOME}/bin/setDomainEnv.sh
java weblogic.WLST << EOF
connect('${CONSOLE_USERNAME}','${CONSOLE_PASSWORD}','${HOSTNAME}:${ADM_SVR_PORT}')
edit()
startEdit()

deploy(appName='${APP_1}', path='${APP_HOME}/${APP_1}', targets='${CLUSTER_NAME}', stageMode='nostage', block='true')
deploy(appName='${APP_2}', path='${APP_HOME}/${APP_2}', targets='${CLUSTER_NAME}', stageMode='nostage', block='true')
startApplication('${APP_1}')
startApplication('${APP_2}')

#stopApplication('${APP_1}')
#stopApplication('${APP_2}')
#undeploy(appName='${APP_1}')
#undeploy(appName='${APP_2}')

save()
activate()
disconnect()
exit()
EOF
```



## 3.7. Create Instances Scripts

```sh
# (10) Create Instance Scripts

# AdminServer (start, stop, log, ps)
cat << EOF_1 > ${DOMAIN_HOME}/startA.sh
#!/bin/sh
DOMAIN_NAME=${DOMAIN_NAME}
DOMAIN_HOME=${DOMAIN_HOME}
SERVER_NAME=AdminServer
SERVER_PORT=8001
EOF_1

cat << "EOF_2" >> ${DOMAIN_HOME}/startA.sh
BOOT_PROPERTIES=${DOMAIN_HOME}/boot.properties

LOG_HOME=${DOMAIN_HOME}/logs
NOHUP_LOG=${LOG_HOME}/nohup
GC_LOG=${LOG_HOME}/gc
HEAPDUMP_DIR=${LOG_HOME}/heapdump
LOG_TIME=$(date +%y%m%d_%H%M)

##### Make Path #####
mkdir -p ${LOG_HOME} ${NOHUP_LOG} ${GC_LOG} ${HEAPDUMP_DIR}
###################

## Process Check ##
WAS_PID=$(ps -ef | grep java | grep weblogic.Server | grep "D${SERVER_NAME}" | awk '{print $2}');
if [ "${WAS_PID}" != "" ]; then
     echo "Server already Started... Please shutdown Server!!"
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

JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.system.BootIdentityFile=${BOOT_PROPERTIES}"
export JAVA_OPTIONS

USER_MEM_ARGS="${USER_MEM_ARGS} -D${SERVER_NAME}"
USER_MEM_ARGS="${USER_MEM_ARGS} -Dserver.name=${SERVER_NAME} -Dserver.port=${SERVER_PORT}"
USER_MEM_ARGS="${USER_MEM_ARGS} -Xms1024m -Xmx1024m -XX:MetaspaceSize=256m -XX:MaxMetaspaceSize=256m"
USER_MEM_ARGS="${USER_MEM_ARGS} -Djava.net.preferIPv4Stack=true -Djava.net.preferIPv6Addresses=false -Dweblogic.wsee.skip.async.response=true"
USER_MEM_ARGS="${USER_MEM_ARGS} -D_Offline_FileDataArchive=true -Dweblogic.connector.ConnectionPoolProfilingEnabled=false -Dcom.bea.wlw.netui.disableInstrumentation=true"
export USER_MEM_ARGS

mv ${NOHUP_LOG}/${SERVER_NAME}.out ${NOHUP_LOG}/${SERVER_NAME}.out.${LOG_TIME}
nohup ${DOMAIN_HOME}/bin/startWebLogic.sh > ${NOHUP_LOG}/${SERVER_NAME}.out 2>&1 &
#sleep 1
#tail -f ${NOHUP_LOG}/${SERVER_NAME}.out
EOF_2


cat << EOF > ${DOMAIN_HOME}/stop.py
connect(url=sys.argv[1])
shutdown(force='true')
exit()
EOF


cat << EOF > ${DOMAIN_HOME}/stopA.sh
. ./bin/setDomainEnv.sh
SERVER_PORT=${ADM_SVR_PORT}
java weblogic.WLST stop.py ${HOSTNAME}:\${SERVER_PORT}
EOF


cat << EOF > ${DOMAIN_HOME}/logA.sh
DOMAIN_HOME=${DOMAIN_HOME}
LOG_HOME=\${DOMAIN_HOME}/logs
NOHUP_LOG=\${LOG_HOME}/nohup
SERVER_NAME=AdminServer
tail -10f \${NOHUP_LOG}/\${SERVER_NAME}.out
EOF


cat << EOF > ${DOMAIN_HOME}/psA.sh
SERVER_NAME=AdminServer
ps -ef | grep java | grep weblogic.Server | grep "D\${SERVER_NAME}" | awk '{print $2}'
EOF


# Managed Server-1 (start, stop, log, ps)
cat << EOF_1 > ${DOMAIN_HOME}/startM1.sh
#!/bin/sh
DOMAIN_NAME=${DOMAIN_NAME}
DOMAIN_HOME=${DOMAIN_HOME}
SERVER_NAME=${M1_SVR_NAME}
SERVER_PORT=${M1_SVR_PORT}
ADM_URL="t3://${HOSTNAME}:${ADM_SVR_PORT}"
EOF_1

cat << "EOF_2" >> ${DOMAIN_HOME}/startM1.sh
BOOT_PROPERTIES=${DOMAIN_HOME}/boot.properties

LOG_HOME=${DOMAIN_HOME}/logs
NOHUP_LOG=${LOG_HOME}/nohup
GC_LOG=${LOG_HOME}/gc
HEAPDUMP_DIR=${LOG_HOME}/heapdump
LOG_TIME=$(date +%y%m%d_%H%M)

##### Make Path #####
mkdir -p ${LOG_HOME} ${NOHUP_LOG} ${GC_LOG} ${HEAPDUMP_DIR}
###################

## Process Check ##
WAS_PID=$(ps -ef | grep java | grep weblogic.Server | grep "D${SERVER_NAME}" | awk '{print $2}');
if [ "${WAS_PID}" != "" ]; then
     echo "Server already Started... Please shutdown Server!!"
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

JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.system.BootIdentityFile=${BOOT_PROPERTIES}"
export JAVA_OPTIONS

USER_MEM_ARGS="${USER_MEM_ARGS} -D${SERVER_NAME}"
USER_MEM_ARGS="${USER_MEM_ARGS} -Dserver.name=${SERVER_NAME} -Dserver.port=${SERVER_PORT}"
USER_MEM_ARGS="${USER_MEM_ARGS} -Xms1024m -Xmx1024m -XX:MetaspaceSize=256m -XX:MaxMetaspaceSize=256m"
USER_MEM_ARGS="${USER_MEM_ARGS} -Djava.net.preferIPv4Stack=true -Djava.net.preferIPv6Addresses=false -Dweblogic.wsee.skip.async.response=true"
USER_MEM_ARGS="${USER_MEM_ARGS} -D_Offline_FileDataArchive=true -Dweblogic.connector.ConnectionPoolProfilingEnabled=false -Dcom.bea.wlw.netui.disableInstrumentation=true"
export USER_MEM_ARGS

mv ${NOHUP_LOG}/${SERVER_NAME}.out ${NOHUP_LOG}/${SERVER_NAME}.out.${LOG_TIME}
nohup ${DOMAIN_HOME}/bin/startManagedWebLogic.sh ${SERVER_NAME} ${ADM_URL}> ${NOHUP_LOG}/${SERVER_NAME}.out 2>&1 &
#sleep 1
#tail -f ${NOHUP_LOG}/${SERVER_NAME}.out
EOF_2


cat << EOF > ${DOMAIN_HOME}/stop.py
connect(url=sys.argv[1])
shutdown(force='true')
exit()
EOF


cat << EOF > ${DOMAIN_HOME}/stopM1.sh
. ./bin/setDomainEnv.sh
SERVER_PORT=${M1_SVR_PORT}
java weblogic.WLST stop.py ${HOSTNAME}:\${SERVER_PORT}
EOF


cat << EOF > ${DOMAIN_HOME}/logM1.sh
DOMAIN_HOME=${DOMAIN_HOME}
LOG_HOME=\${DOMAIN_HOME}/logs
NOHUP_LOG=\${LOG_HOME}/nohup
SERVER_NAME=${M1_SVR_NAME}
tail -10f \${NOHUP_LOG}/\${SERVER_NAME}.out
EOF


cat << EOF > ${DOMAIN_HOME}/psM1.sh
SERVER_NAME=${M1_SVR_NAME}
ps -ef | grep java | grep weblogic.Server | grep "D\${SERVER_NAME}" | awk '{print $2}'
EOF


# Managed Server-2 (start, stop, log, ps)
cat << EOF_1 > ${DOMAIN_HOME}/startM2.sh
#!/bin/sh
DOMAIN_NAME=${DOMAIN_NAME}
DOMAIN_HOME=${DOMAIN_HOME}
SERVER_NAME=${M2_SVR_NAME}
SERVER_PORT=${M2_SVR_PORT}
ADM_URL="t3://${HOSTNAME}:${ADM_SVR_PORT}"
EOF_1

cat << "EOF_2" >> ${DOMAIN_HOME}/startM2.sh
BOOT_PROPERTIES=${DOMAIN_HOME}/boot.properties

LOG_HOME=${DOMAIN_HOME}/logs
NOHUP_LOG=${LOG_HOME}/nohup
GC_LOG=${LOG_HOME}/gc
HEAPDUMP_DIR=${LOG_HOME}/heapdump
LOG_TIME=$(date +%y%m%d_%H%M)

##### Make Path #####
mkdir -p ${LOG_HOME} ${NOHUP_LOG} ${GC_LOG} ${HEAPDUMP_DIR}
###################

## Process Check ##
WAS_PID=$(ps -ef | grep java | grep weblogic.Server | grep "D${SERVER_NAME}" | awk '{print $2}');
if [ "${WAS_PID}" != "" ]; then
     echo "Server already Started... Please shutdown Server!!"
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

JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.system.BootIdentityFile=${BOOT_PROPERTIES}"
export JAVA_OPTIONS

USER_MEM_ARGS="${USER_MEM_ARGS} -D${SERVER_NAME}"
USER_MEM_ARGS="${USER_MEM_ARGS} -Dserver.name=${SERVER_NAME} -Dserver.port=${SERVER_PORT}"
USER_MEM_ARGS="${USER_MEM_ARGS} -Xms1024m -Xmx1024m -XX:MetaspaceSize=256m -XX:MaxMetaspaceSize=256m"
USER_MEM_ARGS="${USER_MEM_ARGS} -Djava.net.preferIPv4Stack=true -Djava.net.preferIPv6Addresses=false -Dweblogic.wsee.skip.async.response=true"
USER_MEM_ARGS="${USER_MEM_ARGS} -D_Offline_FileDataArchive=true -Dweblogic.connector.ConnectionPoolProfilingEnabled=false -Dcom.bea.wlw.netui.disableInstrumentation=true"
export USER_MEM_ARGS

mv ${NOHUP_LOG}/${SERVER_NAME}.out ${NOHUP_LOG}/${SERVER_NAME}.out.${LOG_TIME}
nohup ${DOMAIN_HOME}/bin/startManagedWebLogic.sh ${SERVER_NAME} ${ADM_URL}> ${NOHUP_LOG}/${SERVER_NAME}.out 2>&1 &
#sleep 1
#tail -f ${NOHUP_LOG}/${SERVER_NAME}.out
EOF_2


cat << EOF > ${DOMAIN_HOME}/stop.py
connect(url=sys.argv[1])
shutdown(force='true')
exit()
EOF


cat << EOF > ${DOMAIN_HOME}/stopM2.sh
. ./bin/setDomainEnv.sh
SERVER_PORT=${M2_SVR_PORT}
java weblogic.WLST stop.py ${HOSTNAME}:\${SERVER_PORT}
EOF


cat << EOF > ${DOMAIN_HOME}/logM2.sh
DOMAIN_HOME=${DOMAIN_HOME}
LOG_HOME=\${DOMAIN_HOME}/logs
NOHUP_LOG=\${LOG_HOME}/nohup
SERVER_NAME=${M2_SVR_NAME}
tail -10f \${NOHUP_LOG}/\${SERVER_NAME}.out
EOF


cat << EOF > ${DOMAIN_HOME}/psM2.sh
SERVER_NAME=${M2_SVR_NAME}
ps -ef | grep java | grep weblogic.Server | grep "D\${SERVER_NAME}" | awk '{print $2}'
EOF
```
