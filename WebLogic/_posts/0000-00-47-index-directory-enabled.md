---
date: 2024-10-30 14:41:56 +0900
layout: post
title: "[WebLogic] index-directory-enabled"
tags: [Middleware, WebLogic]
typora-root-url: ..
---

# 1. Overview
index-directory-enabled 옵션 설명


<br><br>


# 2. Descriptions
[index-directory-enabled](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/wbapp/weblogic_xml.html#GUID-25A61D83-3C10-45B6-9481-93035F05CEF7) 옵션을 true로 적용 시,

`http://.../<context-root>/` 와 같이 Directory 를 URI로 호출 할때, Directory Listing을 표시할지를 정의한다.

<br>

같이 살펴봐야 할 옵션으로 [welcome-file-list](https://docs.oracle.com/en/middleware/fusion-middleware/weblogic-server/12.2.1.4/wbapp/web_xml.html#GUID-A75C1CFC-D52C-4C78-B31F-F715E37DB84A) 옵션이 있다.

해당 옵션의 기본값은 [Servlet 3.1 Sepc 에서 8.1.6 Other annotations / conventions](https://download.oracle.com/otn-pub/jcp/servlet-3_1-fr-eval-spec/servlet-3_1-final.pdf?AuthParam=1729821086_e05740d638ef9e1da0ddbba4023ac240) 에 따라 index.html, index.jsp 등이 있고, web.xml 에서 이를 재지정할 수 있다.

해당 옵션에 의해 welcome-file이 존재하면, Directory listing 보다 우선하여 해당 jsp 가 호출된다.


<br><br>


# 3. References
How to Disable Directory Indexing for WebLogic Server (Doc ID 2342612.1)