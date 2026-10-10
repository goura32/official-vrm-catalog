# 収録・検証方針

## 採録条件

1. 配布者・著作権者またはその公式プロジェクトの配布案内を確認できる。
2. **購入・有料サブスクリプション・有料プランを必要とせず**、公式の案内した正規の方法でモデルを入手できる。
3. VRM形式で提供されるか、無料の公式ツールからVRM形式で書き出せる。
4. 公式ページまたは公式配布元、利用条件への参照URLを記録できる。

ログイン、無料会員登録、利用規約への同意、年齢確認、無料アプリの導入は**除外理由にしない**。年齢制限・地域制限やサービスの手続きは順守し、回避方法を案内しない。

無料・有料が混在するサイトでは**モデル個別の無料入手経路**を確認する。支払いが必須なら対象外。寄付が任意なら可。配布元の不明な転載・ミラーは対象外。

## 記録の原則

- 1つの取得物・仕様版を1レコードにする。同一キャラクターでもVRM 0.x/1.0やLOW/HIGHなど配布物が異なれば分ける。データは `data/models.json` および `data/collections/*.json` を正とし、スクリプトは補助。大量の公式コレクションは配布元単位でJSONを分け、IDはファイル間で一意とする。
- `source_url`: 配布根拠。個別モデルページがなければモデル群の公式説明ページ。
- `download_url`: **制作者の公開情報でVRMファイルの直接取得先と確認できたURLのみ**を記録。通常は `.vrm` 拡張子だが、ArweaveのコンテンツIDなど拡張子がないものも含む。ログイン画面や公式アプリの操作で取得するものは `null`。実ダウンロードしていなければ `verification` に明記する。
- `distribution_size_bytes`: 公式GitHub Contents API等で**実ファイルのバイト数**を確認できた場合だけ付与。BOOTH表示のMBを逆算しない。
- `distribution_filename`: 公式ページやGitHubのファイル一覧に記載された**配布物のファイル名**。ZIP形式の場合はVRM実ファイルの名前と混同しない。未確認なら省略する。
- `access_method`: 直接VRM取得・Hub経由・無料エディタ書き出し・公式ページ・BOOTH無料配布を区別。
- `vrm_version`: 未検証なら `null`。旧形式は `0.x` と記録。
- `license_url`: 公開された利用条件へのリンク。権利の許諾可否を推測して記載しない。
- `notes`: 調査で確認した重要な制限や未確認事項。商用利用などはライセンス名称だけで判断しない。
- `verification`: どこまで確認したかを過大に記載しない。
- `binary_evidence`: VRMバイナリのGLBヘッダーとJSONチャンクを解析できた場合のみ記録。Git blob IDとファイル自体のSHA1を混同しない。

## 未検証事項

- 未検証レコードでは、認証必須配布先の実ログイン・実ダウンロードを含む実体確認が未完了。BOOTHの実取得・検査実績は[実機検証レポート](hermes-bulk-run-results.md)に記録し、各レコードの`verification`で確認範囲を示す。VRoid StudioでのA〜Z個別書き出しは未実施。
- 実体未取得または未検証のレコードでは、ファイル内メタデータ、VRMバージョン、正常描画、各機能の挙動は未確認である。個別の確認範囲は`verification`と`notes`に記録する。
- リンク切れやライセンス変更が起きた場合は、公開時点の根拠を再調査する。

## 主な公式根拠

