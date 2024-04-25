---
date: 2022-02-15 12:26:08 +0900
layout: post
title: "[RHCSA] Storage 파티셔닝"
tags: [Linux, RHCSA, Storage, GPT, MBR, parted]
---


# 1. 개요

RHCSA 과정을 준비하면서, Storage 파티셔닝을 정리한다.

fdisk, gdisk 를 먼저 공부했지만, parted 가 너무 편리하여 parted로 정리한다.
{{ site.content.br_small }}
# 2. MBR / GPT

MBR과 GPT의 차이점 등은 다른 구글링으로 쉽게 찾아볼 수 있다.

아래 Section 실습에서는 MBR 이든 GPT이든 mklabel 에서만 지정하면 된다.

> 예시
>
> ```bash
> parted /dev/vdb mklabel msdos # MBR
> parted /dev/vdb mklabel gpt # GPT
> ```
>
> _너무 편리하다.._
{{ site.content.br_small }}
# 3. GPT 파티셔닝

> MBR 파티셔닝은 msdos 로 label 만 주면 되므로, GPT 로 설명한다.

## 3.1 사용 가능한 디스크 확인

```bash
# lsblk --fs
NAME   FSTYPE LABEL UUID                                 MOUNTPOINT
vda                                                     
├─vda1                                                  
├─vda2 vfat         399C-0F7D                            /boot/efi
└─vda3 xfs    root  3cd0d4ca-93f6-423b-a469-70ab2b10b667 /
vdb                                                     
vdc                                                     
vdd
```

> 새로운 디스크(HDD or SDD 등)를 붙이면 /dev/vd{a~...z} 으로 추가 된다.
{{ site.content.br_small }}
```bash
# parted /dev/vdb print
Error: /dev/vdb: unrecognised disk label
Model: Virtio Block Device (virtblk)                                     
Disk /dev/vdb: 5369MB
Sector size (logical/physical): 512B/512B
Partition Table: unknown
Disk Flags: 
```

> /dev/vdb 를 확인해보니 disk label 이 없다는 error와, Partion table이 unknown 이라는 것이 확인된다.
{{ site.content.br_small }}
## 3.2 디스크 라벨링

```
# parted /dev/vdb mklabel gpt
Information: You may need to update /etc/fstab.
```

> /dev/vdb 디스크를 GPT 라벨링
>
> _MBR일 경우 gpt -> msdos_
{{ site.content.br_small }}
```bash
# parted /dev/vdb print                                  
Model: Virtio Block Device (virtblk)
Disk /dev/vdb: 5369MB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags:

Number  Start  End  Size  File system  Name  Flags

```

> print 명령으로 GPT 라벨링 여부도 확인된다.
{{ site.content.br_small }}
## 3.3 파티션 생성

```bash
# parted /dev/vdb mkpart backup xfs 1s 2GB
Warning: You requested a partition from 512B to 2000MB (sectors 1..3906250).
The closest location we can manage is 17.4kB to 2000MB (sectors 34..3906250).
Is this still acceptable to you?
Yes/No? Yes                                                              
Warning: The resulting partition is not properly aligned for best performance:
34s % 2048s != 0s
Ignore/Cancel? Ignore                                                    
Information: You may need to update /etc/fstab.
```

> /dev/vdb 에 최초 파티션을 생성하엿다.
>
> _파티션 명: backup_
>
> __파티션 타입: xfs__
>
> _파티션 크기: 2GB_
>
> ​	_ㄴ최초 파티션이므로, 가장 최소단위 1Sector 부터 2GB 까지 설정)_
>
> ​	_ㄴ"3.2" 에서 Sector size 를 알 수 있다.__
>
> __MBR일 경우 backup -> primary(경우에 따라 extended)_
{{ site.content.br_small }}
```bash
# parted /dev/vdb print                                  
Model: Virtio Block Device (virtblk)
Disk /dev/vdb: 5369MB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags:

Number  Start   End     Size    File system  Name    Flags
 1      17.4kB  2000MB  2000MB               backup 
```

> print의 결과를 보면, 원하는 대로 생성되어 있다.
>
> _1s = 512B 라 예상되지만, 시스템은 최소 크기가 17.4kB 인듯 하다_
{{ site.content.br_small }}
```bash
# mkfs.xfs /dev/vdb1
meta-data=/dev/vdb1              isize=512    agcount=4, agsize=122070 blks
         =                       sectsz=512   attr=2, projid32bit=1
         =                       crc=1        finobt=1, sparse=1, rmapbt=0
         =                       reflink=1
data     =                       bsize=4096   blocks=488277, imaxpct=25
         =                       sunit=0      swidth=0 blks
naming   =version 2              bsize=4096   ascii-ci=0, ftype=1
log      =internal log           bsize=4096   blocks=2560, version=2
         =                       sectsz=512   sunit=0 blks, lazy-count=1
realtime =none                   extsz=4096   blocks=0, rtextents=0

# parted /dev/vdb print
Model: Virtio Block Device (virtblk)
Disk /dev/vdb: 5369MB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags:

Number  Start   End     Size    File system  Name    Flags
 1      17.4kB  2000MB  2000MB  xfs          backup
```

> 파티션의 파일 시스템 유형을 xfs로 선언하고 print로 확인한 모습
{{ site.content.br_small }}
```bash
# udevadm settle
```

> /dev/vda1 장치가 준비되는 것을 기다려주는 명령어
> 원래 윗부분(mkfs)보다 일찍 사용해야 하는데.. 자꾸 이렇게 외워버렸다.
{{ site.content.br_small }}
## 3.4 파일시스템 마운트

실제 디렉토리로 마운트 지점을 할당해야 쓸 수 있다.

```bash
# mkdir /backup
```

> 마운트 지점 디렉토리를 생성한다.
{{ site.content.br_small }}
```bash
# lsblk --fs
NAME   FSTYPE LABEL UUID                                 MOUNTPOINT
vda                                                     
├─vda1                                                  
├─vda2 vfat         399C-0F7D                            /boot/efi
└─vda3 xfs    root  3cd0d4ca-93f6-423b-a469-70ab2b10b667 /
vdb                                                     
└─vdb1 xfs          3b1e73fa-409b-459c-aeaf-8866cef00f32
vdc                                                     
vdd       
```

> /dev/vdb1 파티션의 UUID를 확인한다.
{{ site.content.br_small }}
```bash
UUID=3b1e73fa-409b-459c-aeaf-8866cef00f32 /backup xfs defaults 0 0
```

> /etc/fstab 파일에 위 내용을 추가한다.
{{ site.content.br_small }}
```bash
# systemctl daemon-reload 
```

> /etc/fstab 파일을 시스템이 다시 읽도록 한다.
{{ site.content.br_small }}
```bash
# mount /backup
# mount | grep vdb1
/dev/vdb1 on /backup type xfs (rw,relatime,seclabel,attr2,inode64,noquota)
```

> 실제 mount 가 되도록 하고, 잘 되었는지 확인하는 모습
> 이제 _systemctl reboot_ 으로 재부팅하여도 mount가 항상 되어있다.
