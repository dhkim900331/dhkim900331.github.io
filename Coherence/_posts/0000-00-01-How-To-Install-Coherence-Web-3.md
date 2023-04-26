---
date: 2023-02-02 08:58:49 +0900
layout: post
title: "[Coherence/Web] How to Install Coherence Web 3.X"
tags: [Coherence, Web, Installation]
typora-root-url: ..
---

# 1. 개요

Coherence Web 3.X 설치를 다룬다.

이 버전은 WebLogic 11g 에 호환된다.



[공식 가이드](https://docs.oracle.com/cd/E18686_01/coh.37/e18690.pdf)



# 2. Download (Install)

Oracle Support의 Patches에서 Coherence를 다운로드 받는다.

`Patch 32973233: Coherence 3.7.1 Patch 22 (3.7.1.22) Full Distribution`



`/sw/coherence/3.7.1.22`와 같은 경로 안에 압축을 해제하여 구성한다.



# 3. Configurations

## 3.1 run.xml

```xml
<?xml version='1.0'?>
<coherence>
    <cluster-config>
        <member-identity>
            <cluster-name system-property="tangosol.coherence.cluster">MyCluster</cluster-name>
        </member-identity>
​
        <unicast-listener>
            <address system-property="tangosol.coherence.localhost">wls.local</address>
            <port system-property="tangosol.coherence.localport">10000<port>
            <port-auto-adjust system-property="tangosol.coherence.localport.adjust">true</port-auto-adjust>
        </unicast-listener>
    </cluster-config>
​
    <license-config>
        <edition-name systemproperty="tangosol.coherence.edition">GE</edition-name>
        <license-mode systemproperty="tangosol.coherence.mode">prod</license-mode>
    </license-config>
</coherence>
```



run.xml 구성 내용은 [\[Coherence 3.7] run.xml 설명\]](https://blog.naver.com/ks900331/221497889161) 을 참고한다.



## 3.2 session-cache-config.xml

```sh
$ jar -xvf coherence-web.jar session-cache-config.xml
 inflated: session-cache-config.xml
```



## 3.3 Shell Scripts

### 3.3.1 start

```sh
#!/bin/sh

export JAVA_HOME=/sw/jdk/jdk1.7.0_80
export COHERENCE_HOME=/sw/coherence/3.7.1.22
export JAVAEXEC=$JAVA_HOME/bin/java
export PREFIX=`date +"%Y%m%d_%H%M%S"`
export SERVER_NAME=CacheServer1
export CLASSPATH="${CLASSPATH}:$COHERENCE_HOME/lib/coherence.jar:$COHERENCE_HOME/lib/coherence-web.jar"

JAVA_OPTS="$JAVA_OPTS -Xms6144m -Xmx6144m"
JAVA_OPTS="$JAVA_OPTS -Dtangosol.coherence.override=${COHERENCE_HOME}/lib/run.xml"
JAVA_OPTS="$JAVA_OPTS -Dtangosol.coherence.cacheconfig=${COHERENCE_HOME}/lib/session-cache-config.xml"
JAVA_OPTS="$JAVA_OPTS -Dtangosol.coherence.session.localstorage=true"
JAVA_OPTS="$JAVA_OPTS -Dtangosol.coherence.localhost=wls.local"
JAVA_OPTS="$JAVA_OPTS -Dtangosol.coherence.localport=10000"
export JAVA_OPTS

mv ${LOG_DIR}/${SERVER_NAME}.out ${LOG_DIR}/backup/${SERVER_NAME}.out${PREFIX}

$JAVAEXEC -server -Dcoherence_${SERVER_NAME} -showversion $JAVA_OPTS -cp ${CLASSPATH} com.tangosol.net.DefaultCacheServer > ${LOG_DIR}/${SERVER_NAME}.out 2>&1 &

sleep 1
tail -f ${LOG_DIR}/${SERVER_NAME}.out
```



`tangosol.coherence.localhost`, `tangosol.coherence.localport` 옵션은 run.xml 에도 정의가 되어 있다.

Cache Server를 다중화 하는 경우, 각 Cache Server별로 다르게 설정하는 것을 run.xml이 아닌, 가장 우선순위가 높은 JVM Argument로 지정한다.

즉, Cache Server를 추가로 셋업하려면 위 옵션을 변경하면 된다.

그리고 run.xml 의 Well Known Address를 설정해야 한다. (참고: [\[Coherence 3.7] run.xml 설명\]](https://blog.naver.com/ks900331/221497889161))



### 3.3.2 stop

```sh
#! /bin/sh

export SERVER_NAME=CacheServer1
kill -9 `ps -ef | grep ${SERVER_NAME} | grep -v grep | awk '{print $2}'`
```



## 4. WebLogic

WebLogic 인스턴스에 Coherence 3.7 을 Setup하기 위한 설명이다.



## 4.1 coherence.jar

${COHERENCE_HOME}/coherence.jar를 lib 디렉토리에 복제한다.

```sh
$ cp ${COHERENCE_HOME}/lib/coherence.jar ${WEBLOGIC_DOMAIN_HOME}/lib/

$ ls -al /sw/weblogic/11g/domains/base_domain/lib/coherence.jar
-rw-r--r-- 1 wasadm wasadm 7452777 Jan 23 15:53 /sw/weblogic/11g/domains/base_domain/lib/coherence.jar
```



## 4.2 coherence-web-spi.war

${COHERENCE_HOME}/coherence-web-spi.war 파일은 Shared Library이다.

WLS Admin Console을 통해서 Library로 배포한다.



https://docs.oracle.com/cd/E24290_01/coh.371/e22620/cweb_wls.htm#CHDDHJHG



config.xml 에서는 ...

```xml
  <library>
    <name>coherence-web-spi#1.0.0.0@1.0.0.0</name>
    <target>M1,M2</target>
    <module-type>war</module-type>
    <source-path>${COHERENCE_HOME}/lib/coherence-web-spi.war</source-path>
    <security-dd-model>DDOnly</security-dd-model>
    <staging-mode>nostage</staging-mode>
  </library>
```



## 4.3 Instance Script

WLS 기동 스크립트에는...

```sh
export USER_MEM_ARGS="$USER_MEM_ARGS -Dtangosol.coherence.session.localstorage=false"
export USER_MEM_ARGS="$USER_MEM_ARGS -Dtangosol.coherence.distributed.localstorage=false"
export USER_MEM_ARGS="$USER_MEM_ARGS -Dtangosol.coherence.cacheconfig=${COHERENCE_HOME}/lib/session-cache-config.xml"
export USER_MEM_ARGS="$USER_MEM_ARGS -Dtangosol.coherence.override=${COHERENCE_HOME}/lib/run.xml"
```



Cache Server와 다르게, localstorage=false를 설정하였다.



## 4.4 Web Application

어플리케이션의 weblogic.xml 에 Shared Library를 선언한다.



```xml
<weblogic-web-app>
    <library-ref>
     <library-name>coherence-web-spi</library-name>
    </library-ref>
</weblogic-web-app>
```

