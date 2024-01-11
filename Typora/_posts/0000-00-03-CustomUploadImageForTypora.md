---
date: 2022-12-01 08:41:51 +0900
layout: post
title: "[Typora] 이미지 커스텀 업로드 기능 사용해보기"
tags: [Typora, Shell, Bash, Script, Image, Assets]
typora-root-url: ..
---


# 1. 개요

예전에 [PostImageSorting](PostImageSorting) 에서 Typora 이미지 업로드 기능을 알아보았다.

해당 방식은 나의 Local git directory 에 이미지를 삽입하는 방식이다.



혹, 다른 image cloud (like CDN) 서비스에 업로드하고

해당 이미지의 URL을 사용하고 싶을 때는 어떻게 해야 될까?





# 2. Custom Upload Image

## 2.1 Preferences

그럴때는 Custom Upload 방식을 취하면 된다.



해당 방식은 [공식 메뉴얼](https://support.typora.io/Upload-Image/#custom) 을 참고하면 되며,

[트러블 슈팅](https://support.typora.io/Upload-Image/#troubleshooting) 란 또한 참고하면 된다.



우선, 다음과 같이 `Upload image` 및 `Custom Command` 를 설정한다.

![CustomUploadImageForTypora_1](/../assets/posts/images/07-Typora/CustomUploadImageForTypora/CustomUploadImageForTypora_1.png)





`Custom Command`는 `C:\PROGRA~1\Git\bin\sh.exe /c/Users/Dong-Hyun.KIM/Desktop/GoodMorning/2.-Blog/uploader.sh ${filename}` 와 같이 `uploader.sh`을 설정한다.

뒤에 `${filename}`은 Typora에서 현재 Markdown 의 Filename을 매개변수로 넘겨준다.

**저장하지 않은 Untitled md 일 경우, 빈 값이 전송되므로 유의해야 한다.**



## 2.2 uploader.sh

```shell
#!/usr/bin/bash

BASEDIR=$(dirname "$0")
. ${BASEDIR}/env.sh

MSG_SUC='Upload Success:'
MSG_FAI='Upload Failed:'

ASSET_HOME=${HOME}/${GIT}/assets/posts/images

# Extract markdown filename without DATE Format and Extension
MD_REGEX_DATE='^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-'
MD_REGEX_EXTENSION='\.[mMdD]\{2\}$'
MD_FILENAME=$1
MD_FILENAME=$(echo ${MD_FILENAME} | sed -e "s|${MD_REGEX_DATE}||g")
MD_FILENAME=$(echo ${MD_FILENAME} | sed -e "s|${MD_REGEX_EXTENSION}||g")

# Change image filename
IMG_REGEX_EXTENSION='^.*\.'
IMG_FILENAME=$2
IMG_EXTENSION=$(echo ${IMG_FILENAME} | sed -e "s|${IMG_REGEX_EXTENSION}||g")
IMG_FILENAME=${MD_FILENAME}-$(date +%Y%m%d_%H%M%S).${IMG_EXTENSION}

if [ ! $# -eq 2 ]
then
	echo ${MSG_FAI}
	echo "argument should equal to TWO"
	exit;
fi



# mkdir
/usr/bin/mkdir -p ${ASSET_HOME}/${MD_FILENAME}
if [ ! $? -eq 0 ]
then
	echo ${MSG_FAI}
	echo "failed mkdir"
	exit;
fi

# move
/usr/bin/mv $2 ${ASSET_HOME}/${MD_FILENAME}/${IMG_FILENAME}
if [ ! $? -eq 0 ]
then
	echo ${MSG_FAI}
	echo "failed move"
	exit;
fi

echo ${MSG_SUC}
#echo "file:///../assets/posts/images/${MD_FILENAME}/${IMG_FILENAME}"
#echo 'https://dhkim900331.github.io/assets/posts/images/${MD_FILENAME}/${IMG_FILENAME}'
```



나는 Post (.md) 파일 안에 YAML Front Matter section 에 date 를 설정하였다.

기본적으로는, File name의 date가 설정되어 있어야 하겠지만

너무 URL이 지저분해지는 경향이 있어 변경하였다.

그대신 Filename에는 반드시 (내가알기로는) date format string이 있어야 하는거 같아

`0000-00-01-File.md` 와 같은 형식으로 관리하고 있다.



그러다보니 아래 코드 조각으로 위 파일 형식에서 Prefix date와 Postfix extension을 제거한다.

```shell
# Extract markdown filename without DATE Format and Extension
MD_REGEX_DATE='^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-'
MD_REGEX_EXTENSION='\.[mMdD]\{2\}$'
MD_FILENAME=$1
MD_FILENAME=$(echo ${MD_FILENAME} | sed -e "s|${MD_REGEX_DATE}||g")
MD_FILENAME=$(echo ${MD_FILENAME} | sed -e "s|${MD_REGEX_EXTENSION}||g")
```

> $1은 말머리에서 언급한, Typoar가 현재 수정중인 MD 파일명을 매개변수로 넘겨주는 것이다.



Typora 에디터 내에서 Ctrl+V 로 붙여넣기하는 이미지는, 임시 디렉토리(Windows)에 저장이 된다.

해당 이미지의 경로를 매개변수(`$2`)로 받게 된다.

이미지의 파일명과 확장자를 변수로 분리한다.

```shell
# Change image filename
IMG_REGEX_EXTENSION='^.*\.'
IMG_FILENAME=$2
IMG_EXTENSION=$(echo ${IMG_FILENAME} | sed -e "s|${IMG_REGEX_EXTENSION}||g")
IMG_FILENAME=${MD_FILENAME}-$(date +%Y%m%d_%H%M%S).${IMG_EXTENSION}
```



MD 파일명으로 이미지를 저장할 디렉토리를 생성하고,

이미지를 해당 디렉토리에 저장한다.

```shell
# mkdir
/usr/bin/mkdir -p ${ASSET_HOME}/${MD_FILENAME}
if [ ! $? -eq 0 ]
then
	echo ${MSG_FAI}
	echo "failed mkdir"
	exit;
fi

# move
/usr/bin/mv $2 ${ASSET_HOME}/${MD_FILENAME}/${IMG_FILENAME}
if [ ! $? -eq 0 ]
then
	echo ${MSG_FAI}
	echo "failed move"
	exit;
fi
```



가자 중요한 부분으로,

Typora는 return 값의 마지막 N 줄을 읽어들인다.

Ctrl+V 붙여넣기로 한번에 N 개의 이미지를 삽입하면, 그만큼 N줄을 읽어간다.

여기 스크립트는 1개 이미지만 대상으로 짜여져 있기 때문에, > 1 은 Error 발생한다.



return 값의 형식으로는 `file://` 또는 `http(s)://` 에 해당되는 Protocol만 인식한다.

나머지는 Error가 뜬다...

`file://` 부분을 사용하고자 해당 스크립트를 쓰는 경우는 없을 것이고,

img cloud 에 업로드한 후 uri 를 받아온 다음에 활용하기 좋을 것이다.

```shell
echo ${MSG_SUC}
#echo "file:///../assets/posts/images/${MD_FILENAME}/${IMG_FILENAME}"
#echo 'https://dhkim900331.github.io/assets/posts/images/${MD_FILENAME}/${IMG_FILENAME}'
```

