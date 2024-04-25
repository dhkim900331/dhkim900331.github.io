---
date: 2023-05-11 09:07:29 +0900
layout: post
title: "[Servlet/JSP] File upload App"
tags: [Programming, JSP, Servlet, File, Upload]
typora-root-url: ..
---

# 1. Overview

~~Commons FileUpload 라이브러리를 이용한 파일 업로드 예제 어플리케이션~~

[Uploading-File-With-Servlet]({{ site.url }}/weblogic/Uploading-File-With-Servlet) 를 작성하며 알게 되었는데, Servlet 3.0 부터 외부 라이브러리 없이 request.getParts() 로 가능하다.
{{ site.content.br_small }}
# 2. Description
{{ site.content.br_small }}
배포할 /sw/app/fileUpload 어플리케이션 구조는 다음과 같다.

```
/sw/app/fileUpload/
├── META-INF
└── WEB-INF
    ├── classes
    │   └── example
    │       └── dong
    │           └── FileUploadServlet.class
    ├── src
    │   └── example
    │       └── dong
    │           └── FileUploadServlet.java
    ├── weblogic.xml
    └── web.xml
```

> xml file에는 별다른 내용이 없다.
{{ site.content.br_small }}
FileUploadServlet.java 코드

```java
package example.dong;
import java.io.*;
import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;


@WebServlet(name = "FileUploadServlet", urlPatterns = { "/fileuploadservlet" })
@MultipartConfig(
  fileSizeThreshold = 1024 * 1024 * 10,     // 10 MB
  maxFileSize = 1024 * 1024 * 1024 * 1,    // 1 GB
  maxRequestSize = 1024 * 1024 * 1024 * 1  // 1 GB
)
/* Simple Java File Upload Example */
public class FileUploadServlet extends HttpServlet {

  public void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {

    /* For comparison of Servlet and Apache Commons File Upload APIs */
    Part filePart = request.getPart("file");
    String fileName = filePart.getSubmittedFileName();
    for (Part part : request.getParts()) {
      part.write(fileName);
    }
    response.getWriter().print("Sucessfully Java file upload. -> " + filePart.getSize());
  }

}
```
{{ site.content.br_small }}
maxFileSize = maxRequestSize = 1024 * 1024 * 1024 * 10 과 같이 10GB 으로 설정하면 Exception 발생한다.

```
The field file exceeds its maximum permitted size of -2147483648 characters.
```
{{ site.content.br_small }}
Field 가 수용가능한 범위는 int32 이며, integer 32bit 범위는 -2,147,483,648 ~ 2,147,483,647 이다.

maxFileSize = maxRequestSize = 2147483647 을 설정하여 최대 한계인 2GB File upload 까지 가능하다.

maxFileSize = maxRequestSize = -1 을 설정하면, Unlimited 이다.
{{ site.content.br_small }}
배포 후 curl 로 테스트 한다.

```sh
$ curl -F 'file=@/tmp/test.txt' http://../fileUpload/fileuploadservlet
Sucessfully Java file upload. -> 10485760
```
{{ site.content.br_small }}
참고로, test.txt (10 MB)와 같은 파일은 [다음의 명령](https://zetawiki.com/wiki/%EB%A6%AC%EB%88%85%EC%8A%A4_%EB%8C%80%EC%9A%A9%EB%9F%89_%ED%8C%8C%EC%9D%BC_%EC%83%9D%EC%84%B1)으로 간편하게 생성할 수 있다.

```sh
$ dd if=/dev/zero of=test.txt bs=1 count=0 seek=10M
```

