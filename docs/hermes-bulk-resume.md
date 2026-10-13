# Hermes Agent 一括実機継続指示（BOOTH認証済みChromeプロファイル）

本指示は2026-10-14のB62確認に基づく。新規取得作業の開始時は必ず`origin/main`をfetchし、最新main・NAS索引・ローカルcheckpointを先に確認する。B33〜B62の履歴とB51/B53/B54/B55/B56/B57/B58/B59/B60/B61/B62詳細は`docs/hermes-bulk-run-results.md`を参照する。

B62ではB35 hold `neoneko-tofu-seijin`（BOOTH item5101910、per-model review 25/41）を再評価。公式ページを無認証GETで確認し、無料ZIP 431 KBとVRM 0.0/member listingを記録。公式商品プレビューの塊状の胴・両脚には腕/手や明確な頭胴区分が見えず、作者説明も手/口なしのため、名前ではなく見える形状から`official_product_page_shape_non_humanoid_not_archived`へ分類。ページ年齢/age gateの記載なしだけでは除外理由にせず、確認した画像に明確な性的/不適切表示はないが、実VRM内容は未確認。作者表示の使用/改変可と改変物販売/原本譲渡/転売禁止を私的保存と別軸で記録し、非公開技術検査・一時複製・長期保管は許可/禁止いずれも推定しない。物理member-ID対応は未確認。ダウンロード/認証gate probeなし。source IDs55-58、checkpoint `work/holiday-batch/booth-mixed-zip-reassessment-20261014-b62.json`。
B62 NAS read-only auditは487 ZIP/974 WebP、ZIP 2,168,476,533 bytes、index 487 rows/548,641 bytes・SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。`/mnt/hdd` 0777 root:root、`/mnt/hdd/vrm` 0777 ws2:uucp、models/previews 0777 ws2:ws2、index 0600、lock 0 bytes/mode000。確認pathにnamed/default ACLなし。NFSv3 `rw,sec=sys,local_lock=none`、HDD exportを含む3 exportsはprivate IPv4 /24限定、wildcardなし。サーバー側ACL/UID-GID mapping/squash/user isolation/effective lock未確認のため第三者隔離は未証明。既存資産維持、新規保存停止。NAS書込み・chmod/chown/ACL/NFS変更なし。

B49ではB35 hold `shounokoto-kotatsu-mikan`（BOOTH item6686224）の公式無料ZIPを一時取得して同梱VN3規約を確認。個人/法人の営利・非営利利用と許諾範囲内の複製は認められるが、規約外利用には事前の明示許諾が必要。未改変再配布禁止は保存禁止とは同義でないものの、私的な中立構造検査/長期保管の明示許諾は確認できず`rights_unverified_hold`を維持。ページにモデル年齢/ゲートはなく、年齢不記載を理由に保留していない。規約上ダウンロードは同意とみなされ、未成年者は事前の法定代理人同意が必要だが、利用者側条件は未確認。VRM memberは抽出・metadata検査・描画せず、ZIP/PDFをscratchから削除。B35 hold29は全件未アーカイブ。形状603/230/464、権利矛盾130・利用条件等未確認235・NAS隔離hold2、物理対応不明14は不変。
B50ではB35 hold `mxu-suu-vrm`（BOOTH item3933882）の公式ページを確認。通常VRM ZIPとVRC/Valentine別offerがあり、通常offerは`.vroid`とセットアップ済みVRMを同梱する混合package。商用/改変可・再配布/販売不可・VRChat clone/public upload可は別々の利用軸であり、公開VRoidHub uploadは再配布扱い。再配布禁止だけを保存禁止とは扱わない。一方、ページはダウンロードを同意とみなし、非公開技術検査/長期保管を明示しないため取得せず`rights_unverified_hold`。身長約90cm/女の子表記から年齢を推定せず、年齢不記載のみを中立検査の禁止理由にしない。物理VRM/shape未検査。B35 hold29は全件未アーカイブ。形状603/230/464、権利矛盾130・利用条件等未確認235・NAS隔離hold2、物理対応不明14は不変。

