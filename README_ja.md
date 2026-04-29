# comfyui-yumil-mpm

[English](README.md) | 日本語

[Yumil MPM](https://github.com/maigonia/YumilMPM)と連携する [ComfyUI](https://github.com/comfyanonymous/ComfyUI) カスタムノードです。AI画像生成のプロンプト管理を効率化します。

## 必要なもの

- [Yumil MPM](https://github.com/maigonia/YumilMPM)

## インストール

### ComfyUI Manager

登録準備中です。現在は下記の手動インストールをご利用ください。

### 手動インストール

ComfyUI の `custom_nodes` フォルダにクローンします:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/maigonia/comfyui-yumil-mpm.git
cd comfyui-yumil-mpm
pip install -r requirements.txt
```

インストール後、ComfyUI を再起動してください。

## ノード一覧

### External Prompt Requester

**カテゴリ:** Yumil/API

Yumil MPM にプロンプト生成をリクエストします。Yumil MPM の On-Demand Generation が有効な間、ワークフローがこのノードを通るたびに Yumil MPM へ生成要求が送られ、自動生成された結果を受け取ります。最大10個のカテゴリ名を接続し、それぞれの生成結果を取得できます。

**セットアップ:**
1. Yumil MPM を起動します。
2. 左下の Generation パネル内にある **Demand** ボタンを押して On-Demand Generation を有効にします。

**入力:**
- `timeout_seconds` — リクエストタイムアウト（5〜600秒、デフォルト: 240）
- `prompt_1` 〜 `prompt_10` — プロンプトを取得するカテゴリ名

**出力:**
- `prompt_1` 〜 `prompt_10` — 各カテゴリの生成されたプロンプトテキスト

### Yumil Prompt Parser

**カテゴリ:** Yumil/Prompt

**主な用途:**
- プロンプトに含まれたファイルパスやパラメータを取得したいとき（ControlNet/IPAdapter の参照画像など）
- 複数のパスをまとめて1つのブロックで扱いたいとき（複数の参照画像など）
- パスとkey-valueパラメータ、テキストをセットで扱いたいとき

`###_Path(...).Value(...).Text(...)_###` 形式のパーサーブロックを含むプロンプトテキストを解析します。各要素（Path、Value、Text）は省略可能です。

- **Path** — カンマ区切りで複数のパスを指定可能（例: `Path(img0.png,img1.png)`）。画像に限らず任意のファイルパスを渡せます
- **Value** — カンマ区切りの `key=value` 形式でパラメータを自由に追加可能（例: `Value(strength=0.8,mode=ipadapter)`）
- **Text** — プロンプトテキスト。複数行対応

`Text()` を持つブロックはテキスト値に置換され、持たないブロックは除去されます。1つのプロンプトに複数のブロックが含まれていてもまとめてパースでき、各要素の中身はエスケープ不要で改行や特殊文字、ネストされた括弧もそのまま使えます。

**例:**
- `###_Path(img0.png,img1.png).Value(strength=0.8,mode=ipadapter).Text(hello)_###` — 複数パス、パラメータ、テキストを全て取得。プロンプト中で `hello` に置換
- `###_Path(img.png).Text(hello)_###` — パスとテキストを取得。`hello` に置換
- `###_Path(img.png)_###` — パスを取得。プロンプトからタグを除去
- `###_Value(mode=test).Text(hello)_###` — パスなしでパラメータとテキストを取得

**入力:**
- `prompt` — プロンプトテキスト（パーサーブロックを含む場合あり）

**出力:**
- `clean_text` — ブロックが置換/除去されたプロンプト
- `block_count` — 検出されたブロックの数
- `PARSED_DATA` — 下流ノード用の構造化データ

### Yumil Block Selector

**カテゴリ:** Yumil/Block

**主な用途:**
- パースされたブロックからパス、パラメータ、テキストを取り出したいとき
- パスを Yumil Image Loader や他のノードに渡したいとき
- パラメータを Yumil Value Reader で読み取りたいとき

解析データからインデックスを指定してブロックを1つ選択し、各コンポーネントを取り出します。`Path()` 内のカンマ区切りのパスは個別出力（最大4つ）に分割されます。Yumil Prompt Parser の `PARSED_DATA` を接続してください。異なるインデックスで複数インスタンスを使用すると、個別のブロックを取り出せます。

**入力:**
- `parsed_data` — Yumil Prompt Parser から接続
- `index` — ブロックインデックス（0始まり）

**出力:**
- `path_0` 〜 `path_3` — 個別のパス（存在しない場合は空文字列）
- `path_count` — ブロック内のパスの数
- `value` — key=value パラメータ文字列（そのまま）
- `text` — 関連テキスト

### Yumil Image Loader

**カテゴリ:** Yumil/Image

**主な用途:**
- Yumil Block Selector のパス出力から画像を読み込みたいとき
- ファイルパス文字列から画像を読み込みたいとき

ファイルパスから画像を1枚読み込みます。リサイズオプション付き。Yumil Block Selector のパス出力や、任意の STRING パスを接続できます。

**入力:**
- `path` — 画像ファイルパス
- `resize_mode` — `disabled`、`stretch`、`crop_center`、`pad_white`
- `target_total` — 幅+高さの合計目標値（例: SDXL なら 2048）。0 = リサイズなし。
- `width` / `height`（オプション）— サイズを直接指定。

**出力:**
- `image` — 読み込まれた画像テンソル
- `width` / `height` — 画像の寸法

### Yumil Value Reader

**カテゴリ:** Yumil/Block

**主な用途:**
- key=value 文字列から特定のパラメータを取得したいとき（例: `strength=0.8,mode=ipadapter`）
- 複数のキーを読み取る場合はインスタンスを複数使用

カンマ区切りの `key=value` 文字列から指定したキーの値を読み取ります。キーが見つからない場合はデフォルト値を返します。

**入力:**
- `value` — Block Selector からの key=value 文字列
- `key` — 取得するキー名
- `default_value` — キーが見つからない場合の戻り値（デフォルト: 空文字列）

**出力:**
- `result` — 指定したキーの値

### Yumil Lora Stripper

**カテゴリ:** Yumil/Prompt

テキストから `<lora:名前:重み>` タグを全て抽出・除去します。

**入力:**
- `text` — LoRA タグを含むテキスト

**出力:**
- `text` — LoRA タグが除去されたテキスト
- `loras` — 抽出された LoRA タグ（連結）

### Yumil Text Join

**カテゴリ:** Yumil/Prompt

最大7つのテキスト入力を指定した区切り文字で結合します。空の入力はスキップされます。

**入力:**
- `delimiter` — 区切り文字（デフォルト: `, `）
- `text_0` 〜 `text_6` — テキスト入力

**出力:**
- `text` — 結合結果

### Yumil Batch Save

**カテゴリ:** Yumil/IO

最大6枚の画像（JPEG）とオプションのテキストファイルを指定フォルダに保存します。

**入力:**
- `parent_folder` — 出力先ディレクトリのパス
- `folder_name` — サブフォルダ名（ファイル名のプレフィックスとしても使用）
- `text`（オプション）— `{folder_name}.txt` として保存
- `image_0` 〜 `image_5` — `{folder_name}_0.jpg` 等として保存

## テストの実行

```bash
cd tests
python -m pytest -v
```

## リンク

- [Yumil MPM (GitHub)](https://github.com/maigonia/YumilMPM)

## ライセンス

[MIT](LICENSE)
