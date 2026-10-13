# 完成条件・未保存モデルの扱い（2026-10-14）

この文書は、**カタログの完成**と**NASへの人型VRM収集の完了**を分けて判定するための方針。正本は`data/models.json`、`data/collections/*.json`、`data/download-scope.json`。以下の現行値はB62（2026-10-14）時点であり、B35の混合ZIP再評価・14 ID照合、B36の権利/NAS再評価、B37〜B62の用途別レビューを反映する。履歴値は実績レポートを参照する。

## 完成の定義

- **登録・一次調査**：カタログ1,297 IDが一意で、出典・入手方法・利用条件URL・検証段階が記録され、現在の取得可能性を過大に表示しない。非人型もカタログには残す。登録拡充は原則凍結し、確かな誤登録・重大な欠落や実パッケージで判明した別VRMの補正のみ根拠を添えて検討する。
- **人型VRMのNAS保存**：無料で正規取得でき、利用条件が確認でき、実VRMの形状と全身/顔WebPを検査できたIDのみ、ZIP単体（内部`model.vrm`）で保存する。既存IDを上書きしない。保存済み全件の`verify_nas.py`が`ok:true, errors:[]`、索引・ファイルSHA-256が一致すること。
- **未保存の正確な管理**：権利未確定・人型でない・ページ不存在・取得制限・要会員認証・ID対応不明・VRoid Studio書き出し専用などは、根拠と再開条件があれば保留・除外でよい。**1,297件すべてをNAS保存することは完成条件にしない**。一方、無償取得可能な人型VRMを、推測上の「ZIP同梱ファイル」を理由に見落とさない。
- **作業の終了**：現行方針で実行可能な対象が無くなり、残件が理由別に記録されている状態を「現時点の収集フェーズ完了」と呼ぶ。技術的に未検査のものを「実VRM検証済み」に変更しない。保留の解除は**新しい作者根拠・利用条件・正規ログイン・モデル対応資料**がある場合だけ行う。

## B62時点の排他的内訳（2026-10-14）

| R1/R2/R3以外の797 ID | 件数 | 扱い |
| --- | ---: | --- |
| NAS保存 | 157 | 全体487 ZIP・974 WebP。NAS実機の次回確認が正本 |
| 非人型（実体8・作者索引1・商品ページ60） | 69 | 登録は保持、NASへは保存しない |
| 埋込権利矛盾 | 130 | 公開条件とVRM metadataの不一致を示す。商用/再配布/アバター利用の制限だけで私的保存禁止と推論せず、計画行為ごとに照合。関連条件が未解決なら保留 |
| 利用条件・許諾未確認 | 224 | 権利・取得・複製/保存条件の不足を個別確認。年齢設定未記載だけでは中立な非性的技術検査を止めない。独立した権利/形状/対応/実際の年齢ゲート等が未解決なら保留 |
| ライセンス複製許諾確認済み・NAS隔離未確認 | 2 | `youkihi-recruit-suit`、`youkihi-long-black-hair`: CC BY 4.0の複製許諾を確認。NASの実効的な第三者隔離を確認できないため保存保留 |
| カタログIDと物理VRMの対応不明 | 14 | ZIP内メンバー・作者による対応資料で再確認 |
| 「混合ZIP」のみを理由にした配布範囲外 | 0 | B35で41 IDを再評価。保存3、非人型9、当初hold29。現在も全件未アーカイブ。B51 `neoneko-leo`、B53 `sakurabido-hapicchi`、B54 `branshop-nao`、B55 `neoneko-ngii`、B56 `ratenosu-untitled`、B57 `neoneko-nolt`、B58 `neoneko-roa`、B59 `neoneko-romuru`、B60 `neoneko-shitakee`、B61 `neoneko-shoki-avatar-2`は公式無料URLの認証待ちへ再分類 |
| 別ホストへのリダイレクト拒否 | 2 | 正規取得根拠なしに迂回しない |
| `dweb.link`ブロック・未取得 | 141 | 未要求132と429終端9を含む。再アクセス禁止 |
| BOOTH認証待ち | 10 | B34の145件は状態遷移済み。B51 `neoneko-leo`、B53 `sakurabido-hapicchi`、B54 `branshop-nao`、B55 `neoneko-ngii`、B56 `ratenosu-untitled`、B57 `neoneko-nolt`、B58 `neoneko-roa`、B59 `neoneko-romuru`、B60 `neoneko-shitakee`、B61 `neoneko-shoki-avatar-2`の公式無料URLがsign-inへ302。未ログイン・未取得 |
| 別サービスで正規認証が必要 | 17 | VRoid Hub16、ENRAI/note 1 |
| 商品ページ404 | 3 | 公式の移転先など新根拠を待つ |
| VRoid Studioからのエクスポート専用 | 23 | 直接VRM配布とは区別。後日アプリ実機操作で確認 |
| 公式メタデータのみ・リポジトリ掲載のみ | 5 | 実ファイル未検証のまま記録 |
| **合計** | **797** | **区分は重複しない** |

