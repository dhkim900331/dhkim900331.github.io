---
date: 2022-02-15 11:57:12 +0900
layout: post
title: "[WebLogic] 웹로직에 부하를 주는 스레드 찾기(Linux, AIX, Windows7)"
tags: [Middleware, WebLogic, Thread]
typora-root-url: ..
---


# 1. 개요

웹로직에 부하를 주는 스레드 찾기(Linux, AIX, Windows7)



# 2. 다음의 JSP를 배포하여 실행

```jsp
for (int i=0; i < 3; i++)
    {
       Thread x=new Thread(new Runnable(){
                  public void run()
                    {
                       System.out.println("Thread " +Thread.currentThread().getName() + " started");
                       double val=10;
                       for (;;)
                         {
                            Math.atan(Math.sqrt(Math.pow(val, 10)));
                         }
                     }
              });
        x.start();
    }
%>
```



## 3. OS별 확인 방법

### 3.1 Linux

```bash
# ps -ef | grep java
```

> instance PID를 찾는다. **찾은 PID: 22384**



```bash
# watch "ps -eLo pid,ppid,tid,pcpu,comm | grep 22384"
```

> watch 명령어로 2초마다 cpu 사용량을 게더링 할 수 있다.
>
> _**문서에는 watch가 cpu 사용량을 게더링하기 유용하지 않은 명령어라고 한다.**_



```bash
# ps -eLo pid,ppid,tid,pcpu,comm | grep 22384 > 22384.out
```

> 현재 cpu 사용량 게더링 결과를 22384.out으로 저장 한다.



```bash
# cat 22384.out | awk '{ print "pccpu: "$4" pid: "$1" ppid: "$2" ttid: "$3" comm: "$5}' |sort -n
```

> 게더링 결과의 cpu 사용량을 기준으로 내림차순하여 본다.



```bash
# ps -eLo pid,ppid,tid,pcpu,comm | grep 22384 | awk '{ print "pccpu: "$4" pid: "$1" ppid: "$2" ttid: "$3" comm: "$5}' |sort -n
```

> '다'와 '라'의 명령어를 한 줄로 합쳐서 볼 수 있다.
>
> 실행 결과는 다음과 같다. 인스턴스(22384)의 32.2퍼센트 cpu를 사용하는 스레드 아이디는 **22557, 22558, 22559**
>
![HowToFindIssueThread_1](/../assets/posts/images/01-WebLogic/HowToFindIssueThread/HowToFindIssueThread_1.png)
>
> 22557, 22558, 22559를 헥사값(16진수)로 변환하면 각각 **0x581d, 0x581e, 0x581f** 다.



```bash
# kill -3 22384
```

> 덤프를 생성 후, 위에서 구한 헥사값을 검색하면 다음과 같다.
>
> jsp에서 Thread 3개를 생성 하고, 각각 Math.atan 메소드 실행 부분을 덤프에서도 확인할 수 있다.



```찾은결과
"Thread-36" daemon prio=10 tid=0x00007f43d0059800 nid=0x581f runnable [0x00007f43cf8f7000]
   java.lang.Thread.State: RUNNABLE
     at java.lang.StrictMath.atan(Native Method)
     at java.lang.Math.atan(Math.java:204)
     at jsp_servlet.__highcpu$1.run(__highcpu.java:84)
     at java.lang.Thread.run(Thread.java:745)
     
"Thread-35" daemon prio=10 tid=0x00007f43d0058800 nid=0x581e runnable [0x00007f43cf9f8000]
   java.lang.Thread.State: RUNNABLE
     at java.lang.StrictMath.atan(Native Method)
     at java.lang.Math.atan(Math.java:204)
     at jsp_servlet.__highcpu$1.run(__highcpu.java:84)
     at java.lang.Thread.run(Thread.java:745)

"Thread-34" daemon prio=10 tid=0x00007f43d005b800 nid=0x581d runnable [0x00007f43cfaf9000]
   java.lang.Thread.State: RUNNABLE
     at java.lang.StrictMath.atan(Native Method)
     at java.lang.Math.atan(Math.java:204)
     at jsp_servlet.__highcpu$1.run(__highcpu.java:84)
     at java.lang.Thread.run(Thread.java:745)
```



### 3.2 Windows 7

