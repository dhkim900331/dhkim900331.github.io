---
date: 2024-06-25 16:09:26 +0900
layout: post
title: "[Coherence/Data Grid] How to install Coherence Data Grid 14c?"
tags: [Coherence, Data, Grid]
typora-root-url: ..
---

# 1. Overview
Coherence Data grid 설치 및 기본적인 사용 방법을 설명한다.

{{ site.content.br_small }}


# 2. Descriptions
## 2.1 Data Grid

기본적으로 Coherence Web 과 크게 다르지 않기 때문에, [How-to-install-Coherence-Web-14c]({{ site.url }}/coherence/How-to-install-Coherence-Web-14c) 을 참고하여 설치한다.



[3.2 Cache Configuration]({{ site.url }}/coherence/How-to-install-Coherence-Web-14c#h-32-cache-configuration) 에서 추출하여 사용하는 *session-cache-config.xml 은 필요치 않고, 다음의 Data grid cache config 파일을 사용한다.

```sh
cat << EOF > grid-cache-config.xml
<?xml version="1.0"?>

<cache-config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
   xmlns="http://xmlns.oracle.com/coherence/coherence-cache-config"
   xsi:schemaLocation="http://xmlns.oracle.com/coherence/coherence-cache-config
   coherence-cache-config.xsd">
   <caching-scheme-mapping>
      <cache-mapping>
         <cache-name>*</cache-name>
         <scheme-name>distributed</scheme-name>
      </cache-mapping>
   </caching-scheme-mapping>

   <caching-schemes>
      <distributed-scheme>
         <scheme-name>distributed</scheme-name>
         <backing-map-scheme>
            <local-scheme/>
         </backing-map-scheme>
         <autostart>true</autostart>
      </distributed-scheme>
   </caching-schemes>
</cache-config>
EOF
```

> [autostart](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.2206//develop-applications/configuring-caches.html#GUID-5035C967-54E0-480E-8B57-B0EECF241C2D) : false 일 경우, Cache service 가 시작되지 않아 Coherence clustering 또한 시작되지 않는다.



Cache Server/Client(WLS 또는 CacheFactory 를 모두 포함하여) 는 다음의 환경변수를 사용한다.

```sh
COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.mode=prod"
COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.cacheconfig=grid-cache-config.xml"
COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.override=tangosol-coherence-${DOMAIN_NAME}.xml"
COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.session.localstorage=true"
COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.management.remote=true"
export COHERENCE_ARGS

CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib"
CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib/coherence.jar"
export CLASSPATH
```

> localstorage 는 상황에 맞게 변경한다.



[How-to-install-Coherence-Web-14c]({{ site.url }}/coherence/How-to-install-Coherence-Web-14c)을 토대로 구성하되, `grid-cache-config.xml` 만 교체하여 사용하면 된다.





## 2.2 CacheFactory

CacheFactory API를 사용하는 `${ORACLE_HOME}/bin/coherence.sh` 을 사용시에는 다음과 같이 한다.

```sh
COHERENCE_HOME=/sw/coherence/14c/coherence
DOMAIN_HOME=/sw/coherence/14c/domains/base_domain
DOMAIN_NAME=base_domain
JAVA_HOME=/sw/jdk/jdk1.8.0_381

COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.mode=prod"
COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.cacheconfig=grid-cache-config.xml"
COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.override=tangosol-coherence-${DOMAIN_NAME}.xml"
COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.session.localstorage=false"
COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.management.remote=true"
export COHERENCE_ARGS

CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib"
CLASSPATH="${CLASSPATH}:${DOMAIN_HOME}/lib/coherence.jar"
export CLASSPATH

JAVA_OPTS="-server -showversion -Xms128m -Xmx128m -cp ${CLASSPATH} ${COHERENCE_ARGS}"
export JAVA_OPTS

${JAVA_HOME}/bin/java ${JAVA_OPTS} com.tangosol.net.CacheFactory
```



CacheFactory Client는 Clustering에 가입하여 Cache를 조회하는데 사용하는 간단한 준비된 Application이다.

[Using the Legacy CacheFactory Client](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.2206//develop-applications/starting-and-stopping-cluster-members.html#GUID-ABB02255-7BDD-4E0E-A5B4-6A8E119BEB1F) 참고





# 3. References

[Running Coherence for the First Time](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.2206/install/installing-oracle-coherence-java.html#GUID-453BF180-CBC5-4932-A947-1E1F4394F6C2)

[Using Coherence Query Language](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.0/develop-applications/using-coherence-query-language.html#GUID-C0D082B1-FA62-4899-A043-4345156E6641) 

[Using the Legacy CacheFactory Client](https://docs.oracle.com/en/middleware/standalone/coherence/14.1.1.2206//develop-applications/starting-and-stopping-cluster-members.html#GUID-ABB02255-7BDD-4E0E-A5B4-6A8E119BEB1F) 
