---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] WLDF WLS_DIAGNOSTICS000000.DAT 열기"
tags: [Middleware, WebLogic, WLDF]
typora-root-url: ..
---


# 1. 개요

셧다운 된 서버의 DAT파일만 열 수 있는 것으로 보임.
{{ site.content.br_big }}
# 2. 설명

```
./wlst.sh
exportDiagnosticData(logicalName='EventsDataArchive', logName='/home/cs2/kdh/weblogic/12.2.1/domains/base_domain/servers/m1/data/store/diagnostics/WLS_DIAGNOSTICS000000.DAT', storeDir='/home/cs2/kdh/weblogic/12.2.1/domains/base_domain/servers/m1/data/store/diagnostics' ,exportFileName='myExport.xml')
```
{{ site.content.br_small }}
myExport.xml 열면 xml 로 데이터 집계됨

12cR1 기준 추출가능한 데이터 유형은 [여기](https://docs.oracle.com/middleware/1213/wls/WLSTC/reference.htm#WLSTC244)서 확인
