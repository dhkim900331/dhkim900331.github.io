---
date: 2025-06-18 14:55:41 +0900
layout: post
title: "[WebLogic/JVM] OutOfMemoryError: Metaspace, but there is enough free memory"
tags: [Middleware, WebLogic, JVM, OutOfMemoryError, GC, Memory]
typora-root-url: ..
---

# 1. Overview

Metaspace 공간이 남아 있음에도 `OutOfMemoryError: Metaspace` 발생한 사례 분석.

JVM GC 로그 기반으로 원인 추정하고 대응 방안 정리함.

<br><br>


# 2. Descriptions

문제 발생 시 GC 로그 일부

```
420543.672: [Full GC (Metadata GC Threshold) [PSYoungGen: 19687K->0K(472064K)] [ParOldGen: 371811K->387616K(1572864K)] 391498K->387616K(2044928K), [Metaspace: 348187K->348103K(1480704K)], 1.7806265 secs] [Times: user=1.80 sys=0.00, real=1.78 secs] 
420546.272: [GC (Metadata GC Threshold) [PSYoungGen: 63514K->52108K(472064K)] 451130K->444152K(2044928K), 0.0847171 secs] [Times: user=0.06 sys=0.00, real=0.08 secs] 
420546.357: [Full GC (Metadata GC Threshold) [PSYoungGen: 52108K->0K(472064K)] [ParOldGen: 392043K->389031K(1572864K)] 444152K->389031K(2044928K), [Metaspace: 348188K->348188K(1480704K)], 1.5737886 secs] [Times: user=1.53 sys=0.00, real=1.58 secs] 
```

<br>

### (1) 동적 클래스 로딩 반복되는 패턴

일부 GC Log 이지만, Metaspace 사용량이 오르락내리락 한다는 것은, 클래스가 지속적으로 로드 될 수 있는 구조임을 보여준다.

어플리케이션에서 동적 클래스 로딩 자주 발생하는 구조로 추정 가능. (ex. eflection, Proxy, Hot deploy 등)

<br>

### (2) Metadata GC Threshold의 의미

GC 로그에 Metadata GC Threshold 표시됨.

이는 JVM이 Metaspace 사용량이 증가함에 따라 조기 Full GC를 유도했다는 이다.

[문서에 따르면 high-water mark](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/considerations.html#sthref66)는 MetaspaceSize 값에 의해 초기 설정되며, 단순히 Metaspace Free Size의 부족 시에 Metaspace GC가 발생하는 것이 아니다.

`jvm ergonomics(공학)` 적으로 관리 되는 측면에 의해, 조기에 GC가 수행 되는데,

그 GC 과정에서 언로딩 되는 클래스가 없어 여유공간 확보가 되지 않았다는 것이다.

<br>

### (3) 원인 결론 및 해결 방안

클래스가 빠른 속도로 지속적으로 로드되는 환경에서는 동일 이슈가 재현될 수 있다.

실제 Metaspace 공간의 부족을 미리 예방하지 못한것에 대한 OOME 가 발생했다.ce OOME 발생.

이를 위해,

- high-water mark에 가중치를 부여하기 위해 MaxMetaspaceSize 확대하여 여유 확보한다.

- 클래스 로딩/언로딩 패턴 모니터링하여 누수나 비정상 구조 점검

<br>

이번과 같은 사례에서는 JVM의 동작에 크리티컬한 장애를 초래하지 않을 수 있기 때문에, JVM 프로세스가 강제 종료 되지 않을 수 있다.


<br><br>


# 3. References

[Oracle Java 8 GC Tuning Guide: Class Metadata and Metaspace](https://docs.oracle.com/javase/8/docs/technotes/guides/vm/gctuning/considerations.html#sthref66)
