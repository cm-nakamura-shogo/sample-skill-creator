---
name: profile-photo-processor
description: |
  プロフィール写真の標準化処理。
  背景除去、顔センタリング、明るさ補正を自動で行う。
  Dockerで実行するため安全。
---

# Profile Photo Processor

プロフィール写真を標準化するスキル。Docker経由で安全に実行。

## 機能

- 背景を除去して指定色（デフォルト #e1e1e1）に置換
- 顔を検出して画像の中央に配置
- 暗い画像は明るさを自動補正
- 単一ファイルまたはフォルダ一括処理に対応

## 使用方法

### Docker Compose（推奨）

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/profile-photo-processor

# イメージをビルド（初回のみ）
docker compose build

# フォルダ一括処理
docker compose run --rm profile-photo-processor /input /output

# 単一ファイル処理
docker compose run --rm profile-photo-processor /input/photo.jpg /output/result.jpg
```

### Docker直接実行

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/profile-photo-processor

# イメージをビルド
docker build -t profile-photo-processor .

# 実行（ホストのフォルダをマウント）
docker run --rm \
  -v /path/to/input:/input:ro \
  -v /path/to/output:/output \
  profile-photo-processor /input /output
```

## オプション

| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| `--size` | 1000 | 出力画像の最大サイズ（px） |
| `--bg-color` | e1e1e1 | 背景色（hex） |
| `--face-ratio` | 0.18 | 顔の高さが画像高さに占める割合 |
| `--face-position` | 0.42 | 顔の垂直位置（0=上端, 1=下端） |
| `--model` | isnet-general-use | 背景除去モデル |
| `--no-normalize` | - | 明るさ補正をスキップ |

## 前提条件

- Docker Desktop または Docker Engine がインストールされていること

> **Dockerが使えない場合**
> Rancher Desktop などをインストールし、**起動しておいてください**（起動していないと docker コマンドが使えません）。
> - macOS/Windows: https://rancherdesktop.io/
> - Linux: Docker Engine をインストール・起動

## ファイル構成

```
skills/profile-photo-processor/
├── SKILL.md
├── Dockerfile
├── docker-compose.yml
└── scripts/
    ├── process_profile_photo.py
    ├── pyproject.toml
    └── uv.lock
```