B51ではB35 hold `neoneko-leo`（BOOTH item6505161）を再評価。無料offerは`レオ.zip`（23.1 MB）で、ページは`レオ_v1.09.vrm`と`レオ_素体.vroid`、仕様VRM 0.0を掲載。ページの利用表示は使用/改造使用OK、改変物販売/原本譲渡/転売NG。販売・譲渡制限だけを保存禁止とは扱わないが、非公開検査/長期保管は明示されず、許可も推定しない。商品説明は「少年」で数値年齢は記載なし。年齢を推測せず、年齢不記載だけで中立構造検査/Tポーズを止めない。公式無料URLの認証なし・redirect追従なしGETは302 Location `https://booth.pm/users/sign_in`。ログイン/ダウンロードは行わず、`official_free_download_auth_required_not_verified`へ再分類。物理member-ID対応、metadata、shape/Tポーズは未確認。B35旧age-reviewの年齢理由と混合ZIP除外を訂正。B35 hold29は全件未アーカイブ。形状603/230/464、権利矛盾130、利用条件等未確認234、BOOTH認証待ち1、他サービス認証17、NAS隔離hold2、物理対応不明14は計797。根拠source ID35/36、B51 checkpointは`work/holiday-batch/booth-mixed-zip-reassessment-20261013-b51.json`。

B53ではB35 hold `sakurabido-hapicchi`（BOOTH item4979735）を現行公式ページで再確認。0円ZIP「さくらリクオ_フリーアバター_はぴっち.zip」17.2 MBにVroidファイル・VRM・readmeを記載。作者表示はアバター/個人/個人商用/法人利用と改変OK、Vtuber利用/再配布NG、暴力・性的表現OK、creditは可能な範囲。これらの利用・再配布条件を私的保存禁止とは扱わないが、非公開技術検査/一時複製/長期保管は明示されず、許可/禁止どちらも推定しない。数値年齢/年齢ゲートは確認できず、年齢不記載だけを中立検査の禁止理由にしない。商品サムネイルは頭・胴・両腕までで両脚がなく、全身形状未確認。公式無料download URLへ認証なしHEADを1回行い、302 sign-inを確認。ログイン/GET/ダウンロード/VRM検査なし。主状態を`rights_unverified_hold`から`official_free_download_auth_required_not_verified`へ更新し、私的保存の権利軸は独立に未解決と記録。shape候補603/非人型230/未判定464は不変。B35 hold29は全件未アーカイブ。797件の排他的主状態は権利矛盾130、利用条件等未確認233、BOOTH認証待ち2、他サービス認証17、NAS隔離hold2、物理対応不明14で797。source ID39/40、checkpointは`work/holiday-batch/booth-mixed-zip-reassessment-20261014-b53.json`。

B53 NAS read-only auditは487 ZIP/974 WebP、ZIP bytes 2,168,476,533、`verify_nas.py` `ok:true`/`errors:[]`。index 548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previews 0777、index0600、`.index.lock` 0 bytes/mode000、named/default ACLなし。`findmnt`はNFSv3 `rw,sec=sys,local_lock=none`。`showmount -e`は3 exportsをprivate IPv4 /24に限定しwildcardなしと表示したが、server ACL/UID-GID mapping/squash/利用者単位の隔離/実効lockは未確認。NAS既存資産を保護し、新規保存停止継続。chmod/chown/ACL/NFS変更なし。

B51 NAS read-only auditは487 ZIP/974 WebP、`verify_nas.py` `ok:true`/`errors:[]`、ZIP bytes 2,168,476,533。index 548,641 bytes/SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previews 0777、index 0600、`.index.lock` 0 bytes/mode 000、named/default ACLなし。`findmnt`は`nas1.local:/volume1/hdd`のNFSv3 `rw,sec=sys,local_lock=none`を確認。`showmount -e`は3 exportsをprivate IPv4 /24に限りwildcardなしと表示したが、これは第三者/ユーザー隔離を証明しない。NAS server ACL、UID/GID mapping、squash、個別client allowlist、実効lock制御は未確認。NASの既存資産/権限は変更せず、新規保存停止を継続する。年齢設定未記載だけを中立・非性的検査の禁止理由にしない。

