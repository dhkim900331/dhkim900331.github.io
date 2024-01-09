---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[WebLogic] 진단 기록 끄기 - WLS_DIAGNOSTICS"
tags: [Middleware, WebLogic, WLDF]
typora-root-url: ..
---

# 1. 개요

WLDF (WebLogic Diagnostics Framework) Off
{{ site.content.br_big }}
# 2. 활성화

## 2.1 기동 스크립트

* 다음의 옵션을 주석(#) 처리 합니다.

* 재기동 합니다.

  ```
  #-D_Offline_FileDataArchive=true
  #-Dweblogic.connector.ConnectionPoolProfilingEnabled=false
  #-Dcom.bea.wlw.netui.disableInstrumentation=true
  ```

  > 위 옵션은, WLDF 모듈이 생성하는 .DAT 진단 파일의 인덱싱 관리 등에 대한 옵션들입니다.
  >
  > 위 옵션들을 주석해제하게 되면, WLDF 로 생성하는 .DAT 진단 파일의 최적화(인덱싱 등) 기능을 Off 하게 됩니다.
{{ site.content.br_big }}
## 2.2 Console

* 웹로직 도메인 Console Page를 열어,
  Menu tree > 진단(Diagnostics) > 내장 진단 모듈(Built-in Diagnostics Module)을 엽니다.

[How-To-Disable-WLDF_1](/../assets_copy_1/posts/images/WebLogic/How-To-Disable-WLDF/How-To-Disable-WLDF_1.png)* 비활성화 상태의 인스턴스를 선택하고, 활성화를 누릅니다.

[How-To-Disable-WLDF_2](/../assets_copy_1/posts/images/WebLogic/How-To-Disable-WLDF/How-To-Disable-WLDF_2.png)* 상태가 활성으로 바뀌면, 진단 기능이 활성화 된 것을 의미합니다.

* ***[중요]*** 기동되어 있는 각각의 `인스턴스 > 내장 시스템 모듈 : None (없음)` 으로 되어 있으면
  "비활성화" 입니다.
  또는 Low (낮음; 기본값) 으로 되어 있으면, "활성화" 입니다.
* *이 문서에서 설명하는 `상태: 활성화/비활성화`는 재기동을 할 때마다 초기화 됩니다.*
  그러므로, `None` 또는 `Low` 으로 기능 비활성화/활성화를 할 수 있습니다.
  [Docs 참고](https://docs.oracle.com/middleware/1212/wls/WLDFC/using_builtin_diag_modules.htm#WLDF)
{{ site.content.br_big }}
# 3. 비활성화

## 3.1 기동 스크립트

* 재기동 합니다.

  ```
  -D_Offline_FileDataArchive=true
  -Dweblogic.connector.ConnectionPoolProfilingEnabled=false
  -Dcom.bea.wlw.netui.disableInstrumentation=true
  ```

  > 위 옵션은, 진단 기능에 의해 생성되는 파일의 최적화 기능을 끕니다.
  >
  > WLDF 파일의 인덱싱 관리 등에 의해 High CPU 현상이 발생하는 사례가 있기 때문입니다.
{{ site.content.br_big }}
## 3.2 Console

* "2.2 Console" 설정에서 `활성화`를 `비활성화`로 변경합니다.
