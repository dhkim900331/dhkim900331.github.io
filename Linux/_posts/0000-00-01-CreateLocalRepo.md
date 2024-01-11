---
date: 2022-04-11 12:01:17 +0900
layout: post
title: "[Linux/Repository] Create Local Repository"
tags: [OS, Linux, Repository, Local]
typora-root-url: ..
---

# 1. 개요

고객사에 Apache 설치를 위해 OS Package가 사전 설치되어 있어야 하나, 폐쇄망으로 인하여 직접 Package를 설치해야 되는 상황이 발생하였다.

Linux Image를 마운트하여 직접 Package를 구성해보자.



# 2. Local Repo 구성

### 2.1 Image Upload

* 고객사와 같이 테스트 환경은 CentOS 7.4.1708 이미지다.
* 해당 이미지를 구할 수 있는 미러는 많으나, 오래된 자료라 Not Found 또는 다운로드 속도 지연 문제로 토렌트로 받을수는 있었다.
* 다음과 같이 받은 DVD (Full image) 파일을 특정 경로에 업로드 한다.

```bash
$ ls -rtl /root
-rw-r--r--. 1 root root 4521459712  4월  6 09:31 CentOS-7-x86_64-DVD-1708.iso
-rw-------. 1 root root       1277  4월  6 09:55 anaconda-ks.cfg
```



### 2.2 Image Mount

```bash
$ mkdir /mnt_centos7.4 # 이미 있는 '/mnt' 를 사용해도 된다. 필수로 새로 만들 필요는 없다.
$ mount -o loop CentOS-7-x86_64-DVD-1708.iso /mnt_centos7.4
```

> loop는 block device 장치를 뜻한다. (루프백)
> 일반 파일(iso)을 장치처럼 접근가능하게 하기 위해 부여하는 옵션이다.



### 2.3 기존 Repository 비활성화

* 폐쇄망이나, 기본으로 Enabled 되어 있는 기존 Repo 목록들을 Disabled 해두어야 yum 설치 시 불필요한 접근을 하지 않겠다.

```bash
$ yum repolist enabled # 명령으로 enabled 항목 확인
$ yum-config-manager --disable "disabled 전환할 repo id"
```



### 2.4 Local Repo 생성 및 활성화(자동)

```bash
$ yum-config-manager --add-repo "file:///mnt_centos7.4"

$ cat << EOF > /etc/yum.repos.d/mnt_centos7.4.repo
[mnt_centos7.4]
name=added from: file:///mnt_centos7.4
baseurl=file:///mnt_centos7.4
enabled=1
EOF

$ yum repolist enabled
mnt_centos7.4              added from: file:///mnt_centos7.4              3,894
```



Local repo에서 이미지 검색하는 것이 확인되면, 잘 끝났다.

```bash
$ yum list gcc
Loaded plugins: fastestmirror
Loading mirror speeds from cached hostfile
Installed Packages
gcc.x86_64             4.8.5-16.el7          @mnt_centos7.4
```



위 단계에서, repomd.xml 파일을 찾지 못하는 에러가 발생한다면,

```
Error: Failed to download metadata for repo 'mnt_centos7.4': Cannot download repomd.xml: Cannot download repodata/repomd.xml: All mirrors were tried
```



repo 파일의 baseurl을 다음과 같이 BaseOS, AppStream 존재하는 디렉토리 별로 구성해주어야 한다.

```repo
[mnt_os_base]
name=added from: file:///mnt_os
baseurl=file:///mnt_os/BaseOS
enabled=1

[mnt_os_stream]
name=added from: file:///mnt_os
baseurl=file:///mnt_os/AppStream
enabled=1
```

