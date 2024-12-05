---
date: 2024-03-13 13:41:39 +0900
layout: post
title: "[ODI] All In One Script For 12cR2"
tags: [ODI, Installation, WLST]
typora-root-url: ..
---

# 1. Overview

[How-to-install-ODI-12cR2]({{ site.url }}/odi/How-to-install-ODI-12cR2) 에서 작성한 내용을 토대로,

All In One Script를 작성한다.


<br><br>


# 2. Descriptions

## 2.1 DB Scripts

### 2.1.1 Define Envs

```sh
## OS Env ##
unset $(env | grep ORACLE | awk -F= '{print $1}')
BASEDIR=/sw/downloads
OS_USERNAME=$(id --user --name)
OS_GROUPNAME=$(id --group --name)
OS_HOSTNAME=wls.local


## DB Env ##
DB_INSTALL_PATH=/sw/odi/databases/12.1.0
DB_INVENTORY_PATH=/sw/odi/databases/inventories/12.1.0

ORACLE_BASE=${DB_INSTALL_PATH}
export ORACLE_HOME=${ORACLE_BASE}/product/12.1.0/db_home_1
export ORACLE_SID=ODI
export ORACLE_ODI_PDBNAME=${ORACLE_SID}PDB
ORACLE_DB_GROUP=weblogic
ORACLE_DB_PASSWORD=weblogic1
export PATH=${ORACLE_HOME}/bin:$PATH
```

<br>


### 2.1.2 Install DB

```sh
## Unzip db install files ##
mkdir -p ${ORACLE_HOME}
unzip ${BASEDIR}/V46095-01_1of2.zip -d ${ORACLE_HOME}
unzip ${BASEDIR}/V46095-01_2of2.zip -d ${ORACLE_HOME}
mv ${ORACLE_HOME}/database/* ${ORACLE_HOME}
rm -rf ${ORACLE_HOME}/database


## Install DB Engine ##
cp ${ORACLE_HOME}/response/db_install.rsp ${ORACLE_HOME}/response/db_install.rsp.back
cat << EOF > ${ORACLE_HOME}/response/db_install.rsp
ORACLE_HOME=${ORACLE_HOME}
ORACLE_BASE=${ORACLE_BASE}
ORACLE_HOSTNAME=${OS_HOSTNAME}

UNIX_GROUP_NAME=${OS_USERNAME}
INVENTORY_LOCATION=${DB_INVENTORY_PATH}

SELECTED_LANGUAGES=en
DECLINE_SECURITY_UPDATES=true

oracle.install.responseFileVersion=/oracle/install/rspfmt_dbinstall_response_schema_v12.1.0
oracle.install.option=INSTALL_DB_SWONLY
oracle.install.db.InstallEdition=EE
oracle.install.db.ConfigureAsContainerDB=false
oracle.install.db.DBA_GROUP=${ORACLE_DB_GROUP}
oracle.install.db.OPER_GROUP=${ORACLE_DB_GROUP}
oracle.install.db.BACKUPDBA_GROUP=${ORACLE_DB_GROUP}
oracle.install.db.DGDBA_GROUP=${ORACLE_DB_GROUP}
oracle.install.db.KMDBA_GROUP=${ORACLE_DB_GROUP}
EOF

${ORACLE_HOME}/runInstaller -silent -responseFile ${ORACLE_HOME}/response/db_install.rsp
sleep 10
tail -f ${DB_INVENTORY_PATH}/logs/installActions$(date +%Y-%m-%d)*.log
```

<br>


### 2.1.3 Setup Listener & DB

```sh
## Setup Listener ##
netca -silent -responseFile ${ORACLE_HOME}/assistants/netca/netca.rsp


## Setup DB ##
cp ${ORACLE_HOME}/assistants/dbca/dbca.rsp ${ORACLE_HOME}/assistants/dbca/dbca.rsp.back && \
cat << EOF > ${ORACLE_HOME}/assistants/dbca/dbca.rsp
[GENERAL]
RESPONSEFILE_VERSION = "12.1.0"
OPERATION_TYPE = "createDatabase"

[CREATEDATABASE]
GDBNAME = "GLOBAL_${ORACLE_SID}"
SID = "${ORACLE_SID}"
DATABASECONFTYPE = "SI"
CREATEASCONTAINERDATABASE = true
NUMBEROFPDBS = 1
PDBNAME = "${ORACLE_ODI_PDBNAME}"
PDBADMINPASSWORD = "${ORACLE_DB_PASSWORD}"
SYSPASSWORD = "${ORACLE_DB_PASSWORD}"
SYSTEMPASSWORD = "${ORACLE_DB_PASSWORD}"
STORAGETYPE = "FS"
TEMPLATENAME = "General_Purpose.dbc"
CHARACTERSET = "AL32UTF8"
TOTALMEMORY = "1536"
EMCONFIGURATION = "NONE"
DATABASETYPE = "MULTIPURPOSE"
EOF

dbca -silent -createDatabase -responsefile ${ORACLE_HOME}/assistants/dbca/dbca.rsp
```

