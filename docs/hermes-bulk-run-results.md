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

## 季節系・作者/公式公開VRMの追加連続検証（2026-10-09）

- 開始時のカタログHEADは `2d45b3d3e5d84223fd2642f3158c03fdcbfa0bd1`。NAS開始監査は330 ZIP・660 WebPで成功し、開始時全330索引行のSHA-256をローカルに保存。R3 87件の索引行hashも前回baselineと一致。
- 季節系の権利・出所はToxSam本人が管理する `open-source-avatars` の固定main `0f9a1b2fd99894736563d55b2c9dc9125700d081` で再確認。Halloween Rising 60件とXmas Chibis 80件は、`projects.json` に `creator_id: Polygonal-Mind`、`is_public: true`、`license: CC0` があり、各索引には `format: VRM` と直接ファイルURLがある。ToxSam originals 10件とNeonGlitch86の公開CC0索引も同じ固定コミットでURLを全件照合。MJMoonbowは作者main `6af59479c61ab13b6caa96a9b915498489f2b9cd`、Numiniaは作者main `952a01987b2adefe305864956d59e8bf8cc9e5de` のCC0 LICENSE・ファイルパス/サイズを確認。
- dweb.linkの開始プローブ（季節コレクションのVRMと作者全身画像各2件）は4/4 HTTP 429。別の作者/公式URLを逐次処理した後、Halloween Rising 001とXmas Chibis 001の**元VRM URLのみを各1回**再試行したが、両方とも429、`Retry-After: 900`。H/Xの残り138件はネットワーク未試行としてcheckpointに保留し、代替ゲートウェイ・ミラー・プロキシは使用していない。ToxSam `King Mutatio` 1件も同じhostのため未試行。季節140件は未完了で、取得成功数に計上しない。
- 季節URLとは独立した直接公開候補30件を試行（先行pilot 1件を含む）：28件は取得・バイナリ検査に成功、16件は埋込権利情報の矛盾で破棄・保留、12件はプレビュー生成後に目視、2件は取得段階で保留。ToxSam Pinata直リンクは7件取得し、6人型を保存、`toxsam-original-bffd07cc-601` は両脚のない尾状下半身のため非人型。NeonGlitch86のSHAPEYは埋込 `allowRedistribution=false` で権利保留、NOT NYC AVATARとROCKETMANは作者索引のW3S直URLが別hostへリダイレクトするため追跡せず失敗記録。MJMoonbow 13件は公開CC0表示と実VRMの `Redistribution_Prohibited`、Numinia 2件は公開CC0と埋込 `CC_BY` の矛盾で全件保留。矛盾モデルの一時VRMは削除し、NAS保存していない。
- VRM仕様公式サンプル5件はVRM 1.0と埋込VRM Public Licenseを検査し、全件 `allowRedistribution=true`。Seed-sanとVRM1 Constraint Twistは人型・プレビュー合格として保存。Expressionsの2件はチェック模様、MToon UV Animation Testは記号画像の機能テストで非人型のため保存していない。今回の目視計12件（ToxSam 7体と公式サンプル5件）の分類は人型8・非人型4。ToxSam4件の顔画角は個別に `--face-height-frac 0.5` で再生成し、再目視で頭部切れを解消。
- NASには今回**8件**（ToxSam 6、VRM公式サンプル2）の人型VRMを個別ZIPとTポーズ/顔WebPで追加。累計338 ZIP・WebP676枚。未圧縮1,235,912,821 bytes、ZIP596,275,978 bytes、削減639,636,843 bytes（51.7542%）、WebP8,409,792 bytes、`index.jsonl`392,854 bytes。最終 `verify_nas.py`: `ok:true`, `errors:[]`, formats `zip`。開始時の330索引行は完全一致し、R3 87件も維持。
- 初回処理直後の選別IDは人型候補553、非人型247、未判定497。R1/R2/R3以外の797件は対象集合の件数であり、全件の保存対象ではない。初回時点で直接検証した30件と季節プローブ2件を除く765件は未試行だった。公開GitHub上のVRM本体/画像および一時ログはcommit対象外。GitHub Actions、RDC、外部AI API、別ホストへのリダイレクト追跡は使用していない。

