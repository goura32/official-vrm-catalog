# Hermes Agent 一括実機継続指示（BOOTH認証済みChromeプロファイル）

本指示は2026-10-11のHermes実機確認に基づく。新規取得作業の開始時は必ず`origin/main`をfetchし、最新main・NAS索引・ローカルcheckpointを先に確認する。バッチ30開始時のmainは`7df4d78c94e5aae61f455bec7ce5f95dd128a1d2`だった（履歴上のbaseであり、次回の最新SHAを意味しない）。これより新しい正当な差分を壊さない。

## 状況：認証障壁が部分的に解消

ユーザーがChromeに正規ログインし、Hermesは`browser.use_real_profile: true`、実プロファイルをコピーしたローカルブラウザーセッション`booth-real-profile-local-2`を起動できた。BOOTHトップページでログイン済みアカウントメニューを画面確認。カタログID `pixellangel-dolly-devil` のパイロットは2026-10-10に実取得・検査・Tポーズ/顔確認・NAS保存まで完了。パイロット後にBOOTH認証済み30バッチを実施した。パスワード・Cookie・トークン・認証付き一時ダウンロードURLは表示、記録、リポジトリ追加、チャット出力を禁止。Cookieを手動抽出・curl等へ転送して認証を代用しない。

**現在の実績（2026-10-11）**：
- カタログ計1,297件。R1/R2/R3以外の797件は、NAS保存134、実バイナリ非人型8、作者索引由来非人型1、埋込権利矛盾105、許諾未確認50、モデル対応未確定8、VRM-only取得範囲外3、別hostリダイレクト拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち297、VRoid Hub認証待ち16、公式ページ認証未確認1、商品ページ404が3、VRoid Studioエクスポート専用23、公式メタデータ確認のみ3、公式リポジトリ掲載のみ2。合計797。過去バッチの権利・ID保留は再取得せず。
- BOOTH認証済み実取得は、パイロット＋30バッチで商品ページ151件、無料取得catalog ID204件、物理VRM検査222件、NAS新規保存109件、非人型7件、権利矛盾75件、権利未確認17件、モデル対応未確定8件、VRM-only範囲外3件、HTTP 429は0件。バッチ30は15商品ページ（全てHTTP 200）、無料UI操作9回、10 ID取得、11物理VRM member発見、8件を実VRM検査し、Miraとフルリール1.3/1.4の3件をNAS保存。Sayo/Hatsuka 2版/Pharaohは権利矛盾、ゆるねこは若年外観と性的利用許可の懸念、白ねこみみとエルフ弓使いは許諾範囲不明で保留。鳩・マーモット・カマキリは無料パッケージに編集用sourceを含むため取得範囲外。もやしは複数VRMとsource同梱で対応不明。旧355件ハッシュは不変。
- NASは464 ZIP・928 WebP、未圧縮VRM 3,535,666,721 bytes、ZIP 1,943,831,503 bytes、WebP 14,378,760 bytes、削減率45.0222%。`verify_nas.py`は`ok:true, errors:[]`。未解消の権利矛盾・モデル対応未確定・権利未確認は保存しない。
- 最新のローカルチェックポイントは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261010-30.json`、累計は`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/authenticated-summary-20261010.json`。新規取得の前に匿名302確認を繰り返さず、権利保留案件を新しい許諾根拠なしに再取得しない。

## 継続実行手順（認証済みBOOTH残件）

### A. 前提の安全確認

1. Git最新main、ローカル未コミット変更、実NASマウント（`findmnt -T /mnt/hdd/vrm`）、現在のNAS `index.jsonl`、checkpointを照合。`python3 scripts/verify_nas.py --nas-root /mnt/hdd/vrm`を実行して現時点の保存済み件数を確定する。開始時の全index行とSHA-256をローカルに記録。マウント不明ならNASに書き込まず終了。355件がすでに正常保存済みなら一切上書きしない。
2. `booth-real-profile-local-2`の生存とBOOTHログイン状態を**画面で**再確認。ログインが消えていたらユーザー本人の正規ログインが必要と記録し、Cookieコピーや認証回避をしない。BOOTH・各ショップの規約、ページの無料配布条件を確認し、サイトが自動取得を認めない場合は処理を停止して報告する。

### B. 完了済みパイロット（再取得しない）

- 2026-10-10に`pixellangel-dolly-devil`（`https://booth.pm/ja/items/4795020`）の無料`dolly_devil.vrm`を正規UIから取得し、権利・VRM実体・人型・Tポーズ・顔を確認してNASへ保存済み。有料の`.vroid`は取得していない。保存済みIDの再ダウンロードや上書きは禁止。

