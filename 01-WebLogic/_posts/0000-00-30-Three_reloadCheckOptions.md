---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] servlet-reload-check-secs, resource-reload-check-secs, page-check-seconds"
tags: [WAS, WebLogic]
typora-root-url: ..
---


# 1. 개요

servlet-reload-check-secs, resource-reload-check-secs, page-check-seconds

# 2. 설명

* servlet-reload-check-secs: Servlet 변경
* resource-reload-check-secs: XML, image 등등 모든 일반 파일 재갱신
* page-check-seconds: jsp recompile



0 is 항상 변경 확인.

5 is 이전에 변경된 기록 => 5 일 경우 변경 확인.

-1 is 전혀 확인 하지 않음.



사용자의 요청이 들어왔을 때, 변경 확인.

즉, 0으로 설정 시 매번 변경을 확인한다는 뜻. (요청이 없을때는 0으로 설정해도 변경되지 않는다는 의미.)



```xml
<!-- weblogic.xml 파일의 내용 -->
<weblogic-web-app>
	<container-descriptor>
	   <servlet-reload-check-secs>1</servlet-reload-check-secs>
	   <resource-reload-check-secs>1</resource-reload-check-secs>
	</container-descriptor>
	<jsp-descriptor>
	   <page-check-seconds>1</page-check-seconds>
	</jsp-descriptor>
</weblogic-web-app>
```

