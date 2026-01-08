---
allowed-tools: Bash, Read, Write
description: プロフィール写真を処理する（背景除去、顔センタリング、明るさ補正）
---

## Context

- Plugin root: `$CLAUDE_PLUGIN_ROOT`
- Scripts location: `$CLAUDE_PLUGIN_ROOT/skills/profile-photo-processor/scripts`

## Your task

ユーザーが指定した画像ファイルに対して、プロフィール写真の標準化処理を実行する。

### 処理内容

1. 背景を除去して #e1e1e1 に置換
2. 顔を検出して画像の中央に配置
3. 暗い画像は明るさを自動補正
4. JPEG形式で出力

### 実行方法

```bash
cd $CLAUDE_PLUGIN_ROOT/skills/profile-photo-processor/scripts
uvx --python 3.12 --from . profile-photo-processor <入力画像> <出力画像>
```

### オプション

- `--bg-color`: 背景色（hex, デフォルト: e1e1e1）
- `--face-ratio`: 顔サイズ比率（デフォルト: 0.18）
- `--face-position`: 顔の垂直位置（デフォルト: 0.42）
- `--model`: 背景除去モデル（デフォルト: isnet-general-use）

### 前提条件

uvがインストールされていること。未インストールの場合：

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

ユーザーに入力画像と出力先を確認してから処理を実行すること。
