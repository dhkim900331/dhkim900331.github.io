---
date: 2026-07-03 18:06:16 +0900
layout: post
title: "[MSW] "
tags: [MSW, Lua]
typora-root-url: ..
---


# 1. Overview

3일차에 접어들었고, 2일차에 거의 대부분 작성해둔 맵 이미지를 렌더링 하는 기존 컴포넌트를 좀 더 보강하였고,

캐릭터 이동 가능 여부를 판단할 때 사용하는 passable flag에 대해서 전격 교체를 하였다.

<br>


# 2. Descriptions

기존에는 RectTileMap에 붙은 SpriteRendererComponent의 sprite ruid를 교체해가며 맵을 렌더링했는데,

이는 테스트를 위해 하나만 설치한 것이다.

<br>

바람의나라 맵 cmp 파일에서 얻은 바닥 타일 floor.png 객체와 그 위에 얹어지는 static object가 있는 objects.png 파일을 orderInLayer 조절해가며 보여줄 것이다.

<br>

이를 위해 `/maps/mapRoot/RectTileMap/{ObjectsRenderer | FloorRenderer}` Entity 를 구성했고 각각 SpriteRendererComponent를 할당했다.

<br>

deploy_map 에서 렌더링을 진행한다.

```lua
method void deploy_map(string map_name)
--[[
 MAPINFO에서 땅바닥 이미지인 FloorRuid 를 꺼내 렌더링하고,
 그 위에 (OrderInLayer가 더 높은) ObjectsRuid 를 꺼내 렌더링한다.
 렌더링하는 이미지를 특수하게 조정된 SPRITE_MAP_SCALE 값으로 스케일업 하면 MSW 월드 좌표와 매칭이 된다.
]]--

local map_info = self:get_map_info(map_name)
if map_info == nil then
    log("map info not found")
    return
end

local map_floor_ruid = map_info.FloorRuid
local map_objects_ruid = map_info.ObjectsRuid

-- 맵 이미지 렌더링
self._T.FloorRendererEntity.SpriteRendererComponent.SpriteRUID = map_floor_ruid
self._T.ObjectsRendererEntity.SpriteRendererComponent.SpriteRUID = map_objects_ruid

-- 맵 이미지는 SpriteRenderer로 렌더링하므로 RectTileMap과 월드 좌표계가 완전히 일치하지 않는다.
-- 실제 측정 결과 Sprite 기본 크기로는 월드 타일보다 약간 작게 렌더링되어 타일 중심이 어긋난다.
-- 따라서 월드 타일 중심(0.5, 0.5)과 PNG 맵의 타일 중심이 정확히 일치하도록
-- 측정값을 기반으로 계산한 보정 스케일(SPRITE_MAP_SCALE)을 적용한다.
self._T.FloorRendererEntity.TransformComponent.Scale = Vector3(self.SPRITE_MAP_SCALE, self.SPRITE_MAP_SCALE, 1)
self._T.ObjectsRendererEntity.TransformComponent.Scale = Vector3(self.SPRITE_MAP_SCALE, self.SPRITE_MAP_SCALE, 1)
end
```

<br>

위 deploy_map 인자인 map_name은 바람의나라 맵 파일을 png로 추출한 파일명을 그대로 사용해야 한다.

앞으로 수많은 맵 파일을 업로드 할 때마다 별다른 작업이 없어야 하기 때문이다.

<br>

Workspace - RootDesk - MyDesk - Map 경로를 만들고 단순히, 렌더링할 맵 이미지(floor과 objects) 파일들을 Import 했다.

Import 후 저장을 하면, 윈도우 폴더 `<Project Name>\RootDesk\MyDesk\Map` 하위에 `*.sprite` 파일이 생성된다.

올린 이미지 파일만큼 생성되므로, 해당 파일들을 파싱하여 Filename과 RUID를 추출했다.

<br>

바람의나라 맵 파일에서 얻은 데이터는 다음과 같다.

```
Name	DisplayName	Width	Height	FloorRuid	ObjectsRuid	Collision
```

> Name : 바람의나라 맵 파일 이름 (Code로 렌더링 할 맵 이름을 가리키는데 사용)
>
> DisplayName : 향후 인게임 내 표시할 맵 이름으로 사용
>
> Width / Height : 맵 크기로써, 타일 갯수를 의미
>
> FloorRuid / ObjectsRuid : 업로드한 이미지 마다 갖는 ruid 값
>
> Collision : 타일마다 이동 가능, 불가능을 표현하는 16진수 bit flag

