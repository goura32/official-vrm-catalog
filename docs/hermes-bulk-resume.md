# Hermes Agent 継続一括実行指示（R1/R2・R3検証完了後）

2026-10-09の初回連続処理はmain `2d45b3d3e5d84223fd2642f3158c03fdcbfa0bd1`から開始し、結果更新をcommit `51a5d3451dfc0de5bfd68b9db73822d2fcebec99`に反映。その後のRetry-After継続結果はcommit `e39984779d01cbfbc1235d303c26f1f688455aa3`、追加の季節429履歴はcommit `778890ce5811cd5025a95115174858ea7f929f34`に反映。今回のHTTP 429再試行上限対応はその最新mainを基点とする。実行後の最新状態は[結果レポート](hermes-bulk-run-results.md)が正本。次回はこの文書とレポートを読み、`main`最新とNAS実体を再確認してから継続する。

## 目標・完了済みの扱い

`goura32/official-vrm-catalog`の実機未処理分を**一度のHermes依頼で可能な限り連続処理**する。最優先は作者公開の`data/collections/polygonalmind-halloween-rising.json` **60件**と`polygonalmind-xmas-chibis.json` **80件**（計140件）。同一実行で処理可能分を終えたら、他の公式・原作者が無償公開する直接VRMへ継続（ToxSam originals 10件、NeonGlitch86の許諾確認可能分、公式サンプル等）。認証が必要なBOOTH/Hub/Studio等は認証なしでの正規取得可否を確認し、必要なら対象だけ保留する。作者の無料公開でも利用権限が確認できない対象は取得・保存しない。

**不変の基準値**:
- 登録総数**1,297**。R3 100件とR1/R2 400件の計500件は既に処理済み。R1/R2/R3**以外の797件**の現在の棚卸しは、保存25、確定非人型4、権利保留65（条件矛盾32、許諾未確認33）、別hostリダイレクト拒否2、`dweb.link`恒久ブロック141、明示的認証待ち150、VRoid Studioエクスポート専用23、残り387件が未試行または取得条件未確定。797は「NASへ保存すべき797件」ではない。
- 現在のNASは**ZIP 355件、WebP 710枚**。開始時351件の既存索引行・保存物は不変。現在の未圧縮合計**1,434,953,725 bytes** → ZIP **750,627,115 bytes**、削減率**47.6898%**、WebP **9,116,306 bytes**。最終`verify_nas.py`は`ok:true`・`errors:[]`。次回は355件を不変baselineとし、既存データを保全する。
- 選別リストは**人型候補557、非人型243、未判定497**。今回の続行分は公式ページ候補11件を確認し、人型4件を描画・目視確認・NAS保存、権利保留6件、認証待ち1件とした。BOOTHは6件を代表プローブし、全件でログインへリダイレクトされた。ZIPは実VRM比較で採用済み、**圧縮比較を繰り返さず`--format zip`で統一**する。