B59 `neoneko-romuru`の再評価履歴はB59実機結果を参照。B60 `neoneko-shitakee`は無料ZIPのページ掲載と混合package内のVRM listingを確認したが、別の500円支援offerとは区別した。利用・改変可と販売/原本譲渡/転売禁止を行為別に記録し、これらを私的保存禁止と読み替えない。私的な中立検査・一時複製・長期保管は明示されず、許可/禁止を推定しない。数値年齢/age gateは見当たらず、年齢不記載だけでは中立検査を止めない。無料URLの無認証HEADは302 sign-inのため主状態をBOOTH認証待ちへ変更。私的保存権利、物理member対応、shapeは独立に未解決/未確認。根拠source IDs50/51、詳細はB60実機結果。

B61 `neoneko-shoki-avatar-2`は公式ページに無料ZIPとVRM memberを掲載し、別500円支援offerは分離した。作者表示の使用/改変可、改変物販売・原本譲渡・転売禁止を行為別に記録した。販売/移転制限だけでは私的保存禁止とならないが、非公開中立検査・一時複製・長期保管の明示もないため許可/禁止を推定しない。ページ掲載の無料URLは無認証HEADで302 sign-in。年齢数値/age gateは確認できず、年齢不記載だけでは中立検査を止めない。物理ZIP/member対応/shapeは未確認。主状態はBOOTH認証待ち、保存権利は独立に未解決。根拠source IDs52/54、詳細はB61実機結果。

B62 `neoneko-tofu-seijin`は公式ページを無認証GETで確認し、無料ZIPとVRM listingを確認。公式商品プレビューは塊状の胴と両脚を示し、腕/手・明確な頭胴区分がなく、作者説明も手/口なしとしているため、名前ではなく見える形状から非人型へ分類。年齢不記載だけを除外理由にしておらず、確認したプレビューに明確な性的/不適切表示はない。実VRM/ZIP/member対応は未確認で、ダウンロード・認証gate probeも行っていない。作者表示の使用/改変可と改変物販売・原本譲渡・転売禁止は別行為として記録し、これらを私的保存禁止とは扱わない。一方、非公開中立検査・一時複製・長期保管の明示はなく、許可/禁止を推定しない。主状態を`rights_unverified_hold`から`official_product_page_shape_non_humanoid_not_archived`へ更新し、NAS保存なし。根拠source IDs55-58、詳細はB62実機結果。

この797件の表は単一の主状態による排他的集計であり、未解決の権利軸すべてを網羅する重複なしの件数ではない。B53 `sakurabido-hapicchi`は認証待ちへ分類したが、個人的な非公開技術検査・一時複製・長期保管の許諾範囲は別途未解決のまま記録する。商用利用、アバター/Vtuber利用、再配布の制限だけから私的保存の禁止を推論しない。B54 `branshop-nao`はUVライセンスの個人商用/派生物配布/成人向け表現の条項を各軸で記録し、派生物配布許可を元VRMの再配布許可へ拡張しない。非公開技術検査・長期保管は明示されず、禁止・許可いずれも推定しない。無料URLがsign-inへ302するため取得認証待ちへ分類し、権利軸を独立に未解決とする。成人向け表現条項はモデル年齢の根拠ではなく、数値年齢不記載だけで中立検査を禁止しない。B55 `neoneko-ngii`は使用/改変使用を許可し、改変物販売・原本譲渡・転売を禁止する。販売/移転の禁止を私的保存禁止とは解釈せず、非公開技術検査/長期保管の明示もないため許可を推定しない。年齢・形状を説明や外観ラベルから推測せず、年齢不記載だけで中立検査を禁止しない。


