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

## 2026-10-09 BOOTH追加12商品ページの匿名取得確認（第3バッチ）

- kanon MK3Dのくま、トナカイ、サンタ、うさぎ、ひよこ、ぶた、雪だるま、おばけ、ねこ、いぬ、洋梨、およびshop-perch縦ロールの12商品ページを確認した。無料ダウンロード対象は12カタログIDに対応する。
- 無料ダウンロードリンクを各商品から直接確認し、代表12 URLを匿名要求したところ、全12件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、12件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち79、VRoid Studioエクスポート専用23、残り458件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch3.json`。

## 2026-10-09 BOOTH追加12商品ページの匿名取得確認（第4バッチ）

- shop-perch東雲/時雨、A.P.姐さん/バトラー、そくかちゅう。シロ、はんぐおーばー、MilkS0ju、光昴舎ちえり、Doll House Nasha、めいどちゃん、くらんもモブ、Aidinの12商品ページを確認した。無料ダウンロード対象は関連15カタログIDに対応する。
- 無料ダウンロードリンクを各商品から直接確認し、代表12 URLを匿名要求したところ、全12件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連15件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち94、VRoid Studioエクスポート専用23、残り443件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch4.json`。

## 2026-10-09 BOOTH追加12商品ページの匿名取得確認（第5バッチ）

- 桜美堂まゆき、Hiraeth Dalji、teoteomeやんじゃった子、shop-perchのコトハ、コハク、エレイン、サキ、アイリーン、ヒスイ、ヒイラギ、スズナ、メティスの12商品ページを確認した。
- 無料ダウンロードリンクを各商品から直接確認し、代表12 URLを匿名要求したところ、全12件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、12件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち106、VRoid Studioエクスポート専用23、残り431件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch5.json`。

## 2026-10-09 BOOTH追加12商品ページの匿名取得確認（第6バッチ）

- shop-perchのユズ、ユウナギ、リーヤー、ROLOCKのMIKKE/ペストマスク/黒曜、RomanticSpicaりあん、Ryuneru、naralabぷろふぁむ、ふーふむクロエ、ゆるれあ春うさぎ、SN1572綴よだかの12商品ページを確認した。無料ダウンロード対象は関連16カタログIDに対応する。
- 無料ダウンロードリンクを各商品から直接確認し、代表12 URLを匿名要求したところ、全12件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連16件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち121、VRoid Studioエクスポート専用23、残り416件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch6.json`。

## 2026-10-09 BOOTH追加12商品ページの匿名取得確認（第7バッチ）

