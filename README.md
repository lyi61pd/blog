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

部署到github

```plain
git clone -b master https://github.com/jerryc127/hexo-theme-butterfly.git themes/butterfly
hexo clean && hexo generate && hexo deploy
```