形状の予備選別は人型候補603、非人型候補231、未判定463。NAS内で検証した件数とは別の集計。B35で人型候補へ加えたのは実VRMの全身表示を確認した3 ID。B43 `jima-muscle-mantis`、B44 `jima-muscle-pigeon`、B45 `kumayui-kumano-yucha`は人型候補へ加えた。B46 `youkihi-recruit-suit`、B47 `youkihi-long-black-hair`は既存候補の物理VRM/全身形状を確認したがscope件数は不変。B48 `lillian-nanaka`はB35 holdの1件。正規無料ZIPの標準`ななか.vrm`を商品名/metadata titleで既存IDへ対応させ、別memberの血のりなし版だけで中立Tポーズ/顔を確認して人型候補へ追加した。二つ目のmemberは別IDを推測で作成せず、NASにも保存しない。年齢を推定せず、表示範囲に数値年齢/年齢ゲートなし。非公開技術検査用の複製/保管条件が明記されないため権利holdを維持する。JIMA/Kumanoの複製・保管条件は未解決でrights hold、Youkihi 2件はCC BY 4.0複製許諾を確認した一方NASプライバシーhold。B53 `sakurabido-hapicchi`は商品ページ画像が両脚を示さないためshape未確定のまま未判定に維持し、年齢不記載だけを技術検査禁止理由としない。B54 `branshop-nao`は物理VRMを未取得・未検査のためshape未判定を維持し、年齢不記載だけを中立検査の禁止理由としない。B55 `neoneko-ngii`も未取得のためshape unclassifiedを維持し、キノコ説明/寸法から形状や年齢を推測せず、年齢不記載だけを中立検査の禁止理由としない。B62 `neoneko-tofu-seijin`は公式商品プレビューで腕/手と明確な頭胴区分が見えないため、実VRM未取得のまま非人型予備分類へ追加。年齢不記載のみを理由にせず、物理member/実体検証は未完了。R1/R2/R3の500件も含めた総登録は1,297件。

## B36の再評価（2026-10-11）

- B36スナップショットの130件`official_binary_inspected_rights_conflict_not_archived`は権利矛盾の未解決件数であり、保存禁止の件数ではない。保存済みnotesのキーワード監査では`OnlyAuthor` 61、`Redistribution_Prohibited` 81、商用Disallow 49、`allowRedistribution=false` 7件が見つかった（重複あり。note文字列の分類であり、個々の契約の法的結論ではない）。行為別に再評価するが、矛盾を一括解除しない。
- B36スナップショットの237件`rights_unverified_hold`も「保存禁止」の断定ではなく、取得権限・複製/保管条件・対応・形状等の証拠不足を含む。新しい根拠なしに一括保存へ変更しない。
- B35の保留29件は年齢設定未記載だけを理由に技術検査を拒否しない基準で再評価。27件は数値年齢なし/非数値表記、1件は年齢を明示的にunknown、1件は作者がchild avatarと記載。全件を非公開の中立検査と年齢敏感な利用に分ける。B36では`pike-aurora`をローカル検査し形状/顔表示を確認したが、NAS隔離が未確認のため未保存。`pike-steam-rabbit`はTポーズ/顔プレビュー条件未達で未保存。残る27件は物理member対応・利用条件・全身形状の独立根拠が未解決。29件全体のverification件数は変更しない。
- 最新の読み取り専用NAS監査により、mode 0600の個別ファイルだけではNFSv3 `sec=sys`とmode 0777親ディレクトリ上の第三者アクセスを排除できないことが判明。NAS管理者による実効隔離の確認まで、新規の非再配布VRMをNASへ追加しない。詳細は[NAS保存方式](nas-storage.md)と[B36実績](hermes-bulk-run-results.md)を参照。

## B38の個別再評価（2026-10-11）

