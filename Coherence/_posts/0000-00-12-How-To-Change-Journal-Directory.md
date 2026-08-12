---
date: 2025-04-30 23:47:17 +0900
layout: post
title: "[Coherence/Web] How To Change Journal Directory?"
tags: [Coherence, Web, Flashjournal]
typora-root-url: ../..
---

# 1. Overview

Coherence 12cR2 Flash Journal Directory 변경 방법

<br><br>


# 2. Descriptions

```xml
<coherence xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://xmlns.oracle.com/coherence/coherence-operational-config" xsi:schemaLocation="http://xmlns.oracle.com/coherence/coherence-operational-config.xsd">
  <cluster-config>
	
	...
	
  <journaling-config>
     <flashjournal-manager>
        <minimum-load-factor/>
        <maximum-value-size>32MB</maximum-value-size>
        <maximum-file-size>2GB</maximum-file-size>
        <collector-timeout>10m</collector-timeout>
        <maximum-size system-property="tangosol.coherence.flashjournal.size">30</maximum-size>
        <block-size>256KB</block-size>
        <async-limit>8MB</async-limit>
        <tmp-purge-delay>2h</tmp-purge-delay>
        <writer-timeout>8h</writer-timeout>
        <directory>/path/to/journal-temp-dir</directory>
     </flashjournal-manager>
   </journaling-config>
	
  </cluster-config>
</coherence>
```

<br>

위와 같이 tangosol operational override xml file 을 정의하여 사용한다.

또는 아래의 JVM Option으로도 변경 가능하다.

```sh
#COHERENCE_ARGS="${COHERENCE_ARGS} -Dcoherence.flashjournal.dir=/tmp/tmp"
```

<br>

XML syntax check 가 이루어지지 않기 때문에, XML에 정의 했지만 의도대로 동작하지 않을 때 유의해야 한다.


<br><br>


# 3. References

https://docs.oracle.com/en/middleware/fusion-middleware/coherence/12.2.1.4/develop-applications/operational-configuration-elements.html#GUID-F0BC1DD8-401F-4031-8B25-6D3AFD177C56

**journal file이 지정된 경로가 아닌, /tmp 에 저장됩니다. (Doc ID 3084067.1)**
