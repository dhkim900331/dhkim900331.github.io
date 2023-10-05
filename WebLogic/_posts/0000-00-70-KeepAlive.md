---
date: 2023-06-30 09:02:19 +0900
layout: post
title: "[WebLogic] Keep Alive"
tags: [Middleware, WebLogic, KeepAlive, HTTP]
typora-root-url: ..
---

# 1. Overview

WebLogic 12cR2 환경에서 Keep Alive 가 어떻게 동작하는지 살펴본다.

<br><br>
# 2. Descriptions

<br>
2023-06-29 기준으로 아래의 Java program으로 HTTP Urlconnection을 통해 hello.jsp 호출

그리고 1분 Sleep 이후 world.jsp 호출을 하도록 했는데,

Managed Server가 기본 30 초 이상의 KeepAlive Timeout이 설정되어 있음에도

대략 10초 안에 ESTABLISHED가 TIME_WAIT으로 변경된다.

<br>
HttpUrlConnection 에서 채널이 사라지는 듯한 느낌이다.

크롬 브라우저를 통해 호출 시에는, 크롬 브라우저를 종료하면 바로 사라지는 것을 보아 유추하였다.

<br>
소스 프로그램에서 Keep Alive Header가 제대로 들어가지 않은 것인지..

호출 대상을 OHS 등으로 변경해보아야 할 것 같고, 또는 Header에 값이 안들어간 것인지..

아니면 WLS keepAlive 설정이기본값 30초라고 되어있지만, 5초 처럼 동작한 바가 있다.

(기본 설정환경에서)

<br>
버그 인지.. PSU 적용 후 해봐야 하는지..

<br>
아래는 위 환경에서 쓰인 약간 다른 두 개의 프로그램 코드

```java
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class Java2WAS {
  public static void main(String[] args) {
    int callCount = args.length;
    
    try {
      for(int i=0; callCount>i; i++) {
        httpGetConnection(args[i]);
        Thread.sleep(10 * 1000);
      }
    } catch (Exception e){
      e.printStackTrace();
    }
  }

  private static void httpGetConnection(String UrlData) {
    //http 통신을 하기위한 객체 선언 실시
    URL url = null;
    HttpURLConnection conn = null;

    //http 통신 요청 후 응답 받은 데이터를 담기 위한 변수
    String responseData = "";
    String responseCode = "";
    BufferedReader br = null;
    StringBuffer sb = null;

    try {
      //파라미터로 들어온 url을 사용해 connection 실시
      url = new URL(UrlData);
      conn = (HttpURLConnection) url.openConnection();

      //http 요청에 필요한 타입 정의 실시
      conn.setRequestMethod("GET");
      conn.setRequestProperty("Accept", "text/plain");
      conn.setRequestProperty("Connection", "keep-alive");
      conn.setRequestProperty("Keep-alive", "timeout=60, max=99");

      //http 요청 실시
      conn.connect();
      log("http 요청 방식 : "+"GET");
      log("http 요청 타입 : "+"text/plain");
      log("http 요청 타입 : "+"keep-alive");
      log("http 요청 주소 : "+UrlData);

      //http 요청 후 응답 받은 데이터를 버퍼에 쌓는다
      br = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
      sb = new StringBuffer();
      while ((responseData = br.readLine()) != null) {
        sb.append(responseData); //StringBuffer에 응답받은 데이터 순차적으로 저장 실시
      }

    //http 요청 응답 코드 확인 실시
    responseCode = String.valueOf(conn.getResponseCode());
    log("http 응답 코드 : "+responseCode);
    log("http 응답 데이터 : "+sb.toString());
    } catch (Exception e) {
      e.printStackTrace();
    } finally {
      //http 요청 및 응답 완료 후 BufferedReader를 닫아줍니다
      try {
        if (br != null) {
          br.close();
        }
      } catch (Exception e) {
        e.printStackTrace();
      }
    }
  }
  
  private static void log(String log){
    System.out.println("[INFO] " + log);
  }
}
```

