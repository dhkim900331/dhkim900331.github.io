---
date: 2023-05-10 09:01:07 +0900
layout: post
title: "[WebLogic/WLST] OPatch lsinventory Printed Issue"
tags: [Middleware, WebLogic, WLST, OPatch, lsinventory]
typora-root-url: ..
---

# 1. 개요

WLS Log에 `opatch lsinventory` log가 기록되어, 기동 시점이나, WLST 실행 시 지연이 발생한다는 이슈.



# 2. 설명

WLS PSU April 2022 과 WLS PSU July 2022 적용 시에 `java weblogic.WLST` 호출이 되면 `opatch lsinventory` Log가 기록되어, 지연 발생한다는 보고가 있었다. 



WLS 기동 시점 (`<BEA-141107> <Version: WebLogic Server 14.1.1.0.0 >`) 뒤에 `opatch lsinventory` Log가 실행/기록되어 기동 지연이 발생하고,

`java weblogic.WLST` 를 이용하는 구간에서도 발생하여 위 패치가 적용된 환경에서는 불필요한 지연이 발생하는 것이 확인 되었다.



`java weblogic.WLST` 실행 시 `$ORACLE_HOME/cfgtoollogs/opatch/lsinv` 아래에 lsinventory 결과 기록이 같이 생성되므로, 재현 여부를 확인할 수 있다.



`-Dweblogic.log.DisplayPatchInfo` 기본값이 false 였으나, PSU April/July 2022 부터 기본값이 true 로 지정되어 발생하는 문제.



이러한 지연 현상을 해결하려면, 아래 중 한가지 작업을 수행하면 된다.

* WLS PSU Oct 2022 적용 (해당 PSU 부터 아래 기본값이 **다시** false 됨.)
* `-Dweblogic.log.DisplayPatchInfo=false`



# 3. 참고

How To Troubleshoot WebLogic Server Admin Console "Patch List" Showing 'No Patches Installed' (Doc ID 2777234.1)