- [VRM公式仕様サンプル](https://github.com/vrm-c/vrm-specification/blob/master/samples/README.md)
- [VRoid StudioのAvatarSample A〜Z（無料・利用条件・HubのA〜C）](https://vroid.pixiv.help/hc/ja/articles/4402394424089-AvatarSample-A-Z)
- [VRoid Studioのサンプルモデル利用方法](https://vroid.pixiv.help/hc/ja/articles/31627266179865)
- [VRoid Studio公式サイト](https://vroid.com/studio)

## 今回追加した公式配布元

- [キズナアイ KAMATTE AI (VRM 1.x / 0.x)](https://kizunaai.com/download/kamatteaimodel/)
- [モノ御楠ルナ（LOW / HIGH、BOOTHの各0円配布）](https://booth.pm/ja/items/2091095)
- [ぞん子 3D MODEL type-N](https://zonko.zone-energy.jp/3dmodel) — [公式ライセンス](https://zone-energy.jp/3dmodel/terms.pdf)

## 追加収録における確認範囲（2026-10-08）

作者本人のBOOTHで無料のVRMファイル・VRM収録ZIPが**ダウンロード商品0円**として掲載されているものも収録する。ログインが必要でも対象。

- 直接 `.vrm` ファイル名が記載されている場合でも、認証が必要なBOOTHのダウンロード完了やファイル内メタデータは未確認。
- `.zip` の場合は販売者の内容物記述を根拠とし、実際のアーカイブ内構成は未検証として記録。
- 無料版と有料版のライセンス・収録機能を混同しない。購入不要な無料配布版を収録。
- 商用利用制限などの重要な条件は `notes` に明記し、正確な全文は `license_url` で確認する。
- モデルのバージョンは商品ページの明記がない場合は `null` を維持。`VRM 0.0` は `0.x` に集約する。**Hubに表示されるVRM形式と、StudioのVRMエクスポート設定で得られる形式は区別**する。

## 取得可能性の不確実性（2026-10-08）

BOOTHの `booth.pm/ja/items/...` 共通ページは0円配布として表示されても、`<ショップ>.booth.pm/items/...` の個別URLで非公開と表示される例がある。現時点では実ログイン・実ダウンロードを行っていないため、この矛盾から**取得成功・取得不能のどちらも断定しない**。該当する既登録モデルには `notes` で明記する。今後、実ダウンロードできないと確認できたものは収録対象から外して `docs/research-notes.md` へ移す。

## 有料版との共存

同一商品ページ内で0円のVRMと有料の.vroid、フルパッケージ、色違いが併売される場合、無料版の**実際の配布ファイルだけ**を収録する。0円モデルの利用権と有料版で付与される権利を混同しない。配布者が無料の規約PDFを別ファイルで公開している場合、本文未確認なら `notes` に残す。

## VRoid Project旧ベータ版モデルのライセンス（2026-10-08）

[公式ヘルプ](https://vroid.pixiv.help/hc/ja/articles/4402614652569)によると、AvatarSample A〜Zには独自条件がある一方、旧ベータ版の `β Ver AvatarSample_1〜4` はCC0。旧ベータ版4件は[公式VRoid Hub](https://hub.vroid.com/)で使用許可およびVRM 0.0表示を確認し、別レコードで登録。Hubの利用規約への同意は必要で、実ログイン・ダウンロードは未実施。

## VRoid Hubのダウンロード可否判定

[VRoid公式ヘルプ](https://vroid.pixiv.help/hc/ja/articles/360013153714)では「モデル登録者以外の利用OK」はダウンロード可、「OK（ダウンロードはNG）」はSDK等の連携先利用のみ、と区別する。**実VRMファイルを取得できること**を目標とする本カタログでは後者は原則収録しない。Hubの「OK」表示は未ログインで確認できる掲載許可の根拠であり、実際のダウンロード成功と同一視しない。

旧ベータ版サンプルのVRoid公式アカウントが公開する別衣装・別カラーも、Hub掲載のモデル利用条件とVRM版を個別確認した場合は別レコードとする。**オリジナル版のCC0表記を別衣装に無条件で転用せず**、そのHubページの利用条件にリンクする。

## VRM実ファイルのメタデータ監査（2026-10-08）

公式VRMサンプル5件のうち、次の3件はGitHubからバイナリを取得し、GLB v2ヘッダー・JSONチャンク・VRMC_vrm.specVersion=1.0・VRMライセンス設定を確認した。元のGitHub Contents APIで得たファイルサイズとも一致。

- VRMC_vrm_expressions_isBinary_Overrides.vrm（21,184バイト）
- VRMC_vrm_expressions_isBinary_Overridden.vrm（20,156バイト）
- VRMC_materials_mtoon_UV_Animation_Test.vrm（61,732バイト）

残るSeed-san.vrm（10,917,800バイト）とVRM1_Constraint_Twist_Sample.vrm（10,776,032バイト）はGitHub API上で存在・サイズを確認したものの、読み取りAPIからバイナリ本文が返らず未解析。全ファイルの完全ハッシュ照合や描画・挙動テストは未実施。

## ローカル実ファイル検証

`python3 scripts/inspect_vrm.py <ファイル.vrm> [<配布ZIP> ...]` を使用して、GLBヘッダー、VRM拡張、メタデータ、実ファイル全体のSHA-256を確認する（ネットワーク・追加依存ライブラリ不要）。

- **VRM 1.0**: `VRMC_vrm.specVersion` と `VRMC_vrm.meta` を取得。
- **VRM 0.x**: `VRM.meta` を取得し、旧仕様であることを記録。
- **ZIP**: ZIP内の各 `.vrm` を別々に調べる。ZIPそのものをVRMバイナリと見なさない。
- 出力の `sha256` は実VRMファイル本体のSHA-256。既存の `github_blob_sha` はGitオブジェクトのIDであり同一ではない。
- **ファイルを入手できない**場合は `verification` を昇格させない。VRM本体や配布ZIPをリポジトリへコミットしない。
- メタデータ上の利用条件は配布元の規約と合わせて確認する。規約の解釈やレンダリング成功をスクリプトだけで証明しない。

## 形状未判定モデルの実機確認ルール（2026-10-08追補）

- **事前の画像判定は必須条件ではない**。公式・作者の配布根拠、無料取得条件、利用条件を確認したうえで、人型か不明なVRM/ZIPは検査目的で一時ダウンロードしてよい。既に非人型と判明したモデルは取得不要。
- 一時取得は作業機の一時領域（例：`/tmp/vrm-inspection`）とし、`/mnt/hdd/vrm` の確定保管物と区別する。VRMメタデータだけでなく必要に応じて3D表示を確認し、外見上の人型・非人型・判定保留を記録する。Humanoidリグの有無のみでは決めない。
- 人型と判定でき、無料入手・配布条件と実ファイルの整合が確認できたものだけ、**VRM本体を改変せず個別に可逆圧縮**してNASへ保存する。元VRMのSHA-256、配布元、規約URL、取得日時、カタログIDとの対応は索引に記録する。
- 非人型・破損ファイル・引き続き不明なものは永続保存しない。必要な判定記録だけ残し、一時ファイルを消去する。**どのZIPも原本はNASへ永続保存せず、人型VRMだけ抽出・可逆圧縮**する。元ZIPのファイル名・ZIP内のVRMパスは索引に記録する。
- 有料購入・NFT保有が必要なもの、第三者権利が不明で取得条件を確認できないもの、認証や年齢制限を回避する必要があるものは一時取得もしない。無料会員登録や年齢確認そのものは除外理由としない。
- 形状確認を目的化しすぎない。実機確認ではダウンロードの成否、VRM/ZIP内部、ライセンス、重複、VRM仕様版も同時に調べる。未判定1,002件を画像だけで全件事前分類する必要はない。

## NAS保存方式（2026-10-08決定）

**保存ルールの正本は [NAS保存方式](nas-storage.md)。** `/mnt/hdd/vrm/models/` に**人型VRM本体だけ**を個別に可逆圧縮（ZIP/zstdは実測で選定）し、`/mnt/hdd/vrm/previews/` にTポーズ全身・顔のWebPを別保存する。`index.jsonl` でモデル名、カタログID、配布先、未圧縮SHA-256、画像パスを紐付ける。ZIP原本や非VRMファイルは一時取得・抽出後に削除する。元のVRMを再展開してハッシュが一致することを保存条件とする。実機検証は後日Hermes Agentが担当する。

## Polygonal Mind 100Avatarsについて

[作者の公式GitHub](https://github.com/PolygonalMind/100Avatars) のGit treeに200キャラクター各2種（通常・Voxel）、**計400の実在するVRMパス**を確認。正確なファイルパス・GitHubのバイト数を各JSONへ登録したが、個別ファイルのダウンロードや仕様版判定は未実施（`vrm_version: null`）。

利用条件は[作者README](https://github.com/PolygonalMind/100Avatars/blob/master/README.md)に記載の、オリジナルの無改変再販売をしないよう求める表現を根拠とする。ライセンスをCC0と一律断定しない。通常版とVoxel版は別VRM配布物として別レコードにする。

## 作者BOOTHモデルの継続収録（2026-10-08）

作品・商品ページに「ダウンロード商品 ¥0」かつ `.vrm` ファイル名、または無料ZIP内のVRM存在が明記されているものを採録する。作者ごとの利用規約を参照し、無償であることと商用利用・改変・再配布の許可を混同しない。VRM 0.x／1.0を同梱している場合は各VRMを別レコードにするが、単に同一VRMの「直接配布」と「VRM+VRoidのZIP配布」があるだけなら同一モデルとして重複登録しない。

動物・マスコット型も正式なVRMであれば収録する。改変・商用利用が許可されていてもモデル再配布が禁止される例があるため、NASに保存した原本を公開GitHubに追加しない。実取得・実機確認は登録件数の拡充後にまとめて行う。

## 公開GitHubからの大量登録時の注意（2026-10-08）

原作者自身のリポジトリで実在ファイルを確認しても、拡張子が `.vrm` というだけでは十分ではない。たとえば [MJMoonbow](https://github.com/MJMoonbow/VRMavatars) の5ファイルは2バイトであり、VRM/GLBヘッダーを含むことすらできないため収録しない。残りのファイルはサイズ・パスと作者ライセンス表記で仮採録し、後日の実ファイル解析までVRM形式バージョンを確定しない。

同一無料ZIPの中に4モデルがある場合はそれぞれ別レコードとするが、VRM単体で配布された同一モデルを無料ZIPでも入手できるだけなら重複登録しない。商品「Ver.2」「1.0.1」などの配布物自体の版番号は、**VRMファイルの仕様版と区別**する。

## Polygonal Mind 第3弾（2026-10-08）

- [Polygonal Mind 100Avatars v24.02.1 リリース](https://github.com/PolygonalMind/100Avatars/releases/tag/v24.02.1) は**R3をCC0として説明**し、VRM形式の配布を明示する。前2弾のGitHub本体（400ファイル・200キャラ×通常/Voxel）とR3の201〜300は別のコレクションとして区別する。
- [制作者ToxSamのOpen Source Avatars索引](https://github.com/ToxSam/open-source-avatars/blob/main/data/avatars/100avatars-r3.json) は、R3の100件に対して番号・名前・`format: VRM`・Arweave URL・ファイル名を掲載する。索引が示す `model_file_url` を直接URLとして収録した。記録したURLは `.vrm` 拡張子を持たないArweaveコンテンツID形式。
- **今回の確認はメタデータのみ**。リンクの現在のHTTP応答、実ダウンロード、GLB/VRMのヘッダー、表示確認、同一モデルの派生版は未検証。索引で確認できた標準100件のみ採録し、R3のVoxel版などは実体別URLが確認できるまで追加しない。
- R3のCC0表記をR1/R2の既存モデルへ逆適用しない。個々のモデルの現在の利用条件や配布元の変更は、後日の原本検証時に再確認する。

## 2026-10-08 新規BOOTH無料VRM

- [ARVENDAL](https://booth.pm/ja/items/8944341) は無料1体のみ（有料サポーターパックの15バリエーションは収録しない）。[Wolf Boy](https://booth.pm/ja/items/8949948) は作者が無料で2 VRMを直接公開し、VRM 0.xと記載する。
- [仮想洋品](https://booth.pm/ja/items/8907607)の5商品、[ATOR工房](https://booth.pm/ja/items/8708753)の無料単体2モデル、[潮音こまり](https://booth.pm/ja/items/7034844)、[Miu](https://booth.pm/ja/items/8205729)、[そら](https://booth.pm/ja/items/7969137)を、公式商品ページの0円・VRM収録案内に基づき採録。無料ZIP・単体ファイル・有料の同一モデル追加形式の重複を避ける。
- すべてログイン後の取得成功・ZIP内VRMの内容・実ファイル仕様は未確認であり、登録件数拡充後にHermes Agentで一括検証する。

## Polygonal Mind・ToxSamの公開IPFS VRM（2026-10-08）

- [Polygonal Mind公式100Avatars README](https://github.com/PolygonalMind/100Avatars/blob/master/README.md)には、CEOであるToxSam（Daniel Garcia）の署名があり、[ToxSamが管理するOpen Source Avatars](https://github.com/ToxSam/open-source-avatars)には作品・ライセンス・モデルURLの公開インデックスがある。
- [Halloween Rising](https://github.com/ToxSam/open-source-avatars/blob/main/data/avatars/halloween-rising.json)（60件）と[Xmas Chibis](https://github.com/ToxSam/open-source-avatars/blob/main/data/avatars/xmas-chibis.json)（80件）は、同じインデックスの `projects.json` で `creator_id: Polygonal-Mind`、`license: CC0`、`is_public: true` と明示されている。100Avatars R1/R2の無改変再販制限は**別コレクション**のため引き継がない。
- [ToxSam originals](https://github.com/ToxSam/open-source-avatars/blob/main/data/avatars/toxsam.json)（10件）は作者自身の作品として `creator_id: toxsam`、`license: CC0` と掲載されている。
- 収録した各アイテムには `format: VRM`、`is_public: true`、NFT番号・メタデータ、`https://dweb.link/ipfs/...` または `https://gateway.pinata.cloud/ipfs/...` のVRMファイルURLがある。**カタログが扱うのは公開されたファイルの取得先**であり、NFTそのものの購入・保有・ミントは対象外。
- **未確認事項**：IPFSゲートウェイの現在のHTTP応答、閲覧時のトークン認証や実ダウンロードの成否、ハッシュ照合、内部のVRM仕様バージョンとGLB検証、ライセンスの埋め込みメタデータ。公開URLの存在は購入不要な実取得に成功したことを意味しない。これらのモデルは `creator_index_direct_url_listed_download_untested` として記録する。
- 将来的にモデルの取得にNFT購入・保有や有料会員資格が不可欠と判明した場合は収録対象から除外する。無料会員登録・ログイン・年齢確認のみなら除外しない。
- 実機確認ではHermes Agentが人型VRMを個別にZIPまたはzstdで可逆圧縮し、Tポーズ・顔WebPとともに`/mnt/hdd/vrm`以下に保存する。圧縮方式は実測で決める。NFT関連ページやIPFSリンクを経由した場合もカタログIDと未圧縮VRMのSHA-256を[保存索引](nas-storage.md)に対応させる。元の配布ZIPやVRM/圧縮実体をGitHubに公開しない。
