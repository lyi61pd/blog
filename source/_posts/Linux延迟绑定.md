---
title: Linux延迟绑定
date: 2025-04-10
tags:
  - Linux
  - 二进制
---

# Windows 下.lib .dll .obj .exe

.lib 是静态链接文件

.dll 是动态链接文件

.obj 是编译时生成的中间代码文件，比如一个项目有多个.c 文件，编译时会先全部生成为中间 obj 文件，然后在进行链接生成最终的 exe 文件

.exe 文件是可执行文件

# Linux 下.o .so .a

.o 类似于 Windows 下的.obj 文件，是编译中间产物

.so 是动态链接文件

.a 是静态链接文件,可通过如下命令将中间文件加进 output.a 或者新生成一个 output.a

```plain
创建.a的命令
ar rcx output.a test1.o test2.o
```

## Linux 延迟绑定机制

### 使用的 C 语言例子

```plain
//-------------------------------------------------------------------
// FileName: test1.c
// Author: hexuelin
// Copyright (c) company***.
//-------------------------------------------------------------------
#include <stdio.h>
void stack_overflow(){
 char buf[64] = {0};
 scanf("%s", &buf);
 printf("hello %s\n", &buf);
}
void get_shell(){
 system("/bin/sh");
}
int main(int argc, char const *argv[]){
 stack_overflow();
 return 0;
}
```

## 静态链接和动态链接

静态链接在编译时把需要用到的内容都链接到文件中

动态链接则是会在程序执行时再进行链接

因此静态链接明显会比动态链接文件要大，同样的执行速度也会更快

```plain
#编译时加上-static参数就是静态链接
gcc title.c -o title_static -static
#不加参数默认就是动态链接
gcc title.c -o title
```

![](/blog_imgs/Linux延迟绑定/1744249758419-7eb479dc-c5a7-480c-b6c9-5e819fc619dc.png)

![](/blog_imgs/Linux延迟绑定/1744249762197-97ee9ea1-40e2-4e94-9614-7c13c154a324.png)

### 部分寄存器以及部分汇编指令

下面的汇编指令，部分用其他指令替代作为解释，但是实际上并不能用替代的指令，比如 rip,rsp 寄存器，原则上并不允许直接对他们进行操作

- rip

指向下一条要执行的命令（还没有执行）

push 1

- rsp

栈顶

- rbp

栈底

- mov rax,1

rax=1

- add rax,1

rax=rax+1

- push rax

```plain
add rsp,一个字长（64位一个字长就是64位，8字节）
mov [rsp],rax
```

- jmp 0x6666

```plain
mov rip,0x6666
```

- call printf[@plt ](/plt)

```plain
#printf@plt是一个地址,这个地址的备注名叫做printf@plt
push rip
jmp printf@plt
```

- leave

```plain
mov rsp,rbp
pop rbp
```

- retn

```plain
pop rip
```

### libc.so.6

libc 是 Stantard C Library 的简称，它是符合 ANSI C 标准的一个标准函数库。

在 Linux 操作系统下所说的 libc 即 glibc。glibc 是类 Unix 操作系统中使用最广泛的 libc 库，它的全称是 GNU C Library.

### PLT 和 GOT

**PLT**表称为过程链接表（procedure linkage table）

**GOT**表称为全局偏移量表（global offset table）

**用不太严谨的话来概况，首先可以这么理解**：

**GOT**表中存储真正的函数地址


**PLT**表中存储的是**GOT**表中的地址



调用函数时会先到PLT表，再由PLT表导向GOT表

**GOT[0]**包含.dynamic 段的地址，.dynamic 段包含了动态链接器用来绑定过程地址的信息，比如符号的位置和重定位信息

**GOT[1]**包含动态链接器的标识

**GOT[2]**包含动态链接器的延迟绑定代码的入口点，也就是调用\_dl_runtime_resolve 函数，延迟绑定的时候要调用的函数

printf 第一次调用的时候 got 表中是没有实际地址的， 第一次调用 printf 的时候  ，最终会调用\_dl_runtime_resolve 函数，这个函数的作用就是把 prtinf 函数的实际地址写入到 GOT 表中，之后如果第二次，第三次。。。调用 printf 的时候就能从 GOT 表直接获取到 printf 的地址了

**GOT**表中正式的函数地址要从 GOT[3]开始，也就是第四项

举例：PLT 表中 printf[@plt ](/plt)

```plain
jmp pr****@go***.plt
push printf在got表中的编号
jmp plt表第一行指令
```

举例: GOT 表中 printf[@got.plt ](/got.plt)

```plain
第一次执行printf时：PLT表中printf@plt的第二行
第二三四次执行printf时：动态链接库libc中函数printf的真实地址
```

### 延迟绑定机制下,函数初次调用流程图

![](/blog_imgs/Linux延迟绑定/1744249859364-e8ace29f-3caf-46ab-b72d-b8a6a9abdab5.png)

### IDA 查看 PLT 表

![](/blog_imgs/Linux延迟绑定/1744249774986-45335481-e777-4191-9e00-c872f5da5f7a.png)

### IDA 查看 GOT 表

![](/blog_imgs/Linux延迟绑定/1744249779063-2d695725-69ae-4ddb-9ac7-3550bf6799f5.png)

### .plt     .got    .got.plt

这三者是 ELF 文件格式中的节(section)

.plt 就是 PLT 表

.got 和.got.plt 统称为 GOT 表

.got 里面直接存储的就是函数调用的地址，部分函数地址是直接存放在.got 里面的

PLT 表指向的是.got.plt

printf@plt 指向的就是 pr****@go***.plt

第一次调用时printf@got.plt里指向的是 printf@plt 的下一行也就是 push printf 对应的 got 表里的序号

放在.got 里的相当于.got.plt 第一次调用之后的状态

### RELRO

```plain
#关闭RELRO
gcc title.c -o title_no -z norelro
#部分开启RELRO(Partial RELRO不加参数默认是这个)
gcc title.c -o title_partial -z lazy
#完全开启RELRO(Full RELRO)
gcc title.c -o title_full -z now
```

- RELRO，[堆栈](https://so.csdn.net/so/search?q=%E5%A0%86%E6%A0%88&spm=1001.2101.3001.7020)地址随机化， 是一种用于加强对 binary 数据段的保护的技术。
- 由于 GOT 和 PLT 以及延迟绑定的原因，在启用延迟绑定时，符号解析只发生在第一次使用的时候，该过程是通过 PLT 表进行的，解析完成后，相应的 GOT 条目会被修改为正确的函数地址。因此，在延迟绑定的情况下。.got.plt 必须可写，这就给了攻击者篡改地址劫持程序的执行的可能。
- RELRO（ReLocation Read-Only）机制的提出就是为了解决延迟绑定的安全问题，他将符号重定位表设置为只读，或者在程序启动时就解析并绑定所有的动态符号，从而避免 GOT 上的地址被篡改。RELRO 有两种形式：
  - partial RELRO：一些段（包括.dynamic,.got 等）在初始化后会被标记为只读。在 unbuntu16.04（GCC-5.4.0）上，默认开启 Partial RELRO。
  - Full RELRO ：除了 Partial RELRO，延迟绑定将被禁止，所有的导入符号将在开始时被解析，.got.plt 段会被完全初始化为目标函数的最终地址，并被 mprotect 标记为只读，但其实.got.plt 会被直接合并到.got，也就看不到这段了。另外 link_map 和\_dl_runtime_reolve 的地址也不会被装入。开启 Full RELRO 会对程序启动时的性能造成一定的影响，但也只有这样才能防止攻击者篡改 GOT。
