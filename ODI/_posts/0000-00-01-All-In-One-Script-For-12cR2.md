---
date: 2024-02-27 13:38:15 +0900
layout: post
title: "[ODI] All In One Script For 12cR2"
tags: [ODI, Installation]
typora-root-url: ..
---

# 1. Overview

Oracle Data Integrator 12cR2 (12.2.1.4.0) 의 설치





# 2. Descriptions

## 2.1 Roadmap for Verifying Your System Environment

설치에 앞서 Certification 확인 및 OS 에 필요한 정보들을 [Roadmap for Verifying Your System Environment](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/preparing-install-and-configure-product.html#GUID-35030871-A1A0-435C-8094-A74CCD42EAD1) 에서 전체적으로 확인한다.



---

[About JDK Requirements for an Oracle Fusion Middleware Installation](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/preparing-install-and-configure-product.html#GUID-8AA3A3BA-27F0-43B8-8F62-1B2DC8C5DBB1) 에 따르면, 

`For 12c (12.2.1.4.0), the certified JDK is 1.8.0_211 and later.` JDK 1.8.0_211 이상을 사용하면 된다고 하는데, 현재 포스팅 기준 최신 버전은 JDK 1.8.0_391 이다.

다만, ODI Studio 를 JDK 1.8.0_261 이상 버전으로 실행하려고 하면, JDK에 MSVCR100.dll 을 찾지 못해 실행되지 않는다. 261 미만 버전을 사용해야 될 것으로 보인다.

[JDK 8u261 Release Notes 에서 **JDK/JRE Runtime Windows Visual Studio Library (DLL) Dependency Changes** 참고](https://www.oracle.com/java/technologies/javase/8u261-relnotes.html)



JDK가 이미 최신 버전일 경우, [Setting Java Home for ODI Studio](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/configuring-oracle-data-integrator-studio.html#GUID-F236D36F-05DF-4B43-AC33-0A30C5244B76) 설명에 따라 변경 가능하다고 되어 있지만, 직접 해보니 `odi.conf` 환경변수가 적용되지 않아 재설치 했다.



---

ODI는 Database에 RCU를 이용하여 Repository가 준비되어야 하므로, 반드시 Database 부분도 잘 확인해야 한다.

[About Database Requirements for an Oracle Fusion Middleware Installation](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/preparing-install-and-configure-product.html#GUID-4D3068C8-6686-490A-9C3C-E6D2A435F20A) 에서 RCU 로 생성할 Repository 용 DB의 Certification을 잘 확인해야 한다.



또한, 관련 링크를 통해 확인 시에 [RCU Requirements for Oracle Databases](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/sysrs/system-requirements-and-specifications.html#GUID-35B584F3-6F42-4CA5-9BBB-116E447DAB83) 에서 설치해야 하는 DB Version을 알 수 있다.

여기 포스팅에서는 Oracle 12c DB로 진행한다.



이어서, 페이지 아래에 Characterset 이나 Minimum Tuning Parameters 가 언급되어 있다.

이는 설치 스크립트 단계에서 적용 된다.





## 2.2 Obtaining the Product Distribution

[Obtaining the Product Distribution](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/preparing-install-and-configure-product.html#GUID-BEC7EF99-83DC-4511-9F40-57FD5DA602B2) 참고

[Oracle Data Integrator Downloads](https://www.oracle.com/middleware/technologies/data-integrator-downloads.html) 에서 Oracle Data Integrator 12c (12.2.1.4.0) 를 받는다.

V983389-01.zip 을 압축 해제하여, fmw_12.2.1.4.0_odi.jar 파일을 얻는다.





## 2.3 Installing the Oracle Data Integrator Software

[Installing the Oracle Data Integrator Software](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/installing-product-software.html#GUID-D5AFD830-8A7D-42CC-8C22-CE68C452CF4A) 참고

여기서는 [Installing Oracle Data Integrator in Silent Mode](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/installing-product-software.html#GUID-AEF5AA93-93C2-4DAF-A120-915DAF6FE8EF) 를 진행했다.



```bash
BASEDIR=/sw/downloads
OS_USERNAME=$(id --user --name)
OS_GROUPNAME=$(id --group --name)

ODI_INSTALL_FILE=${BASEDIR}/fmw_12.2.1.4.0_odi.jar
JAVA_HOME=/sw/jdk/jdk1.8.0_211

ODI_INSTALL_PATH=/sw/odi/12cR2
INVENTORY_PATH=/sw/odi/inventories/12cR2
INVENTORY_GROUP=${OS_GROUPNAME}


cat << EOF > ${BASEDIR}/rsp
[ENGINE]
Response File Version=1.0.0.0.0

[GENERIC]
ORACLE_HOME=${ODI_INSTALL_PATH}
INSTALL_TYPE=Enterprise Installation
EOF


cat << EOF > ${BASEDIR}/loc
inventory_loc=${INVENTORY_PATH}
inst_group=${INVENTORY_GROUP}
EOF


${JAVA_HOME}/bin/java -jar ${ODI_INSTALL_FILE} -silent -responseFile ${BASEDIR}/rsp -invPtrLoc ${BASEDIR}/loc
```





## 2.4 Creating the Master and Work Repository Schemas

[Creating the Master and Work Repository Schemas](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/creating-master-and-work-repository-schemas.html#GUID-25AC5AEE-D46D-4E4B-8835-4C1FE32207CC) 참고

RCU 로 Repository 를 생성하기 위해 Oracle DB 12c 를 설치하기로 한다.

[Install-Oracle-12c]({{ site.url/database/Install-Oracle-12c }}) 게시물을 참고하여 진행한다.



DB 엔진 설치

```bash
BASEDIR=/sw/downloads
OS_USERNAME=$(id --user --name)
OS_GROUPNAME=$(id --group --name)
OS_HOSTNAME=wls.local

ORACLE_BASE=/sw/databases/oracle-12c
ORACLE_HOME=${ORACLE_BASE}/product/12.1.0/dbhome_1
ORACLE_SID=ORCL
PATH=$ORACLE_HOME/bin:$PATH

INVENTORY_PATH=/sw/databases/inventories/12cR2

# Download 받은 Oracle DB 12c 는 2개의 ZIP으로 구성되어 있었다.
mkdir -p ${ORACLE_HOME} && \
unzip ${BASEDIR}/V46095-01_1of2.zip -d ${ORACLE_HOME} && \
unzip ${BASEDIR}/V46095-01_2of2.zip -d ${ORACLE_HOME} && \
mv ${ORACLE_HOME}/database/* ${ORACLE_HOME} && \
rm -rf ${ORACLE_HOME}/database


cp ${ORACLE_HOME}/response/db_install.rsp ${ORACLE_HOME}/response/db_install.rsp.back
cat << EOF > ${ORACLE_HOME}/response/db_install.rsp
ORACLE_HOME=${ORACLE_HOME}
ORACLE_BASE=${ORACLE_BASE}
ORACLE_HOSTNAME=${OS_HOSTNAME}

UNIX_GROUP_NAME=${OS_USERNAME}
INVENTORY_LOCATION=${INVENTORY_PATH}

SELECTED_LANGUAGES=en
DECLINE_SECURITY_UPDATES=true

oracle.install.responseFileVersion=/oracle/install/rspfmt_dbinstall_response_schema_v12.1.0
oracle.install.option=INSTALL_DB_SWONLY
oracle.install.db.InstallEdition=EE
oracle.install.db.ConfigureAsContainerDB=false
oracle.install.db.DBA_GROUP=weblogic
oracle.install.db.OPER_GROUP=weblogic
oracle.install.db.BACKUPDBA_GROUP=weblogic
oracle.install.db.DGDBA_GROUP=weblogic
oracle.install.db.KMDBA_GROUP=weblogic
oracle.install.db.config.starterdb.type=GENERAL_PURPOSE
oracle.install.db.config.starterdb.globalDBName=GLOBAL_ORCL
oracle.install.db.config.starterdb.SID=ORCL
oracle.install.db.config.starterdb.characterSet=AL32UTF8
oracle.install.db.config.starterdb.password.ALL=weblogic1
oracle.install.db.config.starterdb.password.SYS=weblogic1
oracle.install.db.config.starterdb.password.SYSTEM=weblogic1
oracle.install.db.config.starterdb.password.DBSNMP=weblogic1
oracle.install.db.config.starterdb.password.PDBADMIN=weblogic1
EOF


${ORACLE_HOME}/runInstaller -silent -responseFile ${ORACLE_HOME}/response/db_install.rsp
tail -f /sw/databases/inventories/12cR2/logs/installActions2*
```



이후 Listener 설치

```bash
netca -silent -responseFile ${ORACLE_HOME}/assistants/netca/netca.rsp
```



이후 DBCA

```bash
$ cp ${ORACLE_HOME}/assistants/dbca/dbca.rsp ${ORACLE_HOME}/assistants/dbca/dbca.rsp.back && \
cat << EOF > ${ORACLE_HOME}/assistants/dbca/dbca.rsp
[GENERAL]
RESPONSEFILE_VERSION = "12.1.0"
OPERATION_TYPE = "createDatabase"

[CREATEDATABASE]
GDBNAME = "GLOBAL_ODI"
SID = "ODI"
DATABASECONFTYPE = "SI"
CREATEASCONTAINERDATABASE = true
NUMBEROFPDBS = 1
PDBNAME = "ODIPDB"
PDBADMINPASSWORD = "weblogic1"
SYSPASSWORD = "weblogic1"
SYSTEMPASSWORD = "weblogic1"
STORAGETYPE = "FS"
TEMPLATENAME = "General_Purpose.dbc"
CHARACTERSET = "AL32UTF8"
TOTALMEMORY = "1536"
EMCONFIGURATION = "NONE"
DATABASETYPE = "MULTIPURPOSE"
EOF

dbca -silent -createDatabase -responsefile ${ORACLE_HOME}/assistants/dbca/dbca.rsp
```



DBCA 이후 진행하면서 포스팅 작성



# 3. References

[Installing and Configuring Oracle Data Integrator](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding)