### C. 次回の優先実作業：認証待ち297件を継続

1. 作業開始時に最新main、worktree、NASマウント、NAS監査、ローカルcheckpointを照合し、`authenticated-summary-20261010.json`とバッチ30 checkpointを再集計する。現在のBOOTH認証待ちは297 ID。既保存109、非人型、権利保留、モデル対応未確定、範囲外source package、404、アクセス制限、エクスポート専用を対象へ戻さず、正規の無料BOOTH VRM/VRM-only ZIPだけを商品ページ単位で処理する。`VRoid Hub`等、別サービスの認証をBOOTHログインで通せると仮定しない。
2. 最初は少数（例えば5～10商品）で連続動作・エラー・負荷を確認し、問題がなければ**恣意的な少件数で終了せず**、入手できる分を順次続ける。直列または低並列で配布元へ適切に間隔をあけ、過剰なアクセスをしない。HTTP 429を一度でも返したホストはその時点で**全IDを含め要求禁止**（別ホスト/ゲートウェイ/プロキシへの迂回もしない）。ブラウザーでのログイン・無料ダウンロードを優先し、匿名URLを再調査しない。
3. 1商品に複数VRM・色違い・0.x/1.0同梱がある場合は**既存のカタログIDごとに**内部ファイル名・SHA-256と対応させる。違うモデルや同一モデルを重複登録しない。無料版と有料支援版を区別する。モデル1件ごとに権利/形状/プレビュー/ZIP/索引を検証し、失敗したものだけ記録して残りを続ける。再配布禁止等のライセンスを破らない。
4. 作業機`~/.local/state/official-vrm-catalog/`に`downloaded`, `archived`, `non_humanoid`, `preview_hold`, `license_hold`, `auth_failed`, `free_not_available`, `rate_limited`等の排他的処理状態と再開用ジャーナルを残す。追加取得の進捗件数を適宜ログ出力し、tmux等で中断に耐える。Cookie/認証トークン/期限付きURLはチェックポイントにも出さない。ユーザー本人の追加操作が不可欠になった場合は、その部分だけ保留。
5. ログイン状態が失われた、BOOTHが利用条件を変更した、またはサイト全体で無料取得できない場合はバッチを止めて報告し、認証回避・購入・別ホスト迂回をしない。商品固有の権利/ID/内容問題は保留し、影響のない他の候補を続ける。

### D. 最終処理

NAS全件`verify_nas.py`で`ok:true, errors:[]`、開始時の355件の索引行・ファイル実体が不変であることを確認。全797 IDの排他的状態を再計算し、認証待ちの減少と新規保存数を明記する。モデル対応未確定は権利保留と別集計する。正本JSON、`data/download-scope.json`、`docs/hermes-bulk-run-results.md`、必要に応じて本指示書を更新。最低限の`scripts/validate.py`、既存テスト、`git diff --check`後に作業内容だけをcommit/push。GitHub Actions/RDCを使用せず、NAS上のVRM/ZIP/WebP、ログ、ユーザー認証情報をGitHubへpushしない。

**日本語の最終報告**：ログインとダウンロードの成功可否、パイロット結果、今回処理した商品/ID数、ダウンロード成功・失敗、人型/非人型/権利保留/画像保留、NAS新規・累計件数、ZIP容量と圧縮率、NAS監査、旧355件不変性、797 IDの内訳、commit SHA・再開チェックポイントと次回必要なユーザー操作。未実施は成功と書かない。

**この文書は実行用指示であり、記載しただけでモデルはダウンロードされていない。**
