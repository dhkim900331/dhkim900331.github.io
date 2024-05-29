---
date: 2024-05-29 14:53:50 +0900
layout: post
title: "[ODI/Studio] Why does not show Physical Schema Lists in Logical Architecture?"
tags: [ODI, ODI Studio, Schema]
typora-root-url: ..
---

# 1. Overview
Logical Architecture Component에 Context와 이에 대응되는 Physical Schemas 를 선택하려고 하지만, List box에는 Undefined 만 표시된다.

![image-20240507152843622](/../assets/posts/images/Why-Does-Not-Show-Physical-Schema-Lists/image-20240507152843622.png)

{{ site.content.br_big }}

# 2. Descriptions
Logical Architecture 에서 생성한 Components 에서는 Context와 이에 대응되는 Physical Schemas 를 선택할 수 있다.

Undefined 로 표시되는 원인은, Physical Architecture 에서 생성한 Component에 Physical Schemas 를 생성하지 않았기 때문에 발생한다.

Physical Architecture Component에 Physical Schema 를 생성하면 된다.

![image-20240507153038000](/../assets/posts/images/Why-Does-Not-Show-Physical-Schema-Lists/image-20240507153038000.png)
{{ site.content.br_small }}
Physical Architecture 에서 생성되는 Components 는 실제 Physical data servers 로 정의되어야 하고,

생성된 Components 에는 Physical data servers가 사용하는 Physical schemas 를 정의해야 한다.

[Physical Architecture](https://docs.oracle.com/middleware/12212/odi/develop/setup_topology.htm#CHDCEADA) 참고
{{ site.content.br_small }}
Logical Architecture 에서는 Logical Schemas 를 생성할 수 있고,

생성된 Logical Schemas 는 Context와 이에 대응되는 Physical Schema를 정의할 수 있다.

[Logical Architecture](https://docs.oracle.com/middleware/12212/odi/develop/setup_topology.htm#CHDJDABI) 참고

{{ site.content.br_big }}

# 3. References
**Logical Architecture Component에 Physical Schemas는 Undefined만 표시됩니다. (Doc ID 3021201.1)**

https://odielt.wordpress.com/2016/04/26/what-is-in-the-topology/

https://www.youtube.com/watch?v=Pe0oUp7dh30

https://docs.oracle.com/middleware/12212/odi/develop/setup_topology.htm

{{ site.content.br_big }}

