---
date: 2026-07-03 18:06:15 +0900
layout: post
title: "[Java/G1GC] References Processing Takes Too Long"
tags: [Java, JVM, GC, G1GC, STW]
typora-root-url: ..
---

# 1. Overview

G1GC의 잦은 Young GC 으로 인해 stop-the-world가 빈번하고,

Application 서비스 지연 문제가 뒤따라 옵니다.

<br>

# 2. Descriptions

대부분의 Young GC 단계가 아래 처럼 완료 되었습니다.

```
4250546.592: [GC pause (G1 Evacuation Pause) (young), 0.3872666 secs]
   [Other: 376.8 ms]
	  [Choose CSet: 0.0 ms]
	  [Ref Proc: 375.0 ms]                <<<<<<<<<<<<<
	  [Ref Enq: 0.0 ms]
	  [Redirty Cards: 0.3 ms]
	  [Humongous Register: 0.0 ms]
	  [Humongous Reclaim: 0.0 ms]
	  [Free CSet: 0.1 ms]
   [Eden: 95.0M(95.0M)->0.0B(91.0M) Survivors: 7168.0K->11.0M Heap: 703.4M(2048.0M)->612.4M(2048.0M)]
 [Times: user=0.45 sys=0.00, real=0.39 secs] 
```

<br>

`real=0.39 secs` 동안 stop-the-world가 발생했고, 이 중 대부분은 `[Ref Proc: 375.0 ms]` 처리에 사용되었습니다.

<br>

Ref Proc 구간은 SoftReference, WeakReference, FinalReference, PhantomReference, JNI Weak Reference 등의 references 객체들이나, Finalizer 구간이 많아 발생하는 것으로 볼 수 있습니다.

[참고] https://www.oracle.com/technetwork/tutorials/tutorials-1876574.html

<br>

[Java SE 11 Reference Object Processing Takes Too Long 섹션](https://docs.oracle.com/en/java/javase/11/gctuning/garbage-first-garbage-collector-tuning.html#GUID-0770AB01-E334-4E23-B307-FD2114B16E0E) 에서는 `-XX:ReferencesPerThread` 옵션을 사용하여 Ref Proc 처리 단계 시 더 많은 스레드를 사용하도록 할 수 있습니다.

<br>

Java SE 1.8 에서는 Java SE 11과 달리 `-XX:+ParallelRefProcEnabled` 옵션만 존재합니다.

또한, 기본값은 Disabled 입니다.

```sh
$ java -XX:+UnlockDiagnosticVMOptions -XX:+PrintFlagsFinal -version | grep -i "proc"
	 intx ActiveProcessorCount					= -1			{product}
	 intx G1RefProcDrainInterval				= 10			{product}
	 bool ParallelRefProcBalancingEnabled		= true			{product}
	 bool ParallelRefProcEnabled				= false			{product}		<<<<
	uintx ProcessDistributionStride				= 4				{product}
```

[참고] https://docs.oracle.com/javase/8/docs/technotes/tools/windows/java.html

<br>

고객은 Java SE 1.8 이므로 다음의 해결책이 있습니다.

1 앱 코드에서 SoftReference / WeakReference / Cleaner / Finalizer 사용처 점검

2 `-XX:+ParallelRefProcEnabled` 을 적용하여 Ref Proc 처리 구간을 Worker 수 만큼 병렬화 시켜 처리 속도 향상

3 그래도 해결되지 않는다면, `-XX:+PrintReferenceGC` 옵션으로 References 객체 처리 구간을 로깅하여 분석  

<br>

고객은 2번 `-XX:+ParallelRefProcEnabled` 을 활성화하여 문제가 해결되었습니다.

<br>

# 3. References

G1GC References Processing 이 너무 오래 걸립니다. (KB914591)
