---
date: 2022-08-22 14:04:46 +0900
layout: post
title: "[JVM/GC] GC Log Options에 따른 Format"
tags: [JVM, GC, Format]
typora-root-url: ..
---

# 1. 개요

GC Log 기록에 관여하는 여러 Options가 있다.

Options 변경에 따른 GC Log Format을 확인하여, 우리가 고객에게 어떤 GC Log options를 적용해줄 지 준비하자.



# 2. 테스트 환경

* CentOS Linux release 7.9.2009

* openjdk version "1.8.0_322"

* Apache Tomcat/9.0.65

* 다음의 기본 GC 옵션이 항상 적용되어 있다.

  * ```
        JAVA_OPTS="$JAVA_OPTS -verbose:gc"
        JAVA_OPTS="$JAVA_OPTS -XX:+UseG1GC"
        JAVA_OPTS="$JAVA_OPTS -Xloggc:${GC_LOG_BASE}/gc_${SERVER_NAME}.log"
    ```



# 3. 옵션별 테스트

## 3.1 모든 옵션을 Off

```
    JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCDetails"
    JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCDateStamps"
    JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCTimeStamps"
    JAVA_OPTS="$JAVA_OPTS -XX:-PrintHeapAtGC"
    JAVA_OPTS="$JAVA_OPTS -XX:-PrintTenuringDistribution"
```



최상단의 기동정보 Log를 제외하고, 첫 GC 부터 몇줄만을 scrab 한다.

gc가 발생한 jvm 상대적인 시간, heap의 확장, g1gc region 정보 등으로 볼 내용이 거의 없다.

```
 0.003: [G1Ergonomics (Heap Sizing) expand the heap, requested expansion amount: 1073741824 bytes, attempted expansion amount: 1073741824 bytes]
[GC pause (G1 Evacuation Pause) (young) 2.327: [G1Ergonomics (CSet Construction) start choosing CSet, _pending_cards: 0, predicted base time: 10.00 ms, remaining time: 190.00 ms, target pause time: 200.00 ms]
 2.327: [G1Ergonomics (CSet Construction) add young regions to CSet, eden: 51 regions, survivors: 0 regions, predicted young region time: 5164.42 ms]
 2.327: [G1Ergonomics (CSet Construction) finish choosing CSet, eden: 51 regions, survivors: 0 regions, old: 0 regions, predicted pause time: 5174.42 ms, target pause time: 200.00 ms]
 52224K->3294K(1024M), 0.0081991 secs]
[GC pause (G1 Evacuation Pause) (young) 4.080: [G1Ergonomics (CSet Construction) start choosing CSet, _pending_cards: 0, predicted base time: 6.79 ms, remaining time: 193.21 ms, target pause time: 200.00 ms]
 4.080: [G1Ergonomics (CSet Construction) add young regions to CSet, eden: 47 regions, survivors: 4 regions, predicted young region time: 951.72 ms]
 4.080: [G1Ergonomics (CSet Construction) finish choosing CSet, eden: 47 regions, survivors: 4 regions, old: 0 regions, predicted pause time: 958.51 ms, target pause time: 200.00 ms]
 51422K->6655K(1024M), 0.0112821 secs]
```



## 3.2 PrintGCDetails

    JAVA_OPTS="$JAVA_OPTS -XX:+PrintGCDetails"
    JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCDateStamps"
    JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCTimeStamps"
    JAVA_OPTS="$JAVA_OPTS -XX:-PrintHeapAtGC"
    JAVA_OPTS="$JAVA_OPTS -XX:-PrintTenuringDistribution"



