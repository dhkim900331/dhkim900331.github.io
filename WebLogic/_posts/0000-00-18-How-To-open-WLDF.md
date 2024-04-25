---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] WLDF WLS_DIAGNOSTICS000000.DAT 열기"
tags: [Middleware, WebLogic, WLDF]
typora-root-url: ..
---


# 1. 개요

셧다운 된 서버의 DAT파일만 열 수 있는 것으로 보임.
{{ site.content.br_small }}
# 2. 설명

```
./wlst.sh
exportDiagnosticData(logicalName='HarvestedDataArchive', logName='/sw/weblogic/12cR2/domains/base_domain/sportal71/data/store/WLS_DIAGNOSTICS000000.DAT', logRotationDir='.', storeDir='/sw/weblogic/12cR2/domains/base_domain/sportal71', query='', exportFileName='sportal71.csv', elfFields='', beginTimestamp=0L, format='csv')
```
{{ site.content.br_small }}
- logName 은 실존하는 파일 경로가 아니다. 다만 실행해도 저 경로안에 DAT 파일이 생성되지는 않았다.
- storeDir은 분석하려는 DAT 파일이 있는 디렉터리이다.
{{ site.content.br_small }}
12cR1 기준 추출가능한 데이터 유형은 [여기](https://docs.oracle.com/middleware/1213/wls/WLSTC/reference.htm#WLSTC244)서 확인
