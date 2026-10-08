# Hermes Agent 一括実機検証 — 実績と再開チェックポイント

基準ブランチ: `main`、開始時 HEAD `d15381bc9f63feb59a9a2395a2a41aff0d499a12`。作業開始時に `origin/main` をfetchし、同一HEADを確認。
カタログ総件数: 1,297件。

## 実績

- 100Avatars R3の100件すべてを作者プレビューで確認。12件は明確な非人型として取得前に除外し、残る88件を人型形状と確認した。
- R3の88モデルを実取得。うちこの連続バッチで新規取得・検査・描画したものは85件、先行実機サンプルが3件。全88件でGLB v2、VRM 0.x、埋込CC0メタデータを確認。
- 新規85件は全身Tポーズ768×1024、顔512×512のWebPとprovenance manifestを生成。全画像の寸法・ハッシュを検証し、接触シートで目視。うち84件は保存品質を通過、`polygonalmind-100avatars-r3-229` 1件は全身と顔を同時に正面化できず保存保留（人型形状自体は確認済み）。
- 目視で向き/画角を補正した4モデル（210/212のyaw、220/282の顔中心・高さ）。生成器にオプションを追加し、他モデルの既定画角は変更していない。
- NAS索引には計87件（先行3件＋今回84件）を保存。ZIP 87件、WebP 174枚、圧縮方式混在なし。
- NAS上のVRM未圧縮合計は512,245,233 bytes、ZIP合計は331,106,920 bytes。削減181,138,313 bytes、圧縮による容量削減率35.3616%。WebP合計3,582,798 bytes、index.jsonl 98,365 bytes。プレビューと索引を含むNASペイロード合計は334,788,083 bytes（ロックファイルは空）。
- 最終 `verify_nas.py`: `ok: true`、`errors: []`、entries 87、previews 174、formats `zip`。

## 圧縮形式

実VRM 3件（未圧縮21,888,509 bytes）をZIP Deflate level 6とzstd level 10で比較。ZIP 13,986,252 bytes、zstd 13,713,638 bytesで、ZIPの追加容量は元サイズ合計比1.2455%。規定の3%以内のため互換性を優先してZIPに統一した。NAS上の実保存でも全87件ZIPのみである。

## 保留・失敗・未処理

- 非人型除外12件（R3）。作者プレビューで判定できたため、VRMは取得していない。
- 正面プレビュー品質保留1件: `polygonalmind-100avatars-r3-229`。yaw 0/90/180/270を試したが、正面全身Tポーズと顔を両方満たす画像にならず、NASには保存していない。再確認用の一時VRMとログは実行機の作業領域にある。
- 権利保留1件: `mjmoonbow-skinnie1-5-41eb4fe`。公開元のCC0説明とVRM埋込`Redistribution_Prohibited`が矛盾したため、VRMと生成画像を作業領域から削除し保存しない。
- 認証待ち0件、恒久的なVRM取得失敗0件。初回はnpm依存不足により一部レンダーが失敗したが、依存導入後に再実行し解消。`npm install`は3件のhigh severity advisoryを表示したため、依存更新は行っていない。
- R3実施時点ではR3以外の1,197レコードが未処理だった。その後のR1/R2継続実機検証の結果は本書末尾に記録する。
- R3 commit時点の選別IDリストは人型候補302件、非人型候補93件、未判定902件。最新のR1/R2反映後の件数は末尾の継続実績を参照。

## NAS障害と復旧記録

`/mnt/hdd/vrm` は `nas1.local:/volume1/hdd` のNFSv3マウント。保存開始時に `.index.lock` がモード000で、ACL上は書き込みのみ可能だった。`archive_vrm.py` が未使用の読取り権限も要求する `a+b` で開いてPermissionErrorになったため、排他ロックは書き込み専用 `ab` で開くよう最小修正した。モデル201の実保存と監査で修正を確認。

後続処理ではNFSの一時I/O待ちが発生し、一件が300秒タイムアウトした。ID 278のZIP/WebPは既にNASに存在したので、元VRM・展開SHA-256・画像ハッシュ/寸法・ZIPメンバーをローカル作業物およびNAS実体と照合後、ロック下でindex行を復旧した。空の孤立 `.index-*` 一時ファイルは監査後に削除。復旧後に独立して `verify_nas.py` を再実行し、87件すべて整合することを確認した。強制アンマウントや未確認ファイルの削除はしていない。

## 検証・反映

- `python3 scripts/validate.py`: 1,297モデル、ID重複なし、選別件数302/93/902で成功。
- `python3 -m unittest discover -s tests -v`: 4件成功。
- `node --check tools/vrm-preview/generate.mjs`、`node --check tools/vrm-preview/renderer.js`、`python3 -m py_compile scripts/archive_vrm.py` 成功。
- `git diff --check`: 成功。`scripts/validate.py` は1,297件・ID一意性・選別件数302/93/902で成功。
- GitHub Actions、RDC、外部AI APIへのVRM/画像送信は使用していない。VRM/ZIP/WebP実体と作業ログはGitHubに含めない。