```
 0.004: [G1Ergonomics (Heap Sizing) expand the heap, requested expansion amount: 1073741824 bytes, attempted expansion amount: 1073741824 bytes]
[GC pause (G1 Evacuation Pause) (young) 2.263: [G1Ergonomics (CSet Construction) start choosing CSet, _pending_cards: 0, predicted base time: 10.00 ms, remaining time: 190.00 ms, target pause time: 200.00 ms]
 2.263: [G1Ergonomics (CSet Construction) add young regions to CSet, eden: 51 regions, survivors: 0 regions, predicted young region time: 5164.42 ms]
 2.263: [G1Ergonomics (CSet Construction) finish choosing CSet, eden: 51 regions, survivors: 0 regions, old: 0 regions, predicted pause time: 5174.42 ms, target pause time: 200.00 ms]
, 0.0078045 secs]
   [Parallel Time: 7.3 ms, GC Workers: 1]
      [GC Worker Start (ms):  2262.8]
      [Ext Root Scanning (ms):  1.0]
      [Update RS (ms):  0.0]
         [Processed Buffers:  0]
      [Scan RS (ms):  0.0]
      [Code Root Scanning (ms):  0.0]
      [Object Copy (ms):  6.3]
      [Termination (ms):  0.0]
         [Termination Attempts:  1]
      [GC Worker Other (ms):  0.0]
      [GC Worker Total (ms):  7.3]
      [GC Worker End (ms):  2270.1]
   [Code Root Fixup: 0.0 ms]
   [Code Root Purge: 0.0 ms]
   [Clear CT: 0.1 ms]
   [Other: 0.4 ms]
      [Choose CSet: 0.0 ms]
      [Ref Proc: 0.1 ms]
      [Ref Enq: 0.0 ms]
      [Redirty Cards: 0.0 ms]
      [Humongous Register: 0.0 ms]
      [Humongous Reclaim: 0.0 ms]
      [Free CSet: 0.0 ms]
   [Eden: 52224.0K(52224.0K)->0.0B(48128.0K) Survivors: 0.0B->4096.0K Heap: 52224.0K(1024.0M)->3294.4K(1024.0M)]
 [Times: user=0.01 sys=0.00, real=0.01 secs]
[GC pause (G1 Evacuation Pause) (young) 4.133: [G1Ergonomics (CSet Construction) start choosing CSet, _pending_cards: 0, predicted base time: 6.84 ms, remaining time: 193.16 ms, target pause time: 200.00 ms]
 4.133: [G1Ergonomics (CSet Construction) add young regions to CSet, eden: 47 regions, survivors: 4 regions, predicted young region time: 983.74 ms]
```



## 3.3 PrintGCDateStamps

```
JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCDetails"
JAVA_OPTS="$JAVA_OPTS -XX:+PrintGCDateStamps"
JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCTimeStamps"
JAVA_OPTS="$JAVA_OPTS -XX:-PrintHeapAtGC"
JAVA_OPTS="$JAVA_OPTS -XX:-PrintTenuringDistribution"
JAVA_OPTS="$JAVA_OPTS -XX:+PrintGCDetails"
```



해당 옵션은, `2022-08-19T16:45:21.960+0900` 와 같이 벽시계(절대값)을 표현한다.

또한, 그 외에도 `-verbose:gc` 옵션으로 인해 기본으로 `PrintGCTimeStamps` 옵션이 활성화 되어, 상대값 시간(JVM 기동 시점 0.0)도 보인다.

```
 0.006: [G1Ergonomics (Heap Sizing) expand the heap, requested expansion amount: 1073741824 bytes, attempted expansion amount: 1073741824 bytes]
2022-08-19T16:45:20.139+0900: [GC pause (G1 Evacuation Pause) (young) 2.252: [G1Ergonomics (CSet Construction) start choosing CSet, _pending_cards: 0, predicted base time: 10.00 ms, remaining time: 190.00 ms, target pause time: 200.00 ms]
 2.252: [G1Ergonomics (CSet Construction) add young regions to CSet, eden: 51 regions, survivors: 0 regions, predicted young region time: 5164.42 ms]
 2.252: [G1Ergonomics (CSet Construction) finish choosing CSet, eden: 51 regions, survivors: 0 regions, old: 0 regions, predicted pause time: 5174.42 ms, target pause time: 200.00 ms]
 52224K->3294K(1024M), 0.0071640 secs]
2022-08-19T16:45:21.960+0900: [GC pause (G1 Evacuation Pause) (young) 4.073: [G1Ergonomics (CSet Construction) start choosing CSet, _pending_cards: 0, predicted base time: 6.88 ms, remaining time: 193.12 ms, target pause time: 200.00 ms]
 4.073: [G1Ergonomics (CSet Construction) add young regions to CSet, eden: 47 regions, survivors: 4 regions, predicted young region time: 949.42 ms]
```



