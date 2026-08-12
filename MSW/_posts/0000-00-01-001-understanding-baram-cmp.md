---
date: 2026-07-03 18:06:16 +0900
layout: post
title: "[MSW] 001. 바람의나라 맵 데이터(CMP) 구조 분석"
tags: [MSW, Lua]
typora-root-url: ../..
---

# 1. Overview

메이플스토리 월드에서 옛날 바람의나라를 구현하기 위한 첫 번째 단계는 원본 클라이언트의 맵 데이터를 이해하는 것이었음.

DizzyThermal 저장소와 여러 도구들을 참고하면서 CMP 파일 구조를 분석하였고, Python으로 필요한 데이터만 추출하는 도구를 작성하였음.


<br><br>


# 2. Descriptions

바람의나라 클라이언트에는 `.cmp` 형태의 맵 파일이 존재하며, 서버의 `.map` 데이터와 서로 대응되는 구조임.

CMP 내부에는 다음과 같은 정보들이 저장되어 있었음.

- 바닥 Tile 정보
- Palette 정보
- Static Object 정보
- Passable Flag(통행 가능 여부)

<br>

DizzyThermal 프로젝트의 TKMapper 코드를 참고하면서 CMP 내부 구조를 이해할 수 있었고, 필요한 부분만 Python으로 이식하여 자동 추출기를 작성하였음.

DizzyThermal 과 개인적으로 소통하면서 많은 도움을 받은게 컸다.

현재는 CMP 하나만 입력하면 다음 데이터를 자동으로 생성 가능함.

- 전체 맵 이미지
- Static Object 레이어
- Passable Flag 데이터

<br>

단순히 이미지를 추출하는 것이 목적이 아니라, 메이플스토리 월드에서 그대로 사용할 수 있는 형태의 데이터로 변환하는 것이 목표였음.

테스트 결과 대부분의 맵에서 정상적으로 동작하는 것을 확인하였으며, 이후 MSW에서 사용할 기본 데이터 준비를 완료하였음.


<br><br>


# 3. References

- https://github.com/DizzyThermal