- Romandi、SAKURA、雪音りう、みやまる、Dollme 002/006/007/008/009/010、7a04m Model Pack 01、マシェリの12商品ページを確認した。無料ダウンロード対象は関連16カタログIDに対応する。
- 各商品から無料ダウンロードリンクを確認し、代表12 URLを匿名要求したところ、全12件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連16件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち137、VRoid Studioエクスポート専用23、残り400件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch7.json`。

## 2026-10-09 BOOTH追加12商品ページの匿名取得確認（第8バッチ）

- Openpose VRM、Openpose Full VRM、あいすくん通常/冬、VOLO、竹燕、魔法少女すもも、ドールシープ、杏、ルル、口遊いろは、Divaの12商品ページを確認した。無料ダウンロード対象は関連13カタログIDに対応する。
- 各商品から無料ダウンロードリンクを確認し、VRM版が複数ある商品は各代表URLを含めて13 URLを匿名要求したところ、全13件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連13件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち150、VRoid Studioエクスポート専用23、残り387件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch8.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第9バッチ）

- Mira、ダークあいす（VRM 1.0/0.x）、金欠な女の子、Yozora Neko、si0JK_NEMU、みつあみちゃん、内藤、かぼちゃん、爆睡ガール（シルバー）、teoteome衣装違い、平た胸族、美和子さんの12商品ページを確認した。無料ダウンロード対象は関連15カタログIDに対応する。
- 各商品から無料ダウンロードリンクを確認し、VRM/ZIP版が複数ある商品は各代表URLを含めて15 URLを匿名要求したところ、全15件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連15件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち165、VRoid Studioエクスポート専用23、残り372件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch9.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第10バッチ）

- 泉淳也、フロウ各版、彩瞳-Ayame-、ほしうさ、ぜろに、VRMアバターN、256穴子、リウォレ、ぷち尚也/ぷち柚希の12商品ページを確認した。無料ダウンロード対象は複数版を含む関連23カタログIDに対応する。
- 各商品から無料ダウンロードリンクを確認し、VRM/ZIP版が複数ある商品は各代表URLを含めて18 URLを匿名要求したところ、全18件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連23件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち188、VRoid Studioエクスポート専用23、残り349件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch10.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第11バッチ）

- 紬たか、PURIN、さよ、普通の女の子、UMEKO、Lua、ほねまる家（墓石）、Quanstella、鳥、 小動物系少女、ゆるねこ、たぬきおにぎりの12商品ページを確認した。無料ダウンロード対象は同梱複数VRMを含む関連15カタログIDに対応する。
- 各商品から無料ダウンロードリンクを確認し、VRM版が複数ある商品は各代表URLを含めて14 URLを匿名要求したところ、全14件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連15件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち203、VRoid Studioエクスポート専用23、残り334件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch11.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第12バッチ）

- 桜夜、たけぴよ、刃切切乃、Vroidshop 323、白ねこみみ、なお、Hatsuka、あにゃめ、熊野ゆちゃ、花圓、もやし、鬼の子キリの12商品ページを確認した。桜夜とHatsukaの複数VRM版を含む関連14カタログIDに対応する。
- 11ページの関連13件について代表12 URLを匿名要求したところ、全件HTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- `kuasa-anyame`の商品ページはHTTP 404（削除または移動）で、無料ダウンロードURLを確認できなかった。商品ページ404として記録し、再試行しない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、13件を認証待ち、1件を商品ページ404として記録した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち216、商品ページ404 1、VRoid Studioエクスポート専用23、残り320件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch12.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第13バッチ）

- こたつみかん、海羽、琴華、梓乃、杏澄、桜美堂のブルーベル/めいめい/かみや/みるっち/めぐみっち/まきのっち、クラゲの12商品ページを確認した。複数VRM版を含む関連17カタログIDに対応する。
- 各商品から無料ダウンロードリンクを確認し、14 URLを匿名要求したところ、全14件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連17件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち233、商品ページ404 1、VRoid Studioエクスポート専用23、残り303件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch13.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第14バッチ）

- エルフ弓使い、エルフ魔法使い、顔文字ブラザーズ、バレンタインミミック、たこやきちゃん/あかしやきくん、はんぺん/樫豆腐、Mira、煌星、ファラオ、マッスル鳩、マーモット、カマキリの12商品ページを確認した。複数VRM版を含む関連23カタログIDに対応する。
- 各商品から無料ダウンロードリンクを確認し、17 URLを匿名要求したところ、全17件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連23件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち256、商品ページ404 1、VRoid Studioエクスポート専用23、残り280件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch14.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第15バッチ）

- とりのともしび、めいどちゃん、teoteome青年/幼少/サングラス/代理配布/太陽妖精/天使/ピンク魔法少女/ノーア/うさぎ執事/あかおにの12商品ページを確認した。複数VRM版を含む関連43カタログIDに対応する。
- 各商品から無料ダウンロードリンクを確認し、12 URLを匿名要求したところ、全12件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連43件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち299、商品ページ404 1、VRoid Studioエクスポート専用23、残り237件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch15.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第16バッチ）

- teoteome賢い少年/夏向け姉/クリスマス/金メイド/ゴシック/性別不明、ming、Fine各版、桜美堂はぴっち/そうま/ももこ、ABENDGIFTアクシスの12商品ページを確認した。複数版を含む関連22カタログIDに対応する。
- 各商品から無料ダウンロードリンクを確認し、16 URLを匿名要求したところ、全16件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連22件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち321、商品ページ404 1、VRoid Studioエクスポート専用23、残り215件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch16.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第17バッチ）

- Bless Beeまゆら、DarthPockナイト、CLEAR Linkシエル/フルリール/スミレ/セドリック、完熟スライムの小屋のうさぎ/リトルデス/ぷちくらげ/ノッポスライム/プリンスライム/ヘンテココトリの12商品ページを確認した。関連34カタログIDに対応する。
- DarthPock商品ページはHTTP 404となったため、関連2件を`official_free_page_not_found`へ分類した。商品削除・移動の可能性があり、推測URLや代替ホストは試行していない。
- 残る11商品から代表ダウンロードURLを各1件、計11 URLを匿名要求したところ、全11件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連32件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち353、商品ページ404 3、VRoid Studioエクスポート専用23、残り181件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch17.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第18バッチ）

- Aisling、ぽめ助、ハーシーとチェイス、SiNE DOLL 473 SD、韓国海苔、ローポリRem、Niumuのしのっち/ぽす太/とろぽり、アシュリー、ChocoOrange、Wingsの12商品ページを確認した。版違いを含む関連13カタログIDに対応する。
- 各商品から代表無料ダウンロードリンクを確認し、12 URLを匿名要求したところ、全12件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連13件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち366、商品ページ404 3、VRoid Studioエクスポート専用23、残り168件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch18.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第19バッチ）

- ぴケの創作屋さんのYumeiro Rainy、Rainy Sunny、Aurora、sakura uniform、Clown doll、赤龍、Monster Animal、Steam Punk Cat、Monotone Blossom、Moon night、Snowflake、Steam Rabbitの12商品ページを確認した。
- 各商品から代表無料ダウンロードリンクを確認し、12 URLを匿名要求したところ、全12件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連12件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち378、商品ページ404 3、VRoid Studioエクスポート専用23、残り156件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch19.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第20バッチ）

- 夜凪の隠れ家のエミル/はる子/きらり/はやと・ひふみ/ルーナ/みんと、star-ria Mizki、沙七の水面ほむら、Avatar Shopらい/そら、melonzzamメイド、0CTR4D四號の12商品ページを確認した。版違い・複数VRMを含む関連15カタログIDに対応する。
- 各商品から代表無料ダウンロードリンクを確認し、12 URLを匿名要求したところ、全12件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連15件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち393、商品ページ404 3、VRoid Studioエクスポート専用23、残り141件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch20.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第21バッチ）

- じょわの店一般男性、baby0to1ロイドちゃん、Canomdarraアリシャーニャ、Hiraeth Samurai Boy、わんぱく八尺様、tamir-tg Belle、cecyliamun ARVENDAL/Wolf Boy、kasou-youhinのBREAK VENOM/還魂符/88 Cherry Steps/NOISE & FRILLSの12商品ページを確認した。複数VRMを含む関連13カタログIDに対応する。
- 各商品から代表無料ダウンロードリンクを確認し、12 URLを匿名要求したところ、全12件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連13件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち406、商品ページ404 3、VRoid Studioエクスポート専用23、残り128件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch21.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第22バッチ）

- kasou-youhin OXYGEN ERROR、ATOR爪モンスター/コマンドーうさぎ、潮音こまり、Miu、るてにうむそら、mossinpc Wanime/moss、すく～るろいど撫子、ぴよたそ、和菓子製作所あづは/ミニあづはの12商品ページを確認した。複数VRMを含む関連16カタログIDに対応する。
- 各商品から代表無料ダウンロードリンクを確認し、12 URLを匿名要求したところ、全12件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連16件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち422、商品ページ404 3、VRoid Studioエクスポート専用23、残り112件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch22.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第23バッチ）

- 墓アバター、ぽたみTECK、キモネーゼ、歌って踊れるスケルトン、ELISE、ラウロシ、Julius、ayame、たびマルのとり、あいすくりーす、ジョン・ドゥ通常/水着の12商品ページを確認した。色違いを含む関連26カタログIDに対応する。
- 各商品から代表無料ダウンロードリンクを確認し、12 URLを匿名要求したところ、全12件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連26件を認証待ちへ変更した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち448、商品ページ404 3、VRoid Studioエクスポート専用23、残り86件。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch23.json`。

