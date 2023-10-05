---
date: 2022-02-15 12:26:08 +0900
layout: post
title: "[RHCSA] LVM 확장"
tags: [Linux, RHCSA]
---

<br># 1. 개요

특정 마운트 지점의 공간이 부족하다는 가정하에

확장 방법을 알아본다.

<br>
# 2. 설명

## 2.1 현재 상황

```bash
# df -h /data
Filesystem                               Size  Used Avail Use% Mounted on
/dev/mapper/servera_01_vg-servera_01_lv  395M   24M  372M   6% /data
```

> /data Total Size가 395MB 이다.

<br>
```bash
# mount | grep /data
/dev/mapper/servera_01_vg-servera_01_lv on /data type xfs (rw,relatime,seclabel,attr2,inode64,noquota)
```

> _/dev/mapper/servera_01_vg-servera_01_lv_ 장치명도 확인을 하였다.
>
> 이 부분은 그냥 쳐본거지, 여기서 얻어야만 하는 정보는 없다.

<br>
/data 의 총 크기를 최소 700MB로 만들기 위해서는 **_대략 400MB_**를 추가 할당해주어야 한다.

<br>
## 2.2 볼륨 그룹 확장과 추가 파티셔닝

```bash
# lvdisplay
  --- Logical volume ---
  LV Path                /dev/servera_01_vg/servera_01_lv
  LV Name                servera_01_lv
  VG Name                servera_01_vg
  LV UUID                SKBNR5-5EJc-k2U1-B5tB-hC6y-Je6W-myzhUV
  LV Write Access        read/write
  LV Creation host, time servera.lab.example.com, 2021-12-09 00:24:30 -0500
  LV Status              available
  # open                 1
  LV Size                400.00 MiB
  Current LE             100
  Segments               2
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     8192
  Block device           253:0
```

> /data 가 마운트된 장치의 논리볼륨(LV)은 _servera_01_vg_ 볼륨 그룹에서 할당되었다.

<br>
```bash
# vgdisplay servera_01_vg
  --- Volume group ---
  VG Name               servera_01_vg
  System ID             
  Format                lvm2
  Metadata Areas        2
  Metadata Sequence No  2
  VG Access             read/write
  VG Status             resizable
  MAX LV                0
  Cur LV                1
  Open LV               1
  Max PV                0
  Cur PV                2
  Act PV                2
  VG Size               504.00 MiB
  PE Size               4.00 MiB
  Total PE              126
  Alloc PE / Size       100 / 400.00 MiB
  Free  PE / Size       26 / 104.00 MiB
  VG UUID               sNogVl-KWL2-F4UZ-C3s6-KJaj-LPrV-zVwGEr
```

> 해당 볼륨 그룹의 정보.
>
> Free Size가 104MB이므로 300MB 정도를 더 확장해야 한다.
>
> 여기 Free Size가 충분했다면 볼륨 그룹 확장이 필요 없다.

<br>
```bash
# parted /dev/vdb print                                 
Model: Virtio Block Device (virtblk)
Disk /dev/vdb: 5369MB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags:

Number  Start   End    Size   File system  Name     Flags
 1      1049kB  269MB  268MB               primary  lvm
 2      271MB   539MB  268MB               primary  lvm
```

> 디스크 장치 크기는 5369MB로 여유가 있다.

<br>
```bash
# parted /dev/vdb mkpart primary 540MB 900MB
# parted /dev/vdb set 3 lvm on
# udevadm settle
```

> 추가로 파티션을 생성하엿다.

<br>
```bash
# parted /dev/vdb print                                 
Model: Virtio Block Device (virtblk)
Disk /dev/vdb: 5369MB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags:

Number  Start   End    Size   File system  Name     Flags
 1      1049kB  269MB  268MB               primary  lvm
 2      271MB   539MB  268MB               primary  lvm
 3      540MB   900MB  360MB               primary  lvm
```

<br>
```bash
# pvcreate /dev/vdb3
# vgextend servera_01_vg /dev/vdb3
```

> /dev/vdb3 장치를 볼륨으로 만들고, 기존 _servera_01_vg_ 그룹에 할당하였다.

<br>
```bash
# vgdisplay
  --- Volume group ---
  VG Name               servera_01_vg
  System ID             
  Format                lvm2
  Metadata Areas        3
  Metadata Sequence No  3
  VG Access             read/write
  VG Status             resizable
  MAX LV                0
  Cur LV                1
  Open LV               1
  Max PV                0
  Cur PV                3
  Act PV                3
  VG Size               844.00 MiB
  PE Size               4.00 MiB
  Total PE              211
  Alloc PE / Size       100 / 400.00 MiB
  Free  PE / Size       111 / 444.00 MiB
  VG UUID               sNogVl-KWL2-F4UZ-C3s6-KJaj-LPrV-zVwGEr
```

> Free Size가 444 MB로 크게 늘어났다.

<br>
## 2.3 논리 볼륨 확장

```bash
# lvextend -L 700MB -n /dev/servera_01_vg/servera_01_lv
```

> _700MB_는 추가할 사이즈가 아니라, 최종 사이즈다.
>
> 명령어로 가상 디스크 장치(LV)를 확장한다.

<br>
```bash
# xfs_growfs /data
```

> 해당 명령어로 새롭게 늘어난 비어있는 공간을 xfs로 채워넣는다.
>
> _**ext4 의 경우에는 resize2fs 를 사용한다.**_

<br>
```bash
# df -h /data
Filesystem                               Size  Used Avail Use% Mounted on
/dev/mapper/servera_01_vg-servera_01_lv  695M   26M  670M   4% /data
```

> 695MB로 많이 늘어났다~~

