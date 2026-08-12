---
date: 2025-08-29 12:22:37 +0900

layout: post
title: "[WebTier/OHS] Converting a wallet to auto_login_only for 14cR2"
tags: [WebTier, OHS, Wallet, SSL, Certificate, auto_login_only]
typora-root-url: ../..
---

# 1. Overview

OHS 12cR2 Wallet을 OHS 14cR2 에서 사용 하기 위해 auto_login_only 로 Converting 해야 할 때를 위한 템플릿

<br><br>


# 2. Descriptions

```sh
# 기본 변수
export ORACLE_HOME=/sw/webtier/14cR2
export WALLETPATH=/sw/webtier/14cR2/domains/base_domain/mywallet
WALLETPASS=weblogic1

cd ${WALLETPATH}
${ORACLE_HOME}/perl/bin/perl ${ORACLE_HOME}/ohs/common/bin/convert_to_auto_login_only.pl ${WALLETPATH} ${WALLETPATH}/auto_login_only ${WALLETPASS}
```

<br><br>


# 3. References

Upgrade to Oracle HTTP Server 14.1.2+ Must Convert Auto_login Wallets to Auto_login_only Using convert_to_auto_login_only.pl (Doc ID 3052996.1)	

