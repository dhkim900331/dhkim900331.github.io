---
date: 2024-11-27 17:16:55 +0900
layout: post
title: "[WebLogic] Intermittently hangs with using file session"
tags: [Middleware, WebLogic, HttpSession]
typora-root-url: ..
---

# 1. Overview

HttpSession store method로 file 을 사용하는 경우, 간헐적으로 Hang 발생 사례


<br><br>



# 2. Descriptions

아무런 동작을 하지 않는, `test.jsp`와 같은 페이지를 호출 시에도, 응답이 간헐적으로 지연되는 현상이 있다.

Thread dump를 추출하여 아래와 같은 Stack Trace가 출력되었다.

```
  "[ACTIVE] ExecuteThread: '13' for queue: 'weblogic.kernel.Default (self-tuning)'" #60 daemon prio=5 os_prio=0 tid=0x000000001f076800 nid=0x21b4 runnable [0x0000000022c6e000]
     java.lang.Thread.State: RUNNABLE
   at java.io.WinNTFileSystem.list(Native Method)
   at java.io.File.list(File.java:1122)
   at weblogic.servlet.internal.session.FileSessionContext$FileEnumerator.recurse(FileSessionContext.java:835)
   at weblogic.servlet.internal.session.FileSessionContext$FileEnumerator.recurse(FileSessionContext.java:840)
   at weblogic.servlet.internal.session.FileSessionContext$FileEnumerator.recurse(FileSessionContext.java:840)
   at weblogic.servlet.internal.session.FileSessionContext$FileEnumerator.recurse(FileSessionContext.java:840)
   at weblogic.servlet.internal.session.FileSessionContext$FileEnumerator.recurse(FileSessionContext.java:840)
   at weblogic.servlet.internal.session.FileSessionContext$FileEnumerator.recurse(FileSessionContext.java:840)
   at weblogic.servlet.internal.session.FileSessionContext$FileEnumerator.recurse(FileSessionContext.java:840)
   at weblogic.servlet.internal.session.FileSessionContext$FileEnumerator.recurse(FileSessionContext.java:840)
   at weblogic.servlet.internal.session.FileSessionContext$FileEnumerator.recurse(FileSessionContext.java:840)
   at weblogic.servlet.internal.session.FileSessionContext$FileEnumerator.recurse(FileSessionContext.java:840)
   at weblogic.servlet.internal.session.FileSessionContext$FileEnumerator.recurse(FileSessionContext.java:840)
   at weblogic.servlet.internal.session.FileSessionContext.getIdsInternal(FileSessionContext.java:683)
   - locked <0x0000000082509b78> (a java.lang.Object)
   at weblogic.servlet.internal.session.SessionContext$SessionInvalidator.cleanupExpiredSessions(SessionContext.java:703)
   ...
```

<br>

HttpSession의 저장을 위해 다음의 설정이 적용되어 있다.

```xml
   <session-descriptor>
     <persistent-store-type>file</persistent-store-type>
   </session-descriptor>
```

<br>

이러한 경우, WLS는 모든 JSP 요청에 대해 Session을 생성하도록 동작한다.

모든 HttpSession을 File 기반으로 생성하고, Session의 읽기/쓰기 및, Expired 되면 다시 삭제하는 모든 일련의 과정이 Disk I/O 에 의존한다.

<br>

Stack Trace 최상위 `java.io.WinNTFileSystem.list(Native Method)` 는 OS Level 수준에서 Disk I/O 의 응답을 기다리는 것을 보여주고 있다.

HttpSession을 File로 사용하여, 발생하는 지연이므로 Disk I/O 에서 지연되는 부분을 점검하거나,

File이 아닌 방식으로 관리하도록 구성한다.


<br><br>



# 3. References

[persistent-store-type](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wbapp/weblogic_xml.html#GUID-699B48A7-879D-4DF2-A919-6AAE62A93BEB)

HttpSession을 File로 관리하는 경우, 간헐적으로 지연 현상 (Doc ID 3060640.1)
