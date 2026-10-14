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

## 2026-10-10 BOOTH認証済み追加バッチ18

- ドルミィのDoll me_006/007/008/009/010の5商品ページを処理。正規0円ZIPを5回取得し、5 catalog IDに対応する物理VRM 5件を検査した。転送68,091,949 bytes、展開後VRM総量76,223,612 bytes。全ページHTTP 200、HTTP 429は0件。
- 5件すべての埋込値は`allowedUserName=OnlyAuthor`、`commercialUssageName=Disallow`、`licenseName=Redistribution_Prohibited`。商品規約は無料取得者の個人的利用・改変、およびVRM対応ゲーム/アプリやメタバースでのアバター利用を案内し、再配布/販売を禁止するが、埋込`OnlyAuthor`は作者のみのアバター利用に限定するため矛盾。5件ともプレビュー生成・NAS保存なし。
- バッチ18は5商品ページ、5ダウンロード試行、5 catalog IDs、5物理VRM検査、NAS純増0件、非人型0件、権利矛盾5件、権利未確認0件。詳細チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-18.json`。
- 累計は商品ページ76、カタログID101件、物理VRM112件、検査112件、NAS新規53件、非人型6件、権利矛盾39件、権利未確認1件。NASは408 ZIP・816 WebP、未圧縮VRM 2,495,905,033 bytes、ZIP 1,332,185,691 bytes、WebP 11,581,876 bytes、削減1,163,719,342 bytes（46.6251%）。`verify_nas.py`は`ok:true`、`errors:[]`。
- 797件の現行内訳はNAS保存78、実バイナリ非人型7、作者索引由来非人型1、埋込権利矛盾69、許諾未確認34、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち417、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。別軸の形状選別は人型候補557、非人型244、未判定496。
- 旧355件の索引を今回の53新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ19

- 七百屋/Nao-YaのVRM詰め合わせvol.1、shirotenのマシェリ2版、vTuberホームセンターのOpenpose avatar、とりにく屋のOpenpose Full 0.x/1.0、hakase3dclusterのあいすくんの5商品ページを処理。正規無料ファイルを7回取得し、10 catalog IDに対応する物理VRM 10件を検査した。転送89,695,642 bytes、展開後VRM総量116,981,596 bytes。全ページHTTP 200、HTTP 429は0件。
- 10件すべて商品/作者の公開条件とVRM埋込メタデータに矛盾。Nao-Ya無料アイテム規約は個人/法人の商用利用・改変・条件付き配布を認めクレジット任意だが、4 VRMは埋込`OnlyAuthor`/商用不可/再配布禁止。shiroten無料VRMは個人VRSNS利用・配信を認める一方、埋込`OnlyAuthor`。vTuber用Openposeはポーズ生成/ControlNet利用可だが埋込`OnlyAuthor`。Torinikuは改変・商用・再配布可（クレジット必須）に対し、0.x/1.0の埋込条件は改変/商用/再配布を禁止。あいすくんはClusterアバター利用を案内する一方、埋込は`OnlyAuthor`。10件ともプレビュー生成・NAS保存なし。
- バッチ19は5商品ページ、7ダウンロード試行、10 catalog IDs、10物理VRM検査、NAS純増0件、非人型0件、権利矛盾10件、権利未確認0件。詳細チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-19.json`。
- 累計は商品ページ81、カタログID111件、物理VRM122件、検査122件、NAS新規53件、非人型6件、権利矛盾49件、権利未確認1件。NASは408 ZIP・816 WebP、未圧縮VRM 2,495,905,033 bytes、ZIP 1,332,185,691 bytes、WebP 11,581,876 bytes、削減1,163,719,342 bytes（46.6251%）。`verify_nas.py`は`ok:true`、`errors:[]`。
- 797件の現行内訳はNAS保存78、実バイナリ非人型7、作者索引由来非人型1、埋込権利矛盾79、許諾未確認34、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち407、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。別軸の形状選別は人型候補557、非人型244、未判定496。
- 旧355件の索引を今回の53新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ20

- hakase3dclusterのあいすくん冬ver、aaaavrmのVOLO、ittokazetauの竹燕、atelierYOZORAの魔法少女すもも、いきどまりのDoll Sheapの5商品ページを処理し、無料配布物を5回取得。5 catalog IDに対応する物理VRM 5件を検査した。転送45,143,374 bytes、展開後VRM総量39,442,516 bytes。全ページHTTP 200、HTTP 429は0件。
- VOLOの埋込権利はEveryone/商用可/再配布禁止で、商品ページの無料配布条件と矛盾せず、人型Tポーズ・顔を確認して保存。魔法少女すももは商品条件の改変/商用利用可・再配布禁止・クレジット任意が埋込Everyone/商用可/再配布禁止と一致し、同様に保存。あいすくん冬verは無料Cluster利用条件と埋込`OnlyAuthor`、竹燕は個人商用・テクスチャ改変の公開許可と埋込`personalNonProfit`/`onlyAuthor`、Doll Sheepは個人/商用・改変可の公開条件と埋込`OnlyAuthor`/商用不可が矛盾するため3件保留。保留品はプレビューなし。
- バッチ20は5商品ページ、5ダウンロード試行、5 catalog IDs、5物理VRM検査、NAS純増2件、非人型0件、権利矛盾3件、権利未確認0件。詳細チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-20.json`。
- 累計は商品ページ86、カタログID116件、物理VRM127件、検査127件、NAS新規55件、非人型6件、権利矛盾52件、権利未確認1件。NASは410 ZIP・820 WebP、未圧縮VRM 2,499,127,729 bytes、ZIP 1,333,948,358 bytes、WebP 11,649,248 bytes、削減1,165,179,371 bytes（46.6234%）。`verify_nas.py`は`ok:true`、`errors:[]`。
- 797件の現行内訳はNAS保存80、実バイナリ非人型7、作者索引由来非人型1、埋込権利矛盾82、許諾未確認34、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち402、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797、未分類0。別軸の形状選別は人型候補557、非人型244、未判定496。
- 旧355件の索引を今回の55新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ21

- Poeale杏、ひるね小屋Lulu、hokekiyoいろは Ver.2、Monotone Diva、declab Miraの5商品ページでダウンロード操作を計7回行い、保持できた配布ファイルは2直接VRM・3 ZIPの計5件（ファイルサイズ合計236,370,442 bytes）。残る2試行は個別結果が耐久ログに残っておらず、完了ファイル・転送量とも確認できない。ZIPの安全検査・抽出を行い、物理VRM6件（5 catalog IDs）をすべて検査した。Iroha ZIPには別途、既存IDへ対応付けできない「geme用 軽めモデル.vrm」もあり、別IDを推測せず保存しなかった。商品ページは全5件HTTP 200、HTTP 429は0件。
- Poeale杏は商品規約のアバター改変・商用利用許可と再配布禁止が埋込`Everyone`/商用可/`Redistribution_Prohibited`と一致。Luluは埋込`CC_BY`に基づく帰属表示が必要で、商品説明中のMMD専用条件は別のMMDファイルに限定されVRM条件と矛盾しない。両方とも二足人型外形、全身Tポーズ、顔を目視確認してNAS保存。Luluの顔プレビューは耳まで切れない画角へ補正した。
- Iroha Ver.2は商品条件がクレジット不要、埋込参照ライセンスがcredit=necessaryで矛盾。DivaとMiraは公開VN3規約が個人/法人の利用条件付き商用利用・アバター利用等を許可する一方、埋込メタデータが`OnlyAuthor`/商用不可のため矛盾。3 IDともプレビュー生成・NAS保存なし。Irohaの未割当て軽量版VRMもカタログ未登録のためNAS保存しない。
- バッチ21の詳細チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-21.json`。
- 累計は商品ページ91、catalog ID121件、物理VRM133件、検査133件、NAS新規57件、非人型6件、権利矛盾55件、権利未確認1件。NASは412 ZIP・824 WebP、未圧縮VRM 2,553,667,601 bytes、ZIP 1,353,709,555 bytes、WebP 11,692,538 bytes、削減1,199,958,046 bytes（46.9896%）。`verify_nas.py`は`ok:true`、`errors:[]`。
- R1/R2/R3以外の797件の内訳はNAS保存82、実バイナリ非人型7、作者索引由来非人型1、埋込権利矛盾85、許諾未確認34、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち397、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797。別軸の予備形状選別は人型候補557、非人型244、未判定496。
- 旧355件の索引を今回の57新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ22

- shop-perchのメティス・ユズ・ユウナギ・リーヤーとRomanticSpicaのダークあいす（VRM 0.x/1.0）の5商品ページで6件の無料VRMを取得。全6件を検査し、保持ファイルの合計は100,092,584 bytes。全商品ページHTTP 200、HTTP 429は0件。
- メティス、ユズ、ユウナギは商品条件がアバター利用・個人/法人商用利用・改変を許可する一方、埋込`OnlyAuthor`/商用不可で矛盾。ダークあいす0.xは個人収益化配信を許可する商品条件と、埋込`commercialUssageName=Disallow`が矛盾。4件はプレビュー/NAS保存なし。リーヤーは商品条件が個人/法人の商用利用を許可するのに対し、埋込VRM 1.0 `commercialUsage=corporation`が個人商用の範囲を明示しないため、権利未確認で保留。
- ダークあいす1.0は埋込`commercialUsage=personalProfit`/`avatarPermission=everyone`/再配布不可と、個人配信・アバター利用可/法人商用・再配布不可の公開条件が整合。正面Tポーズ・頭頂まで収まる顔プレビューを目視しNAS保存した。
- バッチ22は5商品ページ、6ダウンロード試行、6 catalog IDs、6物理VRM検査、NAS純増1件、非人型0件、権利矛盾4件、権利未確認1件。詳細チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-22.json`。
- 累計は商品ページ96、カタログID127件、物理VRM139件、検査139件、NAS新規58件、非人型6件、権利矛盾59件、権利未確認2件。NASは413 ZIP・826 WebP、未圧縮VRM 2,569,135,305 bytes、ZIP 1,362,484,192 bytes、WebP 11,716,254 bytes、削減1,206,651,113 bytes（46.9672%）。`verify_nas.py`は`ok:true`、`errors:[]`。
- R1/R2/R3以外の797件の内訳はNAS保存83、実バイナリ非人型7、作者索引由来非人型1、埋込権利矛盾89、許諾未確認35、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち391、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797。旧355件の索引を今回の58新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ23

- Kado Flow flat、Ver.3、Memorial、Ver.2とHiyoriya Sakuyaの5商品ページを、ログイン済みローカルBOOTHブラウザーから直列確認。各ページHTTP 200、429なし。正規0円ファイル8件（合計206,492,654 bytes）を取得し、ZIP安全検査後に物理VRM 15件を解析。全VRMは0.x。
- Flow Ver.3の4版、Memorialの2版、Ver.2の2版とSakuya Ver.3.1通常版の計9 IDは、人型全身Tポーズ・顔を個別プレビューで確認しNASへ単体ZIP保存。Kadoの埋込商用可/再配布禁止と公開条件が整合し、Ver.3同梱VN3規約では商用Vtuber利用にクレジット必須。Flow補足規約の商用AI利用・AIVtuber・VRMを第三者が取得できるオンラインAIサービス禁止にも従う。Sakuyaの埋込商用可/再配布禁止もREADME・公開規約と整合。Sakuya Ver.3.1の追加PerfectSyncビルドは別カタログIDがないため保存していない。
- `kado-flow-flat`は埋込`commercialUssageName=Disallow`とリンクされた公開Flow補足規約の条件付き商用許可が矛盾するため権利保留。`hiyoriya-sakuya-v2`のZIPは4 VRM（v2-1/PS、v2-2/PS）を含むのに既存IDは1件で、明確な割当がないためモデル対応未確定として保存しない。
- バッチ23は5商品ページ、8ダウンロード試行、11 ID取得、15物理VRM検査、NAS純増9件、権利矛盾1件、モデル対応未確定1件、HTTP 429 0件。チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-23.json`、物理VRM/ZIPの詳細は`...-23-artifacts.json`。
- 累計は商品ページ101、catalog ID138件、物理VRM154件、検査154件、NAS新規67件、非人型6件、権利矛盾60件、権利未確認2件、モデル対応未確定1件。NASは422 ZIP・844 WebP、未圧縮VRM 2,749,505,625 bytes、ZIP 1,457,751,525 bytes、WebP 12,320,910 bytes、削減率46.9813%。`verify_nas.py`は`ok:true`、`errors:[]`。
- R1/R2/R3以外の797件の内訳はNAS保存92、実バイナリ非人型7、作者索引由来非人型1、埋込権利矛盾90、許諾未確認35、モデル対応未確定1、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち380、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797。旧355件の索引を今回の67新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ24

- Hiyoriya Miu/Kotoha/Shino/Asumiとteoteome青年8種の5商品ページをログイン済みローカルBOOTHブラウザーで直列確認。全ページHTTP 200、429なし。無料個別ZIP14件（253,400,360 bytes）を取得し、ZIP安全検査後にVRM 0.xを20件検査。
- HiyoriyaのMiu/Kotoha ZIPは通常版と`_ps`版が各1体ずつあり、4 IDに明確に対応。ShinoのVer.2/2.1とAsumiの旧版/Ver.2.1は各ZIPの通常版だけを既存版IDへ対応し、追加の`_ps` 4件は別IDがないため保存しなかった。作者READMEの個人/法人商用・配信・改変許可、再配布禁止と、全VRMの埋込commercial Allow/Redistribution_Prohibitedが整合。
- teoteomeの8個別ZIPは各1 VRMを含み、BOOTH個別配布名とカタログIDが一致。全VRMの埋込metadataは`commercialUssageName=Allow`/`licenseName=Redistribution_Prohibited`。ショップ共通規約は再配布を広く許可するが、VRM個別の埋込再配布禁止を優先し、NAS内の私的保存に限定した。重複する全部まとめZIPは取得していない。
- 16 IDすべて人型全身Tポーズと顔のプレビューを個別目視しNASへ単体ZIP保存。Asumi旧版は白基調で低コントラストだが、全身各部と顔が見えることを原寸でも確認。バッチ24は5商品ページ、14ダウンロード試行、16 ID取得、20物理VRM検査、NAS純増16件、権利保留0件、429 0件。詳細は`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-24.json`および`...-24-artifacts.json`。
- 累計は商品ページ106、catalog ID154件、物理VRM174件、検査174件、NAS新規83件、非人型6件、権利矛盾60件、権利未確認2件、モデル対応未確定1件。NASは438 ZIP・876 WebP、未圧縮VRM 3,074,446,873 bytes、ZIP 1,652,129,543 bytes、WebP 13,068,310 bytes、削減率46.2625%。`verify_nas.py`は`ok:true`、`errors:[]`。
- R1/R2/R3以外の797件の内訳はNAS保存108、実バイナリ非人型7、作者索引由来非人型1、埋込権利矛盾90、許諾未確認35、モデル対応未確定1、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち364、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797。旧355件の索引を今回の83新規保存IDから除外したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。

## 2026-10-10 BOOTH認証済み追加バッチ25

- BOOTHログイン済みローカルセッションで6商品ページを間隔をあけて確認（全てHTTP 200、429なし）。うち5商品から無料の個別ファイル11件を正規UI操作で取得、合計183,869,466 bytes。重複まとめZIPは取得しなかった。6ページ目の知人代理配布モデル9件は明示的な権利者許諾を確認できずダウンロードせず保留。
- 4つのYoung-seven個別ZIPから7物理VRMを検査。素体（CC0）と眼鏡あり/なしはID・内部名が一致し、3件を保存。ジト目の銀/薄茶2種とセーラー2種は人型・Tポーズ・顔を目視確認したが、既存A/B IDと個別ファイルの対応順が公開情報で確定できず4件をモデル対応保留。
- 太陽の妖精2件、天使2件、ピンク魔法少女2件を個別ZIP/VRMから各1体検査。全て人型でTポーズ・顔を個別確認後に保存。天使2件は白衣装が標準背景で低コントラストだったため、一時プレビュー環境のみ背景を`#808a94`へ変更し、全身・顔が判別できることを確認。ピンク版ZIPの`.vroid`編集データは保存せずVRMだけを保管。
- Noah青年ZIPは2 VRMを含み、商品ページは配布許可を記載していたが、埋込`allowedUserName=OnlyAuthor`/`Redistribution_Prohibited`とauthor情報が一致しないため、プレビュー/NAS保存せず権利矛盾保留。代理配布9件は許諾未確認。個別VRMの埋込再配布禁止はショップ共通規約より制限的なため、保存したTeoteomeモデルの外部再配布はしない。
- バッチ25は6商品ページ、11ダウンロード試行、15 catalog ID取得、15物理VRM検査、NAS純増9件、マッピング保留4件、権利矛盾2件、権利未確認9件、非人型0件、429 0件。今回の追加分は未圧縮162,679,124 bytes→ZIP 99,935,807 bytes（削減率38.5688%）、WebP 366,238 bytes。
- 累計は商品ページ112、catalog ID169、物理VRM189、NAS新規92、非人型6、権利矛盾62、権利未確認11、モデル対応未確定5。NASは447 ZIP・894 WebP、未圧縮VRM 3,237,125,997 bytes、ZIP 1,752,065,350 bytes、WebP 13,434,548 bytes、削減率45.8759%。`verify_nas.py`は`ok:true`、`errors:[]`。旧355件を今回の92新規保存IDから除外した行SHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。
- R1/R2/R3以外の797件の内訳はNAS保存117、実バイナリ非人型7、作者索引由来非人型1、埋込権利矛盾92、許諾未確認44、モデル対応未確定5、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち340、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797。詳細は`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-25.json`および`...-25-artifacts.json`。

## 2026-10-10 BOOTH認証済み追加バッチ26

- 5商品ページをログイン済みローカルBOOTHセッションから直列確認。全てHTTP 200、429なし。無料個別ZIP5件（100,171,032 bytes）をUI操作で取得。R15露出版・全年齢向けではないZIP・重複する1種類版・独立catalog IDのない派生ZIPは取得しなかった。
- 5 ZIPから8物理VRMを検査。賢そうな少年/女装した少年2件、依頼主許可済みの夏向けおねえさん、全年齢のスカート付きクリスマス版、全年齢の金髪版、ゴシック色違い2件の計7 IDは人型Tポーズ・顔を個別目視後保存。賢そう少年ZIP内の追加`賢そうメガネなし.vrm`は独立IDがなく保存せず。
- ゴシック2件の埋込metadataはVRoid HubライセンスURLを参照し、第三者/アバター・商用利用・性的/暴力的表現可、表記不要、改変・再配布不可。今回のプレビューは非性的な全身表示のみ。VRMは未改変でNASローカル保管し、外部配布は行わない。Christmasページでは全年齢と説明されたスカート版のみ取得し、下着露出/R15版は対象外。Gold Maidもページで全年齢とされたZIPだけを取得。
- 初回の`teoteome-christmas-skirt` NAS保存呼出しは120秒でタイムアウト。プロセス終了後、ID索引行・最終ZIP/WebPが存在せず、0-byte `.pending-*`だけであることを確認し、NAS監査が正常な状態でその孤立一時ファイルのみを除去。ローカルscratchで同じarchive呼出しが成功し、NFSへの1MiB write/fsync/read/unlink probeも成功。faulthandler付き再試行で当該IDを保存でき、残り6件も成功した。初回stallの原因は未確定（過渡的NFS I/O停滞の可能性）だが、再監査は`ok:true`、`errors:[]`。
- バッチ26は5商品ページ・5ダウンロード試行・7 catalog ID候補・8物理VRM検査、NAS純増7件、未割当追加VRM1件、権利保留0件、非人型0件、429 0件。今回の追加は未圧縮126,821,644 bytes→ZIP 89,086,304 bytes（削減率29.7547%）、WebP 453,786 bytes。
- 累計は商品ページ117、catalog ID176、物理VRM197、NAS新規99、非人型6、権利矛盾62、権利未確認11、モデル対応未確定5。NASは454 ZIP・908 WebP、未圧縮VRM 3,363,947,641 bytes、ZIP 1,841,151,654 bytes、WebP 13,888,334 bytes、削減率45.2681%。`verify_nas.py`は`ok:true`、`errors:[]`。旧355件のSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。
- R1/R2/R3以外の797件の内訳はNAS保存124、実バイナリ非人型7、作者索引由来非人型1、埋込権利矛盾92、許諾未確認44、モデル対応未確定5、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち333、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797。詳細は`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-26.json`および`...-26-artifacts.json`。

## 2026-10-10 BOOTH認証済み追加バッチ27

