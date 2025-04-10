---
date: 2025-04-11 00:21:07 +0900
layout: post
title: "[WebTier/OHS] Missing compat-libpthread-nonshared with Linux 9"
tags: [WebTier, OHS, OFM, WebLogic, RHEL9, OL9, compat-libpthread-nonshared]
typora-root-url: ..
---

# 1. Overview

Oracle Fusion Middleware 12cR2(12.2.1.4) 를 OL/RHEL 9 설치 시 compat-libpthread-nonshared 패키지 누락 이슈

OHS 이슈에서 먼저 발견했기 때문에, 게시물이 OHS에 있을 뿐, OFM 전체에서 발생한다.

<br>

# 2. Descriptions

RHEL 8 이후, RHEL 9 부터는 'compat-libpthread-nonshared' 패키지가 제공되지 않는다.

[Release 12.2.1.4 의 Minimum Requirements for the Linux Operating System](https://docs.oracle.com/en/middleware/fusion-middleware/12.2.1.4/sysrs/system-requirements-and-specifications.html#GUID-37C51062-3732-4A4B-8E0E-003D9DFC8C26__LINUX9) 에서는 ' compat-libpthread-nonshared' 패키지를 전제조건이다.

RHEL 9 에 OFM 제품군. 예로 OHS 12cR2 를 설치 시 해당 패키지가 설치되어 있지 않으니, 진행되지 않는다.

이를 위해 Patch 35009277 를 적용해야 하며, 자세한 방법은 Patch의 README를 반드시 숙지해야 한다.

> silent 모드로 OHS 설치 시, 예시 명령어 : `<distribution>/fmw_12.2.1.4.0_ohs_linux64.bin -silent -responseFile ... -invPtrLoc ... -ignoreSysPrereqs...  -prereqConfigLoc <PATCH_TOP>/35009277/prereq_metadata/oracle.as.install.ohs.prerequisite/prereq`

<br>

참고로, [Release 14.1.2 의 Minimum Requirements for the Linux Operating System](https://docs.oracle.com/en/middleware/fusion-middleware/14.1.2/sysrs/system-requirements-and-specifications.html#GUID-37C51062-3732-4A4B-8E0E-003D9DFC8C26) 에서 부터는 위 패키지를 요구하지 않기 때문에, 문제가 발생하지 않는다.


<br><br>


# 3. References

**Oracle Fusion Middleware 12.2.1.4.0 Support with OL/RHEL9 (Doc ID 2936471.1)**