## 3.4 PrintGCTimeStamps

```
JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCDetails"
JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCDateStamps"
JAVA_OPTS="$JAVA_OPTS -XX:+PrintGCTimeStamps"
JAVA_OPTS="$JAVA_OPTS -XX:-PrintHeapAtGC"
JAVA_OPTS="$JAVA_OPTS -XX:-PrintTenuringDistribution"
```



`-verbose:gc` 옵션만 활성화 해도, 해당 옵션은 활성화 된다, 사실상 Off 불가능한 옵션으로 보인다.

```
 0.004: [G1Ergonomics (Heap Sizing) expand the heap, requested expansion amount: 1073741824 bytes, attempted expansion amount: 1073741824 bytes]
2.293: [GC pause (G1 Evacuation Pause) (young) 2.293: [G1Ergonomics (CSet Construction) start choosing CSet, _pending_cards: 0, predicted base time: 10.00 ms, remaining time: 190.00 ms, target pause time: 200.00 ms]
 2.293: [G1Ergonomics (CSet Construction) add young regions to CSet, eden: 51 regions, survivors: 0 regions, predicted young region time: 5164.42 ms]
 2.293: [G1Ergonomics (CSet Construction) finish choosing CSet, eden: 51 regions, survivors: 0 regions, old: 0 regions, predicted pause time: 5174.42 ms, target pause time: 200.00 ms]
 52224K->3294K(1024M), 0.0081836 secs]
4.140: [GC pause (G1 Evacuation Pause) (young) 4.140: [G1Ergonomics (CSet Construction) start choosing CSet, _pending_cards: 0, predicted base time: 6.78 ms, remaining time: 193.22 ms, target pause time: 200.00 ms]
 4.140: [G1Ergonomics (CSet Construction) add young regions to CSet, eden: 47 regions, survivors: 4 regions, predicted young region time: 984.85 ms]
```



## 3.5 PrintHeapAtGC

```
JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCDetails"
JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCDateStamps"
JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCTimeStamps"
JAVA_OPTS="$JAVA_OPTS -XX:+PrintHeapAtGC"
JAVA_OPTS="$JAVA_OPTS -XX:-PrintTenuringDistribution"
```



GC 후 Heap 변화량을 나타낸다.

```
 0.003: [G1Ergonomics (Heap Sizing) expand the heap, requested expansion amount: 1073741824 bytes, attempted expansion amount: 1073741824 bytes]
{Heap before GC invocations=0 (full 0):
 garbage-first heap   total 1048576K, used 52224K [0x00000000c0000000, 0x00000000c0102000, 0x0000000100000000)
  region size 1024K, 51 young (52224K), 0 survivors (0K)
 Metaspace       used 6310K, capacity 6502K, committed 6784K, reserved 1056768K
  class space    used 723K, capacity 778K, committed 896K, reserved 1048576K
[GC pause (G1 Evacuation Pause) (young) 2.318: [G1Ergonomics (CSet Construction) start choosing CSet, _pending_cards: 0, predicted base time: 10.00 ms, remaining time: 190.00 ms, target pause time: 200.00 ms]
 2.318: [G1Ergonomics (CSet Construction) add young regions to CSet, eden: 51 regions, survivors: 0 regions, predicted young region time: 5164.42 ms]
 2.318: [G1Ergonomics (CSet Construction) finish choosing CSet, eden: 51 regions, survivors: 0 regions, old: 0 regions, predicted pause time: 5174.42 ms, target pause time: 200.00 ms]
 52224K->3294K(1024M), 0.0068773 secs]
Heap after GC invocations=1 (full 0):
 garbage-first heap   total 1048576K, used 3294K [0x00000000c0000000, 0x00000000c0102000, 0x0000000100000000)
  region size 1024K, 4 young (4096K), 4 survivors (4096K)
 Metaspace       used 6310K, capacity 6502K, committed 6784K, reserved 1056768K
  class space    used 723K, capacity 778K, committed 896K, reserved 1048576K
}
```



