---
date: 2022-02-21 16:44:14 +0900
layout: post
title: "[WebLogic/Bash] config.xml 에서 정보 일괄 추출"
tags: [Middleware, WebLogic, Bash]
typora-root-url: ..
---

# 1. 개요

고객사 시스템 정보 추출을 위해 만든 스크립트
{{ site.content.br_big }}
# 2. 인스턴스 정보

## 2.1 인스턴스명

### (1). server tag 범위 검색

```bash
$ egrep "<server>|<\/server>" config.xml -n
44:  <server>
76:  </server>
77:  <server>
136:  </server>
137:  <server>
157:  </server>
158:  <server>
213:  </server>
```
{{ site.content.br_small }}

### (2). sed 명령으로 범위 출력

```bash
$ sed -n 44,76p config.xml
  <server>
    <name>AdminServer</name>
    <log>
      <date-format-pattern>yyyy. M. d a h'시' mm'분' ss,SSS'초' z</date-format-pattern>
      <file-name>logs/AdminServer.log</file-name>
      <rotation-type>byTime</rotation-type>
      <number-of-files-limited>true</number-of-files-limited>
      <file-count>100</file-count>
      <file-time-span>24</file-time-span>
      <rotation-time>00:00</rotation-time>
      <rotate-log-on-startup>false</rotate-log-on-startup>
      <buffer-size-kb>8</buffer-size-kb>
      <logger-severity>Info</logger-severity>
      <log-file-severity>Info</log-file-severity>
      <stdout-severity>Info</stdout-severity>
      <stdout-format>standard</stdout-format>
      <stdout-log-stack>true</stdout-log-stack>
      <stacktrace-depth>5</stacktrace-depth>
      <domain-log-broadcast-severity>Off</domain-log-broadcast-severity>
      <redirect-stdout-to-server-log-enabled>false</redirect-stdout-to-server-log-enabled>
      <redirect-stderr-to-server-log-enabled>false</redirect-stderr-to-server-log-enabled>
      <domain-log-broadcaster-buffer-size>10</domain-log-broadcaster-buffer-size>
      <log-monitoring-enabled>true</log-monitoring-enabled>
      <log-monitoring-interval-secs>30</log-monitoring-interval-secs>
      <log-monitoring-throttle-threshold>1500</log-monitoring-throttle-threshold>
      <log-monitoring-throttle-message-length>50</log-monitoring-throttle-message-length>
      <log-monitoring-max-throttle-message-signature-count>1000</log-monitoring-max-throttle-message-signature-count>
    </log>
    <listen-port>8001</listen-port>
    <listen-address>was.test.com</listen-address>
    <server-life-cycle-timeout-val>30</server-life-cycle-timeout-val>
    <startup-timeout>0</startup-timeout>
  </server>
```
{{ site.content.br_small }}

### (3).  인스턴스명은 범위의 항상 두번째에 이름을 갖는다.

```bash
$ sed -n 44,76p config.xml | sed -n -e 2p
    <name>AdminServer</name>
```
{{ site.content.br_small }}

### (4). 인스턴스명만 끄집어 내도록 name tag 걸러내기

```bash
$ sed -n 44,76p config.xml | sed -n -e 2p | sed -s "s/<name>//" | sed -s "s/<\/name>//"
    AdminServer
```
{{ site.content.br_small }}

## 2.2 인스턴스 주소

### (1). listen-address와 listen-port만 검색하면 된다.

```bash
$ sed -n 44,76p config.xml | egrep "listen-address|listen-port"
    <listen-port>8001</listen-port>
    <listen-address>was.test.com</listen-address>
```
{{ site.content.br_small }}

## 2.3 (통합) 서버 정보 출력하기

* "1. server tag 범위 검색" 에 head, tail 조합하여 검색 범위를 특정시킨다.

