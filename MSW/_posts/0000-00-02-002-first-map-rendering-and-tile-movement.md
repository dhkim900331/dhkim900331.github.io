---
date: 2026-07-03 18:06:16 +0900
layout: post
title: "[MSW] 002. 메이플스토리 월드 첫 맵 로딩과 좌표계 이해"
tags: [MSW, Lua]
typora-root-url: ..
---

# 1. Overview

메이플스토리 월드 개발 가이드 영상을 수십 개 시청하면서 에디터 사용법과 기본 구조를 익혔음.

1일차에 추출한 바람의나라 맵 이미지를 이용하여 실제 월드에 로드하고 캐릭터 이동까지 확인하는 것을 목표로 진행하였음.

<br>

# 2. Descriptions

우선 Python으로 생성한 맵 PNG를 MSW에 업로드하여 Sprite 형태로 배치하였고, 캐릭터를 생성하여 상하좌우 이동이 정상적으로 이루어지는 것을 확인하였음.

<br>

이후 Atlas Unpacker를 이용하면 하나의 맵 이미지를 개별 Tile로 분리할 수 있다는 점을 확인하였고, 이를 RectTileMap으로 자동 배치하는 코드도 구현하였음.

> Unpacker만 사용해서 끝나는게 아니라, 분해된 Tile을 TileSet에 저장하고 그 TileSet을 RectTileMapComponent.TileSetRUID 에 지정 후 사용 가능

<br>

RectTileMap 기반에서는 Cell 번호를 기준으로 캐릭터를 이동시킬 수 있었으며, 바람의나라의 Tile 기반 이동 방식도 구현 가능함을 확인하였음.

> ToWorld 또는 ToCellPosition 메서드 사용

<br>

하지만 모든 맵을 Atlas로 분해해야 하는 작업량이 매우 크다는 문제가 있었음.

그래서 다른 방식을 검토하였음.

> 내가 가지고 있는 맵만 해도 3천장이 넘는데, 일일히 Unpakcer로 분리하면 Sprites 들이 수만개로 증폭하고, 이런 과정 자체가 부담됨

<br>

RectTileMap 대신 SpriteRenderer에 하나의 전체 맵 이미지를 그대로 출력하고, 월드 Scale 값을 조정하여 캐릭터가 1x, 1y 이동할 때 정확히 바람의나라 Tile 한 칸과 일치하도록 맞추는 방식을 실험하였음.

> 위에서 설명한 ToWorld/ToCell 메서드를 이용하는것과 달리 화면에 렌더링된 이미지 위에 있는 캐릭터가 정확히 이미지 비율에 맞게 걸음을 구사해야 한다.

<br>

여러 차례 Scale과 좌표 계산을 테스트한 결과 일정한 변환 값을 찾을 수 있었으며, 하나의 PNG만으로도 기존 맵을 그대로 표현하면서 Tile 단위 이동을 구현할 수 있었음.

```lua
-- deploy 함수의 공개코드
local map_ruid = map.ruid

-- 맵 이미지 렌더링
self._T.SpriteRendererComponent.SpriteRUID = map_ruid

-- 맵 이미지는 SpriteRenderer로 렌더링하므로 RectTileMap과 월드 좌표계가 완전히 일치하지 않는다.
-- 실제 측정 결과 Sprite 기본 크기로는 월드 타일보다 약간 작게 렌더링되어 타일 중심이 어긋난다.
-- 따라서 월드 타일 중심(0.5, 0.5)과 PNG 맵의 타일 중심이 정확히 일치하도록
-- 측정값을 기반으로 계산한 보정 스케일(SPRITE_MAP_SCALE)을 적용한다.
self._T.TransformComponent.Scale = Vector3(self.SPRITE_MAP_SCALE, self.SPRITE_MAP_SCALE, 1)
```

<br>

위 코드는 이미지를 내 환경에 맞게 튜닝된 SCALE 값만큼 이미지를 펼치는 것이고,

아래 코드는 그 이미지 위에서 바람의나라 움직임처럼 정확히 1칸 Cell 중심 기점으로 이동하는 코드

```lua
local map_width = map_info.size[1]
local map_height = map_info.size[2]

local current_world_pos = self._T.TransformComponent.Position

-- SpriteRenderer 기준: floor.png 중심이 0,0이라고 가정
local origin_x = -(map_width / 2)
local origin_y = -(map_height / 2)

-- 현재 월드 좌표 -> 타일 좌표
local current_tile_x = math.floor(current_world_pos.x - origin_x)
local current_tile_y = math.floor(current_world_pos.y - origin_y)

local next_tile_x = current_tile_x + x
local next_tile_y = current_tile_y + y

-- 경계 검사
if next_tile_x < 0 or next_tile_x >= map_width then
	return
end

if next_tile_y < 0 or next_tile_y >= map_height then
	return
end

-- 타일 좌표 -> 월드 좌표
local next_world_x = origin_x + next_tile_x + 0.5
local next_world_y = origin_y + next_tile_y + 0.5

self._T.TransformComponent.Position = Vector3(next_world_x, next_world_y, current_world_pos.z)
```


<br><br>


최종적으로는 다음 구조를 사용하기로 결정하였음.

- 렌더링 : 전체 맵 PNG(SpriteRenderer)
  - 더 정확히는, 땅바닥에 붙은 tile만 있는 floor.png 와 그 위 static object가 있는 objects.png를 사용할 것이다.

- 이동 : Tile 좌표 기반 계산
- 충돌 : CMP에서 추출한 Passable Flag 사용
  - 앞서 설명한대로 cmp 에 저장된 passable flag 데이터를 사용한다.

<br>


이 구조를 사용하면 수많은 맵을 별도로 타일 분해하지 않아도 되며, 유지보수와 자동화 측면에서도 훨씬 유리할 것으로 판단하였음.


<br><br>


# 3. References

- https://maplestoryworlds-creators.nexon.com/ko/resource/471?postId=471