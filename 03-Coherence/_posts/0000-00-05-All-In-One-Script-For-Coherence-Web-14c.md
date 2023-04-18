---
date: 2023-04-19 08:56:19 +0900
layout: post
title: "[Coherence] All In One Script For Coherence Web 14c"
tags: [Coherence, Installation, Web, WLST, Python]
typora-root-url: ..
---

# 1. 개요

Coherence 14c 테스트 환경을 자동 재구축을 위해 모든 기본 설치 환경을 집약한다.



# 2. 설명

All-In-One-Script-For-Coherence--Web-14c.sh 실행으로 다음 환경을 구성하도록 한다.

- Cache Server (TCP 7, TCP 9000~9200, Distributed Cache)



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



## 3.2 Cluster

Coherence 구성을 위해서는 많은 설정 값이 필요하지만, [Using the Default Operational Override File](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/develop-applications/understanding-configuration.html#GUID-8387E29A-EE03-4075-B4E7-D92779335965) 방식을 사용하여, 일부분 설정값만 override 하도록 한다.



```sh
# (4) Cluster Member
# Cache Server에는 WLS Domain과 같은 개념이 없으나, 임의로 만듬

mkdir -p ${DOMAIN_HOME}/logs
cp -pR ${COH_INSTALL_PATH}/coherence/lib ${DOMAIN_HOME}

# https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/develop-applications/setting-cluster.html#GUID-E3DCA888-1155-4E95-BDC7-668719C86F69

cat << EOF > ${DOMAIN_HOME}/lib/tangosol-coherence-${DOMAIN_NAME}.xml
<?xml version='1.0'?>
<coherence xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://xmlns.oracle.com/coherence/coherence-operational-config" xsi:schemaLocation="http://xmlns.oracle.com/coherence/coherence-operational-configcoherence-operational-config.xsd">
   
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
      <port-auto-adjust system-property="coherence.localport.adjust">$((CS_PORT+100))</port-auto-adjust>

      <well-known-addresses> 
        <address id="1" system-property="coherence.wka">${CS_ADDR}</address> 
        <!--<address id="2" system-property="coherence.wka2">${CS_ADDR}</address>-->
      </well-known-addresses>
    </unicast-listener>
     
    <tcp-ring-listener>
      <enabled>false</enabled>
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



## 3.3 Cache

```sh
# (5) Cache (WebLogic)
# https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/administer-http-sessions/using-coherenceweb-weblogic-server.html#GUID-16EF76E3-D55A-4823-8035-81873199E796


```







## 3.4. Create Cache-Server Script

```sh
# (5) Create Cache-Server Script
# https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/administer-http-sessions/using-coherenceweb-weblogic-server.html#GUID-ECE861D6-450C-494C-8DD7-E9AA15AFF6E3

cat << "EOF" > ${DOMAIN_HOME}/start-CS.sh
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
COH_PID=$(${DOMAIN_HOME}/ps-${SERVER_NAME}.sh)
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

COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.management.remote=true"
COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.override=${DOMAIN_NAME}/lib/tangosol-coherence-${DOMAIN_NAME}.xml"
export COHERENCE_ARGS

CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib/coherence-web.jar"
CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib/coherence.jar"
export CLASSPATH

mv ${NOHUP_LOG}/${SERVER_NAME}.out ${NOHUP_LOG}/${SERVER_NAME}.out.${LOG_TIME}
nohup ${JAVA_HOME}/bin/java ${USER_MEM_ARGS} ${COHERENCE_ARGS} -cp ${CLASSPATH} com.tangosol.net.DefaultCacheServer > ${NOHUP_LOG}/${SERVER_NAME}.out 2>&1 &
EOF


cat << "EOF" > ${DOMAIN_HOME}/ps-CS.sh
#!/bin/sh
DOMAIN_HOME=#DOMAIN_HOME#
SERVER_NAME=#SERVER_NAME#

ps -ef | grep "java" | grep "com.tangosol.net.DefaultCacheServer" | grep "${DOMAIN_HOME}" | grep "D${SERVER_NAME}"
EOF


cat << "EOF" > ${DOMAIN_HOME}/stop-CS.sh
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
COH_PID=$(${DOMAIN_HOME}/ps-${SERVER_NAME}.sh)
if [ "$COH_PID" == "" ]; then
     echo "Server already Stopped."
     exit;
fi
###################

kill -9 $(${DOMAIN_HOME}/ps-${SERVER_NAME}.sh | awk '{print $2}')
EOF


cat << "EOF" > ${DOMAIN_HOME}/log-CS.sh
#!/bin/sh
DOMAIN_NAME=#DOMAIN_NAME#
DOMAIN_HOME=#DOMAIN_HOME#
SERVER_NAME=#SERVER_NAME#

LOG_HOME=${DOMAIN_HOME}/logs
NOHUP_LOG=${LOG_HOME}/nohup
tail -10f ${NOHUP_LOG}/${SERVER_NAME}.out
EOF


cp ${DOMAIN_HOME}/start-CS.sh ${DOMAIN_HOME}/start-CS1.sh
cp ${DOMAIN_HOME}/stop-CS.sh ${DOMAIN_HOME}/stop-CS1.sh
cp ${DOMAIN_HOME}/log-CS.sh ${DOMAIN_HOME}/log-CS1.sh
cp ${DOMAIN_HOME}/ps-CS.sh ${DOMAIN_HOME}/ps-CS1.sh

cp ${DOMAIN_HOME}/start-CS.sh ${DOMAIN_HOME}/start-CS2.sh
cp ${DOMAIN_HOME}/stop-CS.sh ${DOMAIN_HOME}/stop-CS2.sh
cp ${DOMAIN_HOME}/log-CS.sh ${DOMAIN_HOME}/log-CS2.sh
cp ${DOMAIN_HOME}/ps-CS.sh ${DOMAIN_HOME}/ps-CS2.sh

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