<br>


### 2.1.4 Tune DB as ODI requests

```sh
## Tuning DB as ODI requests
sqlplus / as sysdba << EOF
ALTER SYSTEM SET shared_pool_size=150M SCOPE=SPFILE;
--ALTER SYSTEM SET sga_target 150M SCOPE=SPFILE;
ALTER SYSTEM SET session_cached_cursors=100 SCOPE=SPFILE;
ALTER SYSTEM SET processes=500 SCOPE=SPFILE;
ALTER SYSTEM SET open_cursors=800 SCOPE=SPFILE;
ALTER SYSTEM SET db_files=600 SCOPE=SPFILE;

ALTER SESSION SET CONTAINER = ${ORACLE_ODI_PDBNAME};
ALTER PLUGGABLE DATABASE SAVE STATE;

CONN / AS SYSDBA
SHUTDOWN IMMEDIATE;
STARTUP;
EXIT;
EOF
```

<br>


### 2.1.5 Start/Stop Scripts

```sh
## Startup Script
cat << EOF > ${ORACLE_HOME}/bin/startDB.sh
#!/bin/bash
export ORACLE_HOME=${ORACLE_HOME}
export ORACLE_SID=${ORACLE_SID}
export ORACLE_ODI_PDBNAME=${ORACLE_ODI_PDBNAME}

# starting listner
\${ORACLE_HOME}/bin/lsnrctl start

# starting db
\${ORACLE_HOME}/bin/sqlplus / as sysdba << _EOF
startup
_EOF
EOF

## Shutdown Script
cat << EOF > ${ORACLE_HOME}/bin/stopDB.sh
#!/bin/bash
export ORACLE_HOME=${ORACLE_HOME}
export ORACLE_SID=${ORACLE_SID}
export ORACLE_ODI_PDBNAME=${ORACLE_ODI_PDBNAME}

# starting db
\${ORACLE_HOME}/bin/sqlplus / as sysdba << _EOF
shutdown immediate
_EOF

# starting listner
\${ORACLE_HOME}/bin/lsnrctl stop
EOF


## Reset DB Script
cat << EOF > ${ORACLE_HOME}/bin/resetDB.sh
#!/bin/bash
export ORACLE_HOME=${ORACLE_HOME}
export ORACLE_SID=${ORACLE_SID}
export ORACLE_ODI_PDBNAME=${ORACLE_ODI_PDBNAME}

# starting db
\${ORACLE_HOME}/bin/sqlplus / as sysdba << _EOF
shutdown immediate
startup mount
alert system enable restricted session
drop database
_EOF

# starting listner
\${ORACLE_HOME}/bin/lsnrctl stop
EOF

# Add permission
chmod +x ${ORACLE_HOME}/bin/startDB.sh ${ORACLE_HOME}/bin/stopDB.sh ${ORACLE_HOME}/bin/resetDB.sh
```


<br><br>


## 2.2 ODI Scripts

### 2.2.1 Define Envs

