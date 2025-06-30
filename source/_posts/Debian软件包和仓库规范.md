---
title: Debian软件包和仓库规范
date: 2025-04-11
tags:
    - Linux
---

## 版本号


[ deb-version(5)](https://manpages.debian.org/wheezy/dpkg-dev/deb-version.5.en.html)



[ Debian Policy Manual](https://www.debian.org/doc/debian-policy/ch-controlfields.html#standards-version)



### 版本命名格式


```plain
[epoch:]upstream-version[-debian-revision]
```



### epoch


组成元素:



```plain
0-9
```



使用规则:



一般默认省略，省略时默认为0，且一般是一个单独的无符号整数



### upstream-version


组成元素



```plain
0-9
a-z
A-Z
.
+
-
:
~
```



特殊符号使用规则:



如果没有epoch那么不能用`:`



如果没有debian-revision那么不能用`-`



`~`用来标注预先的版本，比如`1.0~beta1~test123`小于`1.0~beta1`小于`1.0`



### debian-revision


组成元素



```plain
0-9
a-z
A-Z
+
.
~
```



### 比较规则


首先比较epoch，然后比较upstream-version，然后比较debian-revision



epoch直接比较数字大小就行



upstream-version和debian-revision的比较算法则比较特殊，会从左到右，遇到数字字符串就一块拿出来，遇到非数字字符也一块拿出来，然后比较，直到把所有的拿出完或者比较出结果。数字字符是直接比数字大小，非数字字符的比较方式如下：



基于ASCII码表，但是有一些修改：



+ `~`小于任何值，甚至比空字符还小
+ 字母小于任何特殊符号（除了`~`）



比如：



`~~` < `~~a` < `~` < 空字符 < `a`



举个例子



12as.d54  和 12asd33



第一步：取出数字12和12比，相等，继续下一步



第二步：取出非数字as.d和asd比，其中比到第三个字符.比d大，所以左边大，结束



### 正则匹配版本号是否规范


Python



```python
import re
rule=r"^(?:[0-9]+:)?[0-9][0-9a-zA-Z\.~+]*(?:-[0-9a-zA-Z\.+~]+)?$"
version="1:2.1.~31a-1be.ta4a+es"
res=re.fullmatch(rule,version)
if res:
    print(res[0])
else:
    print("不匹配")
```



C



```c
#include<stdio.h>                                                                                                        
#include<regex.h>
int if_version(char *version){
    char *pattern ="^([0-9]+:)?[0-9][0-9a-zA-Z\\.~+]*(-[0-9a-zA-Z\\.+~]+)?$";
    regex_t reg;
    int res;
    if(regcomp(&reg,pattern,REG_EXTENDED) < 0){
        return 0;
    }
    res = regexec(&reg,version,0,NULL,0);
    if(res != REG_NOERROR){
        return 0;
    }
    return 1;
}

int main(){
    char *version = "1:1.01a~23-1-beta1";
    if(if_version(version)){
        printf("ok\n");
    }
    else{
        printf("not match\n");
    }
    return 0;
}
```



### 正则获取epoch、upstream-version、debian-revision


Python



```python
import re
def get_parts_of_the_version(version):
    rule=r"^([0-9]+:)?([0-9][0-9a-zA-Z\.~+]*)(-[0-9a-zA-Z\.+~]+)?$"
    res=re.findall(rule,version)
    if res:
        res=res[0]
        epoch=res[0]
        upstream_version=res[1]
        debian_revision=res[2]
    else:
        print("不符合规范")
get_parts_of_the_version("2.1.~31a-1be.ta4a+es-1")
```



## 包名


[https://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-source](https://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-source)



### 原文


```plain
Package names (both source and binary, see Package) must consist only of lower case letters (a-z), digits (0-9), plus (+) and minus (-) signs, and periods (.). They must be at least two characters long and must start with an alphanumeric character.
```



### 组成元素和命名规范


```plain
0-9
a-z
+
-
.
```



+ 必须以字母或数字开头
+ 长度至少为2，包括2



### 正则匹配包名


Python:



```python
import re
def if_package_name(package_name):
    rule=r"^[0-9a-z][0-9a-z\\.+-]+$"
    res=re.fullmatch(rule,package_name)
    if res:
        print(res[0])
    else:
        print("不匹配")
package_name="python3"
if_package_name(package_name)
```



C



```c
#include<stdio.h>                                                                                                        
#include<regex.h>
int if_package_name(char *package_name){
    char *pattern ="^[0-9a-z][0-9a-z\\.+-]+$";
    regex_t reg;
    int res;
    if(regcomp(&reg,pattern,REG_EXTENDED) < 0){
        return 0;
    }
    res = regexec(&reg,package_name,0,NULL,0);
    if(res != REG_NOERROR){
        return 0;
    }
    return 1;
}

int main(){
    char *package_name = "python3";
    if(if_package_name(package_name)){
        printf("ok\n");
    }
    else{
        printf("not match\n");
    }
    return 0;
}
```



## sources.list


[https://wiki.debian.org/SourcesList](https://wiki.debian.org/SourcesList)



通常是如下格式



```plain
deb http://site.example.com/debian distribution component1 component2 component3
deb-src http://site.example.com/debian distribution component1 component2 component3
```



`sources.list` 是 Debian 系统中用于配置 APT 软件包管理器的源列表文件。该文件位于 `/etc/apt` 目录下，用于指定从哪些软件源获取软件包和更新。



每行的内容表示一个软件源，其中可能包含以下几个字段：



1. `deb` 或 `deb-src`：指定该行是用于获取二进制软件包或源代码软件包的源。 
    - `deb` 表示获取二进制软件包。
    - `deb-src` 表示获取源代码软件包。
2. 软件包源地址：指定软件源的地址。可以是 HTTP、HTTPS、FTP 或本地文件系统路径。 
    - HTTP/HTTPS 示例：`http://archive.debian.org/debian/` 或 `https://mirrors.example.com/debian/`
    - FTP 示例：`ftp://ftp.debian.org/debian/`
    - 本地路径示例：`file:/mnt/cdrom/`，表示本地光盘或镜像文件的路径。
3. 发行版名称：指定要获取的 Debian 发行版名称，如 `stable`、`testing`、`unstable` 等。也可以使用发行版的代号，如 `buster`、`bullseye`、`sid` 等。
4. 软件包分区：指定软件包所属的分区或组织。常见的分区包括 `main`、`contrib`、`non-free` 等。 
    - `main`：包含自由软件。
    - `contrib`：包含一些依赖于非自由软件的软件包。
    - `non-free`：包含非自由软件。
5. 可选的部分名称：指定软件包的可选部分，如 `main`, `restricted`, `universe`, `multiverse` 等。这取决于具体的发行版和配置。



## APT


### apt-cache showsrc


```plain
Package: apt
Binary: apt, libapt-pkg5.0, libapt-inst2.0, apt-doc, libapt-pkg-dev, libapt-pkg-doc, apt-utils, apt-transport-https
Version: 1.8.2.13-1
Maintainer: APT Development Team <de***@li***.org>
Build-Depends: cmake (>= 3.4), debhelper (>= 11.2~), docbook-xml, docbook-xsl, dpkg-dev (>= 1.17.14), g++ (>= 4:7), gettext (>= 0.12), googletest <!nocheck> | libgtest-dev <!nocheck>, libbz2-dev, libdb-dev, libgnutls28-dev (>= 3.4.6), liblz4-dev (>= 0.0~r126), liblzma-dev, libseccomp-dev [amd64 arm64 armel armhf i386 mips mips64el mipsel ppc64el s390x hppa powerpc powerpcspe ppc64 x32], libsystemd-dev [linux-any], libudev-dev [linux-any], libzstd-dev (>= 1.0), ninja-build, pkg-config, po4a (>= 0.34-2), xsltproc, zlib1g-dev
Build-Depends-Indep: doxygen, graphviz, w3m
Architecture: any all
Standards-Version: 4.1.1
Format: 3.0 (quilt)
Directory: pool/main/a/apt
Files: 
 77b1b0061ed37ff64cd0fa4ab7bc25cf 152500 apt_1.8.2.13-1.debian.tar.xz
 6014c5bd18389ac81823045e931a5c97 2140 apt_1.8.2.13-1.dsc
 d374ced44608d160fc29e614258ba10e 2071440 apt_1.8.2.13.orig.tar.xz
Checksums-Sha1: 
 4d79b89d128995da2a48ad47777e9072afae3900 152500 apt_1.8.2.13-1.debian.tar.xz
 590993b2b8b73c6b9f0e02a60d96db2e74f858db 2140 apt_1.8.2.13-1.dsc
 925ad34c2253c3480c4de765e2407d744b6b2b4a 2071440 apt_1.8.2.13.orig.tar.xz
Checksums-Sha256: 
 73f609cce107f7e399a82019a1eea50c834b2b3c96437df1b8900370082a57e6 152500 apt_1.8.2.13-1.debian.tar.xz
 08506f0b0ab22b8e3ae44b069a1a98c4c64334ee129ec349e343e81bcb5b61ae 2140 apt_1.8.2.13-1.dsc
 db91de7ab152eabfea5437c44bbded2c6ffd98e20947077a7a91339acc4b93b8 2071440 apt_1.8.2.13.orig.tar.xz
Package-List:
 apt deb admin important arch=any
 apt-doc deb doc optional arch=all
 apt-transport-https deb oldlibs optional arch=all
 apt-utils deb admin important arch=any
 libapt-inst2.0 deb libs optional arch=any
 libapt-pkg-dev deb libdevel optional arch=any
 libapt-pkg-doc deb doc optional arch=all
 libapt-pkg5.0 deb libs optional arch=any
Testsuite: autopkgtest
Testsuite-Triggers: @builddeps@, aptitude, db-util, dpkg, fakeroot, gnupg, gnupg1, gnupg2, gpgv, gpgv1, gpgv2, libfile-fcntllock-perl, lsof, python3-apt, stunnel4, wget
Uploaders: Michael Vogt <m**@de***.org>, Julian Andres Klode <j**@de***.org>, David Kalnischkies <do*****@de***.org>
Vcs-Browser: https://salsa.debian.org/apt-team/apt
Vcs-Git: https://salsa.debian.org/apt-team/apt.git
```



### apt-cache showpkg


```plain
Package: apt
Versions: 
1.8.2.13-1 (/var/lib/apt/lists/professional-packages.chinauos.com_desktop-professional_dists_eagle_main_binary-amd64_Packages) (/usr/lib/dpkg-db/status)
 Description Language: 
                 File: /var/lib/apt/lists/professional-packages.chinauos.com_desktop-professional_dists_eagle_main_binary-amd64_Packages
                  MD5: 9fb97a88cb7383934ef963352b53b4a7
 Description Language: 
                 File: /var/lib/apt/lists/professional-packages.chinauos.com_desktop-professional_dists_eagle_main_binary-i386_Packages
                  MD5: 9fb97a88cb7383934ef963352b53b4a7
 Description Language: 
                 File: /var/lib/apt/lists/professional-security.chinauos.com_dists_eagle_1050_main_binary-amd64_Packages
                  MD5: 9fb97a88cb7383934ef963352b53b4a7
 Description Language: 
                 File: /var/lib/apt/lists/professional-security.chinauos.com_dists_eagle_1050_main_binary-i386_Packages
                  MD5: 9fb97a88cb7383934ef963352b53b4a7

1.8.2.10-1+dde (/var/lib/apt/lists/professional-security.chinauos.com_dists_eagle_1050_main_binary-amd64_Packages)
 Description Language: 
                 File: /var/lib/apt/lists/professional-packages.chinauos.com_desktop-professional_dists_eagle_main_binary-amd64_Packages
                  MD5: 9fb97a88cb7383934ef963352b53b4a7
 Description Language: 
                 File: /var/lib/apt/lists/professional-packages.chinauos.com_desktop-professional_dists_eagle_main_binary-i386_Packages
                  MD5: 9fb97a88cb7383934ef963352b53b4a7
 Description Language: 
                 File: /var/lib/apt/lists/professional-security.chinauos.com_dists_eagle_1050_main_binary-amd64_Packages
                  MD5: 9fb97a88cb7383934ef963352b53b4a7
 Description Language: 
                 File: /var/lib/apt/lists/professional-security.chinauos.com_dists_eagle_1050_main_binary-i386_Packages
                  MD5: 9fb97a88cb7383934ef963352b53b4a7


Reverse Depends: 
  apt-dbgsym,apt 1.8.2.10-1+dde
  dpkg,apt
  libapt-pkg5.0:i386,apt 1.6~
  apt:i386,apt
  libapt-pkg5.0,apt 1.8.2.10-1+dde
  libapt-pkg5.0,apt 1.6~
  dpkg,apt
  apt-utils,apt 1.8.2.10-1+dde
  apt-transport-https,apt 1.5~alpha4
  xdeb,apt 0.7.26~exp6
  org.yuan.yuan,apt
  com.steampowered.steam-launcher,apt 1.6
  com.codium,apt
  libapt-pkg5.0:i386,apt 1.6~
  apt:i386,apt
  squid-deb-proxy-client,apt 0.7.25.3ubuntu1
  wajig,apt
  upgrade-system,apt 0.7.0
  tasksel,apt
  supermin,apt
  packagesearch,apt 0.6.46.1
  reprepro,apt 0.9.4
  reportbug,apt
  python3-reportbug,apt
  python3-apt,apt
  python-apt,apt
  progress-linux-pgp-keys,apt
  progress-linux,apt
  libapt-pkg5.0,apt 1.6~
  netselect-apt,apt
  multistrap,apt
  mmdebstrap,apt
  lsb-release,apt
  libsbuild-perl,apt
  libapt-pkg5.0,apt 1.8.2.13-1
  devscripts,apt 1.3~pre3
  emdebian-archive-keyring,apt
  dwww,apt
  dpkg-www,apt
  dpkg,apt
  dh-make-perl,apt 1.1.8
  dgit,apt
  debconf,apt 0.3.12.1
  deborphan,apt
  debirf,apt
  debian-goodies,apt
  debian-cd,apt
  debfoster,apt
  apt-transport-tor,apt 1.6~alpha6
  dctrl-tools,apt
  daptup,apt
  d-shlibs,apt
  cron-apt,apt
  auto-apt-proxy,apt
  apticron-systemd,apt 1.1~exp9
  apticron,apt 1.1~exp9
  apt-utils,apt 1.8.2.13-1
  apt-transport-tor,apt 1.3~rc1
  apt-transport-https,apt 1.5~alpha4
  apt-transport-s3,apt
  apt-listchanges,apt 0.5.3
  apt-src,apt
  apt-show-versions,apt
  apt-show-source,apt
  apt-move,apt
  apt-listbugs,apt 0.9.11
  apt-file,apt 1.3~exp1~
  apt-build,apt 0.8.16~exp3
  apt-dbgsym,apt 1.8.2.13-1
Dependencies: 
1.8.2.13-1 - adduser (0 (null)) gpgv (16 (null)) gpgv2 (16 (null)) gpgv1 (0 (null)) deepin-keyring (0 (null)) libapt-pkg5.0 (2 1.7.0~alpha3~) libc6 (2 2.15) libgcc1 (2 1:3.0) libgnutls30 (2 3.6.6) libseccomp2 (2 1.0.1) libstdc++6 (2 5.2) apt-transport-https (3 1.5~alpha4~) apt-utils (3 1.3~exp2~) aptitude (3 0.8.10) ca-certificates (0 (null)) apt-doc (0 (null)) aptitude (16 (null)) synaptic (16 (null)) wajig (0 (null)) dpkg-dev (2 1.17.2) gnupg (16 (null)) gnupg2 (16 (null)) gnupg1 (0 (null)) powermgmt-base (0 (null)) apt-transport-https (3 1.5~alpha4~) apt-utils (3 1.3~exp2~) aptitude:i386 (3 0.8.10) apt-transport-https:i386 (3 1.5~alpha4~) apt-transport-https:i386 (3 1.5~alpha4~) apt:i386 (32 (null)) apt-utils:i386 (3 1.3~exp2~) apt-utils:i386 (3 1.3~exp2~) 
1.8.2.10-1+dde - adduser (0 (null)) gpgv (16 (null)) gpgv2 (16 (null)) gpgv1 (0 (null)) debian-archive-keyring (0 (null)) libapt-pkg5.0 (2 1.7.0~alpha3~) libc6 (2 2.15) libgcc1 (2 1:3.0) libgnutls30 (2 3.6.6) libseccomp2 (2 1.0.1) libstdc++6 (2 5.2) apt-transport-https (3 1.5~alpha4~) apt-transport-https:i386 (3 1.5~alpha4~) apt-utils (3 1.3~exp2~) apt-utils:i386 (3 1.3~exp2~) aptitude (3 0.8.10) aptitude:i386 (3 0.8.10) ca-certificates (0 (null)) apt-doc (0 (null)) aptitude (16 (null)) synaptic (16 (null)) wajig (0 (null)) dpkg-dev (2 1.17.2) gnupg (16 (null)) gnupg2 (16 (null)) gnupg1 (0 (null)) powermgmt-base (0 (null)) apt-transport-https (3 1.5~alpha4~) apt-transport-https:i386 (3 1.5~alpha4~) apt-utils (3 1.3~exp2~) apt-utils:i386 (3 1.3~exp2~) apt:i386 (32 (null)) 
Provides: 
1.8.2.13-1 - apt-transport-https (= 1.8.2.13-1) 
1.8.2.10-1+dde - apt-transport-https (= 1.8.2.10-1+dde) 
Reverse Provides:
```

## apt仓库
![](/blog_imgs/Debian软件包和仓库规范/1717638461674-32fc62bb-e337-4892-a0d9-150be8f36951.png)

+ <font style="color:rgb(0, 0, 0);">libgc 是源码包名</font>
+ <font style="color:rgb(0, 0, 0);">libgc-dev_7.6.4.2-2+dde_amd64.deb  是源码包编译出来的二进制包</font>
+ <font style="color:rgb(0, 0, 0);">libgc1c2-dbgsym_7.6.4.2-2+dde_amd64.deb  包名后面带有 -dbgsym 后缀的包是调试符号包（debug symbol package），这些包包含了与相应二进制包相关的调试信息</font>
+ <font style="color:rgb(0, 0, 0);">libgc_7.6.4.2-2+dde.debian.tar.xz 文件名带有 dde.debian.tar.xz 后缀的包是一种源代码包，特指 Deepin 桌面环境（Deepin Desktop Environment，简称 DDE）在 Debian 包管理系统中的源码包，用于对原始源码进行必要的修改和配置，以便在 Debian 系统上正确构建和打包。</font>
+ <font style="color:rgb(0, 0, 0);">libgc_7.6.4.2-2+dde.dsc  文件名带有 .dsc 后缀的文件是 Debian 源码控制文件（Debian Source Control file）。这个文件描述了 Debian 源码包的相关信息</font>
+ <font style="color:rgb(0, 0, 0);">libgc_7.6.4.2.orig.tar.xz   文件名带有 .orig.tar.xz 后缀的包是原始源码包（original source tarball）。这些包包含了上游开发者发布的原始源代码，没有经过任何修改</font>

## 安全公告
[https://security-team.debian.org/security_tracker.html](https://security-team.debian.org/security_tracker.html)

