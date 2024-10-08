---
layout: post
title: "[WebLogic] When Using Same Cookie-Name"
tags: [Middleware, WebLogic, JSESSIONID, Cookie, Invalidate, Session]
typora-root-url: ..
---

# 1. Overview
배포된 2개 이상의 App이 같은 Cookie Name을 사용하는 경우


# 2. Descriptions
다음과 같은 weblogic.xml 구성을 갖는 두 개의 Application(/testapp , /testapp2)이 배포되어 있다.
```xml
<weblogic-web-app>
    <session-descriptor>
        <persistent-store-type>replicated_if_clustered</persistent-store-type>
        <timeout-secs>1800</timeout-secs>
    </session-descriptor>

    <container-descriptor>
        <servlet-reload-check-secs>1</servlet-reload-check-secs>
        <resource-reload-check-secs>1</resource-reload-check-secs>
    </container-descriptor>

    <jsp-descriptor>
        <page-check-seconds>0</page-check-seconds>
    </jsp-descriptor>
</weblogic-web-app>
```

사전에, `weblogic.servlet.internal.session.DebugHttpSessions`를 활성화 하여 Debug log를 볼 수 있다.

`/testapp/session.jsp` 를 호출하여 새로운 Session을 생성하고자 할 때, Debug log는
```
<Debug> <Http> <BEA-000000> <Request received from: /10.191.29.64, Secure: false, Request: weblogic.servlet.internal.ServletRequestImpl@170addca[
GET /testApp/session.jsp HTTP/1.1
Connection: keep-alive
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9,ko;q=0.8

...

<Debug> <Http> <BEA-000000> <weblogic.servlet.internal.ServletRequestImpl@170addca - /testApp/session.jsp: SessionID not found for WASC=ServletContext@138462647[app:testApp module:testApp path:/testApp spec-version:3.1]>
<Debug> <Http> <BEA-000000> <weblogic.servlet.internal.ServletRequestImpl@170addca - /testApp/session.jsp: Creating new session>
<Debug> <HttpSessions> <BEA-000000> <[HTTP Session:100046]Creating new session with ID: _oZAg397R6Kh1IgEvGifQLoWhT7eKJdZpA8AExt7E2_Zear3ZxWp for Web application: /testApp.>
<Debug> <HttpSessions> <BEA-000000> <[HTTP Session:100050]The current server is becoming the primary server for replicated session ID: _oZAg397R6Kh1IgEvGifQLoWhT7eKJdZpA8AExt7E2_Zear3ZxWp.>
<Debug> <Http> <BEA-000000> <weblogic.servlet.internal.ServletRequestImpl@170addca - /testApp/session.jsp: Wrote cookie: JSESSIONID=_oZAg397R6Kh1IgEvGifQLoWhT7eKJdZpA8AExt7E2_Zear3ZxWp!-867346605!NONE; path=/; HttpOnly>
<Debug> <Http> <BEA-000000> <Response committed. request: 'weblogic.servlet.internal.ServletRequestImpl@170addca - /testApp/session.jsp' response: weblogic.servlet.internal.ServletResponseImpl@7ad41652[
HTTP/1.1 200 OK
Date: : Mon, 30 Sep 2024 01:20:12 GMT
Content-Length: : 206
Content-Type: : text/html;charset=UTF-8
X-ORACLE-DMS-ECID: 3974f49c-f689-4a20-8c70-a969bcb4908d-00000014
X-ORACLE-DMS-RID: 0
Set-Cookie: JSESSIONID=_oZAg397R6Kh1IgEvGifQLoWhT7eKJdZpA8AExt7E2_Zear3ZxWp!-867346605!NONE; path=/; HttpOnly
]>
```

