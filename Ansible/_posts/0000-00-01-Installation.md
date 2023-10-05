---
date: 2022-02-15 12:37:56 +0900
layout: post
title: "[Ansible/2.9] Installation"
tags: [Ansible, Install]
---

<br># 1. 개요

Ansible installation

<br>
---

# 2. 설치

CentOS Version

```bash
$ cat /etc/*release
CentOS Stream release 8
NAME="CentOS Stream"
VERSION="8"
ID="centos"
ID_LIKE="rhel fedora"
VERSION_ID="8"
PLATFORM_ID="platform:el8"
PRETTY_NAME="CentOS Stream 8"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:centos:centos:8"
HOME_URL="https://centos.org/"
BUG_REPORT_URL="https://bugzilla.redhat.com/"
REDHAT_SUPPORT_PRODUCT="Red Hat Enterprise Linux 8"
REDHAT_SUPPORT_PRODUCT_VERSION="CentOS Stream"
CentOS Stream release 8
CentOS Stream release 8
```

<br>
참고하여 CentOS 8에  설치 하였다.

> _<https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#installing-ansible-on-rhel-centos-or-fedora>_

<br>
Oralce Linux 7 VM은 다음 링크

> _<https://blogs.oracle.com/scoter/ansible-with-oracle-linux-virtualization-manager-olvm>_

<br>
각각 VM에 다음 링크 대로 적용하여 nopass 설정하였다.

ansible 이 각 VM 에 명령어 실행 시, password 인자를 줄 수 있지만,

이번 설치 및 테스트 환경에서는 nopass 설정을 하였다.

> _<https://devfon.tistory.com/31>_

<br>
/etc/ansible 에 설치완료