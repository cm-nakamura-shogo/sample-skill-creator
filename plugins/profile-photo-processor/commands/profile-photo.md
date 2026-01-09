---
allowed-tools: Bash, Read, Write, Glob
description: プロフィール写真を処理する（背景除去、顔センタリング、明るさ補正）- Docker使用
---

# Profile Photo Processor

プロフィール写真の標準化処理を行う。Docker経由で安全に実行。

## 処理の流れ

1. ユーザーに入力（ファイルまたはフォルダ）と出力先を確認
2. スキルのディレクトリを特定
3. Dockerイメージをビルド（必要に応じて）
4. Dockerでスクリプトを実行

## スキルの場所

このプラグインのスキルは以下にある：
- `${CLAUDE_PLUGIN_ROOT}/skills/profile-photo-processor/`

もし `${CLAUDE_PLUGIN_ROOT}` が解決できない場合は、以下のパスを探す：
- `~/.claude/plugins/marketplaces/*/plugins/profile-photo-processor/skills/profile-photo-processor/`

## 実行手順

### 1. スキルディレクトリに移動

```bash
cd <スキルのディレクトリ>
```

### 2. Dockerイメージをビルド（初回のみ）

```bash
docker compose build
```

### 3. 処理を実行

**フォルダ一括処理の場合：**
```bash
docker compose run --rm \
  -v /absolute/path/to/input:/input:ro \
  -v /absolute/path/to/output:/output \
  profile-photo-processor /input /output
```

**単一ファイル処理の場合：**
```bash
docker compose run --rm \
  -v /absolute/path/to/input:/input:ro \
  -v /absolute/path/to/output:/output \
  profile-photo-processor /input/filename.jpg /output/result.jpg
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
> ユーザーに「Rancher Desktop などをインストールし、**起動しておいてください**（起動していないと docker コマンドが使えません）」と案内する。
> - macOS/Windows: https://rancherdesktop.io/
> - Linux: Docker Engine をインストール・起動

## 注意事項

- 入力・出力パスは絶対パスで指定する
- 入力フォルダは読み取り専用（:ro）でマウントされる
- 対応フォーマット: jpg, jpeg, png, webp, bmp
