# Hermes Agent 継続一括実行指示（R1/R2・R3検証完了後）

2026-10-09の初回連続処理はmain `2d45b3d3e5d84223fd2642f3158c03fdcbfa0bd1`から開始し、結果更新をcommit `51a5d3451dfc0de5bfd68b9db73822d2fcebec99`に反映。その後のRetry-After継続結果はcommit `e39984779d01cbfbc1235d303c26f1f688455aa3`、追加の季節429履歴はcommit `778890ce5811cd5025a95115174858ea7f929f34`に反映。今回のHTTP 429再試行上限対応はその最新mainを基点とする。実行後の最新状態は[結果レポート](hermes-bulk-run-results.md)が正本。次回はこの文書とレポートを読み、`main`最新とNAS実体を再確認してから継続する。

## 目標・完了済みの扱い

`goura32/official-vrm-catalog`の実機未処理分を**一度のHermes依頼で可能な限り連続処理**する。最優先は作者公開の`data/collections/polygonalmind-halloween-rising.json` **60件**と`polygonalmind-xmas-chibis.json` **80件**（計140件）。同一実行で処理可能分を終えたら、他の公式・原作者が無償公開する直接VRMへ継続（ToxSam originals 10件、NeonGlitch86の許諾確認可能分、公式サンプル等）。認証が必要なBOOTH/Hub/Studio等は認証なしでの正規取得可否を確認し、必要なら対象だけ保留する。作者の無料公開でも利用権限が確認できない対象は取得・保存しない。

**不変の基準値**:
- 登録総数**1,297**。R3 100件とR1/R2 400件の計500件は既に処理済み。R1/R2/R3**以外の797件**が探索集合で、41 IDは直接VRM取得を試行、残る756 IDは本実行で直接リクエスト未試行。季節140件のうち7 IDに直接要求済み（Halloween/Xmas 001、Halloween 002/003/004/005、Xmas 002）。Halloween 005は初回と許可された再試行がともに429で終端化し、残る133 IDは未試行。797は「NASへ保存すべき797件」ではない。
- 現在のNASは**ZIP 339件、WebP 678枚**（今回9件追加）。今回の開始時338件と当初330件の全既存索引行が不変。現在の未圧縮合計**1,238,527,933 bytes** → ZIP **597,068,385 bytes**、削減率**51.7921%**。最終`verify_nas.py`は`ok:true`・`errors:[]`。次回は339件を不変baselineとし、既存データを保全。
- 選別リストは**人型候補556、非人型候補243、未判定498**。今回新規の実VRM目視分類は人型9・非人型4。ToxSam Chubby Tubby Catは作者プレビューと実VRM描画で二足人型を確認、The Wormは作者プレビューで手足のない虫状のため取得前除外。MJMoonbow Dragon 2/3も作者PNGから人型候補、Dragon 8は保留、Dragon 9は四足の非人型。候補分類は全件の実物確認ではない。ZIPは実VRM比較で採用済み、**圧縮比較を繰り返さず`--format zip`で統一**する。