## 3.6 PrintTenuringDistribution

```
JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCDetails"
JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCDateStamps"
JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCTimeStamps"
JAVA_OPTS="$JAVA_OPTS -XX:-PrintHeapAtGC"
JAVA_OPTS="$JAVA_OPTS -XX:+PrintTenuringDistribution"
```



New 영역(Eden/Survivor) 을 기본 Threshold 15번 교환 후 Old 영역으로 넘어오는데,

New 영역에 대한 정보를 보여준다.

```
 0.003: [G1Ergonomics (Heap Sizing) expand the heap, requested expansion amount: 1073741824 bytes, attempted expansion amount: 1073741824 bytes]
[GC pause (G1 Evacuation Pause) (young)
Desired survivor size 3670016 bytes, new threshold 15 (max 15)
 2.294: [G1Ergonomics (CSet Construction) start choosing CSet, _pending_cards: 0, predicted base time: 10.00 ms, remaining time: 190.00 ms, target pause time: 200.00 ms]
 2.294: [G1Ergonomics (CSet Construction) add young regions to CSet, eden: 51 regions, survivors: 0 regions, predicted young region time: 5164.42 ms]
 2.294: [G1Ergonomics (CSet Construction) finish choosing CSet, eden: 51 regions, survivors: 0 regions, old: 0 regions, predicted pause time: 5174.42 ms, target pause time: 200.00 ms]
 52224K->3294K(1024M), 0.0075205 secs]
[GC pause (G1 Evacuation Pause) (young)
Desired survivor size 3670016 bytes, new threshold 15 (max 15)
```



## 3.7 모든 옵션을 On

```
JAVA_OPTS="$JAVA_OPTS -XX:+PrintGCDetails"
JAVA_OPTS="$JAVA_OPTS -XX:+PrintGCDateStamps"
JAVA_OPTS="$JAVA_OPTS -XX:+PrintGCTimeStamps"
JAVA_OPTS="$JAVA_OPTS -XX:+PrintHeapAtGC"
JAVA_OPTS="$JAVA_OPTS -XX:+PrintTenuringDistribution"
```



