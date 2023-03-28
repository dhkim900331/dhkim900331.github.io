---
date: 2023-02-10 08:06:28 +0900
layout: post
title: "[Middleware/WebLogic] All In One Script For 11gR1"
tags: [Middleware, WebLogic, Installation, WLST, Python]
typora-root-url: ..
---

# 1. 개요

WebLogic 11gR1 테스트 환경을 자동 재구축을 위해 모든 기본 설치 환경을 집약한다.



# 2. 설명

All-In-One-Script-For-11gR1.sh 실행으로 다음 환경을 구성하도록 한다.

- AdminServer (TCP 8001 , console account : weblogic, weblogic1)
- Managed M1 (TCP 8002)
- Managed M2 (TCP 8003)
- myCluster (M1, M2)
- /sw/app/{testApp, PostDataTest} deployed on myCluster



# 3. Script

## 3.1 Engine

```sh
BASEDIR=/sw/installFiles
OS_USERNAME=$(id --user --name)
OS_GROUPNAME=$(id --group --name)

WLS_INSTALL_FILE=${BASEDIR}/wls1036_generic.jar
JAVA_HOME=/sw/jdk/jdk1.6.0_45

WLS_INSTALL_PATH=/sw/weblogic/11gR1
INVENTORY_PATH=/sw/weblogic/inventories/11gR1
INVENTORY_GROUP=${OS_GROUPNAME}

DOMAIN_NAME=base_domain
DOMAIN_HOME=${WLS_INSTALL_PATH}/domains/${DOMAIN_NAME}

HOSTNAME=wls.local
CONSOLE_USERNAME=weblogic
CONSOLE_PASSWORD=weblogic1

HOSTNAME=wls.local
ADM_ADDR=${HOSTNAME}
ADM_PORT=8001
ADM_USERNAME=weblogic
ADM_PASSWORD=weblogic1

M1_SVR_NAME=M1
M1_SVR_ADDR=${HOSTNAME}
M1_SVR_PORT=8002
M2_SVR_NAME=M2
M2_SVR_ADDR=${HOSTNAME}
M2_SVR_PORT=8003
CLUSTER_NAME=myCluster

APP_HOME=/sw/app
APP_1=testApp
APP_2=PostDataTest


# (1) silent.xml
# https://docs.oracle.com/cd/E24329_01/doc.1211/e24492/silent.htm#WLSIG185
# https://oracle-base.com/articles/11g/weblogic-silent-installation-11g
# wls1036_generic.jar:lpr.xml or gpr.xml

cat << EOF > ${BASEDIR}/silent.xml
<?xml version="1.0" encoding="UTF-8"?>
<bea-installer>
 <input-fields>
  <data-value name="BEAHOME" value="${WLS_INSTALL_PATH}"/>
  <data-value name="WLS_INSTALL_DIR" value="${WLS_INSTALL_PATH}/wlserver_10.3"/>
  <!--<data-value name="COMPONENT_PATHS" value="WebLogic Server/Core Application Server|WebLogic Server/Administration Console|WebLogic Server/Web 2.0 HTTP Pub-Sub Server|WebLogic Server/WebLogic SCA|WebLogic Server/WebLogic JDBC Drivers|WebLogic Server/Third Party JDBC Drivers|WebLogic Server/WebLogic Server Clients|WebLogic Server/WebLogic Web Server Plugins"/>-->
    <data-value name="COMPONENT_PATHS" value="WebLogic Server"/>
  <data-value name="INSTALL_SHORTCUT_IN_ALL_USERS_FOLDER" value="no"/>
  <data-value name="LOCAL_JVMS" value="${JAVA_HOME}"/>
 </input-fields>
</bea-installer>
EOF


# (2) Installation
# https://docs.oracle.com/cd/E24329_01/doc.1211/e24492/silent.htm#CIHCAHGC

${JAVA_HOME}/bin/java -jar ${WLS_INSTALL_FILE} -mode=silent -silent_xml=${BASEDIR}/silent.xml
```