- Kizuna AI KAMATTE AIのVRM 1.x/0.xは、2026-10-09公式ページcheckpoint（`official-page-checkpoint-20261009.jsonl`）に実ダウンロード・VRM member・埋込metadataの記録がある。従来noteの「実ダウンロード未確認」は誤りとして訂正。今回は公式ページ・[二次創作ガイドライン](https://kizunaai.com/guideline/)・[キャラクター利用規約](https://kizunaai.com/terms/)を読み直しただけで、利用規約への再同意、再取得、NAS保存は行っていない。
- VRM 0.xの`Redistribution_Prohibited`は公式3Dモデル規則の再配布禁止と整合するため、単独では権利矛盾でも私的保存禁止でもない。非公開技術検査の複製が「二次創作活動外の複製」に関する条項と、同規約が留保する法令上許容された利用のどちらに該当するかは未解決。この1 IDを`official_binary_inspected_rights_conflict_not_archived`から`rights_unverified_hold`へ移し、保管可とは判断しない。
- VRM 1.xの`allowRedistribution=false`は再配布禁止と整合する。`avatarPermission=onlyAuthor`は、ガイドラインが条件付きで認める改変モデルのSNS/VRChat利用とのアバター利用軸の差としてrights-conflictを維持するが、私的技術保存の禁止とは扱わない。同じく非公開技術検査用コピーの保存条件は未解決であり、NAS未保存。
- この個別変更だけで現行集計は権利矛盾129・利用条件等未確認238（合計797 ID内）となる。129件の矛盾と238件の未確認を一括解除せず、モデルごとに取得、複製/保存、技術検査、アバター利用、商用、公開/再配布を別軸で確認する。

## B39 Sony RAYNOSの個別再評価（2026-10-11）

- `sony-mocopi-raynos-original`、`sony-mocopi-raynos-mini`、`sony-mocopi-raynos-sports`の3件は、2026-10-09の公式ページcheckpointに各v1.0.8 ZIP内VRM member、VRM 0.x、SHA、metadataを記録済み。B39では公式配布案内と[キャラクター使用許諾契約書](https://www.sony.co.jp/en/Products/mocopi-dev/jp/downloads/eula/EulaCharacter.html)を再確認しただけで、同意操作、再取得、NAS保存は行っていない。
- EULA第2条は許諾用途（モーションデータとアバターの組合せ、生成コンテンツ編集、二次著作物等）を定め、その用途に必要な複製・改変を認める。第3条は第三者使用・再許諾等と事前承諾のない営利使用を制限し、第9条は契約終了時の使用中止・対象データ等の削除を合理的に可能な限り2週間以内に求める。モデルファイル再配布制限と派生コンテンツの配布許可は別行為として記録する。
- `Redistribution_Prohibited`はモデルファイルの第三者移転制限と整合する方向で、それだけを保存禁止とは扱わない。`allowedUserName=OnlyAuthor`はEULAが利用者に認める限定的アバター利用との権利差として、3件とも既存`official_binary_inspected_rights_conflict_not_archived`を維持する。私的な中立構造検査・そのための保存はEULAの列挙用途に明記されないため、許諾済みとも一律禁止とも推定せず保留する。
- 3件の再分類は行わず、集計は権利矛盾129・利用条件等未確認238のまま。NAS、download scope、B35 hold29、mapping不明14も変更なし。

## B40 pike-moon-nightの個別再評価（2026-10-11）

- 公式BOOTHページは0円の配布物で、ダウンロードを利用規約への同意として扱う。ページはMoon Night blue/redとVRM・PSD・textureを列挙する。利用規約は商品を使うモデル等の無料/商用利用、成果配布、改変を認める一方、元データそのままの再配布を禁じ、改変データ再配布は相談、credit表記と利用者側のbackupを求める。
- 公開ページでは数値年齢や実年齢ゲートを確認できなかった。年齢未記載だけを理由に中立・非性的な構造検査/Tポーズを止めない。ただしblue/redの独立VRM数・内部memberとcatalog IDの対応、実ファイルの全身形状/Tポーズは未確認。バックアップ案内も技術検査用途の明示許諾とは同一視しない。
- ダウンロード自体が規約同意を伴うため、今回クリック・同意・取得をしていない。権利範囲とmember/形状確認が未完了のため`rights_unverified_hold`を維持し、保存済みへ変更しない。NAS隔離未確認も独立した保存停止理由。
- 1件のhold理由を年齢未記載から実際のmember/形状・取得同意・保存条件へ精緻化しただけで、797件内の集計は権利矛盾129・利用条件等未確認238のまま。B35 hold29全件も未解決のまま保持する。

## B41 branshop-naoの個別再評価（2026-10-11）

- 開始時の`main`/`origin/main`は`8e40aa58ffcafd60fa0b8d3d549fe57536bf7a92`。読み取り専用NAS verifierは487 ZIP/974 WebP、`ok:true`/`errors:[]`、index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。mode/ACL/NFSの状態は[NAS監査](nas-storage.md)記載どおりで、変更なし。
- [公式BOOTH商品ページ](https://booth.pm/ja/items/6595645)はUnitypackage/FBX/Texture等とVRM形式モデルを掲示し、[UVライセンス個別条項](https://uv-license.com/ja/license?utf8=%E2%9C%93&pcu=true&ddw=true&seu=true&veu=true)はPCU（個人商用利用）、DDW（二次著作物の配布）、SEU/VEU（成人向け性的/暴力表現）を許可する。UVライセンス本文はモデル/派生物の配布を個別許可なしでは禁止する一方、DDWが許可するのは派生物の配布であり、元VRMの再配布許可とは扱わない。
- 今回確認した条項に、個人的な非公開技術検査や、その目的での複製/保管を明記した許諾または禁止は見つからず、可否を推定しない。商用・派生物配布・成人表現の各条件を保存禁止へ読み替えない。BOOTHページに数値年齢/実年齢ゲートは見当たらず、年齢未記載だけで中立・非性的検査/Tポーズを止めない。成人向け表現の許可もキャラクターが成人である証拠にはしない。
- 混合パッケージは単独の範囲外理由ではない。一方、ZIP内の正確なVRM member/ID対応、実VRMの全身形状/Tポーズ、検査用複製・保管の根拠は未確認。取得・同意操作・NAS保存なし。`rights_unverified_hold`を維持し、797 ID内の集計（権利矛盾129、利用条件等未確認238）は変更しない。

## B42 jowashop-ordinary-girlの再評価（2026-10-11）

- 公式BOOTHの0円`一般子供.zip`を正規UIで取得し、ZIP内のVRM 1件と`.vroid` 1件を確認。VRMは0.x、title=`一般子供`、author=`じょわ`で、単一のVRM memberと本catalog IDの対応が取れた。
- 作者は約115cm・小学生/幼稚園児タグを掲示し、使用/改変と友人への無償調整・引渡しを許可、自作発言/販売を禁止。子どもとして提示されたモデルであり成人とは扱わないが、数値年齢/年齢ゲートは見当たらない。中立・非性的なTポーズ/顔を確認し、性的/暴力的表現は行わない。
- 埋込`allowedUserName=OnlyAuthor`と`licenseName=Redistribution_Prohibited`は、作者の友人向け無償調整・引渡し許可とアバター利用/第三者移転軸で矛盾する。`commercialUssageName=Disallow`は販売禁止と整合する。これらの軸差だけを私的保存禁止へ読み替えず、個人的な技術検査/長期保管の明示条件も未確認として保留する。
- 1件を`rights_unverified_hold`から`official_binary_inspected_rights_conflict_not_archived`へ移動。NAS保存なし。797 ID内の現行集計は権利矛盾130、利用条件等未確認237。B35 hold29全件は未保存であり、全体として未完了。

## B43 jima-muscle-mantisの再評価（2026-10-11）

- 公式BOOTHの無料ZIPと同梱READMEを確認し、1 VRM/FBX/Blender/texture類の混合パッケージを正規UIから一時取得。唯一のVRM memberは`MuscleMantis.vrm`、本IDと一対一で対応し、VRM 1.0である。
- 商品条件は個人商用・改変・配信/SNS利用を許し、モデルデータの再配布（改変版含む）と性的/暴力表現を禁じる。VRM metadataも`personalProfit`、`allowModification`、`allowRedistribution=false`、`allowExcessivelySexualUsage=false`、`allowExcessivelyViolentUsage=false`で主要な利用軸は整合する。README/metadataはcredit必須だが商品ページは任意と記載する。クレジットを付ければ両条件を満たせるため、権利矛盾には数えず、利用時は必須表記に従う。再配布禁止を保存禁止とは解釈しない。
- 数値年齢/年齢ゲートは見当たらず、年齢未記載のみで中立・非性的構造検査を止めない。ローカルTポーズ/顔を目視確認し、人型の全身表示と正面頭部を確認。JIMAを形状分類の人型候補へ加え、scopeは600/230/467。権利許諾やNAS保存の承認とは別軸である。性的/暴力的用途は行っていない。
- [VRM Public License 1.0](https://vrm.dev/licenses/1.0/)はModel/Avatar Useに必要な複製をRedistributionと区別するが、構造検査/長期保管が許諾されたUseに含まれるかは明記されない。私的検査用コピーの条件は可否を推定せず保留し、`rights_unverified_hold`を維持。NAS保存なし。B35 hold29は全件未保存、集計は権利矛盾130・利用条件等未確認237のまま。

## B44 jima-muscle-pigeonの再評価（2026-10-11）

- [公式BOOTH item 8737858](https://booth.pm/ja/items/8737858)の¥0 ZIPと同梱READMEを確認。FBX/GLB/texture/scriptを含むZIPから唯一の実VRM memberを本IDへ一対一対応させた（`__MACOSX/._`はAppleDouble sidecarでモデルではない）。VRM 0.x/GLB2。
- 商品ページ/READMEは使用者制限なし・商用利用・改変可・credit任意を示し、元/改変VRMの再配布・転売・無償配布/部品配布、性的・過度な暴力表現等を禁止。埋込`allowedUserName=Everyone`、`commercialUssageName=Allow`、`licenseName=Redistribution_Prohibited`、sexual/violent Disallowと整合する。再配布制限だけから私的保存禁止とは推論しない。
- ページ/READMEに数値年齢や年齢ゲートは見当たらず、年齢未記載のみで中立・非性的検査を止めない。Tポーズ全身と正面顔を確認し、形状分類として`download-scope`に追加。shape countは601/230/466。形状分類は許諾や保存承認とは別軸。
- 私的な技術検査/長期保管の明示条件は見つからず、許可/禁止を推測せず`rights_unverified_hold`を維持。NAS保存なし。権利矛盾130・利用条件等未確認237は不変。B35 hold29は全件未アーカイブ、別枠の物理VRM対応不明14にもJIMA Pigeonは含まれない。

## B45 kumayui-kumano-yuchaの再評価（2026-10-12）

- [公式BOOTH item 7039529](https://booth.pm/ja/items/7039529)は無料ZIPを提示し、年齢は「？？？」と記載。年齢ゲートはなく、年齢不明だけを中立・非性的検査の停止理由にしない。ページ規約は個人/金銭目的の商用利用と改変を許可し、改変物を含む再配布を禁止、credit任意。埋込metadataの`allowedUserName=Everyone`、`commercialUssageName=Allow`、`licenseName=Redistribution_Prohibited`と整合する。`sexualUssageName=Allow`/`violentUssageName=Allow`だが、本件では性的・暴力的表現を生成/利用していない。
- ZIPの唯一の実VRM member `熊野ゆちゃ/熊野ゆちゃ.vrm`は本IDへ一対一対応。VRM 0.x/GLB2の中立Tポーズで頭・胴・両腕・両脚、正面顔を確認し、形状分類として`download-scope`の人型候補へ追加。ページ記載のPNG 2点に対し実ZIPはPNG 1点だったが、VRM対応には影響しない。
- 私的な技術検査/長期保管の条件は明示されず、許可/禁止のどちらにも推測せず`rights_unverified_hold`を維持。NAS保存なし。権利矛盾130・利用条件等未確認237、B35 hold29、対応不明14は不変。

## B46 youkihi-recruit-suitの複製許諾・形状確認（2026-10-12）

- [公式BOOTH item 3823494](https://booth.pm/ja/items/3823494)は無料のVRM+sample-image ZIPを配布し、年齢や年齢ゲート、作者独自の使用制限はページ本文に見当たらない。年齢を推定せず、中立・非性的な検査を実施した。
- 実VRM metadataは`licenseName=CC_BY`、`commercialUssageName=Allow`、`allowedUserName=Everyone`。公式[VRM metadata license mapping](https://vrm.dev/en/vrm/meta/license/)は`CC_BY`を[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)へ結び付ける。CC BY 4.0は複製・共有・改変を許し、共有時の帰属表示等を条件とする。従って本カタログでは、作者がライセンスできる範囲で、個人的な非公開技術検査用コピーは明示的な複製許諾の範囲内と分類する。これは規制文言の不在からの推論ではなく、埋込CC_BYの肯定的ライセンス表示に基づく運用判断であり、法的助言ではない。第三者権利などライセンサーが保有しない権利は別途対象外。
- 一意のmember `FreshWomanSet/FreshWoman.vrm`を本IDへ対応させ、VRM 0.xの中立Tポーズ/顔で頭・胴・両腕・両脚と正面頭部を確認。形状候補は既に登録済みのためscope件数は不変。
- `rights_unverified_hold`から`official_binary_inspected_humanoid_render_confirmed_nas_privacy_hold`へ再分類。コピーに関するライセンス保留ではなく、NFSv3 `sec=sys`・world-writable親ディレクトリ等からNASの第三者隔離を確認できないため、NAS保存は行わない。集計は権利矛盾130、利用条件等未確認236、NAS隔離保留1。B35由来の29 IDは全件未アーカイブ。

## B47 youkihi-long-black-hairの複製許諾・形状確認（2026-10-13）

- [公式BOOTH item 3841471](https://booth.pm/ja/items/3841471)の認証済みUIで¥0 `NegativeSet.zip`（表示14.7 MB）の無料ダウンロードを確認。ページ本文はVRM本体とサンプル画像を同梱したZIP、VroidStudioのみで制作した暫定版のため無料と説明する。表示ページ/ZIP内に作者固有利用条件は見当たらず、数値年齢・年齢ゲートもない。タイトル/本文の「少女」から年齢を推定しない。
- 取得ZIPは15,389,698 bytes、SHA-256 `5d6ed73d1d2554a1c071643150c94faf24d8acceaa69bd08b57b4f440e233c09`。`testzip`成功、7 entries（directory 1、sample PNG 5、VRM 1）、expanded 21,761,412 bytes、unsafe path/symlinkなし。唯一の`NegativeSet/NegativeGirL.vrm`を物理memberとして本IDへ対応。
- VRM 0.x/GLB2、18,633,964 bytes、SHA-256 `708df3de1f415fc1516dfd8bbdf7e82e1be974e41d6487938a3d035257536ee0`。metadataは`allowedUserName=Everyone`、commercial/sexual/violent usage=`Allow`、`licenseName=CC_BY`。公式[VRM metadata license mapping](https://vrm.dev/en/vrm/meta/license/)はCC BY 4.0へリンクする。肯定的なCC BY 4.0表示を根拠に、作者が許諾できる権利について個人的技術検査用コピーを複製許諾の範囲内と分類する。取得、保存、技術検査、avatar use、商用、改変、第三者共有は別の行為であり、作者が保有しない第三者権利や他の適用条件は別途残る。
- 年齢を推定せず、中立Tポーズ/顔をローカル生成・目視確認。Tポーズは頭・胴・両腕・両脚が見え、着衣状態で性的/暴力的表現なし。顔は正面だが長い髪が大部分を隠す。preview hashes/dimensionsはB47実機結果に記録。既存人型候補のためscope件数602/230/465は不変。
- `rights_unverified_hold`から`official_binary_inspected_humanoid_render_confirmed_nas_privacy_hold`へ分類を分離。複製許諾は確認したが、NAS隔離は未確認なので保存しない。権利矛盾130・利用条件等未確認235・NAS隔離hold2。B35 hold29は全件未アーカイブ（本IDはその一つ）。

## 優先する実作業

### 1. 混合ZIPの41 ID（35商品）— B35再評価済み

B35開始時checkpointの38 ID `official_product_page_scope_excluded_not_archived`、3 ID `official_package_inspected_scope_excluded_not_archived`は履歴値であり、現在の`verification`件数ではない。無料ZIPに`.vroid`、Blender、FBX、PSD、Unitypackage等が**同梱されている事実だけ**を「NAS保存不可」の理由にしない。

**実際の既定ルール**は「取得したZIPから許諾・モデル対応が確認できる人型`.vrm`だけを抽出し、単体ZIPへ可逆圧縮してNAS保存。元ZIPや編集ソースは永続保存しない」。配布ZIP全体の一時取得が正規利用・利用規約に沿うなら、混合ファイルでも候補になる。ただし、明白な非人型、実際の年齢制限/ゲートや不適切な内容、利用条件の懸念、権利矛盾、ID対応不明、取得禁止は**独立した理由として保留**し、単に混合ZIPだから許諾済みとはしない。年齢設定未記載だけで中立・非性的検査を禁止しない。

B35では35商品を商品単位で重複取得せず再評価した。正規無料の混合ZIPから、商品ページ・規約・実ファイル名・埋込メタデータ・形状が一致した3 ID（ずんだもん歩行/飛行、JIMA中年太りマーモット）だけをVRM単体抽出し、プレビュー付きZIPで保存した。9 IDは既存商品レンダーで非人型と確認し、29 IDは年齢/権利/物理形状/メンバー対応のいずれかが不足するため保留した。41 IDすべてが保存可能または人型とは主張しない。詳細は[実機検証レポート](hermes-bulk-run-results.md)のB35節と正本notesを参照。

過去の分類・検証履歴は消さず、新たに実取得/形状/権利/保存を確認できたIDだけ`verification`と`notes`を変更する。**41 IDすべてが保存可能、あるいは人型だとは主張しない**。メタデータで「パッケージ実体検査済み」となっていても`notes`に「未取得」とある場合は、実機checkpointで矛盾の有無を確かめる。

### 2. 物理VRMの対応不明14 ID — B35既存記録照合済み

既存記録から5 ID分の物理VRM検査、2 ID分のパッケージ内VRM一覧、7 ID分の商品ページ根拠を照合したが、一対一対応が確認できたIDは0。14 IDはすべてモデル対応不明を維持し、新しいダウンロードや推測による割当てを行わない。詳細はB35実績に記録する。

### 3. 利用者操作が必要な対象と停止案件

VRoid Hub16件とENRAI/note1件はBOOTHのログインとは別。正規認証が必要なら個別に利用者操作を依頼し、資格情報は記録しない。VRoid Studio専用23件は無料公式アプリからのエクスポート作業を別タスクとして扱う。埋込権利矛盾130・利用条件等未確認229は**新しい根拠なしに同じ実体を再取得しない**。NAS隔離hold2は既に正規取得/検査したが、新たなNAS保存は禁止中。`dweb.link`の141件（うち要求済み429が9）はホストブロックを保持し、Retry-After経過後も再アクセス・別ゲートウェイによる迂回をしない。

## 一括作業の共通終了判定

1. 最新mainとローカルcheckpoint/NAS索引を照合し、対象ID集合を二重起動・二重登録しない。B34のBOOTH145件は処理完了であり、ENRAI1件とは混同しない。B34チェックポイントの`partial`は独立保留が残る状態を示すので、**無理に完了へ書き換えない**。B35は独立した混合ZIP再評価と14 ID照合であり、未解決保留はそのまま維持する。
2. NASの実マウントを確認し、変更前後に`verify_nas.py`を実行。B35開始時の484件の索引行と、旧355件保護ハッシュ`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`を保護。件数が後続処理で増えれば現在のNAS実体を優先する。
3. 既存`validate.py`、必要に応じた既存テスト、`git diff --check`で検証。無用なレビュー反復やテストの増殖を避け、GitHubへは正本データ・集計・手順だけcommit/pushする。NAS VRM、WebP、一時ZIP、認証情報をpushしない。
4. 最新の797件排他的区分、総NAS件数、何件が「新たに実VRMを検査できたか」を報告。**残件が0ではなくても、停止根拠が明瞭なら収集フェーズを閉じられる**。B35後の残る14 ID対応不明・29 IDの独立holdを、mixed-ZIPのみの理由へ戻さない。

この文書は作業方針・基準であり、作成だけでは再取得やNAS保存は行っていない。

## B49の追加レビュー

`shounokoto-kotatsu-mikan`は同梱VN3規約により個人利用および許諾範囲内の複製が認められる。未改変再配布禁止だけを保存禁止とは扱わないが、規約外の利用には事前の明示許諾が必要で、非公開構造検査/長期保管の明示がないため`rights_unverified_hold`を維持する。キャラクター年齢の未記載はhold理由でなく、VRMを抽出・描画していないためshape分類も不変。規約上の未成年ユーザー同意条件は利用者側の別軸で、今回確認できていない。詳細はB49実績を参照。

## B50の追加レビュー

`mxu-suu-vrm`の商品ページは商用利用・改変とVRChat内のクローン/公開アップロードを許可し、再配布/販売を禁じ、公開VRoidHub掲載を再配布と扱う。再配布禁止だけを私的保存禁止とは扱わないが、非公開技術検査/長期保管は明示されず、ダウンロード自体が規約同意とされるため追加取得せず`rights_unverified_hold`を維持する。作者への確認を避けるよう示唆する曖昧な一文も、私的検査/保存の許可または禁止を具体化しない。身長約90cmと「女の子」表記から年齢を推定しない。年齢不記載だけで中立検査を止める判断ではない。物理VRM未検査のため形状分類は不変。詳細はB50実績を参照。

## B51の追加レビュー

`neoneko-leo`の商品ページは無料の`レオ.zip`（23.1 MB）に`レオ_v1.09.vrm`と`レオ_素体.vroid`を列挙し、仕様をVRM 0.0と表示する。これはページ上の記載であり、物理ZIP/member/metadata/shapeは未検証。作者表示は使用・改造使用OK、改変物販売・原本譲渡・転売NG。これらの販売/移転制限だけを保存禁止とは扱わない一方、非公開技術検査/長期保管の明示条件はなく、保存許可も推定しない。商品説明は「明るい活発な少年」だが数値年齢/年齢ゲートの記載はなく、年齢を推定しない。年齢不記載だけでは中立構造検査/Tポーズを禁止しない。公式無料URLの認証なし・リダイレクト追従なしGETは302 LocationでBOOTH sign-inを示した。ログインも追加取得も行わず、アクセス軸を`official_free_download_auth_required_not_verified`へ分類し、保存条件は別軸で未解決のままにする。B35の旧age-reviewはこの候補について誤っていたため訂正し、混合ZIPも単独の除外理由にしない。権利矛盾130は不変、利用条件等未確認は234、BOOTH認証待ちは1。citation ledger source ID35/36とB51実績を参照。

## B56の追加レビュー

`ratenosu-untitled`の商品ページは無料の`無題 .zip`（33.1 MB）と別の`無題_おまけ .zip`（5.24 MB）を掲載し、主packageにVRM/Unitypackage/Blend/PSDを記載する。2 offerの内容は同一と推定しない。作者条件は無改造モデル/textureの再配布・販売・自作発言を禁止し、VRChatのpublic pedestal利用は許可を要するとする。これらの販売/再配布制限だけを私的保存禁止とは扱わないが、非公開の中立技術検査・一時複製・長期保管の明示許諾も確認できず、保存許可を推定しない。数値年齢/age gateはページに記載がなく、商品名のお兄さん表現から成年を推定しない。年齢不記載だけで中立構造検査/T-poseを止めない。無料主package URLの無認証・redirect追従なしHEADは302 sign-in。ログイン/GET/取得/VRM検査なし。`official_free_download_auth_required_not_verified`へ分類し、私的保存条件は独立に未解決、shapeはunclassifiedのまま。権利矛盾130は不変、利用条件等未確認230、BOOTH認証待ち5。citation source IDs37/38、B56 checkpointを参照。

## B57の追加レビュー

`neoneko-nolt`の商品ページは無料`Nolt_ノルト_.zip`（22.9 MB）と別の「店長のおこづかい」500円offerを表示し、無料ZIPにはVRM 0.0の`ノルト（Nolt）_1.3.vrm`と編集可能な`.vroid`を列記する。これはページ情報であり、物理ZIP/member/metadata/shapeは未確認。作者表示は使用・改変使用OK、改変物販売・原本譲渡・転売NG。販売/移転制限だけを私的保存禁止とは扱わない一方、非公開技術検査・一時複製・長期保管の明示許諾もなく、許可/禁止を推定しない。数値年齢/age gateは確認できず、名前/外見から年齢を推測しない。年齢不記載だけでは中立構造検査/T-poseを禁止せず、混合ZIPだけも除外理由にしない。公式無料URLの認証なし・redirect追従なしHEADは302 sign-in。ログイン/GET/取得/VRM検査なし。`official_free_download_auth_required_not_verified`へ分類し、私的保存条件・shape・物理member-to-ID対応は独立に未解決。source IDs44/45、B57 checkpointを参照。
