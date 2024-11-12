---
date: 2024-10-08 16:44:22 +0900
layout: post
title: "[Coherence] Creating and Deploying App with WebLogic"
tags: [Coherence, Creating, Deploying, App, GAR]
typora-root-url: ..
---

# 1. Overview
Coherence 14c 에서 App을 생성하고 배포하는 내용에 대해 설명한다.
공식 문서만을 기준으로 정리하였으며, 설명하는 순서가 공식 문서의 목차 순서와 다를 수 있다.

<br><br>


# 2. Descriptions

## 2.1 Creating First App
[Building Your First Coherence Application](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/develop-applications/building-your-first-coherence-application.html#GUID-B5575517-C6B7-46BF-9188-2E3903C7862A)에서 가장 심플한 Coherence App을 만들 수 있다.


<br><br>


### 2.1.1 Basic Coherence Standalone Application
해당 과정은 "2.1.2 Basic Coherence JavaEE Web Application"의 방법과 거의 동일하다.

<br><br>


### 2.1.2 Basic Coherence JavaEE Web Application
해당 과정은, JavaEE Module로 Container 등에 배포하는 것이고, WebLogic Server에는 권장되지 않는다고 설명한다.

>  "The instructions in this section are not specific to, or recommended for, WebLogic Server."

<br>

이 Post의 Deploying... Sections 에서도 언급하겠지만, WebLogic Server에는 이미 Coherence가 Integrated 되어 있기 때문이다.

그러나 그것을 제외하면, WAR/EAR 단위의 Coherence Application 배포는 가장 이상적인 구조이다.

JVM의 Life cycle에 영향을 받지 않기도 하고, 즉시 변경사항을 Update 할 수 있기 때문이다.


<br><br>


#### (1) Creating WAR
WAR 단위의 Coherence App은 가장 많은 Resource를 사용하는 구조가 될 수 있다.

<br>

FirstWAR 의 구조

```
/sw/app/FirstWAR
├── index.jsp
└── WEB-INF
    ├── classes
    │          ├── example-config.xml
    │          └── tangosol-coherence-override.xml
    ├── weblogic.xml
    └── web.xml

2 directories, 5 files
```

<br>

Cache 서비스를 호출하는 index.jsp

```jsp
<html>
   <head>
      <title>My First Coherence Cache</title>
   </head>
   <body>
      <h1>
               <%@ page language="java"
                        import="com.tangosol.net.CoherenceSession,
                                com.tangosol.net.NamedCache,
                                com.tangosol.net.Session"
               %>
               <%
                  String key = "k2";
                  String value = "Hello World!";

                  Session coh_session = new CoherenceSession();
                  NamedCache <Object, Object> cache = coh_session.getCache("hello-example");

                  cache.put(key, value);
                  out.println((String)cache.get(key));
                  coh_session.close();

               %>
      </h1>
   </body>
</html>
```

<br>

Cache 정의를 위한 example-config.xml

```xml
<?xml version="1.0"?>

<cache-config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xmlns="http://xmlns.oracle.com/coherence/coherence-cache-config"
   xsi:schemaLocation="http://xmlns.oracle.com/coherence/coherence-cache-config
   coherence-cache-config.xsd">
   <caching-scheme-mapping>
      <cache-mapping>
         <cache-name>hello-example</cache-name>
         <scheme-name>distributed</scheme-name>
      </cache-mapping>
   </caching-scheme-mapping>

   <caching-schemes>
      <distributed-scheme>
         <scheme-name>distributed</scheme-name>
         <service-name>DistributedCache</service-name>
         <local-storage system-property="coherence.session.localstorage">true</local-storage>
         <backing-map-scheme>
            <local-scheme/>
         </backing-map-scheme>
         <autostart>true</autostart>
      </distributed-scheme>
   </caching-schemes>
</cache-config>
```

<br>

Coherence Cluster member 정의를 위한 tangosol-coherence-override.xml 에서는 아래가 필수로 포함되어야 한다.

```xml
 ... skip ...
   <configurable-cache-factory-config>
      <init-params>
         <init-param>
            <param-type>java.lang.String</param-type>
            <param-value system-property="coherence.cacheconfig">
               example-config.xml</param-value>
         </init-param>
      </init-params>
   </configurable-cache-factory-config>
</coherence>
```


> lib에 coherence-metrics.jar는 Server Starts with Info "com.tangosol.coherence.metrics.internal.DefaultMetricRegistry$Adapter not found" (Doc ID 2703637.1) 로 인해 넣은것이고,
>
> coherence-mock.jar 또한 관련 Exception이 발생을 하기에 넣은 것이다.


<br><br>


#### (2) Creating EAR
EAR 단위의 Coherence App은 WAR 보다는 더 적은 Resource를 사용한다.

EAR 단위의 ClassLoader에 Singleton으로 생성된 Coherence Cluster 1개가 생성되고, 하위 WAR가 모두 이 Cluster를 공유한다.

<br>

FirstEAR 의 구조

```
/sw/app/FirstEAR
├── APP-INF
│          └── classes
│              ├── example-config.xml
│              └── tangosol-coherence-override.xml
├── FirstWAR.war
└── META-INF
    ├── application.xml
    └── weblogic-application.xml

3 directories, 5 files
```

<br>

EAR format으로 Coherence를 배포하기 위해서는,

[Packaging Shared Utility Classes](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wlprg/classloading.html#GUID-63E6C6F0-1F21-4281-AA0B-06330E2DBDC4)에서 설명처럼

EAR 하위 WAR 들이 공통으로 사용할 Coherence Libraries/Resources를 APP-INF/lib 또는 classes 에 배치해야 한다.

<br>

그러므로, "(1) Creating WAR" 과 조금 배치가 다른 점이 있다.

FirstWAR.war 에 있던 example-config.xml, tangosol-coherence-override.xml이 EAR의 상위 레벨로 포함되기 위해 APP-INF/classes 에 배치 된다.

EAR에 포함된 FirstWAR.war는 "(1) Creating WAR" 에서 생성한 index.jsp만 유지하고 Coherence 관련된 항목은 모두 제거되었다.

FirstWAR.war는 Coherence와 종속성이 전혀 없다.

<br>

즉, FirstWAR에 포함된 요소는 다음과 같다.

```
index.jsp
WEB-INF/web.xml
WEB-INF/weblogic.xml
```

<br>

META-INF/application.xml

```xml
<application>
   <display-name>FirstEAR</display-name>
   <module>
      <web>
         <web-uri>FirstWAR.war</web-uri>
         <context-root>/FirstWAR</context-root>
      </web>
   </module>
</application>
```

<br>

META-INF/weblogic-application.xml

```xml
<?xml version="1.0"?>
<weblogic-application xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xsi:schemaLocation="http://xmlns.oracle.com/weblogic/weblogic-application
   http://xmlns.oracle.com/weblogic/weblogic-application/1.6/
   weblogic-application.xsd"
   xmlns="http://xmlns.oracle.com/weblogic/weblogic-application">
</weblogic-application>
```


<br><br>

<br>

#### (3) Creating GAR

GAR(Grid ARchive)는 Coherence 의 cache 구성 요소(pof, cache-config)를 포함할 수 있는 Application 형태다.

[Packaging Coherence Applications for WebLogic Server](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/administer/deploying-coherence-applications.html#GUID-2E9D8A7C-F2FC-42EC-845A-A8CD28F4CF4D)의 설명에서,

Cache Config file을 포함하는 GAR을 만들고,

Java EE Module인 EAR에 GAR을 포함하는 과정을 안내한다.

<br>

FirstGAR 의 구조 (아래에서 FirstGAR.gar로 Packaging하여 사용한다.)

```sh
$ tree /sw/app/FirstGAR
/sw/app/FirstGAR
└── META-INF
    ├── coherence-application.xml
    └── example-config.xml

1 directory, 2 files
```

<br>

coherence-application.xml 에서 현재 pof 는 구성하지 않으니 주석 처리 된다.

```xml
<?xml version="1.0"?>
<coherence-application xmlns="http://xmnls.oracle.com/coherence/coherence-application">
   <cache-configuration-ref>META-INF/example-config.xml</cache-configuration-ref>
   <!--<pof-configuration-ref>META-INF/pof-config.xml</pof-configuration-ref>-->
</coherence-application>
```

<br>

FirstEARwithGAR 의 구조

```
/sw/app/FirstEARwithGAR
├── APP-INF
│          └── classes
│              └── tangosol-coherence-override.xml
├── FirstGAR.gar
├── FirstWAR.war
└── META-INF
    ├── application.xml
    └── weblogic-application.xml

3 directories, 5 files
```

<br>

"(2) Creating EAR" 과 조금 배치가 다른 점이 있다.

APP-INF/classes/example-config.xml이 FirstGAR.gar에 포함된 것이고,

GAR에서 example-config.xml을 Loading하므로 tangosol-coherence-override.xml의 하단 부분은 주석/삭제 된다.

```xml
 ... skip ...
<!--
   <configurable-cache-factory-config>
      <init-params>
         <init-param>
            <param-type>java.lang.String</param-type>
            <param-value system-property="coherence.cacheconfig">
               example-config.xml</param-value>
         </init-param>
      </init-params>
   </configurable-cache-factory-config>
-->
</coherence>
```


<br><br>


## 2.2 Deploying First App

여기 Section에서는 Reminder 목적으로 수집된 여러 자료들을 나열하기 때문에,

공식 문서상 안내하는 순서와 다를 수 있다.

<br>

"2.1 Creating First App" 에서는 WAR/EAR/GAR 형식으로 Coherence Application을 구성하는 방법을 설명했다.

Applications을 Weblogic에 배포해보면, 특별히 Application에 Coherence 관련 JAR Libraries가 없음에도 문제 없이 진행된다.

이는 [Overview of the WebLogic Server Coherence Integration](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/administer/deploying-coherence-applications.html#GUID-69C5C7E2-1F70-47FD-A127-73679DE3ADC0)에서 설명하고 있다.

이미 WebLogic에는 Coherence가 Integrated 되어 있기 때문에, 상위 ClassLoader에 Coherence Libraries가 Loading 된다.

<br>

설명 보충을 위해, 다음의 WebLogic Log의 일부분은 FirstEARwithGAR을 배포할 시

WebLogic에 이미 포함되어 있는 Coherence Libraries/Resources등이 호출되는 것을 보여 준다.

`/sw/weblogic/14c/coherence/lib/coherence.jar`가 그렇다.

`tangosol-coherence-override.xml`는 App에서 읽어지고 있다.

```
<Info> <Deployer> <BEA-149059> <Module FirstGAR.gar of application FirstEARwithGAR is transitioning from STATE_NEW to STATE_PREPARED on server M1.>
<Info> (thread=[STANDBY] ExecuteThread: '1' for queue: 'weblogic.kernel.Default (self-tuning)', member=n/a): Loaded operational configuration from "jar:file:/sw/weblogic/14c/coherence/lib/coherence.jar!/tangosol-coherence.xml"
<Info> (thread=[STANDBY] ExecuteThread: '1' for queue: 'weblogic.kernel.Default (self-tuning)', member=n/a): Loaded operational overrides from "jar:file:/sw/weblogic/14c/coherence/lib/coherence.jar!/tangosol-coherence-override-dev.xml"
<Info> (thread=[STANDBY] ExecuteThread: '1' for queue: 'weblogic.kernel.Default (self-tuning)', member=n/a): Loaded operational overrides from "file:/sw/app/FirstEARwithGAR/APP-INF/classes/tangosol-coherence-override.xml"
<Info> (thread=[STANDBY] ExecuteThread: '1' for queue: 'weblogic.kernel.Default (self-tuning)', member=n/a): Optional configuration override "cache-factory-config.xml" is not specified
<Info> (thread=[STANDBY] ExecuteThread: '1' for queue: 'weblogic.kernel.Default (self-tuning)', member=n/a): Optional configuration override "cache-factory-builder-config.xml" is not specified
<Info> (thread=[STANDBY] ExecuteThread: '1' for queue: 'weblogic.kernel.Default (self-tuning)', member=n/a): Optional configuration override "/custom-mbeans.xml" is not specified

Oracle Coherence Version 14.1.1.0.0 Build 77467
 Grid Edition: Development mode
Copyright (c) 2000, 2020, Oracle and/or its affiliates. All rights reserved.

... skip ...

<Info> (thread=DistributedCache:FirstGAR:DistributedCache, member=1): This member has become the distribution coordinator for MemberSet(Size=1
  Member(Id=1, Timestamp=2024-09-09 15:43:42.143, Address=10.65.39.5:9000, MachineId=7674, Location=site:site_base_domain,rack:rack_base_domain,machine:machine_base_domain,process:process_base_domain,member:member_base_domain, Role=CoherenceServer)
  )
```

<br>

[Deploying Coherence Applications to an Application Server (Generic)](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/administer/deploying-coherence-applications.html#GUID-6BE3BCEA-A053-4C0C-810B-A310BB4DF95A)에서는,

Coherence Cluster members는 ClassLoader scope를 가지고 있다. 

앞서 설명한 WAR/EAR/GAR의 구성을 되짚어 보면, 분리 구성하였기 때문에 각 App이 갖는 ClassLoader당 Coherence Member가 될 수 있었다.

<br>

이어서, Docs에서는 WebLogic Server Platform이 아닌 환경에서 사용될 수 있는 배포 옵션 두 가지를 설명하고 있다.

 - Application Server의 Library로 Coherence를 배포
 - 또는 JavaEE Module로 Coherence를 배포

<br>

[Building Your First Coherence Application](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/develop-applications/building-your-first-coherence-application.html#GUID-B5575517-C6B7-46BF-9188-2E3903C7862A)에서는

WebLogic Server Platform이 아닌 Application Server에 배포할 목적으로 Coherence Application을 개발하는 지침을 안내하고 있다.
{{ site.content.br_small }}
특히 [Task 4: Create and Run a Basic Coherence JavaEE Web Application](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/develop-applications/building-your-first-coherence-application.html#GUID-4FBE9413-CDFA-433D-B852-3DC186E11B48)에서 다음처럼 Note가 포함된다.

>  "...The instructions in this section are not specific to, or recommended for, WebLogic Server."

<br>

그럼에도, WebLogic Server에 배포되는 App에 Coherence Libraries를 포함하려면

[Loading Coherence From the Application Classloader](https://docs.oracle.com/en/middleware/standalone/weblogic-server/14.1.1.0/wlcoh/deploy-wls-coherence.html#GUID-AF4DAB4F-DA19-4D02-A7A9-60BC1D68D33F)을 참고한다.

권장되지 않는 사용 사례이다.

이미 눈치 챘겠지만, 여러번 설명했듯이 Coherence가 Integrated 되어 있기 때문에 부모 ClassLoader에서 Coherence 관련 JARs, Resources를 호출하지 않기 위함이다.


<br><br>


# 3. and so on
다룬 사례들은 모두 Coherence Named Cache인데,

Coherence*Web HTTP Session 사용 사례를 다루기 위해서는 조금 더 연구가 필요해 보인다.

WebLogic Server에 배포되는 App의 weblogic.xml 에는 "<persistent-store-type>coherence-web</persistent-store-type>" 선언을 통해 Integrated 된 Coherence를 가볍게 다루도록 되어 있다.

이러한 방법을, WebLogic Server Platform이 아닌 다른 Application Server에 배포되는 Coherence Application에서는 어떻게 구현할 수 있는지에 대한 것 말이다.


<br><br>


# 4. References
Run Multiple Coherence Clusters on the Same Machine (Doc ID 883078.1)
Server Starts with Info "com.tangosol.coherence.metrics.internal.DefaultMetricRegistry$Adapter not found" (Doc ID 2703637.1)

