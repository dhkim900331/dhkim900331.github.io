---
date: 2025-08-29 12:26:41 +0900
layout: post
title: "[WebLogic/JMS] Sample jms application with jdbc store"
tags: [Middleware, WebLogic, ]
typora-root-url: ..
---

# 1. Overview

[Creating-JMS-With-WLST]({{ site.url }}/WebLogic/Creating-JMS-With-WLST) 포스팅에서 생성한 환경에 JDBC Store 구성을 더하고, 샘플 JMS Application 으로 테스트

<br><br>


# 2. Descriptions

- Datasource 생성 필요
- Persistent Store - JDBCStore 생성하여 Datasource를 Targeting 으로 배포
- JMS Server들 마다 Persistent Store를 JDBCStore 를 지정

<br>

> JDBC Store와 JMS Server 는 같은 Targeting (myCluster 등) 을 바라봐야 한다.


<br><br>


Sample app (기본 DD 를 갖는 App에 배포)

```jsp
<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ page import="java.util.*, javax.naming.*, javax.jms.*" %>
<%!
  // ---------- 유틸: 파라미터 숫자 ----------
  private long getLongParamOrDefault(javax.servlet.http.HttpServletRequest req, String name, long def) {
    try { return Long.parseLong(String.valueOf(Objects.toString(req.getParameter(name), String.valueOf(def)))); }
    catch (Exception ignore) { return def; }
  }

  // ---------- 유틸: 스택트레이스 문자열 ----------
  private String toStackTrace(Throwable t) {
    if (t == null) return "";
    java.io.StringWriter sw = new java.io.StringWriter();
    java.io.PrintWriter pw = new java.io.PrintWriter(sw);
    t.printStackTrace(pw);
    pw.flush();
    return sw.toString();
  }

  // ---------- 유틸: 자원 닫기 ----------
  private void closeQuietly(javax.jms.QueueBrowser b) {  // <-- 여기!
    try { if (b != null) b.close(); } catch (Exception ignore) {}
  }
  private void closeQuietly(javax.jms.MessageConsumer c) {
    try { if (c != null) c.close(); } catch (Exception ignore) {}
  }
  private void closeQuietly(javax.jms.MessageProducer p) {
    try { if (p != null) p.close(); } catch (Exception ignore) {}
  }
  private void closeQuietly(javax.jms.Session s) {
    try { if (s != null) s.close(); } catch (Exception ignore) {}
  }
  private void closeQuietly(javax.jms.Connection c) {
    try { if (c != null) c.close(); } catch (Exception ignore) {}
  }
  private void closeQuietly(javax.naming.Context c) {
    try { if (c != null) c.close(); } catch (Exception ignore) {}
  }
%>

<%
  response.setContentType("text/html; charset=UTF-8");

  // ======== 환경값: 필요시 여기만 바꾸세요 ========
  final String JNDI_URL   = "t3://wls.local:8002";  // WLS 주소
  final String CF_JNDI    = "jms/DemoCF";          // ConnectionFactory JNDI
  final String QUEUE_JNDI = "jms/DemoQueue";       // Queue JNDI
  final String JNDI_USER  = null;                  // 도메인 보안 off면 null
  final String JNDI_PASS  = null;                  // ex) "weblogic", "weblogic1"
  // ===============================================

  final String action = Objects.toString(request.getParameter("action"), "").trim(); // send | receive | browse
  final String text   = Objects.toString(request.getParameter("text"), "");
  final long   timeout = getLongParamOrDefault(request, "timeout", 2000L);

  // JMS 핸들
  InitialContext ctx = null;
  Connection conn = null;
  Session jmsSession = null;
  MessageProducer producer = null;
  MessageConsumer consumer = null;
  QueueBrowser browser = null;

  String result = null;
  List<String> browsed = new ArrayList<>();
  String errorStack = null;

  try {
    // JNDI 초기화
    Properties env = new Properties();
    env.put(Context.INITIAL_CONTEXT_FACTORY, "weblogic.jndi.WLInitialContextFactory");
    env.put(Context.PROVIDER_URL, JNDI_URL);
    if (JNDI_USER != null) {
      env.put(Context.SECURITY_PRINCIPAL, JNDI_USER);
      env.put(Context.SECURITY_CREDENTIALS, JNDI_PASS);
    }

    ctx = new InitialContext(env);
    ConnectionFactory cf = (ConnectionFactory) ctx.lookup(CF_JNDI);
    javax.jms.Queue queue = (javax.jms.Queue) ctx.lookup(QUEUE_JNDI);

    conn = cf.createConnection();                     // JMS 1.1
    jmsSession = conn.createSession(false, Session.AUTO_ACKNOWLEDGE);
    conn.start();

    switch (action.toLowerCase(Locale.ROOT)) {
      case "send": {
        producer = jmsSession.createProducer(queue);  // 기본 DeliveryMode=PERSISTENT
        TextMessage msg = jmsSession.createTextMessage(text);
        producer.send(msg);
        result = "메시지 전송 완료: " + msg.getJMSMessageID();
        break;
      }
      case "receive": {
        consumer = jmsSession.createConsumer(queue);
        Message m = consumer.receive(timeout);
        if (m == null) {
          result = "대기 " + timeout + "ms 동안 수신 메시지 없음";
        } else if (m instanceof TextMessage) {
          TextMessage tm = (TextMessage) m;
          result = "수신: " + tm.getText() + " (JMSMessageID=" + tm.getJMSMessageID() + ")";
        } else {
          result = "수신(텍스트 아님): " + m.getClass().getName();
        }
        break;
      }
      case "browse": {
        browser = jmsSession.createBrowser(queue);
        Enumeration<?> e = browser.getEnumeration();
        int i = 0;
        while (e.hasMoreElements() && i < 20) {
          Message m = (Message) e.nextElement();
          if (m instanceof TextMessage) {
            browsed.add(((TextMessage) m).getText());
          } else {
            browsed.add(m.getClass().getName());
          }
          i++;
        }
        result = "브라우즈 " + browsed.size() + "건 (peek만; 소비X)";
        break;
      }
      default: {
        // no-op; 초기 페이지 로드
      }
    }

  } catch (Throwable t) {
    // 1) 브라우저에 보여줄 문자열로 보관
    errorStack = toStackTrace(t);

    // 2) 서버 콘솔(stdout) & 에러(stderr) 출력
    t.printStackTrace(System.out);
    t.printStackTrace(System.err);

    // 3) 사용자 친화적 메시지
    result = "에러 발생: " + t.getClass().getName() + " - " + String.valueOf(t.getMessage());
  } finally {
    // 닫기 (역순)
    try { if (browser != null) browser.close(); } catch (Exception ignore) {}
    closeQuietly(consumer);
    closeQuietly(producer);
    closeQuietly(jmsSession);
    closeQuietly(conn);
    closeQuietly(ctx);
  }
%>

<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8"/>
  <title>JMS Demo (Queue)</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 24px; line-height: 1.5; }
    form { margin: 12px 0; padding: 12px; border: 1px solid #ddd; border-radius: 6px; }
    textarea { width: 100%; height: 120px; }
    code, pre { background: #f7f7f7; padding: 4px 6px; border-radius: 4px; }
    .row { margin: 6px 0; }
    .muted { color: #666; font-size: 90%; }
    .error { color: #b00020; }
  </style>
</head>
<body>
  <h2>JMS Demo (Queue)</h2>

  <div class="row">
    <div>CF: <code><%= CF_JNDI %></code> / Queue: <code><%= QUEUE_JNDI %></code></div>
    <div>Provider: <code><%= JNDI_URL %></code></div>
  </div>

  <form method="post">
    <h3>Send</h3>
    <textarea name="text" placeholder="보낼 메시지를 입력하세요"><%= text %></textarea>
    <input type="hidden" name="action" value="send"/>
    <button type="submit">Send</button>
  </form>

  <form method="post">
    <h3>Receive (consume 1 message)</h3>
    <div class="row">
      Timeout(ms):
      <input type="number" name="timeout" value="<%= timeout %>" min="0" step="100"/>
      <input type="hidden" name="action" value="receive"/>
      <button type="submit">Receive</button>
    </div>
    <div class="muted">AUTO_ACKNOWLEDGE, wait=<%= timeout %>ms</div>
  </form>

  <form method="post">
    <h3>Browse (peek up to 20)</h3>
    <input type="hidden" name="action" value="browse"/>
    <button type="submit">Browse</button>
    <div class="muted">소비 없이 큐 헤드부터 최대 20건만 미리보기</div>
  </form>

  <% if (result != null) { %>
    <h3>Result</h3>
    <pre><%= result %></pre>

    <% if (errorStack != null) { %>
      <h4 class="error">Stack Trace</h4>
      <pre><%= errorStack %></pre>
    <% } %>

    <% if (!browsed.isEmpty()) { %>
      <h4>Browsed Messages</h4>
      <ul>
        <% for (String s : browsed) { %>
          <li><pre><%= s %></pre></li>
        <% } %>
      </ul>
    <% } %>
  <% } %>

</body>
</html>
```