**権利・取得上の保留（再配布許諾や正規URLの新証拠がない限り自動再取得しない）**:
- R3のプレビュー品質: `polygonalmind-100avatars-r3-229`（1件、実VRM人型確認済み、NAS未保存）。
- R1/R2の形状不明: `polygonalmind-100avatars-013-standard`、`-013-voxel`、`-034-standard`、`-034-voxel`（それぞれ完全な`polygonalmind-100avatars-...` ID、4件）。
- R1/R2の埋込権利・作者表示矛盾: `polygonalmind-100avatars-132-standard`、`polygonalmind-100avatars-196-standard`、`polygonalmind-100avatars-166-voxel`（3件）。
- MJMoonbow:既存`mjmoonbow-skinnie1-5-41eb4fe`に加え、今回取得した16件の埋込`Redistribution_Prohibited`（全IDは結果レポート、NAS未保存）。
- 今回追加の権利矛盾: `neonglitch86-shapey`（埋込`allowRedistribution=false`）、`numinia-starter-avatar-01`・`numinia-avatar-arla`（埋込`CC_BY`対公開CC0、NAS未保存）、`tegnike-nikechan-v1`・`tegnike-nikechan-v2`・`tegnike-nikechan-v2-outerwear`（埋込再配布禁止/`allowRedistribution=false`）、`aituber-onair-miko-normal`・`aituber-onair-miko-cheer`（埋込`Redistribution_Prohibited`）、Kizuna AI 2件、Sony RAYNOS 3件、ZONe ぞん子1件、hinzka PerfectSync 2件（READMEの再配布許諾と実VRM埋込`Redistribution_Prohibited`の矛盾）。NeonGlitch86の残り33件は公式README/LICENSE不在で許諾未確認のため、別カテゴリの権利確認待ちとした。
- URL制約: `neonglitch86-index-1`・`neonglitch86-index-3`は別hostへのリダイレクトを2回とも拒否。ミラー/ゲートウェイへ迂回しない。Halloween/Xmas 001、Halloween 002/003/004/005/006の過去再試行は旧方針下の履歴。Halloween 007は`2026-10-09T02:28:25.603909Z`の初回要求でHTTP 429（Retry-After: 900、当時の期限`02:43:25.603909Z`）となり、最新指示に従い再試行せず終端化。同じdweb.link hostは全IDについて恒久的にアクセス禁止。残る季節131 IDとToxSam `King Mutatio`は要求しない。
- 今回の確定非人型は`toxsam-original-bffd07cc-601`、公式仕様サンプル3件、MJMoonbow Dragon 9（作者の実レンダー画像で四足を確認）。これらは人型保存キューへ戻さない。

根拠とチェックポイントは`docs/hermes-bulk-run-results.md`にある。保留は次の一括処理の進捗を妨げない。根拠なしにライセンスを一括で`CC0`に置き換えない（R1/R2は作者README条件、R3は別条件）。

## 作業上の絶対条件

1. **カタログJSONが正本**（`data/models.json`、`data/collections/*.json`）。スクリプトに合わせた値やIDの改変禁止。検証済みメタデータ・選別IDと根拠の追記だけを実施し、モデル件数を増やすことを目的にしない。
2. **取得対象は作者/公式が正規に無料公開したものだけ**。NFT購入・保有必須、第三者権利不明、利用条件の矛盾、ログイン障壁・利用者本人による認証が必要なもの、アクセス制限の回避が必要なものは個別保留。認証情報やVRMのバイナリ/画像を外部AI API・GitHubに送信しない。利用条件が途中で変われば新しい根拠を記録する。
3. NAS永続化物は**人型VRMだけを1モデル1ZIP（内部`model.vrm`）**とし、正面Tポーズ`768×1024`・顔正面`512×512`のWebP2枚、`index.jsonl`、管理ロック以外の配布ZIP・VRM・不要ファイルを永続化しない。VRMや画像のSHA-256を索引に対応付け、展開後VRMハッシュが元ファイルと一致することを要求。
4. 見た目の人型は頭/胴/両腕/両脚（亜人や人型ロボットも可）を根拠に判断。Humanoidリグのみで判断しない。**形状が不明なら無料取得条件確認の上、一時ダウンロード後にモデル実体を描画**。明確な非人型は取得前除外してよい。人型でも正面画像の品質を満たさないものは個別保留。
5. 書込み前に**NAS実体・NFSマウントと空き容量**を`findmnt -T /mnt/hdd/vrm`等で確認。前回は`nas1.local:/volume1/hdd`へのNFSv3。マウント不在時に同名ディレクトリをローカル作成しない。**既存338件を絶対に上書き・削除しない**。始動時のNAS index各行とSHA-256を安全な場所に記録し、処理後に既存行が不変であることを検証。NFS遅延/タイムアウト時はファイル実体とindexを照合してから必要最小の復旧を行う。推測で再実行・削除しない。
6. 作業機の`~/.local/state/official-vrm-catalog/`に中断再開用チェックポイント（処理日時、ID、出典、取得結果、GLB/VRM版、形状、権利・画像品質、NAS保存、SHA-256、理由）を残す。ログ・ZIP一時ファイルはNASには残さない。途中に失敗があっても次の安全な対象へ進む。**現行のHTTP 429方針（旧記録に優先）**: 429を返したIDは再試行せず失敗として終端化する。429が発生したhostはRetry-After経過後も含め恒久的にアクセス対象外とし、同hostの別IDへの初回要求も行わない。checkpointから429 hostを復元してネットワーク要求前に抑止する。別gateway/mirrorへ迂回しない。
7. 未コミット変更があれば尊重し、作業に必要な差分だけ`commit/push`。**RDC・GitHub Actions不使用**。依存の大量アップグレード、テストの過剰追加、既に解消済みの圧縮実測・R1/R2形状レビューの再実施はしない。正常動作を阻害する不具合が出た時だけ最小修正と関連する対象テストを行う。

