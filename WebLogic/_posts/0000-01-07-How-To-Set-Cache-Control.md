---
date: 2025-03-08 10:18:05 +0900
layout: post
title: "[WebLogic] How To Set Cache-Control?"
tags: [Middleware, WebLogic, ]
typora-root-url: ..
---

# 1. Overview

WebLogic 에서 Cache-Control (max-age) 설정 방법

<br>


# 2. Descriptions

WLS 에서는 Cache-Control Header 제어를 가능케 하는 기능은 제공되지 않는다.

기본적으로 JSP/Servlet Code에 의해서 구현해야 한다.

<br>

아래의 JSP code는 Response Header에 Cache-Control 을 추가한다.

해당 JSP 에서만 적용된다.

```jsp
<%
    response.setHeader("Cache-Control", "max-age=10");
%>

<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Index Page</title>
    <script src="js/common.js"></script>
</head>
<body>
    <h1>Welcome to Index Page</h1>
</body>
</html> 
```


<br><br>


이외 정적 파일(JS, HTML, IMG/VIDEO) 들에 대해 Cache-Control header를 적용 하려면 Filter 방식을 이용하거나 Web Server 에서 Response Header를 설정해야 한다.

아래는 Filter 방식에 필요한 Code와

```java
import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;

public class StaticResourceServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;

    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String filePath = "/static" + request.getPathInfo();
        ServletContext context = getServletContext();
        InputStream is = context.getResourceAsStream(filePath);

        response.setHeader("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0");
        response.setHeader("Pragma", "no-cache");
        response.setHeader("Expires", "0");

        // MIME 타입 설정
        String mimeType = context.getMimeType(filePath);
        if (mimeType == null) {
            mimeType = "application/octet-stream";
        }
        response.setContentType(mimeType);

        // 파일 스트림 전송
        OutputStream os = response.getOutputStream();
        byte[] buffer = new byte[1024];
        int bytesRead;
        while ((bytesRead = is.read(buffer)) != -1) {
            os.write(buffer, 0, bytesRead);
        }
        is.close();
        os.flush();
    }
}
```


<br><br>


web.xml 기술 방식이다.

```xml
<web-app>

	<servlet>
		<servlet-name>StaticResourceServlet</servlet-name>
		<servlet-class>example.StaticResourceServlet</servlet-class>
	</servlet>

	<servlet-mapping>
		<servlet-name>StaticResourceServlet</servlet-name>
		<url-pattern>/static/*</url-pattern>
	</servlet-mapping>

</web-app>
```


<br><br>

<br>

# 3. References

**How to Setup Cache-Control: Max-age on WebLogic (Doc ID 2477426.1)**

**WebLogic에서 Cache-Control (max-age) 설정 방법 (Doc ID 3074203.1)**