## 2026-10-10 BOOTH追加12商品ページの匿名取得確認（第24バッチ）

- BUSY CREATIONSドナ/ドニー、にくねこちゃん、りこちゃん、Pippa、無題、Nanami、一般的なパンダ、siroihakumaiカジュアル/メイド/Ao/Savi、Shadow Shop Tomboyの12商品ページを確認した。版違い・色違いを含む関連18カタログIDに対応する。
- 各商品から代表無料ダウンロードリンクを確認し、12 URLを匿名要求したところ、全12件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、VRM取得・描画・NAS保存は行わず、関連18件を認証待ちへ変更した。
- 第24バッチ終了時点の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち466、商品ページ404 3、VRoid Studioエクスポート専用23、残り68件だった。
- チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261009-batch24.json`。

## 2026-10-10 BOOTH未試行候補の匿名取得確認（第25〜29バッチ）

- 第25〜29バッチで58商品ページを確認した。正本JSONの`official_free_distribution_listed_download_untested`は、文書の残68件より4行多い72行だったため、同一商品内の複数VRM・色違いを含む72カタログIDを重複なく対象化した。
- 商品ページ上の無料VRM/VRM入りZIPと代表無料ダウンロードURLを確認し、58 URLを匿名要求した。全58件がHTTP 302で`https://booth.pm/users/sign_in`へ遷移した。HTTP 429は発生していない。
- 認証回避、購入・ログイン、CAPTCHA突破、別host・ミラー・プロキシ経由の迂回は行っていない。VRM/GLB実体取得、埋込メタデータ検査、人型判定、WebP生成、NAS保存は0件。
- 履歴台帳の残68件はすべて認証待ちへ分類し、正本JSONの未試行ラベル72行も全件にアクセス条件を反映した。次回再プローブ対象には戻さない。
- ToxSamの`toxsam-original-bffd07cc-1201`（The Worm）は既存作者プレビューで手足のない虫状と確認できるため、Pinata gatewayへアクセスせず`creator_index_shape_non_humanoid_not_archived`へ分類した。
- 現在の797件棚卸しは、保存25、確定非人型4、権利保留65、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、認証待ち534、商品ページ404 3、VRoid Studioエクスポート専用23、未試行または取得条件未確定0。合計797。
- NASは355 ZIP・710 WebPから変化なし。第25〜29バッチのチェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-auth-checkpoint-20261010-batch25.json`〜`batch29.json`。照合差異と完了結果はローカル`unresolved-reconciliation-20261010.json`／`unresolved-reconciliation-result-20261010.json`に記録した。
- HTTP 429発生ホスト、`dweb.link`、既存権利保留65件、認証待ち534件は再アクセスしない。

## 2026-10-10 BOOTH認証済み実取得のパイロット・追加4バッチ

- `browser.use_real_profile: true` のローカル実プロファイルセッション `booth-real-profile-local-2` でBOOTHログイン状態を画面確認し、`pixellangel-dolly-devil` の `dolly_devil.vrm` を正規無料リンクから実取得した。`dolly_devil.vroid`、有料版、支援版は取得していない。
- パイロットはGLB v2/VRM 0.x、埋込権利、SHA-256、全身Tポーズ768×1024、顔512×512を検査・目視し、NASへ保存。パイロット成功後、追加4バッチを同じ低頻度の直列ブラウザー操作で実施した。
- 追加バッチ01は5商品・5 VRMを取得して検査・描画・目視確認し、5件をNAS保存した。追加バッチ02は5商品・5 VRMを取得し、人型2件を保存、丸いマスコット形状3件を非人型として保存しなかった。追加バッチ03は4商品・6 VRMを取得し、6件すべて人型・プレビュー合格として保存した。
- 追加バッチ04は1商品・8 VRMを取得・検査した。商品説明の商用可と、全8件の埋込`commercialUssageName=Disallow`/`Redistribution_Prohibited`が矛盾したため、描画・NAS保存を行わず8件を権利保留にした。
- 今回の合計は、商品ページ16（パイロット1＋追加15）、実VRM 25件、VRM検査25件、NAS新規14件、非人型3件、権利矛盾8件、HTTP 429 0件、ダウンロードバイト414,060,456 bytes。NASにはモデル単体ZIPとTポーズ/顔WebPだけを保存し、原本VRM・作業用画像は永続保存していない。
- NASは369 ZIP・738 WebP、未圧縮VRM 1,707,129,637 bytes、ZIP 918,813,099 bytes、削減788,316,538 bytes（46.1779%）、WebP 9,697,704 bytes。`python3 scripts/verify_nas.py --nas-root /mnt/hdd/vrm` は`ok:true`、`errors:[]`。
- 開始時355件の索引から今回の14 IDを除外して再計算したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`で開始時baselineと一致し、既存355件の索引行・実体を保護した。現行indexは369 ID一意で重複なし。
- R1/R2/R3を除く797件の現行排他的内訳は、NAS保存39、確定非人型4、作者索引由来の非人型1、埋込権利矛盾40、許諾未確認33、別hostリダイレクト拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち489、VRoid Hub認証待ち16、公式ページ認証未確認1、商品ページ404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797件で、未分類は0件。
- ローカルチェックポイントは`booth-authenticated-pilot-20261010.json`、`booth-authenticated-batch-20261010-01.json`〜`04.json`、`authenticated-summary-20261010.json`、`official-page-20261009/batch-status.json`。認証情報、Cookie、パスワード、トークン、認証付き一時URLは記録していない。

