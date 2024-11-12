---
date: 2024-06-25 16:09:26 +0900
layout: post
title: "[WebLogic] Deployer Command"
tags: [Middleware, WebLogic, Deployer]
typora-root-url: ..
---

# 1. Overview

weblogic.Deployer 의 기본적인 사용 방법


<br><br>


# 2. Descriptions

* 배포된 App list 조회

  * ```
    java weblogic.Deployer -adminurl <ADMIN URL> -username <USERNAME> -password <PWD> -listapps
    ```

<br>

* App 배포 및 롤백

  * ```
    java weblogic.Deployer -adminurl <ADMIN URL> -username <USERNAME> -password <PWD> -deploy <APP PATH> -name <APP NAME> -nostage -targets <TARGET'S NAME> -verbose -debug
    
    java weblogic.Deployer -adminurl <ADMIN URL> -username <USERNAME> -password <PWD> -undeploy -name <APP NAME> -targets <TARGET'S NAME>
    ```

<br>

* 사용 가능 명령어 출력

  * ```
    java weblogic.Deployer -advanced
    ```


<br><br>


# 3. References

[weblogic.Deployer Command-Line Reference](https://docs.oracle.com/middleware/1213/wls/DEPGD/wldeployer.htm#DEPGD318)
