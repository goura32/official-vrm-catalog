# NAS保存とVRMプレビュー生成

2026-10-14 B68再確認（B68 read-only baseline）。**本書がNAS保存方針の正本**。findmnt/stat/getfacl/showmount、verify_nas.py、sha256sumによる読み取り専用再監査は487 ZIP/974 WebP、ZIP 2,168,476,533 bytes、`index.jsonl` 487 rows/548,641 bytes・SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`、`verify_nas.py` `ok:true`/`errors:[]`。`/mnt/hdd` 0777 root:root、`/mnt/hdd/vrm` 0777 ws2:uucp、`models/`と`previews/` 0777 ws2:ws2、index 0600 ws2:ws2、`.index.lock` 0 bytes/mode000。今回確認した全pathにnamed/default ACLなし。NFSv3 `rw,sec=sys,local_lock=none`、3 exportsはいずれもprivate IPv4 /24に限定、wildcardなし。server-side ACL、UID/GID mapping、root/all squash、user isolation、effective NFS lock未確認のため第三者隔離は未証明で、新規保存を停止。chmod/chown/ACL/NFS設定変更なし。詳細は[B68実機検証レポート](hermes-bulk-run-results.md)を参照。過去の「配布ZIP原本を残す」「zstd確定」は旧方針であり、適用しない。

## 基本原則

- **保存するモデル本体は人型VRMのみ。** ダウンロードがZIPでも、内部の`.vrm`をモデル単位に分離して保存する。元の配布ZIP、編集用データ、非人型は永続保存しない。
- **混合ZIPも入力として許容する。** 無料の正規配布ZIPにVRMと`.vroid`/FBX/テクスチャ等が混在していても、NASへ残すのがVRMだけなら保存方針に反しない。別の権利・年齢・ID対応・形状の確認は必要。[完成条件・混合ZIPの再確認方針](completion-criteria.md)を参照。
- **VRMから全身Tポーズと顔の正面WebPを各1枚生成**し、モデルと同じカタログIDで保存する。画像は検索・一覧表示用にZIP外に置く。
- モデルの識別はファイル名だけに頼らず、`index.jsonl`へID、名前、作者、配布元、規約URL、元VRMのSHA-256、圧縮方式、ファイル・画像パスを記録する。
- 形状が不明なものは無料・取得条件を確認したうえで一時取得して検査可能。画像生成に失敗した場合は理由を記録して個別再試行し、**別モデルの画像で代用しない**。
- 圧縮は元VRMのバイト列を完全に復元できる可逆形式だけを使う。実際の展開データのSHA-256が一致することが保存条件。

## 保存構成

```text
/mnt/hdd/vrm/
├── models/
│   ├── <catalog_id>.zip         # ZIPを採用した場合: 内部は model.vrm 1個
│   └── <catalog_id>.vrm.zst     # zstd採用の場合（同じIDで両方は保存しない）
├── previews/
│   ├── <catalog_id>-tpose.webp  # 全身正面Tポーズ、768 × 1024
│   └── <catalog_id>-face.webp   # 顔正面、512 × 512
└── index.jsonl                  # モデルと画像の対応表
```

この構成は保存仕様であり、実際の配置状況は本書末尾と[実機検証レポート](hermes-bulk-run-results.md)を参照する。登録IDは正本`data/models.json`および`data/collections/*.json`の`id`と一致させる。名前に日本語が含まれていてもIDはASCIIなのでパスが安定する。

## 圧縮形式の決定

| 比較する形式 | 圧縮設定 | 特性 |
| --- | --- | --- |
| ZIP | Deflate、level 6、1 VRM/ZIP | OS標準ツール等で扱いやすい |
| zstd | level 10、各VRM単体 | 高速な可逆圧縮に向く |

**ZIPを実機採用済み。** 2026-10-09の3件実測では、zstdとの差は元VRMの合計サイズに対して1.2455%であり、3%基準以内だったため、互換性を優先してZIPに統一した。既存87件もZIPで保存・監査済み。後続の同じNAS索引では形式比較をやり直さず、ZIPを使用する。詳細は[実機検証レポート](hermes-bulk-run-results.md)。

3件以上の実VRMを、できれば複数の制作者・テクスチャ規模から選んで比較する。

```bash
python3 scripts/benchmark_vrm_compression.py /tmp/a.vrm /tmp/b.vrm /tmp/c.vrm
```

測定するのはVRMの元サイズ・圧縮後サイズ・処理時間・**復元SHA-256一致**。ZIPの追加容量が、モデル元サイズ合計の**3%以内**なら互換性優先でZIP、それを超えればzstdを採用する。3件未満、またはzstdコマンドがない場合は結論を保留する。結果は実機検証記録に残す。どちらを採用しても**全モデルを同じ形式に統一**し、重複した別形式は常用保管しない。

異なるカタログIDでVRM SHA-256が完全一致した場合、**保存スクリプトは同一NASファイルシステム上の圧縮ファイルをハードリンクで共有**する。同一データを異なる名前で登録でき、モデル名・出典等はIDごとの索引で保持する。ZIP内のVRM名はID共通の`model.vrm`とし、ZIP外側のファイル名と索引でIDを識別する。ハードリンクできない場合は個別に圧縮保存する。

## 自動プレビュー作成

`tools/vrm-preview/`に、three.js・`@pixiv/three-vrm`・Playwright・sharpを利用したローカル撮影処理を用意する。VRMファイルはローカルHTTPサーバーから読み込み、外部へ送信しない。VRM 0.xは正面方向を補正し、normalized humanoidのTポーズを試みる。顔は頭部ボーンの位置を基準に撮影する。

```bash
cd tools/vrm-preview
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install
node generate.mjs --vrm /tmp/sample.vrm --id <catalog_id> \
    --out-dir /tmp/vrm-previews --browser /usr/bin/chromium
cd ../..
```

モデルの正面方向や頭部ボーン位置が標準カメラに合わない場合に限り、`--front-yaw-deg`（-360〜360度）、`--face-y-offset-frac`（全身高に対する顔中心の補正、-1〜1）、`--face-height-frac`（顔画像の縦画角、0.1〜1）を指定できる。補正後も全身Tポーズと顔を目視し、両方が適切でないモデルは保存しない。

生成されるのは `<catalog_id>-tpose.webp`、`<catalog_id>-face.webp`、**`<catalog_id>-previews.json`**。最後のJSONに元VRMのSHA-256、画像名・画素サイズ・**画像ごとのSHA-256**を含め、取り違えや生成後のすり替わりを検知する。正面はVRM座標系に準拠した標準カメラとする。

**自動生成は必ずしも全モデルで成功しない。** 頭部ボーン欠損、特殊な骨格、髪やアクセサリーの遮蔽、顔の画角、WebGLソフトウェアレンダリングの互換性などは実機で確認する。表示不可のモデルはサムネイルの代用を捏造せず、要手動対応として記録する。VRMのTポーズ画像はモデルの姿勢を表示したもので、VRMバイナリそのものは編集しない。

## 検証してNASへ保存

実機で人型と判断でき、配布・利用条件が確認できたモデルだけに適用する。

```bash
python3 scripts/inspect_vrm.py /tmp/sample.vrm
python3 scripts/archive_vrm.py \
  --id <catalog_id> --vrm /tmp/sample.vrm \
  --previews /tmp/vrm-previews \
  --nas-root /mnt/hdd/vrm --format zip --confirm-humanoid
```

過去の比較でZIP採用を決定したため、同一NASでは原則`--format zip`を継続する。異なる圧縮方式を混在させない。元ZIP内のパスが判明している場合は`--archive-member 'folder/model.vrm'`を追加する。

保存処理は次の条件を満たした場合だけ索引を更新する。

1. カタログIDが正本JSONに**一意に存在**し、既知の非人型リストに入っていない。元VRMは`inspect_vrm.py`でVRMとして認識できる。`--confirm-humanoid`は実機で外形を確認した担当者だけが指定する。
2. 画像2枚がWebPであり、プレビュー生成JSONの`catalog_id`、**元VRMのSHA-256**、画像名・寸法情報・**画像のSHA-256**が一致する。
3. ZIPまたはzstdから復元したVRMのSHA-256が元VRMと一致する。
4. ID別の圧縮VRMとWebPを保存し、**`.index.lock`による排他制御のもと**で索引`index.jsonl`を原子的に更新する。既存の同一IDがあるときは黙って上書きせず停止する。`.index.lock`は小さな管理用ファイルとして残す。

索引は保存済みVRM1体につき1行。索引には`catalog_id`、`name`、`publisher`、`stored_path`、`compression`、`vrm_sha256`、`archive_sha256`、`vrm_size_bytes`、`stored_size_bytes`、`vrm_version`、`source_url`、`license_url`、`distribution_filename`、`archive_member_path`、`retrieved_at`（元の取得日時が判明する場合のみ）、`archived_at`（NAS保管日時）、`previews.tpose/face.path/sha256`を含める。

一時取得した元ZIP、VRM、PNG等の中間画像は**検証完了後に作業機から消去する運用**とする。現行保存スクリプトは取得・一時ファイルの自動消去までは担当せず、実機バッチ処理側が担う。モデル本体・画像・索引はNASに保持し、GitHubへモデル本体やサムネイルはコミットしない。

## 検証用の最小テスト

`tests/test_nas_storage.py` は、NASやネットワークに触れず、一時フォルダ内の合成VRM・実WebP画像で保存処理を検証する。

```bash
python3 -m unittest discover -s tests -v
```

対象は、WebPヘッダーと実寸法、ZIPの可逆復元、**同一バイト列VRMのハードリンク共有**、画像の不整合や既知非人型の拒否、zstdがあればその可逆復元。**合成VRMは3D画像生成の動作テストには使えない**ため、レンダリング・カメラ画角・実データの入手可否は別途実機で検証する。

## NAS保存後の整合性再検証

`scripts/verify_nas.py`は読み取り専用で、圧縮VRMの展開SHA-256、保存先とカタログID、Tポーズ・顔WebPの寸法・SHA-256、索引ID重複、保存形式の混在を検査する。

```bash
python3 scripts/verify_nas.py --nas-root /mnt/hdd/vrm
```

`ok: true`かつ`errors: []`であることをNAS処理の完了条件とする。**実行するまで検査済みと記載しない**。実機作業の継続指示は[Hermes Agent認証済みBOOTH一括継続指示](hermes-bulk-resume.md)へ集約し、保存済みIDと権利保留IDを再処理しない。

## 実行状況（2026-10-11更新）

- **保存実績（B35後）**：ZIP Deflate level 6で**487モデル・WebP 974枚**。未圧縮VRM 3,925,815,073 bytes、ZIP 2,168,476,533 bytes、WebP 15,210,140 bytes。ZIPによる削減率44.7637%。B35後の`verify_nas.py`は`ok:true`、`errors:[]`。
- **B35終了時の残件（797 IDの排他的区分、履歴値）**：NAS保存157、非人型68（実体8・作者索引1・商品ページ59）、埋込権利矛盾130、利用条件/年齢/内容未確認237、物理VRM対応不明14、混合ZIPだけを理由にした範囲外0、別hostリダイレクト拒否2、`dweb.link`恒久ブロック/未試行141、BOOTH認証待ち0、別途未検証1、VRoid Hub認証待ち16、商品ページ404 3、VRoid Studioエクスポート専用23、公式メタデータ/リポジトリのみ5。合計797。B35は41 ID/35商品を再評価し、3 ID保存・9 ID非人型・29 IDを独立根拠不足で保留した。物理VRM対応不明14 IDは既存記録照合後もすべて保留。B34のBOOTH認証待ち145件は全件状態遷移済み。別途未検証1件は未完了のまま維持する。現行の後続再評価後の集計は[完成条件](completion-criteria.md)を参照。
- **保護方針**：B35開始時の484 ZIP・968 WebPの全索引行SHA-256を保持し、読み取り専用監査も全ファイル整合を確認。旧355件の保護対象行SHA-256は`4970dab415f5ca7c730aaaf6ece0e490888c2cdf9789252c3e0208b459501f19`でbaselineと一致する。B35で追加したモデル/プレビューはmode0600。GitHub Actions・RDCは使わない。

## 読み取り専用アクセス管理監査（2026-10-11）

監査は読み取り専用。`chmod`/`chown`、ACL変更、NAS/NFS共有設定変更は行っていない。

- **B40時点のスナップショット**：読み取り専用`verify_nas.py`は`ok:true`、`errors:[]`、ZIP entries 487、previews 974、ZIP bytes 2,168,476,533、形式ZIPのみ。`index.jsonl` SHA-256は`0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。当時の`models/`487 ZIP、`previews/`974 WebP、`index.jsonl`はmode 0600、owner UID/GID 1000/1000、空`.index.lock`はmode 0777。監査書込みなし。
- **B47権限スナップショット（履歴）**：`/mnt/hdd/vrm`、`models/`、`previews/`はmode 0777（`other::rwx`）。`index.jsonl`は0600、`.index.lock`は0 bytes/mode 000。再帰`getfacl`でnamed/default ACLなし。B43以前に記録された`.index.lock` mode 0777との不一致は未解明で、こちらからchmod/chown・ACL・共有設定変更は行っていない。
- 実マウントはautofs配下のNFSv3、`rw`、`sec=sys`、`local_lock=none`。B48の読み取り専用`showmount -e nas1.local`では対象`/volume1/hdd`を含む3 exportsがprivate IPv4 /24に限定され、wildcardは表示されなかった。実IP/許可ネットワーク値は本書に記録しない。
- これはLAN範囲の制限であり、ユーザー単位の私有性を証明しない。NFSv3 AUTH_SYSはクライアント側のUID/GIDを用いる方式で、強い暗号学的なユーザー認証境界ではない（[RFC 5531](https://www.rfc-editor.org/rfc/rfc5531)）。`sec=sys`環境下でサーバーが資格情報をどう制限・マップするか、`root_squash`/`all_squash`、NAS側ACL・共有権限、個別の許可クライアントは未確認。`showmount`はprivate IPv4 /24単位のexport制限を示すが、端末/利用者分離までは示さない。mode 0600だけではこの不足を埋めない。
- **評価：第三者が読めない/変更できない「非公開保存」とは確認できていない。** `/mnt/hdd/vrm`・`models/`・`previews/`は0777。`.index.lock`はB44以降の再確認でmode 000。NFSv3 `sec=sys`、`local_lock=none`であり、exportはprivate IPv4 /24に限定されるが個別端末/利用者の許可設定は不明。NAS側の共有ACL、UID/GID mapping、`root_squash`/`all_squash`、実効lock制御は未確認。B48の`showmount`はネットワーク範囲を示すだけで第三者隔離を証明しない。第三者取得禁止条件がある新規モデルは、NAS管理者が実効的なクライアント・ユーザー隔離とlock運用を確認するまで追加保存しない。既存487件は保持し、削除・権限変更は行わない。
- **B43読み取り専用再確認**：`verify_nas.py`は487 ZIP/974 WebP、`ok:true`、`errors:[]`、ZIP bytes 2,168,476,533。`index.jsonl`は548,641 bytes、SHA-256は`0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`で不変。root/models/previewsは0777、indexは0600、空の`.index.lock`は0777。名前付きACL/default ACLなし。実マウントはNFSv3 `rw,sec=sys,local_lock=none`。`showmount -e`は`RPC: Program not registered`で失敗し、export範囲・サーバー側ACL/UID mapping/squash・実効第三者隔離は引き続き未確認。NASへの書込み、`chmod`/`chown`、ACL/NFS設定変更は行っていない。
- **B44読み取り専用再確認**：487 ZIP/974 WebP、`ok:true`/`errors:[]`、index bytes/hashはB43と同じ。root/models/previewsは0777、indexは0600、名前付き/default ACLなし。NFSv3 `rw,sec=sys,local_lock=none`、`showmount -e`失敗。B44では空の`.index.lock`がmode 000（owner UID/GID 1000/1000、ACL `user::--- / group::--- / other::---`）と確認された。これはB43記録のmode 0777と異なるが、変化の原因/時刻は不明。こちらから権限変更はしていない。親ディレクトリが0777であること、NFS認証/サーバー側共有設定が未確認であることから第三者隔離を認定せず、新規NAS保存は停止する。既存487件は保持する。
- **B45読み取り専用再確認（2026-10-12）**：`verify_nas.py`は487 ZIP/974 WebP、`ok:true`、`errors:[]`、ZIP bytes 2,168,476,533。`index.jsonl`は548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previews 0777、index 0600、`.index.lock` 0 bytes/mode 000。再帰ACL監査でnamed/default ACLなし。実マウントNFSv3 `rw,sec=sys,local_lock=none`、`showmount -e`は`RPC: Program not registered`で失敗。B44のlock mode000も継続観測。サーバー側共有ACL/UID mapping/squash/export範囲と第三者隔離は未確認。NASへの書込みや権限設定変更は行っていない。
- **B46読み取り専用再確認（2026-10-12）**：487 ZIP/974 WebPとindex bytes/hashはB45と同じ。root/models/previews 0777、index 0600、`.index.lock` 0 bytes/mode 000。named/default ACLなし。NFSv3 `rw,vers=3,sec=sys,local_lock=none`、`showmount -e`はRPC errorでexport範囲不明。NAS書込み・chmod/chown・共有設定変更なし。実効的な第三者隔離は引き続き未確認。
- **B47読み取り専用再確認（2026-10-13）**：既存487 ZIP/974 WebP、`verify_nas.py`は`ok:true`/`errors:[]`、ZIP bytes 2,168,476,533。`index.jsonl` 548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previews 0777、index 0600、空`.index.lock` 0 bytes/mode 000。再帰`getfacl`でnamed/default ACLなし。`nfsstat -m`はNFSv3 `rw,vers=3,sec=sys,local_lock=none`を報告し、`findmnt -T`はautofs層を表示。`showmount -e`はRPC errorで失敗し、export範囲を現在確認できない。NASへの書込み、`chmod`/`chown`、ACL/NFS共有設定変更なし。実効的な第三者隔離は未確認のため新規保存停止を継続する。

- **B48読み取り専用再確認（2026-10-13）**：`verify_nas.py`は487 ZIP/974 WebP、`ok:true`、`errors:[]`、ZIP bytes 2,168,476,533。`index.jsonl`は548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previewsは0777、indexは0600、`.index.lock`は0 bytes/mode 000。`getfacl`でnamed/default ACLなし。実マウントはautofs配下のNFSv3 `rw,sec=sys,local_lock=none`。`showmount -e nas1.local`は対象exportを含む3 exportsをprivate IPv4 /24に限定しwildcardなしと表示した（実IP/許可ネットワーク値は記録しない）。これはネットワーク範囲の制限に留まり、0777親ディレクトリ下の第三者・利用者別アクセスを排除する根拠ではない。サーバー側ACL、UID/GID mapping、`root_squash`/`all_squash`、個別許可クライアント、実効lock制御は未確認。NASへの書込み、`chmod`/`chown`、ACL/NFS共有設定変更は行わず、新規保存停止を継続する。
- **B50読み取り専用再確認（2026-10-13）**：`verify_nas.py`は487 ZIP/974 WebP、ZIP bytes 2,168,476,533、ZIPのみ、`ok:true`/`errors:[]`。`index.jsonl`は548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previewsは0777、indexは0600、`.index.lock`は0 bytes/mode 000。`getfacl`でnamed/default ACLなし。実マウントはautofs配下のNFSv3 `rw,sec=sys,local_lock=none`。`showmount -e nas1.local`はHDD exportを含む3 exportsをprivate IPv4 /24に限定しwildcardなしと表示した（実IP/許可ネットワーク値は記録しない）。ネットワーク制限は見えるが、サーバー側ACL、UID/GID mapping、`root_squash`/`all_squash`、個別client/user isolation、実効lock制御は未確認のため、非公開保存の第三者隔離は証明できない。NASへの書込み、`chmod`/`chown`、ACL/NFS共有設定変更は行わず、既存487件を保護し新規保存停止を継続する。
- **B51読み取り専用再確認（2026-10-13）**：B50と同じく`verify_nas.py`は487 ZIP/974 WebP、ZIP bytes 2,168,476,533、ZIPのみ、`ok:true`/`errors:[]`。`index.jsonl`は548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previewsは0777、indexは0600、`.index.lock`は0 bytes/mode 000。再帰`getfacl`でnamed/default ACLなし。`findmnt`はautofs配下の`nas1.local:/volume1/hdd` NFSv3 `rw,sec=sys,local_lock=none`を確認。`showmount -e nas1.local`はHDDを含む3 exportsをprivate IPv4 /24に限定、wildcardなしと表示（実IP/許可ネットワーク値は記録しない）。server-side ACL、UID/GID mapping、squash、個別client allowlist、実効lockは未確認。非公開隔離は証明されず、既存資産を保護し新規保存停止を継続。書込み/権限/NFS設定変更なし。
- **B53読み取り専用再確認（2026-10-14）**：`verify_nas.py`は487 ZIP/974 WebP、2,168,476,533 ZIP bytes、ZIPのみ、`ok:true`/`errors:[]`。`index.jsonl` 548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`で不変。`/mnt/hdd/vrm`・`models/`・`previews/`は0777、indexは0600、`.index.lock`は0 bytes/mode 000、再帰ACLにnamed/default entriesなし。実マウントはautofs配下のNFSv3 `rw,sec=sys,local_lock=none`。`showmount -e`は3 exportsをprivate IPv4 /24に限定しwildcardなしと表示するが、server ACL、UID/GID mapping、`root_squash`/`all_squash`、ユーザー別隔離、実効lockは未確認であり、非公開保存の第三者隔離は証明できない。既存487件を保護し、新規保存停止を継続。NASへの書込み、`chmod`/`chown`、ACL/NFS共有設定変更なし。
- **B54読み取り専用再確認（2026-10-14）**：`verify_nas.py`は487 ZIP/974 WebP、2,168,476,533 ZIP bytes、ZIPのみ、`ok:true`/`errors:[]`。`index.jsonl`は548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previewsは0777、indexは0600、`.index.lock`は0 bytes/mode 000。今回確認したroot/models/previews/index/lockにはnamed/default ACLなし。`findmnt`はautofs配下のNFSv3 `rw,sec=sys,local_lock=none`、`showmount -e`は3 exportsがprivate IPv4 /24に限定されwildcardなしと表示。server-side ACL、UID/GID mapping、`root_squash`/`all_squash`、個別利用者隔離、実効lockは未確認で、非公開保存の第三者隔離は証明できない。既存487件を保護し、新規NAS保存を停止。NASへの書込み、`chmod`/`chown`、ACL/NFS共有設定変更なし。
- **B58読み取り専用再確認（2026-10-14）**：`verify_nas.py`は487 ZIP/974 WebP、2,168,476,533 ZIP bytes、ZIPのみ、`ok:true`/`errors:[]`。`index.jsonl`は487行/548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。root/models/previewsは0777、indexは0600、`.index.lock`は0 bytes/mode 000。`getfacl`でnamed/default ACLなし。`findmnt`はautofs配下の`nas1.local:/volume1/hdd` NFSv3 `rw,sec=sys,local_lock=none`。`showmount -e nas1.local`はHDD exportを含む3 exportsをprivate IPv4 /24に限定しwildcardなしと表示。これはネットワーク範囲であり、ユーザー別隔離の証拠ではない。server-side ACL、UID/GID mapping、`root_squash`/`all_squash`、個別利用者隔離、実効lock制御は未確認で、非公開保存の第三者隔離は証明できない。既存487件を保護し、新規NAS保存停止を継続。NAS書込み・`chmod`/`chown`・ACL/NFS共有設定変更なし。

- **B60読み取り専用再確認（2026-10-14）**：`verify_nas.py`は487 ZIP/974 WebP、ZIP bytes 2,168,476,533、`ok:true`/`errors:[]`。`index.jsonl`は487行/548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。`/mnt/hdd`は0777/root:root、`/mnt/hdd/vrm`は0777/ws2:uucp、`models/`と`previews/`は0777/ws2:ws2、indexは0600/ws2:ws2、空`.index.lock`は0 bytes/mode 000。再帰`getfacl`でnamed/default ACLなし。実マウントはautofs配下の`nas1.local:/volume1/hdd` NFSv3 `rw,sec=sys,local_lock=none`。`showmount -e`は3 exportsがprivate IPv4 /24に限定されwildcardなしと表示（アドレス値は記録しない）。server-side ACL、UID/GID mapping、`root_squash`/`all_squash`、利用者別隔離、実効NFS lockは未確認で、非公開保存の第三者隔離は証明できない。df表示は22T total/16T used/6.8T available/70%使用。既存487件を保持し、新規保存を停止。NAS書込み、`chmod`/`chown`、ACL/NFS変更なし。

- **B66読み取り専用再確認（2026-10-14）**：`verify_nas.py`は487 ZIP/974 WebP、ZIP bytes 2,168,476,533、ZIPのみ、`ok:true`/`errors:[]`。`index.jsonl`は487行/548,641 bytes、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`。`/mnt/hdd` 0777 root:root、`/mnt/hdd/vrm` 0777 ws2:uucp、`models/`・`previews/` 0777 ws2:ws2、index 0600、`.index.lock` 0 bytes/mode 000。`/mnt/hdd`・vrm・models・previews・index・lockでnamed/default ACLなし。autofs配下のNFSv3 `rw,sec=sys,local_lock=none`。`showmount -e`は3 exportsをprivate IPv4 /24に限定しwildcardなしと表示。server-side ACL、UID/GID mapping、squash、user isolation、effective lock未確認で第三者隔離は未証明。既存487件を保持し、新規保存停止。NAS書込み・chmod/chown・ACL/NFS設定変更なし。

- **B68読み取り専用再確認（2026-10-14）**：`verify_nas.py`は487 ZIP/974 WebP、2,168,476,533 ZIP bytes、`ok:true`/`errors:[]`。`index.jsonl`は487行/548,641 bytesで、SHA-256 `0bf57c18c66a14caaa79578f8865f2d8242df49a4a2e7cb7b68e19c7c1ec3a9f`（基準値と一致）。`stat`は`/mnt/hdd` 0777 root:root、`/mnt/hdd/vrm` 0777 ws2:uucp、`models/`と`previews/` 0777 ws2:ws2、index 0600 ws2:ws2、`.index.lock` 0 bytes/mode 000。確認対象全pathで`getfacl`にnamed/default ACLなし。`findmnt`はautofs配下の`nas1.local:/volume1/hdd` NFSv3 `rw,sec=sys,local_lock=none`を表示。`showmount -e`は3 exports・3許可entry、すべてprivate IPv4 /24、wildcardなし（実IP/許可ネットワークは記録しない）。0777ディレクトリとAUTH_SYSのクライアント可視情報だけでは、サーバー側ACL/UID mapping/squash・利用者隔離・実効ロックや第三者からの非公開性を証明できない。既存487件を保護し新規保存停止。NAS書込み・chmod/chown・ACL/NFS設定変更なし。