## 2026-10-10 BOOTH認証済み追加バッチ05

- `el-luna-monochrome`、Libby、toi、minamoの4商品ページを、ログイン済みBOOTHの正規無料ZIPリンクから処理した。ZIP内部を安全な相対パスとして検査し、VRMだけを一時抽出した。
- 5 VRMを検査。`el-luna-monochrome` LOW/HIGH、Libby、toiの4件は人型・Tポーズ・顔プレビュー合格としてNAS保存した。minamoは商品説明の法人利用・改変可と埋込`commercialUsage=personalNonProfit`・`modification=prohibited`が矛盾したため、描画・NAS保存を行わず権利保留にした。
- バッチ05はHTTP 429 0件、VRM取得バイト60,620,972 bytes。チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-05.json`。
- 現在の累計は、商品ページ20、実VRM30件、VRM検査30件、NAS新規18件、非人型3件、権利矛盾9件。NASは373 ZIP・746 WebP、未圧縮VRM 1,767,594,333 bytes、ZIP 958,932,726 bytes、削減808,661,607 bytes（45.7493%）、WebP 9,889,110 bytes。`verify_nas.py` は`ok:true`、`errors:[]`。
- 797件の現行内訳は、NAS保存43、確定非人型4、作者索引由来非人型1、埋込権利矛盾41、許諾未確認33、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち484、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。
- 旧355件の索引を今回の18新規IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。作業用VRM、ZIP、プレビューは監査後に削除済み。

## 2026-10-10 BOOTH認証済み追加バッチ06

- 夢ノ結唱 POPY、夢ノ結唱 ROSE、結月ゆかり 麗の3商品ページを、ログイン済みBOOTHの正規無料ZIPリンクから処理した。ZIP内部を安全な相対パスとして検査し、macOSの`__MACOSX/._*.vrm`メタデータはVRM実体として数えていない。
- 5実VRMを検査した。結月ゆかり 麗は公式ガイドラインの非商用・再配布禁止条件と埋込権利が整合し、人型・Tポーズ・顔プレビュー合格としてNAS保存した。POPY/ROSEの4実VRMは、商品ページが指定するガイドラインURLがHTTP 404で権利条件を確認できず、埋込`commercialUssageName=Disallow`/`Redistribution_Prohibited`も確認されたため、描画・NAS保存を行わず権利保留にした。
- バッチ06はHTTP 429 0件、VRM取得バイト84,723,200 bytes。チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-06.json`。
- 現在の累計は、商品ページ23、実VRM35件、VRM検査35件、NAS新規19件、非人型3件、権利矛盾13件。NASは374 ZIP・748 WebP、未圧縮VRM 1,783,693,525 bytes、ZIP 968,433,008 bytes、削減815,260,517 bytes（45.7063%）、WebP 9,934,886 bytes。`verify_nas.py` は`ok:true`、`errors:[]`。
- 797件の現行内訳は、NAS保存44、確定非人型4、作者索引由来非人型1、埋込権利矛盾43、許諾未確認33、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち481、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。
- 旧355件の索引を今回の19新規IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ07