B54ではB35 hold `branshop-nao`（BOOTH item6595645）を公式公開ページ・リンク先UVライセンスで再確認。無料`Nao_Contents.zip`（9.16 MB）にVRM形式モデルを掲示するが、実ZIP/VRMは未取得。利用条件は個人商用・二次著作物配布・成人向け表現などの軸別許可であり、再配布制限を私的保存禁止とは扱わず、DDWから未改変VRM配布許可も推定しない。非公開の中立技術検査・長期保管は明示されず、許可/禁止いずれも推定しない。数値年齢/年齢ゲートは確認できず、年齢不記載や成人向け表現条項だけで年齢を推定しない。公式download URLの無認証・追従なしHEADはHTTP/2 302 sign-in。認証/cookie/redirect follow/GET/取得/VRM検査なし。catalog verificationを`official_free_download_auth_required_not_verified`へ更新し、私的保存権利と形状scopeは別途未解決・未判定を維持。citation source IDs21/22/41、checkpoint `work/holiday-batch/booth-mixed-zip-reassessment-20261014-b54.json`。

B55ではB35 hold `neoneko-ngii`（BOOTH item6254853）を再評価。無料828 KB ZIPのページ掲載情報・利用表示を記録したが、公式download URLの匿名HEADは302 sign-in。取得/ログイン/VRM解析なし。販売/譲渡制限を保存禁止とは扱わず、私的な中立検査・一時複製・長期保管は明示されないため許可も推定しない。数値年齢/age gateなしと確認し、キノコ説明・寸法から年齢/shapeを推測しない。主状態は`official_free_download_auth_required_not_verified`、shape unclassified、私的保存の権利軸は独立に未解決。source IDs42/43、checkpoint `work/holiday-batch/booth-mixed-zip-reassessment-20261014-b55.json`。

B56ではB35 hold `ratenosu-untitled`（BOOTH item1571536）の過去B52調査をカタログへ反映した。公式ページは無料`無題 .zip`（33.1 MB）と別の`無題_おまけ .zip`（5.24 MB）を表示し、主packageにVRM/Unitypackage/Blend/PSDを記載する。作者の販売・未改造再配布制限だけを私的保存禁止とは扱わないが、個人的な非公開技術検査/一時複製/長期保管の明示許諾もなく、許可を推定しない。年齢/age gateはページに見当たらず、商品名から成年を推測しない。無料主package URLへの無認証・redirect追従なしHEADは302 sign-in。GET/ログイン/取得/VRM検査なし。catalog statusは`official_free_download_auth_required_not_verified`、私的保存権利は独立して未解決、shape unclassified。checkpoint `work/holiday-batch/booth-mixed-zip-reassessment-20261014-b56.json`、source IDs37/38。

B57ではB35 hold `neoneko-nolt`（BOOTH item7933453）を再評価。無料`Nolt_ノルト_.zip`（22.9 MB）と別の「店長のおこづかい」500円offerを公式ページで確認。使用/改変使用OK、改変物販売/原本譲渡/転売NGだが、これらを私的保存禁止へ読み替えず、非公開検査/一時複製/長期保管の許可も推定しない。年齢不記載だけで中立検査を止めず、年齢を推測しない。download URLの匿名・cookieなし・redirect追従なしHEADは302 sign-in。未ログイン・未取得・shape/member対応未確認。主状態をBOOTH認証待ちへ変更し、私的保存権利は独立に未解決。source IDs44/45、checkpoint `work/holiday-batch/booth-mixed-zip-reassessment-20261014-b57.json`。
B58ではB35 hold `neoneko-roa`（BOOTH item5108925）を再評価。無料`ロア.zip`（18.9 MB）にVRM 0.0と`.vroid`を掲載し、別の500円offerも表示。物理ZIP/VRMは未取得。使用/改変使用OK、改変物販売/原本譲渡/転売NGだが、これらを私的保存禁止へ読み替えず、非公開検査/一時複製/長期保管の許可も推定しない。数値年齢/age gateは確認できず、年齢不記載だけで中立検査を止めない。無料download URLの匿名・cookieなし・redirect追従なしHEADは302 sign-in。未ログイン・未取得・shape/member対応未確認。主状態をBOOTH認証待ちへ変更し、私的保存権利は独立に未解決。source IDs46/47、checkpoint `work/holiday-batch/booth-mixed-zip-reassessment-20261014-b58.json`。