**権利・取得上の保留（再配布許諾や正規URLの新証拠がない限り自動再取得しない）**:
- R3のプレビュー品質: `polygonalmind-100avatars-r3-229`（1件、実VRM人型確認済み、NAS未保存）。
- R1/R2の形状不明: `polygonalmind-100avatars-013-standard`、`-013-voxel`、`-034-standard`、`-034-voxel`（それぞれ完全な`polygonalmind-100avatars-...` ID、4件）。
- R1/R2の埋込権利・作者表示矛盾: `polygonalmind-100avatars-132-standard`、`polygonalmind-100avatars-196-standard`、`polygonalmind-100avatars-166-voxel`（3件）。
- MJMoonbow:既存`mjmoonbow-skinnie1-5-41eb4fe`に加え、今回取得した16件の埋込`Redistribution_Prohibited`（全IDは結果レポート、NAS未保存）。
- 今回追加の権利矛盾: `neonglitch86-shapey`（埋込`allowRedistribution=false`）、`numinia-starter-avatar-01`・`numinia-avatar-arla`（埋込`CC_BY`対公開CC0、NAS未保存）。
- URL制約: `neonglitch86-index-1`・`neonglitch86-index-3`は別hostへのリダイレクトを2回とも拒否。ミラー/ゲートウェイへ迂回しない。Halloween/Xmas 001は履歴上各6回、Halloween 002/003、Xmas 002、Halloween 004/005は許可された再試行後も429となり終了。Halloween 005の初回要求は`2026-10-09T01:24:33.662302Z`、唯一の再試行は`01:40:43.514108Z`に開始し、`01:40:43.664481Z`に429（Retry-After: 900）。dweb.linkの最新期限は`2026-10-09T01:55:43.664481Z`。残る季節133 IDとToxSam `King Mutatio`は未試行で、期限中は初回アクセスを含めネットワーク要求なしで延期する。同一IDの再試行は最大1回で、成功しなければ終端化する。
- 今回の確定非人型は`toxsam-original-bffd07cc-601`、公式仕様サンプル3件、MJMoonbow Dragon 9（作者の実レンダー画像で四足を確認）。これらは人型保存キューへ戻さない。

根拠とチェックポイントは`docs/hermes-bulk-run-results.md`にある。保留は次の一括処理の進捗を妨げない。根拠なしにライセンスを一括で`CC0`に置き換えない（R1/R2は作者README条件、R3は別条件）。

## 作業上の絶対条件

1. **カタログJSONが正本**（`data/models.json`、`data/collections/*.json`）。スクリプトに合わせた値やIDの改変禁止。検証済みメタデータ・選別IDと根拠の追記だけを実施し、モデル件数を増やすことを目的にしない。
2. **取得対象は作者/公式が正規に無料公開したものだけ**。NFT購入・保有必須、第三者権利不明、利用条件の矛盾、ログイン障壁・利用者本人による認証が必要なもの、アクセス制限の回避が必要なものは個別保留。認証情報やVRMのバイナリ/画像を外部AI API・GitHubに送信しない。利用条件が途中で変われば新しい根拠を記録する。
3. NAS永続化物は**人型VRMだけを1モデル1ZIP（内部`model.vrm`）**とし、正面Tポーズ`768×1024`・顔正面`512×512`のWebP2枚、`index.jsonl`、管理ロック以外の配布ZIP・VRM・不要ファイルを永続化しない。VRMや画像のSHA-256を索引に対応付け、展開後VRMハッシュが元ファイルと一致することを要求。
4. 見た目の人型は頭/胴/両腕/両脚（亜人や人型ロボットも可）を根拠に判断。Humanoidリグのみで判断しない。**形状が不明なら無料取得条件確認の上、一時ダウンロード後にモデル実体を描画**。明確な非人型は取得前除外してよい。人型でも正面画像の品質を満たさないものは個別保留。
5. 書込み前に**NAS実体・NFSマウントと空き容量**を`findmnt -T /mnt/hdd/vrm`等で確認。前回は`nas1.local:/volume1/hdd`へのNFSv3。マウント不在時に同名ディレクトリをローカル作成しない。**既存338件を絶対に上書き・削除しない**。始動時のNAS index各行とSHA-256を安全な場所に記録し、処理後に既存行が不変であることを検証。NFS遅延/タイムアウト時はファイル実体とindexを照合してから必要最小の復旧を行う。推測で再実行・削除しない。
6. 作業機の`~/.local/state/official-vrm-catalog/`に中断再開用チェックポイント（処理日時、ID、出典、取得結果、GLB/VRM版、形状、権利・画像品質、NAS保存、SHA-256、理由）を残す。ログ・ZIP一時ファイルはNASには残さない。途中に失敗があっても別IDを処理する。**HTTP 429は同一IDにつき初回取得後の再試行を最大1回だけ許可**し、Retry-Afterを守る。再試行開始をcheckpointへ先に記録して回数を消費し、成功しなければ（再度429を含む）`retry_exhausted`として終端化して以後取得しない。Retry-Afterの絶対UTC期限はhost単位でcheckpointに永続化し、期限中は同じhostへの全要求を止める（未試行IDへの初回アクセスもネットワークなしで延期）。最新期限経過後に同じ正規hostだけで再開し、別ゲートウェイには切り替えない。配布元への過剰な並列ダウンロードや無限リトライ禁止。
7. 未コミット変更があれば尊重し、作業に必要な差分だけ`commit/push`。**RDC・GitHub Actions不使用**。依存の大量アップグレード、テストの過剰追加、既に解消済みの圧縮実測・R1/R2形状レビューの再実施はしない。正常動作を阻害する不具合が出た時だけ最小修正と対象テストを行う。

