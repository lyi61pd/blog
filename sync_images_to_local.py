import os
import re
import requests
from pathlib import Path

def download_image(url, save_dir):
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        filename = url.split('/')[-1].split('?')[0]
        local_path = os.path.join(save_dir, filename)

        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return filename
    except Exception as e:
        print(f"[失败] 无法下载图片：{url}\n原因: {e}")
        return None

def process_markdown_file(md_path, image_dir_base):
    article_name = md_path.stem
    image_dir = image_dir_base / article_name
    image_dir.mkdir(parents=True, exist_ok=True)

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配所有外链图片
    pattern = r'!\[(.*?)\]\((https?://[^\s)]+)\)'
    matches = re.findall(pattern, content)

    if not matches:
        print(f"[跳过] 没有外链图片：{md_path.name}")
        return

    updated = False
    for alt_text, url in matches:
        if 'blog_imgs' in url or '://' not in url:
            continue  # 忽略已替换的或本地图

        print(f"[下载] {url}")
        filename = download_image(url, image_dir)
        if filename:
            new_path = f'/blog_imgs/{article_name}/{filename}'
            md_img = f'![{alt_text}]({url})'
            new_md_img = f'![{alt_text}]({new_path})'
            content = content.replace(md_img, new_md_img)
            updated = True

    if updated:
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 已更新：{md_path.name}")
    else:
        print(f"[跳过] 无需更新：{md_path.name}")

def batch_process_posts(posts_dir, image_base_dir):
    posts_dir = Path(posts_dir)
    image_base_dir = Path(image_base_dir)

    md_files = list(posts_dir.glob('*.md'))

    print(f"🔍 共检测到 {len(md_files)} 篇文章，开始处理...\n")

    for md_file in md_files:
        process_markdown_file(md_file, image_base_dir)

    print("\n🎉 所有 Markdown 处理完成！")

if __name__ == '__main__':
    # === 配置路径 ===
    POSTS_DIR = 'source/_posts'
    IMAGE_DIR = 'source/blog_imgs'

    batch_process_posts(POSTS_DIR, IMAGE_DIR)