B59ではB35 hold `neoneko-romuru`（BOOTH item7933498）を再評価。無料`ロムル.zip`（22.8 MB）ページはVRM 0.0と編集用`.vroid`を掲載し、別の500円支援offerは分けて扱う。使用/改造使用OK、改変物販売/原本譲渡/転売NGを別軸で記録し、これらを私的保存禁止とは解釈しない。個人的な非公開中立技術検査/一時複製/長期保管は明示されず、許可/禁止を推定しない。数値年齢・年齢制限/age gateは確認できず、年齢不記載だけで中立構造検査/Tポーズを止めない。無料URLの認証/cookieなし・redirect追従なしHEADは302 sign-in。ログイン/GET/取得/VRM解析なし。物理member-ID対応とshapeは未確認。主状態は`official_free_download_auth_required_not_verified`、私的保存権利は独立して未解決。B35 hold29全件未アーカイブ。source IDs48/49、checkpoint `work/holiday-batch/booth-mixed-zip-reassessment-20261014-b59.json`。

B59の読み取り専用NAS verifier/index再確認は487 ZIP/974 WebP、2,168,476,533 bytes、index 487行/548,641 bytes・SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`、candidate absent、`verify_nas.py` `ok:true`/`errors:[]`。権限/ACL/NFSの詳細値は同日B58読み取り監査から変更なしの前提で再使用し、B59では再プローブしていない。B58監査ではroot/models/previews 0777、index 0600、lock mode 000、named/default ACLなし、NFSv3 `rw,sec=sys,local_lock=none`、3 exportsはprivate IPv4 /24表示。実効server-side隔離・UID/GID mapping/squash/利用者別隔離/lockは未確認。新規NAS保存停止、chmod/chown/ACL/NFS設定変更なし。現行797件は権利矛盾130、利用条件等未確認227、BOOTH認証待ち8、他サービス認証17、物理対応不明14。B35 hold29は全件未アーカイブ。次の候補へ進む前に最新main・NAS・checkpointを再確認し、認証ゲートを迂回しない。

## 状況：認証障壁が部分的に解消

ユーザーがChromeに正規ログインし、Hermesは`browser.use_real_profile: true`、実プロファイルをコピーしたローカルブラウザーセッション`booth-real-profile-local-2`を起動できた。BOOTHトップページでログイン済みアカウントメニューを画面確認。カタログID `pixellangel-dolly-devil` のパイロットは2026-10-10に実取得・検査・Tポーズ/顔確認・NAS保存まで完了。パイロット後にBOOTH認証済み32バッチを実施した。パスワード・Cookie・トークン・認証付き一時ダウンロードURLは表示、記録、リポジトリ追加、チャット出力を禁止。Cookieを手動抽出・curl等へ転送して認証を代用しない。

**履歴スナップショット（2026-10-11、B40時点）**：
- カタログ計1,297件。R1/R2/R3以外の797件は、NAS保存157、非人型68（実体8・作者索引1・商品ページ59）、埋込権利矛盾129、年齢/利用条件等の未確認238、モデル対応未確定14、混合ZIPのみを理由とした範囲外0、別host拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち0、別途未検証1（ENRAI燕・note.com会員登録ゲート）、VRoid Hub認証待ち16、商品ページ404 3、VRoid Studioエクスポート専用23、公式メタデータ/リポジトリのみ5。合計797。
- B35は41 ID/35商品を再評価し、3 IDを2商品の正規無料混合ZIPからVRMのみ抽出して保存、9 IDを既存レンダー根拠で非人型、29 IDを独立根拠不足で保留とした。B36ではそのうち`pike-aurora`の中立Tポーズ/顔をローカル確認したがNAS隔離未確認のため未保存、`pike-steam-rabbit`はプレビュー条件未達で未保存。年齢未記載だけは停止理由としない。14 IDは既存検査記録と照合したが一対一マッピングは0件で、14すべて対応不明のまま維持。
- NASは487 ZIP・974 WebP、未圧縮VRM 3,925,815,073 bytes、ZIP 2,168,476,533 bytes、WebP 15,210,140 bytes、削減率44.7637%。`verify_nas.py`は`ok:true, errors:[]`。B35開始時484行の索引SHA群は全行一致し、旧355件の保護対象SHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`で不変。
- B33 checkpointは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261011-33.json`。B34 checkpointは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-authenticated-batch-20261011-34.json`（`batch34_checkpointed_partial`）。B35 checkpointは`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/booth-mixed-zip-batch-20261011-35.json`。権利/年齢保留・保存済みIDは新しい根拠なしに再取得しない。
- B36ではNASファイル・索引を書き換えていない。B38〜B40の権利再評価もカタログメタデータ・文書だけで、NASファイル・索引・権限に変更なし。`collection-policy.md`の「年齢未記載だけで中立技術検査を止めない」方針と[NAS読み取り専用監査](nas-storage.md)を優先する。487件の既存保存は保持し、第三者アクセスを排除できると確認されるまで新規保存しない。