- ふぁふぁ、U-Stella NEW FEE、パチモンしとちゃの3商品ページを、ログイン済みBOOTHの正規無料ZIPリンクから処理した。ZIP内部を安全な相対パスとして検査し、6実VRMを抽出した。
- 6件すべて人型・Tポーズ・顔プレビュー合格としてNAS保存した。ふぁふぁは埋込再配布禁止、U-Stellaは商用可・再配布禁止、パチモンしとちゃは個人活動収益化可・クレジット必須・再配布禁止の条件を確認し、商品説明と矛盾しないため保存した。
- バッチ07はHTTP 429 0件、VRM取得バイト222,453,224 bytes。チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-07.json`。
- 現在の累計は、商品ページ26、実VRM41件、VRM検査41件、NAS新規25件、非人型3件、権利矛盾13件。NASは380 ZIP・760 WebP、未圧縮VRM 2,228,599,973 bytes、ZIP 1,114,195,112 bytes、削減1,114,404,861 bytes（50.0047%）、WebP 10,601,030 bytes。`verify_nas.py` は`ok:true`、`errors:[]`。
- 797件の現行内訳は、NAS保存50、確定非人型4、作者索引由来非人型1、埋込権利矛盾43、許諾未確認33、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち475、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。
- 旧355件の索引を今回の25新規IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ08

- ミニ東北ずん子、ミニずんだもん、V雪ちゃんの3商品ページを、ログイン済みBOOTHの正規無料ZIPリンクから処理した。ZIP内部を安全な相対パスとして検査し、5実VRMを抽出した。
- ミニ東北ずん子とミニずんだもんは、0.x/1.0の両形式を検査・描画し、同一カタログIDにつきVRM 1.0版を代表保存した。V雪ちゃんは丸い雪だるま状マスコットで人型外形を満たさず、NAS保存しなかった。
- バッチ08はHTTP 429 0件、VRM取得バイト73,981,012 bytes。チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-08.json`。
- 現在の累計は、商品ページ29、実VRM51件、VRM検査51件、NAS新規27件、非人型5件、権利矛盾13件。NASは382 ZIP・764 WebP、未圧縮VRM 2,049,610,905 bytes、ZIP 1,073,021,894 bytes、削減976,589,011 bytes（47.6475%）、WebP 10,409,552 bytes。`verify_nas.py` は`ok:true`、`errors:[]`。
- 797件の現行内訳は、NAS保存52、確定非人型5、作者索引由来非人型1、埋込権利矛盾43、許諾未確認33、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち472、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。
- 旧355件の索引を今回の27新規IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ09

