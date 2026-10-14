# Hermes Agent 継続作業指示（個人用VRMカタログ）

**2026-10-15更新。** これは現行の実行指示。B01〜B85の詳しい実績は[実機検証履歴](hermes-bulk-run-results.md)に保存し、本書では繰り返さない。**目的は、正規に無料入手できる人型VRMを個人用NASへ集めること。細かな権利監査やNASの隔離調査を主作業にしない。** 過去の「NFSの管理者隔離が未証明なので新規保存停止」「独立した長期保管許諾が明記されないので保存停止」は現行の一律停止条件としては採用しない。利用規約・法令に反する取得を許す趣旨ではない。

## B84開始点（履歴）

- GitHub `main` の確認済み基準は `94a52773558d203dc81b62a458a35c04d00ea2b7`。作業時は最新`origin/main`をfetchし、ローカル未コミット変更とcheckpointを尊重する。
- NASは**487 ZIP・974 WebP**、ZIP合計**2,168,476,533 bytes**。索引SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`、read-only `verify_nas.py` は`ok:true, errors:[]`。既存全487件を保護。NAS上で実数が増えていれば実体を優先し再度照合する。
- カタログ**1,297 ID**。現行ラベルで権利矛盾129、未確認219、BOOTH等の認証待ちやNAS隔離保留など別ラベルあり。これらは**保存不可の断定ではなく以前の調査結果**。既存notes・出典を残し、根拠のない一括ラベル書き換えはしない。
- B84は`mjmoonbow-dragon-2-775e309`の文書・権利表示をレビューしただけで、ダウンロード・NAS保存なし。B35以前のチェックポイントを再実行しない。

## B85終了時の最新状態（2026-10-15）

- B85開始時のNASは487 ZIP・974 WebP（ZIP 2,168,476,533 bytes、index SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`）。終了時は686 ZIP・1,372 WebP、ZIP 4,070,462,418 bytes、index SHA-256 `59d737d104b21a584fa1f41d9fe20a301eb776a45571084955b51bdbe9b4a96f`。全件`verify_nas.py`は686 entries/1,372 previews、`ok:true`、`errors:[]`、全形式ZIP。
- B85で人型VRMを199件新規保存（+398 WebP）。開始時487行を現在のindexから時刻で再構成したSHA-256が開始checkpointと一致し、既存行の不変を確認。199件すべて`humanoid_confirmed_by_operator`。全ID・SHA・サイズ・供給元数は`/home/ws2/.local/state/official-vrm-catalog/work/holiday-batch/nas-batch-summary-487-to-686-20261015.json`。優先Aの`youkihi-recruit-suit`/`youkihi-long-black-hair`も保存済み。
- 現行scopeは642候補、未保存49件（VRoid Hub認証待ち16、公式export-only 23、rights conflict 6、権利未確認3、対応付け不明1）。未保存候補の`download_url`直接リンクは0件。ユーザー指定のBOOTH認証待ち16件とは異なり、現状の16件はVRoid Hub認証待ち。
- 作業開始時のmain/origin SHAは`d7f993a99b35ba2f9e2961bf97dfc297391fa36d`。次回は`origin/main`をfetchし、実測index・このresume文書・checkpointを再確認する。

## 最優先：取得・実物検査・NAS保存

1. B85で保存した`youkihi-recruit-suit`/`youkihi-long-black-hair`を含め、NAS indexにあるIDは再取得・上書きしない。新規候補は現行scope/checkpoint/indexを突合し、**既存の実VRM記録や手元の未保存artifactを再利用できるもの**から処理する。
2. B85後の認証待ち16件はBOOTHではなくVRoid Hub（直接download URL 0件）。BOOTH認証待ちの取得は本バッチで完了。別サービス認証へログインを転用せず、ユーザーが当該サービスの既存認証済みprofile利用を明示した場合だけ公式UIから取得する。公式export-only 23件は配布ファイルが見つからない限り推測・迂回しない。公式GitHub上のファイルも正規配布根拠があるものを対象にする。
3. **アバター利用不可、商用不可、改変不可、再配布不可、年齢設定の記載なし、私的長期保存の特別な許諾文がない、配布元と埋込VRM権利表示が食い違う**という理由だけで、正規取得したファイルの**個人用の非公開技術検査・複製**を自動的に不可としない。これらの情報はnotesに残すが、毎回独立した法的鑑定を要求しない。明示的な取得・複製禁止や実際の利用規約上の制限に当たる場合は遵守し、判断できなければそのIDだけ保留する。違法な入手、認証/年齢ゲートの回避、有料版の無断取得はしない。
4. 単一の無料ZIPに編集ソース等が同梱されても、**VRMだけを抽出**し、本人用NASには`model.vrm`1体を収めたZIPとTポーズ・顔WebPを保存する。VRM 0.x/1.0や色・版・商品ID・memberを混同しない。形状は実VRMで確認し、非人型はNASに保存しない。Tポーズや顔の撮影に失敗したモデルは推測画像で代用せず、理由を記録。
5. **今あるNASのディレクトリmode 0777やNFSv3 `sec=sys`だけで作業を停止しない。** この個人利用の環境の運用リスクはユーザーが承知しており、追加のサーバー隔離証明を収集の前提にしない。とはいえ、LAN上の他利用者から絶対に見えないとは断言しない。権限・ACL・export・既存保存物の変更は求められていないので行わない。NASが正しくマウントされ書込み可能で、保存スクリプトが通常どおり動くことだけ確認する。
6. 過去のHTTP 429ホスト（`dweb.link`を含む）の再要求や迂回をしない。正規サイトの利用制限を守り、カート/決済への操作は行わない。Cookie・パスワード・認証付きURLはログ/Gitに残さない。NASのVRM/ZIP/WebPもGitHubにpushしない。

## 完了処理（最小限）

- 保存は`scripts/archive_vrm.py --format zip --confirm-humanoid`、実体検査は`scripts/inspect_vrm.py`を利用。ZIP内外のSHA-256、カタログID、WebP2枚を確認。既存の同一IDを上書きせず、NASの最終`verify_nas.py`を一度実行する。開始時に実測した既存全件が維持されているか確認する。
- 正本JSON、download-scope、レポートは**実際に取得・検査・分類が変わった分だけ**更新。保留や権利の過去記録を勝手に「解決済み」にしない。不要な追加レビュー・定型監査の繰り返し・テスト追加をしない。既存の`validate.py`、既存テスト、`git diff --check`を必要範囲で実行しcommit/push。
- 直列または低並列でサイトへ負荷をかけず、途中結果はローカルcheckpointに保存。作業報告は**今回の新規取得件数、NAS純増、保存できなかった技術的理由、最新累計、監査結果、コミット**を中心に簡潔な日本語で出す。
- **RDC、GitHub Actionsは使用しない**。不必要な管理者権限変更を行わない。

本書の更新だけで実機取得・NAS保存が行われたわけではない。