## B35結果：混合ZIP再評価と対応不明ID照合

現在の方針では、無料の正規ZIPに`.vroid`、Blender、FBX、PSD、Unitypackage等が混在していても、混合形式だけでは除外しない。B35では同一商品URLの重複取得を避け、41 ID/35商品を一件ずつ再評価した。正規無料UIで取得したのは2 ZIP（67,186,856 bytes）だけで、3 IDを物理VRM・埋込メタデータ・年齢/規約・全身形状・プレビューまで確認してNASへ保存した。残る29 IDは独立した年齢/権利/モデル対応/物理形状の不足があり保留。9 IDは非人型として保存しない。混合ZIPそのものは、いずれのhold理由にも用いない。

1. 41 IDの混合ZIP再評価はB35で完了。`official_product_page_scope_excluded_not_archived`/`official_package_inspected_scope_excluded_not_archived`の対象は0 ID。29 IDは新しい権利・年齢・対応・形状根拠が得られるまで保留し、9非人型IDは取得しない。
2. 対応不明14 IDは既存checkpoint/manifest照合を完了したが全件保留のまま。5 IDには物理VRM記録があり、2 IDにはパッケージ内の複数VRM一覧、7 IDには商品ページ根拠があるものの、いずれも一対一対応を証明しない。別の作者根拠・一意なmember対応資料なしに再取得・再割当てしない。
3. 新しい正式な根拠が届いた場合だけ、最新版main・NAS監査・B35 checkpointから再開する。混合ZIPでは正規の無料UIから一時取得し、許諾済み・年齢適合・物理member対応済みの人型VRMだけ抽出する。zip bomb上限とパス逸脱検査を継続し、元ZIP/source/VRoid/textureをNASへ保存しない。
4. HTTP 429を返したホストへ再要求せず、`dweb.link`141 IDを別ゲートウェイで迂回しない。BOOTH認証待ちは0。ENRAI/note1、VRoid Hub16、VRoid Studio export23は別作業として保留。権利矛盾129・許諾未確認238は新しい根拠なしに再取得しない。
5. 実作業の区切りでNAS全件`verify_nas.py`、B35開始484件の行ハッシュと旧355件の不変性、`validate.py`、既存テスト、`git diff --check`を確認する。GitHub Actions/RDCを使わない。

