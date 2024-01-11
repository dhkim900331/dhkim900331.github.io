---
date: 2022-08-18 17:18:20 +0900
layout: post
title: "[Linux/Log Rotation] Log Rotation"
tags: [OS, Linux, Logrotate, Null, Copy]
typora-root-url: ..
---

# 1. 개요

Log 파일의 관리를 위해 Rotation 방법을 알아 보자.



# 2. Null Copy

유닉스 계열에서 별다른 Tools 없이 사용 가능한 방법이다.

과거에 어디선가 null copy 시에 프로세스가 해당 파일의 원본을 계속 물고 있어, 해당 프로세스를 재기동 하기 전까지 file size가 release 되지 않았던 기억이 있지만, 버그일 것이다.



crontab 에 등록 하면 된다.

```sh
# (min:0~59) (hour:0~23) (day:0~31) (month:1~12) (day of the week:0/7-sunday ~ 6-saturday)
0 5 * * * /usr/bin/cp catalina.out catalina.out.$(/usr/bin/date +%Y%m%d_%H%M%S) && /usr/bin/cat /dev/null > catalina.out
```





# 3. logrotate

logrotate 설치가 되어 있어야 한다.



Tomcat WAS를 예시로 설정 하였으며, logrotate_tomcat9.conf 파일을 생성한다.

```
/opt/ssw/tomcat9/logs/catalina.out {
   rotate 90
   create 600 dhkim dhkim
   dateext
   daily
   compress
   missingok
   notifempty
   copytruncate
}
```

> 주요 옵션 : 매일 압축 보관 및 최대 90개 보관, 압축 보관한 파일명 뒤에 date



crontab 에 등록 하면 된다.

```sh
# (min:0~59) (hour:0~23) (day:0~31) (month:1~12) (day of the week:0/7-sunday ~ 6-saturday)
0 5 * * * /usr/sbin/logrotate -f /opt/ssw/tomcat9/logs/logrotate_tomcat9.conf
```



crontab 에 등록하지 않고 검증하려면 그냥 실행하면 된다. Just Do It!

```sh
/usr/sbin/logrotate -f /opt/ssw/tomcat9/logs/logrotate_tomcat9.conf
```



**crontab에 등록하지 않고, /etc/logrotate.d 에 넣어두기만 해도, 매일 logroate daemon 이 처리한다.**
