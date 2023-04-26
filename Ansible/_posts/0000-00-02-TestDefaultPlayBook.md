---
layout: post
title: "[Ansible/2.9] 기본 playbook 테스트"
tags: [Ansible, Install, playbook]
date: 2022-02-15 12:37:56 +0900
---


# 1. 개요
Ansible installation 후에 Sample Playbook testing.


# 2. 테스트
hosts 파일에 테스트용 VM 을 나열하고,
/tmp 에 디렉토리 생성 playbook
/tmp 에 생성한 디렉토리 삭제 playbook
위 playbook 을 all-in-one 으로 만드는 import playbook
총 3가지 테스트한 파일

[20210803.tar.gz](/assets/upload/20210803.tar.gz)