個別ID結果（チェックポイントと正本JSONにも反映）:

- NAS保存した人型8件: `toxsam-original-c1def47c-0`, `toxsam-original-c1def47c-1`, `toxsam-original-bffd07cc-401`, `toxsam-original-bffd07cc-501`, `toxsam-original-bffd07cc-701`, `toxsam-original-bffd07cc-801`, `vrm-spec-seed-san`, `vrm-spec-vrm1-constraint-twist-sample`。
- 非人型4件: `toxsam-original-bffd07cc-601`, `vrm-spec-vrmc-materials-mtoon-uv-animation-test`, `vrm-spec-vrmc-vrm-expressions-isbinary-overridden`, `vrm-spec-vrmc-vrm-expressions-isbinary-overrides`。取得一時ファイルは判定後に破棄。
- 埋込権利矛盾16件（CC0索引/配布表示とVRM内部情報が不一致、全件NAS未保存）: `neonglitch86-shapey`; `numinia-starter-avatar-01`, `numinia-avatar-arla`; `mjmoonbow-goblin-elite-5-c01b977`, `mjmoonbow-goblin-elite-6-09083a0`, `mjmoonbow-kobold-2-1-deb8e71`, `mjmoonbow-kobold-3-1-4920055`, `mjmoonbow-kobold-4-adabccf`, `mjmoonbow-kobold-elite-0-c2e4251`, `mjmoonbow-minotaur-1-4-d310729`, `mjmoonbow-orc-0-1-cdf335c`, `mjmoonbow-orc-1-565b432`, `mjmoonbow-orc-2-04c4a67`, `mjmoonbow-skinnie3-1-f4b22ac`, `mjmoonbow-skinnie4-09f04df`, `mjmoonbow-wight-2-036d78f`。
- 取得失敗2件（作者W3S URLが別hostへredirect、クロスhost追跡を拒否）: `neonglitch86-index-1`, `neonglitch86-index-3`。季節系の最新429は`polygonalmind-halloween-rising-001`と`polygonalmind-xmas-chibis-001`、どちらも元URLのVRMリクエスト。季節系の残りはHalloween `002–060`とXmas `002–080`の138件が未試行。`toxsam-original-59202483-0`（King Mutatio）は同じdweb.link hostのため試行延期。

## Retry-After順守の再開とMJMoonbow追加候補（2026-10-09）

