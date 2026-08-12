---
date: 2024-11-21 10:08:10 +0900
layout: post
title: "[ODI/Patch] SPB(Stack Patch Bundle) to ODI"
tags: [ODI, OPatch, Patch, SPB]
typora-root-url: ../..
---

# 1. Overview
ODI 12.2.1.4 (12cR2) 에 SPB 적용 가이드


<br><br>

<br>

# 2. Descriptions
작성일 기준 다음의 Patch files을 적용한다.
 - Patch 28186730: OPATCH 13.9.4.2.17 FOR EM 13.5 AND FMW/WLS 12.2.1.4.0 AND 14.1.1.0.0
 - Patch 37157608: ODI Stack Patch Bundle 12.2.1.4.241010

<br>

OPatch version 확인
```sh
export ORACLE_HOME=/sw/odi/odi/12cR2
export JAVA_HOME=/sw/jdk/jdk1.8.0_211


${ORACLE_HOME}/OPatch/opatch version
...
OPatch Version: 13.9.4.2.1
```

<br>

SPB README 설명에 따라, OPatch version이 맞지 않으므로 OPatch를 upgrade 한다.

```sh
unzip p28186730_1394217_Generic.zip
${JAVA_HOME}/bin/java -jar 6880880/opatch_generic.jar -silent oracle_home=${ORACLE_HOME} -invPtrLoc ${ORACLE_HOME}/oraInst.loc


${ORACLE_HOME}/OPatch/opatch version
...
OPatch Version: 13.9.4.2.17
```

<br>

SPB 적용

```sh
${ORACLE_HOME}/OPatch/patches/ODI_SPB_12.2.1.4.241010/tools/spbat/generic/SPBAT/spbat.sh -phase precheck -oracle_home ${ORACLE_HOME}
...
SPBAT precheck phase has completed successfully
Time Taken to run precheck phase:  00 hours 09 min 42 secs


${ORACLE_HOME}/OPatch/patches/ODI_SPB_12.2.1.4.241010/tools/spbat/generic/SPBAT/spbat.sh -phase apply -oracle_home ${ORACLE_HOME}
...
SPBAT apply phase has completed successfully
Time Taken to run apply phase:  00 hours 36 min 23 secs
...

```

<br>

적용 여부 확인

```sh
${ORACLE_HOME}/OPatch/opatch lsinventory
...
Patch description:  "ODI Stack Patch Bundle 12.2.1.4.241010 (Patch 37157608)"
```

<br>

ODI Studio로 Repository 연결 시, 다음의 에러가 발생한다.

```
oracle.odi.core.config.MasterRepositoryVersionMismatchException: ODI-10179: Client requires a repository with version 05.02.02.11 but the repository version found is 05.02.02.09.
	at oracle.odi.core.repository.Repository.getMasterRepository(Repository.java:137)
 ...
```

<br>

Patch README의 'Section 5: Post Installation Steps' 지침을 따른다.

```sh
${ORACLE_HOME}/oracle_common/upgrade/bin/ua
# Recommend GUI
# Database Type : Oracle Database
# Database Connect String : localhost:1521/odipdb
# DBA User Name : odidev_odi_repo
# DBA Password : schema1
# Schema User Name : ODIDEV_ODI_REPO
# Schema Password : schema1
# ODI Supervisor User Name : SUPERVISOR
# ODI Supervisor Password : supervsisor1
```


<br><br>


# 3. References

Patch의 README

