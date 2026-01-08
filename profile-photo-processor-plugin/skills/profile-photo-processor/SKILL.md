---
name: profile-photo-processor
description: プロフィール写真の標準化処理。人物写真から背景を除去し、指定色（デフォルト#e1e1e1）に置換、顔検出による自動センタリング、明るさ補正を行う。プロフィール写真の作成、社員証写真の統一、SNSアイコン用画像の加工などに使用。
---

# Profile Photo Processor

プロフィール写真を標準化するスキル。背景除去、顔検出によるセンタリング、明るさ補正を自動で行う。

## セットアップ

uvをインストール（未インストールの場合）：

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

または winget:
```
winget install --id=astral-sh.uv -e
```

## 使用方法

### uvxで実行（推奨）

```bash
cd scripts
uvx --python 3.12 --from . profile-photo-processor <入力画像> <出力画像>
```

### 例

```bash
# 基本的な処理
uvx --python 3.12 --from . profile-photo-processor photo.jpg output.jpg

# カスタム背景色（白）
uvx --python 3.12 --from . profile-photo-processor photo.jpg output.jpg --bg-color ffffff

# 顔サイズと位置の調整
uvx --python 3.12 --from . profile-photo-processor photo.jpg output.jpg --face-ratio 0.20 --face-position 0.40
```

### オプション

| オプション | デフォルト | 説明 |
|-----------|-----------|------|
| `--size` | 1000 | 出力画像の最大サイズ（px） |
| `--bg-color` | e1e1e1 | 背景色（hex） |
| `--face-ratio` | 0.18 | 顔の高さが画像高さに占める割合 |
| `--face-position` | 0.42 | 顔の垂直位置（0=上端, 1=下端） |
| `--model` | isnet-general-use | 背景除去モデル |
| `--no-normalize` | - | 明るさ補正をスキップ |

### 背景除去モデル

- `isnet-general-use`: 高品質（推奨）
- `u2net`: 標準
- `u2net_human_seg`: 人物特化
- `u2netp`: 軽量版

## 処理内容

1. **顔検出**: OpenCV Haar Cascadeで顔を検出
2. **背景除去**: rembgで人物を切り出し
3. **エッジ処理**: モルフォロジー処理でエッジをシャープに
4. **配置計算**: 顔が中央に来るようスケール・位置を調整
5. **明るさ補正**: 暗い画像のみ自動補正（明るい画像はそのまま）
6. **出力**: JPEG形式で保存