<br>

Queue에 메시지를 넣고, JDBC Store의 Monitoring 에서 메시지 통계를 확인할 수 있고,

`select * from M1_WLSTORE;` Query로 메시지 변화를 확인할 수 있다.

```
SQL> select * from M1_WLSTORE;

        ID       TYPE     HANDLE R
---------- ---------- ---------- -
         1          0          0 A
         2          0          1 A
         3          0          2 A
         4          0          3 A
         5          0          4 A
         6          2          0 0
         7          0          5 A
         8          0          6 A
         9          0          7 A
        10          0          8 A
        11          0          9 A

        ID       TYPE     HANDLE R
---------- ---------- ---------- -
        12          7          0 0
        13          0         10 A
        14          7          1 0
        15          2          1 0
        16          8          0 0
        -1         -1          3 0
 134217727         -3          0 0
 268435454         -3          0 0
 402653181         -3          0 0
 536870908         -3          0 0
 671088635         -3          0 0

        ID       TYPE     HANDLE R
---------- ---------- ---------- -
 805306362         -3          0 0
 939524089         -3          0 0
1073741816         -3          0 0
1207959543         -3          0 0
1342177270         -3          0 0
1476394997         -3          0 0
1610612724         -3          0 0
1744830451         -3          0 0
1879048178         -3          0 0
2013265905         -3          0 0
2147483632         -3          0 0

33 rows selected.
```

<br>

33 rows 는 기본으로 존재하는 내부 메시지로 보여진다.

소비한다고 사라지지 않는다.


<br><br>




<br><br>



<br>

# 3. References