## 3.2 Domain

```sh
# (4) Domain
# https://docs.oracle.com/cd/E12839_01/web.1111/e13715/domains.htm#WLSTG157
# wlserver_10.3/common/templates/scripts/wlst/basicWLSDomain.py

${WLS_INSTALL_PATH}/wlserver_10.3/common/bin/wlst.sh << EOF
readTemplate('${WLS_INSTALL_PATH}/wlserver_10.3/common/templates/domains/wls.jar')

# https://docs.oracle.com/cd/E12839_01/web.1111/e13813/reference.htm#WLSTC314
setOption('JavaHome', '${JAVA_HOME}');
setOption('ServerStartMode', 'prod')
setOption('OverwriteDomain', 'true')

cd('/')
cd('Security/base_domain/User/${ADM_USERNAME}')
cmo.setPassword('${ADM_PASSWORD}')

cd('Servers/AdminServer')
set('ListenAddress','${ADM_ADDR}')
set('ListenPort', ${ADM_PORT})

writeDomain('${DOMAIN_HOME}')
closeTemplate()
exit()
EOF
```



## 3.3 Startup AdminServer

```sh
# (5) Create boot.properties
cat << EOF > ${DOMAIN_HOME}/boot.properties
username=${ADM_USERNAME}
password=${ADM_PASSWORD}
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
connect('${ADM_USERNAME}','${ADM_PASSWORD}','${ADM_ADDR}:${ADM_PORT}')
edit()
startEdit()

## Create Managed
cd('/')
cmo.createServer('${M1_SVR_NAME}')
cd('/Servers/${M1_SVR_NAME}')
cmo.setListenAddress('${M1_SVR_ADDR}')
cmo.setListenPort(${M1_SVR_PORT})

cd('/Servers/${M1_SVR_NAME}/Log/${M1_SVR_NAME}')
cmo.setLogFileSeverity("Info")
cmo.setStdoutSeverity("Info")
cmo.setDomainLogBroadcastSeverity("Off")
cmo.setRotationType("byTime")

cd('/Servers/${M1_SVR_NAME}/WebServer/${M1_SVR_NAME}/WebServerLog/${M1_SVR_NAME}')
cmo.setNumberOfFilesLimited(True)
cmo.setRotationType("byTime")

cd('/')
cmo.createServer('${M2_SVR_NAME}')
cd('/Servers/${M2_SVR_NAME}')
cmo.setListenAddress('${M2_SVR_ADDR}')
cmo.setListenPort(${M2_SVR_PORT})

cd('/Servers/${M2_SVR_NAME}/Log/${M2_SVR_NAME}')
cmo.setLogFileSeverity("Info")
cmo.setStdoutSeverity("Info")
cmo.setDomainLogBroadcastSeverity("Off")
cmo.setRotationType("byTime")

cd('/Servers/${M2_SVR_NAME}/WebServer/${M2_SVR_NAME}/WebServerLog/${M2_SVR_NAME}')
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
connect('${ADM_USERNAME}','${ADM_PASSWORD}','${ADM_ADDR}:${ADM_PORT}')
edit()
startEdit()

## Create Cluster
cd('/')
cmo.createCluster('${CLUSTER_NAME}')
cd('/Clusters/${CLUSTER_NAME}')
cmo.setClusterMessagingMode('unicast')

## Assign Managed to Cluster
cd('/')
cd('/Servers/${M1_SVR_NAME}')
cmo.setCluster(getMBean('/Clusters/${CLUSTER_NAME}'))

cd('/')
cd('/Servers/${M2_SVR_NAME}')
cmo.setCluster(getMBean('/Clusters/${CLUSTER_NAME}'))

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
connect('${ADM_USERNAME}','${ADM_PASSWORD}','${ADM_ADDR}:${ADM_PORT}')
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
cat << "EOF" > ${DOMAIN_HOME}/startA.sh
#!/bin/sh
DOMAIN_NAME=#DOMAIN_NAME#
DOMAIN_HOME=#DOMAIN_HOME#
SERVER_NAME=#SERVER_NAME#
SERVER_PORT=#SERVER_PORT#
BOOT_PROPERTIES=${DOMAIN_HOME}/boot.properties

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
WAS_PID=$(${DOMAIN_HOME}/psA.sh)
if [ "$WAS_PID" != "" ]; then
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

JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.system.BootIdentityFile=${BOOT_PROPERTIES}"
export JAVA_OPTIONS

USER_MEM_ARGS="${USER_MEM_ARGS} -D${SERVER_NAME}"
USER_MEM_ARGS="${USER_MEM_ARGS} -Dserver.name=${SERVER_NAME} -Dserver.port=${SERVER_PORT}"
USER_MEM_ARGS="${USER_MEM_ARGS} -Xms1024m -Xmx1024m -XX:PermSize=256m -XX:MaxPermSize=256m"
USER_MEM_ARGS="${USER_MEM_ARGS} -Djava.net.preferIPv4Stack=true -Djava.net.preferIPv6Addresses=false -Dweblogic.wsee.skip.async.response=true"
USER_MEM_ARGS="${USER_MEM_ARGS} -D_Offline_FileDataArchive=true -Dweblogic.connector.ConnectionPoolProfilingEnabled=false -Dcom.bea.wlw.netui.disableInstrumentation=true"
export USER_MEM_ARGS

mv ${NOHUP_LOG}/${SERVER_NAME}.out ${NOHUP_LOG}/${SERVER_NAME}.out.${LOG_TIME}
nohup ${DOMAIN_HOME}/bin/startWebLogic.sh > ${NOHUP_LOG}/${SERVER_NAME}.out 2>&1 &
#sleep 1
#tail -f ${NOHUP_LOG}/${SERVER_NAME}.out
EOF


cat << "EOF" > ${DOMAIN_HOME}/stopA.sh
#!/bin/sh
DOMAIN_HOME=#DOMAIN_HOME#
SERVER_ADDR=#SERVER_ADDR#
SERVER_PORT=#SERVER_PORT#

. ${DOMAIN_HOME}/bin/setDomainEnv.sh

##### User Check #####
USER=#OS_USERNAME#
if [ "$USER" != $(/usr/bin/whoami) ]; then
     echo "* you do not have permission. *"
     exit;
fi
####################

## Process Check ##
WAS_PID=$(${DOMAIN_HOME}/psA.sh)
if [ "$WAS_PID" == "" ]; then
     echo "Server already Stopped."
     exit;
fi
###################

java weblogic.WLST << INNER_EOF
connect(url='${SERVER_ADDR}:${SERVER_PORT}')
shutdown(force='true')
exit()
INNER_EOF
EOF


cat << "EOF" > ${DOMAIN_HOME}/logA.sh
#!/bin/sh
DOMAIN_HOME=#DOMAIN_HOME#
SERVER_NAME=#SERVER_NAME#

LOG_HOME=${DOMAIN_HOME}/logs
NOHUP_LOG=${LOG_HOME}/nohup
tail -10f ${NOHUP_LOG}/${SERVER_NAME}.out
EOF


cat << "EOF" > ${DOMAIN_HOME}/psA.sh
#!/bin/sh
SERVER_NAME=#SERVER_NAME#
ps -ef | grep "java" | grep "weblogic.Server" | grep "D${SERVER_NAME}"
EOF

sed -i "s|#OS_USERNAME#|${OS_USERNAME}|g" ${DOMAIN_HOME}/*A.sh
sed -i "s|#DOMAIN_NAME#|${DOMAIN_NAME}|g" ${DOMAIN_HOME}/*A.sh
sed -i "s|#DOMAIN_HOME#|${DOMAIN_HOME}|g" ${DOMAIN_HOME}/*A.sh
sed -i "s|#SERVER_NAME#|AdminServer|g" ${DOMAIN_HOME}/*A.sh
sed -i "s|#SERVER_ADDR#|${ADM_ADDR}|g" ${DOMAIN_HOME}/*A.sh
sed -i "s|#SERVER_PORT#|${ADM_PORT}|g" ${DOMAIN_HOME}/*A.sh


# Managed Server (start, stop, log, ps)
cat << "EOF" > ${DOMAIN_HOME}/startM.sh
#!/bin/sh
DOMAIN_NAME=#DOMAIN_NAME#
DOMAIN_HOME=#DOMAIN_HOME#
SERVER_NAME=#SERVER_NAME#
SERVER_PORT=#SERVER_PORT#
ADM_URL="t3://#ADM_ADDR#:#ADM_PORT#"
BOOT_PROPERTIES=${DOMAIN_HOME}/boot.properties

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
WAS_PID=$(${DOMAIN_HOME}/ps${SERVER_NAME}.sh)
if [ "$WAS_PID" != "" ]; then
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

JAVA_OPTIONS="${JAVA_OPTIONS} -Dweblogic.system.BootIdentityFile=${BOOT_PROPERTIES}"
export JAVA_OPTIONS

USER_MEM_ARGS="${USER_MEM_ARGS} -D${SERVER_NAME}"
USER_MEM_ARGS="${USER_MEM_ARGS} -Dserver.name=${SERVER_NAME} -Dserver.port=${SERVER_PORT}"
USER_MEM_ARGS="${USER_MEM_ARGS} -Xms1024m -Xmx1024m -XX:PermSize=256m -XX:MaxPermSize=256m"
USER_MEM_ARGS="${USER_MEM_ARGS} -Djava.net.preferIPv4Stack=true -Djava.net.preferIPv6Addresses=false -Dweblogic.wsee.skip.async.response=true"
USER_MEM_ARGS="${USER_MEM_ARGS} -D_Offline_FileDataArchive=true -Dweblogic.connector.ConnectionPoolProfilingEnabled=false -Dcom.bea.wlw.netui.disableInstrumentation=true"
export USER_MEM_ARGS

mv ${NOHUP_LOG}/${SERVER_NAME}.out ${NOHUP_LOG}/${SERVER_NAME}.out.${LOG_TIME}
nohup ${DOMAIN_HOME}/bin/startManagedWebLogic.sh ${SERVER_NAME} ${ADM_URL}> ${NOHUP_LOG}/${SERVER_NAME}.out 2>&1 &
#sleep 1
#tail -f ${NOHUP_LOG}/${SERVER_NAME}.out
EOF


cat << "EOF" > ${DOMAIN_HOME}/stopM.sh
#!/bin/sh
DOMAIN_HOME=#DOMAIN_HOME#
SERVER_NAME=#SERVER_NAME#
SERVER_ADDR=#SERVER_ADDR#
SERVER_PORT=#SERVER_PORT#

. ${DOMAIN_HOME}/bin/setDomainEnv.sh

##### User Check #####
USER=#OS_USERNAME#
if [ "$USER" != $(/usr/bin/whoami) ]; then
     echo "* you do not have permission. *"
     exit;
fi
####################

## Process Check ##
WAS_PID=$(${DOMAIN_HOME}/ps${SERVER_NAME}.sh)
if [ "$WAS_PID" == "" ]; then
     echo "Server already Stopped."
     exit;
fi
###################

java weblogic.WLST << INNER_EOF
connect(url='${SERVER_ADDR}:${SERVER_PORT}')
shutdown(force='true')
exit()
INNER_EOF
EOF


cat << "EOF" > ${DOMAIN_HOME}/logM.sh
#!/bin/sh
DOMAIN_HOME=#DOMAIN_HOME#
SERVER_NAME=#SERVER_NAME#

LOG_HOME=${DOMAIN_HOME}/logs
NOHUP_LOG=${LOG_HOME}/nohup
tail -10f ${NOHUP_LOG}/${SERVER_NAME}.out
EOF


cat << "EOF" > ${DOMAIN_HOME}/psM.sh
#!/bin/sh
SERVER_NAME=#SERVER_NAME#
ps -ef | grep "java" | grep "weblogic.Server" | grep "D${SERVER_NAME}"
EOF


cp ${DOMAIN_HOME}/startM.sh ${DOMAIN_HOME}/start${M1_SVR_NAME}.sh
cp ${DOMAIN_HOME}/stopM.sh ${DOMAIN_HOME}/stop${M1_SVR_NAME}.sh
cp ${DOMAIN_HOME}/logM.sh ${DOMAIN_HOME}/log${M1_SVR_NAME}.sh
cp ${DOMAIN_HOME}/psM.sh ${DOMAIN_HOME}/ps${M1_SVR_NAME}.sh

cp ${DOMAIN_HOME}/startM.sh ${DOMAIN_HOME}/start${M2_SVR_NAME}.sh
cp ${DOMAIN_HOME}/stopM.sh ${DOMAIN_HOME}/stop${M2_SVR_NAME}.sh
cp ${DOMAIN_HOME}/logM.sh ${DOMAIN_HOME}/log${M2_SVR_NAME}.sh
cp ${DOMAIN_HOME}/psM.sh ${DOMAIN_HOME}/ps${M2_SVR_NAME}.sh

sed -i "s|#OS_USERNAME#|${OS_USERNAME}|g" ${DOMAIN_HOME}/*${M1_SVR_NAME}.sh
sed -i "s|#DOMAIN_NAME#|${DOMAIN_NAME}|g" ${DOMAIN_HOME}/*${M1_SVR_NAME}.sh
sed -i "s|#DOMAIN_HOME#|${DOMAIN_HOME}|g" ${DOMAIN_HOME}/*${M1_SVR_NAME}.sh
sed -i "s|#SERVER_NAME#|${M1_SVR_NAME}|g" ${DOMAIN_HOME}/*${M1_SVR_NAME}.sh
sed -i "s|#SERVER_ADDR#|${M1_SVR_ADDR}|g" ${DOMAIN_HOME}/*${M1_SVR_NAME}.sh
sed -i "s|#SERVER_PORT#|${M1_SVR_PORT}|g" ${DOMAIN_HOME}/*${M1_SVR_NAME}.sh
sed -i "s|#ADM_ADDR#|${ADM_ADDR}|g" ${DOMAIN_HOME}/*${M1_SVR_NAME}.sh
sed -i "s|#ADM_PORT#|${ADM_PORT}|g" ${DOMAIN_HOME}/*${M1_SVR_NAME}.sh

sed -i "s|#OS_USERNAME#|${OS_USERNAME}|g" ${DOMAIN_HOME}/*${M2_SVR_NAME}.sh
sed -i "s|#DOMAIN_NAME#|${DOMAIN_NAME}|g" ${DOMAIN_HOME}/*${M2_SVR_NAME}.sh
sed -i "s|#DOMAIN_HOME#|${DOMAIN_HOME}|g" ${DOMAIN_HOME}/*${M2_SVR_NAME}.sh
sed -i "s|#SERVER_NAME#|${M2_SVR_NAME}|g" ${DOMAIN_HOME}/*${M2_SVR_NAME}.sh
sed -i "s|#SERVER_ADDR#|${M2_SVR_ADDR}|g" ${DOMAIN_HOME}/*${M2_SVR_NAME}.sh
sed -i "s|#SERVER_PORT#|${M2_SVR_PORT}|g" ${DOMAIN_HOME}/*${M2_SVR_NAME}.sh
sed -i "s|#ADM_ADDR#|${ADM_ADDR}|g" ${DOMAIN_HOME}/*${M2_SVR_NAME}.sh
sed -i "s|#ADM_PORT#|${ADM_PORT}|g" ${DOMAIN_HOME}/*${M2_SVR_NAME}.sh

chmod 700 ${DOMAIN_HOME}/*.sh
rm ${DOMAIN_HOME}/*M.sh
```