## ローカルチェックポイントと再開

実行機に次のチェックポイントを残した（GitHubには含めない）。

- `/home/ws2/.local/state/official-vrm-catalog/r3-batch-checkpoint.jsonl`
- `/home/ws2/.local/state/official-vrm-catalog/r3-batch-visual-review.json`
- `/home/ws2/.local/state/official-vrm-catalog/r3-nas-archive-checkpoint.jsonl`
- `/home/ws2/.local/state/official-vrm-catalog/r3-nas-archive-retry.log`

NASの次回処理前に `findmnt -T /mnt/hdd/vrm` と `python3 scripts/verify_nas.py --nas-root /mnt/hdd/vrm` を実行する。R1/R2継続処理後もR3 87行はSHA-256で不変を確認。未実体検証の残り797レコードは次回の対象候補とし、Actions/RDCは使わない。

## R1/R2継続実機検証（2026-10-08）

- 開始時は `main` の `35ac3d8c78d07f9a7e037a5a76f2cca23181a9bb`。作者リポジトリの固定ソースコミット `ff07c2ad0017819c4e5366656ee1e5bcc4029bd4` で正本400件すべてのVRMパスと配布サイズが一致することを確認した。作者READMEは無改変モデルの再販売を避けるよう求めており、R3のCC0をR1/R2へ適用していない。保存物はNAS内の私的アーカイブで、公開再配布しない。
- 400件を実取得・GLB v2/VRM 0.xのメタデータ検査。397件のTポーズ/顔WebPを生成し、各IDの接触シートで外形・正面・画角を確認。結果は人型243件（先行NAS保存2件を含む）、非人型150件、形状判定保留4件（`polygonalmind-100avatars-013-standard`, `polygonalmind-100avatars-013-voxel`, `polygonalmind-100avatars-034-standard`, `polygonalmind-100avatars-034-voxel`）、権利保留3件。取得失敗0、無効VRM 0、描画失敗0。人型243件のうち241件をこの継続処理で新規保存した。
- 非人型PNG候補資料はモデル外形ではなくUV/アルベドテクスチャだったため、事前形状除外には使わず実VRMを個別確認した。対象PNGは199件を取得、055は5 MiB安全上限を超えた。これはVRM取得失敗には数えない。
- 権利保留: `polygonalmind-100avatars-132-standard` と `polygonalmind-100avatars-196-standard` は埋込作者が `CryptoAvatars` とカタログの作者表示に一致せず、`polygonalmind-100avatars-166-voxel` は埋込`Redistribution_Prohibited`。3件ともNAS保存せず。`PolygonalMind` と `Polygonal Mind` の表記差で最初に保留した014-standard/021-standardは、同一作者表記と確認して再処理し、最終保留には含めない。
- R1/R2 NAS保存243件の未圧縮合計664,548,692 bytes、ZIP合計237,087,874 bytes、削減427,460,818 bytes（64.3235%）。Tポーズ/顔WebP合計4,432,050 bytes。R3を含む累計330件は未圧縮1,176,793,925 bytes、ZIP568,194,794 bytes、削減608,599,131 bytes（51.7167%）、WebP8,014,848 bytes、`index.jsonl`384,293 bytes。
- 最終 `verify_nas.py`: `ok: true`、`errors: []`、entries330、previews660、formats `zip`。R3 87件の索引行SHA-256は開始時と一致。GitHub Actions/RDCおよび別個の外部AI APIは使用せず、VRMの取得・検査・描画はローカル実行、プレビュー目視はHermes組込み視覚機能で実施。GitHubにはVRM/ZIP/WebPやローカル処理ログを含めない。
- 反映後の `python3 scripts/validate.py`: 1,297件一意、scope545/243/509で成功。`git diff --check`成功。既存ユニットテスト4件は作業開始前に成功し、実装コード・依存定義は変更していない。
- 最新選別件数は人型候補545、非人型243、未判定509（うちR1/R2の形状保留4・権利保留3）。R3/R1/R2以外の797レコードは今回未着手。

R1/R2のローカル再開・監査チェックポイント（GitHubへは含めない）:

- `/home/ws2/.local/state/official-vrm-catalog/r12-batch-checkpoint.jsonl`
- `/home/ws2/.local/state/official-vrm-catalog/r12-batch-visual-review.jsonl`
- `/home/ws2/.local/state/official-vrm-catalog/r12-nas-archive-checkpoint.jsonl`
- `/home/ws2/.local/state/official-vrm-catalog/r12-nas-baseline.json`