- `booth-real-profile-local-2`のBOOTHログイン状態を画面のアカウントメニューで確認。5商品ページを直列確認（全てHTTP 200、429なし）。表示された無料ダウンロード操作を4回実施し、個別VRM4件・計63,850,064 bytesを取得。購入・有料版・VRoid編集データは取得していない。
- 4物理VRMを検査。Naito/Mitsuamiの無料VRMは各ページで無料VRM版を特定し、埋込CC_BY_SAと商品条件（商用/改変可、未改変モデル配布・販売不可）に従い外部再配布なし。Yozora Nekoは個人利用・改変可、Redistribution_Prohibited/商用不可と一致。3件とも人型Tポーズ・顔を個別確認してNASへ保存。Yozoraはcrop topで腹部が見えるが下着/裸体はなく、Tポーズは中立。Naito/Mitsuamiは服装が全身を覆い、露出・性的ポーズなし。
- 金欠な女の子は商品説明が配信/アバター使用を認めていたが、埋込`allowedUserName=OnlyAuthor`と同一メタデータ内のOther permission URL `allowed_to_use_user=everyone`が一致しない。公式[VRM 0.0 schema](https://github.com/vrm-c/vrm-specification/blob/master/specification/0.0/schema/vrm.meta.schema.json)ではこの2項目は別条件であり、矛盾が解消できないためプレビュー/NAS保存せず、記録後に一時VRMを削除。美和子さんは「著作権を放棄していないが基本著作権フリー」との説明に対し具体的なZIP利用条件が不明なため、ダウンロードせずrights-unverified保留。
- バッチ27は5ページ・4ダウンロード・4物理VRM、NAS純増3件、権利矛盾1件、権利未確認1件、非人型0件、モデル対応未確定0件、429 0件。今回の追加は未圧縮45,642,744 bytes→ZIP 26,951,223 bytes（削減率40.9518%）、WebP 124,026 bytes。冗長な再アーカイブ呼出し1件は既存IDを検出してwriterが拒否し、状態変更なし。監査は`ok:true`、`errors:[]`。
- 累計は商品ページ122、catalog ID180、物理VRM201、NAS新規102、非人型6、権利矛盾63、権利未確認12、モデル対応未確定5。NASは457 ZIP・914 WebP、未圧縮VRM 3,409,590,385 bytes、ZIP 1,868,102,877 bytes、WebP 14,012,360 bytes、削減率45.2103%。旧355件SHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。
- R1/R2/R3以外の797件の内訳はNAS保存127、実バイナリ非人型7、作者索引由来非人型1、埋込権利矛盾93、許諾未確認45、モデル対応未確定5、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち328、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797。詳細は`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-27.json`および`...-27-artifacts.json`。

## 2026-10-10 BOOTH認証済み追加バッチ28

- `booth-real-profile-local-2`のログイン状態をアカウントメニューで確認し、5商品ページを直列閲覧（全てHTTP 200、429なし）。商品ページ上の無料操作だけを5回行い、合計152,243,258 bytesを取得。有料版、購入、認証回避は行っていない。
- 4物理VRMを検査。かぼちゃん（Everyone/CC_BY_SA、商用・改変可、原型再配布禁止）は人型・Tポーズ・顔を確認し、外部再配布なしのローカルNAS保管。泉淳也は掲載VRM `172972167827481004.vrm` のみを対象にし、同梱VRMA/JPGは除外。埋込Other permission URLの一般/商用/改変/再配布許可と商品ページのVRoid規約遵守が整合し、人型・プレビュー合格で保存。Nは無料ZIP内にVRMが1件だけでID対応が明確、埋込再配布禁止と商品規約が整合。R18/R18G利用許可はあるが、保存したプレビューは非性的なTポーズのみ。いずれも原本は外部再配布しない。
- みうこー「爆睡ガール（シルバー）」は埋込`allowedUserName=OnlyAuthor`と同一VRMのOther permission URL `allowed_to_use_user=everyone`が不整合のため、権利保留。プレビュー/NAS保存なしで一時VRMを削除。彩瞳Ayame v2無料ZIPはVN3利用規約PDFを全頁確認。ZIP内VRM12種（A/B/Cの通常版・シンプル版・軽量版）に対しカタログはパッケージID1件だけのため対応を推測せず保留し、ZIP/規約抽出物を削除。v1は商品ページに通常版/Cluster版の2 VRMと記載されるが個別対応がなく、ダウンロードせず保留。高校生を明示するタイトルの候補`l0ve4u-nemu`も本バッチではページを開かず、年齢/内容確認待ちとした。
- バッチ28は5ページ、5ダウンロード操作、4物理VRM検査、NAS純増3件、権利矛盾1件、モデル対応未確定2件、権利未確認0件、非人型0件、HTTP 429 0件。保存した3件は未圧縮48,331,116 bytes→ZIP 28,276,721 bytes（削減率41.4938%）、WebP 129,978 bytes。作業機のVRM/ZIP/規約/プレビュー、プレビュー実行環境、npm cacheは削除し不存在を確認。
- 累計は商品ページ127、無料ファイル取得ID185、物理VRM205、NAS新規105、非人型6、権利矛盾64、権利未確認12、モデル対応未確定7。バッチ28では認証待ち6 IDを再分類したが、Ayame v1はページ確認のみでダウンロードしておらず、実取得ID累計には含めない。NASは460 ZIP・920 WebP、未圧縮VRM 3,457,921,501 bytes、ZIP 1,896,379,598 bytes、WebP 14,142,338 bytes、削減率45.1584%。`verify_nas.py`は`ok:true`、`errors:[]`。バッチ27終了時457件のindex hashはバッチ28新規3行を除くと`a5e72e78f01c99755dfa6e7d46dbd7253274abda5573f52e5e73e0dc30166c8a`で一致。旧355件SHA-256も`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`で不変。
- R1/R2/R3以外の797件の内訳はNAS保存130、実バイナリ非人型7、作者索引由来非人型1、埋込権利矛盾94、許諾未確認45、モデル対応未確定7、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち322、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797。詳細は`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-28.json`および`...-28-artifacts.json`。

## 2026-10-10 BOOTH認証済み追加バッチ29

- `booth-real-profile-local-2`のアカウントメニューでログインを確認。BOOTHの商品ページ9件を直列確認し、全てHTTP 200、HTTP 429なし。表示された¥0のUI操作を5回行い、合計45,441,872 bytesを取得。有料版・支援版・認証回避・購入は行っていない。初回zeroniクリックはボタンが画面外で作動せず、スクロール後に可視ボタンを1回クリックし正常取得。
- 9物理VRMを検査。`vroidshop-323`は商品ページ条件と埋込`allowedUserName=ExplicitlyLicensedPerson`が無料取得者に適用されることを確認し、公序良俗・政治/宗教/ヘイト禁止条件に従う。全身Tポーズ・顔を目視し、衣服は全身を覆う。`models/vroidshop-323.zip`とWebP2枚をNASへ保存。`amkr-zeroni`はリンゴ型マスコットで非人型、顔プレビューも空のため保存しない。
- ほしうさ2種（くろ/ピンク）はReadmeがUV Licenseの成人向け暴力利用許可を明記する一方、くろVRMは`violentUssageName=Disallow`、ピンクは`allowedUserName=OnlyAuthor`とCC_BYが同居するため権利保留。リウォレ4種はファイル名でIDを明確に対応できたが、Readmeが許可用途を限定し「その他は作者へ問合せ」とする一方、埋込メタデータは性的/暴力的利用を許可。さらに「少年」と明記された兎キャラクターが目視でも子どもらしいため、権利・内容確認保留。刃切切乃は商品ページがCluster利用向け無料配布を示す一方、埋込`allowedUserName=OnlyAuthor`で矛盾し保留。
- UMEKOは無料VRMのみの版に対し、作者の共通規約が「全額を購入した人」に使用を限定し、¥0版が対象か判断できないため未取得。紬たかは商品ページの必須外部TOSがDNS_PROBE_FINISHED_NXDOMAINで読めず未取得。Luaは全文規約未確認、QuanstellaはTerms of Uses未確認のため未取得のまま次回へ回した。これらと権利保留分の一時ファイルはNASへ保存しない。
- バッチ29は9ページ、5無料UIダウンロード、9物理VRM検査、NAS純増1件、非人型1件、権利矛盾7件、許諾未確認2件、新規モデル対応保留0件、HTTP 429 0件。NAS純増分は未圧縮18,571,044 bytes→ZIP 11,392,684 bytes、Tポーズ/顔WebPを各1枚。作業機のVRM/ZIP/プレビュー、プレビュー実行環境、npm cacheは監査後に削除。
- 累計は商品ページ136、無料ファイル取得ID194、物理VRM214、NAS新規106、非人型7、権利矛盾71、権利未確認14、モデル対応未確定7。NASは461 ZIP・922 WebP、未圧縮VRM 3,476,492,545 bytes、ZIP 1,907,772,282 bytes、WebP 14,198,188 bytes、削減率45.1236%。`verify_nas.py`は`ok:true`、`errors:[]`。index SHA-256は`6c4eeb92da7996da3561d80812ea95e902d03e78958322936af0818161389ad4`、旧355件の保護SHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`で不変。
- R1/R2/R3以外の797件の内訳はNAS保存131、実バイナリ非人型8、作者索引由来非人型1、埋込権利矛盾101、許諾未確認47、モデル対応未確定7、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち311、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797。詳細は`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-29.json`および`...-29-artifacts.json`。

## 2026-10-11 BOOTH認証済み追加バッチ30

- `booth-real-profile-local-2`のログイン状態を画面で確認。BOOTH商品ページ15件を直列確認（全てHTTP 200、HTTP 429なし）。無料UI操作9回で10 catalog ID分のファイルを取得し、物理VRM memberを11件確認した。8件はVRMバイナリ/メタデータ検査、形状・プレビュー確認まで実施。有料取得、購入、認証回避、別ホスト/プロキシ迂回は行っていない。
- `renga-wisp-mira`は商品ページ/READMEと埋込条件を照合し、VRM 1.0、人型、Tポーズ/顔を確認。商用利用等を禁止するページ側のより厳しい条件に従い、非性的用途のローカルNAS保管として保存。フルリール1.3/1.4は各版の直接VRM、商品ページ条件、埋込権利情報、人型/Tポーズ/顔を個別確認し、2件を保存。B30のNAS純増は3 ZIP・WebP6枚。
- Sayo、Hatsuka PC/Quest、Pharaohの4件は商品条件と埋込権利値の矛盾で未保存。ゆるねこは若年に見える外観と性的利用許可の年齢/内容懸念、白ねこみみとKuranmo弓使いは非公開保管・プレビューの許諾範囲が不明で保留。Moyashiは2 VRM/編集用sourceを含みID対応不明のためVRMを抽出せずZIP削除。Muscle Pigeonの取得ZIPも編集用source混在の範囲外と確認後に削除。マーモット/カマキリは商品ページでsource同梱を確認し、未取得。ChocoOrange/Wingsは配布物範囲や利用条件が不明、AxisはAvatarSample_V固有条件未確認のため、3件とも未取得の許諾/範囲保留。作業ZIP/VRM/プレビューは最終監査後に削除し、scratchと一時node_modulesが不存在であることを確認した。
- バッチ30は15ページ、無料UI操作9回、取得ID10、物理VRM member 11、実VRM検査8、NAS純増3、権利矛盾4、許諾/年齢内容保留3、ページ/規約/配布範囲保留3、モデル対応不明1、無料配布ファイル範囲外3、HTTP 429 0。BOOTH累計は151ページ、取得catalog ID204、物理VRM検査222、NAS新規109、権利矛盾75、許諾未確認20、モデル対応未確定8。
- NASは464 ZIP・928 WebP、未圧縮VRM 3,535,666,721 bytes、ZIP 1,943,831,503 bytes、WebP 14,378,760 bytes、削減率45.0222%。`verify_nas.py`は`ok:true`、`errors:[]`。当初355件の保護対象行SHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaseline一致。
- R1/R2/R3以外の797件はNAS保存134、実バイナリ非人型8、作者索引由来非人型1、埋込権利矛盾105、許諾未確認53、モデル対応未確定8、VRM-only取得範囲外3、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち294、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2（合計797）。
- 作業チェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-30.json`。GitHub Actions/RDCは不使用。権利/ID保留と保存済みIDを次バッチで再取得しない。

## 2026-10-11 BOOTH認証済み追加バッチ31

- ローカルログイン済みセッション`booth-real-profile-local-2`を確認し、9商品ページを直列確認（全てHTTP 200、HTTP 429なし）。ページ上の無料操作11回で11 catalog ID/物理VRMを取得・検査した。有料版・購入・認証回避・別ホスト/プロキシ迂回は行っていない。
- `bizava-toma-b/c/d`は各0円直接VRMと作者ライセンスPDFを照合。埋込権利（再配布・性的・暴力的利用禁止）と条件が整合し、成人男性ビジネスアバターの人型Tポーズ/顔を確認後、3件をNAS保存。
- `bizava-keito-a/c/d`はページ/作者条件が利用を許可する一方、VRM埋込`allowedUserName=OnlyAuthor`と矛盾するため3件を権利保留。Keito Aはメタデータ照合前に生成した未確認プレビューを含め削除、C/Dは描画前にVRMを削除し、いずれもNAS保存なし。`youkihi-businessman`は商品ページ上に作者固有の利用許諾がなく未取得。`clearlink-ciel-14/15`はAlice題材・若年寄りの外観で年齢記載がないため、ページ確認のみで保留。
- CLEAR Linkの「スミレ」は5つの直接VRM（1.1戦闘服/インナー/ドレス、1.2戦闘服/浴衣）を個別に取得。ページ記載の170cm「お姉さん」設定に沿う成人寄り外観で、全身Tポーズ・顔・ID対応を個別確認。商品条件と埋込`ExplicitlyLicensedPerson`、再配布禁止、商用/性的/暴力的利用禁止が整合したため、非商用の私的NAS保管として5件を保存。有料支援ZIPは取得せず、インナーの腹部露出とドレスの肩/胸元は非性的で明示的表現なし。
- バッチ31は9ページ、無料UI操作11回、取得ID/物理VRM11、実VRM検査11、NAS純増8、権利矛盾3、ページのみの権利/年齢保留3、非人型0、モデル対応不明0、HTTP 429 0。取得VRM・一時プレビュー・npm環境・ページ確認用スクリーンショットを削除。scratch 2,604ファイル（401,665,723 bytes）の削除と不存在を確認した。
- 累計は商品ページ160、無料ファイル取得ID215、物理VRM検査233、NAS新規117、権利矛盾78、権利未確認23、モデル対応未確定8、認証待ち280。797件の内訳はNAS保存142、実バイナリ非人型8、作者索引由来非人型1、埋込権利矛盾108、許諾未確認56、モデル対応未確定8、VRM-only取得範囲外3、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち280、VRoid Hub認証待ち16、公式ページ認証未確認1、商品ページ404 3、VRoid Studioエクスポート専用23、公式メタデータのみ3、公式リポジトリのみ2（合計797）。
- NASは472 ZIP・944 WebP、未圧縮VRM 3,675,464,357 bytes、ZIP 2,026,793,964 bytes、WebP 14,732,368 bytes、削減率44.8561%。`verify_nas.py`は`ok:true`、`errors:[]`、index SHA-256は`6a188ab3df7c1511f914d8c3b7a89049cb99b1f72fba95dbf2cc2daa55833a09`。既存355件の保護対象行SHA-256はbaseline `4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`と一致。
- B31 checkpointは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261011-31.json`。GitHub Actions/RDCは不使用。権利/年齢保留と保存済みIDは再取得しない。

## 2026-10-11 BOOTH認証済み追加バッチ32

- 最新main `bd34e5d142904ade383d22118710f478bb4b029b` を確認して開始。BOOTH商品ページ23件を直列確認（全てHTTP 200、429なし）。正規の無料UI操作6回で12 catalog ID/物理VRMを取得し、12件すべてVRM 0.xの実体・埋込メタデータまで検査した。転送量168,524,556 bytes。
- `chicken-stickman`と`projectkyoukoku-kosei`の直接VRM、及び「ぴえんシリーズ」ZIP内7 VRMを検査。6体（ぴえん/ぎゃふん/ぐすん/しょぼん/トゥクン/どきん）はページ/埋込条件が整合し、頭・胴・両腕・両脚を持つ人型形状、全身Tポーズ、正面顔を確認してNASへ保存。棒人間と煌星を含め、バッチ32のNAS純増は8件。
- ぴえん系7 IDは実VRMの全身プレビューにより、旧`non_humanoid`予備分類から`humanoid_candidates`へ訂正。ぴえ子は形状上は人型だが、女性化した胸部・まつ毛表現、年齢未記載、埋込性的利用Allowのため保留し、抽出VRMとプレビューを削除した。
- BREAK VENOM、OXYGEN ERROR、kanon MK3Dくまはページ上の利用/商用許可と埋込`allowedUserName=OnlyAuthor`/商用Disallowが矛盾し、3件を権利保留とした。プレビューを作らず、取得した一時ZIP/VRMを削除。Ratenosuは商品ページでUnitypackage/Blender/PSD/PMX同梱を確認したため範囲外として未取得。許諾/年齢保留34 ID（33件はページ確認のみ、ぴえ子1件は実VRM確認後に削除）。HTTP 429、モデル対応保留、追加の確定非人型は0件。
- バッチ32は23ページ、無料UI操作6回、取得ID/物理VRM12、検査12、NAS純増8、権利矛盾3、許諾/年齢保留34、範囲外1。保存分は未圧縮127,846,564 bytes→ZIP 89,013,014 bytes。作業scratch 2,627ファイル（398,767,657 bytes）と商品確認スクリーンショットは削除し、存在しないことを確認。
- NASは480 ZIP・960 WebP、未圧縮VRM 3,803,310,921 bytes、ZIP 2,115,806,978 bytes、WebP 14,979,780 bytes、削減率44.3693%。`verify_nas.py`は`ok:true`、`errors:[]`、formats `zip`。index SHA-256は`0164d6e60fefed0c8314a7fe39bbe29c17dd6dfc6f35e8ef39141e3a000d6608`。baseline時刻以前に保存済みの355行を現在indexから再構成したSHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致。
- BOOTH累計は183商品ページ、取得ID227、物理VRM検査245、NAS新規125、権利矛盾81、権利未確認57、対応未確定8、認証待ち234、HTTP 429 0。797件の排他的内訳はNAS保存150、実バイナリ非人型8、作者索引非人型1、埋込権利矛盾111、許諾未確認90、モデル対応未確定8、VRM-only範囲外4、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち234、VRoid Hub認証待ち16、公式ページ認証未確認1、404 3、VRoid Studioエクスポート専用23、公式メタデータのみ3、公式リポジトリのみ2（合計797）。形状選別は人型572、非人型238、未判定487。
- ローカルcheckpointは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261011-32.json`。GitHub Actions/RDCは不使用。

## 2026-10-11 BOOTH認証済み追加バッチ33

- 開始時mainは`507e6d76d4f62dbf11f3721fce21bef40ef4cb4f`。B33専用workerは実行中でなく、NAS索引、archive記録、正本JSONの89状態遷移を突合した。遷移IDとJSON変更IDは89件で一致し、status不一致は0件。
- ログイン済みBOOTHセッションで67商品ページを確認し、正規無料UI操作16回、取得catalog ID16件、物理VRM16件を検査した。取得転送量は213,408,944 bytes、HTTP 429は0。
- 89件の遷移内訳：埋込権利と商品ページ条件の矛盾12、rights-unverified 69（私的保管/プレビュー許諾範囲不明12、年齢/内容懸念55、権利・規約不明2）、配布範囲外4（商品ページだけで範囲外を確認3、混合編集素材ZIPを検査1）、ID対応不明1、権利と形状確認を通過したNAS保存3。別途の`official_free_download_auth_required_not_verified` 1件はこの89件に含めず、未検証のまま維持。
- 権利矛盾12件のうち2件は、埋込`allowedUserName=Everyone`と商品ページの個人アバター限定・公開アップロード禁止が整合せず、取得物を描画前に削除。残る矛盾品も埋込`OnlyAuthor`/商用利用禁止等とページ・配布許可が両立しないため保管していない。保留・範囲外品のVRM/ZIP/プレビューはNASへ保存していない。
- 新規NAS保存は`junebunnyyy-blue-panda`、`brochimanac-julius`、`pike-steam-punk-cat`。各ZIPの単一`model.vrm`を展開してSHA-256を照合し、Tポーズ/顔WebPのindex hashも実体と一致。3件すべてreadback成功。
- B33後のNASは483 ZIP・966 WebP、未圧縮VRM 3,899,265,521 bytes、ZIP 2,148,721,691 bytes、削減1,750,543,830 bytes（44.8942%）、WebP15,091,308 bytes。`verify_nas.py`は`ok:true`、`errors:[]`、index SHA-256は`e6f596f51eb8c1a94c148141c7f261f4b702430de45ebdca318b86ddbe8e4c36`。B33新規3行を除いた開始時480行はSHA-256`0164d6e60fefed0c8314a7fe39bbe29c17dd6dfc6f35e8ef39141e3a000d6608`と一致。新規128 IDを除いた保護対象355行はbaseline SHA-256`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`と一致。
- 作業機のB33 scratch 15ファイル（133,932,317 bytes）はNAS readback後に削除し不存在を確認。`tools/vrm-preview/node_modules/`はnpm生成マーカー付き・Git未追跡と確認して削除。Cookie、パスワード、認証トークン、認証付き一時URLは記録していない。
- 累計（pilot＋B01–B33）は商品ページ250、無料取得ID243、物理VRM検査261、NAS新規128、権利矛盾93、許諾未確認126、対応未確定9、HTTP 429 0。R1/R2/R3以外の797件の排他的内訳はNAS保存153、実バイナリ非人型8、作者索引非人型1、埋込権利矛盾123、許諾未確認159、モデル対応未確定9、配布範囲外8、別host拒否2、`dweb.link`ブロック/未試行141、BOOTH認証待ち145、別途BOOTH未検証1、VRoid Hub認証待ち16、ページ404 3、VRoid Studioエクスポート専用23、公式メタデータのみ3、公式リポジトリのみ2（合計797）。形状選別は人型575・非人型238・未判定484。
- `scripts/validate.py`は1,297件一意・scope 575/238/484で成功。既存unittest 5件成功、`git diff --check`成功。GitHub Actions/RDCは使用していない。

## 2026-10-11 BOOTH認証済み追加バッチ34（継続M時点の履歴スナップショット）

以下のB34数値はcommit `a12dd76f33b01489732f0586a7dece831b478dc4`（継続M）時点の履歴である。現在の累積状態は本ファイル末尾の「継続N/O/P後」を参照。

- B33を`c2af5462adc9f875ba62913f1baccee64722bfd2`へpushして作業ツリーcleanを確認した後、B34を別checkpointで開始した。ログイン済み`booth-real-profile-local-2`で商品ページ86件を確認（navigation loads 92回）、すべてHTTP 200、HTTP 429は0。無料UI取得は4回、取得catalog ID9件・物理VRM9件を検査し、配布ファイル転送は36,591,848 bytes。B34開始時のBOOTH認証待ち145件から26件が残る。
- `aonecodo-skelton`は`Skelton-VRM-V100.zip`から`SkeltonV100.vrm`（6,302,620 bytes、VRM 0.x、SHA-256=`4d56b56e798f72be177a24f9a0c7ae2e5d68717da929a5d85351da2baabc3367`）を抽出・検査。READMEと埋込Everyone/commercial Allow/Redistribution_Prohibitedを確認し、元モデルを再配布しないNAS内バックアップとして保存した。Tポーズ/顔プレビューで頭・胴・両腕・両脚の揃った二足人型骸骨を目視確認。NASの`models/aonecodo-skelton.zip`とWebP2枚をreadbackし、VRM/画像hash一致。
- `wannpaku-hasshakusama`は主ZIPを一度だけ取得し、ページはVRChat/Cluster利用可とする一方、埋込`allowedUserName=OnlyAuthor`・commercial/sexual/violent Disallowを確認したため権利矛盾で未保存。描画せず一時ZIP/VRMを削除。`pike-steam-rabbit`は単一VRMのほか`.vroid`/`.vroidcustomitem`、texture、sample等を含む27-member編集用パッケージと確認し、取得範囲外として未保存。ZIP/VRMを削除。
- ページのみの権利/年齢保留は41 ID。既存31 ID（初回18 IDに、NEMU、Teoteome flat-chest、ぷち尚也/ぷち柚希、性別不明VRM、および継続KのSiNE DOLL 473 SD、Tolopoly、Rainy Sunny、sakura uniform、Monster Animal、Hayato/Hifumi双子、Roid-chan、Samurai Boyを追加）に、継続MのMiu、Azuha/Mini Azuha、あいすくりーす3色、にくねこ2種、りこちゃん、こぎつねちゃんの10 IDを追加した。年齢未記載、少年設定、学校制服、ちび/ロリ系表現等から年齢を推測せず保留した。VRM-only配布範囲外は18 B34 ID。既存17 IDに加え、Rem-kunはページが無料ZIP内にVRM、UnityPackage、blend、PNG texture、FBXを明記したため混合形式として除外。モデル対応不明はMonotone Blossom、Yumeiro Rainy、Snowflake、Dojimaのたこやきちゃん/あかしやきくんの5 ID。商品ページレンダーで非人型と確認した47 IDは、既存31 ID（Valentine's mimic 4色、Kimoneze、Nagiの大腸菌/ファージ、アナゴ、墓石、kazura bird 2種、たぬきおにぎり2種、たけぴよ、くらんもクラゲ2種、はんぺん、樫豆腐、tabimaru original bird、とりのともしび3色、ぷちくらげ6色、ノッポスライム4色）と、継続Jで確認したkanon MK3Dの動物/果物キャラクター9 ID、プリンスライム1 ID、ヘンテココトリ2 variant、継続Kで確認した韓国海苔1 ID、継続Mで確認したぴよたそ、墓石、低ポリパンダの3 ID。すべて取得前に除外した。Pomesukeは全身形状が見えず判定を保留した。
- 継続Eでは`ジャンクアバターコーナー1.zip`（497,430 bytes、SHA-256=`2d8b8b16f9b0d3379a286c1023fea1a1010c6a5e6b0c93886a354e79492e569e`）を正規無料UIから一度取得。ZIP整合性検査成功、6件のVRM 0.xを実ファイル名・catalog IDに対応させ、各バイナリ/埋込メタデータを検査した。6件すべてが`allowedUserName=OnlyAuthor`、commercial/sexual/violent Disallow、`Redistribution_Prohibited`で、商品ページの一般使用許可と矛盾したため描画もNAS保存も行わなかった。ZIPは最終scratch走査で不在を確認。HTTP応答ステータスはブラウザ取得結果から別途取得していない。
- B34の119状態遷移は、NAS保存1、埋込権利矛盾7、権利/年齢/規約保留41、範囲外18（商品ページ17、実パッケージ1）、商品ページ形状非人型47、モデルID対応不明5。継続Eの4ページ、Gの10ページ、Hの5ページ、Iの6ページ、Jの13ページ、Kの10ページ、Mの10ページはすべてHTTP 200、HTTP 429は0。Eでは無料UI取得1回・取得ID/物理VRM6件、追加アーカイブ0。Gでは10ページ（11 navigation loads）を確認し12 IDを年齢/権利保留4、混合ソース範囲外7、商品ページ非人型1に分類。Hでは5ページ（5 navigation loads）を確認し8 IDすべてを公式商品レンダーに基づく非人型として取得前に除外。Iでは6ページ（6 navigation loads）を確認し17 IDを年齢/権利保留1、非人型16に分類。Jでは13ページ（14 navigation loads）を確認し12 IDを非人型、Dojimaの2 IDを個別形状対応不明に分類した。Kでは10ページ（10 navigation loads）を確認し8 IDを年齢/権利保留、韓国海苔1 IDを非人型、Rem-kun1 IDをVRM/UnityPackage/blend/PNG/FBX混合形式の範囲外とした。Mでは10ページ（10 navigation loads）を確認し13 IDを権利/年齢保留10、非人型3に分類し、ダウンロード/保存を行っていない。Mでは5 IDを公式レンダーの人型二足形状の根拠により、非人型候補から人型候補へ、4 IDを未判定から人型候補へ移した。Iのitem3898075ページは元のtabimaru bird IDだけに対応付け、source_urlが異なるとり灯3色は実配布ページitem4226437と確認してから分類した。Roid-chan、Monster Animal、Miu、Mini Azuha、Riko、Kogitsune、リス/肉ねこ各variantは公式レンダーで人型候補と確認したが、年齢/権利保留のため未取得。開始時145 BOOTH認証待ちから26件が残る。別途未検証1件は未完了のまま維持する。B34は全145件の処理完了ではなく、同じcheckpointで続行する部分実績。
- NASは484 ZIP・968 WebP、未圧縮VRM 3,905,568,141 bytes、ZIP 2,153,972,896 bytes、WebP 15,132,012 bytes、削減率44.8487%。`verify_nas.py`は`ok:true`、`errors:[]`。B34開始時の483行を新規IDから除いて再構成したindex hashは開始値`e6f596f51eb8c1a94c148141c7f261f4b702430de45ebdca318b86ddbe8e4c36`と一致。旧355件の保護対象hashもbaseline`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`と一致。
- R1/R2/R3以外の797件の排他的内訳はNAS保存154、実バイナリ非人型8、作者索引非人型1、商品ページ形状非人型47、埋込権利矛盾130、許諾未確認200、モデル対応未確定14、VRM-only範囲外26、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち26、別途BOOTH未検証1、VRoid Hub認証待ち16、商品ページ404 3、VRoid Studioエクスポート専用23、公式メタデータのみ3、公式リポジトリのみ2（合計797）。形状予備分類は人型588・非人型237・未判定472。
- `scripts/validate.py`: 1,297件一意、scope 588/237/472で成功。既存unit test 5件成功、`git diff --check`成功。NAS全件監査は484 ZIP/968 WebP、`errors:[]`。旧355行の再構成hashは`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`と一致。continuation Bの一時VN3 PDF（999,088 bytes）とブラウザー画面キャプチャ（130,947 bytes）は記録後に削除。continuation EのZIP（497,430 bytes）と画面キャプチャは、作業完了時の対象パス走査で不在を確認した（削除操作自体は記録されていない）。continuation Gのブラウザー画面キャプチャ（86,864 bytes）は記録後に削除し、不在を確認。continuation H/J/K/Mでは一時ファイルを生成していない。一時`node_modules`も不存在。package-lockは作成していない。GitHub Actions/RDCは不使用。
- ローカルB34 checkpoint: `/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261011-34.json`。statusは`batch34_checkpointed_partial`。B34開始145件中26件が残るため、次回はこのcheckpointを再開し、保存ID/過去の権利保留を再取得しない。

## 2026-10-11 B34最新チェックポイント（継続N/O/P後）

- B34継続Nでは10ページ・11 navigation loads・12 IDを確認。Akabeko/Nanakaは配布ZIPにVRM以外の形式も明記されていたため範囲外2 ID、狐AkyO/Cubeは公式全身レンダーから非人型2 ID、Virtual Munchkin Yoshida 8 variantは二足人型形状を確認したが商品ページに年齢設定がないため権利/年齢保留8 ID。取得・保存なし。
- 継続Oでは9ページ・9 loads・13 IDを確認。9件すべて無料ZIPの内容一覧に`.vroid`、blend、FBX、texture/PSD等のVRM以外の制作ファイルが明記されていたためVRM-only範囲外とし、取得・保存なし。
- 継続Pでは既存source_urlのPomesukeページを1回再確認。全身ギャラリーは丸い犬型マスコットがスケートボードに乗る形状で、二足人型の胴・両腕・両脚が確認できず、取得前に非人型へ遷移。ダウンロードなし。作業中、カタログにない未確認item IDを誤って1回開き404となったが、候補外のため商品ページ件数から除外し、再試行・代替URL確認なし。
- 累積は105 unique product pages、候補ページnavigation 113回、無料UI操作4回、物理VRM9件検査、転送36,591,848 bytes、NAS新規保存1件（`aonecodo-skelton`）、145状態遷移。内訳は保存1、埋込権利矛盾7、権利/年齢保留49、配布範囲外33（商品ページ32、実パッケージ1）、商品ページ非人型50、モデル対応不明5。BOOTH認証待ち145 IDは全件状態遷移し、残り0。HTTP 429は0。
- R1/R2/R3以外の797件の最新排他的内訳：NAS保存154、実バイナリ非人型8、作者索引非人型1、商品ページ非人型50、埋込権利矛盾130、許諾未確認208、モデル対応未確定14、配布範囲外41（商品ページ38、実パッケージ3）、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち0、別途未検証1、VRoid Hub認証待ち16、商品ページ404 3、VRoid Studioエクスポート専用23、公式メタデータのみ3、公式リポジトリのみ2。合計797。形状候補は人型596、非人型230、未判定471。
- 別途未検証1 IDは`enrai-tsubame-official-vrm`。source_urlはnote.comの会員登録ゲートでありBOOTH認証待ちとは別分類。会員登録/取得を推測で行わず、状態を未検証のまま維持。
- N/O/P後の追加NAS保存は0。総数484 ZIP・968 WebP、旧355件SHA-256とB34開始483件SHA-256は一致。2026-10-11 15:08 JST時点で`validate.py`（1,297 unique、scope 596/230/471）、既存unit tests（5件）、NAS全件監査（`ok:true`、`errors:[]`）、797件排他的集計、145遷移ID/status照合、`git diff --check`はすべて成功。N/O/Pの一時ブラウザー画面1ファイル（63,024 bytes）は分類記録後に削除し、不在を確認。commit/pushのreadback結果はこのcheckpointのdelivery欄に記録する。
- checkpoint: `/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261011-34.json`、status `batch34_checkpointed_partial`。次の継続ではBOOTH認証待ちが0件であることと、別途未検証1件が未完了であることを先に確認し、保存済みID・既存holdを再取得しない。

## 2026-10-11 B35：混合ZIP41 ID再評価・物理VRM対応不明14 ID照合

- B35開始時のmainは`ab6c91473b5c5c171d87bf43264d1512b6bece52`。対象41 ID/35商品を正本のsource URL・同日までの保持ページ証拠・既存の実体検査記録と照合し、41件すべてに個別の権利/年齢/形状/ID対応/outcomeを記録した。混合ZIPだけを理由とする範囲外は0 IDになった。
- 正規の無料UIから新規取得した配布物は2 ZIP、合計67,186,856 bytes。商品`2744821`の`ずんだもん_通常_2025モデルセット.zip`は25,914,816 bytes、SHA-256 `066ad32b0b35686dc59cf6ad7f07896b172f6e7ad185f85d6e52cd1f66f45b98`。商品`8806174`の`MiddleAgedMarmot_v1.0.0.zip`は41,272,040 bytes、SHA-256 `39ae1ec838acd3535bbc7781c518239b8d75b270a900e57d30342d1a082ece50`。ZIP integrity/path検査は正常。保存対象は下表のVRM単体だけで、配布元の元ZIP・編集素材はNAS/Gitに保存していない。

| ID | ZIP内の選択VRM | VRM SHA-256 | NAS ZIP SHA-256 | T-pose WebP SHA-256 | face WebP SHA-256 |
| --- | --- | --- | --- | --- | --- |
| `tohozunko-zundamon-2025-walking` | `歩行(Walking)/VRM/Zundamon(Walking Type)_vrm10.vrm`（2,837,984 bytes, VRM 1.0） | `d0a6125c5c6b89d286fc05a64834e7b47c30910f9d5c0a5e26f6fe70b82267bc` | `4bbb2ed536512c72d8195724fbaad92a78dee3d158bb4adbea15263d3fa506e6` | `58a593e30e9d6a93b89ce2f2009f81a9e215f8a262c6ba71b0d63bb08ca60a4c` | `928f4eee2adadcc5aea085a2dc0723e44ccda1ae670f9a62fca4e301a42cb60f` |
| `tohozunko-zundamon-2025-flying` | `飛行(Flying)/VRM/Zundamon(Flying Type)_vrm10.vrm`（2,556,688 bytes, VRM 1.0） | `627fae1c24d6530511d853492a2b283adae87fdb8fde802a50383e40117363a9` | `388e2a816b5fbf6a9fa643af2576e8c1dc3ddec8a3db2bea8f7a5bc1d236e8cc` | `c38b2352003d84c151a88f4b1459918358a9137822f143c9fe25fec5baea05f2` | `39310234f5e493deb662a5bff17370452ef20bf76d0544c9a8981fd4d0b2c902` |
| `jima-middle-aged-marmot` | `MiddleAgedMarmot/Models/MiddleAgedMarmot.vrm`（14,852,260 bytes, VRM 1.0） | `cf391c0b72cc2cffeeb10919ea088c68a5c222897a23ae64484d345a87943ba5` | `a61204f84ffbf0c18f8d204fd1ea4c70e6853b1a105aa50e36859cdc23430cef` | `86885abf91fed1aaae0e96e54aff81cc13b7bb87ad5b1c0b56e7526839a4bfbc` | `e98a29bd62dc9508a3c094fcb653daa019e05dd5842acaa352cff32e62cd3264` |

- ずんだもんは公式プロフィールに年齢概念なしと明記。配布物の日本語VN3は非営利の個人/法人利用と本人用アバター利用を許可し、性的/暴力的/政治宗教的利用・第三者利用を禁止する。選択VRM1.0 metadataは`commercialUsage=personalNonProfit`、`allowRedistribution=false`、`modification=prohibited`、`creditNotation=required`。VN3サマリー表の未改変再配布/credit欄とは差があるため、より厳しいmetadata側を適用し、非営利・非改変・非再配布、credit保持で私用保管した。VRM0.xのwalking/flying各1メンバーもmetadataまで確認したが、既存カタログIDが明記するVRM1.0だけを選び、0.xは抽出・保存していない。
- マーモットは作者が商品名・説明・同梱規約でmiddle-aged/Humanoidと明記。VRM1.0実体と全身レンダーで頭・胴・両腕・両脚を確認。商用/改変は許可される一方、再配布・第三者取得可能な公開は禁止のため、元VRMのまま私用NASへ保存した。B35追加モデルZIP3件とWebP6枚はowner-only mode0600。親ディレクトリの既存modeは変更していない。

- 41 IDの排他的結果：NAS保存3（上表）、既存商品レンダーで非人型9（`moopee-akabeko-chan`, `mxu-purin-normal`, `mxu-purin-plus`, `neoneko-affordable-dog-corgi`, `neoneko-affordable-dog-default`, `neoneko-affordable-dog-husky`, `neoneko-affordable-dog-shiba`, `neoneko-affordable-dog-tanuki`, `neoneko-aorinu`）、年齢/権利/モデルmember対応/物理全身形状の独立根拠不足でhold29（`branshop-nao`, `jima-muscle-mantis`, `jima-muscle-pigeon`, `jowashop-ordinary-girl`, `kumayui-kumano-yucha`, `lillian-nanaka`, `mxu-suu-vrm`, `neoneko-leo`, `neoneko-ngii`, `neoneko-nolt`, `neoneko-roa`, `neoneko-romuru`, `neoneko-shitakee`, `neoneko-shoki-avatar-2`, `neoneko-tofu-seijin`, `neoneko-tsukiyomi-akane`, `pike-aurora`, `pike-moon-night`, `pike-steam-rabbit`, `propofol7-satake-nagisa`, `ratenosu-untitled`, `sakurabido-hapicchi`, `sakurabido-megumicchi`, `sakurabido-mirucchi`, `shounokoto-kotatsu-mikan`, `tatougai-oninoko-kiri`, `youkihi-long-black-hair`, `youkihi-recruit-suit`, `yumenonakaya-rem-lowpoly`)。29件は取得/保存しておらず、物理形状が全件確認済みとは主張しない。`data/models.json`の各ID notesが個別の年齢/権利/形状/対応根拠とhold条件を記録する。