- Halloween/Xmas Chibis 001は履歴上各6回HTTP 429のため再試行終了。Halloween 002は初回`2026-10-08T23:15:06.179514Z`と許可済み再試行`23:37:16.736058Z`、Halloween 003は初回`2026-10-08T23:59:02.838137Z`と許可済み再試行`2026-10-09T00:15:38.771996Z`がともに429で終了。Xmas 002も初回`2026-10-08T23:15:07.128451Z`と許可済み再試行`2026-10-09T00:33:14.336020Z`が429で終了。Halloween 004は初回`2026-10-09T00:52:33.621620Z`と許可済み再試行`01:08:15.257082Z`、Halloween 005は初回`01:24:33.662302Z`と唯一の再試行`01:40:43.514108Z`、Halloween 006は初回`01:56:38.972893Z`と唯一の再試行`02:12:28.787714Z`がそれぞれ429（Retry-After: 900）。最新はHalloween 007の初回`02:28:25.603909Z`の429で、期限は`2026-10-09T02:43:25.603909Z`。H005/H006は再試行上限で終端化、H007は再試行枠が残る。残る季節131 IDとKing Mutatioは同host要求をネットワークなしで延期し、別ゲートウェイへ迂回しない。
- MJMoonbowの固定コミット`6af59479c61ab13b6caa96a9b915498489f2b9cd`にあるDragon画像4件を確認。Dragon 2/3は頭・胴・両腕・両脚のある人型候補、Dragon 8は翼以外の腕が画像で明瞭でないため保留、Dragon 9は四足の非人型として取得前に除外した。
- `mjmoonbow-dragon-2-775e309`、`mjmoonbow-dragon-3-dbede1e`、`mjmoonbow-dragon-8-4-b210d8d`は固定コミットの元VRMを直接取得・検査した。全件VRM 0.xで、埋込`licenseName=Redistribution_Prohibited`が公開リポジトリのCC0表示と矛盾したため、3件とも権利保留・プレビュー生成なし・一時VRM破棄・NAS未保存。正確なSHA-256と取得バイト数はローカルの`holiday-batch-mj-extra-worker.log`に記録。`mjmoonbow-dragon-9-3f69838`のVRM本体は取得していない。
- ToxSam作者索引にある未取得2体をプレビューで見直した。`toxsam-original-bffd07cc-1101`（Chubby Tubby Cat）は頭・胴・両腕・両脚の二足人型で、以前の非人型スコープ分類を訂正。CC0、VRM埋込author=ToxSam/licenseName=CC0、GLB v2/VRM 0.xを確認し、正面Tポーズと顔画像を目視後NASへ保存。`toxsam-original-bffd07cc-1201`（The Worm）は作者画像で手足のない虫状のため取得前に非人型除外を維持。
- 累計の直接公開候補は34件（32件取得・検査、19件権利保留、13件描画レビュー、うち人型9/非人型4、別host redirect拒否2）。季節9ユニークIDを含む直接URL試行は43 ID、R1/R2/R3以外の797件中754件は直接VRM未リクエスト。Halloween 005/006は各1回の再試行429で終端。今回のpostdeadline4 workerはH007初回要求1件の後、残る季節131 IDとKing Mutatioを`network_attempted:false`で延期し、追加HTTP要求0件。worker summaryは季節候補133 ID、seasonal network attempts 1、rate-limited collection 2、primary queue 0。取得・レンダー・NAS保存はなく、339 ZIP・678 WebPを維持。候補棚卸しでは非季節の未保存直接候補21 IDは19件の埋込権利矛盾と2件の別host redirect拒否で、追加取得可能な候補はなかった。選別数は人型556、非人型243、未判定498。
- 再開用ログ: `/home/ws2/.local/state/official-vrm-catalog/holiday-batch-resume-worker.log`、`holiday-batch-mj-extra-worker.log`、`holiday-batch-final-seasonal-worker.log`、`holiday-batch-postcooldown-worker.log`、`holiday-batch-postcooldown2-worker.log`、`holiday-batch-seasonal-retrycap-worker.log`、`holiday-batch-seasonal-retrycap2-worker.log`、`holiday-batch-seasonal-retrycap3-worker.log`、`holiday-batch-seasonal-retrycap4-worker.log`、`holiday-batch-seasonal-postcooldown-worker.log`、`holiday-batch-seasonal-postcooldown2-worker.log`、`holiday-batch-seasonal-postcooldown3-worker.log`、`holiday-batch-seasonal-postdeadline-worker.log`、`holiday-batch-seasonal-postdeadline2-worker.log`、`holiday-batch-seasonal-postdeadline3-worker.log`、`holiday-batch-seasonal-postdeadline4-worker.log`、`holiday-batch-toxsam-cat-worker.log`。統合checkpointは`holiday-batch-checkpoint.jsonl`、画面分類/固定commit根拠は`work/holiday-batch/source-validation.json`。当時のhost期限は`2026-10-09T02:43:25.603909Z`。期限後にH007を再試行するという当時の案は、本書末尾の最新HTTP 429方針変更によって撤回。

再開用チェックポイント（GitHubには含めない）:

- `/home/ws2/.local/state/official-vrm-catalog/holiday-batch-checkpoint.jsonl`
- `/home/ws2/.local/state/official-vrm-catalog/holiday-batch-visual-review.jsonl`
- `/home/ws2/.local/state/official-vrm-catalog/holiday-batch-worker.log`
- `/home/ws2/.local/state/official-vrm-catalog/holiday-batch-resume-worker.log`
- `/home/ws2/.local/state/official-vrm-catalog/holiday-batch-mj-extra-worker.log`
- `/home/ws2/.local/state/official-vrm-catalog/holiday-batch-final-seasonal-worker.log`
- `/home/ws2/.local/state/official-vrm-catalog/holiday-batch-postcooldown-worker.log`
- `/home/ws2/.local/state/official-vrm-catalog/holiday-batch-postcooldown2-worker.log`
- `/home/ws2/.local/state/official-vrm-catalog/holiday-batch-seasonal-retrycap-worker.log`
- `/home/ws2/.local/state/official-vrm-catalog/holiday-batch-seasonal-retrycap2-worker.log`
- `/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/source-validation.json`
- `/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/nas-baseline.json`
- `/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/nas-baseline-before-final-archive.json`
- `/home/ws2/.local/state/official-vrm-catalog/run_open_cc0_batch.py`
- `/home/ws2/.local/state/official-vrm-catalog/run_mj_extra_batch.py`
- `/home/ws2/.local/state/official-vrm-catalog/run_seasonal_retry.py`

