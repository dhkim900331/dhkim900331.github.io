---
date: 2023-02-02 08:58:49 +0900
layout: post
title: "[Database/Oracle] Oracle 19c 설치"
tags: [Database, Oracle, 19c, Installation]
typora-root-url: ..
---

# 1. Overview

Oracle DB가 필요하게 되어, 19c 설치를 하며 작성을 한다.

정확도가 떨어지는 가이드의 문서가 될 수 있겠다.

<br>

[다음의 게시물](https://fliedcat.tistory.com/106)을 기초로 하였다.


<br><br>


# 2. 문서 작성 기준이 되는 테스트 환경

```shell
$ cat /etc/*release
Oracle Linux Server release 8.7
NAME="Oracle Linux Server"
VERSION="8.7"
ID="ol"
ID_LIKE="fedora"
VARIANT="Server"
VARIANT_ID="server"
VERSION_ID="8.7"
PLATFORM_ID="platform:el8"
PRETTY_NAME="Oracle Linux Server 8.7"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:oracle:linux:8:7:server"
HOME_URL="https://linux.oracle.com/"
BUG_REPORT_URL="https://bugzilla.oracle.com/"

ORACLE_BUGZILLA_PRODUCT="Oracle Linux 8"
ORACLE_BUGZILLA_PRODUCT_VERSION=8.7
ORACLE_SUPPORT_PRODUCT="Oracle Linux"
ORACLE_SUPPORT_PRODUCT_VERSION=8.7
Red Hat Enterprise Linux release 8.7 (Ootpa)
Oracle Linux Server release 8.7
```

<br>


# 3. 사전 준비사항

## 3.1 설치 파일

[Oracle Database 19c](https://www.oracle.com/database/technologies/oracle-database-software-downloads.html)에서 `Linux x86-64 (ZIP, 2.8GB)` 를 받았다.


<br><br>


## 3.2 Packages

[Operating System Checklist for Oracle Database Installation on Linux](https://docs.oracle.com/en/database/oracle/oracle-database/19/ladbi/operating-system-checklist-for-oracle-database-installation-on-linux.html#GUID-E5C0A90E-7750-45D9-A8BC-C7319ED934F0) 참고

> 본인은, 위 문서를 보았지만 기존 시스템에 WLS, OHS 등 다양한 설치를 진행해왔던 터라 실제 Yum 을 진행하지 않고 넘어갔다.

<br>


# 4. 소프트웨어 설치

## 4.1 기본 환경 구성

```shell
$ cat ~/.bash_profile
export ORACLE_BASE=/sw/databases/oracle-19c
export ORACLE_HOME=${ORACLE_BASE}/product/19.3/dbhome_1
export ORACLE_SID=ORCL
export PATH=$ORACLE_HOME/bin:$PATH
```


```shell
$ mkdir -p $ORACLE_HOME
$ mv LINUX.X64_193000_db_home.zip ${ORACLE_HOME}
$ cd ${ORACLE_HOME} && unzip ${ORACLE_HOME}/LINUX.X64_193000_db_home.zip
```

<br>


## 4.2 응답 파일 작성

기본적으로 `$ORACLE_HOME/inventory/response/db_install.rsp` 위치한 기본 응답파일을 사용하면 된다.

아래는 위 파일을 내 환경에 맞게 변경하였고, 주석을 제거하였다.

`oracle.install.responseFileVersion` 은 그대로 사용해야 되는것으로 보인다.

<br>

```shell
$ cat $ORACLE_HOME/install/response/db_install.rsp

UNIX_GROUP_NAME=<Group Name of OS Account that run installer>
INVENTORY_LOCATION=/sw/databases/oracle-19c/inventory
ORACLE_HOME=/sw/databases/oracle-19c/product/19.3/dbhome_1
ORACLE_BASE=/sw/databases/oracle-19c

oracle.install.responseFileVersion=/oracle/install/rspfmt_dbinstall_response_schema_v19.0.0
oracle.install.option=INSTALL_DB_SWONLY

oracle.install.db.InstallEdition=SE2
oracle.install.db.OSDBA_GROUP=<Group Name>
oracle.install.db.OSBACKUPDBA_GROUP=<Group Name>
oracle.install.db.OSDGDBA_GROUP=<Group Name>
oracle.install.db.OSKMDBA_GROUP=<Group Name>
oracle.install.db.OSRACDBA_GROUP=<Group Name>
oracle.install.db.rootconfig.executeRootScript=true
oracle.install.db.rootconfig.configMethod=SUDO
oracle.install.db.rootconfig.sudoPath=/usr/bin/sudo
oracle.install.db.rootconfig.sudoUserName=<sudo username>
oracle.install.db.config.starterdb.type=GENERAL_PURPOSE
oracle.install.db.config.starterdb.globalDBName=GLOBAL_ORCL
oracle.install.db.config.starterdb.SID=ORCL
oracle.install.db.ConfigureAsContainerDB=false
oracle.install.db.config.starterdb.characterSet=AL32UTF8
oracle.install.db.config.starterdb.password.ALL=<Password of OS Account that run installer>
oracle.install.db.config.starterdb.password.SYS=<Password of OS Account that run installer>
oracle.install.db.config.starterdb.password.SYSTEM=<Password of OS Account that run installer>
oracle.install.db.config.starterdb.password.DBSNMP=<Password of OS Account that run installer>
oracle.install.db.config.starterdb.password.PDBADMIN=<Password of OS Account that run installer>
```

<br>


## 4.3 설치 실행

```shell
$ $ORACLE_HOME/runInstaller -silent -responseFile $ORACLE_HOME/install/response/db_install.rsp
Launching Oracle Database Setup Wizard...

[WARNING] [INS-08101] Unexpected error while executing the action at state: 'supportedOSCheck'
   CAUSE: No additional information available.
   ACTION: Contact Oracle Support Services or refer to the software manual.
   SUMMARY:
       - java.lang.NullPointerException
```


내 환경과 같이 OS Pass에 실패할 경우, 다음과 같이 진행한다. [참고](https://positivemh.tistory.com/486)

```shell
$ export CV_ASSUME_DISTID=RHEL7.6
$ $ORACLE_HOME/runInstaller -silent -responseFile $ORACLE_HOME/install/response/db_install.rsp

Launching Oracle Database Setup Wizard...

[WARNING] [INS-32056] The specified Oracle Base contains the existing Central Inventory location: /sw/databases/oracle-19c/inventory.
   ACTION: Oracle recommends that the Central Inventory location is outside the Oracle Base directory. Specify a different location for the Oracle Base.

 Enter password for user <***> :
The response file for this session can be found at:
 /sw/databases/oracle-19c/product/19.3/dbhome_1/install/response/db_2022-12-29_02-58-41PM.rsp

You can find the log of this install session at:
 /sw/databases/oracle-19c/inventory/logs/InstallActions2022-12-29_02-58-41PM/installActions2022-12-29_02-58-41PM.log
Successfully Setup Software.
```

<br>


## 4.4 설치 확인

```shell
$ sqlplus / as sysdba

SQL*Plus: Release 19.0.0.0.0 - Production on Thu Dec 29 15:06:11 2022
Version 19.3.0.0.0

Copyright (c) 1982, 2019, Oracle.  All rights reserved.

Connected to an idle instance.

SQL>
```

<br>


# 5. 리스너 구성 및 확인

```shell
$ netca -silent -responseFile $ORACLE_HOME/assistants/netca/netca.rsp

Parsing command line arguments:
    Parameter "silent" = true
    Parameter "responsefile" = /sw/databases/oracle-19c/product/19.3/dbhome_1/assistants/netca/netca.rsp
Done parsing command line arguments.
Oracle Net Services Configuration:
Profile configuration complete.
Oracle Net Listener Startup:
    Running Listener Control:
      /sw/databases/oracle-19c/product/19.3/dbhome_1/bin/lsnrctl start LISTENER
    Listener Control complete.
    Listener started successfully.
Listener configuration complete.
Oracle Net Services configuration successful. The exit code is 0
```

<br>


```shell
$ lsnrctl status

LSNRCTL for Linux: Version 19.0.0.0.0 - Production on 29-DEC-2022 15:09:17

Copyright (c) 1991, 2019, Oracle.  All rights reserved.

Connecting to (DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=wls.local)(PORT=1521)))
STATUS of the LISTENER
------------------------
Alias                     LISTENER
Version                   TNSLSNR for Linux: Version 19.0.0.0.0 - Production
Start Date                29-DEC-2022 15:08:43
Uptime                    0 days 0 hr. 0 min. 33 sec
Trace Level               off
Security                  ON: Local OS Authentication
SNMP                      OFF
Listener Parameter File   /sw/databases/oracle-19c/product/19.3/dbhome_1/network/admin/listener.ora
Listener Log File         /sw/databases/oracle-19c/diag/tnslsnr/wls/listener/alert/log.xml
Listening Endpoints Summary...
  (DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST=wls.local)(PORT=1521)))
  (DESCRIPTION=(ADDRESS=(PROTOCOL=ipc)(KEY=EXTPROC1521)))
The listener supports no services
The command completed successfully
```

<br>


# 6. 데이터베이스 생성 및 확인

```shell
$ cat $ORACLE_HOME/assistants/dbca/dbca.rsp
gdbName=GLOBAL_ORCL
sid=ORCL
databaseConfigType=SI
createAsContainerDatabase=true
numberOfPDBs=1
pdbName=ORCLPDB
useLocalUndoForPDBs=true
pdbAdminPassword=wls.local1234
templateName=General_Purpose.dbc
sysPassword=wls.local1234
systemPassword= wls.local1234
storageType=FS
characterSet=AL32UTF8
nationalCharacterSet=AL16UTF16
listeners=LISTENER
databaseType=MULTIPURPOSE
totalMemory=1024
```


```shell
$ dbca -silent -createDatabase -responsefile $ORACLE_HOME/assistants/dbca/dbca.rsp

...
54% complete
Creating Pluggable Databases
58% complete
77% complete
Executing Post Configuration Actions
100% complete
Database creation complete. For details check the logfiles at:
 /sw/databases/oracle-19c/cfgtoollogs/dbca/GLOBAL_ORCL.
Database Information:
Global Database Name:GLOBAL_ORCL
System Identifier(SID):ORCL
Look at the log file "/sw/databases/oracle-19c/cfgtoollogs/dbca/GLOBAL_ORCL/GLOBAL_ORCL.log" for further details.
```


```shell
$ sqlplus / as sysdba

SQL> select NAME,CDB from v$database ;
NAME      CDB
--------- ---
GLOBAL_O  YES


SQL> show con_name;
CON_NAME
------------------------------
CDB$ROOT


SQL> alter session set container=ORCLPDB;
Session altered.


SQL> show con_name;
CON_NAME
------------------------------
ORCLPDB


! lsnrctl status

LSNRCTL for Linux: Version 19.0.0.0.0 - Production on 30-DEC-2022 10:25:00

Copyright (c) 1991, 2019, Oracle.  All rights reserved.

Connecting to (DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=wls.local)(PORT=1521)))
STATUS of the LISTENER
------------------------
Alias                     LISTENER
Version                   TNSLSNR for Linux: Version 19.0.0.0.0 - Production
Start Date                29-DEC-2022 15:08:43
Uptime                    0 days 19 hr. 16 min. 16 sec
Trace Level               off
Security                  ON: Local OS Authentication
SNMP                      OFF
Listener Parameter File   /sw/databases/oracle-19c/product/19.3/dbhome_1/network/admin/listener.ora
Listener Log File         /sw/databases/oracle-19c/diag/tnslsnr/wls/listener/alert/log.xml
Listening Endpoints Summary...
  (DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST=wls.local)(PORT=1521)))
  (DESCRIPTION=(ADDRESS=(PROTOCOL=ipc)(KEY=EXTPROC1521)))
Services Summary...
Service "GLOBAL_ORCL" has 1 instance(s).
  Instance "ORCL", status READY, has 1 handler(s) for this service...
Service "ORCLXDB" has 1 instance(s).
  Instance "ORCL", status READY, has 1 handler(s) for this service...
Service "f1023596eb1af8a5e053f522410aa522" has 1 instance(s).
  Instance "ORCL", status READY, has 1 handler(s) for this service...
Service "orclpdb" has 1 instance(s).
  Instance "ORCL", status READY, has 1 handler(s) for this service...
The command completed successfully
```


_**데이터베이스 삭제는 `dbca -silent -deleteDatabase -sourceDB ORCL`**_


<br><br>


# 7. DB & Listener Startup

```sh
$ /sw/databases/oracle-19c/product/19.3/dbhome_1/bin/lsnrctl start LISTENER
$ sqlplus / as sysdba
sqlplus> startup
ORACLE instance started.

Total System Global Area  805304088 bytes
Fixed Size                  9139992 bytes
Variable Size             218103808 bytes
Database Buffers          570425344 bytes
Redo Buffers                7634944 bytes
Database mounted.
Database opened.
```

<br>


# 8. User 관리

```sh
sqlplus> ALTER SESSION SET "_ORACLE_SCRIPT"=true;
sqlplus> CREATE USER weblogic IDENTIFIED BY weblogic1;
sqlplus> ALTER USER weblogic IDENTIFIED BY weblogic1;
sqlplus> GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW to weblogic;
sqlplus> DROP USER  weblogic CASCADE;
sqlplus> REVOKE <권한> FROM weblogic;
```

<br>


# 9. 기본 SQL Query

```sql
CREATE TABLE emp (empno NUMBER(4) NOT NULL, ename VARCHAR2(10));
```

```sql
INSERT INTO emp (empno, ename) VALUES (1, 'jane');
```

```sql
SELECT * FROM emp;
```

