---
date: 2022-11-29 18:03:31 +0900
layout: post
title: "[Typora] 포스트 이미지 깔끔하게 정리"
tags: [Typora, Shell, Bash, Script, Image, Assets, Sort]
typora-root-url: ..
---


# 1. 개요

Post (.md) 작성을 해오면서, 다양한 jekyll theme 도 적용해보고

이에 따라 디렉토리나 이미지들이 지저분하게 보관이 되어왔다.
{{ site.content.br_small }}
이번 기회에, Post 파일에서 사용되지 않는 Garbage 이미지 파일을 찾아 삭제하고

> 해당 부분은 [NotUsedImageCleaner](NotUsedImageCleaner) 에서 다룬다.
{{ site.content.br_small }}
assets/img 아래에 저장되는 이미지들을 assets/posts/images 으로 이동시키고, 이동된 정보를 모든 Post를 수정해보도록 한다.

> 굳이 옮기지 않아도 되지만, 향후 Post 관련 디렉토리를 좀 더 체계적으로 관리하기 위함.
{{ site.content.br_small }}
# 2. Script

## 2.1 ImageLinkSorter.sh

```shell
#!/usr/bin/bash

# _posts md 파일 내에 삽입된 이미지 링크 경로를 올바르게 수정해준다.
# 실제 존재하는 이미지인지 여부와 관계없이, assets/posts/images 로 고정해준다.

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
	
	# 에서 이미지 경로만 추출
	imgPath=$(echo "${imgTag}" | cut -d'(' -f2 | cut -d')' -f1)
	
	# 이미지가 하나의 MD파일에 여러개가 업로드 되어 있음
	echo "${imgPath}" |
	while read TAG
	do
		# 이미지 하나에 대한 정보 (파일명, 확장자, 디렉토리)
		iName=$(echo ${TAG} | awk -F'/' '{print $NF}' | cut -d'.' -f1)
		iExt=$(echo ${TAG} | awk -F'/' '{print $NF}' | cut -d'.' -f2)
		iDir=$(echo ${TAG} | awk -F'/' '{print $((NF-1))}')
		
		# 이미지를 기존 assets/img 가 아닌 새로운 경로로 옮기는 작업 (일회성 실행)
		#mkdir -p ${HOME}/${GIT}/assets/posts/images/${iDir}
		#mv ${HOME}/${GIT}/assets/img/${iDir}/${iName}.${iExt} ${HOME}/${GIT}/assets/posts/images/${iDir}/${iName}.${iExt}
		
		# post md 파일에서 이미지 path 변경하기 (https://sysopt.tistory.com/79)
		sed -i "/${iDir}\/${iName}\.${iExt}/ c\\!\[${iName}\](\/..\/assets\/posts\/images\/${mCat}\/${iDir}\/${iName}\.${iExt})" ${MD}	
	done
done
```
{{ site.content.br_small }}
## 2.2 Description

Script의 Part 별로 어떤 역할인지 설명한다.
{{ site.content.br_small }}
내가 그동안 작성해온 모든 Post (.md) 파일들만 작업 대상이므로,

선별한다.

```shell
# 내가 만든 post md 파일
find $HOME/$GIT/*/_posts -type f -name "*.md" |
while read MD
```
{{ site.content.br_small }}
image markdown (`![이름](이미지 파일경로)`) 가 포함된 Post 파일만 찾는다.

```shell
	# 에서 첨부한 이미지 tag 추출
	imgTag=$(grep "\!\[" ${MD})
	if [ "x$imgTag" == "x" ]
	then
		# 이미지 tag가 없는 md파일은 스킵한다.
		continue
	fi
```
{{ site.content.br_small }}
나의 post 게시물들은 `07.typora` 와 같이 디렉터리를 만들어, 마치 카테고리처럼 관리한다.

구조가 default jekyll blog 와 달라서 필요한 변수이다.

디렉토리 구조중에, 카테고리로 분류되는 지점을 변수화 해준다.

```shell
	# 에서 Category 추출 (https://linuxhint.com/sed-capture-group-examples/)
	mCat=$(echo ${MD} | sed 's/^\(.*\)\/\(.*\)\/_posts\/\(.*\)\.md$/\2/')
```
{{ site.content.br_small }}
image markdown 에서 `(이미지 파일경로)` 부분만 추출한다. 이름은 가변적이기 때문에 필요없다.

	# 에서 이미지 경로만 추출
	imgPath=$(echo "${imgTag}" | cut -d'(' -f2 | cut -d')' -f1)
{{ site.content.br_small }}
1개 Post 파일에도 여러 image markdown 이 존재할 수 있으므로, loop 를 생성한다.

```shell
	# 이미지가 하나의 MD파일에 여러개가 업로드 되어 있음
	echo "${imgPath}" |
	while read TAG
	do
```
{{ site.content.br_small }}
앞에서 구한 실제 image file의 정보를 가지고, 여러 단계로 변수화한다.

```shell
		# 이미지 하나에 대한 정보 (파일명, 확장자, 디렉토리)
		iName=$(echo ${TAG} | awk -F'/' '{print $NF}' | cut -d'.' -f1)
		iExt=$(echo ${TAG} | awk -F'/' '{print $NF}' | cut -d'.' -f2)
		iDir=$(echo ${TAG} | awk -F'/' '{print $((NF-1))}')
```
{{ site.content.br_small }}
이 부분은, 말머리에 언급한 기존 `assets/img` 에 업데이트 되는 이미지를 앞으로는 `assets/posts/images` 로 경로 변경을 위해 실행한 코드 조각이다.

직접 윈도우 상에서 디렉토리 복제를 하지 않은 이유는, Post에 사용되고 있지 않은 Garbage file을 한번 여기서 걸러내기 위함이다.

```shell
		# 이미지를 기존 assets/img 가 아닌 새로운 경로로 옮기는 작업 (일회성 실행)
		#mkdir -p ${HOME}/${GIT}/assets/posts/images/${iDir}
		#mv ${HOME}/${GIT}/assets/img/${iDir}/${iName}.${iExt} ${HOME}/${GIT}/assets/posts/images/${iDir}/${iName}.${iExt}
```
{{ site.content.br_small }}
sed Pattern 검색 기능을 이용해서, 이미지 파일명으로 변경이 필요한 Line을 수정한다.

```shell
		# post md 파일에서 이미지 path 변경하기 (https://sysopt.tistory.com/79)
		sed -i "/${iDir}\/${iName}\.${iExt}/ c\\!\[${iName}\](\/..\/assets\/posts\/images\/${mCat}\/${iDir}\/${iName}\.${iExt})" ${MD}	
	done
done
```
{{ site.content.br_small }}
