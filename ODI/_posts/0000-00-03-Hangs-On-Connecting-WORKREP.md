---
date: 2024-03-26 13:36:02 +0900
layout: post
title: "[ODI/Studio] Hangs On Connecting WORKREP with ODI Studio"
tags: [ODI, Studio, WORKREP]
typora-root-url: ..
---

# 1. Overview

ODI  12cR2 Studio 에서 WORKREP (작업저장소 Repository) 접근 시 Hang 사례


<br><br>


# 2. Descriptions

ODI Studio 에서 WORKREP 를 접근 시, 다음 화면에서 Hang 걸린다.

![Hangs-On-Connecting-WORKREP_1](/../assets/posts/images/ODI/Hangs-On-Connecting-WORKREP/Hangs-On-Connecting-WORKREP_1.png)

<br>

Stack trace는 socketRead0 에 걸려 있다.

```
"ProgressBarThread" #133 prio=5 os_prio=0 tid=0x000000002b510800 nid=0x3677c runnable [0x0000000022c6c000]
   java.lang.Thread.State: RUNNABLE
	at sun.nio.ch.SocketDispatcher.read0(Native Method)
 ...
	at oracle.jdbc.driver.OraclePreparedStatement.executeQuery(OraclePreparedStatement.java:3766)
 ...
	at oracle.odi.adapter.GlobalObjectHelper.refreshSeededKMTemplates(GlobalObjectHelper.java:382)
	at oracle.odi.domain.mapping.generator.KMTemplateRegistry.loadKMTemplates(KMTemplateRegistry.java:309)
	at oracle.odi.domain.mapping.generator.KMTemplateRegistry.loadKMTemplates(KMTemplateRegistry.java:267)
	at oracle.odi.adapter.OdiAdapter.refreshRepositorySeededObjects(OdiAdapter.java:562)
	at oracle.odi.adapter.OdiAdapter$OdiAdapterInstanceListener.afterOpen(OdiAdapter.java:261)
	at oracle.odi.core.OdiInstance.createInstance(OdiInstance.java:742)
	at oracle.odi.ui.docking.panes.OdiCnxFactory$2.run(OdiCnxFactory.java:247)
	at oracle.ide.dialogs.ProgressBar.run(ProgressBar.java:961)
	at java.lang.Thread.run(Thread.java:748)
```


ODI 설치 위치 아래 log/studio.log 를 보면, WARNING 메시지가 있다.

```
[2024-03-20T16:27:48.216+09:00] [] [NOTIFICATION] [] [] [tid: 17] [ecid: 0000OtQkSzcB_6D_z9w0yW1_yczI000001,0] New data source: [ODIDEV_ODI_REPO/*******@jdbc:oracle:thin:@10.65.37.51:1521/ODIPDB]
[2024-03-20T16:27:49.591+09:00] [dms] [WARNING] [DMS-50763] [oracle.dms.instrument] [tid: 50] [ecid: 0000OtQk_TNB_6D_z9w0yW1_yczI000003,0] 충돌 유형 해당 사항 없음이(가) 있는 n/a 유형의 기존 명사 /DMS-Internal을(를) 생성하려고 시도합니다.
[2024-03-20T16:27:59.284+09:00] [] [NOTIFICATION] [] [] [tid: 17] [ecid: 0000OtQkSzcB_6D_z9w0yW1_yczI000001,0] New data source: [ODIDEV_ODI_REPO/*******@jdbc:oracle:thin:@(description=(address=(host=10.65.37.51)(protocol=tcp)(port=1521))(connect_data=(service_name=ODIPDB)(server=dedicated)))]
[2024-03-20T16:28:06.184+09:00] [odi] [WARNING] [] [oracle.odi.core] [tid: 17] [ecid: 0000OtQkSzcB_6D_z9w0yW1_yczI000001,0] odi.core.security.SecurityManager.loadAuthenticationMode found the authMode:mUsingLDAPAuthentication: false,mUsingIDCSAuthentication:false,indExternalAuth:null.
[2024-03-20T16:28:06.185+09:00] [odi] [NOTIFICATION] [] [oracle.odi.core] [tid: 17] [ecid: 0000OtQkSzcB_6D_z9w0yW1_yczI000001,0] Created OdiInstance instance id=1
[2024-03-20T16:28:08.395+09:00] [odi] [WARNING] [] [oracle.odi.mapping] [tid: 17] [ecid: 0000OtQkSzcB_6D_z9w0yW1_yczI000001,0] Refreshing/creating repository seeded objects.
[2024-03-20T16:28:08.400+09:00] [odi] [WARNING] [] [oracle.odi.mapping] [tid: 17] [ecid: 0000OtQkSzcB_6D_z9w0yW1_yczI000001,0] The repository seeding version is less than the client version.   Repository seeding version=1, client seeding version=3771.  The repository seeding will be refreshed.
```


이는, RCU가 생성한 Repository version과 Client Tool인 ODI Studio 의 seeding version이 맞지 않아 발생한다.

<br>

ODI Studio 에서 Master Schema 에 로그인 후 도구 > Groovy 에서 새 스크립트를 만들어, 'print OdiAdapter.getClientSeedingVersion()' 를 실행하면 아래와 같이 Client seeding version이 확인된다.

![Hangs-On-Connecting-WORKREP_2](/../assets/posts/images/ODI/Hangs-On-Connecting-WORKREP/Hangs-On-Connecting-WORKREP_2.png)

<br>

Repository DB에 연결하여 확인하면 '1' 로 확인된다, Client 와 Version이 다르다.

```sh
$ sqlplus <ODI Schema>/<schema password>@//<HOST>:<PORT>/<ODI SID>

SQL> select ID_NEXT from SNP_ID where ID_TBL = 'SEEDING_VERSION';

   ID_NEXT
----------
         1
```


권장하지 않는 방법이겠지만, 수동으로 Repository 에서 seeding version '1'을 '3771' 로 업데이트한다.

```sh
SQL> UPDATE SNP_ID SET ID_NEXT = 3771 WHERE ID_TBL = 'SEEDING_VERSION';

1 row updated.

SQL> commit;

Commit complete.

SQL> select ID_NEXT from SNP_ID where ID_TBL = 'SEEDING_VERSION';

   ID_NEXT
----------
      3771
```


**How to Clear The Cache For ODI Studio (Doc ID 1943854.1)** 문서에 따라 Cache를 지우고 ODI Studio를 실행하면 WORKREP 에 정상적으로 연결이 된다.

<br>

수동으로 seeding version을 업데이트 하지 않는 방법은 시간이 다시 허락할 때 진행해본다.

아마도, RCU와 ODI Studio tool version을 맞추는 것일 것이다.


<br><br>


# 3. References

**KM Seeding for Execution Type Repositories (Doc ID 2852999.1)**

**ODI-26209 or ODI-26210 Error Connecting to the Repository while Using Different ODI Studio Client Releases (Doc ID 2758401.1)**

**ODI Studio - WORKREP/Test Connection HANGS - "The repository seeding version is less than the client version." Error in Log (Doc ID 2567419.1)**