- 天羽ソラ、フッキー、Papecoの3商品ページを、ログイン済みBOOTHの正規無料ZIPリンクから処理した。ZIP内部を安全な相対パスとして検査し、3実VRMを抽出した。
- 天羽ソラは人型・Tポーズ・顔プレビュー合格としてNAS保存した。フッキーは平たい箱状マスコットで非人型のため保存しなかった。Papecoは人型形状を確認したが、商品独自規約と埋込`commercialUssageName=Disallow`/`Redistribution_Prohibited`の対応を確定できず権利保留にした。
- バッチ09はHTTP 429 0件、VRM取得バイト47,948,772 bytes。チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-09.json`。
- 現在の累計は、商品ページ32、実VRM54件、VRM検査54件、NAS新規28件、非人型6件、権利矛盾14件。NASは383 ZIP・766 WebP、未圧縮VRM 2,064,157,529 bytes、ZIP 1,081,151,851 bytes、削減983,005,678 bytes（47.6226%）、WebP 10,456,140 bytes。`verify_nas.py` は`ok:true`、`errors:[]`。
- 797件の現行内訳は、NAS保存53、確定非人型6、作者索引由来非人型1、埋込権利矛盾44、許諾未確認33、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち469、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。
- 旧355件の索引を今回の28新規IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ10

- シロ（VRM 0.x/1.0）、無料VTuber VRM、Anime Student、ちえり、Nashaの5商品ページを、ログイン済みBOOTHの正規無料ダウンロードリンクから処理した。ZIP内部を安全な相対パスとして検査し、6実VRMを抽出・検査した。無料.vroidや支援版・有料版は取得していない。
- 6件すべて人型・Tポーズ・顔プレビュー合格としてNAS保存した。シロはカタログ上のVRM 0.x/1.0の2 IDを別々に保存し、他4商品も各1件を保存した。埋込権利条件と商品説明に解消不能な矛盾はなく、HTTP 429は0件だった。
- バッチ10は5商品ページ、代表ダウンロード試行5件、カタログID6件、物理VRM6件、取得配布バイト87,400,313 bytes。チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-10.json`。
- 現在の累計は、商品ページ37、カタログID55件、物理VRM60件、VRM検査60件、NAS新規34件、非人型5件、権利矛盾14件。NASは389 ZIP・778 WebP、未圧縮VRM 2,152,217,193 bytes、ZIP 1,132,888,272 bytes、削減1,019,328,921 bytes（47.3618%）、WebP 10,725,714 bytes。`verify_nas.py` は`ok:true`、`errors:[]`。
- 797件の現行内訳は、NAS保存59、確定非人型6、作者索引由来非人型1、埋込権利矛盾44、許諾未確認33、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち463、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。
- 旧355件の索引を今回の34新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ11

- 「めいどちゃん」、Dalji、モブ、Aidin、まゆきの5商品ページを、ログイン済みBOOTHの正規無料ダウンロードから処理した。5 ZIPから8件の実VRMを抽出し、全8件を検査した。取得ZIP合計136,578,408 bytes、VRM合計115,614,636 bytes。
- 人型外形を確認した。めいどちゃん通常・黒・素体、Aidin、まゆきの5 IDをNAS保存した。DaljiはVRM 1.0の`avatarPermission=onlyAuthor`と商品説明のアバター利用案内を整合できず権利保留に変更し、今回作成されたZIPとプレビュー3点をNASから除去した。モブ1・モブ2は商品ページの配信商用利用可と、各VRMの`commercialUssageName=Disallow`が矛盾するため権利保留。HTTP 429は0件。
- バッチ11の内訳は5商品ページ、5ダウンロード試行、8カタログID、8実VRM検査、NAS純増5件、非人型0件、権利矛盾保留3件。詳細チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-11.json`。
- 現在の累計は、商品ページ42、カタログID63件、物理VRM68件、VRM検査68件、NAS新規39件、非人型5件、権利矛盾17件。NASは394 ZIP・788 WebP、未圧縮VRM 2,226,155,585 bytes、ZIP 1,184,838,694 bytes、WebP 10,916,702 bytes、削減1,041,316,891 bytes（46.7765%）。`verify_nas.py`は`ok:true`、`errors:[]`。
- 797件の現行内訳は、NAS保存64、確定非人型6、作者索引由来非人型1、埋込権利矛盾47、許諾未確認33、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち455、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。
- 旧355件の索引を今回の39新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ12

- サンタ、縦ロール、東雲、時雨、姐さん（ミニ）の5商品ページを、ログイン済みBOOTHの無料ダウンロード操作から処理した。無料の指定ファイル5点（4直接VRMと1 ZIP）を取得し、ZIPから編集用ファイルをNAS対象外にしてVRMのみ抽出。取得配布バイトは67,429,347 bytes、VRM総量は68,277,640 bytes。
- 姐さん（ミニ）は埋込権利値と商品規約が整合し、人型の全身Tポーズ・顔を目視確認してNAS保存した。残るサンタ、縦ロール、東雲、時雨は各VRMの`commercialUssageName=Disallow`（一部は`allowedUserName=OnlyAuthor`）と商品ページの商用/アバター利用許可が矛盾したため権利保留。これら4件はプレビュー生成・NAS保存を行わず、HTTP 429は0件。
- バッチ12は5商品ページ、5ダウンロード試行、5 catalog IDs、5実VRM検査、NAS純増1件、非人型0件、権利保留4件。詳細チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-12.json`。
- 現在の累計は、商品ページ47、カタログID68件、物理VRM73件、VRM検査73件、NAS新規40件、非人型5件、権利矛盾21件。NASは395 ZIP・790 WebP、未圧縮VRM 2,240,228,425 bytes、ZIP 1,191,786,216 bytes、WebP 10,966,518 bytes、削減1,048,442,209 bytes（46.8007%）。`verify_nas.py`は`ok:true`、`errors:[]`。
- 797件の現行内訳は、NAS保存65、確定非人型6、作者索引由来非人型1、埋込権利矛盾51、許諾未確認33、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち450、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。
- 旧355件の索引を今回の40新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ13

