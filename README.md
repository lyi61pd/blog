### Deployment
安装

```plain
npm install -g hexo-cli
hexo init blog
cd blog
npm install
hexo server
git clone -b master https://github.com/jerryc127/hexo-theme-butterfly.git themes/butterfly
npm install hexo-renderer-pug hexo-renderer-stylus hexo-generator-search hexo-generator-feed hexo-generator-sitemap hexo-generator-searchdb --save
npm install hexo-deployer-git --save
hexo new "我的第一篇文章"
hexo clean && hexo server
```

调配置

```plain
# 博客标题
title: "你的博客名称"

# 博客头像（链接或本地图片路径）
avatar: /images/avatar.png

# 博客描述
subtitle: "一句简单介绍"

# 作者名
author: "你的名字"
```

```plain
comments:
  use: Valine # 或 Waline, Disqus, Gitalk
  Valine:
    appId: # 从Leancloud获取
    appKey: # 从Leancloud获取

```

```plain
# 永久链接格式（推荐）
permalink: :year/:month/:day/:title/

# 使用更友好的链接样式
pretty_urls:
  trailing_index: false
  trailing_html: false

```

```plain
deploy:
  type: git
  repo: https://github.com/你的用户名/你的用户名.github.io.git
  branch: main # 或 master

```
新增文章
```
hexo new "我的第一篇文章"
```

部署到github

### 手动部署
```plain
git clone -b master https://github.com/jerryc127/hexo-theme-butterfly.git themes/butterfly
python3 sync_images_to_local.py
hexo clean && hexo generate && hexo deploy
```

### 自动部署 (GitHub Actions)

项目已配置 GitHub Actions，每次推送到 main/master 分支时会自动执行部署。

**设置步骤：**

1. 生成 SSH 密钥对：
```bash
ssh-keygen -t rsa -b 4096 -C "lyi61pd@gmail.com" -f ~/.ssh/deploy_key
```

2. 将公钥添加到目标仓库：
   - 进入 `your-username.github.io` 仓库
   - Settings → Deploy keys → Add deploy key
   - 粘贴 `deploy_key.pub` 的内容，勾选 "Allow write access"

3. 将私钥添加到源码仓库：
   - 进入当前博客源码仓库
   - Settings → Secrets and variables → Actions → New repository secret
   - Name: `DEPLOY_KEY`
   - Value: `deploy_key` 文件的内容

4. 推送代码即可自动部署：
```bash
git add .
git commit -m "update blog"
git push origin main
```