```
 0.005: [G1Ergonomics (Heap Sizing) expand the heap, requested expansion amount: 1073741824 bytes, attempted expansion amount: 1073741824 bytes]
{Heap before GC invocations=0 (full 0):
 garbage-first heap   total 1048576K, used 52224K [0x00000000c0000000, 0x00000000c0102000, 0x0000000100000000)
  region size 1024K, 51 young (52224K), 0 survivors (0K)
 Metaspace       used 6310K, capacity 6502K, committed 6784K, reserved 1056768K
  class space    used 723K, capacity 778K, committed 896K, reserved 1048576K
2022-08-19T16:48:32.362+0900: 2.252: [GC pause (G1 Evacuation Pause) (young)
Desired survivor size 3670016 bytes, new threshold 15 (max 15)
 2.252: [G1Ergonomics (CSet Construction) start choosing CSet, _pending_cards: 0, predicted base time: 10.00 ms, remaining time: 190.00 ms, target pause time: 200.00 ms]
 2.252: [G1Ergonomics (CSet Construction) add young regions to CSet, eden: 51 regions, survivors: 0 regions, predicted young region time: 5164.42 ms]
 2.252: [G1Ergonomics (CSet Construction) finish choosing CSet, eden: 51 regions, survivors: 0 regions, old: 0 regions, predicted pause time: 5174.42 ms, target pause time: 200.00 ms]
, 0.0077020 secs]
   [Parallel Time: 7.4 ms, GC Workers: 1]
      [GC Worker Start (ms):  2252.1]
      [Ext Root Scanning (ms):  1.1]
      [Update RS (ms):  0.0]
         [Processed Buffers:  0]
      [Scan RS (ms):  0.0]
      [Code Root Scanning (ms):  0.0]
      [Object Copy (ms):  6.3]
      [Termination (ms):  0.0]
         [Termination Attempts:  1]
      [GC Worker Other (ms):  0.0]
      [GC Worker Total (ms):  7.4]
      [GC Worker End (ms):  2259.5]
   [Code Root Fixup: 0.0 ms]
   [Code Root Purge: 0.0 ms]
   [Clear CT: 0.0 ms]
   [Other: 0.2 ms]
      [Choose CSet: 0.0 ms]
      [Ref Proc: 0.1 ms]
      [Ref Enq: 0.0 ms]
      [Redirty Cards: 0.0 ms]
      [Humongous Register: 0.0 ms]
      [Humongous Reclaim: 0.0 ms]
      [Free CSet: 0.0 ms]
   [Eden: 52224.0K(52224.0K)->0.0B(48128.0K) Survivors: 0.0B->4096.0K Heap: 52224.0K(1024.0M)->3294.4K(1024.0M)]
Heap after GC invocations=1 (full 0):
 garbage-first heap   total 1048576K, used 3294K [0x00000000c0000000, 0x00000000c0102000, 0x0000000100000000)
  region size 1024K, 4 young (4096K), 4 survivors (4096K)
 Metaspace       used 6310K, capacity 6502K, committed 6784K, reserved 1056768K
  class space    used 723K, capacity 778K, committed 896K, reserved 1048576K
}
 [Times: user=0.01 sys=0.00, real=0.01 secs]
{Heap before GC invocations=1 (full 0):
 garbage-first heap   total 1048576K, used 51422K [0x00000000c0000000, 0x00000000c0102000, 0x0000000100000000)
  region size 1024K, 51 young (52224K), 4 survivors (4096K)
 Metaspace       used 10499K, capacity 10810K, committed 11136K, reserved 1058816K
  class space    used 1214K, capacity 1315K, committed 1408K, reserved 1048576K
```



위 옵션은 과한 것 같다. 해당 옵션이 필요한 시점은 문제가 발생하여 디버깅을 해야 될 수준일 텐데

일반적으로 그러한 시점은 없어 보인다.



## 3.8 권장 옵션

GC Log 시점은 벽시계 기준이 보기에 편리하고, Heap 상태만 알 수 있어도 반은 먹고(?) 들어간다고 생각된다.



```
JAVA_OPTS="$JAVA_OPTS -XX:-PrintGCDetails"
JAVA_OPTS="$JAVA_OPTS -XX:+PrintGCDateStamps"
JAVA_OPTS="$JAVA_OPTS -XX:+PrintGCTimeStamps"
JAVA_OPTS="$JAVA_OPTS -XX:+PrintHeapAtGC"
JAVA_OPTS="$JAVA_OPTS -XX:-PrintTenuringDistribution"
```



또한 모든 옵션을 On 한 기준의 GC Log 파일에서, 상단 JVM Arguments 로그를 빼면 6초 동안 12 kbytes 가 기록되었다.

(말도 안되지만..) 이 기준을 근거로, 1시간(3600초, 6초가 600번) 동안 7 mbytes 가 기록된다고 단순 계산된다.

1일 = 168MB
