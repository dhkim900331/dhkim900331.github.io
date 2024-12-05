---
date: 2024-11-12 15:33:47 +0900
layout: post
title: "[WebLogic/WLST] How To Upgrade a Domain"
tags: [Middleware, WebLogic, Upgrade, WLST]
typora-root-url: ..
---

# 1. Overview
WebLogic Domain Upgrade 방법 및 사례


<br><br>


# 2. Descriptions
다음의 WLST Script를 통해 Debug log 수집과 더불어 Upgrade가 완료된다.
```sh
export ORACLE_HOME=/sw/weblogic/12cR2
export DLOG_DIR=/tmp/wlstDebug
mkdir ${DLOG_DIR}

export WLST_PROPERTIES="${WLST_PROPERTIES} -Dwlst.debug.init=true"
export WLST_PROPERTIES="${WLST_PROPERTIES} -Dwlst.offline.log.priority=debug"
export WLST_PROPERTIES="${WLST_PROPERTIES} -Dwlst.offline.log=${DLOG_DIR}/debug.log"

${ORACLE_HOME}/oracle_common/common/bin/wlst.sh << EOF
readDomainForUpgrade('<A domain path which need-to-be-upgrade>')
updateDomain()
closeDomain()
exit()
EOF
```

<br>

WLS 12cR2 기준으로, 12.2.1.1 이상에서 12.2.1.4 으로 업그레이드 하는 경우, ORACLE_HOME과 JAVA_HOME을 동일하게 구성 할 수 있다.

ORACLE_HOME과 JAVA_HOME이 변경되지 않는 경우에는 Reconfiguration Wizard 를 실행하지 않아도 된다.

즉, 별도로 상위 버전의 ORACLE_HOME을 별도 설치할 필요가 없고, 업그레이드 과정이 필요치 않다.

> [참고](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/wlupg/intro.html#GUID-CA66052C-DA8C-45B6-9A4F-D67B63B524A8)
>
>   \>\>  If you are upgrading from version 12.2.1.1.0 and later to version 12.2.1.4.0, the Reconfiguration Wizard only needs to be run when the location of the JDK or the Oracle Home is changed as part of the upgrade. If the Oracle Home and the JDK binaries are in the same location, running Reconfiguration Wizard is not required.


<br><br>

<br>

# 3. References
본문에 링크됨