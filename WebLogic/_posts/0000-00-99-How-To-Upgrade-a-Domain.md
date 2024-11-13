---
date: 2024-11-12 15:33:47 +0900
layout: post
title: "[WebLogic/WLST] How To Upgrade a Domain"
tags: [Middleware, WebLogic, Upgrade, WLST]
typora-root-url: ..
---

# 1. Overview
WebLogic Domain Upgrade 방법 및 사례

<br>

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

Upgrade 하려는 Domain의 ORACLE_HOME과
상위 버전의 ORACLE_HOME이 동일하면 Upgrade를 수행하는 WLST에서 다음과 유사한 Exception이 발생한다.
```
SEVERE [20] com.oracle.cie.domain.progress.AbstractProgressGenerator - 20850: The domain is already at the current version.
20850: Domain Location:
        /sw/weblogic/12213/domains/one_domain
   Admin Server URL:
        http://wls.local:8001 
Click cancel to exit the wizard.
20850: Click cancel to exit the wizard.
 Error occurred in phase {Selecting Reconfig Templates} execution.
com.oracle.cie.wizard.ext.progress.ProgressOperationException
    at com.oracle.cie.domain.progress.domain.reconfig.wlscore.SelectReconfigTemplatePhase.execute(SelectReconfigTemplatePhase.java:71)
    at com.oracle.cie.domain.progress.AbstractProgressGenerator.run(AbstractProgressGenerator.java:94)
    at java.lang.Thread.run(Thread.java:750)
```

실제 위 사례는,
`/sw/weblogic/12213`은 WLS 12.2.1.4 버전이며 (경로만 같을 뿐, 상위 버전),
사용하던 이전 버전의 `one_domain`만 새로 설치한 WLS 12.2.1.4 아래에 옮겨 경로를 유지하려고 했다.
업그레이드 과정 중(domain version이 변경된 이후로 보임), 기 경로가 동일하여 실패한다.

다르게 설명하면,
업그레이드를 위해 `one_domain`의 구성 요소를 Parsing 하는 과정 중에,
이미 `${DOMAIN_HOME}` 값이 변경될 필요 없이 동일하다는 것이 문제다.


# 3. References
동일 사례 없음
문서 작성하여 번호 부여 필요