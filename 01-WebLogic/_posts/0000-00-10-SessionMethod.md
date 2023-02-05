---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] Session을 생성하고 복제하는 Method (setAttribute, getAttribute, getSession)"
tags: [WAS, WebLogic, Session]
typora-root-url: ..
---


# 1. 개요

Session을 생성하고 복제하는 Method (setAttribute, getAttribute, getSession)



# 2. Oracle 공식 문서 확인

[여기](http://docs.oracle.com/cd/E23943_01/web.1111/e13709/failover.htm /l CLUST201) 에서 Session Replocation Sync가 setAttribute method로 동작한다는 부분은 다음과 같습니다.

> (setAttribute 로 검색시)

![SessionMethod_1](/../assets/posts/images/01-WebLogic/SessionMethod/SessionMethod_1.png)



# 3. 실제 Test 결과 및 결론

Session 생성과 복제는, setAttribute, getAttribute method로 동작함을 확인하였습니다만.

실제론, FailoverTest_get.jsp를 다음 처럼 수정하니, getSession(true)으로 Session 생성/복제가 동작됨을 확인했습니다.



```FailoverTest_get.jsp
<%
        // Session
        session = request.getSession(true);
%>
Current Connected Server: <h3><%=serverName%></h3>
```

>setAttribute()와 getAttribute()는 javax.servlet.ServletRequest class에 구현되어 있습니다.
>
>getSession()은 javax.servlet.http class에 구현되어 있으며, javax.servlet.ServletRequest를 상속 받습니다.
>
>(public interface HttpServletRequest extends ServletRequest)



[여기](http://docs.oracle.com/javaee/6/api/javax/servlet/http/HttpServletRequest.html) 문서의 문서의 getSession() 설명입니다.

getSession(), getSession(true) = HttpSession이 존재하면 현재 HttpSession을 반환하고 존재하지 않으면 새로이 세션을 생성합니다.

getSession(false) = HttpSession이 존재하면 현재 HttpSession을 반환하고 존재하지 않으면 새로이 생성하지 않고 그냥 null을 반환합니다.



![SessionMethod_2](/../assets/posts/images/01-WebLogic/SessionMethod/SessionMethod_2.png)



