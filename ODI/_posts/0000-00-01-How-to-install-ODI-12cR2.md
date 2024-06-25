---
date: 2024-02-27 13:38:15 +0900
layout: post
title: "[ODI] How to install ODI 12cR2?"
tags: [ODI, Installation]
typora-root-url: ..
---

# 1. Overview

Oracle Data Integrator 12cR2 (12.2.1.4.0) 의 설치를 위해 공식 메뉴얼과 해외 블로그를 토대로 정리한다.

ODI 와 Oracle DB 를 설치하고, WLS Domain 구성하여 ODI Studio 에서 생성한 Agent와의 연결까지 진행한다.
{{ site.content.br_big }}
# 2. Descriptions

## 2.1 Roadmap for Verifying Your System Environment

설치에 앞서 Certification 확인 및 OS 에 필요한 정보들을 [Roadmap for Verifying Your System Environment](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/preparing-install-and-configure-product.html#GUID-35030871-A1A0-435C-8094-A74CCD42EAD1) 에서 전체적으로 확인한다.
{{ site.content.br_big }}
---

[About JDK Requirements for an Oracle Fusion Middleware Installation](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/preparing-install-and-configure-product.html#GUID-8AA3A3BA-27F0-43B8-8F62-1B2DC8C5DBB1) 에 따르면, 

`For 12c (12.2.1.4.0), the certified JDK is 1.8.0_211 and later.` JDK 1.8.0_211 이상을 사용하면 된다고 하는데, 현재 포스팅 기준 최신 버전은 JDK 1.8.0_391 이다.

다만, ODI Studio 를 JDK 1.8.0_261 이상 버전으로 실행하려고 하면, JDK에 MSVCR100.dll 을 찾지 못해 실행되지 않는다. 261 미만 버전을 사용해야 될 것으로 보인다.

[JDK 8u261 Release Notes 에서 **JDK/JRE Runtime Windows Visual Studio Library (DLL) Dependency Changes** 참고](https://www.oracle.com/java/technologies/javase/8u261-relnotes.html)



JDK가 이미 최신 버전일 경우, [Setting Java Home for ODI Studio](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/configuring-oracle-data-integrator-studio.html#GUID-F236D36F-05DF-4B43-AC33-0A30C5244B76) 설명에 따라 변경 가능하다고 되어 있지만, 직접 해보니 `odi.conf` 환경변수가 적용되지 않아 재설치 했다.





---

ODI는 Database에 RCU를 이용하여 Repository가 준비되어야 하므로, 반드시 Database 부분도 잘 확인해야 한다.

[About Database Requirements for an Oracle Fusion Middleware Installation](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/preparing-install-and-configure-product.html#GUID-4D3068C8-6686-490A-9C3C-E6D2A435F20A) 에서 RCU 로 생성할 Repository 용 DB의 Certification을 잘 확인해야 한다.
{{ site.content.br_small }}
또한, 관련 링크를 통해 확인 시에 [RCU Requirements for Oracle Databases](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/sysrs/system-requirements-and-specifications.html#GUID-35B584F3-6F42-4CA5-9BBB-116E447DAB83) 에서 설치해야 하는 DB Version을 알 수 있다.

여기 포스팅에서는 Oracle 12c DB로 진행한다.
{{ site.content.br_small }}
이어서, 페이지 아래에 Characterset 이나 Minimum Tuning Parameters 가 언급되어 있다.

이는 설치 스크립트 단계에서 적용 된다.
{{ site.content.br_big }}
## 2.2 Obtaining the Product Distribution

[Obtaining the Product Distribution](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/preparing-install-and-configure-product.html#GUID-BEC7EF99-83DC-4511-9F40-57FD5DA602B2) 참고

[Oracle Data Integrator Downloads](https://www.oracle.com/middleware/technologies/data-integrator-downloads.html) 에서 Oracle Data Integrator 12c (12.2.1.4.0) 를 받는다.

V983389-01.zip 을 압축 해제하여, fmw_12.2.1.4.0_odi.jar 파일을 얻는다.
{{ site.content.br_big }}
## 2.3 Installing the Oracle Data Integrator Software

[Installing the Oracle Data Integrator Software](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/installing-product-software.html#GUID-D5AFD830-8A7D-42CC-8C22-CE68C452CF4A) 참고

여기서는 [Installing Oracle Data Integrator in Silent Mode](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/installing-product-software.html#GUID-AEF5AA93-93C2-4DAF-A120-915DAF6FE8EF) 를 진행했다.
{{ site.content.br_small }}
```bash
BASEDIR=/sw/downloads
OS_USERNAME=$(id --user --name)
OS_GROUPNAME=$(id --group --name)
OS_HOSTNAME=wls.local

ODI_INSTALL_FILE=${BASEDIR}/fmw_12.2.1.4.0_odi.jar
ODI_INSTALL_PATH=/sw/odi/12cR2
INVENTORY_PATH=/sw/odi/inventories/12cR2
INVENTORY_GROUP=${OS_GROUPNAME}

JAVA_HOME=/sw/jdk/jdk1.8.0_211


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
{{ site.content.br_big }}
## 2.4 Creating the Master and Work Repository Schemas

[Creating the Master and Work Repository Schemas](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/creating-master-and-work-repository-schemas.html#GUID-25AC5AEE-D46D-4E4B-8835-4C1FE32207CC) 참고

RCU 로 Repository 를 생성하기 위해 Oracle DB 12c 를 설치하기로 한다.

[Install-Oracle-12c]({{ site.url }}/database/Install-Oracle-12c) 게시물을 참고하여 진행한다.
{{ site.content.br_small }}
DB 엔진 설치

```bash
BASEDIR=/sw/downloads
OS_USERNAME=$(id --user --name)
OS_GROUPNAME=$(id --group --name)
OS_HOSTNAME=wls.local

ORACLE_BASE=/sw/databases/oracle-12c
ORACLE_HOME=${ORACLE_BASE}/product/12.1.0/dbhome_1
ORACLE_SID=ODI
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
oracle.install.db.config.starterdb.globalDBName=GLOBAL_ODI
oracle.install.db.config.starterdb.SID=ODI
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
{{ site.content.br_small }}
이후 Listener 설치

```bash
netca -silent -responseFile ${ORACLE_HOME}/assistants/netca/netca.rsp
```
{{ site.content.br_small }}
이후 DB 를 생성한다.

```bash
cp ${ORACLE_HOME}/assistants/dbca/dbca.rsp ${ORACLE_HOME}/assistants/dbca/dbca.rsp.back && \
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
{{ site.content.br_small }}
> PDB 구성을 하지 않으면 다음과 같이 RCU 구성 단계에서 실패한다.
>
> ```
> ERROR - RCU-6002 필요 조건 검증을 실패했습니다.
> CAUSE - RCU-6002 지정된 데이터베이스에 대해 최소 메타데이터 저장소 로드 요구 사항이 충족되지 않았습니다.
> ACTION - RCU-6002 필요 조건 요구사항이 충족되도록 데이터베이스 구성을 수정하십시오.
> 
> ERROR - RCU-6080 지정된 데이터베이스에 대한 전역 필요 조건 검사를 실패했습니다.
> CAUSE - RCU-6080 전역 필요 조건 검사를 실패했습니다. 지정된 데이터베이스에 대한 요구사항을 확인하십시오.
> ACTION - RCU-6080 전역 필요 조건 요구사항이 충족되도록 데이터베이스 구성을 수정하십시오.
> 선택된 Oracle 데이터베이스는 CDB(다중 테넌트 컨테이너 데이터베이스)입니다. CDB(다중 테넌트 컨테이너 데이터베이스)에 대한 접속은 지원되지 않습니다. 대신 적합한 PDB(플러그인할 수 있는 데이터베이스)에 접속하십시오.
> ```
{{ site.content.br_small }}
[RCU Requirements for Oracle Databases](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/sysrs/system-requirements-and-specifications.html#GUID-35B584F3-6F42-4CA5-9BBB-116E447DAB83) 에서 요구하는 값에 의해 일부 Tuning 이 필요하다.

```sh
sqlplus / as sysdba << EOF
ALTER SYSTEM SET shared_pool_size=150M SCOPE=SPFILE;
--ALTER SYSTEM SET sga_target 150M SCOPE=SPFILE;
ALTER SYSTEM SET session_cached_cursors=100 SCOPE=SPFILE;
ALTER SYSTEM SET processes=500 SCOPE=SPFILE;
ALTER SYSTEM SET open_cursors=800 SCOPE=SPFILE;
ALTER SYSTEM SET db_files=600 SCOPE=SPFILE;

ALTER SESSION SET CONTAINER = ODIPDB;
ALTER PLUGGABLE DATABASE SAVE STATE;

CONN / AS SYSDBA
SHUTDOWN IMMEDIATE;
STARTUP;
EXIT;
EOF
```
{{ site.content.br_small }}
RCU Silent mode로 Repository 를 생성하기 위해, 필요한 Parameters file을 준비한다.

```sh
cat << EOF > ${BASEDIR}/odi_rcu_parameters.txt
###SYS_PASSWORD###
###ODI_SCHEMA_PASSWORDS###
###SUPERVISOR_PASSWORD###
D
###WORK_REPOSITORY###
###WORK_REPOSITORY_PASSWORD###
###ENCRYPTION###
EOF
```
{{ site.content.br_small }}
> SYS_PASSWORD : DBA Password
>
> ODI_SCHEMA_PASSWORDS : ODI Schema Password "[Specifying Schema Passwords](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/creating-master-and-work-repository-schemas.html#GUID-AB0E3E97-A6EA-43DF-9235-0A0A1CAE2F9C) 참고"
>
> 
>
> "이하 [Custom Variables for Oracle Data Integrator](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/rcuug/repository-creation-utility-screens.html#GUID-A3033F72-D0A9-498D-AC19-BCF2AC3FBBCC) 참고"
>
> SUPERVISOR_PASSWORD : ODI Supervisor Password
>
> D : (D)evelopement Or (E)xecution
>
> WORK_REPOSITORY : Work Repository Name
>
> WORK_REPOSITORY_PASSWORD : Work Repository Password
>
> ENCRYPTION : AES-128(Default) or AES-256
{{ site.content.br_small }}
RCU Silent mode 실행

```sh
${ODI_INSTALL_PATH}/oracle_common/bin/rcu -silent -createRepository \
  -connectString ${OS_HOSTNAME}:1521/ODIPDB -dbUser SYS -dbRole SYSDBA \
  -useSamePasswordForAllSchemaUsers true \
  -schemaPrefix ODIDEV \
  -component ODI -component IAU -component IAU_APPEND -component IAU_VIEWER -component OPSS \
  < ${BASEDIR}/odi_rcu_parameters.txt
```
{{ site.content.br_big }}
## 2.5 Configuring Oracle Data Integrator Studio

[Configuring Oracle Data Integrator Studio](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/configuring-oracle-data-integrator-studio.html#GUID-C273EFBE-C0A8-49A2-908B-255BCF9DA468) 참고
{{ site.content.br_small }}
앞서 ODI 를 Unix에 설치하였지만,

ODI Studio 환경은 GUI에서 대부분 사용되므로,

별도로 Windows 에 설치한 ODI Studio 로 설명.
{{ site.content.br_small }}
[Starting ODI Studio](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/configuring-oracle-data-integrator-studio.html#GUID-E56E3874-6455-4D8E-B01A-0BC585B1BBD5) 참고하여 실행.

'저장소에 접속...' 클릭

![How-to-install-ODI-12cR2_1](/../assets/posts/images/ODI/How-to-install-ODI-12cR2/How-to-install-ODI-12cR2_1.png)
{{ site.content.br_small }}
'Oracle Data Integrator 로그인' 에서 '+' 클릭하여 새로운 로그인 접속 정보 기입

기입되는 정보는 [Connecting to the Master Repository](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/configuring-oracle-data-integrator-studio.html#GUID-79B5C886-DBFC-460C-A8A0-29710A42A30A) 참고

![How-to-install-ODI-12cR2_2](/../assets/posts/images/ODI/How-to-install-ODI-12cR2/How-to-install-ODI-12cR2_2.png)
{{ site.content.br_small }}
최초 로그인 시 'ODI 초기화' 수행 된다.

![How-to-install-ODI-12cR2_3](/../assets/posts/images/ODI/How-to-install-ODI-12cR2/How-to-install-ODI-12cR2_3.png)
{{ site.content.br_big }}
## 2.6 Configuring the Domain for a Standalone Agent

[Configuring the Domain for a Standalone Agent](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/configuring-domain-standalone-agent.html#GUID-36693629-7238-44AC-9BEB-B5F9305EBB3E) 참고
{{ site.content.br_small }}
새 에이전트 생성

[Creating an Agent in the Master Repository with ODI Studio](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/configuring-domain-standalone-agent.html#GUID-6EEED355-F944-447F-A4CE-EA7BD9FE160C) 참고

![How-to-install-ODI-12cR2_4](/../assets/posts/images/ODI/How-to-install-ODI-12cR2/How-to-install-ODI-12cR2_4.png)
{{ site.content.br_small }}
![How-to-install-ODI-12cR2_5](/../assets/posts/images/ODI/How-to-install-ODI-12cR2/How-to-install-ODI-12cR2_5.png)
{{ site.content.br_small }}
모두 저장.

![How-to-install-ODI-12cR2_6](/../assets/posts/images/ODI/How-to-install-ODI-12cR2/How-to-install-ODI-12cR2_6.png)
{{ site.content.br_small }}
생성한 에이전트 접속 테스트를 수행하면, 물리적인 에이전트가 아직 없기에

`oracle.odi.runtime.agent.invocation.InvocationException: ODI-1424: http://wls.local:20910/oraclediagent을(를) 사용하여 에이전트 호스트 또는 포트에 접속할 수 없습니다.` 에러가 발생한다.
{{ site.content.br_small }}
[Configuring the Domain](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/configuring-domain-standalone-agent.html#GUID-B6B5E795-4B47-458E-B57E-616553240460) 참고

참고하여 생성된 WLST Script

```python
### Templates ###    
# If you want to check useable Templates, call 'showAvailableTemplates'
# showAvailableTemplates('true', 'true', 'true')
selectTemplate('Oracle Data Integrator - Agent')
loadTemplates()

### Setup global env ###
setOption('JavaHome', '/sw/jdk/jdk1.8.0_211');
setOption('ServerStartMode', 'prod')
setOption('OverwriteDomain', 'true')

### Setup default datasource ###
cd('/JDBCSystemResource/LocalSvcTblDataSource/JdbcResource/LocalSvcTblDataSource/JDBCDriverParams/NO_NAME_0')
set('DriverName','oracle.jdbc.OracleDriver')
set('URL','jdbc:oracle:thin:@wls.local:1521/ODIPDB')
set('PasswordEncrypted', 'schema1')
cd('Properties/NO_NAME_0/Property/user')
cmo.setValue('ODIDEV_STB')
getDatabaseDefaults()


### Setup Credential Keys
# I don't know why this need
# https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding/configuring-domain-java-ee-agent.html#GUID-AFBE99F1-1677-41DE-8AD4-3E71CF4C414B
cd('/SecurityConfiguration/base_domain')
cmo.setUseKSSForDemo(false)
cd('/Credential/TargetStore/oracle.odi.credmap/TargetKey/SUPERVISOR')
create('c','Credential')
cd('Credential')
cmo.setUsername('SUPERVISOR')
cmo.setPassword('supervisor1')


### Setup WLS account ###
cd('/Security/base_domain/User/weblogic')
cmo.setPassword('weblogic1')


### Setup Admin&Managed(ODI) Servers ###
cd('/Servers/AdminServer')
set('ListenAddress','wls.local')
set('ListenPort', 8001)

cd('/Servers/ODI_server1')
set('ListenAddress','wls.local')
set('ListenPort', 20910)

### Create domain
writeDomain('/sw/odi/12cR2/domains/base_domain')
closeTemplate()
```
{{ site.content.br_small }}
이후 인스턴스 기동 후 ODI Studio 에서 앞서 생성한 OracleDIAgent 를 체크하면 된다.

ODI Studio 에서 생성한 Agent 이름은 Master Repository 에 저장이 되는데,

ODI_server1 기동 시 바라보는 Agent 이름이 서로 맞지 않을 때 아래처럼 에러가 난다.

그러므로 아래 에러가 발생하면, 로그처럼 'OracleDIAgent' 가 ODI Studio 에서 생성한 이름과 같은지 확인한다.

그리고 ODI_server1 재기동하면 에러가 사라진다.
{{ site.content.br_small }}
```
<Mar 5, 2024 3:57:39,597 PM KST> <Error> <HTTP> <BEA-101216> <Servlet: "AgentServlet" failed to preload on startup in Web application: "oraclediagent".
ODI-1405: Agent OracleDIAgent start failure: the agent is not defined in the topology for master repository.
        at oracle.odi.runtime.agent.servlet.AgentServlet$1.doAction(AgentServlet.java:1188)
        at oracle.odi.core.persistence.dwgobject.DwgObjectTemplate.execute(DwgObjectTemplate.java:173)
        at oracle.odi.runtime.agent.servlet.AgentServlet.getSnpAgentForAgentInstance(AgentServlet.java:1178)
        at oracle.odi.runtime.agent.servlet.AgentServlet.startup(AgentServlet.java:586)
        at oracle.odi.runtime.agent.servlet.AgentServlet.init(AgentServlet.java:371)
        Truncated. see log file for complete stacktrace
>
<Mar 5, 2024 3:57:39,778 PM KST> <Error> <Deployer> <BEA-149231> <Unable to set the activation state to true for the application "oraclediagent".
weblogic.application.ModuleException: ODI-1405: Agent OracleDIAgent start failure: the agent is not defined in the topology for master repository.
        at weblogic.application.internal.ExtensibleModuleWrapper.start(ExtensibleModuleWrapper.java:140)
        at weblogic.application.internal.flow.ModuleListenerInvoker.start(ModuleListenerInvoker.java:124)
        at weblogic.application.internal.flow.ModuleStateDriver$3.next(ModuleStateDriver.java:233)
        at weblogic.application.internal.flow.ModuleStateDriver$3.next(ModuleStateDriver.java:228)
        at weblogic.application.utils.StateMachineDriver.nextState(StateMachineDriver.java:45)
        Truncated. see log file for complete stacktrace
Caused By: ODI-1405: Agent OracleDIAgent start failure: the agent is not defined in the topology for master repository.
        at oracle.odi.runtime.agent.servlet.AgentServlet$1.doAction(AgentServlet.java:1188)
        at oracle.odi.core.persistence.dwgobject.DwgObjectTemplate.execute(DwgObjectTemplate.java:173)
        at oracle.odi.runtime.agent.servlet.AgentServlet.getSnpAgentForAgentInstance(AgentServlet.java:1178)
        at oracle.odi.runtime.agent.servlet.AgentServlet.startup(AgentServlet.java:586)
        at oracle.odi.runtime.agent.servlet.AgentServlet.init(AgentServlet.java:371)
        Truncated. see log file for complete stacktrace
>
```
{{ site.content.br_big }}


# 3. References

[Installing and Configuring Oracle Data Integrator](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/oding)

https://oracle-base.com/articles/12c/odi-12c-silent-installation-on-ol7-12212
