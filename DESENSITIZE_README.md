# 脱敏脚本使用说明

这个脚本用于对 Markdown 文件中的敏感信息进行脱敏处理。

## 使用方法

### 1. 处理单个文件
```bash
python3 desensitize.py path/to/your/file.md
```

### 2. 处理整个目录
```bash
python3 desensitize.py path/to/your/directory
```

### 3. 预览模式（不实际修改文件）
```bash
python3 desensitize.py --preview path/to/your/file.md
```

### 4. 不创建备份文件
```bash
python3 desensitize.py --no-backup path/to/your/file.md
```

## 脱敏规则

脚本会自动识别并脱敏以下内容：

1. **邮箱地址**: `user@example.com` → `us***@ex***.com`
2. **特定用户名**: 
   - `ut005204` → `ut******`
   - `pudding` → `user***`
   - `likeda` → `user***`
3. **公司名**: `uniontech` → `company***`
4. **Git 仓库 URL**: 完整 URL → 脱敏后的通用 URL
5. **密码**: `password: 123456` → `password: ********`
6. **API Key/Token**: `api_key: abc123` → `api_key: ********`
7. **IP 地址**: `192.168.1.1` → `192.168.x.x`
8. **用户路径**: `/Users/username` → `/Users/user***`

## 注意事项

- 脚本默认会创建备份文件（`.bak` 后缀）
- 只处理 `.md` 文件
- 建议先使用 `--preview` 模式查看效果
- 脱敏是不可逆的，请确保有备份

## 示例

```bash
# 预览当前目录下所有 md 文件的脱敏效果
python3 desensitize.py --preview ./

# 脱敏处理博客文章目录且不创建备份
python3 desensitize.py --no-backup source/_posts/

# 处理单个文件且不创建备份
python3 desensitize.py --no-backup source/_posts/Git.md
```
