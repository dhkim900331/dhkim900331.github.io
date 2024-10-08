---
layout: post
title: "[WebLogic] How to change context root of console"
tags: [Middleware, WebLogic, console, context, root, WLST]
typora-root-url: ..
---

# 1. Overview

어떻게 Admin Console의 Context Root를 변경하나요?
{{ site.content.br_big }}

# 2. Descriptions

Admin Console Page > Click `DOMAIN_NAME` > Configuration > General > Advanced 에서 Console Context Path 를 변경하면 됩니다.
{{ site.content.br_small }}
또는 다음의 WLST Script를 실행합니다.

```python
connect('<USERNAME>','<PASSWORD>','<ADMIN_URL>')
edit()
set('ConsoleContextPath', 'A string that you want as console context-root')
save()
activate()
```
{{ site.content.br_small }}
Console Page와 WLST 모두 재시작이 필요한 MBean Attribute 이므로 Admin Server를 재시작해야 합니다.
{{ site.content.br_big }}

# 3. References

**Admin Console Page의 Context Root를 변경하는 방법 (Doc ID 3034385.1)**