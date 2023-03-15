---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[Middleware/WebLogic] WTC 설정"
tags: [Middleware, WebLogic, WTC]
typora-root-url: ..
---

# 1. 개요

WTC 설정 가이드




# 2. 설명

## 2.1 테스트 환경

* Tuxedo
  * Address : 172.16.0.145:20001
  * Local Access Point ID : TDOM
* WebLogic
  * Address : 192.168.56.2:8001
  * Local Access Point ID : WDOM02

> Tuxedo 입장에서, WDOM02는 Remote Access Point ID 다.



## 2.2 웹로직 설정

(1). 콘솔 > 상호 운용성 > WTC 서버 > 새로 만들기 > WTC Server-0

![WTCConfigration_1](/../assets/posts/images/01-WebLogic/WTCConfigration/WTCConfigration_1.png)



(2). 새로 만든 WTC Server-0 대상 M1 설정

![WTCConfigration_2](/../assets/posts/images/01-WebLogic/WTCConfigration/WTCConfigration_2.png)



(3). WTC Server-0 > 로컬 AP

![WTCConfigration_3](/../assets/posts/images/01-WebLogic/WTCConfigration/WTCConfigration_3.png)

> `netstat -an | grep 8011`으로 할당되지 않은 포트 검증하고 진행



(4). WTC Server-0 > 원격 AP

![WTCConfigration_4](/../assets/posts/images/01-WebLogic/WTCConfigration/WTCConfigration_4.png)



(5). WTC Server-0 > Import

![WTCConfigration_5](/../assets/posts/images/01-WebLogic/WTCConfigration/WTCConfigration_5.png)

> Tuxedo 에서 WebLogic 쪽 서비스 호출할 때 이름이다.



## 2.3 턱시도 서비스 호출

(1). 웹로직 기동 시 8001, 8011 port 확인된다.

![WTCConfigration_6](/../assets/posts/images/01-WebLogic/WTCConfigration/WTCConfigration_6.png)



(2). 웹로직 Log에서 TDOM 연결 되었음이 확인된다.

![WTCConfigration_7](/../assets/posts/images/01-WebLogic/WTCConfigration/WTCConfigration_7.png)



(3). 아래 JSP를 호출 시 TOUPPER 서비스는 잘 호출되나,
정의되지 않은 `tpcall("LTOUPPER")` 호출하면 에러 발생한다.

![WTCConfigration_8](/../assets/posts/images/01-WebLogic/WTCConfigration/WTCConfigration_8.png)



```jsp
<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
    

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<title>WTC test jsp</title>
</head>
<body>
<%@ page import="java.util.*, java.text.SimpleDateFormat, , javax.naming.* , weblogic.wtc.gwt.*, weblogic.wtc.jatmi.*"%>

<%!
java.util.Date utilDate = new java.util.Date();

public void log(String text){
	System.out.println(utilDate.toString() + " : " + text);
}


public String Toupper(String toConvert)
		   throws TPException, TPReplyException
		{
		     Context ctx;
		     TuxedoConnectionFactory tcf;
		     TuxedoConnection myTux;
		     TypedString myData;
		     Reply myRtn;
		     int status;

		     log("toupper called, converting " + toConvert);

		     try {
		          ctx = new InitialContext();
		          tcf = (TuxedoConnectionFactory) ctx.lookup("tuxedo.services.TuxedoConnection");
		     }
		     catch (NamingException ne) {
		          // Could not get the tuxedo object, throw TPENOENT
		           throw new TPException(TPException.TPENOENT, "Could not get TuxedoConnectionFactory : " + ne);
		     }

		     myTux = tcf.getTuxedoConnection();

		     myData = new TypedString(toConvert);

		     log("About to call tpcall");
		     try {
		          myRtn = myTux.tpcall("TOUPPER", myData, 0);
		}
		     catch (TPReplyException tre) {
		          log("tpcall threw TPReplyExcption " + tre);
		          throw tre;
		     }
		     catch (TPException te) {
		          log("tpcall threw TPException " + te);
		          throw te;
		     }
		     catch (Exception ee) {
		          log("tpcall threw exception: " + ee);
		          throw new TPException(TPException.TPESYSTEM, "Exception: " + ee);
		     }
		     log("tpcall successfull!");

		     myData = (TypedString) myRtn.getReplyBuffer();

		     myTux.tpterm();// Closing the association with Tuxedo

		     return (myData.toString());
		}


%>

<form name="testform" action="/test/testWTC.jsp" method="post">
  Input Text to convert : <input type="text" size="30" name="aaa" value="lower_case_character">
    <input type="submit" name="submitButton" value="submit">
</form>


<%
	
	if ( request.getParameter("aaa") != null) {
		String toConvert = request.getParameter("aaa");
		out.print("Converted text : " + Toupper(toConvert));
	}
%>

	


</body>
</html>

```



