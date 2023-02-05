---
date: 2022-12-02 08:52:18 +0900
layout: post
title: "[Typora] 불필요한 이미지 리소스 제거"
tags: [Typora, shell, bash, script, linux, image, assets, remove]
typora-root-url: ..
---


# 1. 개요

Post (md) 파일에서 link 되지 않아

사용되고 있지 않는 image 를 일괄 제거해본다.





# 2. ImageGC.sh

```shell
#!/usr/bin/bash

# 사용하지 않은 이미지 들을 추적하여 제거한다.

BASEDIR=$(dirname "$0")
. ${BASEDIR}/env.sh

# post에 사용되었을 것으로 예상되는 이미지 파일
find $HOME/$GIT/assets/img $HOME/$GIT/assets/posts/images \
	-type f -name "*.jpg" -o -name "*.png" | grep -v "favicons" |
while read IMG
do
	# 이미지 하나에 대한 정보 (파일명, 확장자, 디렉토리)
	iName=$(echo ${IMG} | awk -F'/' '{print $NF}' | cut -d'.' -f1)
	iExt=$(echo ${IMG} | awk -F'/' '{print $NF}' | cut -d'.' -f2)
	iDir=$(echo ${IMG} | awk -F'/' '{print $((NF-1))}')

	# post 에서 image 검색
	EXIST=$(find $HOME/$GIT/*/_posts -type f -name "*.md" | xargs grep "${iDir}/${iName}.${iExt}")
	
	# EXIST length 값 비교로 image 사용 여부 확인
	if [ "${#EXIST}" == "0" ]
	then
		echo "Image not used: ${iDir}/${iName}.${iExt}"
		/usr/bin/rm $IMG
	else
		echo "Image used: ${iDir}/${iName}.${iExt}"
	fi
done
```