```bash
PAGE_RANGE=$(egrep "<server>|<\/server>" config.xml -n | cut -d ':' -f1)
PAGE_COUNT=$(echo "${PAGE_RANGE}" | wc -l)

for ((idx=1; idx<=PAGE_COUNT; idx=idx+2))
do
	HERE=$(echo "${PAGE_RANGE}" | head -n ${idx} | tail -1)
	NEXT=$(echo "${PAGE_RANGE}" | head -n $((idx+1)) | tail -1)
	
	INSTANCE_NAME=$(sed -n ${HERE},${NEXT}p config.xml | sed -n -e 2p | sed 's/ //g')
	INSTANCE_ADDR=$(sed -n ${HERE},${NEXT}p config.xml | egrep "listen-address|listen-port" | sed 's/ //g')
	
	echo "
	########## start ##########"
	echo "인스턴스 : ${INSTANCE_NAME}"
	echo "주소 : ${INSTANCE_ADDR}"
	echo "########## end ##########
	"
done
```

![Get-Config-Bash_1](/../assets/posts/images/WebLogic/Get-Config-Bash/Get-Config-Bash_1.png)

# 3. 배포 App 정보

## 3.1 App 이름

### (1). app-deployment tag 범위 검색

```bash
$ egrep "<app-deployment>|<\/app-deployment>" config.xml -n
237:  <app-deployment>
246:  </app-deployment>
247:  <app-deployment>
256:  </app-deployment>
```
{{ site.content.br_small }}

### (2). sed 명령으로 범위 출력

```bash
$ sed -n 237,246p config.xml
  <app-deployment>
    <name>webapp</name>
    <target>myCluster_1</target>
    <module-type>war</module-type>
    <source-path>/usr/ssw/Applications/webapp</source-path>
    <security-dd-model>DDOnly</security-dd-model>
    <staging-mode>nostage</staging-mode>
    <plan-staging-mode>nostage</plan-staging-mode>
    <cache-in-app-directory>false</cache-in-app-directory>
  </app-deployment>
```
{{ site.content.br_small }}

### (3). 어플리케이션명은 범위의 항상 두번째에 이름을 갖는다.

```bash
$ sed -n 237,246p config.xml | sed -n -e 2p
    <name>webapp</name>
```
{{ site.content.br_small }}

## 3.2 App 배포 Target

```bash
$ sed -n 237,246p config.xml | grep "target"
    <target>myCluster_1</target>
```
{{ site.content.br_small }}

## 3.3 App Source Path

```bash
$ sed -n 237,246p config.xml | grep "source-path"
    <source-path>/usr/ssw/Applications/webapp</source-path>
```
{{ site.content.br_small }}

## 3.4 (통합) App 정보 출력하기

```bash
PAGE_RANGE=$(egrep "<app-deployment>|<\/app-deployment>" config.xml -n | cut -d ':' -f1)
PAGE_COUNT=$(echo "${PAGE_RANGE}" | wc -l)

for ((idx=1; idx<=PAGE_COUNT; idx=idx+2))
do
	HERE=$(echo "${PAGE_RANGE}" | head -n ${idx} | tail -1)
	NEXT=$(echo "${PAGE_RANGE}" | head -n $((idx+1)) | tail -1)
	
	APPLICATION_NAME=$(sed -n ${HERE},${NEXT}p config.xml | sed -n -e 2p | sed 's/ //g')
	APPLICATION_TARGET=$(sed -n ${HERE},${NEXT}p config.xml | grep "target" | sed 's/ //g')
	APPLICATION_PATH=$(sed -n ${HERE},${NEXT}p config.xml | grep "source-path" | sed 's/ //g')
	
	if [ "${APPLICATION_TARGET}" == "<target></target>" ]; then
		continue;
	fi
	
	echo "
	########## start ##########"
	echo "어플리케이션명 : ${APPLICATION_NAME}"
	echo "타겟정보 : ${APPLICATION_TARGET}"
	echo "소스위치 : ${APPLICATION_PATH}"
	echo "########## end ##########
	"
done
```

![Get-Config-Bash_2](/../assets/posts/images/WebLogic/Get-Config-Bash/Get-Config-Bash_2.png)

# 4. Datasource 정보

## 4.1 Datasource 이름

### (1). jdbc-system-resource tag 범위 검색