- 物理VRMとの対応不明14 IDを既存記録のみで照合。結果は全件ambiguous維持、B35新規取得・ページアクセス0。
- 特記：`pike-aurora`と`pike-steam-rabbit`はB34に単一VRM memberとmetadataを物理パッケージから検査済み。B35で再取得せず、その既存member対応を維持した。年齢根拠と物理VRMの全身T-pose検査が不足するためholdであり、ID-to-member対応不明へは分類していない。

| ID | 既存検査記録の種類と照合結果 |
| --- | --- |
| `dojima-akashiyaki-kun` | 商品ページのみ。1無料ZIPに2名が記載され、個別VRM memberの対応なし |
| `dojima-takoyaki-chan` | 上記と同じ商品。ページ記録のみで一対一対応なし |
| `hiyoriya-sakuya-v2` | B23にVRM 0.x 4 members（Sakuya-v2-1/1_ps/2/2_ps）のSHA記録。1 IDが複数variantを含み、個別IDなし |
| `pike-monotone-blossom` | 商品ページにouter A/B。ZIP未検査、IDは1件 |
| `pike-red-dragon` | 商品ページにA/B。ZIP/memberとIDの対応なし |
| `pike-snowflake` | 商品ページにA/B。ZIP/memberとIDの対応なし |
| `pike-yumeiro-rainy` | 商品ページにAjisai/Snail body。ZIP/memberとIDの対応なし |
| `shounokoto-moyashi` | B30 ZIP inventoryに`moyashi-vrm-after.vrm`/`moyashi-vrm-human.vrm`の2候補。どちらも抽出・検査なし |
| `teoteome-young-seven-sailor-a` | B25物理VRM `ないちせーら.vrm` SHA `e8ea5d51418d9ea30acd2efdfe57ea36bdcdabf0b76da1a9055ebae3cdb13e38`。A/B候補のどちらかを示す作者根拠なし |
| `teoteome-young-seven-sailor-b` | B25物理VRM `あるちせーら.vrm` SHA `e4c56b996cf7407998fa3303933318004bf53d1d5a7625ba0060ca4977098e6b`。A/B対応根拠なし |
| `teoteome-young-seven-silver-eye-a` | B25物理VRM `ジト目オッド銀.vrm` SHA `61b60fd9f8b51b77a11ec5f40b142b4007cf1cdebaf276c1cc5043a30b831189`。A/B対応根拠なし |
| `teoteome-young-seven-silver-eye-b` | B25物理VRM `ジト目オッド薄茶.vrm` SHA `97175b1043e2aa59e751c611247fbc7458719fb90531855b9b8314a6dbfe4198`。A/B対応根拠なし |
| `watanosoko-ayame-v1` | 商品ページに通常版/Cluster版2 variants。物理member記録なし |
| `watanosoko-ayame-v2` | B28 inventoryに12 VRM variantsとlicense記録。1 ID内のper-variant mappingなし |

- B35のNAS最終実測：487 ZIP/974 WebP、未圧縮VRM 3,925,815,073 bytes、ZIP 2,168,476,533 bytes、WebP 15,210,140 bytes、圧縮削減率44.7637%。index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。`verify_nas.py`は`ok:true`/`errors:[]`。B35開始時484行それぞれのline SHA-256が全件一致。旧355行を基準時刻で再構成したSHA-256も`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`と一致。全797 IDの排他的集計はNAS157、非人型68、埋込権利矛盾130、権利/年齢/内容未確認237、mapping不明14、混合ZIPのみ範囲外0、別host2、`dweb.link`141、BOOTH auth0、別途未検証1、VRoid Hub16、404 3、VRoid Studio export23、公式metadata/repo5（合計797）。shape予備分類は人型599・非人型230・未判定468。
- `validate.py`は1,297 unique・scope 599/230/468で成功。既存unit tests 5件成功。HTTP 429は0、RDC/GitHub Actionsは不使用、購入/checkoutなし。Gallery操作中に意図しないcreator cart/security interstitial（HTTP 403）へ一度遷移したが、checkout/paymentは行わず、interstitialを回避・再要求していない（詳細は非公開B35 checkpoint `ui_safety_events`）。

## B36：NASアクセス監査とB35 hold再評価（2026-10-11）