```sh
## OS Env ##
unset $(env | grep ORACLE | awk -F= '{print $1}')
BASEDIR=/sw/downloads
OS_USERNAME=$(id --user --name)
OS_GROUPNAME=$(id --group --name)
OS_HOSTNAME=wls.local


## ODI Env ##
JAVA_HOME=/sw/jdk/jdk1.8.0_211
INSTALL_FILE=${BASEDIR}/fmw_12.2.1.4.0_odi.jar
INSTALL_PATH=/sw/odi/odi/12.2.1.4
INVENTORY_PATH=/sw/odi/odi/inventories/12.2.1.4
INVENTORY_GROUP=${OS_GROUPNAME}

DOMAIN_NAME=odi_domain
DOMAIN_HOME=${INSTALL_PATH}/domains/${DOMAIN_NAME}

ADM_ADDR=${OS_HOSTNAME}
ADM_NAME=AdminServer
ADM_PORT=8001
ADM_USERNAME=weblogic
ADM_PASSWORD=weblogic1

AGENT_1_NAME=M1
AGENT_1_ADDR=${OS_HOSTNAME}
AGENT_1_PORT=8002


## RCU Env ##
RCU_DB_HOSTNAME=wls.local        # is ORACLE_HOSTNAME
RCU_DB_PORT=1521                 # is DB Port
RCU_DB_NAME=ODIPDB               # is ORACLE_ODI_PDBNAME
RCU_DB_SYS_PASSWORD=weblogic1    # is ORACLE_DB_PASSWORD

RCU_SCHEMA_PREFIX=ODIDEV
RCU_SCHEMA_PASSWORD=schema1
RCU_SUPERVISOR_PASSWORD=supervisor1
RCU_PRODUCTION_MODE=D
RCU_WORK_REPOSITORY=WORKREP
RCU_ENCRYPTION=AES-128

RCU_JDBC_DRIVER=oracle.jdbc.OracleDriver
RCU_JDBC_URL=jdbc:oracle:thin:@${RCU_DB_HOSTNAME}:${RCU_DB_PORT}/${RCU_DB_NAME}
```

> SUPERVISOR account : SUPERVISOR / ${RCU_SUPERVISOR_PASSWORD}
> SCHEMA account : ${RCU_SCHEMA_PREFIX}_ODI_REPO / ${RCU_SCHEMA_PASSWORD}


<br><br>


### 2.2.2 Install ODI

```sh
## Install ODI Engine ##
cat << EOF > ${BASEDIR}/rsp
[ENGINE]
Response File Version=1.0.0.0.0

[GENERIC]
ORACLE_HOME=${INSTALL_PATH}
INSTALL_TYPE=Enterprise Installation
EOF


cat << EOF > ${BASEDIR}/loc
inventory_loc=${INVENTORY_PATH}
inst_group=${INVENTORY_GROUP}
EOF


${JAVA_HOME}/bin/java -jar ${INSTALL_FILE} -silent -responseFile ${BASEDIR}/rsp -invPtrLoc ${BASEDIR}/loc
```


<br><br>



### 2.2.3 Setup ODI Schema with RCU

```sh
## Setup ODI Schema with RCU
cat << EOF > ${BASEDIR}/odi_rcu_parameters.txt
${RCU_DB_SYS_PASSWORD}
${RCU_SCHEMA_PASSWORD}
${RCU_SUPERVISOR_PASSWORD}
${RCU_PRODUCTION_MODE}
${RCU_WORK_REPOSITORY}
${RCU_ENCRYPTION}
EOF

${INSTALL_PATH}/oracle_common/bin/rcu -silent -createRepository \
 -connectString ${RCU_DB_HOSTNAME}:${RCU_DB_PORT}/${RCU_DB_NAME} -dbUser SYS -dbRole SYSDBA \
 -useSamePasswordForAllSchemaUsers true \
 -schemaPrefix ${RCU_SCHEMA_PREFIX} \
 -component ODI -component IAU -component IAU_APPEND -component IAU_VIEWER -component OPSS \
 < ${BASEDIR}/odi_rcu_parameters.txt
```


<br><br>



### 2.2.4 Setup Domain

