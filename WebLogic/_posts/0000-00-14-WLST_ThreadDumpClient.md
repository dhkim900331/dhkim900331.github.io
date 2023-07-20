---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] WLST으로 Thread Dump Client 만들기"
tags: [Middleware, WebLogic, Thread, Dump, WLST]
typora-root-url: ..
---


# 1. 개요

WLST으로 Thread Dump Client 만들기



# 2. Tool 개발

## 2.1 wlfullclient.jar

[여기]({{ site.url }}/weblogic/fullclient_jar) 참고하여 wlfullclient.jar 준비



위 jar 외에도 수많은 라이브러리를 classpath 로 잡아야 하나, 어떤것이 특정적으로 필요한지 몰라서 아래와 같이 모든 라이브러리를 사용했다.



```
weblogic.jar
wlfullclient.jar
jython-modules.jar
com.oracle.cie.wizard_7.1.0.0.jar
com.oracle.cie.config_8.1.0.0.jar
com.oracle.cie.comdev_7.1.0.0.jar
com.oracle.cie.config-wls_8.1.0.0.jar
com.oracle.cie.encryption_2.1.0.0.jar
com.oracle.cie.dependency_1.1.0.0.jar
com.oracle.cie.service-table_1.1.0.0.jar
com.oracle.cie.config-owsm_8.1.0.0.jar
com.oracle.cie.config-security_8.1.0.0.jar
com.oracle.core.weblogic.msgcat_3.0.0.0.jar
com.bea.core.xml.xmlbeans_1.0.0.0_2-6-0.jar
com.oracle.cie.config-wls-schema_12.1.3.0.jar
```



## 2.2 autoThreadDump_wlst.cmd

```bash
@echo off
set LIBPATH=<위 라이브러리가 있는 경로>
set CLASSPATH=%LIBPATH%\weblogic.jar
set CLASSPATH=%CLASSPATH%;%LIBPATH%\wlfullclient.jar
... skip ...
set CLASSPATH=%CLASSPATH%;%LIBPATH%\com.oracle.cie.config-wls-schema_12.1.3.0.jar

set LOG_DIR=<스레드 덤프를 남길 로그 디렉토리 경로>
set RUN_DIR=<autoThreadDump.cmd 가 위치하는 디렉토리 경로>
set JAVA_HOME=
set INSTANCE_NAME=%1
set ADDR=t3://%2:%3
set USERNAME=<웹로직 콘솔 아이디>
set PASSWORD=<웹로직 콘솔 패스워드>

set PREFIX=%DATE:~2%_%TIME:~0,-3%
set PREFIX=%PREFIX::=%
set PREFIX=%PREFIX:-=%
set PREFIX=%PREFIX: =0%
set PREFIX=%PREFIX:/=%

set THREAD_DUMP_FILENAME=%LOG_DIR%\%INSTANCE_NAME%_%PREFIX%

start /B %JAVA_HOME%\bin\java.exe -cp %CLASSPATH% weblogic.WLST RUN_DIR%\autoThreadDump_wlst.py %ADDR% %USERNAME% %PASSWORD% %THREAD_DUMP_FILENAME%

rem 아래 필요없는 Exception log가 생기는 것을 다시 지워준다.
del %LOG_DIR%\cfgfwk_*.log
```

> 모든 파일앞에는 절대 경로 또는 상대경로가 반드시 들어가야 한다.



## 2.3 autoThreadDump_wlst.py

```python
connect(sys.argv[2], sys.argv[3], sys.argv[1])
threadDump(writeToFile='true', fileName=sys.argv[2]+"_1.txt")

import time
time.sleep(5)
threadDump(writeToFile='true', fileName=sys.argv[2]+"_2.txt")
time.sleep(5)
threadDump(writeToFile='true', fileName=sys.argv[2]+"_3.txt")
```

> 5초 간격으로 3번의 덤프를 생성한다.



# 3. 실행

실행 방법에는 두가지가 있을 수 있다.

하나는, 직접 테스트용으로 실행.

두번째는,  다른 자바 프로그램에 코드로 삽입하여 자동화 방식(?) 등..



### 3.1 직접 실행

```
autoThreadDump_wlst.cmd AdminServer 192.168.56.2 8001
```

> AdminServer_<년월일시분초>_1.txt ~ 3.txt 파일이 생성된다.



### 3.2 자바 코드에 심기

#### (1). autoThreadDump() 메서드 생성

```java
private void autoThreadDump(String cmd, String instanceName, String ip, String port) throws IOException, InterruptedException {
	Runtime rt = Runtime.getRuntime();
	Process pc = null;
	String command = null;
	command = cmd + " ";
	command += instanceName + " ";
	command += ip + " ";
	command += port;
	
	try {
		pc = rt.exec(command);
	} catch (IOException e) {
		e.printStackTrace();
	} finnaly {
		pc.getErrorStream().close();
		pc.getInputStream().close();
		pc.getOutputStream().close();
		pc.waitFor();
	}
}
```



#### (2). 메서드 호출

```java
try {
	autoThreadDump("<경로>\\autoThreadDump_wlst.cmd", "AdminServer", "192.168.56.2", "8001");
} catch (Exception e) {
	e.printStackTrace();
}
```

