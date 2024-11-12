---
layout: post
title: "[WebLogic] How To Pack or Unpack"
tags: [Middleware, WebLogic, Pack, Unpack]
typora-root-url: ..
---

# 1. Overview
Pack을 이용하여 Domain을 Template 화 할 수 있으며,
Unpack으로 손쉽게 Template 을 Remote machin에 설치할 수 있다.


# 2. Descriptions
다음을 실행하여, Domain에 대한 Template을 생성한다.
```sh
${ORACLE_HOME}/oracle_common/common/bin/pack.sh \
 -domain=${DOMAIN_HOME} \
 -template=/tmp/template.jar \
 -template_name="My Template" \
 -managed=true
```

다음을 실행하여, Template을 원하는 경로에 재구성 할 수 있다.
이때, domain 경로를 변경이 가능하며 영향 받는 모든 파일이 수정된다.
```sh
${ORACLE_HOME}/oracle_common/common/bin/unpack.sh \
 -domain=${NEW_DOMAIN_HOME} \
 -template=/tmp/template.jar \
 -user_name=weblogic \
 -password=weblogic1
```

그러나, References 에서 설명하듯 다음과 같은 파일들은 포함되지 않기 때문에
Template에 의하여 생성된 Domain을 즉시 사용 가능하지 않다.
```
2.1.3 Files and Directories Included in Managed Server Templates
...
```

# 3. References
https://docs.oracle.com/middleware/1221/wls/WLDPU/commands.htm