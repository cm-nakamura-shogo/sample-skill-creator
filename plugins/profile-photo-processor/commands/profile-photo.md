---
allowed-tools: Bash, Read, Write
description: プロフィール写真を処理する（背景除去、顔センタリング、明るさ補正）
---

## このコマンドについて

プロフィール写真の標準化処理を行う。背景除去、顔センタリング、明るさ補正を自動で実行する。

## 処理の流れ

1. ユーザーに入力画像パスと出力画像パスを確認
2. スクリプトの場所を特定
3. uvxでスクリプトを実行

## スクリプトの場所

このプラグインのスクリプトは以下にある：
`${CLAUDE_PLUGIN_ROOT}/skills/profile-photo-processor/scripts/`

もし `${CLAUDE_PLUGIN_ROOT}` が解決できない場合は、以下のパスを探す：
- `~/.claude/plugins/marketplaces/*/plugins/profile-photo-processor/skills/profile-photo-processor/scripts/`

## 実行コマンド

```bash
cd <スクリプトのディレクトリ>
uvx --python 3.12 --from . profile-photo-processor <入力画像> <出力画像>
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

uvがインストールされていること。未インストールの場合：

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 手順

1. まずユーザーに入力画像と出力先を確認する
2. スクリプトのディレクトリに移動してuvxで実行する
3. 処理結果をユーザーに報告する
