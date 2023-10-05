---
date: 2023-07-14 08:50:48 +0900
layout: post
title: "[WEB/Nginx] Install Nginx"
tags: [WEB, Nginx, Install]
typora-root-url: ..
---

# 1. 개요

NGINX 기본 설치 및 튜닝을 진행한다.

설치 템플릿 구조나 튜닝에 대한 부분은 전체적으로 내가 Apache 에 익숙하므로

은연히 Apache 템플릿에 맞추어질 수 있다.

<br>
# 2. 설치

## 2.1 다운로드

[여기](https://nginx.org/en/download.html) 에서 Mainline/Stable Version을 받자.

작성일 기준 [nginx-1.21.6](https://nginx.org/download/nginx-1.21.6.tar.gz)

> Mainline Version nginx-1.21.6 으로 진행한다.

<br>
## 2.2 설치

* 설치 스크립트화를 위해 만들어두었다.

```bash
SOURCE_DIR=/tmp/nginx-1.21.6
INSTALL_DIR=/usr/ssw/nginx-1.21.6

INSTALL_USERNAME=dhkim
INSTALL_GROUPNAME=dhkim

INSTALL_OPTIONS="
--prefix=${INSTALL_DIR} \
--sbin-path=${INSTALL_DIR}/sbin/nginx \
--modules-path=${INSTALL_DIR}/modules \
--conf-path=${INSTALL_DIR}/conf/nginx.conf \
--error-log-path=${INSTALL_DIR}/logs/error.log \
--http-log-path=${INSTALL_DIR}/logs/access.log \
--pid-path=${INSTALL_DIR}/logs/nginx.pid \
--lock-path=${INSTALL_DIR}/logs/nginx.lock \
--user=${INSTALL_USERNAME} \
--group=${INSTALL_GROUPNAME} \
--http-client-body-temp-path=${INSTALL_DIR}/tmp/client-body-temp \
--http-proxy-temp-path=${INSTALL_DIR}/tmp/proxy-temp \
--http-fastcgi-temp-path=${INSTALL_DIR}/tmp/fastcgi-temp \
--http-uwsgi-temp-path=${INSTALL_DIR}/tmp/uwsgi-temp \
--http-scgi-temp-path=${INSTALL_DIR}/tmp/scgi-temp \
"

PERFORMANCE_MODULE_OPTIONS="
--with-threads \
--with-file-aio \
--with-http_v2_module
"

MODULE_OPTIONS="
--with-http_ssl_module \
--with-http_realip_module \
--with-http_addition_module \
--with-http_sub_module \
--with-http_dav_module \
--with-http_flv_module \
--with-http_mp4_module \
--with-http_gunzip_module \
--with-http_gzip_static_module \
--with-http_auth_request_module \
--with-http_random_index_module \
--with-http_secure_link_module \
--with-http_degradation_module \
--with-http_slice_module \
--with-http_stub_status_module \
--with-http_xslt_module=dynamic \
--with-http_image_filter_module=dynamic \
--with-stream=dynamic \
--with-stream_ssl_module \
--with-stream_realip_module \
--with-pcre \
"

cd ${SOURCE_DIR}
make clean
./configure ${INSTALL_OPTIONS} ${PERFORMANCE_MODULE_OPTIONS} ${MODULE_OPTIONS}
make && make install
```

> http_xslt_module 을 위해 ` libxslt-devel.x86_64` 을 설치했다.
>
> http_image_filter_module 을 위해 `gd-devel.x86_64` 을 설치했다.

<br>
## 2.3 실행 커맨드

[여기](https://nginx.org/en/docs/beginners_guide.html#control)에 실행 커맨드.

<br>
```bash
$ pwd
/usr/ssw/nginx-1.21.6/sbin

$ ./nginx
nginx: [emerg] mkdir() "/usr/ssw/nginx-1.21.6/tmp/client-body-temp" failed (2: No such file or directory)

$ mkdir /usr/ssw/nginx-1.21.6/tmp
```

> nginx 기동 시 설치 옵션으로 준 tmp 디렉토리가 없다는 에러가 발생하였다.

<br>
```bash
$ ./nginx
nginx: [emerg] bind() to 0.0.0.0:80 failed (13: Permission denied)

$ sudo chown root:dhkim nginx
$ sudo chmod 4770 ./nginx
```

> 1024 이하 privileged port 이므로 권한 부여가 필요하다.

<br>
```bash
$ ./nginx
$ ps -ef | grep nginx
root       69613       1  0 10:12 ?        00:00:00 nginx:
dhkim      69614   69613  0 10:12 ?        00:00:00 nginx:
dhkim      69616    1816  0 10:12 pts/0    00:00:00 grep --color=auto nginx

$ netstat -an | grep LISTEN | grep tcp | grep 80
tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN
```

> 잘 기동이 되었다.

<br>
# 3. 튜닝

## 3.1 기본 튜닝

* nginx.conf

```bash
user dhkim dhkim;
worker_processes  auto;

pid        logs/nginx.pid;

# worker_rlimit_nofile 은 open files 개수이며, worker_connections 보다 같거나 커야 한다.
worker_rlimit_nofile 2048;
events {
    worker_connections  1024;
    
    # multi_accept : 동시에 여러 커넥션을 연결한다.
    multi_accept on;
    
    # 커넥션 연결 시 (이벤트 처리에)사용할 메서드
    use epoll;
}

http {
	log_format customformat '$remote_addr - $remote_user [$time_local] '
    	                '"$request" $status $body_bytes_sent '
        	            '"$http_referer" "$http_user_agent" '
						'[$request_time]';

    # 읽을 데이터와 쓸 데이터들을 버퍼를 거치지 않고, 직접 FD간에 주고받아 성능을 올린다.
    sendfile on;
    
    # sendfile on 필요. 패킷을 바로 보내지 않고, 최대크기(MSS) 를 채운뒤 보내므로 트래픽 감소 효과.
    tcp_nopush on;
    
    # slow network system에서 패킷 안정성을 위해, 200ms 지연 알고리즘이 구현되어 있다.
    # tcp_nodelay on 옵션으로, 200ms 지연을 제거하여 더 빠르게 응답한다.
    tcp_nodelay on;
    
    # 시간초과하여 닫을 커넥션을 빠르게 닫는다. FIN_WAIT 지연을 없애준다.
    reset_timedout_connection on;
    
    # client -> nginx timeout
    client_body_timeout 10;
    # nginx -> client timeout
    send_timeout 5;
    keepalive_timeout 20;
    
    # keepalive 연결 커넥션 수이며, 최대 도달해야 IDLE 커넥션을 closed 한다.
    # 큰 수치일 경우, 최대 도달 전까지 메모리 사용량이 늘어날 수 있다.
    keepalive_requests 500;
    
    server_tokens off;

    include       mime.types;
    default_type  application/octet-stream;

    # root 기본값은 html 임을 명심한다.
    root /usr/ssw/nginx-1.21.6/html;

    server {
        listen       80;
        server_name  test.dhkim.com alias.dhkim.com;
        
        error_log  logs/error-test.dhkim.com.log  info;
        access_log logs/access-test.dhkim.com.log customformat;
        
        # Header의 Content-Type에 해당 값을 추가한다. off면 추가하지 않는다.
        charset utf8;
        
        # /testapp 으로 시작하는 URI는 htdocs 아래에서 찾는다.
        location /testapp {
            root /usr/ssw/nginx-1.21.6/htdocs;
            index index.html index.html;
            
            # GET/POST 외에 모두 금지
            limit_except GET POST {
                deny all;
            }
        }
        
        error_page 403 404 /40x.html;
        location = /40x.html {
            root /usr/ssw/nginx-1.21.6/htdocs/testapp/errors;
        }
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/ssw/nginx-1.21.6/htdocs/testapp/errors;
        }
    }
}
```

<br>
## 3.2 Log Rotation

[링크](https://www.nginx.com/resources/wiki/start/topics/examples/logrotation/)를 참고하여 스크립트화.

<br>
```bash
#!/bin/bash

# reopen 시에 소유자가 user 설정 값과 동일하게 변경된다.
# reopen 기능이 있지만, 소유자를 변경하기 위해서만 사용한다.
/usr/ssw/nginx-1.21.6/sbin/nginx -s reopen

LOG_DIR=/usr/ssw/nginx-1.21.6/logs
ls -l ${LOG_DIR}/*.log | awk '{print $NF}' | \
while read LINE;
do
	cp ${LINE} ${LINE}.$(date "+%Y%m%d_%H%M%S")
	cat /dev/null > ${LINE}
done
```

> LOG_DIR 디렉토리 내에 *.log 파일들만 대상으로 한다.
>
> 기존 쓰기 중인 파일은, backup copy 하고, null copy 로 마무리한다.
>
> ___이후 해당 스크립트를 고도화하고, 크론탭으로 설정하면 되겠다___

<br>
## 3.3 mod_proxy

작성이 필요하나~ 외부 일정으로 인해 차후 기입.

