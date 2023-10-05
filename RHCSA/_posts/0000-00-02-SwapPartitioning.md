---
date: 2022-02-15 12:26:08 +0900
layout: post
title: "[RHCSA] Swap 파티셔닝"
tags: [Linux, RHCSA, Swap, GPT, MBR, parted]
---

<br># 1. 개요

RHCSA 과정을 준비하면서, Swap파티셔닝을 정리한다.

fdisk, gdisk 를 먼저 공부했지만, parted 가 너무 편리하여 parted로 정리한다.

<br>
_Swap이 아닌 일반 스토리지는 [여기를 클릭]({{ site.url }}/rhcsa/StoragePartitioning)_

<br>
# 2. Swap

일반 스토리지 단계에서부터 이어서 진행한다.

<br>
```bash
# parted /dev/vdb print
Model: Virtio Block Device (virtblk)
Disk /dev/vdb: 5369MB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags:

Number  Start   End     Size    File system  Name    Flags
 1      17.4kB  2000MB  2000MB  xfs          backup
```

> 현재 장치 정보는 위와 같은 상태

<br>
## 2.1 파티션 생성

```bash
# parted /dev/vdb mkpart swap1 linux-swap 2001MB 2513MB
Information: You may need to update /etc/fstab.

# parted /dev/vdb mkpart swap2 linux-swap 2514MB 3026MB
Information: You may need to update /etc/fstab.
```

> swap1, swap2 이름의 linux-swap 속성, 각각 512MB 크기를 2개 만들었다.

<br>
```bash
# parted /dev/vdb print                                  
Model: Virtio Block Device (virtblk)
Disk /dev/vdb: 5369MB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags:

Number  Start   End     Size    File system  Name    Flags
 1      17.4kB  2000MB  2000MB  xfs          backup
 2      2001MB  2513MB  513MB                swap1   swap
 3      2514MB  3026MB  512MB                swap2   swap
```

> print로 확인

<br>
``` bash
# udevadm settle 
```

> 여기서는 헷갈리지 않고 해당 명령어를 잘 사용했다 ^^

<br>
```bash
# mkswap /dev/vdb2
Setting up swapspace version 1, size = 489 MiB (512749568 bytes)
no label, UUID=52c19f22-9abe-4e8a-94ac-bb6689e18e4b

# mkswap /dev/vdb3
Setting up swapspace version 1, size = 488 MiB (511700992 bytes)
no label, UUID=00eb7f1a-1082-49cb-bd04-8b1d8a48e7a4 
```

> 파일 시스템을 swap으로 잘 지정하였다.
>
> 여기도 UUID를 잘 어딘가에 기록해둔다.

<br>
```bash
# parted /dev/vdb print
Model: Virtio Block Device (virtblk)
Disk /dev/vdb: 5369MB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags:

Number  Start   End     Size    File system     Name    Flags
 1      17.4kB  2000MB  2000MB  xfs             backup
 2      2001MB  2513MB  513MB   linux-swap(v1)  swap1   swap
 3      2514MB  3026MB  512MB   linux-swap(v1)  swap2   swap 
```

> print로 swap 까지 잘 확인되는 모습

<br>
## 2.2 Swap 활성화

```bash
UUID=52c19f22-9abe-4e8a-94ac-bb6689e18e4b swap swap defaults 0 0
UUID=00eb7f1a-1082-49cb-bd04-8b1d8a48e7a4 swap swap pri=10 0 0
```

> /etc/fstab 으로 영구적으로 활성화 할 수 있게 설정한다.
>
> pri=10은 가장 먼저 사용하는 우선순위 개념.

<br>
```bash
# swapon --show
# swapon /dev/vdb2
# swapon /dev/vdb3
# swapon --show
NAME      TYPE      SIZE USED PRIO
/dev/vdb2 partition 489M   0B   -2
/dev/vdb3 partition 488M   0B   -3
```

> _1: show 명령으로 활성화된 swap이 있는지 살펴보지만 없다._
>
> __2-3: 각각 장치를 활성화하였다._
>
> _4-7: 정상적으로 활성화되었다고 확인된다._
>
> /dev/vdb3 의 PRIO는 -3을 나온다. reboot 해야 적용된다.

<br>
```bash
# systemctl reboot
...

# swapon --show
NAME      TYPE      SIZE USED PRIO
/dev/vdb3 partition 488M   0B   10
/dev/vdb2 partition 489M   0B   -2

# free -h
total        used        free      shared  buff/cache   available
Mem:          1.8Gi       177Mi       1.4Gi        16Mi       188Mi       1.5Gi
Swap:         976Mi          0B       976Mi
```

> 시스템 reboot 이후 swap 활성화가 잘 되어 있으며, 메모리에도 잘잡힌다.