<br>

맵 이미지 업로드만 사용자가 하고 나머지는 py 스크립트를 이용해 자동화 하도록 하여, 위 데이터가 csv 파일로 생성되게 하였다.

csv를 MSW 에 DataSet 서비스를 사용해 메모리로 읽을 수 있다.

```lua
-- CSV 데이터 로드
local dataSet = _DataService:GetTable("MapDataSet")
if dataSet == nil then
	log("MapDataSet not found")
	return
end

-- CSV 데이터 갯수만큼 loop
local rowCount = dataSet:GetRowCount()

for i = 1, rowCount do
	local name = dataSet:GetCell(i, "Name")
	local DisplayName = dataSet:GetCell(i, "DisplayName")
	local width = tonumber(dataSet:GetCell(i, "Width"))
	local height = tonumber(dataSet:GetCell(i, "Height"))
	local FloorRuid = dataSet:GetCell(i, "FloorRuid")
	local ObjectsRuid = dataSet:GetCell(i, "ObjectsRuid")
	local collisionText = dataSet:GetCell(i, "Collision")

	-- self.MAPINFO 에 name을 key로하여 value 업데이트
	-- 클라이언트는 자신의 메모리에서 각 맵 데이터 리소스를 사용할 수 있다.
	if name ~= nil and name ~= "" then
		-- 
		self.MAPINFO[name] = {
			name = name,
			DisplayName = DisplayName,
			size = { width, height },
			width = width,
			height = height,
			FloorRuid = FloorRuid,
			ObjectsRuid = ObjectsRuid,
			collision = self:parse_collision(collisionText, width, height)
		}
	end
end
```

<br>

이제 맵 교체는 좀 더 손쉬워질 것으로 예상한다.

<br>

그리고 나서, 캐릭터가 이동할 때마다 현재 타일에서 목적지 타일로 이동이 가능한가를 2일차에 passable_flag 데이터로 완성했었는데,

이 데이터에는 방향 값을 계산할 수 있는 것이 아니였다.

<br>

다시 cmp 파일 분석 결과 collision 으로 분류할 만한 16진수 값이 들어있어 이를 csv에 포함했고,

이동 관련 스크립트에서는 목적지 타일의 collision bit flag에 따라 가능/불가능을 판단하도록 했다.

```lua
method void MovementByOffset(integer x, integer y)
--[[
 캐릭터를 목적지 타일로 1칸씩 이동 한다.
]]--

local map_name = self._T.CurrentStateComponent.current_map_name
local map_info = self._T.MapControllerComponent:get_map_info(map_name)

if map_info == nil then
	return
end

local map_width = map_info.width
local map_height = map_info.height

local current_world_pos = self._T.TransformComponent.Position

-- SpriteRenderer 기준: floor 이미지 중심이 0,0이라고 가정
local origin_x = -(map_width / 2)
local origin_y = -(map_height / 2)

-- 현재 월드 좌표 -> 0-base 타일 좌표
local current_tile_x = math.floor(current_world_pos.x - origin_x)
local current_tile_y = math.floor(current_world_pos.y - origin_y)

local next_tile_x = current_tile_x + x
local next_tile_y = current_tile_y + y

-- 경계 + collision bit 검사
-- x, y는 이동 방향이다.
-- 예: x=1,y=0 오른쪽 / x=-1,y=0 왼쪽 / x=0,y=1 위 / x=0,y=-1 아래
if not self._T.MapControllerComponent:is_passable(
	map_name,
	current_tile_x,
	current_tile_y,
	next_tile_x,
	next_tile_y,
	x,
	y
) then
	return
end

-- 0-base 타일 좌표 -> 월드 좌표
-- 타일 중앙에 캐릭터를 위치시키기 위해 +0.5
local next_world_x = origin_x + next_tile_x + 0.5
local next_world_y = origin_y + next_tile_y + 0.5

self._T.TransformComponent.Position = Vector3(
	next_world_x,
	next_world_y,
	current_world_pos.z
)
end
```

<br>

이제 캐릭터가 맵 위를 움직이는 시스템의 기본 틀은 갖췄고,

캐릭터의 모습을 바람의나라 실제 캐릭터로 임시로 교체하고 방향과 이동에 따른 애니메이션을 구현할 차례다.


<br><br>


# 3. References