`2026-10-09T02:43:25.603909Z`は最後に記録されたRetry-After期限（履歴値）。最新指示によりdweb.linkは期限後も恒久的にアクセスしない。H007は初回429で再試行なしに終端化し、残る季節131 IDとKing Mutatioも要求しない。R1/R2/R3以外で直接VRM未試行の754 IDは権利と公式URLを確認し、既保存・非人型・権利保留を除外して継続する。

## HTTP 429方針変更（2026-10-09）

- 最新のユーザー指示を優先し、HTTP 429後の再試行を全面禁止。同じhostへの別IDの初回要求も含め、そのhostには以後アクセスしない。Retry-Afterは履歴記録のみとし、期限後にアクセスを再開しない。別gateway/mirrorへの迂回もしない。
- Halloween 007は`2026-10-09T02:28:25.603909Z`の初回HTTP 429で終端化し、1回も再試行していない。dweb.linkを恒久ブロックし、残る季節131 IDとToxSam King Mutatioを未要求のまま除外する。
- `run_open_cc0_batch.py`はcheckpoint内のHTTP 429 hostを再起動後も復元して、同hostの全要求をネットワーク前に抑止する。新規HTTP 429要求上限は1回（再試行0回）。2026-10-09T02:56:47Zのseasonal workerはprimary queue 0、seasonal target 132（未要求131件+King Mutatio）、seasonal network attempts 0で終了し、132件すべて`network_attempted:false`で記録。新たなHTTP要求・429はない。無通信の回帰テスト、`scripts/validate.py`、`git diff --check`は成功。
- 非季節の未保存直接候補21 IDは権利矛盾19件と別host redirect拒否2件で、追加取得可能候補は0件。よってこの更新で新規取得・NAS保存はない。NASは339 ZIP/678 WebPのまま。

## 2026-10-09 非季節直接配布の続行実機検証

- `/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/nonseasonal-direct-20261009/` の17件をバイナリ検査。12件は実VRMを描画し、頭・胴・両腕・両脚、全身Tポーズ、顔正面をカード単位で確認してNASへ保存した。5件は埋込権利情報によりプレビュー生成・保存を行わず保留した。
- 新規NAS保存12件：`pronama-kurei-kei-vrm`、`bandainamco-mirai-komachi`、つくよみちゃんタイプAの通常・スパッツ・Recotte Studio・着せ替え・マテリアル削減の輪郭線あり／なし10件。
- 権利保留5件：`tegnike-nikechan-v1`、`tegnike-nikechan-v2`、`tegnike-nikechan-v2-outerwear`、`aituber-onair-miko-normal`、`aituber-onair-miko-cheer`。前3件は埋込再配布禁止/`allowRedistribution=false`、後2件は埋込`Redistribution_Prohibited`。新しい許諾根拠がない限り再取得しない。
- TYC ZIPの「顔だけ輪郭線あり」余剰VRMはカタログIDへ対応付けず、保存していない。取得失敗0件、描画失敗0件、今回の非人型0件。
- NASは開始339 ZIP・678 WebPから、351 ZIP・702 WebPへ増加。今回分は未圧縮VRM 157,765,676 bytes、ZIP 128,134,928 bytes、WebP 391,474 bytes。全体は未圧縮1,396,293,609 bytes、ZIP 725,203,313 bytes、削減率48.0623%、WebP 8,828,344 bytes。
- 最終`verify_nas.py`は`ok:true`、`errors:[]`、entries351、previews702、formats `zip`。339件の開始時indexを新規12行から除外して再構成したSHA-256は`06e51fd04961c4d1963336b75047d19dee51d6390855c1ed7ca0d43bcb222f6d`で、開始時baselineと一致した。
- R1/R2/R3以外の797件の棚卸しは、保存21、確定非人型4、権利保留24、別hostリダイレクト拒否2、`dweb.link`恒久ブロック対象141、残り605は未試行または取得条件未確定。明示的な認証待ちは0件。HTTP 429後の再試行、`dweb.link`への新規要求、迂回ゲートウェイ/ミラーは行っていない。
- 選別リストは人型候補557、非人型243、未判定497。`pronama-kurei-kei-vrm`を実VRM描画確認に基づき人型候補へ追加した。
- 継続チェックポイントは`archive-checkpoint-20261009.jsonl`、`nas-baseline-after-nonseasonal-direct-20261009.json`、`batch-status.json`。取得元ZIP/VRMはNASへ原本保存せず、GitHubにも含めない。

