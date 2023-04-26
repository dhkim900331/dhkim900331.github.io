---
date: 2022-02-15 12:26:08 +0900
layout: post
title: "[RHCSA] Container 생성"
tags: [Linux, RHCSA]
---


# 1. 개요

podman 을 이용한 Container 생성과 비-루트 계정으로 서비스를 등록해본다.



# 2. 컨테이너 생성

## 2.1 이미지 검색

```0
# podman search docker.io/httpd
INDEX       NAME                                              DESCRIPTION                                       STARS   OFFICIAL   AUTOMATED
docker.io   docker.io/library/httpd                           The Apache HTTP Server Project                    3802    [OK]
docker.io   docker.io/centos/httpd-24-centos7                 Platform for running Apache httpd 2.4 or bui...   40
docker.io   docker.io/manageiq/httpd                          Container with httpd, built on CentOS for Ma...   1                  [OK]
docker.io   docker.io/clearlinux/httpd                        httpd HyperText Transfer Protocol (HTTP) ser...   1
... skip ...
```

> 사용할(띄울) 이미지를 검색한다.
>
> 여기서는 httpd 에서 가장 낮은 버전(아무거나) 을 활용한다.



```bash
# skopeo inspect docker://docker.io/library/httpd
{
    "Name": "docker.io/library/httpd",
    "Digest": "sha256:0c8dd1d9f90f0da8a29a25dcc092aed76b09a1c9e5e6e93c8db3903c8ce6ef29",
    "RepoTags": [
        "2",
        "2-alpine",
        "2-alpine3.13",
        "2-alpine3.14",
        "2-alpine3.15",
        "2-bullseye",
        "2-buster",
... skip ...
```

> inspect 명령을 사용하여 찾은 이미지에서 포함된 릴리즈들을 모두 확인할 수 있다.
>
> 우리는 2-alpine3.15 를 아래에서 사용하기로 하자.



## 2.2 이미지 다운로드

```bash
# podman pull docker.io/library/httpd:"2-alpine3.14"
```



## 2.3 컨테이너 실행

```bash
# mkdir /html
# echo "Hello World" > /html/index.html
```

> 옵션으로, 호스트 디렉토리를 컨테이너에게 전달하기 위한 환경



```bash
# podman run --detach --name "myweb" -p "8080:80" -v "/html:/usr/local/apache2/htdocs:Z" -e "BLOGGER=DHKIM" -e "GIT=dhkim900331" docker.io/library/httpd
```

> __--detach : 백그라운드 실행_
>
> _--name : 컨테이너 명_
>
> _-p : 호스트 8080 port를 컨테이너 80 port로 forwarding_
>
> _-v : 호스트 /html 디렉토리를 컨테이너의 /usr/.../htdocs 디렉토리로 연결_
>
> _  ㄴ Z 옵션은 SELinux 옵션. 주지 않으면 SELinux policy 다를 경우 권한 문제 발생_
>
> _-e : 환경 변수를 key:value pair로 전달__
>
> 마지막 argument는 아까 받은 이미지



```bash
# podman ps -a
CONTAINER ID  IMAGE                           COMMAND           CREATED        STATUS            PORTS                 NAMES
3c6ad1ea13e3  docker.io/library/httpd:latest  httpd-foreground  3 minutes ago  Up 3 minutes ago  0.0.0.0:8080->80/tcp  myweb
```

> 컨테이너 실행 중인 상태(STATUS를 보고 판단)



```bash
# podman exec -it myweb /bin/bash
root@3c6ad1ea13e3:/usr/local/apache2# hostname
3c6ad1ea13e3
```

> 컨테이너 내부로 접속하여 hostname 명령을 쳐보았다.



# 3. 비-루트 계정 서비스 등록

* 여기서부터는 비-루트 계정으로 로그인하면서 진행한다.

  * 앞서 컨테이너 생성 시 아래에서 사용할 계정과 다르면 컨테이너를 지우고 여기 계정으로 다시 생성한다.

* systemctl --user 옵션을 사용한다.

  * 반드시 ssh <user>@<host> 방식으로 로그인 해야한다.

  * 그렇지 않으면 다음 처럼 bus에 연결하지 못한다.

    ```bash
    # systemctl --user
    Failed to connect to bus: 그런 파일이나 디렉터리가 없습니다
    ```



```bash
# ssh test@localhost
```

> 컨테이너를 일반계정 test 에 서비스 등록하기 위하여 ssh 로그인



```bash
# mkdir -p ~/.config/systemd/user
# podman generate systemd myweb --new > ~/.config/systemd/user/container-myweb.service
```

> 현재 실행중인 myweb 컨테이너를 service 파일로 생성



```bash
# podman stop myweb
# podman rm myweb
# systemctl --user enable --now container-myweb.service
```

> myweb 컨테이너를 정지/삭제 하고,
>
> user 서비스를 재부팅 시 자동 시작되도록 및 지금 당장 시작하도록 설정한다.