## 一括作業の順序

1. `git fetch`・最新main・`docs/nas-storage.md`・`docs/hermes-bulk-run-results.md`・NAS索引・保存済みモデル/画像・チェックポイントの整合を確認。`python3 scripts/verify_nas.py --nas-root /mnt/hdd/vrm`を実行し、**355件/710枚の開始時監査**を確認。NASマウント未確認なら書込み作業はしない。
2. 季節140 IDを正本から確認。H001–006等の過去再試行は旧方針下の履歴。H007は初回429で最新指示により再試行せず終端化し、dweb.linkを恒久ブロックする。残る131季節IDとKing Mutatioも同hostのため要求しない。Retry-After期限待ちは行わない。
3. 取得物ごとにGLB/VRM構造、実版、ライセンス/作者埋込情報、同一バイナリハッシュを検査。外形は作者プレビューまたは実VRM描画で人型/非人型/判定保留に分ける。人型はTポーズ・顔正面のWebPを生成し、実際に画像・画角を点検。NASに`scripts/archive_vrm.py --format zip --confirm-humanoid`で保存。元VRMと復元ZIPのSHA-256、プレビューID・画像SHAを照合。失敗IDを記録して進む。
- 4. `dweb.link`対象を除外した後、公式ページ候補11件を確認した。LAUGH DiAMOND 4件は保存済み、Kizuna AI 2件・Sony 3件・ZONe 1件は権利保留、ENRAIは会員登録必須で認証待ち。追加でhinzka公式GitHub 2件を実体検査したが埋込権利情報がREADMEと矛盾し権利保留。BOOTHは代表16件（既存6件＋追加10商品ページ）を検査し、¥0表示でもダウンロードURLがログインへ遷移したため認証回避せず18件を認証待ちとして記録。VRoid Hubは3代表ページでpixiv IDログインを確認し、3件を認証待ちとした。既確認のToxSam、Neon CC0、MJMoonbow、Numinia、VRM仕様サンプルは再取得しない。ToxSam `King Mutatio`を含む429 host対象は永久除外する。新たな正規公開元と権利根拠が見つかった場合のみ、その候補を処理する。既保存・非人型・権利保留は処理キューから除外。
5. 最後に全件`python3 scripts/verify_nas.py --nas-root /mnt/hdd/vrm`で`ok:true`・`errors:[]`を確認し、**開始時355件の索引行・保存ファイルハッシュが変わっていないこと**を確認。実績レポート・正本の根拠つき更新・選別リストを必要最小限の差分で整備。`git diff --check`・`scripts/validate.py`（必要なら既存4単体テスト）後にcommit/push。処理待ち・保留を再開可能な状態で残す。

## 最終報告

**直近実行分の新規実績**（公式ページ11件を確認、4件をNAS保存、6件を権利保留、1件を認証待ち。追加で公式GitHub 2件を権利保留、BOOTH 112プローブ・計133件を認証待ち、VRoid Hub 16件を認証待ち。NeonGlitch86のREADME/LICENSE不在を確認し、33件を許諾未確認として保留。権利保留は計65件、明示的認証待ちは150件。HTTP 429後の再試行なし、dweb.link恒久除外）と**現在累計355 ZIP/710 WebP**、NAS監査、既存351件の不変性、Git commit SHA、再開チェックポイントを日本語で簡潔にまとめる。

本書は実行指示であり、**記載した時点ではHermesを起動していない**。実行時は合理的な範囲で**逐次の小分け依頼なしに実処理を続行**し、必要不可欠な利用者認証・権利判断のみ個別保留として報告する。