```bash
$ egrep "<jdbc-system-resource>|<\/jdbc-system-resource>" config.xml -n
270:  <jdbc-system-resource>
274:  </jdbc-system-resource>
275:  <jdbc-system-resource>
279:  </jdbc-system-resource>
```
{{ site.content.br_small }}

### (2). sed 명령으로 범위 출력

```bash
$ sed -n 270,274p config.xml
  <jdbc-system-resource>
    <name>myDataSource_1</name>
    <target>M1,myManaged_1</target>
    <descriptor-file-name>jdbc/myDataSource_1-2365-jdbc.xml</descriptor-file-name>
  </jdbc-system-resource>
```
{{ site.content.br_small }}

### (3). 데이터소스명은 범위의 항상 두번째에 이름을 갖는다.

```bash
$ sed -n 270,274p config.xml | sed -n -e 2p
    <name>myDataSource_1</name>
```
{{ site.content.br_small }}

## 4.2 Datasource 배포 Target

```bash
$ sed -n 270,274p config.xml | grep "target"
    <target>M1,myManaged_1</target>
```
{{ site.content.br_small }}

## 4.3 데이터소스 JDBC xml 파일명 출력

```bash
$ sed -n 270,274p config.xml | grep "descriptor-file-name"
    <descriptor-file-name>jdbc/myDataSource_1-2365-jdbc.xml</descriptor-file-name>
```
{{ site.content.br_small }}

## 4.4 (통합) Datasource 정보 출력하기

* XML 파일 안의 USERNAME, URL STRING, JNDI 정보 출력

```bash
PAGE_RANGE=$(egrep "<jdbc-system-resource>|<\/jdbc-system-resource>" config.xml -n | cut -d ':' -f1)
PAGE_COUNT=$(echo "${PAGE_RANGE}" | wc -l)

for ((idx=1; idx<=PAGE_COUNT; idx=idx+2))
do
	HERE=$(echo "${PAGE_RANGE}" | head -n ${idx} | tail -1)
	NEXT=$(echo "${PAGE_RANGE}" | head -n $((idx+1)) | tail -1)
	
	DATASOURCE_NAME=$(sed -n ${HERE},${NEXT}p config.xml | sed -n -e 2p | sed 's/ //g')
	DATASOURCE_TARGET=$(sed -n ${HERE},${NEXT}p config.xml | grep "target" | sed 's/ //g')
	DATASOURCE_XML=$(sed -n ${HERE},${NEXT}p config.xml | grep "descriptor-file-name" | sed 's/ //g')
	
	# XML 파일명만 출력
	DATASOURCE_XML_REAL=$(echo ${DATASOURCE_XML} | cut -d '>' -f2 | cut -d '<' -f1)
	
	# USER 명은 <name>user</name> TAG 아래에 있다.
	DATASOURCE_XML_USERNAME_LINE=$(cat ${DATASOURCE_XML_REAL} | grep "<name>user<\/name>" -n | cut -d ':' -f1)
	DATASOURCE_XML_USERNAME=$(cat ${DATASOURCE_XML_REAL} | sed -n -e $((DATASOURCE_XML_USERNAME_LINE+1))p | sed 's/ //g')
	
	# URL STRING
	DATASOURCE_XML_URL=$(cat ${DATASOURCE_XML_REAL} | grep "<url>" | sed 's/ //g')
	
	# JNDI
	DATASOURCE_XML_JNDI=$(cat ${DATASOURCE_XML_REAL} | grep "<jndi-name>" | sed 's/ //g')
	
	echo "
	########## start ##########"
	echo "데이터소스명 : ${DATASOURCE_NAME}"
	echo "타겟정보 : ${DATASOURCE_TARGET}"
	echo "XML : ${DATASOURCE_XML}"
	
	echo "
	-------"
	echo "USER : ${DATASOURCE_XML_USERNAME}"
	echo "URL : ${DATASOURCE_XML_URL}"
	echo "JNDI : ${DATASOURCE_XML_JNDI}"
	echo "-------"
	
	echo "########## end ##########
	"
done
```

![Get-Config-Bash_3](/../assets/posts/images/WebLogic/Get-Config-Bash/Get-Config-Bash_3.png)

