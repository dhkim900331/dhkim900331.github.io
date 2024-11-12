---
date: 2024-06-25 16:09:26 +0900
layout: post
title: "[JVM/Heap] How to calculate SurvivorRatio?"
tags: [JVM, Heap, SurvivorRatio]
typora-root-url: ..
---

# 1. Overview
SurvivorRatio옵션값에 따른 계산 방식


<br><br>


# 2. Descriptions

Heap 은 New / Old 영역으로 구성 되어 있으며, New 영역은 다시 Eden 과 Survivor 로 구성 되어 있다.

Survivor는 From 과 To 영역으로 구성 되어 있다.

<br>

JVM 옵션으로 Heap 전체 크기가 2GB, NewSize 768MB, SurvivorRatio 8 설정일 경우

다음의 공식에 의해 계산한다.

```
# SurvivorRatio 공식
SurvivorRatio : 8
NewSize = Eden : Survivor(From) : Survivor(To) -> 8 : 1 : 1
```


SurvivorRatio는 Eden의 크기가 Survivor의 From과 To 개별에 보다 8배 크다는 것이다.

Eden = NewSize(768) / 10 * 8

Survivor(From) = NewSize(768) / 10 * 1

Survivor(To) = NewSize(768) / 10 * 1
