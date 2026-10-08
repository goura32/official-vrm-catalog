# Official VRM Catalog

公式配布元から**購入せずに入手できるVRMモデル**のカタログです。VRMファイル本体の転載・再配布は行いません。

## 収録データ

- [モデル一覧（JSON）](data/models.json)
- [収録・検証方針](docs/collection-policy.md)
- [追加調査・保留候補](docs/research-notes.md)

VRM 0.x / 1.0のモデル、アバター型と機能検証用モデルを対象とします。無料の編集ソフトからVRMとして書き出せる公式サンプルも対象です。

| `access_method` | 取得方法 |
| --- | --- |
| `direct_vrm` | 公式配布先からVRMファイルを直接取得 |
| `vroid_hub_vrm` | VRoid Hubの公式モデルページからVRMを取得 |
| `vroid_studio_export` | 無料のVRoid Studioでサンプルを読み込み、VRMとして書き出す |
| `official_page_download` | 公式配布ページの手順・同意確認などを経て入手 |
| `booth_free_download` | 権利者のBOOTHページにある0円配布物を入手 |

**無料であればログイン、会員登録、年齢確認が必要でも収録します。** 各サービスの利用規約・年齢制限等に従って取得してください。料金が必要なモデルは対象外です。

## 今回確認した主な公式・作者配布元

- [VRM Consortium公式サンプル](https://github.com/vrm-c/vrm-specification/tree/master/samples) — アバターと機能テスト
- [VRoid Studio AvatarSample A〜Z](https://vroid.pixiv.help/hc/ja/articles/4402394424089-AvatarSample-A-Z) — 無料公式サンプルをVRM出力（A〜CのHub掲載版はVRM 0.x）
- [旧ベータ版 AvatarSample 1〜4](https://vroid.pixiv.help/hc/ja/articles/4402614652569) — 公式ヘルプ上のオリジナル版はCC0。加えて[公式Hubの衣装・カラー違い](https://hub.vroid.com/characters/675572020956181239/models/7175071267176594918)を別モデルとして登録（個別Hub利用条件に準拠）
- [キズナアイ KAMATTE AI](https://kizunaai.com/download/kamatteaimodel/) — VRM 1.x／0.x
- [東北ずん子・ずんだもん公式BOOTH](https://tohozunko.booth.pm/) — 無料配布版のある公式3Dモデル
- [BOOTHのクリエイター本人による無償VRM配布](https://booth.pm/ja/items/4911831) — 収録したモデルの個別ページと利用条件はJSONを参照
- [「あいす」VRM 0.x / 1.0](https://booth.pm/ja/items/7938475)、[Frii（2 VRM）](https://booth.pm/ja/items/6168778) — 仕様版・ファイル名を区別して登録
- [軽量ないものアバター](https://booth.pm/ja/items/8595180)、[standalone ALPHA試用版](https://booth.pm/ja/items/7851789) — 無料VRM版のみを収録

「無料版」以外の有料編集データや有料機能は、モデルの収録対象に含めません。

## 確認レベル

`verification` は、カタログへ登録した根拠の範囲を示します。実際のダウンロード・書き出しやVRMファイル内の権利情報まで検証済みとは限りません。

- `official_repository_file_listed`: 公式リポジトリでVRMファイルの存在を確認（内部未解析）
- `official_binary_metadata_confirmed`: VRMバイナリのGLBヘッダーとJSONチャンクを取得・解析
- `official_hub_and_help_confirmed`: VRoid公式ヘルプと公式Hubモデルページで配布案内を確認
- `official_hub_permission_and_format_confirmed`: 公式Hubモデルの投稿者、他者利用「OK（ダウンロードNGではない）」、VRM形式と利用条件を確認
- `official_help_confirmed_export_untested`: 公式ヘルプが無料モデルと書き出し方法を案内。個別エクスポートは未検証
- `official_free_distribution_listed_download_untested`: 公式配布元に無料のVRM配布案内を確認。個別の実ダウンロードは未検証

`binary_evidence` はGLBヘッダーと埋め込みVRMメタデータの解析結果。`github_blob_sha` はGitHubのGit blob IDで、VRMファイルそのもののSHA1ではありません。実際の描画・挙動検証やファイル全体のSHA1照合は未実施です。

`distribution_size_bytes` は公式GitHub APIで確認できた**配布VRMファイル自体のバイト数**（確認済みのものだけ）です。BOOTHの表示MBとは精度が異なるため推測補完しません。

`distribution_filename` は公式の配布ファイル名（直接 `.vrm` またはVRMを含むと案内された `.zip`）です。**ZIP名はZIP内部のVRM名とは限りません。** 未確認のモデルでは省略します。

`vrm_version: null` は、配布モデルの実ファイルに含まれるVRM仕様バージョンが未確認であることを示します。VRoid Hubの表示値は**Hubで配布されるモデル**に対するもので、VRoid Studioから再書き出ししたファイルの版を保証しません。既知の値も公開された説明に基づくものがあり、全件についてバイナリ解析済みという意味ではありません。
同じモデルに複数のVRM仕様版やLOW/HIGHなど異なる取得物がある場合は別レコードとします。

## 注意

- 「公式配布」や「無料」は「無条件に商用利用・改変・再配布可能」という意味ではありません。**個別の利用条件を必ず確認**してください。
- VRoid StudioのAvatarSample A〜Zは **CC0ではありません**（[公式条件](https://vroid.pixiv.help/hc/ja/articles/4402394424089-AvatarSample-A-Z)）。一方、旧ベータ版 AvatarSample_1〜4 は [CC0](https://vroid.pixiv.help/hc/ja/articles/4402614652569) です。両シリーズの利用条件を混同しないでください。
- VRoid Hubでは**他の人の利用OK**と**他の人の利用OK（ダウンロードNG）**を区別します。後者しか確認できないモデルは、VRMファイルの取得元としては登録しません。公式Hubで「OK」と表示されてもログイン後の実ダウンロードは別途確認が必要です。
- リンク先の条件・公開状況は変更される場合があります。BOOTHの無料ZIPにVRMが含まれる旨が公式説明に記載されていても、ZIP内部の解析まで完了しているとは限りません。**0円掲載はダウンロード成功の証明ではありません。** ショップ固有URLが非公開表示になる例があり、ログイン後の実際の取得可否は別途検証が必要です。
- 本カタログはVRM Consortium、pixivなどの公式プロジェクトではありません。

## データ検証

Python 3のみを使用します。外部ライブラリもGitHub Actionsも不要です。

```bash
python3 scripts/validate.py
```
