---
date: 2024-05-29 14:53:50 +0900
layout: post
title: "[ODI] All In One Script For 11gR1"
tags: [ODI, Installation, WLST]
typora-root-url: ..
---

# 1. Overview

[How-to-install-ODI-12cR2]({{ site.url }}/odi/How-to-install-ODI-12cR2) 에서 작성한 내용을 토대로,

All In One Script를 작성한다.


<br><br>


# 2. Descriptions

## 2.1 Downloads

[Oracle Software Delivery Cloud](https://edelivery.oracle.com) 에서 Download 할 List

- Oracle Database Standard Edition 2 12.1.0.2.0 (2.5 GB)
- Oracle WebLogic Server 10.3.6.0.0 (1018.5 MB)
- Oracle Data Integrator 11.1.1.9.0 (4.1 GB)
- Oracle Fusion Middleware Repository Creation Utility 11.1.1.9.0 (561.4 MB)


<br><br>


## 2.2 DB

### 2.2.1 Define Envs

```sh
## OS Env ##
unset $(env | grep ORACLE | awk -F= '{print $1}')
BASEDIR=/sw/downloads
OS_USERNAME=$(id --user --name)
OS_GROUPNAME=$(id --group --name)
OS_HOSTNAME=wls.local


## Setup OS Kernel Parameters
# ref. https://velog.io/@w10sim/오라클-데이터베이스-설치하기싱글-노드x8664
sudo cat << EOF > /etc/sysctl.conf
kernel.shmmax = 2147483648
kernel.shmall = 943719
kernel.shmmni = 4096
kernel.sem = 250 32000 100 128
kernel.panic_on_oops = 1
fs.file-max = 6815744
fs.aio-max-nr = 1048576
net.core.rmem_default = 262144
net.core.rmem_max = 4194304
net.core.wmem_default = 262144
net.core.wmem_max = 1048576
net.ipv4.ip_local_port_range = 9000 65500
EOF
sudo sysctl -p

sudo cat << EOF > /etc/security/limits.conf
${OS_USERNAME} soft nofile 1024
${OS_USERNAME} hard nofile 65536
${OS_USERNAME} soft nproc 2047
${OS_USERNAME} hard nproc 16384
${OS_USERNAME} soft stack 10240
${OS_USERNAME} hard stack 32768
${OS_USERNAME} soft memlock 3774874
${OS_USERNAME} hard memlock 3774874
EOF


## DB Env ##
DB_INSTALL_PATH=/sw/databases/oracle-12c
DB_INVENTORY_PATH=/sw/databases/inventories/12cR1

export ORACLE_BASE=${DB_INSTALL_PATH}
export ORACLE_HOME=${ORACLE_BASE}/product/12.1.0/db_home_1
export ORACLE_SID=ODI
export ORACLE_ODI_PDBNAME=${ORACLE_SID}PDB
export ORACLE_DB_GROUP=weblogic
export ORACLE_DB_PASSWORD=weblogic1
export PATH=${ORACLE_HOME}/bin:$PATH
```

<br>


### 2.2.2 Install DB

```sh
## Move unziped file to ORACLE_HOME ##
mkdir -p ${ORACLE_HOME}
mv ${BASEDIR}/database/* ${ORACLE_HOME}


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
oracle.install.db.InstallEdition=SE
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


### 2.2.3 Setup Listener & DB

```sh
## Setup Listener ##
netca -silent -responseFile ${ORACLE_HOME}/response/netca.rsp


## Setup DB ##
cp ${ORACLE_HOME}/assistants/dbca/dbca.rsp ${ORACLE_HOME}/assistants/dbca/dbca.rsp.back
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


### 2.2.4 Tune DB as ODI requests

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

CONN / AS SYSDBA;
SHUTDOWN IMMEDIATE;
STARTUP;
EXIT;
EOF
```

<br>


## 2.3 RCU

### 2.3.1 Define Envs

```sh
## OS Env ##
BASEDIR=/sw/downloads


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
RCU_MASTER_REPOSITORY_ID=001
RCU_WORK_REPOSITORY_ID=001

RCU_JDBC_DRIVER=oracle.jdbc.OracleDriver
RCU_JDBC_URL=jdbc:oracle:thin:@${RCU_DB_HOSTNAME}:${RCU_DB_PORT}/${RCU_DB_NAME}
```


<br><br>


### 2.3.2 Setup ODI Schema with RCU

```sh
## Setup ODI Schema with RCU
cat << EOF > ${BASEDIR}/odi_rcu_parameters.txt
${RCU_DB_SYS_PASSWORD}
${RCU_SCHEMA_PASSWORD}
${RCU_MASTER_REPOSITORY_ID}
${RCU_SUPERVISOR_PASSWORD}
${RCU_PRODUCTION_MODE}
${RCU_WORK_REPOSITORY_ID}
${RCU_WORK_REPOSITORY}
${RCU_SCHEMA_PASSWORD}
EOF
	
${BASEDIR}/rcuHome/bin/rcu -silent -createRepository \
  -connectString ${RCU_DB_HOSTNAME}:${RCU_DB_PORT}/${RCU_DB_NAME} -dbUser SYS -dbRole SYSDBA \
  -useSamePasswordForAllSchemaUsers true \
  -schemaPrefix ${RCU_SCHEMA_PREFIX} \
  -component ODI -component IAU \
  -component OPSS < ${BASEDIR}/odi_rcu_parameters.txt
```


<br><br>


## 2.4 WLS

### 2.4.1 Install WLS

```sh
## OS Env ##
BASEDIR=/sw/downloads
OS_USERNAME=$(id --user --name)
OS_GROUPNAME=$(id --group --name)
OS_HOSTNAME=wls.local

WLS_INSTALL_FILE=${BASEDIR}/wls1036_generic.jar
JAVA_HOME=/sw/jdk/jdk1.7.0_201

WLS_INSTALL_PATH=/sw/weblogic/11gR1
INVENTORY_PATH=/sw/weblogic/inventories/11gR1
INVENTORY_GROUP=${OS_GROUPNAME}


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


<br><br>


## 2.5 ODI

### 2.5.1 Define Envs

```sh
## OS Env ##
BASEDIR=/sw/downloads
OS_USERNAME=$(id --user --name)
OS_GROUPNAME=$(id --group --name)
OS_HOSTNAME=wls.local


## WLS Env ##
# https://docs.oracle.com/middleware/11119/core/ODING/ODING.pdf#page=62&zoom=100,124,846
MIDDLEWARE_HOME=${WLS_INSTALL_PATH}


## ODI Env ##
JAVA_HOME=/sw/jdk/jdk1.7.0_201
ODI_INSTALL_FILE=${BASEDIR}/Disk1/runInstaller
ODI_INSTALL_PATH=/sw/odi/11gR1
ODI_INVENTORY_PATH=/sw/odi/inventories/11gR1
ODI_INVENTORY_GROUP=${OS_GROUPNAME}
```

<br>


### 2.5.2 Install ODI

```sh
## Install ODI Engine ##
cat << EOF > ${BASEDIR}/rsp
[ENGINE]
Response File Version=1.0.0.0.0

[GENERIC]
ORACLE_HOME=${ODI_INSTALL_PATH}
MIDDLEWARE_HOME=${MIDDLEWARE_HOME}
APPSERVER_TYPE=WLS
SKIP_SOFTWARE_UPDATES=true
SPECIFY_DOWNLOAD_LOCATION=false
USE EXISTING REPOSITORY=false
SKIP REPOSITORY CREATION=true

[APPLICATIONS]
ODI_STUDIO=true
ODI_SDK=true
STANDALONE_AGENT=false
ORACLE_DATA_INTEGRATOR_J2EE_AGENT=true
ORACLE_DATA_INTEGRATOR_CONSOLE=true
ORACLE_DATA_INTEGRATOR_PUBLIC_WEB_SERVICE=true
EOF


cat << EOF > ${BASEDIR}/loc
inventory_loc=${ODI_INVENTORY_PATH}
inst_group=${ODI_INVENTORY_GROUP}
EOF

${ODI_INSTALL_FILE} -silent -responseFile ${BASEDIR}/rsp -invPtrLoc ${BASEDIR}/loc -jreLoc ${JAVA_HOME}
```

<br>


### 2.5.3 ODI Studio

ODI 11gR1 의 ODI Studio 가 Windows 10/11 에서 정상적으로 설치가 되지 않아, Windows에는 별도로 설치를 하지 않았다.

TigerVNC 를 구축 및 활용하여, `${ODI_INSTALL_PATH}/oracledi/client/odi.sh` 실행하였다.

<br>

Studio 에서 Login을 위한 정보는 아래와 같다.

```sh
Oracle Data Integrator Connection
Login Name : Any string that you want
User : SUPERVISOR
Password : ${RCU_SUPERVISOR_PASSWORD}

Database Connection (Master Repository)
User : ${RCU_SCHEMA_PREFIX}_ODI_REPO
Password : ${RCU_SCHEMA_PASSWORD}
Driver List : Oracle JDBC Driver
Driver Name : oracle.jdbc.OracleDriver
Url : jdbc:oracle:thin:@${RCU_DB_HOSTNAME}:${RCU_DB_PORT}/${RCU_DB_NAME}
```

<br>


# 3. References

[How-to-install-ODI-12cR2]({{ site.url }}/odi/How-to-install-ODI-12cR2)

https://oracle-base.com/articles/11g/odi-11g-silent-installation-on-ol7
