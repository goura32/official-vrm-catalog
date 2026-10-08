# NAS保存方式（人型VRMのみ）

2026-10-08決定。**本書をNAS保管の現行ルールの正本**とする。過去の調査記録にある「原本ZIPを永続保存」は旧方針であり、適用しない。

## 対象

- **NASに保管するモデル本体は人型の `.vrm` だけ**。直接取得したVRMも、配布ZIP内から抽出したVRMも同じ扱いにする。元のZIP、画像、VRoid編集ファイル、VRMA、非人型モデルは保存対象外。取得方法や同梱物は索引に記録すればよい。
- 未判定のモデルは配布・取得条件を確認できれば作業機の一時領域へダウンロードし、必要に応じて描画して判定する。既知の非人型は取得しない。人型と確認できないものはNASへ永続化せず、一時ファイルを削除する。
- 複数VRM入りZIPは**VRMごとに検査し、人型だけ抽出・保存**する。VRM 0.x / 1.0、衣装違い等の独立モデルは別のカタログIDに対応させる。
- **元の配布ファイルそのものを保全する必要はない**。ただし作者から取得したVRMの内容は改変・再エクスポートせず、ロスレス圧縮する。再展開すれば元VRMのバイト列に完全復元できることを検証する。

## フォルダ・形式

```text
/mnt/hdd/vrm/
├── files/
│   ├── vroid-avatarsample-a.vrm.zst
│   ├── kizuna-ai-kamatte-vrm1.vrm.zst
│   └── <catalog_id>.vrm.zst
└── index.jsonl
```

- **1カタログIDにつき1つの`<catalog_id>.vrm.zst`**。IDは正本JSONの`id`と一致させる。現行の1,297 IDはすべて`[a-z0-9-]`のみ、最大49文字でファイル名に安全。モデル名・作者名は日本語も含め索引から引く。ZIPの元ファイル名をNASの保存名として使わない。
- **zstdによる可逆圧縮**（初期設定`zstd -10 -T0`）。各VRMを個別に圧縮し、アプリで使う際は作業領域で`.vrm`に展開する。複数モデルをまとめたZIP/7zなどのコンテナは作らない。
- VRMのテクスチャにはJPEG/PNG等の圧縮済みデータが含まれるため、zstdの削減率は未計測であり、**圧縮率を保証しない**。実機試行時に元サイズ・圧縮後サイズ・所要時間を記録する。設定変更は測定結果に応じて判断し、一律の重い高圧縮処理は避ける。
- 同じ未圧縮SHA-256を持つ複数IDは**同一内容**と見なし、同一ファイルシステムならハードリンクで圧縮実体を共有する（例：`ln`）。ファイル名はID別に保つ。更新時は既存の圧縮ファイルを上書き編集せず、別の一時ファイルを作って検証後にリネームする。ハードリンク不可なら安全を優先し通常保存する。
- カタログのJSONはGitHub側が正本。NASの`index.jsonl`は**保存済み実体と正本IDとの対応表**であり、同一の配布物の再カタログ化はしない。ZIPや補助データをNASへ永続保存しない（この索引のみ管理用の例外）。

## 索引形式

`index.jsonl` は**保存済みの人型VRMを1行に1レコード**で記録する。最低限、次のフィールドを保持する。相対パスは`/mnt/hdd/vrm`を起点とする。

| フィールド | 内容 |
| --- | --- |
| `catalog_id` | 正本JSONの`id`（一意） |
| `name` / `publisher` | モデル名・配布者（カタログから転記） |
| `stored_path` | 例：`files/vroid-avatarsample-a.vrm.zst` |
| `vrm_sha256` | **展開後のVRM本体**のSHA-256（64桁） |
| `vrm_size_bytes` / `stored_size_bytes` | 展開後と圧縮保存後のサイズ |
| `vrm_version` | 実ファイルで確認した`0.x`または`1.0` |
| `source_url` / `license_url` | 公式・作者の配布元と利用条件 |
| `distribution_filename` | 取得時のVRM/ZIPファイル名（参考情報。元ファイルは保存しない） |
| `archive_member_path` | ZIPから抽出したときのZIP内部パス（直接VRMなら`null`） |
| `retrieved_at` | 取得日時（ISO 8601） |

`index.jsonl` のレコード例（ハッシュ値は説明用の仮値であり、実登録に転用しない）：

```json
{"catalog_id":"vroid-avatarsample-a","name":"AvatarSample A","publisher":"VRoid Project","stored_path":"files/vroid-avatarsample-a.vrm.zst","vrm_sha256":"<実ファイルから計算したSHA-256>","vrm_size_bytes":null,"stored_size_bytes":null,"vrm_version":null,"source_url":"https://vroid.com/","license_url":"https://vroid.com/","distribution_filename":null,"archive_member_path":null,"retrieved_at":null}
```

上のJSONは**索引フィールドの配置例**で、URL・名前・値は実際の登録情報を表していない。実機確認時には正本の値と取得時に確認した値を使用し、未確認事項を推測で補完しない。

## 保存手順（後日Hermes Agent）

1. カタログIDと正本データを確認。公式・作者の配布条件と購入不要な取得経路を確認し、作業機の一時領域にVRM/ZIPを取得。配布条件不明・有料・認証回避が必要な対象は取得しない。
2. ZIPの場合は安全に展開してVRMのみ抽出（`../`を含む不正パス、展開後の異常に大きいファイル・ZIP爆弾に注意）。元ZIPと、非VRMファイルは一時扱い。
3. `scripts/inspect_vrm.py`等でGLB/VRM構造を確認し、必要なら実際に表示して人型と判定。正本IDとの対応、バージョン、利用条件を確認。人型でなければNASには保存しない。
4. 元のVRM本体でSHA-256を計算し、`zstd -10 -T0 <元VRM> -o <一時圧縮パス>` で個別に圧縮。**一時圧縮ファイルを展開して求めたSHA-256が元VRMと完全一致すること**を確認する。
5. 既存の保存済みSHA-256と同一なら、可能ならハードリンクで重複排除。違う場合は新しい圧縮ファイルを検証後に移動。**保存したファイルの展開検証が成功してから**`index.jsonl`を原子的に更新する。
6. 元のダウンロードZIP/VRMや、展開した検査用VRMを一時領域から削除。保存物はID別の`.vrm.zst`と`index.jsonl`のみ。原本データや圧縮VRMをGitHubへコミットしない。

**復元例**：`zstd -d -c /mnt/hdd/vrm/files/<catalog_id>.vrm.zst > /tmp/<catalog_id>.vrm`。復元後の`sha256sum`が索引の`vrm_sha256`と一致することを確認して使用する。

NASへの実ファイル保存・圧縮処理は現時点では未実施。実機検証時の担当はHermes Agentとし、GitHub ActionsやRDCは使用しない。
