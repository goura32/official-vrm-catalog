# 収録・検証方針

## 採録条件

1. 配布者・著作権者またはその公式プロジェクトの配布案内を確認できる。
2. **購入・有料サブスクリプション・有料プランを必要とせず**、公式の案内した正規の方法でモデルを入手できる。
3. VRM形式で提供されるか、無料の公式ツールからVRM形式で書き出せる。
4. 公式ページまたは公式配布元、利用条件への参照URLを記録できる。

ログイン、無料会員登録、利用規約への同意、年齢確認、無料アプリの導入は**除外理由にしない**。年齢制限・地域制限やサービスの手続きは順守し、回避方法を案内しない。

無料・有料が混在するサイトでは**モデル個別の無料入手経路**を確認する。支払いが必須なら対象外。寄付が任意なら可。配布元の不明な転載・ミラーは対象外。

## 記録の原則

- 1つの取得物・仕様版を1レコードにする。同一キャラクターでもVRM 0.x/1.0やLOW/HIGHなど配布物が異なれば分ける。データは `data/models.json` を正とし、スクリプトは補助。
- `source_url`: 配布根拠。個別モデルページがなければモデル群の公式説明ページ。
- `download_url`: **確認できた直接VRMファイルURLだけ**を記録。ログイン画面や公式アプリの操作で取得するものは `null`。
- `distribution_size_bytes`: 公式GitHub Contents API等で**実ファイルのバイト数**を確認できた場合だけ付与。BOOTH表示のMBを逆算しない。
- `distribution_filename`: 公式ページやGitHubのファイル一覧に記載された**配布物のファイル名**。ZIP形式の場合はVRM実ファイルの名前と混同しない。未確認なら省略する。
- `access_method`: 直接VRM取得・Hub経由・無料エディタ書き出し・公式ページ・BOOTH無料配布を区別。
- `vrm_version`: 未検証なら `null`。旧形式は `0.x` と記録。
- `license_url`: 公開された利用条件へのリンク。権利の許諾可否を推測して記載しない。
- `notes`: 調査で確認した重要な制限や未確認事項。商用利用などはライセンス名称だけで判断しない。
- `verification`: どこまで確認したかを過大に記載しない。
- `binary_evidence`: VRMバイナリのGLBヘッダーとJSONチャンクを解析できた場合のみ記録。Git blob IDとファイル自体のSHA1を混同しない。

## 未検証事項

- 認証が必要な配布先の**実ログイン・実ダウンロード**、VRoid StudioでのA〜Zの**個別書き出し**は未実施。
- 実ファイル内のメタデータ、VRMバージョン、モデルの正常な描画、各機能の挙動は未検証。
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
