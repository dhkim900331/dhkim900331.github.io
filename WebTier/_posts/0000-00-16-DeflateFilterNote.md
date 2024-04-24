---
date: 2023-07-14 08:50:48 +0900
layout: post
title: "[WebTier/Apache] DeflateFilterNote"
tags: [WebTier, Apache, mod_deflate]
typora-root-url: ..
---

# 1. Overview

mod_deflate.so 모듈로 특정 확장자를 압축 하고, 해당 정보를 DeflateFilterNote 으로 AccessLog에 Logging 설정 할 수 있다.



# 2. Descriptions

```httpd.conf
LoadModule filter_module "${PRODUCT_HOME}/modules/mod_filter.so"
LoadModule deflate_module "${PRODUCT_HOME}/modules/mod_deflate.so"
<IfModule deflate_module>
   DeflateFilterNote Input instream
   DeflateFilterNote Output outstream
   DeflateFilterNote Ratio ratio

   AddOutputFilterByType DEFLATE text/html text/plain text/xml
</IfModule>


LogFormat "%h %l %u %t %E \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\" %f %{outstream}n/%{instream}n (%{ratio}n%%)" combined-deflate
LogFormat "%h %l %u %t %E \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"" combined
LogFormat "%h %l %u %t %E \"%r\" %>s %b" common

#CustomLog "||${PRODUCT_HOME}/bin/odl_rotatelogs ${ORACLE_INSTANCE}/servers/${COMPONENT_NAME}/logs/access_log 43200" common
CustomLog "||${PRODUCT_HOME}/bin/odl_rotatelogs ${ORACLE_INSTANCE}/servers/${COMPONENT_NAME}/logs/access_log 43200" combined-deflate
```



이와 같이 설정하면, (8kb html 파일 호출 시)

```
(8kb html 파일 호출 시)
"GET /index.html HTTP/1.1" 200 2386 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36" 2368/8893 (26%)
```



LogFormat에 %f 설정 시, 확장자만 나타낼 수는 없고, 파일 전체 경로가 출력된다.

```
"GET / HTTP/1.1" 200 2386 "-" "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36" /sw/webtier/12cR2/domains/base_domain/config/fmwconfig/components/OHS/instances/worker1/htdocs/index.html 2368/8893 (26%)
```





# 3. References

[2.2 Apache HTTP Server and Third-party Modules in Oracle HTTP Server](https://docs.oracle.com/middleware/1221/webtier/administer-ohs/under_mods.htm#HSADM1292)

[mod_deflate](https://httpd.apache.org/docs/2.2/ko/mod/mod_deflate.html)

[mod_filter](https://httpd.apache.org/docs/2.4/mod/mod_filter.html)