- バトラーちゃん（ミニ）、ちょっとやんじゃった子、コトハ、コハク、エレインの5商品ページを、ログイン済みBOOTHの無料選択肢から処理した。指定ファイル5点を取得し、ZIPから実VRM1件を安全に抽出。取得配布バイト79,194,038 bytes、物理VRM合計83,532,316 bytes。
- バトラーちゃん、やんじゃった子、コトハ、エレインの4 IDは人型・Tポーズ・顔プレビューを目視確認してNAS保存。やんじゃった子のVRM埋込CC0に商品説明上の追加制限は見当たらなかった。コハクはVRM 1.0の`avatarPermission=onlyAuthor`と商品ページの一般アバター利用許可が整合しないため権利保留とし、プレビュー/NAS保存を行わなかった。HTTP 429は0件。
- バッチ13は5商品ページ、5ダウンロード試行、5 ID、5実VRM検査、NAS純増4件、非人型0件、権利保留1件。詳細チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-13.json`。
- 現在の累計は商品ページ52、カタログID73件、物理VRM78件、検査78件、NAS新規44件、非人型5件、権利矛盾22件。NASは399 ZIP・798 WebP、未圧縮VRM 2,308,794,341 bytes、ZIP 1,234,050,813 bytes、WebP 11,163,116 bytes、削減1,074,743,528 bytes（46.55%）。`verify_nas.py`は`ok:true`、`errors:[]`。
- 797件の現行内訳はNAS保存69、確定非人型6、作者索引由来非人型1、埋込権利矛盾52、許諾未確認33、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち445、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。
- 旧355件の索引を今回の44新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ14

- サキ ver.2、アイリーン、ヒスイ ver.1.5、ヒイラギ、スズナの5商品ページから、無料版VRMを各1件取得・検査した。配布バイト合計78,223,396 bytes。商品説明は商用利用とアバター利用を許可する一方、全5 VRMは`allowedUserName=OnlyAuthor`/`commercialUssageName=Disallow`で権利条件が矛盾したため、5件とも保留。プレビュー生成・NAS保存は行わず、HTTP 429は0件。
- バッチ14は5商品ページ、5ダウンロード試行、5カタログID、5 VRM検査、NAS純増0件、非人型0件、権利保留5件。詳細チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-14.json`。
- 累計は商品ページ57、カタログID78件、物理VRM83件、検査83件、NAS新規44件、非人型5件、権利矛盾27件。NASは399 ZIP・798 WebP、未圧縮VRM 2,308,794,341 bytes、ZIP 1,234,050,813 bytes、WebP 11,163,116 bytes、削減1,074,743,528 bytes（46.55%）。`verify_nas.py`は`ok:true`、`errors:[]`。
- 797件の現行内訳はNAS保存69、確定非人型6、作者索引由来非人型1、埋込権利矛盾57、許諾未確認33、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち440、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。
- 旧355件の索引を今回の44新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ15