```sh
## Setup Domain
cat << EOF > ${BASEDIR}/dom
# Templates #  
# If you want to check useable Templates, call 'showAvailableTemplates'
# showAvailableTemplates('true', 'true', 'true')
selectTemplate('Oracle Data Integrator - Agent')
loadTemplates()

# Setup global env #
setOption('JavaHome', '${JAVA_HOME}');
setOption('ServerStartMode', 'prod')
setOption('OverwriteDomain', 'true')

# Setup default datasource #
cd('/JDBCSystemResource/LocalSvcTblDataSource/JdbcResource/LocalSvcTblDataSource/JDBCDriverParams/NO_NAME_0')
set('DriverName','${RCU_JDBC_DRIVER}')
set('URL','${RCU_JDBC_URL}')
set('PasswordEncrypted', 'schema1')
cd('Properties/NO_NAME_0/Property/user')
cmo.setValue('${RCU_SCHEMA_PREFIX}_STB')
getDatabaseDefaults()


# Setup Credential Keys #
# I don't know why this need
# https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/configuring-domain-java-ee-agent.html#GUID-AFBE99F1-1677-41DE-8AD4-3E71CF4C414B
cd('/SecurityConfiguration/base_domain')
set('UseKSSForDemo', false)
cd('/Credential/TargetStore/oracle.odi.credmap/TargetKey/SUPERVISOR')
create('c', 'Credential')
cd('Credential')
set('Username', 'SUPERVISOR') # Must be 'SUPERVISOR'
cmo.setPassword('${RCU_SUPERVISOR_PASSWORD}')

# Setup WLS account #
cd('/Security/base_domain/User/${ADM_USERNAME}')
cmo.setPassword('${ADM_PASSWORD}')

# Setup Admin&Managed(ODI) Servers #
cd('/Servers/AdminServer')
set('Name','${ADM_NAME}')
set('ListenAddress','${ADM_ADDR}')
set('ListenPort', ${ADM_PORT})

cd('/Servers/ODI_server1')
set('Name','${AGENT_1_NAME}')
set('ListenAddress','${AGENT_1_ADDR}')
set('ListenPort', ${AGENT_1_PORT})

# Create domain #
writeDomain('${DOMAIN_HOME}')
closeTemplate()
EOF

${INSTALL_PATH}/oracle_common/common/bin/wlst.sh ${BASEDIR}/dom
```


<br><br>


### 2.2.5 Create instance scripts

```sh
# Create boot.properties
cat << EOF > ${DOMAIN_HOME}/boot.properties
username=${ADM_USERNAME}
password=${ADM_PASSWORD}
EOF

# Create instance scripts
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
USER_MEM_ARGS="${USER_MEM_ARGS} -Xms1024m -Xmx1024m -XX:MetaspaceSize=512m -XX:MaxMetaspaceSize=512m"
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
sed -i "s|#SERVER_NAME#|${ADM_NAME}|g" ${DOMAIN_HOME}/*A.sh
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
USER_MEM_ARGS="${USER_MEM_ARGS} -Xms1024m -Xmx1024m -XX:MetaspaceSize=512m -XX:MaxMetaspaceSize=512m"
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


cp ${DOMAIN_HOME}/startM.sh ${DOMAIN_HOME}/start${AGENT_1_NAME}.sh
cp ${DOMAIN_HOME}/stopM.sh ${DOMAIN_HOME}/stop${AGENT_1_NAME}.sh
cp ${DOMAIN_HOME}/logM.sh ${DOMAIN_HOME}/log${AGENT_1_NAME}.sh
cp ${DOMAIN_HOME}/psM.sh ${DOMAIN_HOME}/ps${AGENT_1_NAME}.sh

sed -i "s|#OS_USERNAME#|${OS_USERNAME}|g" ${DOMAIN_HOME}/*${AGENT_1_NAME}.sh
sed -i "s|#DOMAIN_NAME#|${DOMAIN_NAME}|g" ${DOMAIN_HOME}/*${AGENT_1_NAME}.sh
sed -i "s|#DOMAIN_HOME#|${DOMAIN_HOME}|g" ${DOMAIN_HOME}/*${AGENT_1_NAME}.sh
sed -i "s|#SERVER_NAME#|${AGENT_1_NAME}|g" ${DOMAIN_HOME}/*${AGENT_1_NAME}.sh
sed -i "s|#SERVER_ADDR#|${AGENT_1_ADDR}|g" ${DOMAIN_HOME}/*${AGENT_1_NAME}.sh
sed -i "s|#SERVER_PORT#|${AGENT_1_PORT}|g" ${DOMAIN_HOME}/*${AGENT_1_NAME}.sh
sed -i "s|#ADM_ADDR#|${ADM_ADDR}|g" ${DOMAIN_HOME}/*${AGENT_1_NAME}.sh
sed -i "s|#ADM_PORT#|${ADM_PORT}|g" ${DOMAIN_HOME}/*${AGENT_1_NAME}.sh

chmod 700 ${DOMAIN_HOME}/*.sh
rm ${DOMAIN_HOME}/*M.sh
```


<br><br>



# 3. References

[How-to-install-ODI-12cR2]({{ site.url }}/odi/How-to-install-ODI-12cR2)
