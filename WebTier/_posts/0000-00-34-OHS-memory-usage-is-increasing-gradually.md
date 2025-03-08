---
date: 2025-01-31 09:38:02 +0900
layout: post
title: "[WebTier/OHS] OHS memory usage is increasing gradually"
tags: [WebTier, OHS, smaps, valgrind, MaxConnectionsPerChild]
typora-root-url: ..
---

# 1. Overview

OHS 12cR2(12.2.1.4) event mpm child processes 가 점진적으로 메모리 사용률이 증가하여 재기동으로 해소 중이다.

메모리가 증가하는 원인을 분석해야 한다.


<br><br>


# 2. Descriptions

OHS 와 같은 binary process의 경우, 이러한 상황에서 분석하기 위해

OHS 자체에서 제공하는 기능이 충분치 않다.

`mod_status` 와 같은 모듈 외에 특별한 것이 있지 않기 때문에, `top` 과 같은 명령어에 의존적이다.

<br>

[valgrind](https://valgrind.org/) 를 사용하여, 메모리를 사용하는 모듈을 파악하려 하며,

smaps 자료로 메모리 사용 형태를 파악하기로 한다.

<br>

## 2.1 valgrind

apachectl 을 사용하는 OHS 12cR1 이전 버전들에 대해서는, valgrind 셋업이 비교적 쉽다.

OHS 12cR2 부터는 launch를 사용해야 하는데, binary 다 보니 valgrind 셋업이 되지 않아,

lastinvocation을 활용해야 한다.

<br>

lastinvocation.log 를 shell script로 복제한다.

```sh
$ cp ${DOMAIN_HOME}/servers/<worker>/logs/lastinvocation.log ${DOMAIN_HOME}/servers/<worker>/logs/start-<worker>_with_valgrind.sh
$ chmod +x ${DOMAIN_HOME}/servers/<worker>/logs/start-<worker>_with_valgrind.sh
```

<br>

shell 을 수정하여, valgrind 를 셋업한다.
lastinvocation.log와 비교하면, valgrind를 어떻게 셋업해야 할지 알 수 있다.

```sh
$ vi ${DOMAIN_HOME}/servers/<worker>/logs/start-<worker>_with_valgrind.sh
PATH=/sw/webtier/12cR2/wlserver/../ohs/bin:/sw/webtier/12cR2/wlserver/../bin:/bin:/usr/bin:/usr/local/bin; export PATH
...
exec valgrind --trace-children=yes --tool=memcheck --leak-check=full --log-file=/tmp/valgrind-%p.log --num-callers=35 --error-limit=no --read-var-info=yes --track-origins=yes -v /sw/webtier/12cR2/wlserver/../ohs/bin/launch httpd -DOHS_MPM_EVENT -d /sw/webtier/12cR2/.../<worker> -k start -f /sw/webtier/12cR2/.../<worker>/httpd.conf
```

<br>

OHS 실행

```sh
$ ${DOMAIN_HOME}/servers/<worker>/logs/start-<worker>_with_valgrind.sh
```

> 1024 미만의 Port를 사용 시, root 권한이 필요한데, `exec valgrind` 명령은 shell 내장함수라서 root 권한을 부여하며 실행하여도 valgrind는 적용되지 않아, 1024 미만의 Port 로 기동되지 않는다.
>
> 1024 미만의 Port를 사용하지 않도록 하거나, firewall-rules 등을 통한 조치를 하거나, 여기서 연구되지 않은 다른 방법을 찾아야 한다.

<br>

`/tmp/valgrind-<pid>.log` 아 기록되며, `kill -TERM <parent pid>` 으로 종료 시 일부 로그에 Leak summary 가 기록된다.

해당 자료를 통해 조사해야 한다.


<br><br>


## 2.2 smaps

OHS 모든 프로세스 대상으로, `/proc/<pid>/smaps` 자료를 수집하여 조사한다.

실제 고객은 OHS parent, child, rotatelogs 등 세 종류의 모든 프로세스를 조사하였다.

<br>

이 중, child processes 들에서 아래와 같이 `[Heap]`의 사용량은 적으나,

`Anonymous` 라고 하는, 어느 모듈이 사용하는지 추적되지 않은 익명으로 기록되고 있다.

또한, 여기서 `Private` 항목으로 메모리 사용률이 높다고 나오는데, 해당 child process 만 독점적으로 사용하고 있다는 것이다.

```
7fc808000000-7fc80c000000 rw-p 00000000 00:00 0 
Size:              65536 kB
Rss:               65536 kB
Pss:               65536 kB
Shared_Clean:          0 kB
Shared_Dirty:          0 kB
Private_Clean:         0 kB
Private_Dirty:     65536 kB
Referenced:        65092 kB
Anonymous:         65536 kB
AnonHugePages:      2048 kB
Swap:                  0 kB
KernelPageSize:        4 kB
MMUPageSize:           4 kB
Locked:                0 kB
```

<br>

고객은, valgrind 를 통해 더 이상 추적 하지 않고,

`MaxConnectionsPerChild` 옵션값을 10,000 으로 설정하여 주기적 재기동으로 문제를 해결하는 것으로 만족했다.

smaps 자료를 통해, 해당 child process 만의 메모리 점유 문제이므로 동의한 것이다.


<br><br>


# 3. References

<br>