- RomanticSpicaのりあん、6666669 (ROLOCK)のMIKKE・ペストマスクちゃん・黒曜の4商品ページを処理。7件の無料ダウンロード選択（直接VRM 6件、黒曜ZIP 1件）から8カタログID分・物理VRM 8件を検査した。転送バイト109,867,725、ZIP内展開後のVRM総量122,082,220 bytes。HTTP 429は0件。
- MIKKE、黒曜0.x/1.0、りあん通常・素体1.0の5 IDは埋込条件と商品条件を確認し、人型Tポーズ・顔を目視してNAS保存。ペストマスクちゃんはローブ状で両腕・両脚を確認できないため非人型として除外。りあん通常・素体0.xは商品ページが個人収益化配信を許可する一方、埋込`commercialUssageName=Disallow`のため権利保留とし、NAS保存しなかった。
- バッチ15は4商品ページ、7ダウンロード試行、8カタログID、8 VRM検査、NAS純増5件、非人型1件、権利保留2件。詳細チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-15.json`。
- 累計は商品ページ61、カタログID86件、物理VRM91件、検査91件、NAS新規49件、非人型6件、権利矛盾29件。NASは404 ZIP・808 WebP、未圧縮VRM 2,391,025,157 bytes、ZIP 1,279,715,344 bytes、WebP 11,356,652 bytes、削減1,111,309,813 bytes（46.4784%）。`verify_nas.py`は`ok:true`、`errors:[]`。
- 797件の現行内訳はNAS保存74、実バイナリ非人型7、作者索引由来非人型1、埋込権利矛盾59、許諾未確認33、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち432、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。別軸の形状選別は人型候補557、非人型244、未判定496。
- 旧355件の索引を今回の49新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ16

- はうろーのRyuneru、naralabのぷろふぁむ、ふーふむのクロエ、ゆるれあの春うさぎ、SN1572の綴よだかの5商品ページを処理。5件の無料ダウンロード選択（直接VRM2件、ZIP3件）から5 catalog IDに含まれる物理VRM 11件を検査した。転送バイト292,246,168、展開後VRM総量266,573,220 bytes。全ページはHTTP 200で、HTTP 429は0件。
- Ryuneru、ぷろふぁむ、春うさぎの3 IDは埋込条件と公開規約を確認し、人型Tポーズ・顔を目視してNAS保存。クロエZIPのLO1126/LO1136 2 VRMは公開Type 1規約が再配布を許可する一方、双方の埋込`Redistribution_Prohibited`が再配布を禁じるため権利矛盾で保留。綴よだかZIP内の6 VRMは、同梱readmeが必須とする作者TOSがDNS_PROBE_FINISHED_NXDOMAINで確認できず権利未確認保留。これら8件はプレビュー/NAS保存なし。
- バッチ16は5商品ページ、5ダウンロード試行、5 catalog IDs、11物理VRM検査、NAS純増3件、非人型0件、権利矛盾1 ID、権利未確認1 ID。詳細チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-16.json`。
- 累計は商品ページ66、カタログID91件、物理VRM102件、検査102件、NAS新規52件、非人型6件、権利矛盾30件、権利未確認1件。NASは407 ZIP・814 WebP、未圧縮VRM 2,473,562,333 bytes、ZIP 1,324,978,264 bytes、WebP 11,552,738 bytes、削減1,148,584,069 bytes（46.4344%）。`verify_nas.py`は`ok:true`、`errors:[]`。
- 797件の現行内訳はNAS保存77、実バイナリ非人型7、作者索引由来非人型1、埋込権利矛盾60、許諾未確認34、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち427、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。別軸の形状選別は人型候補557、非人型244、未判定496。
- 旧355件の索引を今回の52新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ17

- RRROのRomandi、3Dもでる販売屋のSAKURA、unreallyの雪音りう、Niumuのみやまる、ドルミィのDoll me_002の5商品ページを処理。正規0円ZIPを5回取得し、5 catalog IDに対応する物理VRM 5件を検査した。転送68,036,112 bytes、展開後VRM総量81,268,372 bytes。全ページHTTP 200で、HTTP 429は0件。
- みやまるは商品ページ・同梱readmeの個人/法人商用不可、改変可、再配布不可、クレジット不要が埋込メタデータと整合。人型Tポーズと顔を目視しNASへ保存した。RomandiとSAKURAは商品条件が商用利用を許可する一方、VRM埋込`OnlyAuthor`/`commercialUssageName=Disallow`のため保留。雪音りうはモデル条件と公式キャラクター規約が商用ファン作品・配信収益化を許可する一方、埋込`commercialUssageName=Disallow`のため保留。Doll me_002は商品ページが利用者へメタバースでのアバター利用を案内する一方、埋込`allowedUserName=OnlyAuthor`のため保留。4件はプレビュー生成・NAS保存をしていない。
- バッチ17は5商品ページ、5ダウンロード試行、5 catalog IDs、5物理VRM検査、NAS純増1件、非人型0件、権利矛盾4件、権利未確認0件。詳細チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-17.json`。
- 累計は商品ページ71、カタログID96件、物理VRM107件、検査107件、NAS新規53件、非人型6件、権利矛盾34件、権利未確認1件。NASは408 ZIP・816 WebP、未圧縮VRM 2,495,905,033 bytes、ZIP 1,332,185,691 bytes、WebP 11,581,876 bytes、削減1,163,719,342 bytes（46.6251%）。`verify_nas.py`は`ok:true`、`errors:[]`。
- 797件の現行内訳はNAS保存78、実バイナリ非人型7、作者索引由来非人型1、埋込権利矛盾64、許諾未確認34、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち422、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。別軸の形状選別は人型候補557、非人型244、未判定496。
- 旧355件の索引を今回の53新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。