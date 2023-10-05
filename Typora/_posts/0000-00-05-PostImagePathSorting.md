---
date: 2022-12-02 08:52:18 +0900
layout: post
title: "[Typora] 불필요한 이미지 리소스 제거"
tags: [Typora, Shell, Bash, Script, Image, Assets, Remove]
typora-root-url: ..
---

<br># 1. 개요

[PostImageSorting](PostImageSorting)에서는 Image 의 경로를 바로 잡아주었다.

> Typora로 image를 paste 하고 나면 내가 원하는 Image 경로가 아니다. (냅둬도 상관은 없음)

<br>
이 게시물에서는,

문제가 없이 존재하는 Image 자체를

내가 원하는 디렉토리 구조로 옮겨 세팅해주는 스크립트다.

<br><br>

<br># 2. ImagePathSorter.sh

```shell
#!/usr/bin/bash

# Post에 사용된 모든 image를 구조적으로 통일한다.
# 예) <category>/<postname>/<imagename>_<idx>.png

BASEDIR=$(dirname "$0")
. ${BASEDIR}/env.sh

# 내가 만든 post md 파일
find $HOME/$GIT/*/_posts -type f -name "*.md" |
while read MD
do
	# 에서 첨부한 이미지 tag 추출
	imgTag=$(grep "\!\[" ${MD})
	if [ "x$imgTag" == "x" ]
	then
		# 이미지 tag가 없는 md파일은 스킵한다.
		continue
	fi
	
	# 에서 Category 추출 (https://linuxhint.com/sed-capture-group-examples/)
	mCat=$(echo ${MD} | sed 's/^\(.*\)\/\(.*\)\/_posts\/\(.*\)\.md$/\2/')
	
	# 에서 MD 파일명 추출 (date format string 제거)
	MD_REGEX_DATE='^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-'
	mName=$(echo ${MD} | sed 's/^\(.*\)\/\(.*\)\/_posts\/\(.*\)\.md$/\3/')
	mName=$(echo ${mName} | sed -e "s|${MD_REGEX_DATE}||g")
	
	# 에서 이미지 경로만 추출
	imgPath=$(echo "${imgTag}" | cut -d'(' -f2 | cut -d')' -f1)
	
	# 이미지 갯수 카운트 용도
	IDX=1
		
	# 이미지가 하나의 MD파일에 여러개가 업로드 되어 있음
	echo "${imgPath}" |
	while read TAG
	do
		# 이미지 하나에 대한 정보 (파일명, 확장자, 디렉토리)
		#iName=$(echo ${TAG} | awk -F'/' '{print $NF}' | cut -d'.' -f1)
		iName=$(basename ${TAG} | cut -d'.' -f1)
		iExt=$(echo ${TAG} | awk -F'/' '{print $NF}' | cut -d'.' -f2)
		iDir=$(echo ${TAG} | awk -F'/' '{print $((NF-1))}')
		
		# 이미지를 옮길 디렉토리 생성
		mkdir -p ${HOME}/${GIT}/assets/posts/images/${mCat}/${mName}
		
		# 생성한 디렉토리에 이미지를 옮기며, 이름을 변경한다.
		mv ${HOME}/${GIT}/assets/${TAG} ${HOME}/${GIT}/assets/posts/images/${mCat}/${mName}/${mName}_${IDX}.${iExt}
		
		# post md 파일에서 이미지 path 변경하기 (https://sysopt.tistory.com/79)
		sed -i "/${iDir}\/${iName}\.${iExt}/ c\\!\[${mName}_${IDX}\](\/..\/assets\/posts\/images\/${mCat}\/${mName}\/${mName}_${IDX}\.${iExt})" ${MD}
		
		IDX=$((IDX+1))
	done
	
	# 이미지 갯수 카운트 초기화
	IDX=1
done
```

<br><br>
내가 게시한 모든 post 파일에서 img tag가 있는 게시물만 loop 한다.

```shell
# 내가 만든 post md 파일
find $HOME/$GIT/*/_posts -type f -name "*.md" |
while read MD
do
	# 에서 첨부한 이미지 tag 추출
	imgTag=$(grep "\!\[" ${MD})
	if [ "x$imgTag" == "x" ]
	then
		# 이미지 tag가 없는 md파일은 스킵한다.
		continue
	fi
```

<br>
post 파일 경로는 일반적으로 다음과 같다.

`...skip...<Category>/_posts/<Filename>.md`

내 blog는 Custom을 하여, Directory 이름으로 Category를 사용한다.

여기서 Category 값을 빼내는 방식이다.

```shell
	# 에서 Category 추출 (https://linuxhint.com/sed-capture-group-examples/)
	mCat=$(echo ${MD} | sed 's/^\(.*\)\/\(.*\)\/_posts\/\(.*\)\.md$/\2/')
```

<br>
이외 makrdown 파일명을 구한다.

일반적인 Default Jekyll Blog 게시물의 경우에는, Filename 앞부분(prefix)에 date format이 있어야 한다.

나는 이 부분 또한 Custom하여 `0000-00-01` 과 같은 Simple한 Fake format으로 변경했다.

> 실제 date는 파일내부 YAML Front matter section에 있다.

그러므로 Fake format을 제거하고 구한다.

```shell
	# 에서 MD 파일명 추출 (date format string 제거)
	MD_REGEX_DATE='^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-'
	mName=$(echo ${MD} | sed 's/^\(.*\)\/\(.*\)\/_posts\/\(.*\)\.md$/\3/')
	mName=$(echo ${mName} | sed -e "s|${MD_REGEX_DATE}||g")
```

<br>
post 내에 image tag로 감싸져 있는, 실제 path를 구하고,

다음에서, Image Name_IDX 로 관리하기 위해, IDX var를 사용한다.

```shell
	# 에서 이미지 경로만 추출
	imgPath=$(echo "${imgTag}" | cut -d'(' -f2 | cut -d')' -f1)
	
	# 이미지 갯수 카운트 용도
	IDX=1
```

<br>
`<Category>/<Markdown filename>/<Makrdown filename>_<IDX>.png` 와 같이 이미지를 옮기고,

URL을 수정한다.

```shell
		# 이미지를 옮길 디렉토리 생성
		mkdir -p ${HOME}/${GIT}/assets/posts/images/${mCat}/${mName}
		
		# 생성한 디렉토리에 이미지를 옮기며, 이름을 변경한다.
		mv ${HOME}/${GIT}/assets/${TAG} ${HOME}/${GIT}/assets/posts/images/${mCat}/${mName}/${mName}_${IDX}.${iExt}
		
		# post md 파일에서 이미지 path 변경하기 (https://sysopt.tistory.com/79)
		sed -i "/${iDir}\/${iName}\.${iExt}/ c\\!\[${mName}_${IDX}\](\/..\/assets\/posts\/images\/${mCat}\/${mName}\/${mName}_${IDX}\.${iExt})" ${MD}
```

