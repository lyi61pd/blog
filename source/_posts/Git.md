---
title: Git
date: 2025-06-30
tags:
    - Git
---

## 初始化
### 新建仓库
直接复制gitlab的，稍微改了点，还是待优化

```bash
# Git global setup
git config --global user.name "xxx"
git config --global user.email "xxx"


# Create a new repository
git clone xxxx
cd uscan
git switch -c main
touch README.md
git add README.md
git commit -m "add README"
git push -u origin main


# Push an existing folder
cd existing_folder
git init
git checkout -b main
git remote add origin xxxxxx
git add .
git commit -m "Initial commit"
git push -u origin main

# Push an existing Git repository
cd existing_repo
git remote rename origin old-origin
git remote add origin g**@company***.com:ut******/uscan.git
git push -u origin --all
git push -u origin --tags
```

## 强制将本地状态同步到远程仓库并清空历史记录
危险操作, 确保知道自己在做什么再这么搞

```plain
rm -rf .git
git init
git add .
git commit -m "Initial commit - reset history"
git remote add origin g**@gi***.com:lyi61pd/blog.git
git branch -M main
git push -f origin main
```

## 分支
### 删除本地的远程分支跟踪引用
```bash
git remote prune origin
```

### 查看所有分支
```bash
git branch -a
```

### 删除远程分支
```bash
git push origin --delete feature-前端操作按钮颜色及布局调整
```

### 删除本地分支
```bash
git branch -d feature-前端操作按钮颜色及布局调整
```

### 切换当前分支
```bash
git checkout dev
```

### 更新默认分支origin/HEAD
先去gitlab->settings设置，然后

```bash
git fetch origin
git remote set-head origin -a
```

### 新建本地分支
```bash
git branch new_branch_name
```

### 新建远程分支
基于本地当前分支，推送到远程分支，如果远程分支不存在相当于新建远程分支

```plain
git push --set-upstream origin feature-架构划分合入clickhouse迁移
```

### 新建本地分支并切换到该分支
相当于

:::info
git branch new_branch_name

git checkout new_branch_name

:::

```bash
git checkout -b new_branch_name
```

### 查看本地分支和远程分支的跟踪关系
```bash
git branch -vv
```

返回结果例子

:::info
* master                abc1234 [origin/master] Initial commit

  feature-branch        def5678 [origin/feature-branch] Added new feature

  another-branch        ghi9101 Added another feature

:::

在这个示例中：

+ master 分支跟踪 origin/master
+ feature-branch 分支跟踪 origin/feature-branch
+ another-branch 没有跟踪任何远程分支

### 设置本地分支和远程分支的跟踪关系
```bash
git branch --set-upstream-to=origin/origin_branch_name local_branch_name
```

## Commit
### 合并多个Commit
合并最近的5个commit

```bash
git rebase -i HEAD~5
```

会有这样的画面

![](https://cdn.nlark.com/yuque/0/2024/png/22226417/1720691456171-86166bbf-1321-4c45-a1b4-f2b9c22220c3.png)

然后改成

![](https://cdn.nlark.com/yuque/0/2024/png/22226417/1720691528190-6b5890c8-ba99-4cd6-a20a-58d2464546a8.png)

然后ctrl+o enter ctrl+x

然后会有这样的画面

![](https://cdn.nlark.com/yuque/0/2024/png/22226417/1720691598392-d8184fe0-f32b-4314-a2f7-fd9a2906fced.png)

这里改成想要提交commit记录的说明内容

![](https://cdn.nlark.com/yuque/0/2024/png/22226417/1720691639533-f13c0e2a-5b48-4ff3-8a7b-83fb55efab16.png)

然后ctrl+o enter ctrl+x

本地commit记录已合并完成

推送到远程仓库

```bash
git push --force
```



### 删除某个文件的所有commit记录
比如项目里有个sql，如果反复更新这个sql，仓库会变得很大，如果可以的话，可以全部删掉

删除前先备份，因为这个命令会把当前的也删掉

```plain
git filter-branch --force --index-filter \
"git rm --cached --ignore-unmatch path/to/the/file" \
--prune-empty --tag-name-filter cat -- --all
```

然后再把备份的搞过来，重新提交commit，这样历史的就没了，只留下最新的

然后如果有其他协作者, 因为远程commit历史被修改了, 其他协作者本地会出现不同步的问题, 这时候需要这样同步

```bash
git fetch origin
git reset --hard origin/your-branch-name
```

## .gitignore
### .gitignore不生效
如果文件或目录已经被 Git 跟踪，那么即使它们在 `.gitignore` 中被列出，Git 也会继续跟踪它们，需要先从 Git 仓库中移除这些文件

```plain
git rm -r --cached .
git add .
git commit -m "Remove ignored files from tracking"
```

## Tag
### 查看本地所有Tag
```shell
git tag
```

### 查看远程所有Tag
```shell
git ls-remote --tags origin
```

### 基于当前commit新建Tag
```shell
git tag 0.1
```

### 将本地Tag推送到远程
```shell
git push origin 0.1
```

### 拉取远程的Tag
```shell
git fetch --tags
```

本地只增不删，所以如果远程删了，同步到本地的时候，本地并不会删，需要手动删

### 删除本地的Tag
```shell
git tag -d 0.1
```

### 删除远程的Tag
```shell
git push --delete origin 0.1
```

## PR
### 切换至远程的PR
相当于在本地新建了个pr-1分支，把远程的提交拉过来了

```plain
 git ls-remote origin 'pull/*/head'
 git fetch origin refs/pull/1/head
 git checkout -b pr-1 FETCH_HEAD
```

