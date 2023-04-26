---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] BSU, OPatch, Tool Upgrade 정리"
tags: [Middleware, WebLogic, OPatch, BSU]
typora-root-url: ..
---


# 1. 개요

BSU, OPatch, Tool Upgrade 정리



# 2. Patch 전에는 백업이 필수다.

오라클 공식문서에서는 ORACLE_HOME 백업을 권고한다.

아래에서 설명할 예시 환경은 다음과 같이 지정하자.



WLS11gR1 :

 \- 오라클 제품 홈 (ORACLE_HOME) : /sw/weblogic/11gR1

 \- 웹로직 엔진 홈 (WL_HOME) : /sw/weblogic/11gR1/wlserver_10.3



WLS12cR1 :

 \- 오라클 제품 홈 (ORACLE_HOME) : /sw/weblogic/12cR1

 \- 웹로직 엔진 홈 (WL_HOME) : /sw/weblogic/12cR1/wlserver



위에서 말한 ORACLE_HOME 백업 하려고 하면,

대게 DOMAIN_HOME (웹로직 도메인) 이 아래에 같이 위치한 경우가 있으므로,

다음의 명령어로 백업을 하자.



예) 12cR1 의 DOMAIN_HOME을 제외한, ORACLE_HOME 백업

```sh
mkdir /backupdir
cp -pR `ls /sw/weblogic/12cR1 | grep -v "domains"` /backupdir
```



# 3. BSU

* bsu.sh 의 최대 Heap Memory는 2GB 이상 늘려주어야 OOME 를 피한다.
* HP 장비에서는 `MEM_ARGS="-d64"`옵션을 추가한다.



## 3.1 command

* 패치 설치/삭제/확인 명령어는 다음의 각 줄에 대응한다.

  ```sh
  ./bsu.sh -install -verbose -patch_download_dir=./cache_dir -patchlist=RVBS -prod_dir=../../wlserver_10.3 -log=../install_DEM4.log
  
  ./bsu.sh -remove -verbose -patchlist=RVBS -prod_dir=../../wlserver_10.3 -log=../remove_RVBS.log
  
  ./bsu.sh -status=applied -view -verbose -prod_dir=../../wlserver_10.3
  ```

  

> BSU 패치는 일반적으로 1시간 잡고 진행할 정도로, 느리며 아래에서 BSU 툴을 Patch 하면 빨라진다.



## 3.2 BSU Tool Patch

* WebLogic 10.3.6 이하의 버전들은 BSU 를 3.3으로 업그레이를 사전에 진행해야 한다.

* 아래 패치를 적용하면, 충돌 검사가 빨라진다.

* Enhancement for WLS BSU (Smart Update): Resolves Very Long Time to Apply Patches - Especially When Checking for Patch Conflicts (문서 ID 2271366.1)

  * 패치파일: 패치 27238412: SMART UPDATE TOOL ENHANCEMENT V3

    > 위 문서에서, 3.3 Bsu 업데이트 방법도 제공한다.
    >
    > 3.3 BSU(11g는 기본적으로 3.3 BSU) 패치 이후에는,
    >
    > bsu_update 패치를 받아 bsu 디렉토리에 넣고 ./bsu_update.sh 을 실행하면 끝난다.
    >
    > ( 위 쉘스크립트는, 엔진에 jar를 복사하는 작업만 진행하므로 1초이내 끝. )

  

# 4. OPatch

### 4.1 Recovery oraInventory

* OPatch 진행을 하는 경우, oraInventory(패치 정보를 담고 있는 디렉토리) 손상 또는 삭제된 경우가 있어 복구하는 방법도 필요하다.

  ```oraInst.loc
  # oraInst.loc 파일의 내용
  inventory_loc=/sw/weblogic/oraInventory_12cR1
  # group name of os account
  group=app
  ```

  ```sh
  ./attachHome.sh -invPtrLoc oraInst.loc
  ```

  > 거의 1분 이내에 저 경로 인벤토리를 생성해준다.



### 4.2 command

