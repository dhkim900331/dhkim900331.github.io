---
date: 2024-05-02 14:41:32 +0900
layout: post
title: "[WebTier/OHS] Removed wlst key files under user home"
tags: [WebTier, OHS, nmConnect, NodeManager]
typora-root-url: ..
---

# 1. Overview
OHS Component가 생성하고 사용하는 `/home/<USER>/.wlst` key files 들이 제거되어 발생하는 문제와 원인에 대해 설명한다.


<br><br>

<br>

# 2. Descriptions
OHS Component는 user home directory 하위의 .wlst (`/home/<USER>/.wlst`) key files 들을,

NodeManager에 connect 시에 인증 수단으로 사용한다.

<br>

Component가 `storeUserConfig` flag를 사용하면서, NodeManager에 connect 할 때 내부적으로 nmConnect 라는 function을 사용하는데,

이 때, NodeManager에 연결에 실패하면 .wlst key files들이 제거된다.

이는 bug가 아니라, 의도적으로 design 된 것이다.

<br>

그러므로, Component를 storeUserConfig flag를 사용하여 시작 시에,

NodeManager가 중지되어 있거나, 중지되어 있지 않더라도 기타 문제가 발생하여 nmConnect 가 failed 되면

.wlst key files 들은 제거 된다.

<br>

NodeManager가 항시 기동되어 있는지, process check 하고 Component 기동을 하거나,

다음과 같이 WLST script 를 사용하여 .wlst key files 제공 없이 access 할 수 있다.

```sh
$ cat start-worker1.sh
#!/usr/bin/bash
BASEDIR=$(realpath $(dirname $0))
DOMAIN_HOME=${BASEDIR}
DOMAIN_NAME=$(basename ${DOMAIN_HOME})
WORKER=<WORKER NAME>
NM_ADDR=<HOSTNAME>
NM_PORT=<NM PORT>
NM_USERNAME=<NM USERNAME>
NM_PASSWORD=<NM PWD>
WL_HOME=${DOMAIN_HOME}/../../wlserver

${WL_HOME}/../oracle_common/common/bin/wlst.sh << INNER_EOF
nmConnect('${NM_USERNAME}', '${NM_PASSWORD}', '${NM_ADDR}', '${NM_PORT}', '${DOMAIN_NAME}', '${DOMAIN_HOME}','plain')
nmStart(serverName='${WORKER}', serverType='OHS')
nmServerStatus(serverName='${WORKER}', serverType='OHS')
nmDisconnect()
exit()
INNER_EOF
```


<br><br>

<br>

# 3. References

**Stopping OHS 12.1.3 Fails with "error occurred while performing nmConnect : Cannot connect to Node Manager" (Doc ID 1959645.1)**

**USER HOME Directory 아래에 있는 .wlst Key가 삭제 되었습니다. (Doc ID 3030991.1)**