<br><br>
```java
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class Java2WAS {
  public static void main(String[] args) {
    httpGetConnection();
  }

  private static void httpGetConnection() {
    //http 통신을 하기위한 객체 선언 실시
    String UrlData = "";
    URL url = null;
    HttpURLConnection conn = null;

    //http 통신 요청 후 응답 받은 데이터를 담기 위한 변수
    String responseData = "";
    String responseCode = "";
    BufferedReader br = null;
    StringBuffer sb = null;

    try {
      //파라미터로 들어온 url을 사용해 connection 실시
      UrlData = "http://wls.local:8002/SessionApp/hello.jsp";
      url = new URL(UrlData);
      conn = (HttpURLConnection) url.openConnection();

      //http 요청에 필요한 타입 정의 실시
      conn.setRequestMethod("GET");
      conn.setRequestProperty("Accept", "text/plain");
      conn.setRequestProperty("Connection", "keep-alive");
      conn.setRequestProperty("Keep-alive", "timeout=10, max=99");

      //http 요청 실시
      conn.connect();
      log("http 요청 방식 : "+"GET");
      log("http 요청 타입 : "+"text/plain");
      log("http 요청 타입 : "+"keep-alive");
      log("http 요청 주소 : "+UrlData);

      //http 요청 후 응답 받은 데이터를 버퍼에 쌓는다
      br = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
      sb = new StringBuffer();
      while ((responseData = br.readLine()) != null) {
        sb.append(responseData); //StringBuffer에 응답받은 데이터 순차적으로 저장 실시
      }

    //http 요청 응답 코드 확인 실시
    responseCode = String.valueOf(conn.getResponseCode());
    log("http 응답 코드 : "+responseCode);
    log("http 응답 데이터 : "+sb.toString());
    
    
    try {
      Thread.sleep(60 * 1000);
      log("sleep done...");
    } catch (Exception e) {
      e.printStackTrace();
    }
    
    
    // 같은 Channel에 다른 페이지 호출
    
      //파라미터로 들어온 url을 사용해 connection 실시
      UrlData = "http://wls.local:8002/SessionApp/world.jsp";
      url = new URL(UrlData);
      conn = (HttpURLConnection) url.openConnection();

      //http 요청에 필요한 타입 정의 실시
      conn.setRequestMethod("GET");
      conn.setRequestProperty("Accept", "text/plain");
      conn.setRequestProperty("Connection", "keep-alive");
      conn.setRequestProperty("Keep-alive", "timeout=10, max=99");

      //http 요청 실시
      conn.connect();
      log("http 요청 방식 : "+"GET");
      log("http 요청 타입 : "+"text/plain");
      log("http 요청 타입 : "+"keep-alive");
      log("http 요청 주소 : "+UrlData);

      //http 요청 후 응답 받은 데이터를 버퍼에 쌓는다
      br = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
      sb = new StringBuffer();
      while ((responseData = br.readLine()) != null) {
        sb.append(responseData); //StringBuffer에 응답받은 데이터 순차적으로 저장 실시
      }

    //http 요청 응답 코드 확인 실시
    responseCode = String.valueOf(conn.getResponseCode());
    log("http 응답 코드 : "+responseCode);
    log("http 응답 데이터 : "+sb.toString());
    
    
    try {
      Thread.sleep(15 * 1000);
      log("sleep done...");
    } catch (Exception e) {
      e.printStackTrace();
    }
    } catch (Exception e) {
      e.printStackTrace();
    } finally {
      //http 요청 및 응답 완료 후 BufferedReader를 닫아줍니다
      try {
        if (br != null) {
          br.close();
        }
      } catch (Exception e) {
        e.printStackTrace();
      }
    }
  }
  
  private static void log(String log){
    System.out.println("[INFO] " + log);
  }
}
```

<br><br>
# 3. References

https://bugs.openjdk.org/browse/JDK-8278067
