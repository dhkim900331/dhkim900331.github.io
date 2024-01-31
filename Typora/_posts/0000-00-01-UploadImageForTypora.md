---
layout: post
title: "[Typora] 블로그 이미지 업로드"
tags: [Typora, Shell, Bash, Script, Image, Assets, Sort]
typora-root-url: ..
date: 2021-12-08 12:41:57 +0900
---


# 1. 개요

blog post 작성 시 이미지 업로드를 위해 Typora 에 PicGo 를 활용했었는데,

이미지가 한 곳에 모두 쌓이다 보니 어느 post에서 생성된 이미지인지 분간이 어렵다.

포스트별 디렉토리를 생성하고, 그 안에 이미지를 업로드 하도록 설정한다.



# 2. Typora

## 2.1 이미지의 시작지점 (root) 지정

Format > Image > Use Image Root Path 메뉴

![UploadImageForTypora_1](/../assets_copy_final/posts/images/Typora/UploadImageForTypora/UploadImageForTypora_1.png)







디렉토리는 다음 이미지처럼 최상단을 지정한다.

![UploadImageForTypora_2](/../assets_copy_final/posts/images/Typora/UploadImageForTypora/UploadImageForTypora_2.png)





이렇게 설정하거나, 다음과 같이 YAML Front Matter typora-root-url 를 집어넣는다.

```markdown
---
title: "[Typora] 블로그 이미지 업로드"
date: 2021-12-08 12:41:57 +0900
categories: [GIT Blog, Plugins]
tags: [Typora, PicGo, Jekyll]
author: DongHyun Kim
typora-root-url: ..
---
```

> .md 파일이 _posts 에 있으니, image를 상단(..) 에서 상대경로로 읽으라고 지정하는 것이다.



## 2.2 Typora Image 메뉴 설정

환경 설정에서 Image를 다음과 같이 설정한다.

클립보드 이미지 또는 드래그&드랍으로 삽입하는 이미지를 assets/img/<md 파일명 디렉토리/ 안에 넣는다.

![UploadImageForTypora_3](/../assets_copy_final/posts/images/Typora/UploadImageForTypora/UploadImageForTypora_3.png)





실제로 이미지는 md 파일명을 디렉토리로 삼고, 그 안에 들어간다.

![UploadImageForTypora_4](/../assets_copy_final/posts/images/Typora/UploadImageForTypora/UploadImageForTypora_4.png)



> 2021 날짜가 붙은것은, 블로그를 포스팅 완료 후 이미지를 삽입한 게시물들이 있어 저렇게 나올 뿐이다.
>
> 현재 이 게시믈 typora_1.md 는 아직 포스팅 하지 않은 상태로 작성 중이다.



## 2.3 포스팅 후 게시글 확인

포스팅 후 확인해보면 이미지가 잘 나타나고, 이미지 별로 다음과 같이 URL이 생성된다.

![UploadImageForTypora_5](/../assets_copy_final/posts/images/Typora/UploadImageForTypora/UploadImageForTypora_5.png)