[여기](https://technet.microsoft.com/en-us/sysinternals/bb896682) 에서 프로세스 리스트를 확인할 수 있는 pslist 툴을 설치한다.

> 압축을 해제하고 cmd로 해당 디렉토리에서 다음 작업을 이어간다.



```bash
# pslist java
```

![HowToFindIssueThread_2](/../assets/posts/images/01-WebLogic/HowToFindIssueThread/HowToFindIssueThread_2.png)
>
> pc에서 현재 동작중인 프로세스 중 자바를 찾아본다. **java PID는 7820**
>
> 각 파라메타 설명은 pslist 툴을 다운로드 받은 홈페이지에 있다.



```bash
# pslist -d 7820
8604   8    138786          Running  0:03:25.999   0:00:00.000    0:03:30.540
```

> java 프로세스의 스레드 정보를 볼 수 있다.
>
> 다음이 그 정보인데, Cswtch와 User/Kernel Time을 보면 문제가 되는 스레드 아이디는 **7384, 5712, 8604 다.**Cswtch(Context Switch)는 멀티태스킹을 위하여 실행되는 여러 스레드들의 상태를 저장하고, 복구하는 일련의 과정이 얼마나 자주 일어났는지를 뜻한다.
>
> *참고사이트: http://en.wikipedia.org/wiki/Context_switch*
>
> ***User Time은*** CPU의 사용자 영역에서 실행된 총 시간이다. 모두 03분 26초 실행 시간을 보여주고 있다.
>
> ***Kernel Time은*** CPU의 커널 영역을 의미하는 시간이다.
>
> User Time 3분대를 기록한 스레드 3개가 너무 오랫동안 실행이 되며, Cswtch 수치가 이상하다.
>
> 각 스레드 아이디를 헥사값으로 변환하여 스레드 덤프에서 찾아보자.
>
> 7384: **1CD8**, 5712: **1650**, 8604: 219C 각각을 찾아보니 다음과 같다.



```찾은결과
"Thread-15" daemon prio=6 tid=0x0000000007729800 nid=0x219c runnable [0x000000000cdaf000]
   java.lang.Thread.State: RUNNABLE
     at java.lang.StrictMath.atan(Native Method)
     at java.lang.Math.atan(Math.java:187)
     at jsp_servlet.__highcpu$1.run(__highcpu.java:79)
     at java.lang.Thread.run(Thread.java:662)

"Thread-14" daemon prio=6 tid=0x0000000007729000 nid=0x1650 runnable [0x000000000ccaf000]
   java.lang.Thread.State: RUNNABLE
     at java.lang.StrictMath.atan(Native Method)
     at java.lang.Math.atan(Math.java:187)
     at jsp_servlet.__highcpu$1.run(__highcpu.java:79)
     at java.lang.Thread.run(Thread.java:662)

"Thread-13" daemon prio=6 tid=0x0000000007728000 nid=0x1cd8 runnable [0x000000000cbaf000]
   java.lang.Thread.State: RUNNABLE
     at java.lang.StrictMath.atan(Native Method)
     at java.lang.Math.atan(Math.java:187)
     at jsp_servlet.__highcpu$1.run(__highcpu.java:79)
     at java.lang.Thread.run(Thread.java:662)
```



### 3.3 AIX

```bash
# ps -ef | grep java
```

> instance PID를 찾는다. **찾은 PID: 16908684**



```bash
# ps -mp 16908684 -o THREAD
```

> instance PID의 스레드 목록을 출력한다.



```위명령의결과
    USER      PID     PPID        TID S  CP PRI SC    WCHAN        F     TT BND COMMAND

     cs2 16908684 17825820          - A 360  60 55        *   202001  pts/2   - /usr/java7_64/bin/java -Xms512m -Xmx512m -Dweblo

       -        -        -    4980787 S   0  82  1 f1000f0a10004c40  8410400      -   - -

       -        -        -    9306279 S   0  82  1 f1000f0a10008e40  8410400      -   - -

       -        -        -   12976337 Z   0  82  1        -   c00001      -   - -

       -        -        -   13893815 S   0  82  1 f1000f0a1000d440  8410400      -   - -

       -        -        -   15663295 Z   0  98  1        -   c00001      -   - -

       -        -        -   20578311 S   0  82  1 f1000f0a10013a40  8410400      -   - -

       -        -        -   21168367 S   0  60  1 f1000f0a10014340  8410400      -   - -

       -        -        -   21561529 R 120 162  0        -   400000      -   - -

       -        -        -   24510581 S   0  66  1 f10005000e3ba208   410400      -   - -

       -        -        -   31195139 Z   0  98  1        -   c00001      -   - -

       -        -        -   32243767 S   0  82  1 f1000f0a1001ec40  8410400      -   - -

       -        -        -   38928587 S   0  82  1 f100012020bbd4b0   410400      -   - -

       -        -        -   39583921 S   0  82  1 f100012027555f78   410400      -   - -

       -        -        -   46858399 S   0  82  1 f1000f0a1002cb40  8410400      -   - -

       -        -        -   52035835 S   0 100  1 f1000f0a10031a40  8410400      -   - -

       -        -        -   53542927 S   0  82  1 f1000f0a10033140  8410400      -   - -

       -        -        -   54525969 S   0  60  1 f1000f0a10034040  8410400      -   - -

       -        -        -   56295463 Z   0  98  1        -   c00001      -   - -

       -        -        -   56819751 Z   0  98  1        -   c00001      -   - -

       -        -        -   56885315 S   0  82  1 f1000f0a10036440  8410400      -   - -

       -        -        -   60031145 S   0  82  1 f1000f0a10039440  8410400      -   - -

       -        -        -   68812921 S   0  82  1 f1000f0a10041a40  8410400      -   - -

       -        -        -   70451297 S   0  82  1 f1000f0a10043340  8410400      -   - -

       -        -        -   72417493 Z   0  98  1        -   c00001      -   - -

       -        -        -   73072781 S   0  94  1 f1000f0a10045b40  8410400      -   - -

       -        -        -   76677207 Z   0  98  1        -   c00001      -   - -

       -        -        -   77267163 S   0  82  1 f100012020b6ec78   410400      -   - -

       -        -        -   77594839 S   0  60  1 f1000f0a1004a040  8410400      -   - -

       -        -        -   85590073 S   0  82  1 f1000f0a10051a40  8410400      -   - -

       -        -        -   90570909 S   0  82  1 f1000f0a10056640  8410400      -   - -

       -        -        -   95551739 S   0  82  1 f1000f0a1005b240  8410400      -   - -

       -        -        -   99811459 S   0  78  1 f1000f0a1005f340  8410400      -   - -

       -        -        -  103415911 S   0  82  1 f1000f0a10062a40  8410400      -   - -

       -        -        -  103546957 S   0  82  1 f100012020b6eb78   410400      -   - -

       -        -        -  111018063 S   0  60  1 f1000120085fc598   410400      -   - -

       -        -        -  118685867 S   0  66  1 f1000f0a10071340  8410400      -   - -

       -        -        -   18088333 S   0  78  1 f1000f0a10091440  8410400      -   - -

       -        -        -   18153845 S   0  60  1 f1000f0a10091540  8410400      -   - -

       -        -        -   18612571 S   0  82  1 f1000f0a10091c40  8410400      -   - -

       -        -        -   22413601 S   0  82  1 f1000f0a10095640  8410400      -   - -

       -        -        -   23527931 Z   0  98  1        -   c00001      -   - -

       -        -        -   43450815 R 120 162  0        -   400000      -   - -

       -        -        -   58196403 S   0  82  1 f1000f0a100b7840  8410400      -   - -

       -        -        -   61538703 S   0  78  1 f1000f0a100bab40  8410400      -   - -

       -        -        -   66978283 S   0  82  1 f1000f0a100bfe40  8410400      -   - -

       -        -        -   76087735 S   0  82  1 f1000f0a100c8940  8410400      -   - -

       -        -        -   79102281 S   0  60  1 f1000f0a100cb740  8410400      -   - -

       -        -        -   83231169 S   0  82  1 f10001201fb6a978   410400      -   - -

       -        -        -   83624307 S   0  82  1 f1000f0a100cfc40  8410400      -   - -

       -        -        -   83755267 S   0  62  1 f100011808232118   410400      -   - -

       -        -        -   84541707 R 120 162  0        -   400000      -   - -

       -        -        -   85000601 S   0  66  1 f1000f0a100d1140  8410400      -   - -

       -        -        -   91291923 S   0  82  1 f1000f0a100d7140  8410400      -   - -

       -        -        -   94175563 S   0  82  1 f1000f0a100d9d40  8410400      -   - -

       -        -        -   95551785 Z   0  98  1        -   c00001      -   - -

       -        -        -   96010609 S   0  82  1 f1000f0a100db940  8410400      -   - -

       -        -        -   97386857 S   0  82  1 f1000f0a100dce40  8410400      -   - -

       -        -        -  101187847 S   0  60  1 f1000f0a100e0840  8410400      -   - -
```

> CP는 ~ 이다. 대부분 CP가 0이지만 TID(Thread ID) **21561529, 43450815, 84541707**는 120의 높은 값을 보여주고 있다.
>
> 위 TID를 각각 16진수로 변환하면 **14900B9, 29701BF, 50A010B**가 된다.
>
> 스레드 덤프에서 16진수로 변환한 TID를 검색해보니, 실행한 jsp 정보를 볼 수 있었다.



```찾은결과
3XMTHREADINFO      "Thread-33" J9VMThread:0x00000000524AEB00, j9thread_t:0x00000100151EC5C0, java/lang/Thread:0x00000000498A4898, s

tate:R, prio=5

3XMJAVALTHREAD            (java/lang/Thread getId:0x54, isDaemon:true)

3XMTHREADINFO1            (native thread ID:0x14900B9, native priority:0x5, native policy:UNKNOWN, vmstate:CW, vm thread flags:0x00

000001)

3XMCPUTIME               CPU usage total: 2274.685427000 secs, user: 2274.684771000 secs, system: 0.000656000 secs

3XMHEAPALLOC             Heap bytes allocated since last GC cycle=0 (0x0)

3XMTHREADINFO3           Java callstack:

4XESTACKTRACE                at jsp_servlet/__test$1.run(__test.java:81(Compiled Code))

4XESTACKTRACE                at java/lang/Thread.run(Thread.java:795)

3XMTHREADINFO3           Native callstack:

4XENATIVESTACK               _event_wait+0x2b8 (0x09000000005C489C [libpthreads.a+0x1689c])

4XENATIVESTACK               _cond_wait_local+0x4e4 (0x09000000005D2668 [libpthreads.a+0x24668])

4XENATIVESTACK               _cond_wait+0xbc (0x09000000005D2C40 [libpthreads.a+0x24c40])

4XENATIVESTACK               pthread_cond_wait+0x1a8 (0x09000000005D38AC [libpthreads.a+0x258ac])

4XENATIVESTACK               (0x090000000149D2F4 [libj9thr26.so+0x62f4])

4XENATIVESTACK               (0x090000000149CF40 [libj9thr26.so+0x5f40])

4XENATIVESTACK               (0x09000000013E2F58 [libj9vm26.so+0xff58])

4XENATIVESTACK               (0x09000000013EF850 [libj9vm26.so+0x1c850])

4XENATIVESTACK               (0x0900000001DCEF3C [libj9jit26.so+0x7dff3c])

4XENATIVESTACK               (0x09000000013D9864 [libj9vm26.so+0x6864])

4XENATIVESTACK               (0x09000000014B4CE0 [libj9prt26.so+0x2ce0])

4XENATIVESTACK               (0x09000000013D96D4 [libj9vm26.so+0x66d4])

4XENATIVESTACK               (0x0900000001499AF4 [libj9thr26.so+0x2af4])

4XENATIVESTACK               _pthread_body+0xf0 (0x09000000005B1D54 [libpthreads.a+0x3d54])

NULL

​

3XMTHREADINFO      "Thread-35" J9VMThread:0x00000000524B1300, j9thread_t:0x000001001771AD40, java/lang/Thread:0x00000000498A5908, s

tate:R, prio=5

3XMJAVALTHREAD            (java/lang/Thread getId:0x56, isDaemon:true)

3XMTHREADINFO1            (native thread ID:0x29701BF, native priority:0x5, native policy:UNKNOWN, vmstate:CW, vm thread flags:0x00

000001)

3XMCPUTIME               CPU usage total: 2265.056957000 secs, user: 2265.056386000 secs, system: 0.000571000 secs

3XMHEAPALLOC             Heap bytes allocated since last GC cycle=0 (0x0)

3XMTHREADINFO3           Java callstack:

4XESTACKTRACE                at jsp_servlet/__test$1.run(__test.java:81(Compiled Code))

4XESTACKTRACE                at java/lang/Thread.run(Thread.java:795)

3XMTHREADINFO3           Native callstack:

4XENATIVESTACK               _event_wait+0x2b8 (0x09000000005C489C [libpthreads.a+0x1689c])

4XENATIVESTACK               _cond_wait_local+0x4e4 (0x09000000005D2668 [libpthreads.a+0x24668])

4XENATIVESTACK               _cond_wait+0xbc (0x09000000005D2C40 [libpthreads.a+0x24c40])

4XENATIVESTACK               pthread_cond_wait+0x1a8 (0x09000000005D38AC [libpthreads.a+0x258ac])

4XENATIVESTACK               (0x090000000149D2F4 [libj9thr26.so+0x62f4])

4XENATIVESTACK               (0x090000000149CF40 [libj9thr26.so+0x5f40])

4XENATIVESTACK               (0x09000000013E2F58 [libj9vm26.so+0xff58])

4XENATIVESTACK               (0x09000000013EF850 [libj9vm26.so+0x1c850])

4XENATIVESTACK               (0x0900000001DCEF3C [libj9jit26.so+0x7dff3c])

4XENATIVESTACK               (0x09000000013D9864 [libj9vm26.so+0x6864])

4XENATIVESTACK               (0x09000000014B4CE0 [libj9prt26.so+0x2ce0])

4XENATIVESTACK               (0x09000000013D96D4 [libj9vm26.so+0x66d4])

4XENATIVESTACK               (0x0900000001499AF4 [libj9thr26.so+0x2af4])

4XENATIVESTACK               _pthread_body+0xf0 (0x09000000005B1D54 [libpthreads.a+0x3d54])

NULL

​

3XMTHREADINFO      "Thread-34" J9VMThread:0x0000000052308300, j9thread_t:0x000001001771B260, java/lang/Thread:0x00000000498A5250, s

tate:R, prio=5

3XMJAVALTHREAD            (java/lang/Thread getId:0x55, isDaemon:true)

3XMTHREADINFO1            (native thread ID:0x50A010B, native priority:0x5, native policy:UNKNOWN, vmstate:CW, vm thread flags:0x00

000001)

3XMCPUTIME               CPU usage total: 2264.278773000 secs, user: 2264.278270000 secs, system: 0.000503000 secs

3XMHEAPALLOC             Heap bytes allocated since last GC cycle=0 (0x0)

3XMTHREADINFO3           Java callstack:

4XESTACKTRACE                at jsp_servlet/__test$1.run(__test.java:81(Compiled Code))

4XESTACKTRACE                at java/lang/Thread.run(Thread.java:795)

3XMTHREADINFO3           Native callstack:

4XENATIVESTACK               _event_wait+0x2b8 (0x09000000005C489C [libpthreads.a+0x1689c])

4XENATIVESTACK               _cond_wait_local+0x4e4 (0x09000000005D2668 [libpthreads.a+0x24668])

4XENATIVESTACK               _cond_wait+0xbc (0x09000000005D2C40 [libpthreads.a+0x24c40])

4XENATIVESTACK               pthread_cond_wait+0x1a8 (0x09000000005D38AC [libpthreads.a+0x258ac])

4XENATIVESTACK               (0x090000000149D2F4 [libj9thr26.so+0x62f4])

4XENATIVESTACK               (0x090000000149CF40 [libj9thr26.so+0x5f40])

4XENATIVESTACK               (0x09000000013E2F58 [libj9vm26.so+0xff58])

4XENATIVESTACK               (0x09000000013EF850 [libj9vm26.so+0x1c850])

4XENATIVESTACK               (0x0900000001DCEF3C [libj9jit26.so+0x7dff3c])

4XENATIVESTACK               (0x09000000013D9864 [libj9vm26.so+0x6864])

4XENATIVESTACK               (0x09000000014B4CE0 [libj9prt26.so+0x2ce0])

4XENATIVESTACK               (0x09000000013D96D4 [libj9vm26.so+0x66d4])

4XENATIVESTACK               (0x0900000001499AF4 [libj9thr26.so+0x2af4])

4XENATIVESTACK               _pthread_body+0xf0 (0x09000000005B1D54 [libpthreads.a+0x3d54])

NULL
```

