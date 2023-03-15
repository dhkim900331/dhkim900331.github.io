---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[Middleware/WebLogic] 12c max request parameter count 최대값 변경"
tags: [Middleware, WebLogic]
typora-root-url: ..
---


# 1. 개요

12c max request parameter count 최대값 변경



# 2. 설명

* HTTP request의 parameter 최대 개수는 기본값으로 10,000개 입니다.

* parameter를 10,001개 이상 request에 담아 보내면 아래와 같이 에러 로그가 발생합니다.

  ```
  <Error> <ServletContext> <BEA-000000> <Rejecting request since max request parameter limit exceeded 10000>
  ```

* 보안상의 이슈로 인해, 10,000개의 제한이 걸려있습니다.

  * 사이트 https://www.oracle.com/technetwork/topics/security/alerts-086861.html 에서 CVE-2011-5035 구체적인 내용을 확인할 수 있습니다.
  * 중요한 보안의 경우 확인하지 못함.

  

  소스 코드의 리뷰로 파라메터 개수 변경이 어려운 경우,

  아래의 가이드로 수치를 변경할 수 있습니다.



```bash
cd /weblogic/wls
cd oracle_common/common/bin

# MaxRequestParameterCount 값을 확인 또는 변경하려는 서버로 로그인
./wlst.sh
connect('아이디','패스워드','t3://인스턴스_주소:포트')

# 아래 명령을 차례대로 입력하여 최대 값 확인
cd('Servers/AdminServer')
cmo.getWebServer().getMaxRequestParameterCount()

# 아래 명령을 차례대로 입력하여 최대 값 수정 및 종료
edit()
startEdit()
cmo.getWebServer().setMaxRequestParameterCount(20000)
save()
activate()
exit()
```

