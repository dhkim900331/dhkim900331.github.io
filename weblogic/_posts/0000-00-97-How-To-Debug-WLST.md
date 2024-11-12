---
date: 2024-11-12 15:33:47 +0900
layout: post
title: "[WebLogic/WLST] How To Debug WLST"
tags: [Middleware, WebLogic, WLST, Debug]
typora-root-url: ..
---

# 1. Overview
WLST 명령문의 Debugging 방법


# 2. Descriptions
스크립트 예시는, Domain upgrade 시 WLST debugging.
`WLST_PROPERTIES`에는 Debugging 뿐만 아니라, 다양한 옵션을 구성할 수 있다.
```sh
ORACLE_HOME=/sw/weblogic/12cR2
DLOG_DIR=/tmp/wlstDebug
mkdir ${DLOG_DIR}

export WLST_PROPERTIES="${WLST_PROPERTIES} -Dwlst.debug.init=true"
export WLST_PROPERTIES="${WLST_PROPERTIES} -Dwlst.offline.log.priority=debug"
export WLST_PROPERTIES="${WLST_PROPERTIES} -Dwlst.offline.log=${DLOG_DIR}/debug.log"

${ORACLE_HOME}/oracle_common/common/bin/wlst.sh << EOF
readDomainForUpgrade('/sw/weblogic/12cR2/domains/one_domain')
updateDomain()
closeDomain()
exit()
EOF
```


# 3. References
How To Debug WLST Jython Scripts (Doc ID 1360744.1)
Unable To Upgrade 12.1.3 To 12.2.1.4 with Error "com.oracle.cie.domain.script.jython.WLSTException: 64254: Error occurred in "Backup & Initialization" phase execution" (Doc ID 2778711.1)