- 開始時の`main`/`origin/main`/HEADは`6d6f192ffa6ac8459c170159359c162f86ad3b63`で一致し、worktreeはclean。B36後の読み取り専用`verify_nas.py`は`ok:true`、`errors:[]`、487 ZIP/974 WebP、ZIP 2,168,476,533 bytes、形式ZIPのみ。index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`もB35後の値と一致。今回NASへの書込み・削除・権限/ACL/共有変更は一切なし。
- 読み取り専用NAS監査：`/mnt/hdd/vrm`、`models/`、`previews/`のmodeは0777、`index.jsonl`は0600、owner UID/GID 1000/1000。models/previewsの全1,461ファイルは0600。getfaclは基底ACLのみで名前付き/default ACLなし（2ディレクトリ+1,461ファイル）。autofs配下のNFSv3 `rw,sec=sys`。`showmount -e`は3 exportsで、対象`/volume1/hdd`はprivate IPv4 /24に限定、wildcardなし。実IPは記録しない。`root_squash`等とNAS側ユーザー/共有権限はクライアントから確認できず、AUTH_SYSのUID/GIDを使う方式もユーザー単位の強い認証境界ではない。よって現状は「ネットワーク範囲は限定」だが「第三者アクセス不能な私有保存」は未確認。mode 0600のみを根拠に新規アーカイブしない。
- 既存の`jima-middle-aged-marmot`を含む487件は依頼に従い保持し、取り出し/削除/権限変更なし。マーモットのBOOTH条件は元モデルの再配布・第三者が取得できる公開を禁止しているが、現NAS共有で第三者アクセスが排除できるかは未確認。NAS管理者による実効隔離の確認が残件。
- 権利監査：130件の現statusはsource条件とVRM embedded metadataの不一致を示し、保存禁止の確定ではない。notesのキーワード監査（重複あり）では`OnlyAuthor` 61、`Redistribution_Prohibited` 81、commercial Disallow 49、`allowRedistribution=false` 7件。商用/再配布/アバター利用の軸は私的技術検査・ローカル保存と別評価する。個別の矛盾が未解決なため130件のstatusは変更せず、237件も一括解除しない。
- 日本著作権法第30条/第30条の4は私的使用・非享受目的の利用に関する例外を定めるが、特定のVRM取得、NAS保存、可視化が適用要件を満たすとは断定しない。米国法が適用される場合もfair useは17 U.S.C. §107の個別要素判断である。VRM metadataとVRM Public Licenseは`Model Use`/`Avatar Use`/`Redistribution`等の範囲が別なので、用途フラグだけから「保存禁止」と結論しない。参照：[著作権法](https://laws.e-gov.go.jp/law/345AC0000000048?occasion_date=20260519)、[文化庁の第30条・第30条の4資料](https://www.bunka.go.jp/seisaku/chosakuken/pdf/94097701_02.pdf)、[VRM metadata](https://vrm.dev/en/vrm/meta/license/)、[VRM Public License 1.0](https://vrm.dev/licenses/1.0/)、[17 U.S.C. §107](https://uscode.house.gov/view.xhtml?req=%28title%3A17+section%3A107+edition%3Aprelim%29)。法的助言ではない。
- B35の29 holdを新基準で再評価：27 IDは年齢数値が未記載/非数値、1 IDは作者がage unknown、1 IDは作者がchild avatarと明記。年齢未記載だけでは中立・非性的な構造検査/Tポーズ表示を止めず、年齢を推測しない。29件すべて未保存のまま、他の権利・物理member対応・全身形状・保存先アクセス条件を別に確認する。

### 正規無料UIでローカル検査した2件

両商品ページ/同梱READMEは、無料・商用利用や改変を許可し、元データの再配布は禁止、改変データの再配布は相談、バックアップは利用者責任と記載。実体を一時ローカル検査したことはアバター利用・公開・再配布を行ったことを意味しない。いずれもVRM 0.x metadataは`allowedUserName=Everyone`、`commercialUssageName=Allow`、`licenseName=Other`。年齢は推測せず、性的/暴力的な出力は作成していない。

| ID | 正規無料ZIP / ZIP SHA-256 | 唯一のVRM member / VRM SHA-256 | ローカル表示結果 | NAS判断 |
| --- | --- | --- | --- | --- |
| `pike-aurora` | item [5353568](https://booth.pm/ja/items/5353568)、29,455,101 bytes、`b94a20d3ab0194183d348c43f3ee59221cbc33f2737f783f44e07f642e3e40c4` | `Aurora free.vrm`、19,483,012 bytes、`8b3a1ae85da5ca6eea9fff06d6ac5a591e14fa2eb09ba6e69fb8ff16e0d623e0` | Tポーズで頭・胴・両腕・両脚を確認。顔正面。性的/暴力的描写なし。face画像では角先の一部が上端で切れるが顔は見える。T-pose SHA `d17daac39e508f719d545e1dbf3e2a6c74b7cd31f383567719d0fd33268d87ea`、face SHA `1aebcf291f5238c520915c7496287a3294a89e2369457f20c8ef2ad09c33aab7`。 | 形状・プレビューは確認できたが、NASの第三者隔離が未確認のため保存せず。`rights_unverified_hold`維持。 |
| `pike-steam-rabbit` | item [4468213](https://booth.pm/ja/items/4468213)、26,324,649 bytes、`460c0bb4e8164345e00a1d56e2ac8d3467c5373624468546cb545c3e930a3ee6` | `Steam Rabbit Black outer.vrm`、13,250,904 bytes、`78f4ab6f497b640557c0b9c8597226683fc4b5ac4d0760052219f27b82860e3` | Tポーズ画像で腕がT字に見えず、顔画像はゴーグル等で隠れて確認できない。性的/暴力的描写なし。T-pose SHA `6979f3cbb1465c2f4c901ec1091e678933a389634895a768d4e7c3c233cea4e6`、face SHA `c7d47c9f7f5faff514ba7b3188b6720ee66a78e6bb700d8717a8e6b5ce9eed54`。 | プレビュー条件未達かつNAS隔離未確認のため保存せず。`rights_unverified_hold`維持。 |

2 ZIP/2 VRMはmode 0700のローカルscratchだけで検査し、NASへは書き込まなかった。記録後にZIP/VRM/previewと一時`node_modules`を削除し、不在を確認した。B36後もNAS件数は487/974、B35の保護対象は不変。RDC/GitHub Actions・購入/checkoutは不使用。今後はNAS管理者による実効的な非公開設定確認、または規約上第三者保管が許される保存先の確認が必要。
- B35 checkpoint（履歴）: `/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-mixed-zip-batch-20261011-35.json`。B35は41/41 outcomeと14/14照合記録済み。B35専用scratchの29ファイル（89,943,366 bytes）と生成した`tools/vrm-preview/node_modules`（2,229ファイル、112,569,124 bytes）は、NAS/チェックポイントへの反映後に削除し不存在を確認した。B35ではカタログ正本・scope・文書だけをGitへstageした。

## B37：rights-conflictの用途別再評価サンプル（2026-10-11）

- BOOTH [商品4911831](https://booth.pm/ja/items/4911831)の現在表示を確認。0円の直接VRMとしてType 1〜4と各body版、計8 variantが列挙され、別に任意の100円一括ZIPが案内される。商品説明はモデル/改変物の商用利用を許可し、再販のみを禁止している。今回はページ文面だけを再確認し、再取得・購入・一括ZIPの取得はしていない。
- 対応する8 IDは`yousoron-amane-type-1`, `yousoron-amane-type-1-body`, `yousoron-amane-type-2`, `yousoron-amane-type-2-body`, `yousoron-amane-type-3`, `yousoron-amane-type-3-body`, `yousoron-amane-type-4`, `yousoron-amane-type-4-body`。各既存noteは実VRM metadataの`commercialUssageName=Disallow`と`licenseName=Redistribution_Prohibited`を記録している。
- ここには実際の公開条件と埋込metadataの商用/再配布軸の矛盾があるが、その矛盾だけでは非公開の非商用構造検査や私的保存を禁止するとは言えない。確認した商品ページには私的保存を明示的に禁じる記載は見つからなかったものの、それだけで保存許諾・著作権法上の適用を断定しない。NASの第三者アクセスも未確認のため、8 IDすべて`official_binary_inspected_rights_conflict_not_archived`を維持し、NASへ追加しない。
- この8 IDは「単純な商用/再配布フラグを保存禁止と誤読した可能性がある」優先レビュー群として整理する。B37時点の130件全体を一括解除したり、他商品へ一般化したりはしない。次は同様の記録を持つsource familyを一つずつ照合し、保存・技術検査・アバター利用・商用・第三者配布を別軸で記録する。

## B38：Kizuna AIの利用条件と保存軸の個別再評価（2026-10-11）

- 最新main・NASの開始状態は`c116ab99711f0a7e223754de1421624b05c0237c`、487 ZIP/974 WebP、`verify_nas.py ok:true/errors:[]`。今回も既存NASへの書込み、削除、chmod/chown、ACL/NFS設定変更なし。
- 公式配布ページはVRM 1.x/0.xを案内し、ダウンロード前に利用規約への同意を求める。`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/official-page-20261009/official-page-checkpoint-20261009.jsonl`には両VRM member、サイズ、SHA-256、埋込metadataが記録されているため、カタログの「実ダウンロード未確認」は誤記として修正した。checkpointに同意イベントの記録はない。今回その同意ボタン操作・再取得は行っていない。
- [二次創作ガイドライン](https://kizunaai.com/guideline/)は二次創作活動を私的使用の範囲に限定し、二次創作活動とは関係しないコンテンツの複製等を認めない旨を記載する。3Dモデル規則は元/改変モデルの配布・販売・譲渡を禁じ、改変モデルのSNS/VRChat利用を条件付きで認める一方、自由に取得/コピーできるpublic avatarを禁じる。[キャラクター利用規約](https://kizunaai.com/terms/)は適用法上一般に認められる利用を妨げない旨を記載する。非公開の中立技術検査用複製がこれらの条項・適用法とどう交差するかはページだけでは確定できず、法的結論を出さない。
- `kizuna-ai-kamatte-vrm0`の`licenseName=Redistribution_Prohibited`は公式の3Dモデル再配布禁止と整合する。これだけで保存禁止/権利矛盾とは扱わず、技術検査用複製・保持条件が未確認として`rights_unverified_hold`へ再分類した。`kizuna-ai-kamatte-vrm1`の`allowRedistribution=false`も再配布禁止と整合するが、`avatarPermission=onlyAuthor`は改変モデルのSNS/VRChat利用条件とアバター利用軸で差が残るためrights-conflictを維持する。どちらも非公開技術保存の根拠とはせず、NAS未保存を維持する。
- 797 ID内の排他的集計は埋込権利矛盾129、利用条件等未確認238（他の区分は不変）。B35 hold29、物理対応不明14、NAS 487/974も不変。正本は`data/models.json`、現行集計と保留条件は`docs/completion-criteria.md`/`docs/hermes-bulk-resume.md`を参照。

## B39：Sony mocopi RAYNOS 3件の権利/保存軸再評価（2026-10-11）

- 開始時の`main`/`origin/main`は`c8bfee43dd75d8ddd2b2d1771d8f05f96948709e`で一致。NASは読み取り専用`verify_nas.py`で487 ZIP/974 WebP、`ok:true`/`errors:[]`、index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。今回もNASへの書込み・削除・chmod/chown・ACL/NFS変更なし。
- [公式配布情報](https://www.sony.co.jp/en/Products/mocopi-dev/jp/downloads/DownloadInfo.html)はOriginal/mini/SportsのRAYNOSアバターを掲載し、v1.0.8配布を案内。公式EULAは2025-04-17改定。既存checkpoint `/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/official-page-20261009/official-page-checkpoint-20261009.jsonl`には3 ZIPそれぞれのVRM 0.x member、サイズ、SHA、`licenseName=Redistribution_Prohibited`、`allowedUserName=OnlyAuthor`を記録済み。今回はページ/EULAの読取りだけで、同意操作、再取得、アバター利用、NAS保存は行っていない。
- EULA第2条は許諾用途としてモーションデータとアバターの組合せ、生成コンテンツ編集、二次著作物作成と、それらの出力の無償配布を定める。元許諾データの複製・改変はその用途に必要な範囲に限る。第3条は第三者使用・再許諾等と事前承諾のない営利利用を制限し、第9条は契約終了時に合理的に可能な限り2週間以内に使用停止・削除することを定める。EULAはキャラクター/データの使用をもって同意とみなすが、checkpointに個別の同意イベントは記録されていない。
- `Redistribution_Prohibited`は元VRMの第三者移転制限と整合する方向で、単独では個人的な保管を禁止しない。`allowedUserName=OnlyAuthor`はEULAが利用者に認める限定的avatar利用との軸差としてrights-conflictを維持する。一方、非公開の中立構造検査はEULA第2条の列挙用途に明記されず、そのための複製・保持が許諾範囲内かは未確定。許可とも一律禁止とも推定せず3件すべて未保存とした。
- 3件の`verification`と集計は変更なし（権利矛盾129、利用条件等未確認238）。既存487件、B35 hold29、物理mapping不明14も不変。詳細は`data/models.json`の各ID notesを参照。

## B40：pike-moon-nightの年齢・権利・mapping hold再評価（2026-10-11）

- 開始時の`main`/`origin/main`は`c9295601cc56a2b81f3e6362203f86fef7ab63cf`で一致。NASの読み取り専用検証は487 ZIP/974 WebP、`ok:true`/`errors:[]`、index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。今回もNASへの書込み・削除・権限変更なし。
- B40完了時点の再監査では、`/mnt/hdd/vrm`/`models`/`previews`が0777、`other::rwx`、名前付き/default ACLなし。1,461 assetと`index.jsonl`は0600だが、空の`.index.lock`は0777。NFSv3 `rw,sec=sys,local_lock=none`。`showmount -e`は`RPC: Program not registered`で失敗し、export範囲を再確認できず。B36でprivate IPv4 /24限定を見た記録は履歴情報としてのみ保持し、現在の隔離根拠には使わない。サーバー側ACL、UID/GID mapping、squash、lock有効性は不明。NAS設定・権限変更はせず、新規保存停止を継続。
- BOOTH [item 5167120](https://booth.pm/ja/items/5167120)の現行本文を読んだ。商品は0円で、ページはblue/red・VRM・PSD・textureを列挙する。本文には「download時に利用規約へ同意」とあるため、今回はダウンロード・同意操作なし。
- 規約は商品を使うモデル等の無料/商用利用・成果配布・改変を許可し、元データそのままの再配布を禁止、改変データ再配布は相談、credit表記を求める。また、データbackupは利用者側の責任とする。したがって再配布禁止だけを私的保存禁止と読み替えないが、backup案内は中立的な構造検査の明示許諾と同一視しない。利用規約の性的/暴力的内容は作成・検査用途に用いていない。
- 公開ページに数値年齢や実年齢ゲートは見つからず、年齢未記載だけを中立・非性的構造検査/Tポーズの停止理由にしない。ただし同ページのblue/red各 variant が実ファイルで何memberか、どのmemberが本IDに対応するかは未確認。実VRMの全身形状/Tポーズも未検査。追加ダウンロードは規約への同意を伴うため、明示的承認なしには行わない。
- `pike-moon-night`は`rights_unverified_hold`のまま。hold理由を年齢不明ではなく、取得条件への未同意、member/ID対応、物理形状、およびNASの第三者隔離未確認に整理した。モデルを保存済みへ変更せず、B35 hold29全件の状態・集計（権利矛盾129、利用条件等未確認238）を維持。

## B41：branshop-naoの権利・年齢・混合ZIP hold再評価（2026-10-11）

- 開始時`main`/`origin/main`は`8e40aa58ffcafd60fa0b8d3d549fe57536bf7a92`で一致。NAS verifierは487 ZIP/974 WebP、`ok:true`/`errors:[]`、index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。読み取り専用のmode/ACL/NFS監査はB40記録と同じ、NASへの書込み・権限変更なし。
- [BOOTH item 6595645](https://booth.pm/ja/items/6595645)はUnitypackage/FBX/Texture等とVRM形式モデルを掲載し、混合パッケージだけでは除外しない。ページはUVライセンスの個別条項PCU/DDW/SEU/VEUを明示。リンク先[UVライセンス](https://uv-license.com/ja/license?utf8=%E2%9C%93&pcu=true&ddw=true&seu=true&veu=true)の一般条項はモデルと派生物の配布を個別許可なしでは不可とするが、DDWは二次的著作物の第三者配布を許可する。これは元VRMの再配布許可とは別。個人商用・派生物配布・成人表現の条件を私的保存禁止へ読み替えない。
- 確認した規約本文には私的な構造検査・そのための保管を明記する許諾/禁止が見当たらないため、可否を推定しない。年齢設定や実年齢ゲートは商品ページで確認できず、未記載だけで中立・非性的検査を止めない。SEU/VEUは成人向け表現の許諾であり、キャラクター年齢の証拠ではない。
- `Nao_Contents.zip`内のVRM memberとIDの対応、実VRMの全身形状/Tポーズ、個人的な検査用複製/保管の根拠が未解決のため、`rights_unverified_hold`を維持。追加取得・同意操作・NAS保存なし。権利矛盾129、利用条件等未確認238の集計は変わらず。B35 hold29全体も未解決のまま。

## B42：jowashop-ordinary-girlの子ども表示・権利矛盾・物理検査（2026-10-11）

- 開始時`main`/`origin/main`は`833ebea4dcbc3e8b5dbb72473c30d67a517fbe11`。読み取り専用NAS verifierは487 ZIP/974 WebP、`ok:true`/`errors:[]`、index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。mode/ACL/NFSは前回監査と同じで、NASへの書込みなし。
- [BOOTH item 7392963](https://booth.pm/ja/items/7392963)の無料UIから`一般子供.zip`（16,605,054 bytes）を取得。ZIPは`testzip`成功、unsafe path/symlinkなし、2 member（`一般子供.vrm`と`.vroid`）。`.vroid`は展開/使用せず。ZIP SHA-256 `01ab3ee63216df77786a5ed357e9812cce53635737be6fd26253ffcf14493ab6`。
- 唯一のVRMは15,591,436 bytes、VRM 0.x/GLB2、SHA-256 `9317d9b428b8434748bb72bac99e1cfcc7e8f899ed3d2c651afe4c1d24b9b2c7`。metadata title=`一般子供`、author=`じょわ`、`allowedUserName=OnlyAuthor`、`licenseName=Redistribution_Prohibited`、commercial/sexual/violent=`Disallow`。公式[UniVRM metadata仕様](https://vrm.dev/en/univrm/meta/univrm_meta/)は`OnlyAuthor`を作者のみがアバターを操作できる設定、`Redistribution Prohibited`を配布/改変ライセンス区分として記載。
- 作者ページは約115cm・小学生/幼稚園児タグを掲載し、使用/改変と友人向けの無償調整・引渡しを許可する一方、自作発言・販売を禁止。子どもとして示されたモデルを成人とは扱わない。数値年齢/年齢ゲートは見当たらず、年齢属性のみを中立・非性的検査の停止理由にしない。成人・性的・暴力的用途は行っていない。
- ページの友人向け無償改変・引渡し許可と埋込`OnlyAuthor`/`Redistribution_Prohibited`がアバター利用/第三者移転軸で矛盾する。commercial Disallowは販売禁止と整合する。矛盾は私的保存禁止を意味しない。非公開技術検査・そのための長期保管条件はページ/metadataに明示されていないため許諾・禁止のどちらにも推測せず、この1 IDを`rights_unverified_hold`から`official_binary_inspected_rights_conflict_not_archived`へ変更。
- rendererはVRMを外部へ送らないローカルHTTP経由で実行。`jowashop-ordinary-girl-tpose.webp` 768×1024 SHA-256 `2322c09e8267b08a52103ebaae02b5d969ea8f6439df03031e1c08dcb60f8890`、face 512×512 SHA-256 `5e693f7404fc67a198c9724ec292141d3410e4e9d5328ea99330acc28beda2c7`。目視で頭・胴・両腕・両脚の全身と正面顔を確認。
- `jowashop-ordinary-girl`を`rights_unverified_hold`から`official_binary_inspected_rights_conflict_not_archived`へ移した。NAS保存なし。作業後にscratch内のZIP/VRM/WebPと一時`node_modules`を削除。797 ID内集計は権利矛盾130、利用条件等未確認237。B35 hold29は全件未保存で、全体として未完了。

## B43：JIMA Muscle Mantisの利用条件・物理検査（2026-10-11）

- 開始時`main`/`origin/main`は`547ccc98320c5738c4be0cf2418d4cf27ed958a7`。NASの読み取り専用検証は487 ZIP/974 WebP、`ok:true`/`errors:[]`、ZIP bytes 2,168,476,533、index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`（548,641 bytes）。root/models/previewsは0777、indexは0600、`.index.lock`は0 bytes/0777、名前付き/default ACLなし。実マウントはNFSv3 `rw,sec=sys,local_lock=none`。`showmount -e`は`RPC: Program not registered`で失敗しexport範囲は未確認、サーバー側のACL/UID mapping/squashも未確認。第三者隔離は証明できないため新規NAS保存なし。NASへの書込み・権限変更なし。
- [公式BOOTH item 8768066](https://booth.pm/ja/items/8768066)の¥0 `MuscleMantis_v1.0.zip`を認証済みprofileの正規UIで一時取得し、同梱READMEをVRM利用前に確認。商品ページ表示は26.9 MB。ZIP SHA-256 `35f5068f49b4143a82568db10e42e772b1ecab310e9724769fc5c43da1d04cab`、`testzip`成功、安全でないmember path/symlinkなし。唯一のVRMは`MuscleMantis/Models/MuscleMantis.vrm`（7,476,532 bytes）、ほかのFBX/Blender/texture等は展開・使用せず。
- VRMは1.0/GLB2、sha256 `ca70caf50e4df02b8091ac2a4f438a4eed7e743563a0af05f53a1966f005b639`。metadataは`avatarPermission=everyone`、`commercialUsage=personalProfit`、`modification=allowModification`、`allowRedistribution=false`、`allowExcessivelySexualUsage=false`、`allowExcessivelyViolentUsage=false`、`creditNotation=required`。商品ページは個人商用・改変・配信/SNSを許可し、データの再配布/転売（改変版を含む）と性的/暴力表現を禁止するため、これらの軸はmetadataと整合する。再配布禁止は公開/第三者配布の制限であり、それだけで私的保存禁止としない。
- 商品ページはcredit任意とする一方、同梱README/VRM metadataはcredit必須とする。クレジットを付ければ両条件を満たせるため、権利矛盾には数えず、利用時は必須表記を採用する。これは私的保存禁止を意味しない。[VRM Public License 1.0](https://vrm.dev/licenses/1.0/)はModel/Avatar Useに必要な複製をRedistributionと区別するが、非公開構造検査や長期保管がその用途に含まれるかは明記されないため、保管可とも一律禁止とも推定しない。
- BOOTHページに数値年齢や年齢ゲートは見当たらず、年齢未記載だけで中立・非性的な技術検査/Tポーズを止めない。商品はhumanoid mantis/bodybuilder avatarと記載。ローカルrendererでTポーズ768×1024 sha256 `56e423d4b0806f6c14ac5eac17b8fa6096dbf45e48d068ad12ed4dc1d1835fb8`、face 512×512 sha256 `c5e7093af22e8a86c1fd16cab23d0539f77580655a9e6433568911fd96ea3e30`を生成し、全身の頭/胴/両腕/両脚と正面頭部を目視確認。性的/暴力的表示は行っていない。
- `jima-muscle-mantis`は全身形状を根拠に`download-scope`の人型候補へ追加し、shape countを600/230/467に更新。これは保存許可ではない。私的技術検査/長期保管の条件が未解決のため`rights_unverified_hold`を維持し、NAS保存なし。JIMAは別枠の物理VRM対応不明14 IDには含まれず、14件は維持。ZIP/VRM/previewsと一時`node_modules`は削除し、package.json/lockfileは変更なし。rights分類集計130/237は不変。B35 hold29は全件未アーカイブ。

## B44：JIMA Muscle Pigeonの規約・物理検査（2026-10-11）

- 開始時`main`/`origin/main`は`b1a7b82fef3e4f9b43c107b954956f62d5b11345`。NASは読み取り専用`verify_nas.py`で487 ZIP/974 WebP、`ok:true`/`errors:[]`、ZIP bytes 2,168,476,533、index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previewsは0777、indexは0600、名前付き/default ACLなし。実マウントNFSv3 `rw,sec=sys,local_lock=none`、`showmount -e`はRPCエラーでexport範囲不明。`.index.lock`は0 bytes/mode 000（getfacl user/group/other all `---`）と現在観測。B43記録のmode 0777と食い違うが原因・発生時刻は不明。NAS変更は行わず、サーバー側ACL/UID mapping/squashと第三者隔離は依然未確認。
- [公式BOOTH item 8737858](https://booth.pm/ja/items/8737858)の¥0 `MusclePigeon_v1.0.0.zip`を正規UIから一時取得（20,207,030 bytes、SHA-256 `ce039b9b08f5e2badb72b23eddea2df21da67540982e8b3cf919768402139c0b`）。READMEをVRM使用前に確認。ZIP testzip成功、unsafe path/symlinkなし。FBX/GLB/texture/README/制作scriptの混合配布だが、実VRM memberは`MusclePigeon/Models/VRM/MusclePigeon.vrm` 1件（`__MACOSX/._`はAppleDouble sidecar）でIDと一対一対応。target VRMだけをscratchへ抽出。
- VRM 0.x/GLB2、10,120,408 bytes、SHA-256 `79362c71c6de176b7863a480c0b94edf3d0c0d38b2323a80334b7e6dc3b7545b`。metadataは`allowedUserName=Everyone`、`commercialUssageName=Allow`、`licenseName=Redistribution_Prohibited`、`sexualUssageName=Disallow`、`violentUssageName=Disallow`。商品ページ/READMEと整合し、商用利用・改変を許可、credit任意、再配布・転売・無償配布（改変版含む）と部品配布・性的/過度な暴力表現等を禁止。再配布制限だけを私的保存禁止とは読み替えないが、非公開技術検査/長期保管条件も明示されないため`rights_unverified_hold`を維持。
- 年齢情報/ゲートなし。年齢未記載だけで中立検査を止めず、ローカルrendererでTポーズ全身・正面顔を確認。T-pose 768×1024 SHA-256 `43637962188a7bd2c4c5ed3a62e4dae5055ab29f101beb2a09c7876675b25475`、face 512×512 SHA-256 `3da9ac371071a4220e96fde3ffffe27628385ad9949d23ece115cbcab8009f9e`。初回faceの頭頂切れを`--face-y-offset-frac 0.04`で調整し、最終画像で頭頂を含む正面頭部を確認。性的/暴力的表示なし。
- `jima-muscle-pigeon`を形状分類の`humanoid_candidates`へ追加し、scopeを601/230/466に更新（保存許可ではない）。別枠のmapping不明14 IDにJIMA Pigeonは含まれず、14件の保留は不変。権利集計130/237も不変。NAS保存なし。ZIP/VRM/previews、evidence scratch、一時`node_modules`を削除し、package.json/lockfile変更なし。npm installでは3 high severity advisoriesが表示されたが、依存定義は変更せず。RDC/GitHub Actions/新規テスト不使用。

## B45：kumayui-kumano-yuchaの再評価（2026-10-12）

- 開始時`main`/`origin/main`は`ade82e4eccc608bd1289754a149761f26c21b578`。NASを読み取り専用で再確認し、487 ZIP/974 WebP、`ok:true`/`errors:[]`、ZIP bytes 2,168,476,533、index 548,641 bytes/SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previewsは0777、indexは0600、`.index.lock`は0 bytes/mode 000。再帰getfaclでnamed/default ACLなし。NFSv3 `rw,sec=sys,local_lock=none`、`showmount -e`は`RPC: Program not registered`。サーバー側共有ACL/UID mapping/squash/export範囲と第三者隔離は未確認。chmod/chown/NAS設定変更なし。
- [公式BOOTH item 7039529](https://booth.pm/ja/items/7039529)は¥0の`熊野ゆちゃ.zip`（表示19.5 MB）を掲載。年齢は`？？？`、年齢ゲートなし。ページ規約は個人利用・金銭目的の商用利用・改変を許可し、改変物を含む再配布を禁止、credit任意。正規のログイン済みUIで一度取得した実ZIPは20,409,872 bytes、SHA-256 `e7e3ce06f639a8709de2876b2d407b6ddf6157aeed71bfac449eb3032fc772fe`。ZIP `testzip`成功、5 entries（directory 1含む）、unsafe path/symlinkなし。ページ記載はPNG×2だが、実体はPNG×1、VRM×1、`.vroid`×1、Unitypackage×1。
- 実VRM memberは`熊野ゆちゃ/熊野ゆちゃ.vrm`の1件で商品名・本IDに一対一対応。VRM 0.x/GLB2、12,763,404 bytes、SHA-256 `c14e3ab59823e3eba9b51e26a812c7d61f4b255c8f08216c1d310011c7a1ae76`。metadataは`allowedUserName=Everyone`、`commercialUssageName=Allow`、`licenseName=Redistribution_Prohibited`、`sexualUssageName=Allow`、`violentUssageName=Allow`。確認したページ規約と使用/改変/再配布の主要軸は整合。再配布禁止のみを保存禁止とは読み替えない。
- 年齢「？？？」のみで中立検査を止めず、年齢を推定せず、性的/暴力的表現を行わずにローカルTポーズ/顔を生成・目視確認。全身で頭・胴・両腕・両脚、正面顔で頭頂から顎までを確認。T-pose 768×1024 SHA-256 `9796c086b7fa6153e7e7a8dd2ccefbb0392046696491ef618d6abb76578e6ac2`、face 512×512 SHA-256 `29610c081c1b2235d8df9e78ecca33ec46e8978c2038315342bf19ba7fb1cb39`（`--face-y-offset-frac 0.04`で頭頂を含めた）。Playwright同梱headless shellは未導入だったため、既存`/usr/bin/google-chrome`をrendererに指定して生成成功。
- 形状分類のみ`kumayui-kumano-yucha`を`humanoid_candidates`へ追加し、scopeを602/230/465に更新。権利矛盾130・利用条件等未確認237、B35 hold29、mapping不明14は不変。私的な非公開技術検査/長期保管条件は明示されないため`rights_unverified_hold`を維持し、NAS未保存。ZIP/VRM/previews/evidence scratchと一時`node_modules`は除去し、package.json/lockfile変更なし。npm installでは3 high severity advisoriesが表示されたが、依存定義は変更していない。RDC/GitHub Actions/新規テスト不使用。

## B46：Youkihi Recruit Suitの再評価（2026-10-12）

- 開始時`main`/`origin/main`は`bcda135004ed285550c4f2954f082e1397c4ca58`。NAS読み取り専用確認は487 ZIP/974 WebP、`ok:true`/`errors:[]`、ZIP bytes 2,168,476,533、index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previews 0777、index 0600、`.index.lock` 0 bytes/mode 000、named/default ACLなし。NFSv3 `rw,sec=sys,local_lock=none`、`showmount -e`失敗。NAS変更なし。
- [公式BOOTH item 3823494](https://booth.pm/ja/items/3823494)の¥0 `FreshWomanSet.zip`（表示7.9 MB）を正規ログイン済みUIから一時取得（8,279,720 bytes、SHA-256 `e362bc2ba7787f49780e0b716c47cafd1af13a63a382ff7586a257afbf35a85b`）。ページはVRMとsample imagesを含む無料prototypeと説明し、author-specific restrictions、数値年齢、age gateは見当たらない。ZIP testzip成功、6 entries（directory 1含む）、unsafe path/symlinkなし。VRM memberは`FreshWomanSet/FreshWoman.vrm`1件で本IDへ対応し、sample imagesは一時確認のみ。
- VRM 0.x/GLB2、12,819,856 bytes、SHA-256 `4201b77d17e8e334ddd40b2e1f63c68d3b6ad37c14c537bda1c0e13aa8ab423a`。metadataは`author=Youkihi`、`title=FreshWoman`、`allowedUserName=Everyone`、`commercialUssageName=Allow`、`sexualUssageName=Allow`、`violentUssageName=Allow`、`licenseName=CC_BY`。公式[VRM metadata mapping](https://vrm.dev/en/vrm/meta/license/)は`CC_BY`を[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)へ対応させる。CC BY 4.0は複製/共有/改変を許可し、共有時の帰属表示などを条件とする。したがって本カタログでは、作者がライセンス可能な権利について、個人の非公開技術検査用コピーは肯定的な複製許諾の範囲内と分類する。これは許諾の不在からの推論ではなく、埋込ライセンスに基づく運用判断であり、他の権利やライセンサーが保有しない第三者権利を無効にするものではない。
- 年齢は推定せず、中立Tポーズ/顔をrendererで生成し目視確認。頭・胴・両腕・両脚が明瞭で、人型形状。顔正面、頭頂から顎まで表示。T-pose 768×1024 SHA-256 `bad3677d54a17b2773fdd99ba1f0c6122497dc781fcbef212c5addc2ac58aaf1`、face 512×512 SHA-256 `e4a1b009abf394f176b36a7c4a327a9bfbfa846555949d5ed7473edfd8981dc9`。性的/暴力的用途・表示は行っていない。既にshape candidateだったためscope 602/230/465は不変。
- `rights_unverified_hold`から`official_binary_inspected_humanoid_render_confirmed_nas_privacy_hold`へ分類を分離。権利矛盾130・利用条件等未確認236、NAS隔離hold1。NFSv3 `sec=sys`/mode0777親dirで実効的な第三者隔離は未確認のためNASには保存せず、既存487 ZIP/974 WebPは変更なし。ZIP/VRM/previews/evidence scratchと一時`node_modules`を削除。npm installは3 high severity advisoriesを表示したがpackage.json/lockfileは不変。Playwright同梱headless shellが無かったため`/usr/bin/google-chrome`をrendererに指定して成功。RDC/GitHub Actions/新規テスト不使用。

## B47：Youkihi Long Black Hairの再評価（2026-10-13）

- 開始時の`main`/`origin/main`は`e40ce5f402d194810779388af4a0df7cd61abcc1`。B35由来hold29の`youkihi-long-black-hair`を次の候補として確認。商品ページ1件、無料UI操作1回、物理VRM member 1件、対象ID 1件、NAS保存0件として区別した。
- [公式BOOTH item 3841471](https://booth.pm/ja/items/3841471)の認証済みUIで¥0 `NegativeSet.zip`（表示14.7 MB）を確認し、一度だけ取得。本文はVRM本体とサンプル画像を同梱したZIP、VroidStudioのみで制作した暫定版なので無料と説明。表示範囲に作者固有の利用条件、数値年齢、年齢ゲートは見当たらない。タイトル/本文に「少女」とあるが年齢は推定しない。配布物にREADMEはなく、5点のPNGは検査後に破棄。
- ZIPは15,389,698 bytes、SHA-256 `5d6ed73d1d2554a1c071643150c94faf24d8acceaa69bd08b57b4f440e233c09`。`testzip`成功、7 entries（directory 1、PNG 5、VRM 1）、expanded 21,761,412 bytes。絶対/親相対パス、symlinkなし。唯一のVRM member `NegativeSet/NegativeGirL.vrm`を本IDに一対一対応。
- 実VRMは0.x/GLB2、18,633,964 bytes、SHA-256 `708df3de1f415fc1516dfd8bbdf7e82e1be974e41d6487938a3d035257536ee0`。metadataは`author=Youkihi`、`title=NegativeGirL`、`allowedUserName=Everyone`、`commercialUssageName=Allow`、`sexualUssageName=Allow`、`violentUssageName=Allow`、`licenseName=CC_BY`。公式[VRM license mapping](https://vrm.dev/en/vrm/meta/license/)の`CC_BY`リンクはCC BY 4.0を指し、[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)は複製/共有/改変を認める一方、帰属表示等の条件と第三者権利等の留保がある。したがって作者が許諾できる権利について、非公開技術検査用コピーは肯定的な複製許諾の範囲内と運用分類する。商用・avatar use等の各metadata flagを私的保存条件と混同せず、これを法律相談や全権利の保証とは扱わない。
- 年齢推定や性的/暴力的表示を行わず、既存preview generatorでneutral T-pose/faceを生成・目視確認。T-pose 768×1024 SHA-256 `428b75afc221103ec413e28572f70f6932f7af9d45050f6f7da0bd0072da9f05`は頭・胴・両腕・両脚が見え、着衣状態。face 512×512 SHA-256 `a21e789c52f5595bb29a11ab7bdcad35fdd36747f4d3ed902c4c00872cd4628d`は正面だが長い髪が顔の大部分を覆う。既存humanoid candidateの物理確認でありscope 602/230/465は不変。
- `rights_unverified_hold`から`official_binary_inspected_humanoid_render_confirmed_nas_privacy_hold`へ分類を分離。CC BY 4.0の複製許諾は確認したが、NAS隔離を確認できず保存しない。権利矛盾130、利用条件等未確認235、NAS隔離hold2。B35 hold29は全件未アーカイブ（本IDを含む）。既存487 ZIP/974 WebPは変更なし。scratchと一時`node_modules`は検査記録後に削除し、`package.json`/lockfileは不変。RDC/GitHub Actions/新規テスト不使用。
- B47後の最終NAS read-only audit：`verify_nas.py`は487 ZIP/974 WebP、`ok:true`、`errors:[]`、ZIP bytes 2,168,476,533。index 548,641 bytes/hash `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previews 0777、index 0600、`.index.lock` 0 bytes/mode 000、named/default ACLなし。NFSv3 `sec=sys,local_lock=none`。`showmount -e`はRPC errorで失敗しexport範囲未確認。NASの既存資産/権限は変更していない。

## B48：lillian-nanakaの再評価（2026-10-13）

- B48開始時の`main`/`origin/main`は`7b8d5740f8330331d88ba167f7cad2cf91ff55f4`。B35 hold29の`lillian-nanaka`を[公式BOOTH item 6259209](https://booth.pm/ja/items/6259209)で確認。認証済み画面に¥0「無料ダウンロード」`エプロンナースアバター_ななか.zip`（表示48.6 MB）があり、正規UIから一度だけ一時取得。ページ表示条件は商用利用・X等SNS投稿・改変を許可し、自作発言・再配布・性的/暴力表現を禁止。無料版の説明はVRM、`.vroid`、肌テクスチャを含む。数値年齢・年齢ゲートは表示範囲で見つからず、年齢は推定しない。証拠引用はcitation ledger source ID 32に2件記録。
- ZIPは50,972,225 bytes、SHA-256 `46c42f490453a08bf52e88848e802cc59e5fbc0adac7ee015b679ed9b2c3fac5`。`testzip`は問題なし、7 entries、expanded 64,460,955 bytes。directory 2、PNG 2、VRM 2、`.vroid` 1。unsafe path、symlink、暗号化memberなし。物理VRMは`エプロンナースアバター ななか/ななか.vrm`（21,334,648 bytes、SHA-256 `00be1fb7261483bf2d1c76b90be7d12fc5303dd97dfc98f8c7ffdd853c38465d`）と`エプロンナースアバター ななか/ななか　血のりなし.vrm`（21,272,920 bytes、SHA-256 `12cb8abff40725226937e4f4b5604319a1909d68fa1abd2deef7fd14dad0e346`）。
- 両memberはGLB2/VRM 0.x、metadata `title=ななか`、`author=LINK@`、`allowedUserName=ExplicitlyLicensedPerson`、`commercialUssageName=Allow`、`sexualUssageName=Disallow`、`violentUssageName=Disallow`、`licenseName=Redistribution_Prohibited`。表示された商品条件とmetadata flagsは各行為の範囲で整合する。標準`ななか.vrm`を既存IDへ商品名/metadata titleで対応。比較結果はnodes/meshes/material names/humanoid bone namesが一致、GLB JSON chunk全体は不一致。血のりなしmemberは別の配布binaryとして記録するが、別カタログIDを推測で追加しない。
- 中立プレビューは規約の暴力表現禁止を避け、血のりなしmemberのみで生成。Tポーズは頭・胴・両腕・両脚が見える着衣表示で、スカートから出た脚に紫の装飾があるが、血・裸体・性的/暴力表現は視認されない。T-pose 768×1024 SHA-256 `87d0bfcdab564c35a70114789413b096159c81a2cf954ae8fdf66a16f6e7e3ef`、face 512×512 SHA-256 `0fa5a1ac42edec697cc57e78e31826196b973c2d5f5bd60aa82c21efb3f8b07f`。正面顔は明瞭。年齢推定なし。
- 商用/再配布などの制限だけを私的保存禁止とは扱わない一方、非公開技術検査用の長期複製/保管条件は明記されないため`rights_unverified_hold`を維持。NAS隔離未確認のため保存なし。人型候補602→603、非人型230、未判定465→464。権利矛盾130、利用条件等未確認235、NAS隔離hold2、対応不明14、B35 hold29（全件未アーカイブ）は不変。既存NAS 487 ZIP/974 WebPは変更なし。
- 検査後に一時ZIP、抽出VRM、preview画像/JSON、scratch内renderer依存を削除し、ハッシュ等を照合。scratchにはページ表示条件のテキスト記録のみ残した。NAS権限/ACL/共有設定への書込み変更なし。RDC/GitHub Actions/新規テスト不使用。

## B49：shounokoto-kotatsu-mikanの再評価（2026-10-13）

- B49開始時に`git fetch origin --prune`を実行。`main`と`origin/main`は`6d00b1528b1c33ce1d6551abcb3fc1e6622baa54`で一致、worktree clean。B35 hold29から`shounokoto-kotatsu-mikan`を選び、[公式BOOTH item 6686224](https://booth.pm/ja/items/6686224)を認証済みUIで確認。¥0 `kotatsumikan.zip`（表示6.74 MB）を公式UIから1回一時取得。citation ledger source ID33に商品ページの証拠2件と同梱英語参考訳の複製条項1件を記録し、ID一意性を確認。
- ZIPは7,068,831 bytes、SHA-256 `247d76ebea57ee3372a8653a27fd94dd05d6f374f2b8c3faad84f256d686131c`、13 entries、expanded 13,162,123 bytes。`testzip`は問題なし。unsafe path、symlink、暗号化member、重複名なし。単一の`.vrm` memberは`kotatsumikan/Orange_After_2_VRM.vrm`（2,259,904 bytes）。ZIP内には日本語/英語/韓国語/中国語のVN3 PDFがあり、日本語原本と参考英訳を確認。日本語PDFは1,162,150 bytes/SHA-256 `68845da8e88a076269a4ba4bd5b8f0ec900c4b0715cb5cbe63c7178cca4cf9c7`、英語PDFは1,026,341 bytes/SHA-256 `6c6c000c27ebd6d8bf743c45e57e957b53407d560e365814008179e5aa5da1c5`。規約上日本語版が優先し、英語版は参考訳。
- 規約は個人/法人の営利・非営利利用を認め、許諾範囲内の複製を認める。未改変状態の再配布は禁止、改変データの配布は許可。再配布禁止だけから私的保存禁止とは結論しない。一方、規約に記載のない利用方法には権利者の事前明示許諾を要求し、非公開の中立構造検査や長期ローカル保管を明示的に扱っていないため、その適用は未解決。`rights_unverified_hold`を維持し、authorへの許諾依頼・追加取得・VRM抽出/metadata検査/描画は行わない。再開条件は検査/保管を明示的に含む権利者許諾またはそれを明確にする正式な解釈。
- 規約は購入/ダウンロード/インストール等の開始を同意とみなし、未成年ユーザーは事前の法定代理人同意が必要とする。UIからのダウンロードを行ったが、利用者の年齢/法定代理人同意は確認しておらず、これを法的にクリアしたとは主張しない。ページ上にキャラクターの数値年齢/年齢ゲートは見当たらないが、VRM metadataは未確認。年齢不記載は中立検査を止めた理由ではなく、権利範囲と利用者側条件の未解決がhold理由。
- ZIP/PDFのscratchバイナリは削除し、ページ根拠と最小限のライセンス所見テキストだけを保持。NASへの書込みなし。更新後も総登録1,297、shape候補603/230/464、rights conflict130、利用条件等未確認235、NAS隔離hold2、物理対応不明14、B35 hold29全件未アーカイブ。既存NAS487 ZIP/974 WebPは変更なし。再監査`verify_nas.py`は`ok:true`/`errors:[]`、ZIP bytes 2,168,476,533、index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previews 0777、index 0600、lock mode 000、named/default ACLなし、NFSv3 `rw,sec=sys,local_lock=none`。exportはprivate IPv4 /24に限定表示だが、server-side ACL/mapping/squash/client isolation/effective lockは未確認。権限変更なし。RDC/GitHub Actions/新規テスト不使用。

## B50：mxu-suu-vrmの再評価（2026-10-13）

- B50開始時に`git fetch origin --prune`を実行。`main`/`origin/main`は`162e76529cc03a50fc92f95e8b07cd3dce011c43`で一致しworktree clean。B35 hold29の未確認候補`mxu-suu-vrm`を選び、公式[BOOTH item 3933882](https://booth.pm/ja/items/3933882)を公開ページだけで再確認。ページは通常VRM無料offer `スゥ_リメイクv1.2.zip`（19.8 MB）、VRC版（8.01 MB）、VRM-only Valentine版（13.8 MB）を別々に掲示。通常offerに`.vroid`とセットアップ済みVRMを含むと説明するため、mixed packageだけを除外理由にはしない。citation ledger source ID34に公式ページを登録し、5件の短い逐語証拠を照合。
- 利用条件はダウンロード時点で同意とみなす。ページは商用利用/改変を許可し、改変後を含む再配布/販売を禁止、VRChat内avatar cloneとVRChat等へのpublic uploadを許可し、第三者が取得できるVRoidHubへのアップロードを再配布と説明する。作者への確認を避けるよう示唆する非公式な一文は、私的検査/保存の具体的な許可または禁止を定めない。再配布禁止だけを私的保存禁止とは扱わない一方、非公開の中立技術検査/長期保存は明示されない。規約同意操作を追加取得と同時に行うことを承認済みと推定せず、B50ではクリック/ダウンロードを行わなかった。よって`rights_unverified_hold`を維持。
- ページには「女の子」タグと約90 cmの身長があるが数値年齢/年齢ゲートはない。年齢を推定せず、年齢不記載だけで中立検査を禁止しない。ZIP/VRMは未取得・未抽出・未解析・未描画で、member-to-ID対応、VRM仕様、形状、全身Tポーズは未確認。shape scopeは更新しない。追加取得にはダウンロード同意の明示的な承認と、私的検査/保管の権利範囲の確認が必要。
- 検査後もcatalog total1,297、shape603/230/464、rights conflict130、利用条件等未確認235、NAS隔離hold2、物理対応不明14は不変。NAS read-only verifierは487 ZIP/974 WebP、`ok:true`、`errors:[]`、ZIP bytes2,168,476,533、index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previews 0777、index0600、lock 0 bytes/mode000、named/default ACLなし、NFSv3 `rw,sec=sys,local_lock=none`。`showmount -e`はHDD exportを含む3 exportをprivate /24に限定表示、wildcardなし。server ACL、UID/GID mapping、squash、client/user isolation、実効lockは未確認。NAS書込み・権限変更なし。RDC/GitHub Actions/新規テストなし。

## B51：neoneko-leo再評価（2026-10-13）

- 開始時`git fetch origin --prune`後、branch `main`、`HEAD`と`origin/main`は`c08d314646b8f162254a8eafb7dc60347f96a271`で一致、worktree clean。NASの`verify_nas.py --nas-root /mnt/hdd/vrm`は`ok:true`、`errors:[]`、487 entries/974 previews、ZIP bytes 2,168,476,533。index 548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。
- 読み取り専用調査でroot/models/previews 0777、index 0600、`.index.lock` 0 bytes/mode 000、再帰ACLにnamed/default entriesなし。`findmnt`は`nas1.local:/volume1/hdd`、NFSv3 `rw,sec=sys,local_lock=none`。`showmount -e`は3 exportsをprivate IPv4 /24に限定しwildcardなしと表示。ただしserver ACL、UID/GID mapping、squash、利用者ごとの隔離、実効lockは不明で、非公開隔離を証明できない。NASへの書込み、chmod/chown、ACL/NFS変更なし。
- [公式BOOTH item 6505161](https://booth.pm/ja/items/6505161)は無料`レオ.zip`（23.1 MB）、VRM 0.0、member名`レオ_v1.09.vrm`と`.vroid` source`レオ_素体.vroid`をページ上に掲載。利用表示は使用/改造使用OK、改変物販売/原本譲渡/転売NG。禁止は販売/移転の軸であり、私的保存禁止とは推論しない。非公開技術検査/長期保管の明示もなく、保存許可も推定しない。商品説明の少年表記から年齢を推定せず、年齢不記載だけで中立構造検査/Tポーズを止めない。
- 公式ダウンロードURLは一度だけ、認証なし・redirect追従なしGETで調査し、HTTP/2 302、Location `https://booth.pm/users/sign_in`。ログイン/バイパス/ダウンロードなし。よってverificationを`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ再分類する一方、private storage/retention権利は独立に未解決と記録。ZIP/VRM member、metadata、shape/T-poseは物理未検証。B35旧age-reviewの年齢理由holdと混合ZIP除外を訂正し、同じ販売/移転禁止を保存禁止とは扱わない。
- 797件を全レコードから再集計。変更前は権利矛盾130、利用条件等未確認235、BOOTH認証0、他サービス認証17。変更後は130/234/1/17、partition total797を維持。shape603/230/464、B35 hold29全件未保存。citation source ID35（BOOTH商品ページ、6 quotes）/36（公式download URLの302 probe、1 quote）。B51 checkpointは`work/holiday-batch/booth-mixed-zip-reassessment-20261013-b51.json`。この記録は商品ページ条件とアクセス状況の整理であり、適用法令の個別判断は行っていない。RDC/GitHub Actions/新規テストなし。

## B53：sakurabido-hapicchi再評価（2026-10-14）

- 開始時`git fetch origin --prune`後、branch `main`、`HEAD`/`origin/main`は`855ab98bb9a2a0c4bc3b8d4f103069f8075972bb`で一致、worktree clean。B35 hold29の候補`sakurabido-hapicchi`を選び、[公式BOOTH item 4979735](https://booth.pm/ja/items/4979735)を再確認。商品ページは¥0の「さくらリクオ_フリーアバター_はぴっち.zip」（17.2 MB）と、Vroidファイル・VRMファイル・readmeの同梱を記載。mixed ZIPのみを理由に除外しない。citation source ID39に商品ページと利用条件の逐語根拠2件を、ID40にdownload gate probeの逐語根拠1件を登録し、source ID一意性・URL対応を確認。
- 作者表示はアバター利用/個人利用/個人商用利用/法人利用/改変OK、Vtuber利用/再配布NG、暴力・性的表現OK、クレジットは記載可能な範囲。Vtuber利用・再配布の制限だけを私的保存禁止とは扱わない。個人的な非公開技術検査・一時複製・長期保管は明示されず、許可も禁止も推定しない。数値年齢/年齢ゲートは商品ページに見当たらず、年齢不記載だけを中立非性的な構造検査/T-poseの禁止理由にしない。
- 公式商品ページ画像は頭・胴・両腕を見せるが両脚を含まないクロップで、全身形状は確認できない。よって人型候補/非人型のどちらにも追加せず、unclassified 464を維持。正規無料download URL `https://booth.pm/downloadables/3587956?variation_id=8376265`へ認証・cookieなし、redirect追従なしのHEADを一度実施し、HTTP/2 302 Location `https://booth.pm/users/sign_in`を確認。GET、ログイン、認証回避、ZIP/VRM取得・解析・描画なし。`verification`は`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ再分類したが、個人の私的検査/複製/保管に関する権利軸は別途未解決。
- 更新後のR1/R2/R3以外797件の排他的主状態は、権利矛盾130、利用条件等未確認233、BOOTH認証待ち2、別サービス認証待ち17、NAS隔離hold2、物理対応不明14などで合計797。形状603/230/464は不変。B35 hold29は全件未アーカイブ。NASは読み取り専用で再監査し、487 ZIP/974 WebP、2,168,476,533 ZIP bytes、`verify_nas.py` `ok:true`/`errors:[]`、index 548,641 bytes/SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`を確認。root/models/previews 0777、index 0600、`.index.lock` 0 bytes/mode 000、named/default ACLなし、NFSv3 `rw,sec=sys,local_lock=none`、exportはprivate IPv4 /24表示。実効的なユーザー隔離・server ACL・UID/GID mapping/squash・lockは不明のため新規NAS保存を停止。NAS変更なし。
- citation source IDs39/40、B53 checkpoint `work/holiday-batch/booth-mixed-zip-reassessment-20261014-b53.json`。RDC/GitHub Actions/新規テストなし。

## B54：branshop-nao再評価（2026-10-14）

- 開始時に`git fetch origin --prune`を実行し、branch `main`、`HEAD`/`origin/main`=`026a5bcbf3987fd350a6656fcd0362cfe65a3fad`、worktree cleanを確認。B35 hold29の未再評価候補`branshop-nao`（BOOTH item6595645）を選定。
- 現行公式BOOTHページは無料`Nao_Contents.zip`（9.16 MB）にVRChat用asset一式（unitypackage/FBX/Texture等）とVRM形式3Dモデルを掲載し、作品説明は「2頭身ローポリキャラ」。これはページ記載で、実ZIP/VRMの取得・物理検査を意味しない。リンク先の匿名・redirectなしHEADはHTTP/2 302で`https://booth.pm/users/sign_in`。ログイン、認証情報/cookie使用、HEAD probeでのredirect follow、GETによるZIP取得、VRM解析/表示は実施せず、download gateは認証待ち。
- UVライセンスの基礎条項は個性表現目的のモデル利用・翻案許諾と、本人に収益が生じない個人利用での改変/パーツ流用を記載。PCUは個人商用利用、DDWは二次著作物の配布、SEU/VEUは成人向け性的/暴力表現の利用を許可する一方、基礎条項は個別許諾がないモデル/二次創作物の配布・販売を禁止する。DDWを未改変の元VRM配布許可へ拡張しない。規約はダウンロード者を利用者とし利用により同意成立、使用/売買時の著作者名・モデル名表記（箇所なし/技術事情の例外）、著作者の利益・配布/更新/公開停止を阻害する利用禁止、規約の変更可能性も記す。これらの許諾・制限は別軸として記録し、単なる再配布制限を私的保存禁止とは扱わない。
- ページ/規約は非公開の中立技術検査・長期保管を明示しない。従って禁止・許可どちらも推定せず、私的検査複製/retentionの権利軸は未解決。数値年齢・age gateを確認できず、SEU/VEUは利用内容の許諾でありモデル年齢の根拠ではない。年齢不記載だけで中立構造検査/T-poseを禁止しない。2頭身表現からshapeを推測せず、shape unclassifiedのまま。
- Catalog row `branshop-nao`は`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ変更。`download_url` null、`distribution_filename`/公式source URL維持、`download-scope.json`不変更。797件は正本とcheckpointから排他的に再計算し、NAS保存157、非人型68、権利矛盾130、利用条件等未確認232、NAS隔離hold2、物理ID対応不明14、混合ZIPのみの除外0、別host拒否2、dweb.link未試行/429 141、BOOTH認証待ち3、他サービス認証17、404 3、export-only 23、metadata/repository-only 5、合計797。ENRAI/noteの認証待ち1件はBOOTH認証3件に含めず、他サービス17件側に数える。shape603/230/464。
- B35初回hold29はcheckpointのper-model reviewとNAS indexで照合：29件すべて現在もNAS非収録。B54候補も未取得/未保存。NAS read-only auditは487 ZIP/974 WebP、2,168,476,533 bytes、ZIPのみ、`ok:true`/`errors:[]`。index 548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previews 0777、index 0600、lock 0 bytes/mode000、確認した各pathにnamed/default ACLなし。NFSv3 `rw,sec=sys,local_lock=none`、3 exportsはprivate IPv4 /24表示。ただしserver ACL、UID/GID mapping/squash、利用者別隔離、実効lockは未確認。第三者隔離を証明できないため新規保存停止。NAS設定・既存資産の変更なし。
- Citation ledger source IDs21/22/41はURL一意性を確認し、引用quote数2/2/1、ID21/22の閲覧日を2026-10-14に更新。B54 checkpoint `work/holiday-batch/booth-mixed-zip-reassessment-20261014-b54.json`。catalog validator、全797行の排他的partition assertion、NAS verifier、`git diff --check`に合格。RDC/GitHub Actions/不要テストなし。

## B55：neoneko-ngii再評価（2026-10-14）

- `git fetch origin main`後、branch `main`、`HEAD`/`origin/main`=`c556ac8eb1fc589eeb1ab5b3d1348ba093181663`、ahead/behind `0/0`を確認。B55の既存ローカル差分を確認し、対象は今回のカタログ/文書更新のみ。B35 hold29から`neoneko-ngii`（BOOTH item6254853）を選定。
- 現行公式ページはHTTP 200。無料offerは`ンギィ.zip` 828 KB、別に500円の「店長のおこづかい」offerを表示。両offerの内容が同一とは仮定しない。無料版ページはVRM 0.0、221 KB、4,160 polygons、2,080 meshes、1 material、19 bones、0 blendshapes、寸法1.82m×1.58m×0.16m、`ンギィ_v1.06.vrm`等を列記する。これは商品ページ記載であり、ZIP/VRM実体・member・カタログID対応の物理検証ではない。
- 作者表示は使用/改変使用OK、改変物販売/原本譲渡/転売NG。これら販売・移転制限だけを私的保存禁止とは扱わない。一方、一般商用利用、非公開の中立技術検査、個人的な一時複製/長期保管は明示されないため許可/禁止を推定せず、権利軸を未解決として維持。数値年齢/年齢ゲートはページ上で確認できない。キノコ説明・寸法・商品名から年齢/形状を推測せず、年齢不記載だけを中立構造検査/Tポーズの禁止理由としない。
- 公式無料download URLに認証/cookieなし・redirect追従なしのHEADを一度実施し、HTTP 302 `https://booth.pm/users/sign_in`を確認。GET、ログイン、redirect follow、取得、VRM解析/描画はなし。物理member mapping・shapeは未確認/unclassified。モデルrowの主状態を`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ変更し、取得ゲートと私的保存条件を別軸で保持。
- 全カタログ1,297 IDは一意。R1/R2/R3の基幹500 IDを除く797 IDの主状態を全データから再計算。NAS157、非人型68、権利矛盾130、利用条件等未確認231、NAS隔離hold2、物理mapping不明14、混合ZIPのみの除外0、別host拒否2、dweb.link未取得/429 141、BOOTH認証待ち4、他サービス認証17（VRoid Hub16＋note.com/ENRAI1）、404 3、VRoid Studio export-only23、metadata/repository-only5、合計797。ENRAI/noteはBOOTHではないため、同じ`official_free_download_auth_required_not_verified`ラベルでもBOOTH認証4件へ誤算入しない。shapeは603/230/464。
- B35 checkpointの41 ID/outcomeを照合。hold29は全件現在のNAS indexに存在せず、今回の`neoneko-ngii`も未保存。B35の3 archive recordsは3件ともindexに存在。
- NASは読み取り専用で再監査。487 ZIP/974 WebP、2,168,476,533 ZIP bytes、`verify_nas.py` `ok:true`/`errors:[]`。index 548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`、B54値から不変。root/models/previews 0777、index 0600、`.index.lock` 0 bytes/mode 000。named/default ACLなし。NFSv3 `rw,sec=sys,local_lock=none`、showmountの3 exportsはprivate IPv4 /24表示・wildcardなし。server ACL、UID/GID mapping、squash、利用者別隔離、実効lockは未確認のため第三者隔離は証明できず、新規NAS保存停止を継続。chmod/chown/ACL/NFS変更なし。
- Citation ledger source ID42は公式商品ページ（商品/仕様/利用条件3 quotes）、ID43は匿名download gate（1 quote）に各1件ずつ対応。B55 checkpointは`work/holiday-batch/booth-mixed-zip-reassessment-20261014-b55.json`。scratchには可視ページテキストとgate probeだけを残し、ZIP/VRM/HTMLなし。RDC/GitHub Actions/新規テストなし。
- 検証：`python3 scripts/validate.py`は1,297 models/unique IDs・11 catalog filesで成功。既存`unittest discover -s tests -v`は5 tests成功（追加テストなし）。全797 IDの排他的partitionは重複0/合計797、B35 hold29のNAS収録0、NAS verifierは`ok:true`/`errors:[]`、`git diff --check`成功。

## B56：ratenosu-untitled のB52調査を正本へ反映（2026-10-14）

- B55 commit後に`git fetch origin main`し、`main`の`HEAD`/`origin/main`=`8d62cd947bb2c137defdcdc85279fed48170d0d3`、worktree cleanを確認。B35 hold29からB52で調査済みだが未反映だった`ratenosu-untitled`（BOOTH item1571536）を選定。公式ページと既存gate evidence、citation ledger ID37/38を再照合。ID37はpage terms/listing 4 quotes、ID38は302 gate 1 quoteで、URL対応は各一意。
- 公式商品ページは無料`無題 .zip`（33.1 MB）と別の無料`無題_おまけ .zip`（5.24 MB）を表示。主package説明にはVRM/Unitypackage/Blend/PSDを記載するが、別offerの内容が同一とは仮定しない。これは商品ページ情報であり、ZIP/member/VRM実体・version・shape・catalog ID対応の物理検査ではない。
- 作者条件は無改造モデル/textureの再配布禁止、販売禁止、自作発言禁止、VRChatのpublic pedestalは許可が必要。販売・再配布・avatar用途の禁止を私的保存禁止へ読み替えない。一方、個人的な非公開中立技術検査・一時複製・長期保管の明示許諾も確認できず、許可/禁止を推定しない。数値年齢/age gateはページに記載なし。商品名のお兄さん表現から成年を推定せず、年齢不記載だけを中立検査/T-poseの禁止理由としない。
- 公式主package URL `https://booth.pm/downloadables/1560985?variation_id=2489465`を認証/cookieなし・redirect追従なしHEADで確認し、HTTP 302 `https://booth.pm/users/sign_in`。ログイン、redirect follow、GET、取得、VRM解析/描画なし。主状態を`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ更新し、私的保存権利軸は独立に未解決、shape unclassified、`download_url:null`、`vrm_version:null`を維持。表示上の配布名は`無題 .zip`。
- B56 checkpoint `work/holiday-batch/booth-mixed-zip-reassessment-20261014-b56.json`。読み取り専用NAS indexは487行・548,641 bytes・SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`で、候補IDなし。既存487 ZIP/974 WebPを変更せず、chmod/chown/ACL/NFS設定変更・追加保存なし。B35 hold29は未アーカイブを維持。RDC/GitHub Actions/新規テストなし。
- 検証：`scripts/validate.py`成功（1,297 unique IDs/11 files）、既存unittest 5/5成功、NAS verifier `ok:true`/`errors:[]`（487 ZIP/974 WebP, 2,168,476,533 bytes）。797件の排他的partitionは重複0/合計797（権利矛盾130、利用条件等未確認230、BOOTH認証待ち5、他認証17、その他は上表）、shape603/230/464。B35 hold29のNAS収録0、source37/38は一意でquotes 4/1、`git diff --check`成功。

## B57：neoneko-nolt のB35 hold再評価（2026-10-14）

- B56 commit後に`git fetch origin main`し、`main`/`origin/main`=`979a9fc570c898a4898159b18105474bd288622a`、worktree cleanを確認。B35 hold `neoneko-nolt`（BOOTH item7933453）を選定。B34に混合ZIPを理由とした配布範囲外記録があったため、現行公式ページとB35 hold理由を再照合した。
- 公式商品ページは認証なしGETでHTTP 200。無料`Nolt_ノルト_.zip`（22.9 MB）と別の「店長のおこづかい」500円offerを表示。無料ZIPの説明はVRM 0.0 `ノルト（Nolt）_1.3.vrm`と編集可能な`.vroid`を列挙するが、物理ZIP/VRM/member/metadata/shapeは未確認。別offerの内容を無料版と同一視しない。
- 作者の表示は使用/改変使用OK、改変物販売/原本譲渡/転売NG。販売・譲渡制限だけを私的保存禁止と解釈しない一方、個人的な非公開中立技術検査・一時複製・長期保管の明示許諾も確認できず、許可/禁止を推定しない。数値年齢/age gateは確認できず、名前/外見から年齢を推測しない。年齢不記載だけでは中立構造検査/T-poseを禁止せず、混合ZIPのみも除外理由としない。
- 公式無料URL `https://booth.pm/downloadables/8333210?variation_id=13285813`を認証/cookieなし・redirect追従なしHEADで確認し、HTTP 302 `https://booth.pm/users/sign_in`。ログイン、redirect follow、download URLへのGET、取得、VRM解析/描画なし。カタログ主状態を`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ変更し、私的保存権利軸、physical member-to-ID mapping、shapeは独立に未解決/未判定。`download_url:null`維持。citation source IDs44/45（product page 2 quotes、gate 1 quote）、B57 checkpointを参照。
- 読み取り専用NAS再確認：487 ZIP/974 WebP、ZIP 2,168,476,533 bytes、index 487行/548,641 bytes・SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`、candidate absent。NAS書込み・既存資産変更・chmod/chown/ACL/NFS変更なし。B35 hold29は全件未アーカイブ。RDC/GitHub Actions/新規テストなし。
- 検証：`scripts/validate.py`成功（1,297 unique IDs/11 files）、既存unittest 5/5成功（新規テスト0）、NAS verifier `ok:true`/`errors:[]`。797件の排他的partitionは重複0/合計797（権利矛盾130、利用条件等未確認229、BOOTH認証待ち6、他認証17ほか）、shape603/230/464。B35 hold29のNAS収録0。citation source IDs44/45は一意でquotes 2/1、`git diff --check`成功。

## B58：neoneko-roa のB35 hold再評価（2026-10-14）

- B57 push後に`git fetch origin main`し、`main`/`origin/main`=`440af19e4b409cdbecab3e17aa80d5373d4df75f`、worktree cleanを確認。B35 hold29から`neoneko-roa`（BOOTH item5108925）を選定し、B34/B35の混合ZIP/年齢理由を現行公式ページで再照合。
- 公式商品ページは認証なしGETでHTTP 200。無料`ロア.zip`（18.9 MB）にVRM 0.0の`ロア_1.01.vrm`（ページ記載16.4 MB）と`ロア_1.0.vroid`を掲載し、別の500円offerも表示。ページ記載は配布説明であり、物理ZIP/VRM/member/metadata/shape/カタログID対応を検証したものではない。別offerの内容は今回の判定対象に含めない。
- 作者表示は使用/改変使用OK、改変物販売/原本譲渡/転売NG。これらの販売・移転制限だけを私的保存禁止とは解釈しない。一方、個人的な非公開中立技術検査・一時複製・長期保管も明示されず、許可/禁止を推定しない。数値年齢/age gateは確認できず、年齢不記載だけで中立構造検査/T-poseを禁止しない。名前・寸法・外見から年齢/形状を推測しない。
- 公式無料download URL `https://booth.pm/downloadables/3730879?variation_id=8601679`を認証/cookieなし・redirect追従なしHEADで確認し、HTTP 302 `https://booth.pm/users/sign_in`。ログイン、redirect follow、download URLへのGET、取得、VRM解析/描画なし。カタログ主状態を`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ変更し、私的保存権利、物理member-to-ID mapping、shapeは独立に未解決/未確認。`download_url:null`維持。
- Citation ledger source ID46は公式商品ページ（仕様・同梱記載・利用条件2 quotes）、ID47は匿名download gate（1 quote）に各1件ずつ対応。B58 checkpointは`work/holiday-batch/booth-mixed-zip-reassessment-20261014-b58.json`。raw page HTML・response headers・ZIP/VRMは保存せず、scratchには抜粋descriptionとリダイレクト先だけを残した。
- B58の読み取り専用NAS監査は487 ZIP/974 WebP、ZIP bytes 2,168,476,533、`verify_nas.py` `ok:true`/`errors:[]`。index 487行/548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`、候補IDなし。root/models/previewsは0777、indexは0600、`.index.lock`は0 bytes/mode 000。named/default ACLなし。NFSv3 `rw,sec=sys,local_lock=none`、3 exportsはprivate IPv4 /24表示・wildcardなし。server ACL、UID/GID mapping、squash、利用者別隔離、実効lockは未確認のため第三者隔離を証明できず、新規NAS保存停止を継続。NAS書込み、chmod/chown/ACL/NFS変更なし。
- 検証：`scripts/validate.py`成功（1,297 unique IDs/11 files）。既存unittest 5/5成功（新規テスト0）。全797 IDの排他的partitionは重複0/合計797（権利矛盾130、利用条件等未確認228、BOOTH認証待ち7、他サービス認証17、その他は現行表）、shape603/230/464。B35 hold29は全件カタログに残り、NAS収録0。citation IDs46/47は一意でquotes 2/1、`git diff --check`成功。RDC/GitHub Actions不使用。

## B59：neoneko-romuru のB35 hold再評価（2026-10-14）

- B58 push後、最新`main`/`origin/main`=`728d245fa36eb78612dfe29cedecec3d120162f1`、worktree cleanを確認。B35 hold29の次候補`neoneko-romuru`（BOOTH item7933498）を選び、B34/B35の混合ZIP・年齢未記載に関する保留理由を現行公式ページと照合。
- 公式商品ページは認証なし・cookieなし・redirect追従なしGETでHTTP 200。0円offerは`ロムル.zip`（22.8 MB）で、ページはVRM 0.0 `ロムル_v1.0.vrm`と`.vroid`を列挙。別の500円「店長のおこづかい」offerは今回の対象と分けた。ページ掲載情報は実ZIP/VRM検査ではなく、物理member-to-ID対応も未確認。
- ページ記載のモデル仕様はVRM 0.0、14.4 MB、37,257 polygons、3 meshes、15 materials、107 bones、57 blendshapes、寸法1.2m×1.2m×0.3m。これは作者のlistingであり、実バイナリ・形状の確認済み値ではない。
- 作者表示は使用/改造使用OK、改変物販売/原本譲渡/転売NG。これらの販売・移転制限だけを私的保存禁止と解釈しない。一方、個人的な非公開中立技術検査・一時複製・長期保管も明示されず、許可/禁止を推定しない。商品説明/ページに数値年齢や年齢制限/age gateは見当たらず、名前・説明・外見から年齢を推定しない。年齢不記載だけを理由に中立構造検査/T-poseを禁止しない。混合ZIPも単独の除外理由にしない。
- 公式無料URL `https://booth.pm/downloadables/8333275?variation_id=13285900`を認証/cookieなし・redirect追従なしHEADで確認し、HTTP 302 `https://booth.pm/users/sign_in`。ログイン、download URLへのGET、取得、VRM解析/描画なし。カタログ主状態を`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ変更。私的保存権利、物理member-to-ID mapping、shapeは独立に未解決/未確認。`download_url:null`維持。
- Citation ledger ID48は公式商品ページ（3 quotes: 仕様、同梱member、利用条件）、ID49は匿名gate結果（1 quote）。B59 checkpointは`work/holiday-batch/booth-mixed-zip-reassessment-20261014-b59.json`。HTML・response headers・ZIP/VRMは保存せず、scratchにはページ説明抜粋とredacted gate結果だけを保持。
- B59の読み取り専用NAS verifier/index再確認は487 ZIP/974 WebP、ZIP bytes 2,168,476,533、`verify_nas.py` `ok:true`/`errors:[]`。index 487行/548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`、候補IDなし。権限/ACL/NFS詳細は同日B58監査を参照し、B59では再プローブしていない。既存資産/NAS設定変更、新規保存、chmod/chown/ACL/NFS変更なし。
- 検証：`scripts/validate.py`成功（1,297 unique IDs/11 files）、既存unittest 5/5成功（新規tests 0）。scope shape603/230/464。797 IDの排他的主状態は権利矛盾130、利用条件等未確認227、BOOTH認証待ち8（その他は現行表）、重複0/合計797。B35 hold29全件はカタログに残りNAS収録0。citation IDs48/49は一意、quotes 3/1。`git diff --check`成功。commit/push/readbackの検証結果はB59 checkpointの`git_delivery`に記録する。RDC/GitHub Actions不使用。

## B60：neoneko-shitakee のB35 hold再評価（2026-10-14）

- B59後に`git fetch origin main`し、作業開始時`main`/`origin/main`=`a4c46564ac8f730ae69a75b5f6b1fb7053439885`を確認。変更前worktreeはclean。B35 hold29の次候補として`neoneko-shitakee`（BOOTH item6254560）を再評価。
- 公式商品ページは認証・cookieなし・redirect追従なしGETでHTTP 200。無料offerは`シタケェ.zip`（12.9 MB）、ページ listing は`シタケェ2_v1.01.vrm`、VRM 0.0とblend/FBX/texture/PSD類。別の500円「店長のおこづかい」offerとは分けた。商品ページの記載であり、実ZIP/VRM/member-to-ID対応を検証したものではない。
- 作者表示は使用/改造使用可、改変物販売/原本譲渡/転売禁止。これらの販売・移転制限だけを私的保存禁止とは解釈しない。一方、個人的な非公開中立技術検査・一時複製・長期保管も明示されず、許可/禁止を推定しない。数値年齢/age gateは確認できず、年齢不記載だけで中立構造検査/T-poseを禁止しない。名前・外見から年齢/shapeを推測しない。
- ページ掲載の無料download URLを認証/cookieなし・redirect追従なしHEADで確認し、HTTP 302 `https://booth.pm/users/sign_in`。ログイン、redirect follow、download URLへのGET、取得、VRM解析/描画なし。カタログ主状態を`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ変更し、`download_url:null`を維持。私的保存権利、実ファイル、member-to-ID mapping、shapeは別軸で未解決/未確認。B35 hold29は引き続き全件NAS未収録。
- Citation ledger source ID50は公式商品ページ（quotes 4）、ID51は匿名download gate（quote 1）。両IDは一意。保存したのは最小限の引用・redacted gate evidenceのみで、HTML、response headers、ZIP/VRMは保存していない。B60 checkpointは`work/holiday-batch/booth-mixed-zip-reassessment-20261014-b60.json`。
- B60 NAS読み取り専用監査は487 ZIP/974 WebP、ZIP bytes 2,168,476,533、`verify_nas.py` `ok:true`/`errors:[]`。index 487行/548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`、候補IDなし。`/mnt/hdd` 0777/root:root、`/mnt/hdd/vrm` 0777/ws2:uucp、`models/`と`previews/` 0777/ws2:ws2、index 0600/ws2:ws2、空`.index.lock` 0 bytes/mode000。named/default ACLなし。NFSv3 `rw,sec=sys,local_lock=none`、3 exportsはprivate IPv4 /24限定。server ACL、UID/GID mapping、squash、user isolation、effective lockは未確認のため第三者隔離は証明できず、新規NAS保存停止。NAS書込み、chmod/chown/ACL/NFS変更なし。
- 検証：`scripts/validate.py`成功（1,297 models、1,297 unique IDs、11 catalog files）。既存unittest 5/5成功、新規tests 0。797 IDの排他的partitionは重複0/合計797（権利矛盾130、利用条件等未確認226、BOOTH認証待ち9、他サービス認証17、その他は現行表）。shape 603/230/464。B35 hold29は全件カタログに残り、NAS収録0。RDC/GitHub Actions不使用。commit/push/readbackの確定値はB60 checkpointの`git_delivery`に記録する。

## B61：neoneko-shoki-avatar-2 のB35 hold再評価（2026-10-14）

- B60後に`git fetch origin main`。作業開始時`main`/`origin/main`=`35b652cbb3f28641319d80ab1607056bd9ee3439`、worktree cleanを確認。B35 hold29中、B35 `per_model_review`順でB60後の次候補`neoneko-shoki-avatar-2`（BOOTH item8721870、候補レビュー24/41）を再評価。
- 公式ページは無認証・cookieなし・redirect追従なしGETでHTTP 200。無料offerは`さんぷるあばたー_2.zip`（1.09 MB）、ページ記載memberは`しょきあばたー_2_v1.0.vrm`等、VRM仕様版表示は0.0。blend/FBX/PNG/PSD/UV filesもlisting。別の500円「店長のおこづかい」offerとは分けた。これらは商品ページ上の記載であり、実ZIP/VRM・member-to-ID対応を確認したものではない。
- 作者の表示は使用・改変可、改変物の販売・原本の譲渡・転売は不可。これらの販売/移転制限だけを私的保存禁止とは解釈しない。一方、非公開の中立技術検査・一時複製・長期保管の明示もないため、許可/禁止を推定しない。数値年齢/age gateはページ本文で確認できず、年齢不記載だけで中立構造検査/T-poseを禁止しない。年齢や形状を推測せず、実ファイル内容は未確認。
- ページ掲載の無料download URL `https://booth.pm/downloadables/9471710?variation_id=14565241`へ無認証・cookieなし・redirect追従なしHEADを行い、HTTP 302 `https://booth.pm/users/sign_in`。redirect follow、ログイン、download URLへのGET、取得、VRM解析/描画なし。カタログ主状態を`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ変更し、`download_url:null`を維持。私的保存権利、shape、physical member mappingは別軸で未解決/未確認。B35 hold29は全件NAS未収録。
- Citation ledger source ID52は公式商品ページ（quotes 5）、ID54は匿名download gate（quote 1）。ID重複なし。scratchには最小限の本文抜粋とgate結果だけを記録し、HTML・response headers・ZIP/VRMは保存していない。checkpoint: `/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-mixed-zip-reassessment-20261014-b61.json`。
- B61 NAS読み取り専用監査：487 ZIP/974 WebP、ZIP bytes 2,168,476,533、`verify_nas.py` `ok:true`/`errors:[]`。index 487行/548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`、B35 hold29のNAS entry 0。`/mnt/hdd` 0777 root:root、`/mnt/hdd/vrm` 0777 ws2:uucp、models/previews 0777 ws2:ws2、index 0600、lock 0 bytes/mode000。named/default ACLなし。NFSv3 `rw,sec=sys,local_lock=none`、exports 3件は`192.168.1.0/24`。server-side ACL、UID/GID mapping、squash、per-user isolation、effective lock semanticsは未確認のため非公開隔離は証明できず、新規保存停止。NAS書込み、chmod/chown/ACL/NFS変更なし。
- 検証：`scripts/validate.py`成功（1,297 models、1,297 unique IDs、11 catalog files）。既存unittest 5/5成功、新規tests 0。797 IDの排他的partitionは重複0/合計797（権利矛盾130、利用条件等未確認225、BOOTH認証待ち10、他サービス認証17、NAS隔離hold2、物理対応不明14、その他は完成条件表）。shape 603/230/464。B35 hold29は全件catalogに残り、NAS収録0。RDC/GitHub Actions不使用。commit/push/readbackはB61 checkpointの`git_delivery`に記録。

## B62：neoneko-tofu-seijin のB35 hold再評価（2026-10-14）

- B61後に`git fetch origin main`。作業開始時`main`/`origin/main`=`cb2484f5a4031b85c901b922fb3f03ff9b46c4f0`、worktree cleanを確認。B35 `per_model_review`順でB61（24/41）の次にあたる`neoneko-tofu-seijin`（25/41、hold29中15番目、BOOTH item5101910）を選定。
- 公式商品ページは無認証・cookieなし・redirect追従なしGETでHTTP 200。無料offerは`とーふ星人.zip`（431 KB）、ページはVRM 0.0 member `tofu_seijin.vrm`と仕様表示（280 KB）を掲載。別の500円支援offerは今回の選定対象外。これは商品ページ情報であり、物理ZIP/VRM/member-to-ID対応を検証したものではない。
- 作者表示は使用・改変可、改変物販売・原本譲渡・転売不可。これらの利用/移転制限だけを私的保存禁止とは解釈しない。一方、個人的な非公開中立技術検査・一時複製・長期保管は明示されず、許可/禁止を推定しない。年齢数値/age gateの記載なしだけでは中立検査を止めない。商品プレビューは塊状の胴と両脚を示し、腕/手や明確な頭胴区分が見えず、作者説明も手/口なし。名前やspecies labelではなく構造を根拠に、`official_product_page_shape_non_humanoid_not_archived`へ分類。確認したプレビューに明確な性的/不適切表示は見えないが、実VRM/実内容は未確認。年齢は推定しない。
- ダウンロードURLへのgate probe、ログイン、取得、VRM解析/描画なし。`download_url:null`維持。物理member-ID対応は未確認。Citation ledger IDs55-58は一意（source55 page quotes 4、source56-58 official preview images）。B62 checkpointは`work/holiday-batch/booth-mixed-zip-reassessment-20261014-b62.json`。
- 読み取り専用NAS監査：`verify_nas.py`は487 ZIP/974 WebP、ZIP bytes 2,168,476,533、`ok:true`/`errors:[]`。`index.jsonl`は487行/548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。B35 hold29全IDがNASに存在しない。`/mnt/hdd`は0777/root:root、`/mnt/hdd/vrm`は0777/ws2:uucp、models/previewsは0777/ws2:ws2、indexは0600/ws2:ws2、空`.index.lock`は0 bytes/mode000。確認したpathにnamed/default ACLなし。実マウントはautofs配下のNFSv3 `rw,sec=sys,local_lock=none`。`showmount`はHDDを含む3 exportsがprivate IPv4 /24限定・wildcardなしと表示。NAS server-side ACL、UID/GID mapping、`root_squash`/`all_squash`、利用者別隔離、実効lockは未確認のため第三者隔離は証明できず、新規保存停止を継続。NAS書込み・chmod/chown・ACL/NFS設定変更なし。
- 検証：`scripts/validate.py`成功（1,297 unique IDs/11 files）、既存unittest 5/5成功（新規tests 0）。shape603/231/463。797件の排他的partitionは重複0・合計797（NAS157、非人型69、権利矛盾130、利用条件等未確認224、NAS隔離hold2、物理対応不明14、混合ZIPのみ除外0、別host拒否2、dweb.link未取得/429 141、BOOTH認証待ち10、他サービス認証17、404 3、VRoid Studio export-only23、metadata/repository-only5）。B35 hold29のNAS収録0。`git diff --check`成功。RDC/GitHub Actions不使用。

## B63：neoneko-tsukiyomi-akane のB35 hold再評価（2026-10-14）

- `origin/main`をfetchして、開始基準の`main`/`origin/main`がB62 commit `16bf82fea0a89b87cffa44ec51063374fb58df1d`で一致することを確認。B35 `per_model_review`順でB62（25/41、hold29中15番目）の次の`neoneko-tsukiyomi-akane`（26/41、hold29中16番目、BOOTH item5036417）を選定。既存差分はこのB63変更だけ。
- 公式BOOTH商品ページと同ページの作者previewを確認。無料`月詠赤音.zip` 20.5 MBに`月詠赤音_1.02.vrm`（VRM 0.0、表示14.2 MB）および`月詠赤音_1.0_ベース.vroid`を掲載。別500円「店長のおこづかい」variantも掲載され、作者は内容不変と説明。これらは商品ページのlistingであり、物理ZIP/VRM/member-to-ID対応を検証したものではない。
- 作者表示は使用・改変使用および髪型/衣装変更を許可し、改変物販売・原本譲渡・転売を禁止する。販売/移転制限だけを私的保存禁止とは解釈しない。一方、非公開技術検査・一時複製・長期保管の明示条件もないため保存許可/禁止は推定しない。ページ本文の年齢関連語検索では数値年齢/age gateを確認できず、年齢を推定しない。年齢不記載だけでは中立的な構造検査/Tポーズを止めない。
- 商品ページの公式四面preview ID61は頭・胴・両腕・両脚が見えるため人型候補へ追加。ID60は上半身crop、ID62は表情資料でshape根拠には使わない。形状はページpreview上の予備分類であり、実VRM検査・年齢確定・権利確認・保存承認ではない。B28既存checkpointは本IDを含む12商品/12代表probeで集計12件HTTP 302 loginを記録するが、商品別response rowはない。B63でdownload URLを再probeせず、ログイン・取得・展開・VRM検査・renderも行わない。
- カタログ主状態を`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ更新し、`download_url:null`と物理member対応未確認を維持。私的保存条件は独立して未解決。`data/download-scope.json`のhuman candidateに追加。B35 hold29は全件カタログに残り、NAS収録0。
- Citation ledger source ID59は公式商品ページ（verbatim quotes 8件）、ID60/61/62は公式preview画像。ledgerは61 source entriesで数値ID重複なし、最大ID62（ID59-62は全て存在）。scratch evidenceは商品ページの必要最小抜粋とpreview reviewだけを保存し、HTML、download URL、ZIP/VRMは保存していない。
- B63 NAS read-only auditは487 ZIP/974 WebP、ZIP bytes 2,168,476,533、`verify_nas.py` `ok:true`/`errors:[]`。index 487 rows/548,641 bytes・SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`で前回baseline不変。`/mnt/hdd` 0777 root:root、`/mnt/hdd/vrm` 0777 ws2:uucp、models/previews 0777 ws2:ws2、index 0600、`.index.lock` 0 bytes/mode 000。確認pathにnamed/default ACLなし。autofs配下NFSv3 `rw,sec=sys,local_lock=none`。`showmount`は3 exportsをprivate IPv4 /24に限定しwildcardなしと表示。server-side ACL、UID/GID mapping、squash、利用者別隔離、実効lockは未確認で第三者隔離は未証明。NAS書込み、chmod/chown、ACL/NFS設定変更なし。新規保存停止を継続。
- 検証：`scripts/validate.py`成功（1,297 models、1,297 unique IDs、11 catalog files、scope 604/231/462）。既存`python3 -m unittest discover -s tests -v` 5/5成功、新規tests 0。797 IDの排他的partitionは重複0/合計797（NAS157、非人型69、権利矛盾130、利用条件等未確認223、NAS隔離hold2、物理対応不明14、混合ZIPのみ除外0、別host拒否2、dweb.link未取得/429 141、BOOTH認証待ち11、他サービス認証17、404 3、VRoid Studio export-only23、metadata/repository-only5）。shape 604/231/462。`git diff --check`成功。RDC/GitHub Actions不使用。変更のcommit/push有無はB63 checkpointの`git_delivery`を参照。
- 生`verification`ラベルは排他的797件とは別集計：`rights_unverified_hold` 223、`official_binary_inspected_rights_conflict_not_archived` 130、`official_binary_inspected_embedded_rights_conflict_not_archived` 3（Polygonal Mind R1/R2の797件外）、`official_free_download_auth_required_not_verified` 12（BOOTH 11＋ENRAI/note 1）、`official_hub_auth_required` 16。candidateの遷移先labelはcatalog JSONと一致。B63 checkpointは両方の集計を保持する。

## B64：sakurabido-megumicchi のB35 hold再評価（2026-10-14）

- B63後に`git fetch --no-tags origin main`。開始基準`main`/`origin/main`は`3ba4a9a48ff5a2ce8d1706cca8c19d2ef903055d`で一致。B35 `per_model_review`順33/41・hold29中23番目の`sakurabido-megumicchi`（BOOTH item5689713）を選定。B64は継続中handoffを先行処理したため順序外。B35順27–29番の`pike-aurora`/`pike-moon-night`/`pike-steam-rabbit`はB36/B40で個別再評価済み。よって次の未再評価holdは`propofol7-satake-nagisa`（review30/41、hold20/29）。
- 公式商品ページは無料ZIP `さくらリクオ_フリーアバター_50F_めぐみっち.zip` 14.8 MBと、Vroid/VRM/readmeのページ記載を示す。一方、支援/tip版ではVroidファイル付きZIPを取得できる旨もあり、両offerの物理内容やVRM memberとcatalog IDの対応は未確認。商品ページの範囲を超えてZIP/VRMを取得・検査していない。
- 商品ページはアバター/Vtuber/個人/個人商用/法人利用・改変を許可し、再配布を禁止、法人クレジットを可能な範囲で必須とする。これらの利用条件を私的保存禁止とは読み替えないが、非公開の技術検査・一時複製・長期保管も明示されないため保存許可/禁止を推定せず、私的保存権利は未解決。
- 詳細規約リンクの匿名・cookieなし・redirectなしHEADはHTTP/2 404。本文、login、代替URLには進んでいない。商品ページの50フォロワー記念はキャラクター年齢ではなく、年齢関連語も見当たらない。年齢を推定せず、年齢不記載だけで中立構造検査/T-poseを禁止しない。実VRM内容や年齢は未確認。
- 作者の後ろ向き全身previewは頭/胴/両腕/両脚を示すため人型候補へ追加。close-upは全身判定に使っていない。これはpage-previewの予備分類で、実VRM/T-pose検査・保存承認を意味しない。既存B13 gate checkpointは本IDを含む12商品/17 catalog ID、14 probe全件HTTP 302 loginを記録し個別response rowはない。gate再probe/認証/ダウンロードなし。catalog `verification`は`official_free_download_auth_required_not_verified`へ整理し、`download_url:null`と私的保存権利の未解決を維持。candidate IDは人型候補scopeへ追加したが、scope掲載は取得・保存許可ではない。
- Citation ledger IDs63-66は一意。ID63の商品ページquote 2件、ID66の404応答記録quote 1件、ID64/65はpreview画像。scratchには本文の最小抜粋、画像レビュー記録、404状態だけを置き、HTML/ZIP/VRMなし。
- B64 read-only NAS再監査：`verify_nas.py`成功、487 ZIP/974 WebP、ZIP 2,168,476,533 bytes、errorsなし。index 487 rows/548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。`/mnt/hdd` 0777 root:root、`/mnt/hdd/vrm` 0777 ws2:uucp、models/previews 0777 ws2:ws2、index 0600、lock 0 bytes/mode000、named/default ACLなし。NFSv3 `rw,sec=sys,local_lock=none`。showmountは3 exportsを`192.168.1.0/24`に限定しwildcardなし。server-side ACL、UID/GID mapping、squash、利用者隔離、実効lockは未確認で、非公開隔離を証明できない。NAS既存487件保護、新規保存停止。NAS書込み、chmod/chown、ACL/NFS設定変更なし。
- Verification：`scripts/validate.py`成功（1,297 models/unique IDs、11 catalog files、scope 605/231/461）、既存unittest 5/5成功、新規tests 0、`git diff --check`成功。排他的partitionは重複0/797（NAS157、非人型69、権利矛盾130、利用条件等未確認222、NAS隔離hold2、物理対応不明14、混合ZIPのみ除外0、別host拒否2、dweb.link未取得/429 141、BOOTH認証待ち12、他サービス認証17、404 3、VRoid Studio export-only23、metadata/repository-only5）。raw labelsは`rights_unverified_hold` 222、`official_free_download_auth_required_not_verified` 13（BOOTH12＋ENRAI/note1）、embedded-rights conflict3（797件外）、`official_hub_auth_required`16。shape 605/231/461。B35 hold29は全件catalog内・NAS収録0。
- Checkpoint `work/holiday-batch/booth-mixed-zip-reassessment-20261014-b64.json`。RDC/GitHub Actions不使用。

## B65：propofol7-satake-nagisa のB35 hold再評価（2026-10-14）

- 開始時に`git fetch --no-tags origin main`を実行し、`main`/`origin/main`とも`3498d6560335d7a05721fcd94d5487ee99becbdd`を確認。B35 original review orderでは`propofol7-satake-nagisa`（BOOTH item8447196）が30/41、hold29中20番目。B64時点の次候補指定と一致。
- 公式商品ページは無料`SatakeNagisa_0.4.zip`（96.8 MB）と無料版内容の`VRMファイル`を列記。無料版銃は無可動モデルとして区別され、射撃/炎等のギミックは別のEX版説明にある。公開creator manual Ver0.4（2026-08-27）はHumanoid骨格・UpperChestなしを記すが、骨格情報だけで体形・人型分類は確定しない。公式previewだけでは頭・胴・両腕・両脚を同時に明瞭確認できず、`data/download-scope.json`は変更しない。実ZIP、member-to-catalog-ID対応、VRM metadata/binary、T-poseは未検査。
- 商品ページのタグ`青年`は数値年齢ではない。公開ページ/説明書に数値年齢や実際の年齢ゲートを確認できず、年齢を推定しない。B35旧記録にある「年齢未確認」を中立検査の禁止根拠とする扱いを撤回する。年齢の未記載・非数値タグだけでは、中立・非性的なVRM構造検査/T-poseを禁じない。実際の年齢制限・内容は入手根拠ができた時に個別判定。
- 商品ページはVN3 license templateを参照し、公開manualにもVN3 PDFへのリンクがある。匿名Google Drive viewerは`Sign in`を表示し、license全文・個別条件は確認できなかった。商品ページのアバター利用/無料版の条件付きpublic uploadと、私的な技術検査・一時複製・長期保管の許諾は別軸。非公開保存の許可・禁止を推定せず、商用/再配布/アバター利用の制限だけで保存禁止とも判定しない。規約の沈黙も許可とはみなさず、私的保存条件は未解決。
- 公式無料URL `https://booth.pm/downloadables/9536544?variation_id=14104950`への匿名HEADはHTTP 302で`https://booth.pm/users/sign_in`へ遷移。redirect追従・cookie/credential・GET・login・download・extract・renderはなし。状態を`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ変更し、`download_url:null`、shape scope未変更、NAS未保存を維持。B35 hold29は引き続きcatalog内・NAS収録0。
- Citation ledger source IDs67–70は一意で各sourceに根拠quoteを添付。最小抜粋のみを`/home/ws2/.hermes/cache/scratch/vrm-b65-20261014-evidence.txt`に保存。HTML、認証情報、ZIP/VRMは保存していない。B65個別JSON checkpointは作成済みと確認できず、B65の結果本文とこの根拠抜粋を参照。
- B65後、B35 hold29の未着手は`sakurabido-mirucchi`（review34/41・hold24/29）、`tatougai-oninoko-kiri`（review36/41・hold26/29）、`yumenonakaya-rem-lowpoly`（review41/41・hold29/29）の3件。次候補は`sakurabido-mirucchi`。権利矛盾130件と他の許諾未確認件の個別監査は未完。
- NASは読み取り専用で再確認：`verify_nas.py` `ok:true`/`errors:[]`、487 ZIP/974 WebP、ZIP 2,168,476,533 bytes、`index.jsonl` 487 rows/548,641 bytes・SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。`/mnt/hdd` 0777 root:root、`/mnt/hdd/vrm` 0777 ws2:uucp、models/previews 0777 ws2:ws2、index 0600、`.index.lock` 0 bytes/mode000。確認pathにnamed/default ACLなし。NFSv3 `rw,sec=sys,local_lock=none`、3 exports/3 host entries、wildcardなし、private network限定（prefix /24）。サーバー側ACL・UID/GID mapping・squash・user isolation・実効lockを確認できず、非公開隔離は未証明。既存487件保護・新規保存停止を継続。NAS書込み、chmod/chown、ACL/NFS設定変更なし。

## B66：sakurabido-mirucchi のB35 hold再評価（2026-10-14）

- 開始前に`git fetch --no-tags origin main`を実行し、開始時`main`/`origin/main`は`3498d6560335d7a05721fcd94d5487ee99becbdd`で一致。B35 original review順34/41、hold29中24番目の`sakurabido-mirucchi`（BOOTH item5715397）を選定。
- 公式商品ページは無料`さくらリクオ_フリーアバター_50F_みるっち.zip`（20.2 MB）を掲載し、ページ上の同梱物はVRoid/VRM/readme。別記載の支援時VRoid提供との実内容・同一性は未検証。ページはアバター/Vtuber、暴力・性的表現、個人/個人商用/法人利用、改変を許可し、再配布を禁止、法人creditを可能な範囲で必須とする。商用/再配布/アバター条件と非公開技術検査・一時複製・長期保管は別軸であり、これらの禁止・許可だけから私的保存の可否を推定しない。
- 商品ページが参照するFANBOX post5545930は匿名取得404で全文未確認。利用規約の沈黙を保存許可とは扱わず、私的検査・一時複製・長期保管条件は未解決。ページ上に数値年齢/実際の年齢ゲートは確認できず、`年齢`/`年令`/`歳`/`未成年`/`18禁`/`R-18`/`R18`/`成人`/`age`/`minor`の語句も見つからなかった。商品名の`50F`をフォロワー数以外に解釈せず、年齢を推測しない。年齢未記載だけでは中立・非性的な構造検査/Tポーズ表示を禁止しない。実際のVRM内容や年齢制限は未確認。
- 公式preview source73は顔・上半身の拡大で全身形状根拠にならない。source74の背面全身像では頭・胴・両腕・両脚・足が見え、衣服で覆われ、画像自体に明示的な性的内容はない。腕は下向き斜めでT-poseではない。これを根拠に`data/download-scope.json`のhumanoid candidateへ追加したが、実VRM・member-to-ID対応・Tポーズ/VRM内容は未検査。
- 公式無料download endpointへの匿名HEADはHTTP/2 302、LocationはBOOTH sign-in。redirect追従、cookie/credential、GET、login、download、extract、renderはなし。`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ状態を更新し、`download_url:null`、NAS未保存を維持。shape scopeは606人型候補/231非人型/460未判定。
- B35 hold29は全件catalogに残り、NAS収録は0。B66後に未再評価で残るのは`tatougai-oninoko-kiri`（review36/41・hold26/29）と`yumenonakaya-rem-lowpoly`（review41/41・hold29/29）の2件。次は`tatougai-oninoko-kiri`。R1/R2権利矛盾130件と、他の許諾未確認220件の全件個別根拠監査は未完了。
- 現行排他的797件の内訳は権利矛盾130、利用条件等未確認220、BOOTH認証待ち14（全1,297件のraw `official_free_download_auth_required_not_verified`は15＝BOOTH14＋ENRAI/note 1）。`rights_unverified_hold`は220。B66一件の状態更新による差分であり、未確認群全件を監査済みとは扱わない。
- NASは読み取り専用再確認で487 ZIP/974 WebP、ZIP 2,168,476,533 bytes、`index.jsonl` 487 rows/548,641 bytes・SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`、verifier `ok:true`/`errors:[]`。親/モデル/previewディレクトリ0777、index0600、lock mode000、named/default ACLなし、NFSv3 `rw,sec=sys,local_lock=none`、3 exportsはprivate IPv4 /24限定でwildcardなし。server-side ACL/UID-GID mapping/squash/user isolation/effective lock未確認のため第三者隔離は未証明。既存487件保護、新規保存停止、NAS書込み/chmod/chown/ACL/NFS変更なし。
- Citation ledger source IDs66/71–74は各URLとの対応を確認し、ID一意性を検証。テキストsourceには根拠quoteを登録し、画像sourceは目視所見をcheckpointへ記録。Checkpoint `work/holiday-batch/booth-mixed-zip-reassessment-20261014-b66.json`、最小証拠抜粋`/home/ws2/.hermes/cache/scratch/vrm-b66-20261014-evidence.txt`。RDC/GitHub Actions不使用。

## B67：tatougai-oninoko-kiri のB35 hold再評価（2026-10-14）

- 開始時に`git fetch --no-tags origin main`を実行し、`main`/`origin/main`とも`3498d6560335d7a05721fcd94d5487ee99becbdd`を確認。B35 original review orderでは`tatougai-oninoko-kiri`（BOOTH item5189443）が36/41、hold29中26番目。B66時点の次候補指定と一致。
- 公式商品ページは無料`oninoko_kiri_free_.zip`（25.7 MB）を掲載し、無料版の内容として`.vroid`と`oninoko_kiri00.vrm`、VRM 0.0を記載。有償版（おまけ）のVRM 3体は別offerとして扱い、無料版との内容同一性を仮定しない。物理ZIP/memberは未取得。
- 商品条件は個人/商用利用、アバター等の活動、改変を許可し、無料分の再配布はcredit付きで許可する一方、有償分の再配布を禁止する。利用・再配布条件を個人的な非公開保存へ読み替えない。ページは列挙外の利用について相談を求め、非公開技術検査・一時複製・長期保管は具体的に記載しないため、保存許可/禁止のどちらも推定しない。年齢数値/実年齢ゲートは商品本文で見つからず、年齢は推測しない。年齢未記載だけでは中立・非性的な構造検査/T-poseを禁止しない。
- 公式preview source77は「基本無料」coverの全身像で、文字が下半身に一部重なるものの頭・胴・左右の腕・左右の脚・足が見える。人型候補へ追加し、`data/download-scope.json`を607人型/231非人型/459未判定に更新した。source78/79の表情シートは上半身のみ。source80は画像自体に有償版VRMの例と明記されるため、無料版の形状根拠から除外。T-pose/実VRM/member-to-ID対応/モデル内容は未検査。
- 無料download endpointの匿名HEADはHTTP 302でBOOTH sign-inへ遷移。redirect追従、cookie/credential、GET、login、download、extract、renderなし。状態を`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ更新し、`download_url:null`、NAS未保存を維持。匿名アクセス待ちは取得ゲートの主状態であり、私的保存条件は別途未確定。
- B35 hold29は全件catalogに残りNAS収録0。B67後に未再評価で残るのは`yumenonakaya-rem-lowpoly`（review41/41・hold29/29）1件。現行排他的797件は権利矛盾130、条件未確認219、BOOTH認証待ち15。全1,297件raw labelsでは`rights_unverified_hold` 219、`official_free_download_auth_required_not_verified` 16（BOOTH15＋ENRAI/note1）。130件の権利矛盾と残る未確認群の個別根拠監査は未完で、一括解除しない。
- 読み取り専用`verify_nas.py`は487 ZIP/974 WebP、2,168,476,533 ZIP bytes、`ok:true`/`errors:[]`。このバッチでNAS/権限/NFS変更なし。Citation ledger source IDs75–80のURL対応とID一意性を確認し、ページ/gate/preview根拠を付与。Checkpoint `work/holiday-batch/booth-mixed-zip-reassessment-20261014-b67.json`、最小証拠`/home/ws2/.hermes/cache/scratch/vrm-b67-20261014-evidence.txt`。ZIP/VRM/HTML/認証情報を保存・commitせず、RDC/GitHub Actions不使用。

## B68：yumenonakaya-rem-lowpoly のB35 hold再評価（2026-10-14）

- 作業開始時に`git fetch --no-tags origin main`を実行し、`main`/`origin/main`とも`3498d6560335d7a05721fcd94d5487ee99becbdd`。B35 original review 41/41・hold29/29の`yumenonakaya-rem-lowpoly`（BOOTH item7296492）を最後の未着手holdとして選定。B67 checkpointに残る未着手IDは本件のみ。
- 公式商品ページは無料`Rem_ver0.01.zip`（3.31 MB）を表示。内容物欄は`Rem_ver1.00`見出し下にVRM data/UnityPackage/blend/PNG texture/FBX/termsを列挙し、更新履歴にはVRM追加・フォルダ名v1.01とある。物理ZIP・member・版・catalog ID対応は未確認。混合ZIPは単独の除外理由ではない。
- 商品ページはVN3ライセンスの日本語PDFをリンクするが、匿名viewerではPDF本文を確認できなかった。非公開技術検査・一時複製・長期保管条件、商用/アバター/再配布条件は内容を読めず未解決。条件不明を保存許可/禁止のどちらにも推論しない。
- 商品説明の「睡眠不足のおとこのこ」は数値年齢/実際の年齢ゲートではなく、年齢を推測しない。年齢未記載だけで中立・非性的な構造検査/T-poseを禁止しない。公式front/back全身previewは頭・胴・両腕・両脚・足を示し、人型候補へ追加。腕は下向きでT-poseではなく、画像は衣服を着た中立表現で明らかな性的/不適切内容なし。実VRM/metadata/contentは未検査。
- 公式無料download endpointへの匿名HEADはHTTP 302でBOOTH sign-inへ遷移。redirect追従、cookie/credential、login、GET、download、extract、VRM inspectionなし。モデル状態を`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ変更し、`download_url:null`、private-storage rights未解決を維持。
- `data/download-scope.json`は608人型候補/231非人型/458未判定。正本catalogの1,297 IDsは一意。B35 hold29 IDsは全件catalogに存在し、NAS index内0件、全件個別再評価済み。現行状態内訳はBOOTH auth16、rights-unverified9、embedded rights conflict1、non-humanoid1、NAS privacy hold2。全29件をアーカイブしたことは意味しない。
- R1/R2/R3以外の797 IDsをcatalog raw `verification`と供給元で独立再集計：NAS157、非人型69、権利矛盾130、条件未確認218、NAS隔離hold2、対応不明14、別host拒否2、creator-index unavailable/429 141、BOOTH auth16、他無料auth1、VRoid Hub auth16、404 3、export-only23、metadata/repository-only5、合計797。全1,297件raw labelsは`rights_unverified_hold` 218、`official_free_download_auth_required_not_verified`17（BOOTH16＋ENRAI/note1）、`official_binary_inspected_rights_conflict_not_archived`130、`official_hub_auth_required`16。未確認群全件・権利矛盾130件の個別根拠監査は未完で、一括解除しない。補助年齢レビューでは現行218 notes中117件に年齢不明/未記載、81件に年齢語と保留語が同居するキーワードヒットを検出（年齢が唯一の理由という判定ではない）。11件の旧notesで年齢不明を中立検査/Tポーズの禁止理由とする扱いを訂正し、verification・shape・保存状態は変更なし。残りは個別根拠確認が未完。
- 読み取り専用`verify_nas.py`は487 ZIP/974 WebP、2,168,476,533 ZIP bytes、`ok:true`/`errors:[]`。`index.jsonl` SHA-256は基準値と同一。`stat`は`/mnt/hdd` 0777 root:root、`/mnt/hdd/vrm` 0777 ws2:uucp、models/previews 0777 ws2:ws2、index 0600、lock 0 bytes/mode000。確認対象全pathの`getfacl`にnamed/default ACLなし。`findmnt`はNFSv3 `rw,sec=sys,local_lock=none`、`showmount -e`は3 exports/3許可entry・private IPv4 /24・wildcardなし（具体的network values omitted）。クライアント可視情報ではserver-side ACL/UID mapping/squash/利用者隔離/実効lockを証明できず、非公開隔離は未確認のまま。NAS/権限/NFS設定変更なし、新規保存停止継続。Citation ledger source IDs81–84はURL対応・一意性を確認し、source81に2 quotes、source82に1 response quoteを添付。Checkpoint `work/holiday-batch/booth-mixed-zip-reassessment-20261014-b68.json`、最小証拠`/home/ws2/.hermes/cache/scratch/vrm-b68-20261014-evidence.txt`。ZIP/VRM/HTML/認証情報を保存せず、RDC/GitHub Actions不使用。

## B69：権利矛盾の私的保存軸・年齢注記の補助監査（2026-10-14）

- 開始前に`git fetch --no-tags origin main`を実行。`main`と`origin/main`は`55bb91c5c559a76ffe0a463c432896085df88267`で一致し、作業ツリーはclean。読み取り専用NAS監査は487 ZIP/974 WebP、2,168,476,533 ZIP bytes、`verify_nas.py` `ok:true`/`errors:[]`、`index.jsonl` SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`で基準値と一致。モード/ACL/NFSの実測は上記B68監査と同じで、非公開隔離はサーバー側未証明。NAS書込み・chmod/chown・ACL/NFS変更なし。
- カタログ正本とcollections 11ファイルを集約し、`official_binary_inspected_rights_conflict_not_archived`は130 unique IDsと確認。notesの語句スクリーニングでは115件が商用/再配布/アバター利用などの利用軸に触れる一方、125件には個人的な私的コピー・技術検査・保管条件を明示する語句が見つからなかった。これはnotesのキーワード集計であり、規約の読み直しや個別の法的判定ではない。保存禁止とも保存許可とも推定せず、根拠URL単位の監査を続ける。
- 同一の公式商品ページに紐づく`yousoron-amane-type-1`, `-type-1-body`, `-type-2`, `-type-2-body`, `-type-3`, `-type-3-body`, `-type-4`, `-type-4-body`の8件を一群として再点検。BOOTH item4911831は各VRMを無料で列挙し、利用・改変・商用利用を認め、「再販のみ」控えるよう案内する（既存citation source ID14。ページを2026-10-14に再確認）。正本notesに記録済みのVRM metadataは`commercialUssageName=Disallow`/`licenseName=Redistribution_Prohibited`であり、商用・再配布軸の差異はrights-conflictラベルに残す。ただし、この差異は非商用の私的構造検査用複製・長期保管を禁止する根拠ではない。ページも私的な技術検査用長期アーカイブを明示しないため、保存許可/禁止は未確定のまま。status、download scope、NAS資産は変更せず、新規取得/プレビュー生成なし。
- 年齢記載の補助キーワードscreenは現行`rights_unverified_hold` 218件中117件が年齢不明/未記載表現、81件が年齢語と保留語の併記にヒット（B68集計と同じ）。重複語・履歴noteを含み、年齢が唯一の保留理由の件数ではない。B68以前に訂正済みの11件以外を本監査で一括解除せず、年齢の未記載だけでは中立・非性的検査/Tポーズを禁止しない原則を維持する。
## B70：権利矛盾グループの利用軸と保存軸の分離（2026-10-14）

- 開始時に`git fetch --no-tags origin main`を実行。`main`/`origin/main`は`39f92611114a2280c14d052b1df73c48e96d9594`で一致し、作業ツリーclean。NAS読み取り専用検証は487 ZIP/974 WebP、2,168,476,533 ZIP bytes、`verify_nas.py` `ok:true`/`errors:[]`、index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。directory modeは`/mnt/hdd`・`/mnt/hdd/vrm`・models・previewsが0777、index 0600、lock mode000; 確認pathにnamed/default ACLなし。NFSv3 `rw,sec=sys,local_lock=none`、3 exportsはprivate IPv4 /24限定、wildcardなし。サーバー側隔離は引き続き未証明。設定変更・NAS書込みなし。
- `neoneko-junk-konojiblockun`, `-sumoutori`, `-johanshin`, `-johanshin-v091`, `-bone-model`, `-keisatsukan`の6 IDsを同一のBOOTH item5421814のグループとして確認。現行の商品ページは「使用、改変して使用 OK」とし、改変物販売・原本譲渡・転売を不可としている（citation source ID90、2026-10-14確認）。一方、6件の既存VRM metadataは`allowedUserName=OnlyAuthor`等を記録しており、使用許諾の射程に矛盾が残る。商用/譲渡/再販制限は各利用行為の条件として扱い、私的な技術検査用コピーや長期保管の禁止とは同一視しない。商品ページに非公開検査・保管の明示条件はなく、保存許可も推定しない。`OnlyAuthor`とページの使用許可との不一致が未解決のため、検査利用の許諾も確定扱いしない。6件のverificationは維持し、取得・NAS保存なし。
- B69開始時点の全130 rights-conflict IDsのnotes lexical screenでは125件に私的コピー/検査/保存軸の語句がなかった。B69で同一ページの8件、B70で6件を個別に確認したため、B70時点でこの初期欠落群の未確認は111件。語句が見つかった他5件も個別解釈は未完。これはnotesの優先付けであり、残件を保存禁止/許可とみなさない。
- 次段階は残る111件と語句ヒット5件を商品URL/現行規約/VRM metadataに照らしてグループ単位で確認し、利用用途の矛盾と私的複製/保管条件を分けて記録する。その後、現行`rights_unverified_hold` 218件を同じ行為別基準で続ける。B36時点の237件は履歴値で、現行値ではない。年齢未記載だけで中立検査/Tポーズを禁じず、実際の年齢制限・不適切内容は個別判断する。RDC/GitHub Actions不使用。

## B71：リウォレ4 variantの利用・年齢・保存条件整理（2026-10-14）

- 開始時baselineは`main`/`origin/main` `5eb5e026aca119a69e6364f270408de3079c4ade`。fetch後も一致。NAS読み取り専用再検証は487 ZIP/974 WebP、2,168,476,533 ZIP bytes、`verify_nas.py` `ok:true`/`errors:[]`、index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。B70監査以降NAS内容・設定は変更せず。
- `chemical-riwore-normal-white`, `chemical-riwore-normal-black`, `chemical-riwore-lop-white`, `chemical-riwore-lop-black`の4件（BOOTH item4458219）を一群として再確認。現行ページはVRM対応サービス/ゲーム、配信/撮影、改変を認める一方、改変済み/未改変の再配布、政治的利用、侮辱・不快行為等を禁じ、列挙外の使用は作者照会としている（citation source ID91、2026-10-14確認）。既存notes記録の埋込metadataは性的/暴力的利用を許可するが、作者条件の射程と一致するか未解決で、センシティブ用途の許可とは扱わない。商品ページは「活発なウサギの少年」と記すが、数値年齢・年齢制限は確認されず、年齢を推測しない。年齢未記載だけを中立的構造検査/Tポーズの禁止理由としない。一方で、技術検査/表示が列挙許可に含まれるかページ上で確認できないため、本追補で追加検査・描画・Tポーズ表示は実施せず、verification labelを維持。これは年齢を理由とする停止ではない。
- 商品ページは私的技術検査用複製・長期保管の条件を明記しない。再配布禁止を私的保存禁止と同一視しない一方、保存許可も推定せず、4件ともNAS未保存。既存notesから外見・年齢を推定してholdする表現を除き、許諾/保存/年齢の各根拠を分離して記録した。
- B69のYousoron 8 variantsのnotesにも、商品ページの商用/改変可・再販禁止は利用行為の条件であり、私的複製/長期保管の許可・禁止を示さない旨を追記。8件はrights-conflictのまま、status・download scope・NAS資産変更なし。
- B69初期screenで語句欠落だった125件のうち、B69/B70/B71で計18件（8+6+4）を商品単位で確認。更新後の現行notes lexical screenではrights-conflict 130件中107件に私的保存軸の語句がなく、残る5件の明示語句も個別解釈は未完。語句欠落107件＋語句ヒット5件を、保存可否の自動判定に使わず個別監査する。次のまとまり候補はBOOTH item4935982のNaoya Model Pack 4 variant。`rights_unverified_hold`は現行218件（B36時点237件は履歴値）。取得・描画・NAS書込み・設定変更なし。

## B72：Naoya Model Pack vol.1の4 variantを同一商品ページで確認（2026-10-14）

- 開始時`main`/`origin/main`は`dfe854010c950e4feb6c109d3fcd0d848119efe7`で一致。NAS読み取り専用検証は487 ZIP/974 WebP、2,168,476,533 ZIP bytes、`verify_nas.py` `ok:true`/`errors:[]`、index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。
- `naoya-model-pack01-aquamarine`, `-ametrine`, `-rubellite`, `-peridot`の4件（BOOTH item4935982）を一群として確認。商品ページは無料VRM ZIPと別売り有料`.vroid` ZIPを区別し、モデルデータの改変・商用利用・有償改変/受託制作を認める一方、有料部分の再利用可能な形での再配布、政治/宗教活動、誹謗中傷を禁じ、列挙外用途は作者照会としている（citation source ID92）。既存VRM metadataの`OnlyAuthor`/`commercialUssageName=Disallow`/`Redistribution_Prohibited`とは利用許諾の射程に矛盾が残る。
- 商用/再配布条件は各利用行為の条件であり、私的技術検査用複製・長期保管の禁止とはみなさない。ページに私的複製/保管条件は明示されず、保存許可も推定しない。4件のrights-conflict labelは維持し、notesのみ行為別に補足。新規ダウンロード・描画・Tポーズ表示・NAS保存なし。

## B73：ほしうさのUV License誤読修正と個別再分類（2026-10-14）

- 開始時`main`/`origin/main`は`dfe854010c950e4feb6c109d3fcd0d848119efe7`。BOOTH item2556708とページがリンクするUV Licenseを確認（citation source IDs93–94）。現行リンクは`pcu=true&ccu=true&seu=true`で、個人/法人商用利用と成人向け性的表現を許可するが、暴力表現の許可は示していない。
- `usamimiten-hoshiusa-black`の旧note「UV Licenseが成人向け暴力表現を許可」は誤り。埋込`violentUssageName=Disallow`との矛盾は確認できないため、rights-conflictから`rights_unverified_hold`へ再分類。これは保存許諾の認定ではなく、私的な検査用複製/長期保管の条件が未確認のための保留。既存ZIPは削除済みで、新規取得・NAS保存なし。
- `usamimiten-hoshiusa-pink`の埋込`allowedUserName=OnlyAuthor`/`CC_BY`と、公開された幅広い利用条件・二次配布制限との不整合は継続するためrights-conflictを維持。商用/性的利用・二次配布の条件を私的保存禁止と同一視せず、UV License/BOOTHページに私的保存条件の明記もないため許可も推定しない。両モデルとも年齢を推測せず、年齢不記載だけを中立検査/Tポーズの禁止理由にしていない。
- B73後のraw labelsは`official_binary_inspected_rights_conflict_not_archived` 129、`rights_unverified_hold` 219（B36時点237は履歴値）。B69初期のprivate-axis語句欠落125件から、B69–B73で24商品ページ対応IDを確認・notes補正した。B73時点のlexical screenは補助的な履歴値であり、B74のnotes更新後に件数を再利用しない。語句検索は保存可否の判定に使わない。次候補として挙げたBOOTH item3871143（Cloodworks Hatsuka PC/Quest 2 variants）はB74で再評価済み。shape scopeは608/231/458のまま。NAS487 ZIP/974 WebPとindex hash不変、ACL/NFS設定変更なし。RDC/GitHub Actions不使用。
- B35 checkpointの41 review rows（保存3、非人型9、hold29）を現行catalog labelsとNAS indexに突合。元hold29は全件NAS未収録で、現状はBOOTH認証待ち16、`rights_unverified_hold` 9、rights-conflict 1、非人型1、NAS隔離hold2。全29を一律に「許諾未確認」と扱わず、catalogの個別状態を維持。読み取り照合のみで状態変更なし。

## B74：Cloodworks Hatsukaの利用許諾・metadata範囲再確認（2026-10-14）

- 開始時`main`/`origin/main`は`dfe854010c950e4feb6c109d3fcd0d848119efe7`で一致。B72/B73の未コミット追補を引き継ぎ、最新ページとNASを先に読み取り確認した。
- BOOTH item3871143の現行商品ページは無料Hatsuka ZIP（20.6 MB）にPC/Quest VRMを列挙し、改変・再配布・商用利用・再販売に特段の制限はないとする一方、VRoid Studio内包著作物の利用規約が適用されると明記し、著作権を株式会社クルード・ワークスに帰属としている（citation source ID95）。VRoid公式ガイドは提供素材がCC0ではなくpixivが権利を保持すること、特別表記のない素材には広い利用ライセンスがあること、特別表記素材には個別条件があることを説明する（source ID96）。同ガイドのソフト目的外利用/リバースエンジニアリング禁止はVRoid Studio本体に関する条項と読み、出力VRMの中立構造検査を明示的に禁じる根拠とは確認できないが、検査許可も推定しない（source ID96）。
- 既存checkpoint `work/holiday-batch/booth-authenticated-batch-20261010-30.json`は正規無料UIからの取得、2つの実VRM member、metadata `licenseName=Other`/`otherLicenseText=パブリックドメイン（著作権放棄）`、Tポーズ/顔確認を記録する。公開条件の著作権留保・VRoid素材権利とmetadataのpublic-domain表記の適用範囲差は未解決のまま、2 IDsの`official_binary_inspected_rights_conflict_not_archived`を維持した。この権利範囲の不整合は、商用・再配布・アバター利用の禁止を私的保存禁止と誤読した判断ではない。個人的な非公開技術検査用複製・長期保管の明示条件は確認できず、保存許可/禁止を推定しない。年齢記載なしは中立検査を止める理由にせず、既存の構造/Tポーズ確認を維持。今回はページ閲覧だけで、再取得・再描画・追加NAS保存なし。
- B35 hold29を既存checkpoint 41 rowsと現行catalog/NAS indexで再照合。全29 IDsはNAS未収録で、現行状態はBOOTH認証待ち16、`rights_unverified_hold` 9、権利矛盾1、非人型1、NAS隔離hold2。全29を一括して許諾未確認にせず、個別状態を維持。総catalogは1,297 IDs一意、shape scopeは608/231/458。全1,297 raw labelsは権利矛盾129、`rights_unverified_hold` 219。
- B74読み取り専用NAS監査：487 ZIP/974 WebP、ZIP 2,168,476,533 bytes、`verify_nas.py` `ok:true`/`errors:[]`。`index.jsonl` 487 rows/548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。`/mnt/hdd`・`/mnt/hdd/vrm`・models/previewsは0777、index 0600、lock 0 bytes/mode000、確認pathにnamed/default ACLなし。NFSv3 `rw,sec=sys,local_lock=none`。`showmount -e`の3 exportsはすべてprivate IPv4 /24、wildcardなし。server-side ACL、UID/GID mapping、squash、利用者隔離、実効lockは未確認で、第三者隔離は証明できない。既存487件を保持し、新規保存停止継続。NAS書込み・chmod/chown・ACL/NFS設定変更なし。
- Citation ledger sources95–96はそれぞれ公式BOOTH商品ページとVRoid公式ガイドに対応し、引用evidenceを登録済み。RDC/GitHub Actions不使用。

## B75：最新main・NAS・B35 hold29の再確認とVRoid Studio規約範囲の補正（2026-10-14）

- B75開始時に`git fetch --no-tags origin main`を実行。`main`と`origin/main`は`dfe854010c950e4feb6c109d3fcd0d848119efe7`で一致。worktreeには同一タスクのB72–B74変更が未コミットで存在したため保持し、fetch/監査で作業ファイルを上書きしていない。
- NASは読み取り専用で実数487 ZIP/974 WebP、ZIP 2,168,476,533 bytes。`scripts/verify_nas.py --nas-root /mnt/hdd/vrm`の実行結果は487 entries/974 previews、ZIPのみ、`ok:true`/`errors:[]`。`index.jsonl`は487 rows/548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。既存ファイルに変更なし。
- `stat`で`/mnt/hdd` 0777 root:root、`/mnt/hdd/vrm` 0777 ws2:uucp、models/previews 0777 ws2:ws2、index 0600 ws2:ws2。root/vrm/models/previews/index/`.index.lock`の`getfacl`ではnamed/default ACLなし。lockは0 bytes/mode 000。NFSv3 `rw,sec=sys,local_lock=none`。`showmount -e`のclient-visible結果は3 exports・wildcardなし・private IPv4範囲のみ。server-side ACL、UID/GID mapping、squash、user isolation、実効lockは未確認で、非公開性は証明できない。新規保存停止を継続し、NAS/ACL/NFS設定を変更していない。
- B35 checkpointの41 review rowsをcurrent catalog/NAS indexにID単位で照合。初期hold29は29 unique IDsすべて現行カタログに存在しNAS未収録。現行verificationの内訳はBOOTH認証待ち16、`rights_unverified_hold` 9、rights-conflict 1、非人型1、NAS隔離hold2。全29を「許諾等未確認」や保存禁止へ一括分類せず、個別状態を維持した。
- current catalogは1,297 IDs unique。全体のraw labelsは`official_binary_inspected_rights_conflict_not_archived` 129、`rights_unverified_hold` 219。B36の130/237は履歴値。129/219の全件個別根拠監査は未完で、キーワードscreenから許可・禁止を推定しない。年齢の未記載だけを中立構造検査/Tポーズの禁止理由にせず、実際の年齢制限や内容は別途判断する。
- B75で公式VRoid Studio個別規約を現在のページから確認し、citation source ID97にArticle 7、11–13および改訂履歴のevidenceを登録。Article 12は出力物の利用を含有コンテンツの個別ライセンスに従わせ、Article 13は個別条件表示のない提供コンテンツについて使用・複製・アーカイブ・改変・表示を含む標準ライセンスを定める。Article 11は第三者権利/利用条件の遵守を求める。Article 7はVRoid Studio自体の目的外利用・解析行為等を規定する。公式ガイドは特別表示のない提供モデルについて、出力モデルデータをVRoid Studio以外のソフトウェアで編集・利用する例を明示する（source ID96）。したがってArticle 7を独立ツールによる中立検査の一律禁止とは読まないが、特定VRMの素材・個別条件未確認を理由に全体の検査/保存許可も推定しない。これらは全出力VRMへの包括許可/禁止を意味しない。
- Hatsuka PC/Quest（BOOTH item3871143）の商品ページ(source95)は改変・再配布・商用利用等に特段の制限なしとしつつ、VRoid Studio内包著作物の条件適用とClood Worksの著作権帰属を明記。公式ガイド(source96)は提供コンテンツがCC0ではなくpixivが権利を保持すること、個別表示のない提供素材に広いライセンスがあることを説明する。標準ライセンスにアーカイブ権が明記される点をnotes/docsに反映したが、当該VRM内の正確な素材・個別表示とmetadataのpublic-domain表記の適用範囲は未解決のためrights-conflictを維持。商用/再配布/アバター制限を保存禁止とは扱わず、個別モデル全体への保存許可も推定しない。追加取得・再描画・NAS保存なし。
- state/scope labelsはB75で変更なし。source IDs95–97を追記。RDC/GitHub Actions不使用、NAS書込み/権限設定変更なし。

## B76：くらんも「モブ」2 variantsの商用利用・私的保存軸を分離（2026-10-14）

- 開始時の`main`/`origin/main`は`82e894ac9df707a6e43d37e960fc36d21b2ec279`で一致し、B75追補はpush済み・worktree clean。BOOTH item4136312の公開商品ページを再確認（citation source ID98）。無料版ZIPは16.6 MB、説明は無料VRMモデルを「モブ1」「モブ2」の2体とし、有償版は別ページitem4110873として区別する。
- 現行ページは改変/編集可能、配信・動画での商用利用可能、クレジット不要とする一方、モデル再配布/転載、NFT化、R18等を禁止し、「規約が更新された場合、最新日時の規約が有効」とする。B76は本文を確認し、年齢/age gate、個人的な非公開検査、複製、保存/保管に関する記載を確認できなかった。年齢を推測せず、未記載のみを中立構造検査/Tポーズ表示の禁止理由にしない。
- 既存`kuranmo-mob-mob1`/`kuranmo-mob-mob2`記録の実VRM検査・SHA-256は変更せず、両者の埋込`commercialUssageName=Disallow`とページの「配信、動画での商用利用可能」の範囲矛盾を理由にrights-conflictを維持。ここで確認した再配布禁止は私的保存禁止と同義ではないが、保存条件が明記されないため保存許可も推定しない。2 IDsのverification、shape scope、NAS状態は変更なし。再ダウンロード、再描画、NAS書込みなし。
- B76で`verify_nas.py`を読み取り専用で再実行し、487 ZIP/974 WebP、ZIP 2,168,476,533 bytes、ZIPのみ、`ok:true`・`errors:[]`を確認。`index.jsonl` SHA-256も`0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`で不変。raw rights-conflict 129・`rights_unverified_hold` 219も不変。NAS権限/ACL/NFS exportsを読み取り専用で調査したが、client-visibleなworld-writable directoryとサーバー側隔離未証明のため新規保存停止を継続。NAS書込み、chmod/chown、ACL/NFS設定変更、RDC、GitHub Actionsなし。
- B35 `per_model_review`のhold29をcurrent catalog/NAS indexと再照合。29 IDすべてindex未収録。現在のverificationは認証待ち16、`rights_unverified_hold` 9、rights-conflict 1、非人型1、`official_binary_inspected_humanoid_render_confirmed_nas_privacy_hold` 2。B35 checkpoint内の歴史snapshot `verification_after_review` は29件すべて`rights_unverified_hold`で、20/29 IDは後続レビュー後のcurrent catalog labelと異なる。checkpointを過去記録として保持し、現行状態はcatalog/indexを正とする。B76ではhold/statusの変更なし。

## B77：BOOTH「マシェリ」のOnlyAuthor・私的検査/保管軸を分離（2026-10-14）

- 開始時`main`/`origin/main`は`ae1e44f2beffca64d42043a3612edf2a2854d87f`で一致、worktree clean。B19（2026-10-10）で認証済み正規配布から取得・検査済みの`shiroten-macherie-sailor`/`shiroten-macherie-rabbit`を対象に、今回は現在の公開BOOTH item4921493と公式VRM 0.0 schemaを確認（source IDs99,101）。実ファイルを再取得せず、既存SHA-256/GLB検査記録を維持。
- 現在の商品ページは無料VRMを2衣装（セーラー、子うさぎミルクカラー）として列挙。VRSNSの個人利用、モデルを使用したライブ/動画配信/SNS掲載、クレジットなしを許可し、再配布（営利/非営利、改変有無を問わず）と他人がダウンロードできる状態での公開、公序良俗に反するコンテンツへの使用を禁止。改変は有償版のみ・個人利用に限る。商用利用の明示許可は確認できず、許可と推定しない。列挙外用途は作者へ照会するよう明記。数値年齢・実際の年齢ゲートは記載されず、「子うさぎ衣装」からキャラクター年齢を推測しない。
- 埋込`allowedUserName=OnlyAuthor`は公式VRM 0.0 schema上「アバターとして利用できるユーザー」を制限する値で、ページのVRSNS個人利用許可とアバター利用軸で矛盾。`Redistribution_Prohibited`はページの再配布禁止と整合する。いずれもファイルの個人非公開保存を禁止する根拠にはしない。一方、非公開の構造検査/複製/長期保管は規約に列挙されず、未列挙用途は作者照会とされるため、許可・禁止のどちらも推定しない。このページ解釈から法令上の例外/許諾も判断しない。
- 年齢不記載だけを中立構造検査/Tポーズ表示の禁止理由にしないが、未列挙用途の照会が未了のためB77では追加検査・Tポーズ生成・再取得を行わず、NAS保存なし。verification/shape scope/NAS indexに変更なし。権利矛盾はアバター利用範囲に限定して維持。
- B77 NASを読み取り専用で再確認：`verify_nas.py`は487 ZIP/974 WebP、2,168,476,533 bytes、`ok:true`・`errors:[]`。index 487 rows/548,641 bytes・基準SHA-256は不変。NFSv3 `rw,sec=sys,local_lock=none`、確認pathにnamed/default ACLなし、exportsは`192.168.1.0/24`限定。client-visible親directoryは0777で、サーバー側利用者隔離は未証明のため、新規保存停止を維持。NAS index/artifacts、mode、ACL、NFS設定は変更していない。

## B78：BOOTH「あまね Type-1〜4」の商用・再販・私的保管軸を分離（2026-10-14）

- 開始時`main`/`origin/main`はB77 commit `db80ad3cf939f696c5c5a29392030ddc5ed6814b`で一致、worktree clean。権利矛盾129 recordsのsource URL群からBOOTH item4911831（8 variants）を選び、公開商品ページを再確認（source ID14）。無料allType ZIP（52.2 MB）と8種の個別無料VRMを掲載し、100円の支援版と無料版は同一ファイルと表示。今回はリンクをクリックせず、追加取得・再検査・描画なし。
- 商品ページはcluster/VRC等での利用、モデル/名前の改変、商用利用を許可し、「再販のみ」控えるよう記載。既存8 VRMの`commercialUssageName=Disallow`とは商用利用軸で直接矛盾する。一方、ページの再販制限とmetadataの広い`Redistribution_Prohibited`は適用範囲を同一視せず、非再販の再配布許可も推定しない。いずれも私的な非公開構造検査・複製・長期保管の許可/禁止を示さず、ページにもその条件は明記されない。
- 法律・条例・公序良俗に反する行為、政治/宗教にかかわる表現での利用は禁止。クレジットは任意。ページ本文/表示に数値年齢・age gateは見当たらず、年齢を推測しない。年齢不記載だけで中立構造検査/Tポーズを禁止しない。verification/既存SHA-256/shape scope/NAS indexは変更なし。NAS保存停止を維持。