## 一括作業の順序

1. `git fetch`・最新main・`docs/nas-storage.md`・`docs/hermes-bulk-run-results.md`・NAS索引・保存済みモデル/画像・チェックポイントの整合を確認。`python3 scripts/verify_nas.py --nas-root /mnt/hdd/vrm`を実行し、**339件/678枚の開始時監査**を確認。NASマウント未確認なら書込み作業はしない。
2. 季節140 IDを正本からキュー化。Halloween/Xmas 001とHalloween 002/003、Xmas 002、Halloween 004/005は再試行上限に達したため除外。最新のdweb.link期限（2026-10-09 01:55:43.664481 UTC）後、未試行133 IDを元の正規hostで続ける。429が出た場合はhost期限を更新し、同hostへの全要求（未試行IDの初回要求を含む）をネットワークなしで延期する。
3. 取得物ごとにGLB/VRM構造、実版、ライセンス/作者埋込情報、同一バイナリハッシュを検査。外形は作者プレビューまたは実VRM描画で人型/非人型/判定保留に分ける。人型はTポーズ・顔正面のWebPを生成し、実際に画像・画角を点検。NASに`scripts/archive_vrm.py --format zip --confirm-humanoid`で保存。元VRMと復元ZIPのSHA-256、プレビューID・画像SHAを照合。失敗IDを記録して進む。
4. 季節キューの処理可能分が終わったら、**同じ一括実行中に**今回未試行の公式/作者公開VRMへ進む。ToxSam Chubby Tubby Catは画像上の人型候補からVRM実体・権利・描画を検査し保存済み。The Wormは作者画像で手足のない虫状のため事前除外。既確認のToxSam、Neon CC0、MJMoonbow、Numinia、VRM仕様サンプルは再取得しない。ToxSam `King Mutatio`はdweb.link待機のまま。累計結果は保存9、非人型4、権利矛盾19、リダイレクト拒否2。認証必要のBOOTH商品は`auth_required`として保留。既保存・非人型・権利保留は処理キューから除外。
5. 最後に全件`python3 scripts/verify_nas.py --nas-root /mnt/hdd/vrm`で`ok:true`・`errors:[]`を確認し、**開始時339件の索引行・保存ファイルハッシュが変わっていないこと**を確認。実績レポート・正本の根拠つき更新・選別リストを必要最小限の差分で整備。`git diff --check`・`scripts/validate.py`（必要なら既存4単体テスト）後にcommit/push。処理待ち・保留を再開可能な状態で残す。

## 最終報告

**直近実行分の新規実績**（Halloween 005の許可済み再試行も429で終端、残る季節133 IDとKing Mutatioはhost cooldown中にネットワーク要求なしで延期。今回のNAS新規保存0）と**現在累計339 ZIP/678 WebP**、NAS監査、既存330件の不変性、Git commit SHA、再開チェックポイント、次回の最優先残件を日本語で簡潔にまとめる。

本書は実行指示であり、**記載した時点ではHermesを起動していない**。実行時は合理的な範囲で**逐次の小分け依頼なしに実処理を続行**し、必要不可欠な利用者認証・権利判断のみ個別保留として報告する。
