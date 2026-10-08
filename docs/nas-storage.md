# NAS保存とVRMプレビュー生成

2026-10-09更新。**本書がNAS保存方針の正本**。過去の「配布ZIP原本を残す」「zstd確定」は旧方針であり、適用しない。

## 基本原則

- **保存するモデル本体は人型VRMのみ。** ダウンロードがZIPでも、内部の`.vrm`をモデル単位に分離して保存する。元の配布ZIP、編集用データ、非人型は永続保存しない。
- **VRMから全身Tポーズと顔の正面WebPを各1枚生成**し、モデルと同じカタログIDで保存する。画像は検索・一覧表示用にZIP外に置く。
- モデルの識別はファイル名だけに頼らず、`index.jsonl`へID、名前、作者、配布元、規約URL、元VRMのSHA-256、圧縮方式、ファイル・画像パスを記録する。
- 形状が不明なものは無料・取得条件を確認したうえで一時取得して検査可能。画像生成に失敗した場合は理由を記録して個別再試行し、**別モデルの画像で代用しない**。
- 圧縮は元VRMのバイト列を完全に復元できる可逆形式だけを使う。実際の展開データのSHA-256が一致することが保存条件。

## 保存構成

```text
/mnt/hdd/vrm/
├── models/
│   ├── <catalog_id>.zip         # ZIPを採用した場合: 内部は <catalog_id>.vrm 1個
│   └── <catalog_id>.vrm.zst     # zstd採用の場合（同じIDで両方は保存しない）
├── previews/
│   ├── <catalog_id>-tpose.webp  # 全身正面Tポーズ、768 × 1024
│   └── <catalog_id>-face.webp   # 顔正面、512 × 512
└── index.jsonl                  # モデルと画像の対応表
```

この構成は**提案する実保存先**であり、実ファイルはまだNASへ配置していない。登録IDは正本`data/models.json`および`data/collections/*.json`の`id`と一致させる。名前に日本語が含まれていてもIDはASCIIなのでパスが安定する。

## 圧縮形式の決定

| 比較する形式 | 圧縮設定 | 特性 |
| --- | --- | --- |
| ZIP | Deflate、level 6、1 VRM/ZIP | OS標準ツール等で扱いやすい |
| zstd | level 10、各VRM単体 | 高速な可逆圧縮に向く |

**当面はZIPを暫定デフォルトとし、実測後に最終決定する。** VRMには既に圧縮されたテクスチャ等が含まれることがあり、zstdの容量メリットは未計測である。

3件以上の実VRMを、できれば複数の制作者・テクスチャ規模から選んで比較する。

```bash
python3 scripts/benchmark_vrm_compression.py /tmp/a.vrm /tmp/b.vrm /tmp/c.vrm
```

測定するのはVRMの元サイズ・圧縮後サイズ・処理時間・**復元SHA-256一致**。ZIPの追加容量が、モデル元サイズ合計の**3%以内**なら互換性優先でZIP、それを超えればzstdを採用する。3件未満、またはzstdコマンドがない場合は結論を保留する。結果は実機検証記録に残す。どちらを採用しても**全モデルを同じ形式に統一**し、重複した別形式は常用保管しない。

異なるカタログIDでVRM SHA-256が完全一致した場合、同一NASファイルシステムならハードリンクでの重複排除を**後続の最適化候補**とする（現行の保存スクリプトはまだ自動重複排除しない）。

## 自動プレビュー作成

`tools/vrm-preview/`に、three.js・`@pixiv/three-vrm`・Playwright・sharpを利用したローカル撮影処理を用意する。VRMファイルはローカルHTTPサーバーから読み込み、外部へ送信しない。VRM 0.xは正面方向を補正し、normalized humanoidのTポーズを試みる。顔は頭部ボーンの位置を基準に撮影する。

```bash
cd tools/vrm-preview
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install
node generate.mjs --vrm /tmp/sample.vrm --id <catalog_id> \
    --out-dir /tmp/vrm-previews --browser /usr/bin/chromium
cd ../..
```

生成されるのは `<catalog_id>-tpose.webp`、`<catalog_id>-face.webp`、**`<catalog_id>-previews.json`**。最後のJSONに元VRMのSHA-256、画像名・画素サイズを含め、取り違えを防ぐ。正面はVRM座標系に準拠した標準カメラとする。

**自動生成は必ずしも全モデルで成功しない。** 頭部ボーン欠損、特殊な骨格、髪やアクセサリーの遮蔽、顔の画角、WebGLソフトウェアレンダリングの互換性などは実機で確認する。表示不可のモデルはサムネイルの代用を捏造せず、要手動対応として記録する。VRMのTポーズ画像はモデルの姿勢を表示したもので、VRMバイナリそのものは編集しない。

## 検証してNASへ保存

実機で人型と判断でき、配布・利用条件が確認できたモデルだけに適用する。

```bash
python3 scripts/inspect_vrm.py /tmp/sample.vrm
python3 scripts/archive_vrm.py \
  --id <catalog_id> --vrm /tmp/sample.vrm \
  --previews /tmp/vrm-previews \
  --nas-root /mnt/hdd/vrm --format zip --confirm-humanoid
```

圧縮方式の測定でzstdを選択した場合は`--format zstd`。元ZIP内のパスが判明している場合は`--archive-member 'folder/model.vrm'`を追加する。

保存処理は次の条件を満たした場合だけ索引を更新する。

1. カタログIDが正本JSONに**一意に存在**する。元VRMは`inspect_vrm.py`でVRMとして認識できる。
2. 画像2枚がWebPであり、プレビュー生成JSONの`catalog_id`、**元VRMのSHA-256**、画像名とサイズが一致する。
3. ZIPまたはzstdから復元したVRMのSHA-256が元VRMと一致する。
4. ID別の圧縮VRMとWebPを保存し、索引`index.jsonl`を原子的に更新する。既存の同一IDがあるときは黙って上書きせず停止する。

索引には`catalog_id`、`name`、`publisher`、`stored_path`、`compression`、`vrm_sha256`、`archive_sha256`、`vrm_size_bytes`、`stored_size_bytes`、`vrm_version`、`source_url`、`license_url`、`distribution_filename`、`archive_member_path`、`retrieved_at`、`previews.tpose/face.path/sha256`を含める。

一時取得した元ZIP、VRM、PNG等の中間画像は**検証完了後に作業機から消去する運用**とする。現行保存スクリプトは取得・一時ファイルの自動消去までは担当せず、実機バッチ処理側が担う。モデル本体・画像・索引はNASに保持し、GitHubへモデル本体やサムネイルはコミットしない。

## 実行状況

- **完了**：保存仕様、圧縮比較スクリプト、Tポーズ・顔WebP生成ツール、対応付けを検証する保存スクリプトのソースをリポジトリに追加。
- **未完了**：VRM実物を用いた圧縮率比較、npm依存の導入、WebGLによる画像生成の実機テスト、NASへの保存。GitHub ActionsやRDCは使わず、後日のHermes Agent実機検証で行う。
