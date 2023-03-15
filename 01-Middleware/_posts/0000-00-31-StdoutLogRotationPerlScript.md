---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[Middleware/WebLogic] Stdout Log Rotation (perl script)"
tags: [Middleware, WebLogic]
typora-root-url: ..
---


# 1. 개요

Stdout Log Rotation (perl script)

# 2. 설명

```perl
# rotateLOG.pl 파일 내용
#!/usr/bin/perl 
$TRUE=1; 
$FALSE=0; 
$DEBUG=$FALSE; 
#$DEFAULT_LOG_PFX="/was_log/디렉토리/로그이름.";
$DEFAULT_LOG_PFX="/home/weblogic/was/1213/domains/base_domain/logs/AdminServer/AdminServer.out."; 
$logPfx=$DEFAULT_LOG_PFX;
$ignoreConsole=$FALSE; ​ 
 
while($aLine = <STDIN>){
	($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time());
	$logFile=$logPfx.sprintf("%02d%02d%02d%",($year%100),($mon+1),$mday,$hour,$min,$sec); 
	open(logH,">> $logFile"); 
    #Auto flush ON
	select((select(logH),$|=1)[0]);
	#use IO::Handle;
	#logH->autoflush($TRUE);
	print logH $aLine;
	if($ignoreConsole){ 
		print $aLine;
	} 
	close(logH); 
}
```



```sh
# 시작 방법
nohup ${DOMAIN_HOME}/bin/startWebLogic.sh 2>&1 | ./rotateLOG.pl &
```

> perl script의 sprintf 안의 %02d 가 늘어날수록, 시간단위가 작아진다. %02d%02d%02d -> 년월일, 하루 단위로 로테이션
>
> %02d%02d%02d%02d -> 한 시간 단위로 로테이션