## 2026-10-09 公式ページ候補とBOOTH取得可否の続行検証

- 公式ページ候補11件を確認した。LAUGH DiAMOND 4件は公式ZIPから実VRMを検査し、4件すべて人型・Tポーズ・顔プレビュー合格としてNASへ保存した。
- Kizuna AI 2件、Sony RAYNOS 3件、ZONe ぞん子1件は実VRMの埋込権利情報が再配布禁止または公式ページ条件と矛盾するため、6件すべてNAS未保存。新しい許諾根拠がない限り再取得しない。
- ENRAI遠雷燕は公式0円作品ページを確認したが、購入/ダウンロードに会員登録が必要なため、ログインせず`auth_required`として保留した。
- BOOTHは6件を代表プローブ（夢ノ結唱 POPY/ROSE、結月ゆかり麗、縦ロール、桜夜）した。各ページは¥0表示だったが、公開ダウンロードURLはHTTP 302で`/users/sign_in`へ遷移した。認証回避は行わず、6件を認証待ちとしてチェックポイントに記録した。残りのBOOTH無料商品へ無差別アクセスはしていない。
- NASは351 ZIP・702 WebPから355 ZIP・710 WebPへ増加。今回分は未圧縮VRM 38,660,116 bytes、ZIP 25,423,802 bytes、WebP 287,962 bytes。全体は未圧縮1,434,953,725 bytes、ZIP 750,627,115 bytes、削減率47.6898%、WebP 9,116,306 bytes。
- 最終`verify_nas.py`は`ok:true`、`errors:[]`、entries355、previews710、formats `zip`。351件の開始時indexを新規4行から除外したSHA-256は`06735d2ea2c9776c1fdc80b38957a0e902a27f61041ee8abe7b8bb03665c3375`で開始時baselineと一致した。
- R1/R2/R3以外の797件の現在棚卸しは、保存25、確定非人型4、権利保留30、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、明示的認証待ち6、残り589件が未試行または取得条件未確定。今回もHTTP 429後の再試行、`dweb.link`アクセス、認証回避は行っていない。
- 公式ページ続行チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/official-page-20261009/official-page-checkpoint-20261009.jsonl`、BOOTHプローブは`booth-probe-checkpoint-20261009.jsonl`、NAS baselineは`nas-baseline-after-official-page-20261009.json`。

## 2026-10-09 直接GitHub・BOOTH・VRoid Hubの追加棚卸し

- `hinzka/52blendshapes-for-VRoid-face`のmainをcommit `756f5abab7d2295ad5b5dbc2cd86972c388c48d2`へ固定し、女性/男性PerfectSync VRM 2件を実取得・検査した。両方ともサイズと固定ソースを照合し、GLB v2/VRM 0.x、人型候補の実体であることを確認した。
- 作者READMEは再配布・販売を許可し、VRoid公式サンプル利用条件も出力VRMの利用・配布を許可する一方、実VRMの埋込`licenseName=Redistribution_Prohibited`が矛盾するため、2件とも権利保留・プレビュー生成/NAS保存なし。女性SHA-256は`36d6d242999d580bd0d3bcd8656bb2d4d5d4839f187d8198226bda905e1d9114`、男性は`7526838f4a45086a1d0abb23e9f38ad3f0103889f1efa70d2605ef25e7e6ef99`。
- BOOTHの追加10商品ページ（12カタログID：ミニずん子/ずんだもん、NEW FEE 3種、パチモンしとちゃ2種、minamo、れん、天羽ソラ、ぱペコ、とべ～るくん）を確認した。全て商品ページは¥0だが、匿名の無料ダウンロードURLはHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。認証回避はせず、12件を認証待ちとして記録した。
- VRoid HubはAvatarSample_A、β AvatarSample_1、TOKYO6小春六花の3ページを匿名確認した。各ページでpixiv IDログインが表示され、匿名ダウンロードリンクを取得できなかったため、3件を認証待ちとして記録した。残りのVRoid Hub候補へログインなしの無差別アクセスは行っていない。
- NASは新規保存なし。355 ZIP・710 WebP、未圧縮1,434,953,725 bytes、ZIP 750,627,115 bytes、削減率47.6898%、WebP 9,116,306 bytesを維持した。
- R1/R2/R3以外の797件の棚卸しは、保存25、確定非人型4、権利保留32、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、明示的認証待ち22、残り571件が未試行または取得条件未確定。今回も429後の再試行、`dweb.link`、認証回避、ミラー/プロキシ迂回は行っていない。
- 追加チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/hinzka-direct-20261009/rights-checkpoint-20261009.jsonl`、`official-page-20261009/vroid-probe-checkpoint-20261009.jsonl`。

