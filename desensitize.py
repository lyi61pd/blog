#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown文件脱敏处理脚本
用于将敏感信息（邮箱、用户名、公司名、密码等）进行脱敏处理
"""

import os
import re
import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Tuple

class MarkdownDesensitizer:
    def __init__(self):
        # 脱敏规则配置
        self.desensitize_rules = [
            # 邮箱脱敏
            (r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', self._mask_email),
            
            # 用户名脱敏（常见的用户名模式）
            (r'\but\d{6}\b', 'ut******'),  # ut005204 -> ut******
            (r'\bpudding\b', 'user***'),   # pudding -> user***
            (r'\blikeda\b', 'user***'),    # likeda -> user***
            
            # 公司名脱敏
            (r'\buniontech\b', 'company***'),
            (r'\bUniontech\b', 'Company***'),
            (r'\bUNIONTECH\b', 'COMPANY***'),
            
            # Git仓库URL脱敏
            (r'(git@|https?://)[^/]+\.uniontech\.com[:/][^/\s]+/[^\s]+', self._mask_git_url),
            (r'(git@|https?://)[^/]+\.com[:/][^/\s]+/[^\s]+\.git', self._mask_git_url),
            
            # 密码相关（常见密码模式）
            (r'password\s*[:=]\s*[^\s\n]+', 'password: ********'),
            (r'passwd\s*[:=]\s*[^\s\n]+', 'passwd: ********'),
            (r'pwd\s*[:=]\s*[^\s\n]+', 'pwd: ********'),
            
            # API Key 和 Token
            (r'(api_key|apikey|token|key)\s*[:=]\s*[a-zA-Z0-9_-]{8,}', r'\1: ********'),
            
            # 服务器地址和端口
            # (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?\b', '192.168.x.x'),
            
            # 特定路径脱敏
            (r'/home/[^/\s]+', '/home/user***'),
            (r'/Users/[^/\s]+', '/Users/user***'),
        ]
    
    def _mask_email(self, match) -> str:
        """邮箱脱敏处理"""
        email = match.group(0)
        parts = email.split('@')
        if len(parts) != 2:
            return email
        
        username = parts[0]
        domain = parts[1]
        
        # 用户名脱敏：保留前2个字符，其余用*替代
        if len(username) <= 2:
            masked_username = username
        elif len(username) <= 4:
            masked_username = username[0] + '*' * (len(username) - 1)
        else:
            masked_username = username[:2] + '*' * (len(username) - 2)
        
        # 域名脱敏：保持结构，但替换敏感部分
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            if 'uniontech' in domain.lower():
                masked_domain = 'company***.com'
            else:
                masked_domain = domain_parts[0][:2] + '***.' + domain_parts[-1]
        else:
            masked_domain = domain
        
        return f"{masked_username}@{masked_domain}"
    
    def _mask_git_url(self, match) -> str:
        """Git URL脱敏处理"""
        url = match.group(0)
        if 'uniontech' in url.lower():
            if url.startswith('git@'):
                return 'git@company***.com:user***/repo***.git'
            else:
                return 'https://company***.com/user***/repo***.git'
        else:
            if url.startswith('git@'):
                return 'git@github.com:user***/repo***.git'
            else:
                return 'https://github.com/user***/repo***.git'
    
    def desensitize_content(self, content: str) -> Tuple[str, int]:
        """
        对内容进行脱敏处理
        返回: (脱敏后的内容, 脱敏处理次数)
        """
        modified_content = content
        total_replacements = 0
        
        for pattern, replacement in self.desensitize_rules:
            if callable(replacement):
                # 如果replacement是函数，使用re.sub的回调功能
                modified_content, count = re.subn(pattern, replacement, modified_content, flags=re.IGNORECASE)
            else:
                # 如果replacement是字符串，直接替换
                modified_content, count = re.subn(pattern, replacement, modified_content, flags=re.IGNORECASE)
            
            total_replacements += count
        
        return modified_content, total_replacements
    
    def process_file(self, file_path: Path, backup: bool = True) -> Dict:
        """
        处理单个文件
        """
        result = {
            'file': str(file_path),
            'success': False,
            'replacements': 0,
            'error': None,
            'backed_up': False
        }
        
        try:
            # 检查文件是否存在
            if not file_path.exists():
                result['error'] = '文件不存在'
                return result
            
            # 读取原文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 脱敏处理
            desensitized_content, replacements = self.desensitize_content(original_content)
            
            # 如果有修改，则处理
            if replacements > 0:
                # 创建备份
                if backup:
                    backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                    shutil.copy2(file_path, backup_path)
                    result['backed_up'] = True
                    print(f"✓ 已创建备份: {backup_path}")
                
                # 写入脱敏后的内容
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(desensitized_content)
                
                result['success'] = True
                result['replacements'] = replacements
                print(f"✓ 已处理: {file_path} (脱敏 {replacements} 处)")
            else:
                result['success'] = True
                result['replacements'] = 0
                print(f"- 无需处理: {file_path}")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"✗ 处理失败: {file_path} - {e}")
        
        return result
    
    def process_directory(self, dir_path: Path, backup: bool = True) -> List[Dict]:
        """
        处理目录下所有.md文件
        """
        results = []
        
        if not dir_path.exists():
            print(f"✗ 目录不存在: {dir_path}")
            return results
        
        if not dir_path.is_dir():
            print(f"✗ 不是目录: {dir_path}")
            return results
        
        # 查找所有.md文件
        md_files = list(dir_path.rglob('*.md'))
        
        if not md_files:
            print(f"- 目录中没有找到.md文件: {dir_path}")
            return results
        
        print(f"找到 {len(md_files)} 个.md文件")
        
        # 处理每个文件
        for md_file in md_files:
            result = self.process_file(md_file, backup)
            results.append(result)
        
        return results
    
    def process_path(self, path: str, backup: bool = True) -> List[Dict]:
        """
        处理路径（文件或目录）
        """
        path_obj = Path(path)
        
        if path_obj.is_file():
            if path_obj.suffix.lower() == '.md':
                return [self.process_file(path_obj, backup)]
            else:
                print(f"✗ 不是.md文件: {path}")
                return []
        elif path_obj.is_dir():
            return self.process_directory(path_obj, backup)
        else:
            print(f"✗ 路径不存在: {path}")
            return []


def main():
    parser = argparse.ArgumentParser(description='Markdown文件脱敏处理工具')
    parser.add_argument('path', help='要处理的文件或目录路径')
    parser.add_argument('--no-backup', action='store_true', help='不创建备份文件')
    parser.add_argument('--preview', action='store_true', help='预览模式，只显示会被脱敏的内容，不实际修改文件')
    
    args = parser.parse_args()
    
    desensitizer = MarkdownDesensitizer()
    
    if args.preview:
        # 预览模式
        print("=== 预览模式 ===")
        path_obj = Path(args.path)
        
        if path_obj.is_file() and path_obj.suffix.lower() == '.md':
            with open(path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            desensitized_content, replacements = desensitizer.desensitize_content(content)
            
            if replacements > 0:
                print(f"\n文件: {path_obj}")
                print(f"将进行 {replacements} 处脱敏处理")
                print("\n--- 脱敏后内容预览 ---")
                print(desensitized_content[:1000] + "..." if len(desensitized_content) > 1000 else desensitized_content)
            else:
                print(f"文件 {path_obj} 无需脱敏处理")
        
        elif path_obj.is_dir():
            md_files = list(path_obj.rglob('*.md'))
            total_replacements = 0
            
            for md_file in md_files:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                _, replacements = desensitizer.desensitize_content(content)
                if replacements > 0:
                    print(f"{md_file}: 将脱敏 {replacements} 处")
                    total_replacements += replacements
            
            print(f"\n总计将脱敏 {total_replacements} 处")
    
    else:
        # 实际处理模式
        print("=== 开始脱敏处理 ===")
        results = desensitizer.process_path(args.path, backup=not args.no_backup)
        
        # 统计结果
        total_files = len(results)
        success_files = len([r for r in results if r['success']])
        total_replacements = sum(r['replacements'] for r in results)
        failed_files = [r for r in results if not r['success']]
        
        print(f"\n=== 处理完成 ===")
        print(f"总文件数: {total_files}")
        print(f"成功处理: {success_files}")
        print(f"总脱敏次数: {total_replacements}")
        
        if failed_files:
            print(f"失败文件数: {len(failed_files)}")
            for failed in failed_files:
                print(f"  - {failed['file']}: {failed['error']}")


if __name__ == '__main__':
    main()