다른 탭에서, `/testapp2/session.jsp` 호출 시, 같은 브라우저이고 같은 site domain이므로 Header에 Cookie가 전달된다.
이 App의 Context에는 Session이 아직 없기 때문에, 찾지 못한다. ('Trying other contexts' 부분)
해당 JSESSIONID 를 재사용 하되, 다른 Value를 부여한다. ('Creating new session' 부분)
```
<Debug> <Http> <BEA-000000> <Request received from: /10.191.29.64, Secure: false, Request: weblogic.servlet.internal.ServletRequestImpl@21b720dc[
GET /testApp2/session.jsp HTTP/1.1
Connection: keep-alive
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate
Accept-Language: en-US,en;q=0.9,ko;q=0.8
Cookie: JSESSIONID=_oZAg397R6Kh1IgEvGifQLoWhT7eKJdZpA8AExt7E2_Zear3ZxWp!-867346605!NONE

]>

...

<Sep 30, 2024 10:23:52,379 AM KST> <Debug> <Http> <BEA-000000> <weblogic.servlet.internal.ServletRequestImpl@21b720dc - /testApp2/session.jsp: SessionID: _oZAg397R6Kh1IgEvGifQLoWhT7eKJdZpA8AExt7E2_Zear3ZxWp!-867346605!NONE found in cookie header>
<Sep 30, 2024 10:23:52,379 AM KST> <Debug> <Http> <BEA-000000> <weblogic.servlet.internal.ServletRequestImpl@21b720dc - /testApp2/session.jsp: SessionID= _oZAg397R6Kh1IgEvGifQLoWhT7eKJdZpA8AExt7E2_Zear3ZxWp found for WASC=ServletContext@1630425426[app:testApp2 module:testApp2 path:/testApp2 spec-version:3.1]>
<Sep 30, 2024 10:23:52,379 AM KST> <Debug> <Http> <BEA-000000> <weblogic.servlet.internal.ServletRequestImpl@21b720dc - /testApp2/session.jsp: Trying to find session: _oZAg397R6Kh1IgEvGifQLoWhT7eKJdZpA8AExt7E2_Zear3ZxWp!-867346605!NONE>
<Sep 30, 2024 10:23:52,384 AM KST> <Debug> <Http> <BEA-000000> <weblogic.servlet.internal.ServletRequestImpl@21b720dc - /testApp2/session.jsp: Trying other contexts to find valid session for id: _oZAg397R6Kh1IgEvGifQLoWhT7eKJdZpA8AExt7E2_Zear3ZxWp!-867346605!NONE>
<Sep 30, 2024 10:23:52,384 AM KST> <Debug> <Http> <BEA-000000> <weblogic.servlet.internal.ServletRequestImpl@21b720dc - /testApp2/session.jsp: Couldn't find valid session for id: _oZAg397R6Kh1IgEvGifQLoWhT7eKJdZpA8AExt7E2_Zear3ZxWp!-867346605!NONE>
<Sep 30, 2024 10:23:52,406 AM KST> <Debug> <HttpSessions> <BEA-000000> <[HTTP Session:100046]Creating new session with ID: _oZAg397R6Kh1IgEvGifQLoWhT7eKJdZpA8AExt7E2_Zear3ZxWp for Web application: /testApp2.>
<Sep 30, 2024 10:23:52,407 AM KST> <Debug> <HttpSessions> <BEA-000000> <[HTTP Session:100050]The current server is becoming the primary server for replicated session ID: _oZAg397R6Kh1IgEvGifQLoWhT7eKJdZpA8AExt7E2_Zear3ZxWp.>
<Sep 30, 2024 10:23:52,409 AM KST> <Debug> <HttpSessions> <BEA-000000> <sessionId:_oZAg397R6Kh1IgEvGifQLoWhT7eKJdZpA8AExt7E2_Zear3ZxWp associated with roid:5659102074411398003>
```

- 어느 한쪽에서 `session.invalidate()` 시에, 두 App에서 모든 JSESSIONID가 삭제된다.
- 두 App의 자체 Context에 JSESSIONID 가 보관되지만, invalidate 에서는 공통적으로 삭제된다는 것이 확인된다.
- 두 App의 JSESSIONID의 분리를 위해, cookie-name 또는 cookie-path 를 별다르게 한다. (같은 Site Url 아래에 Cookie가 저장되므로)


# 3. References
https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wbapp/weblogic_xml.html