以下のB34/B35記述は履歴であり、B36のNAS privacy gateを上書きしない。現時点の未解決作業は、NAS管理者による実効隔離の確認、個別権利/対応/形状hold、および上記の認証/エクスポート案件。新しい根拠がないまま過去のページ確認・ZIP取得を再実行しない。

## 継続実行手順（認証済みBOOTH結果）

### A. 前提の安全確認

1. Git最新main、ローカル未コミット変更、実NASマウント（`findmnt -T /mnt/hdd/vrm`）、現在のNAS `index.jsonl`、checkpointを照合。`python3 scripts/verify_nas.py --nas-root /mnt/hdd/vrm`を実行して現時点の保存済み件数を確定する。開始時の全index行とSHA-256をローカルに記録。**B36監査ではmode 0777の親ディレクトリ、NFSv3 `sec=sys`、サーバー側隔離未確認のため、NAS管理者が第三者アクセスを実効的に排除できると確認するまで新規NAS保存を行わない。** `chmod`/`chown`やNAS/NFS設定変更は禁止。355件/484件は過去baseline、現在保護する実体は487 ZIP/974 WebP。
2. `booth-real-profile-local-2`の生存とBOOTHログイン状態を**画面で**再確認。ログインが消えていたらユーザー本人の正規ログインが必要と記録し、Cookieコピーや認証回避をしない。BOOTH・各ショップの規約、ページの無料配布条件を確認し、サイトが自動取得を認めない場合は処理を停止して報告する。

### B. 完了済みパイロット（再取得しない）

- 2026-10-10に`pixellangel-dolly-devil`（`https://booth.pm/ja/items/4795020`）の無料`dolly_devil.vrm`を正規UIから取得し、権利・VRM実体・人型・Tポーズ・顔を確認してNASへ保存済み。有料の`.vroid`は取得していない。保存済みIDの再ダウンロードや上書きは禁止。

### C. B34実行履歴（再実行禁止）

- B34は105商品ページ（候補navigation 113回）、無料UI操作4回、物理VRM9件検査、転送36,591,848 bytes、NAS新規保存1件、145状態遷移を記録した。B34開始145 IDすべてに状態遷移があり、BOOTH認証待ちは0、別途未検証のENRAI燕1 IDは未完了のまま維持。B34時点の詳細は`docs/hermes-bulk-run-results.md`に残す。
- B34作業中に候補外item IDを誤って一度開き404となったが、ページ件数に含めず再試行・代替URL確認をしていない。この履歴は監査用であり、再アクセスしない。
- B34の権利/年齢保留・対応不明・範囲外・非人型は、B35で明示的に再評価したID以外を再取得対象へ戻さない。BOOTHや別サービスの認証を推測・迂回しない。

### D. 最終処理

NAS全件`verify_nas.py`で`ok:true, errors:[]`、B35開始時484行と旧355件の索引行・ファイル実体が不変であることを確認。全797 IDの排他的状態を再計算し、認証待ち・新規保存数・hold理由を明記する。モデル対応未確定は権利/年齢保留と別集計する。正本JSON、`data/download-scope.json`、`docs/hermes-bulk-run-results.md`、必要に応じて本指示書を更新。最低限の`scripts/validate.py`、既存テスト、`git diff --check`後に作業内容だけをcommit/push。GitHub Actions/RDCを使用せず、NAS上のVRM/ZIP/WebP、ログ、ユーザー認証情報をGitHubへpushしない。

**日本語の最終報告**：ログインとダウンロードの成功可否、パイロット結果、今回処理した商品/ID数、ダウンロード成功・失敗、人型/非人型/権利保留/画像保留、NAS新規・累計件数、ZIP容量と圧縮率、NAS監査、旧355件不変性、797 IDの内訳、commit SHA・再開チェックポイントと次回必要なユーザー操作。未実施は成功と書かない。

**この文書は実行用指示であり、記載しただけでモデルはダウンロードされていない。**
