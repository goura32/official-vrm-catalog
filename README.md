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

## 確認レベル

`verification` は、カタログへ登録した根拠の範囲を示します。実際のダウンロード・書き出しやVRMファイル内の権利情報まで検証済みとは限りません。

- `official_repository_file_listed`: 公式リポジトリでVRMファイルの存在を確認
- `official_hub_and_help_confirmed`: VRoid公式ヘルプと公式Hubモデルページで配布案内を確認
- `official_help_confirmed_export_untested`: 公式ヘルプが無料モデルと書き出し方法を案内。個別エクスポートは未検証
- `official_free_distribution_listed_download_untested`: 公式配布元に無料のVRM配布案内を確認。個別の実ダウンロードは未検証

`vrm_version: null` は、配布モデルの実ファイルに含まれるVRM仕様バージョンが未確認であることを示します。
同じモデルに複数のVRM仕様版やLOW/HIGHなど異なる取得物がある場合は別レコードとします。

## 注意

- 「公式配布」や「無料」は「無条件に商用利用・改変・再配布可能」という意味ではありません。**個別の利用条件を必ず確認**してください。
- VRoid StudioのAvatarSample A〜Zは **CC0ではありません**。禁止事項もあります（[公式条件](https://vroid.pixiv.help/hc/ja/articles/4402394424089-AvatarSample-A-Z)）。
- リンク先の条件・公開状況は変更される場合があります。
- 本カタログはVRM Consortium、pixivなどの公式プロジェクトではありません。

## データ検証

Python 3のみを使用します。外部ライブラリもGitHub Actionsも不要です。

```bash
python3 scripts/validate.py
```
