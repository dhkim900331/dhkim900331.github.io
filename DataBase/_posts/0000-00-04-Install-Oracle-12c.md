---
date: 2024-02-27 13:38:15 +0900
layout: post
title: "[Database/Oracle] Oracle 12c 설치"
tags: [Database, Oracle, 12c, Installation]
typora-root-url: ..
---
{{ site.content.br_small }}
# 1. 개요

Oracle DB가 필요하게 되어, 12c 설치를 하며 작성을 한다.

정확도가 떨어지는 가이드의 문서가 될 수 있겠다.
{{ site.content.br_small }}
[Install-Oracle-19c]({{ site.url/database/Install-Oracle-19c }}) 게시물을 참고하여 작성
{{ site.content.br_big }}
# 2. 문서 작성 기준이 되는 테스트 환경

```shell
Oracle Linux Server release 8.8
NAME="Oracle Linux Server"
VERSION="8.8"
ID="ol"
ID_LIKE="fedora"
VARIANT="Server"
VARIANT_ID="server"
VERSION_ID="8.8"
PLATFORM_ID="platform:el8"
PRETTY_NAME="Oracle Linux Server 8.8"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:oracle:linux:8:8:server"
HOME_URL="https://linux.oracle.com/"
BUG_REPORT_URL="https://github.com/oracle/oracle-linux"

ORACLE_BUGZILLA_PRODUCT="Oracle Linux 8"
ORACLE_BUGZILLA_PRODUCT_VERSION=8.8
ORACLE_SUPPORT_PRODUCT="Oracle Linux"
ORACLE_SUPPORT_PRODUCT_VERSION=8.8
Red Hat Enterprise Linux release 8.8 (Ootpa)
Oracle Linux Server release 8.8
```
{{ site.content.br_big }}
# 3. 사전 준비사항

## 3.1 설치 파일

OTN 에서 Oracle 12c 를 내려 받는다.
{{ site.content.br_big }}
## 3.2 Packages

