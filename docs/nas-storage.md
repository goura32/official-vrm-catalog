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
│   ├── <catalog_id>.zip         # ZIPを採用した場合: 内部は model.vrm 1個
│   └── <catalog_id>.vrm.zst     # zstd採用の場合（同じIDで両方は保存しない）
├── previews/
│   ├── <catalog_id>-tpose.webp  # 全身正面Tポーズ、768 × 1024
│   └── <catalog_id>-face.webp   # 顔正面、512 × 512
└── index.jsonl                  # モデルと画像の対応表
```

この構成は保存仕様であり、実際の配置状況は本書末尾と[実機検証レポート](hermes-bulk-run-results.md)を参照する。登録IDは正本`data/models.json`および`data/collections/*.json`の`id`と一致させる。名前に日本語が含まれていてもIDはASCIIなのでパスが安定する。

## 圧縮形式の決定

| 比較する形式 | 圧縮設定 | 特性 |
| --- | --- | --- |
| ZIP | Deflate、level 6、1 VRM/ZIP | OS標準ツール等で扱いやすい |
| zstd | level 10、各VRM単体 | 高速な可逆圧縮に向く |

**ZIPを実機採用済み。** 2026-10-09の3件実測では、zstdとの差は元VRMの合計サイズに対して1.2455%であり、3%基準以内だったため、互換性を優先してZIPに統一した。既存87件もZIPで保存・監査済み。後続の同じNAS索引では形式比較をやり直さず、ZIPを使用する。詳細は[実機検証レポート](hermes-bulk-run-results.md)。

3件以上の実VRMを、できれば複数の制作者・テクスチャ規模から選んで比較する。

```bash
python3 scripts/benchmark_vrm_compression.py /tmp/a.vrm /tmp/b.vrm /tmp/c.vrm
```

測定するのはVRMの元サイズ・圧縮後サイズ・処理時間・**復元SHA-256一致**。ZIPの追加容量が、モデル元サイズ合計の**3%以内**なら互換性優先でZIP、それを超えればzstdを採用する。3件未満、またはzstdコマンドがない場合は結論を保留する。結果は実機検証記録に残す。どちらを採用しても**全モデルを同じ形式に統一**し、重複した別形式は常用保管しない。

異なるカタログIDでVRM SHA-256が完全一致した場合、**保存スクリプトは同一NASファイルシステム上の圧縮ファイルをハードリンクで共有**する。同一データを異なる名前で登録でき、モデル名・出典等はIDごとの索引で保持する。ZIP内のVRM名はID共通の`model.vrm`とし、ZIP外側のファイル名と索引でIDを識別する。ハードリンクできない場合は個別に圧縮保存する。

## 自動プレビュー作成

`tools/vrm-preview/`に、three.js・`@pixiv/three-vrm`・Playwright・sharpを利用したローカル撮影処理を用意する。VRMファイルはローカルHTTPサーバーから読み込み、外部へ送信しない。VRM 0.xは正面方向を補正し、normalized humanoidのTポーズを試みる。顔は頭部ボーンの位置を基準に撮影する。

```bash
cd tools/vrm-preview
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install
node generate.mjs --vrm /tmp/sample.vrm --id <catalog_id> \
    --out-dir /tmp/vrm-previews --browser /usr/bin/chromium
cd ../..
```

モデルの正面方向や頭部ボーン位置が標準カメラに合わない場合に限り、`--front-yaw-deg`（-360〜360度）、`--face-y-offset-frac`（全身高に対する顔中心の補正、-1〜1）、`--face-height-frac`（顔画像の縦画角、0.1〜1）を指定できる。補正後も全身Tポーズと顔を目視し、両方が適切でないモデルは保存しない。

生成されるのは `<catalog_id>-tpose.webp`、`<catalog_id>-face.webp`、**`<catalog_id>-previews.json`**。最後のJSONに元VRMのSHA-256、画像名・画素サイズ・**画像ごとのSHA-256**を含め、取り違えや生成後のすり替わりを検知する。正面はVRM座標系に準拠した標準カメラとする。

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

過去の比較でZIP採用を決定したため、同一NASでは原則`--format zip`を継続する。異なる圧縮方式を混在させない。元ZIP内のパスが判明している場合は`--archive-member 'folder/model.vrm'`を追加する。

保存処理は次の条件を満たした場合だけ索引を更新する。

1. カタログIDが正本JSONに**一意に存在**し、既知の非人型リストに入っていない。元VRMは`inspect_vrm.py`でVRMとして認識できる。`--confirm-humanoid`は実機で外形を確認した担当者だけが指定する。
2. 画像2枚がWebPであり、プレビュー生成JSONの`catalog_id`、**元VRMのSHA-256**、画像名・寸法情報・**画像のSHA-256**が一致する。
3. ZIPまたはzstdから復元したVRMのSHA-256が元VRMと一致する。
4. ID別の圧縮VRMとWebPを保存し、**`.index.lock`による排他制御のもと**で索引`index.jsonl`を原子的に更新する。既存の同一IDがあるときは黙って上書きせず停止する。`.index.lock`は小さな管理用ファイルとして残す。

索引は保存済みVRM1体につき1行。索引には`catalog_id`、`name`、`publisher`、`stored_path`、`compression`、`vrm_sha256`、`archive_sha256`、`vrm_size_bytes`、`stored_size_bytes`、`vrm_version`、`source_url`、`license_url`、`distribution_filename`、`archive_member_path`、`retrieved_at`（元の取得日時が判明する場合のみ）、`archived_at`（NAS保管日時）、`previews.tpose/face.path/sha256`を含める。

一時取得した元ZIP、VRM、PNG等の中間画像は**検証完了後に作業機から消去する運用**とする。現行保存スクリプトは取得・一時ファイルの自動消去までは担当せず、実機バッチ処理側が担う。モデル本体・画像・索引はNASに保持し、GitHubへモデル本体やサムネイルはコミットしない。

## 検証用の最小テスト

`tests/test_nas_storage.py` は、NASやネットワークに触れず、一時フォルダ内の合成VRM・実WebP画像で保存処理を検証する。

```bash
python3 -m unittest discover -s tests -v
```

対象は、WebPヘッダーと実寸法、ZIPの可逆復元、**同一バイト列VRMのハードリンク共有**、画像の不整合や既知非人型の拒否、zstdがあればその可逆復元。**合成VRMは3D画像生成の動作テストには使えない**ため、レンダリング・カメラ画角・実データの入手可否は別途実機で検証する。

## NAS保存後の整合性再検証

`scripts/verify_nas.py`は読み取り専用で、圧縮VRMの展開SHA-256、保存先とカタログID、Tポーズ・顔WebPの寸法・SHA-256、索引ID重複、保存形式の混在を検査する。

```bash
python3 scripts/verify_nas.py --nas-root /mnt/hdd/vrm
```

`ok: true`かつ`errors: []`であることをNAS処理の完了条件とする。**実行するまで検査済みと記載しない**。実機作業の継続指示は[Hermes Agent R1/R2・R3完了後の一括プロンプト](hermes-bulk-resume.md)へ集約し、保存済みIDと権利保留IDを再処理しない。

## 実行状況

- **完了**：ZIP Deflate level 6を統一採用。NASにはR3 87件、R1/R2 243件、ToxSam 7件、VRM公式サンプル2件、計339件のVRM ZIPとWebPプレビュー678枚を保存。最終`verify_nas.py`監査は`ok: true`、`errors: []`、形式はZIPのみ。今回開始時338件と当初330件の索引行は不変。
- **形状・プレビュー**：R3は88実VRM中87保存。R1/R2は400実VRM中397件を描画し、243人型保存、150非人型除外、4件形状保留。今回の追加描画13件は人型9、非人型4。Chubby Tubby Catは頭・胴・両腕・両脚の二足人型。各保存物の実サイズ、SHA-256、プレビュー監査は[実機検証レポート](hermes-bulk-run-results.md)を参照。
- **保留・未完了**：R3-229のプレビュー品質保留、従来の権利保留に加えて、今回19件の埋込権利矛盾、NeonGlitch86のリダイレクト拒否2件、季節系のdweb.link 429がある。Halloween/Xmas 001は履歴上各6回、Halloween 002/003、Xmas 002、Halloween 004は各初回+1回で自動取得を終了。Halloween 005は2026-10-09 01:24:33.662302 UTCの初回429後、1回の再試行枠が残る。最新host期限は2026-10-09 01:39:33.662302 UTC。残る133件は未試行。期限中は同hostの初回要求もすべてネットワークなしで延期する。R1/R2/R3以外の797件のうち756件は直接VRM未試行。Actions/RDCは使用していない。