* 패치 설치/삭제/확인 명령어는 다음의 각 줄에 대응한다.

  ```sh
  ./opatch apply 27419391 -jdk /opt/java7 -invPtrLoc $ORACLE_HOME/oraInst.loc -oh $ORACLE_HOME
  
  ./opatch rollback 27419391 -jdk /opt/java7 -invPtrLoc $ORACLE_HOME/oraInst.loc -oh $ORACLE_HOME
  
  ./opatch lsinventory -jdk /opt/java7 -invPtrLoc $ORACLE_HOME/oraInst.loc
  ```

  

  위에 -jdk, invPtrLoc, -oh 옵션을 쓰는 이유는 OPatch 툴이 알고 있는 정보와 다른 경우 다른 패치 경로를 바라보기 때문에 직접 고정해주는데 사용된다.

  보통 jdk는 그렇지 않지만, invPtrLoc나 oh 의 경우는 다른 오라클 제품이 웹로직 이후에 설치되면 바뀔 수 있다.

  왜냐? 공식문서를 보니,

  Unix 기준으로 /var/lib/oraInst.loc 를 웹로직의 OPatch 툴이 실행되면 가장 먼저 읽어보는 파일이라고 한다.

  근데, 실제로 다른 오라클 제품이 이후에 설치되면서 위 파일이 다른 경로로 바꾸어 버렸다.

  이런 사소하지만 발생하면 절대 찾을 수 없을것 같은 이슈를 위해 위 옵션 사용을 습관화 해야 한다.



### 4.2 OPatch Tool Patch

* 12cR2 psu 17년 중순?? 부터 OPatch 13.9.2.0.0 을 13.9.4.0.0 으로 업그레이드 해야 한다.

* 패치파일 : Using OUI NextGen OPatch 13 for Oracle Fusion Middleware 12c (문서 ID 1587524.1)

  > 위 문서 도입 부분에 [Patch 28186730](https://support.oracle.com/epmos/faces/ui/patch/PatchDetail.jspx?parent=DOCUMENT&sourceId=1587524.1&patchId=28186730) 을 안내하고 있음



# 5. Trouble Shooting

* 아래 트러블 슈팅은, 실제 고객사 OPatch 에러를 정리하였다.



## 5.1 기존 패치 롤백 시

```
---------------------------
# 기존 패치 롤백 시, 아래 에러 발생 및
# 패치 파일 not found class(file) 또는 not readable 등의 에러
--------------------------

Recommended actions: OPatch won't be able to roll back the given patch. A common reason is there are other patches that depend on this patch. You need to roll back those dependent patches before you can roll back this patch.

OPatch failed with error code 43
```

위 문맥상, 종속적인 다른 패치가 있으니 그것부터 지우라는 거지만.. 대게 아래 문서와 같은 듯하다.

Error "Prerequisite check CheckRollbackable on auto-rollback patches failed" When Applying Patch (문서 ID 1582100.1) 문서를 확인한다.

ORACLE_HOME/.patch_storage 아래에는 웹로직에 걸려 있는 패치 디렉토리가 있으며, 일부 파일이 누락되어 있어 발생한 문제다. /etc , /files 를 통째로 넣어준다.

> patch_storage 폴더 복구 방법은 없음



## 5.2 신규 패치 적용 시

```
[ Error during Update inventory for apply Phase]. Detail: OPatch failed: ApplySession failed in system modification phase... 'ApplySession::apply failed: Check if library regeneration is needed with error message: com.oracle.cie.gdr.libraries.LibraryException: com.oracle.cie.gdr.utils.GdrException: Failed to apply xml diff to component definition /weblogic/wlserver/inventory/Components/oracle.wls.libraries/12.1.3.0.0/compDef.xml'

OPatch will attempt to restore the system...

Restoring the Oracle Home...

Checking if OPatch needs to invoke 'make' to restore some binaries...

OPatch was able to restore your system. Look at log file and timestamp of each file to make sure your system is in the state prior to applying the patch.

Log file location: /weblogic/wlserver/cfgtoollogs/opatch/27419391_Jul_10_2018_12_16_42/apply2018-07-10_12-16-34PM_1.log
```

opatch 가 compDef.xml 로 현재 웹로직과 패치 파일 비교를 수행해야 하나, xml 파일이 없어 발생하는 문제.

다른 버그 등으로 발생할 수 있으나 대게는, 파일이 없는 경우이며

문서를 확인한다. (XX저축은 solution 2번에 해당되었음)



OPatch apply or rollback fails with com.oracle.cie.gdr.libraries.LibraryException: com.oracle.cie.gdr.utils.GdrException: Failed to apply xml diff to component definition error in WebLogic PSU (문서 ID 2088228.1)