[4.7 About Operating System Requirements](https://docs.oracle.com/database/121/LADBI/pre_install.htm#LADBI7532) 참고

> 본인은, 위 문서를 보았지만 기존 시스템에 WLS, OHS 등 다양한 설치를 진행해왔던 터라 실제 Yum 을 진행하지 않고 넘어갔다.
{{ site.content.br_big }}
# 4. 소프트웨어 설치

## 4.1 기본 환경 구성

```shell
$ cat ~/.bash_profile
export ORACLE_BASE=/sw/databases/oracle-12c
export ORACLE_HOME=${ORACLE_BASE}/product/12.1.0/dbhome_1
export ORACLE_SID=ORCL
export PATH=$ORACLE_HOME/bin:$PATH
```
{{ site.content.br_small }}
```shell
$ mkdir -p ${ORACLE_HOME} && \
unzip V46095-01_1of2.zip -d ${ORACLE_HOME} && \
unzip V46095-01_2of2.zip -d ${ORACLE_HOME} && \
mv ${ORACLE_HOME}/database/* ${ORACLE_HOME} && \
rm -rf ${ORACLE_HOME}/database
```
{{ site.content.br_small }}
> OTN 에서 내려받은 Oracle 12c 는 1of.. 2of.. zip 으로 나뉘어져 있었다.
{{ site.content.br_big }}
## 4.2 응답 파일 작성

기본적으로 `$ORACLE_HOME/response/db_install.rsp` 위치한 기본 응답파일을 사용하면 된다.

아래는 위 파일을 내 환경에 맞게 변경하였고, 주석을 제거하였다.

`oracle.install.responseFileVersion` 은 그대로 사용해야 되는것으로 보인다.
{{ site.content.br_small }}
[3.1.2 What is a Response File?](https://docs.oracle.com/cd/E24628_01/em.121/e37799/ch3_response_file.htm#OUICG186) 참고
{{ site.content.br_small }}
```shell
$ cp ${ORACLE_HOME}/response/db_install.rsp ${ORACLE_HOME}/response/db_install.rsp.back
$ cat << EOF > ${ORACLE_HOME}/response/db_install.rsp
ORACLE_HOME=/sw/databases/oracle-12c/product/12.1.0/dbhome_1
ORACLE_BASE=/sw/databases/oracle-12c
ORACLE_HOSTNAME=wls.local

UNIX_GROUP_NAME=weblogic
INVENTORY_LOCATION=/sw/databases/oracle-12c/inventory

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
```
{{ site.content.br_big }}
## 4.3 설치 실행

```shell
$ ${ORACLE_HOME}/runInstaller -silent -responseFile ${ORACLE_HOME}/response/db_install.rsp
Starting Oracle Universal Installer...

Checking Temp space: must be greater than 500 MB.   Actual 5635 MB    Passed
Checking swap space: must be greater than 150 MB.   Actual 16383 MB    Passed
Preparing to launch Oracle Universal Installer from /tmp/OraInstall2024-02-22_02-46-50PM. Please wait ...[weblogic@wls response]$ [WARNING] [INS-13001] Environment does not meet minimum requirements.
   CAUSE: Minimum requirements were not met for this environment
   ACTION: Either check the logs for more information or check the supported configurations for this product.
[WARNING] [INS-32016] The selected Oracle home contains directories or files.
   ACTION: To start with an empty Oracle home, either remove its contents or choose another location.
[WARNING] [INS-32055] The Central Inventory is located in the Oracle base.
   ACTION: Oracle recommends placing this Central Inventory in a location outside the Oracle base directory.
You can find the log of this install session at:
 /sw/databases/oracle-12c/inventory/logs/installActions2024-02-22_02-46-50PM.log
```
{{ site.content.br_small }}
```shell
$ tail -f /sw/databases/oracle-12c/inventory/logs/installActions2024-02-22_02-46-50PM.log
INFO: Installation in progress
INFO: Extracting files to '/sw/databases/oracle-12c/product/12.1.0/dbhome_1'.
INFO: Extracting files to '/sw/databases/oracle-12c/product/12.1.0/dbhome_1'.
INFO: Performing fastcopy operations based on the information in the file 'oracle.server_EE_dirs.lst'.
INFO: Performing fastcopy operations based on the information in the file 'oracle.server_EE_filemap.jar'.
INFO: Performing fastcopy operations based on the information in the file 'racfiles.jar'.
INFO: Performing fastcopy operations based on the information in the file 'oracle.server_EE_exp_1.xml'.
INFO: Performing fastcopy operations based on the information in the file 'oracle.server_EE_1.xml'.
INFO: Performing fastcopy operations based on the information in the file 'setperms1.sh'.
INFO: Number of threads for fast copy :1

...

Successfully Setup Software.

...

INFO: Exit Status is 0
INFO: Shutdown Oracle Database 12c Release 1 Installer
```
{{ site.content.br_big }}
## 4.4 설치 확인

```shell
$ sqlplus / as sysdba

SQL*Plus: Release 12.1.0.2.0 Production on Thu Feb 22 14:50:11 2024

Copyright (c) 1982, 2014, Oracle.  All rights reserved.

Connected to an idle instance.

SQL>
```
{{ site.content.br_big }}
# 5. 리스너 구성 및 확인

```shell
$ netca -silent -responseFile ${ORACLE_HOME}/assistants/netca/netca.rsp

Parsing command line arguments:
    Parameter "silent" = true
    Parameter "responsefile" = /sw/databases/oracle-12c/product/12.1.0/dbhome_1/assistants/netca/netca.rsp
Done parsing command line arguments.
Oracle Net Services Configuration:
Profile configuration complete.
Oracle Net Listener Startup:
    Running Listener Control:
      /sw/databases/oracle-12c/product/12.1.0/dbhome_1/bin/lsnrctl start LISTENER
    Listener Control complete.
    Listener started successfully.
Listener configuration complete.
Oracle Net Services configuration successful. The exit code is 0
```
{{ site.content.br_small }}
```shell
$ lsnrctl status

LSNRCTL for Linux: Version 12.1.0.2.0 - Production on 22-FEB-2024 14:51:28

Copyright (c) 1991, 2014, Oracle.  All rights reserved.

Connecting to (DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=wls.local)(PORT=1521)))
STATUS of the LISTENER
------------------------
Alias                     LISTENER
Version                   TNSLSNR for Linux: Version 12.1.0.2.0 - Production
Start Date                22-FEB-2024 14:50:41
Uptime                    0 days 0 hr. 0 min. 46 sec
Trace Level               off
Security                  ON: Local OS Authentication
SNMP                      OFF
Listener Parameter File   /sw/databases/oracle-12c/product/12.1.0/dbhome_1/network/admin/listener.ora
Listener Log File         /sw/databases/oracle-12c/diag/tnslsnr/wls/listener/alert/log.xml
Listening Endpoints Summary...
  (DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST=wls.local)(PORT=1521)))
  (DESCRIPTION=(ADDRESS=(PROTOCOL=ipc)(KEY=EXTPROC1521)))
The listener supports no services
The command completed successfully
```
{{ site.content.br_big }}
# 6. 데이터베이스 생성 및 확인

기본적으로 `${ORACLE_HOME}/assistants/dbca/dbca.rsp` 위치한 기본 응답파일을 사용하면 된다.

아래는 위 파일을 내 환경에 맞게 변경하였고, 주석을 제거하였다.
{{ site.content.br_small }}
[A.5 Running Database Configuration Assistant Using a Response File](https://docs.oracle.com/database/121/LADBI/app_nonint.htm#LADBI7843) 참고
{{ site.content.br_small }}
```shell
$ cp ${ORACLE_HOME}/assistants/dbca/dbca.rsp ${ORACLE_HOME}/assistants/dbca/dbca.rsp.back
$ cat << EOF > ${ORACLE_HOME}/assistants/dbca/dbca.rsp
[GENERAL]
RESPONSEFILE_VERSION = "12.1.0"
OPERATION_TYPE = "createDatabase"

[CREATEDATABASE]
GDBNAME = "GLOBAL_ORCL"
SID = "ORCL"
DATABASECONFTYPE = "SI"
CREATEASCONTAINERDATABASE = true
NUMBEROFPDBS = 1
PDBNAME = "ORCLPDB"
PDBADMINPASSWORD = "weblogic1"
SYSPASSWORD = "weblogic1"
SYSTEMPASSWORD = "weblogic1"
STORAGETYPE = "FS"
TEMPLATENAME = "General_Purpose.dbc"
CHARACTERSET = "AL32UTF8"
TOTALMEMORY = "800"
EMCONFIGURATION = "NONE"
DATABASETYPE = "MULTIPURPOSE"
EOF
```
{{ site.content.br_small }}
```shell
$ dbca -silent -createDatabase -responsefile ${ORACLE_HOME}/assistants/dbca/dbca.rsp
Copying database files
1% complete
2% complete
27% complete
Creating and starting Oracle instance
29% complete
32% complete
33% complete
34% complete
38% complete
42% complete
43% complete
45% complete
Completing Database Creation
48% complete
51% complete
53% complete
62% complete
70% complete
72% complete
Creating Pluggable Databases
78% complete
100% complete
Look at the log file "/sw/databases/oracle-12c/cfgtoollogs/dbca/GLOBAL_ORCL/GLOBAL_O.log" for further details.
[weblogic@wls response]$

```
{{ site.content.br_big }}
```shell
$ sqlplus / as sysdba

SQL> select NAME,CDB from v$database;

NAME      CDB
--------- ---
GLOBAL_O  YES

SQL> show con_name;

CON_NAME
------------------------------
CDB$ROOT


SQL> ! lsnrctl status

LSNRCTL for Linux: Version 12.1.0.2.0 - Production on 22-FEB-2024 15:47:16

Copyright (c) 1991, 2014, Oracle.  All rights reserved.

Connecting to (DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=wls.local)(PORT=1521)))
STATUS of the LISTENER
------------------------
Alias                     LISTENER
Version                   TNSLSNR for Linux: Version 12.1.0.2.0 - Production
Start Date                22-FEB-2024 14:50:41
Uptime                    0 days 0 hr. 56 min. 34 sec
Trace Level               off
Security                  ON: Local OS Authentication
SNMP                      OFF
Listener Parameter File   /sw/databases/oracle-12c/product/12.1.0/dbhome_1/network/admin/listener.ora
Listener Log File         /sw/databases/oracle-12c/diag/tnslsnr/wls/listener/alert/log.xml
Listening Endpoints Summary...
  (DESCRIPTION=(ADDRESS=(PROTOCOL=tcp)(HOST=wls.local)(PORT=1521)))
  (DESCRIPTION=(ADDRESS=(PROTOCOL=ipc)(KEY=EXTPROC1521)))
Services Summary...
Service "GLOBAL_ORCL" has 1 instance(s).
  Instance "ORCL", status READY, has 1 handler(s) for this service...
Service "ORCLXDB" has 1 instance(s).
  Instance "ORCL", status READY, has 1 handler(s) for this service...
Service "orclpdb" has 1 instance(s).
  Instance "ORCL", status READY, has 1 handler(s) for this service...
The command completed successfully
```
{{ site.content.br_big }}
_**데이터베이스 삭제는 `dbca -silent -deleteDatabase -sourceDB ORCL`**_
{{ site.content.br_big }}
# 7. DB & Listener Startup

```sh
$ lsnrctl start LISTENER
$ sqlplus / as sysdba
SQL> startup
ORACLE instance started.

Total System Global Area 1.0066E+10 bytes
Fixed Size                  2934744 bytes
Variable Size            1677723688 bytes
Database Buffers         8355053568 bytes
Redo Buffers               30617600 bytes
Database mounted.
Database opened.
```
{{ site.content.br_big }}
# 8. User 관리

```sh
sqlplus> ALTER SESSION SET "_ORACLE_SCRIPT"=true;
sqlplus> CREATE USER weblogic IDENTIFIED BY weblogic1;
sqlplus> ALTER USER weblogic IDENTIFIED BY weblogic1;
sqlplus> GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW to weblogic;
sqlplus> DROP USER  weblogic CASCADE;
sqlplus> REVOKE <권한> FROM weblogic;
```
{{ site.content.br_big }}
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