## 2026-10-09 NeonGlitch86権利確認の追加棚卸し

- NeonGlitch86公式GitHubリポジトリのREADMEとルート一覧を確認した。READMEはrawリンクのみで、LICENSEファイルは存在しなかった。
- `neonglitch86-shapey`（既存の埋込権利矛盾）と別hostリダイレクト拒否2件を除く33件を、バイナリ取得なしで`rights_unverified_hold`に分類した。許諾根拠がないため、VRM取得・描画・NAS保存は行っていない。
- NASは新規保存なし。797件の現在棚卸しは、保存25、確定非人型4、権利保留65（条件矛盾32、許諾未確認33）、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち35、VRoid Studioエクスポート専用23、残り502件が未試行または取得条件未確定。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/neonglitch86-rights-checkpoint-20261009.json`、`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/vroid-studio-export-checkpoint-20261009.json`、`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/vroid-hub-auth-checkpoint-20261009.json`。

## 2026-10-09 VRoid Hub残り13件の匿名確認

- AvatarSample_B/C、β AvatarSample_2/3/4、各ダークネス・制服バリエーション、TOKYO6夏色花梨/花隈千冬の計13ページを実ブラウザで一度だけ確認した。
- 全13件でpixiv IDログインが表示され、VRMダウンロードリンクは0件だった。利用ボタンや利用条件が表示されるページもあったが、ログインなしで実体取得できないため、13件を認証待ちに変更した。
- 認証回避、再試行ループ、ミラー/プロキシ利用、VRM取得・描画・NAS保存は行っていない。

## 2026-10-09 BOOTH追加10商品ページの匿名取得確認

- エルルナ、SpringSnow、Jessair Cute_Model、Libby、toi、CURRY、あまねType-1〜4、RomanticSpicaあいす、Pate's Oblivion Frii、Pyurin Bear Girlの10商品ページを確認した。無料ダウンロード対象は計20カタログIDに対応する。
- 無料ダウンロードリンクを各商品から直接確認し、代表10 URLを匿名要求したところ、全10件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、20件を認証待ちへ変更した。商品説明上の利用条件・再配布制限は各カタログnotesに保持した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち55、VRoid Studioエクスポート専用23、残り482件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009.json`。

## 2026-10-09 BOOTH追加12商品ページの匿名取得確認

- Pyurin Bear Girl系、standalone ALPHA試用版、いものアバター、夢ノ結唱 POPY/ROSE、結月ゆかり 麗、ふぁふぁ、V雪ちゃん、マツモトくん、フッキー、molzの12商品ページを確認した。無料ダウンロード対象は12カタログIDに対応する。
- 無料ダウンロードリンクを各商品から直接確認し、代表12 URLを匿名要求したところ、全12件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、12件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち67、VRoid Studioエクスポート専用23、残り470件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch2.json`。
