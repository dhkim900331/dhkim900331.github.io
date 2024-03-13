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
DB_INSTALL_PATH=/sw/databases/oracle-12c
DB_INVENTORY_PATH=/sw/databases/inventories/12cR2

ORACLE_BASE=${DB_INSTALL_PATH}
export ORACLE_HOME=${ORACLE_BASE}/product/12.1.0/db_home_1
export ORACLE_SID=ODI
export ORACLE_ODI_PDBNAME=${ORACLE_SID}PDB
ORACLE_DB_GROUP=weblogic
ORACLE_DB_PASSWORD=weblogic1
export PATH=${ORACLE_HOME}/bin:$PATH
```





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
tail ${DB_INVENTORY_PATH}/logs/installActions$(date +%Y-%m-%d)*.log
```





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
ODI_INSTALL_FILE=${BASEDIR}/fmw_12.2.1.4.0_odi.jar
ODI_INSTALL_PATH=/sw/odi/12cR2
ODI_INVENTORY_PATH=/sw/odi/inventories/12cR2
ODI_INVENTORY_GROUP=${OS_GROUPNAME}

ODI_DOMAIN_NAME=odi_domain
ODI_DOMAIN_HOME=${ODI_INSTALL_PATH}/domains/${ODI_DOMAIN_NAME}
ODI_DOMAIN_PASSWORD=weblogic1

ODI_ADM_ADDR=${OS_HOSTNAME}
ODI_ADM_NAME=odiAdm
ODI_ADM_PORT=8001

ODI_AGENT_1_NAME=odiAgent1
ODI_AGENT_1_ADDR=${OS_HOSTNAME}
ODI_AGENT_1_PORT=8002


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





### 2.2.2 Install ODI

```sh
## Install ODI Engine ##
cat << EOF > ${BASEDIR}/rsp
[ENGINE]
Response File Version=1.0.0.0.0

[GENERIC]
ORACLE_HOME=${ODI_INSTALL_PATH}
INSTALL_TYPE=Enterprise Installation
EOF


cat << EOF > ${BASEDIR}/loc
inventory_loc=${ODI_INVENTORY_PATH}
inst_group=${ODI_INVENTORY_GROUP}
EOF

${JAVA_HOME}/bin/java -jar ${ODI_INSTALL_FILE} -silent -responseFile ${BASEDIR}/rsp -invPtrLoc ${BASEDIR}/loc
```





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

${ODI_INSTALL_PATH}/oracle_common/bin/rcu -silent -createRepository \
 -connectString ${RCU_DB_HOSTNAME}:${RCU_DB_PORT}/${RCU_DB_NAME} -dbUser SYS -dbRole SYSDBA \
 -useSamePasswordForAllSchemaUsers true \
 -schemaPrefix ${RCU_SCHEMA_PREFIX} \
 -component ODI -component IAU -component IAU_APPEND -component IAU_VIEWER -component OPSS \
 < ${BASEDIR}/odi_rcu_parameters.txt
```





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
cd('/Security/base_domain/User/weblogic')
cmo.setPassword('${ODI_DOMAIN_PASSWORD}')

# Setup Admin&Managed(ODI) Servers #
cd('/Servers/AdminServer')
set('Name','${ODI_ADM_NAME}')
set('ListenAddress','${ODI_ADM_ADDR}')
set('ListenPort', ${ODI_ADM_PORT})

cd('/Servers/ODI_server1')
set('Name','${ODI_AGENT_1_NAME}')
set('ListenAddress','${ODI_AGENT_1_ADDR}')
set('ListenPort', ${ODI_AGENT_1_PORT})

# Create domain #
writeDomain('${ODI_DOMAIN_HOME}')
closeTemplate()
EOF

${ODI_INSTALL_PATH}/oracle_common/common/bin/wlst.sh ${BASEDIR}/dom
```





# 3. References

[How-to-install-ODI-12cR2]({{ site.url }}/odi/How-to-install-ODI-12cR2)
