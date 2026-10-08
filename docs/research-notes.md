# 追加調査・収録保留

2026-10-08時点の公開情報に基づく。**冒頭の保留候補と「追加保留配布物」だけ** `data/models.json` および `data/collections/*.json` の収録件数に含めない。「今回収録した関連モデル」「追加収録・要注意」は登録済みレコードの補足。根拠を確認できた未収録候補は登録する。

| 候補 | 調査結果 | 保留理由 |
| --- | --- | --- |
| [Alicia Solid / ニコニ立体ちゃん (VRM 0.x)](https://github.com/vrm-c/UniVRM/blob/master/Tests/Models/Alicia_vrm-0.51/AliciaSolid_vrm-0.51.vrm) | 公式UniVRMリポジトリに約7.9MBのVRM実ファイルが存在。公式コードにはニコニ立体ちゃん規約URLが記載されている | [旧公式利用規約URL](https://3d.nicovideo.jp/alicia/rule.html)に今回アクセスできず、条件の現行性を検証できない |
| [東北ずん子（通常モデル）](https://zunko.jp/con_illust.html) | [BOOTH共通商品URL](https://booth.pm/ja/items/1050142)には0円の3バージョンZIPが掲載。ショップ固有URLは非公開と表示される場合があり、公開状態が食い違う | 実ダウンロード可否とZIP中のVRMバージョンを確認後、各配布物の収録を判断 |
| [ずんだもん（人型・マスコット）](https://zunko.jp/con_illust.html) | [マスコットのBOOTH共通商品URL](https://booth.pm/ja/items/2744821)は0円とVRM 1.0・歩行/飛行モデル2種を掲載。一方ショップ固有URLは非公開表示の場合あり | ショップ固有URLでは非公開表示。実ダウンロード可否と他の人型モデルの配布条件を再確認 |
| [HAOLAN / ハオラン](https://booth.pm/ja/items/3818504) | 作者の公式BOOTHに0円商品。ただし記載物はUnitypackage・FBX・テクスチャ・Blender。バーチャルキャストに第三者が0 VCCのVRMとして掲載 | 作者の0円パッケージ内にVRMがあると確認できない。オリジナルとVRM配布元の関係の追加確認が必要 |

## 東北ずん子・ずんだもんの追加保留配布物（2026-10-08）

- [東北ずん子公式3Dモデル](https://booth.pm/ja/items/1050142)：0円の `旧モデル_zunko.zip`、`Zunko_ModelSet.zip`、`Zunko2023K_ModelSet.zip`。新バージョンはVRM 1.0にも対応と記載。ただしショップ固有URLでは非公開表示となるため、3配布物の実取得・ZIP内部・VRM仕様バージョンは未検証。**まだ収録しない**。
- [マスコットずんだもん公式3Dモデル](https://booth.pm/ja/items/2744821)：0円の `ずんだもん_通常_2025モデルセット.zip` はVRM 1.0に対応、歩行版と飛行版の2VRMモデルと公式明記。ただしショップ固有URLは非公開表示。**まだ収録しない**。
- 既登録の[ミニ東北ずん子](https://booth.pm/ja/items/7304550)・[ミニずんだもん](https://booth.pm/ja/items/7304529)・[あまね](https://booth.pm/ja/items/4911831)・[Libby](https://booth.pm/ja/items/4893360)も、共通商品ページの無料表示とショップURLの非公開表示が食い違うため、取得可否の確認が必要。

## 今回収録した関連モデル

- [ミニ東北ずん子](https://booth.pm/ja/items/7304550) と [ミニずんだもん](https://booth.pm/ja/items/7304529)：BOOTHの商品ページで公式配布の無料ZIPを確認。実ZIP未解析につきバージョンは不明。
- [あまね](https://booth.pm/ja/items/4911831)：Type-1〜4の通常版と素体版、計8ファイルを0円で配布と明記。

## 2026-10-08 追加収録・要注意

- [あいす](https://booth.pm/ja/items/7938475)：無料のVRM 0.x / 1.0は別ファイル。VRoid編集データは有料で収録対象外。無料のPDF規約本文は未取得。
- [Frii](https://booth.pm/ja/items/6168778)：無料のVRMが2種類あるが、`Frii.vrm` の規格版は未確認。
- [Small Black White Bear Girl](https://booth.pm/ja/items/6835336) と [2](https://booth.pm/ja/items/6839545)、[練習用Black Bear](https://booth.pm/ja/items/6820844)：別商品・別VRMとして収録。
- [standalone ALPHA](https://booth.pm/ja/items/7851789)：無料の試用版だけ収録（有料フルパッケージは対象外）。
- [いものアバター](https://booth.pm/ja/items/8595180)：無料VRM本体のみ収録。有料の色違い・追加テクスチャは対象外。

## 今回確認した公式VRoid Hubの追加バリエーション（登録済み）

- β Ver AvatarSample_1の[ダークネス版](https://hub.vroid.com/characters/675572020956181239/models/6535695942068248968)、[制服2019](https://hub.vroid.com/characters/675572020956181239/models/7175071267176594918)、[制服2019ダークネス](https://hub.vroid.com/characters/675572020956181239/models/5306079829291212184)
- β Ver AvatarSample_[2](https://hub.vroid.com/characters/945152946522067123/models/3383751442912063017)・[3](https://hub.vroid.com/characters/6193066630030526355/models/537531113514541613)・[4](https://hub.vroid.com/characters/2792872861023597723/models/9138892883072488102) の制服2019版
- いずれもVRoid Project公式アカウント公開、「他の人の利用OK（ダウンロードNGではない）」、VRM 0.0を公開ページで確認。実ダウンロードは未実施。

## バイナリメタデータ未解析の公式サンプル

- [Seed-san](https://github.com/vrm-c/vrm-specification/tree/master/samples/Seed-san)：公式GitHubで10,917,800バイトの実ファイルを確認。大きいバイナリを読み取りAPIが返さないため内部未解析。
- [VRM1 Constraint Twist](https://github.com/vrm-c/vrm-specification/tree/master/samples/VRM1_Constraint_Twist_Sample)：同様に10,776,032バイトを確認。内部未解析。
- 残りの公式テスト3件はバイナリメタデータ解析済み（models.json の binary_evidence）。

## 次の確認

- 公式配布ページの実ダウンロード／認証の要否（購入不要である限り認証は除外理由にしない）
- 配布アーカイブのVRMファイル有無・ファイル内拡張・バージョン・権利情報
- 配布停止・閲覧不可などの状態変化
- 同じモデルの別バージョンを別レコードとする場合の重複チェック

認証・年齢制限を回避して取得しない。実行に利用者のアカウントが必要な検証は未実施として記録する。

## 過去会話・資料からの追加収録（2026-10-08）

過去のVRM / VRMA調査メモ（`vrm-vrma-test-resources.md`）を参照し、**新たな公式配布ページで確認できた25件**を `data/models.json` に追加。内訳はコナミLAUGH DiAMOND 4、つくよみちゃんタイプA 10、Sony mocopi RAYNOSちゃん 3、夢ノ結唱 POPY/ROSE 2、ミライ小町 1、AIニケちゃん 3、結月ゆかり麗 1、ふぁふぁ無料VRM 1。原本は未取得。

制作元の[Polygonal Mind 100Avatars](https://github.com/PolygonalMind/100Avatars) はGitツリー全件のパスとファイルサイズを確認できたため、200モデル×標準版・Voxel版 = 400件を `data/collections/polygonalmind-*.json` に分割収録。

**未収録として調査継続**：夢ノ結唱PASTEL/HALO/AVERの公式サイトには無料の3DモデルZIPの案内があるが、各ZIPへのVRM同梱を今回明示的に確認できなかったため除外。Alicia Solidの権利条件・配布状態、東北ずん子/ずんだもんの一部商品のショップ側公開状態も保留のまま。

## 追加収録（2026-10-08・無料作者配布30件）

作者本人のBOOTH商品ページでVRM形式と0円配布を確認し、次の計30件を `data/models.json` に登録した（総数516→546）。

- [kanon MK3D](https://booth.pm/ja/items/6179337)：動物・季節マスコット11件。利用条件はUVライセンス＋作者個別条項。小型VRMも含む。
- [shop-perch](https://booth.pm/ja/items/6676231)：縦ロール（ZIP同梱）、[東雲ver.2](https://booth.pm/ja/items/6316885)、[時雨](https://booth.pm/ja/items/6444701)の3件。
- [A.P.のおみせ](https://booth.pm/ja/items/6050266)：姐さん、[バトラーちゃん](https://booth.pm/ja/items/5980433)の小型VRM 2件。無料のVRM単体と編集用ZIPは**同一モデルとして数える**。
- [そくかちゅう。「シロ」](https://booth.pm/ja/items/7234388)：VRM 1.0と0.xの別版2件（同じZIP）。
- [CustomLive2DAvatar「めいどちゃん」](https://booth.pm/ja/items/2593934)：通常・黒服の2件を同一ZIPに収録。[くらんも「モブ」](https://booth.pm/ja/items/4136312)は2モデル入り無料ZIP。
- その他：[Anime Student](https://booth.pm/ja/items/6018415)、[ちえり](https://booth.pm/ja/items/6076752)、[Nasha](https://booth.pm/ja/items/6095735)、[VTuberモデル](https://booth.pm/ja/items/5095913)、[Aidin](https://booth.pm/ja/items/3707650)、[まゆき](https://booth.pm/ja/items/4825706)、[Dalji](https://booth.pm/ja/items/4898876)、[ちょっとやんじゃった子](https://booth.pm/ja/items/3124874)。

**実ファイル未確認**：BOOTHのログイン後ダウンロード、ZIP内部のVRMファイル名、仕様バージョン等は実機確認フェーズで調べる。NASの将来原本保存先は `/mnt/hdd/vrm`。

## 作者配布モデルを追加（2026-10-08・35件）

無料のVRMファイル、またはVRMを含むZIPと0円価格をBOOTHの商品単位で照合したうえで、35件を `data/models.json` に登録（総数546→581）。

- [shop-perch](https://booth.pm/ja/items/8580892)：コトハ、コハク、エレイン、サキ、アイリーン、ヒスイ、ヒイラギ、スズナ、メティス、ユズ、ユウナギ、リーヤーの12モデル。VRM 0.x／1.0は商品説明に沿って記録。有料の `.vroid` は数えない。
- [6666669 / ROLOCK](https://booth.pm/ja/items/6029627)：MIKKE、ペストマスクちゃん、黒曜VRM 0.x/1.0の4モデル。**黒曜の2版は同じ無料ZIPに同梱**。MIKKEのショップ固有URLに非公開表示があるためログイン後取得は要確認。
- [RomanticSpicaの「りあん」](https://booth.pm/ja/items/8165924)：通常版・素体版それぞれにVRM 0.x／1.0があり4件。
- [ドルミィのDoll me](https://booth.pm/ja/items/5173073)：002、006、007、008、009、010の計6件。すべて作者ページでは0円だが**期間限定無料**と記載。VRM1.0非対応を明記。
- その他9件：[Ryuneru](https://booth.pm/ja/items/8824510)、[ぷろふぁむ](https://booth.pm/ja/items/8183172)、[クロエ](https://booth.pm/ja/items/6272301)、[春うさぎ](https://booth.pm/ja/items/8087217)、[綴よだか](https://booth.pm/ja/items/3822052)、[ロマンディ](https://booth.pm/ja/items/4036136)、[SAKURA](https://booth.pm/ja/items/4592729)、[雪音りう](https://booth.pm/ja/items/8519166)、[みやまる](https://booth.pm/ja/items/6867490)。

**収録保留**：初音ミクなど第三者IPのファンモデルは権利元公式の配布ではないため、作者配布だけを根拠として今回は採録しない。VRoidアクセサリー、ポーズ集、VRM変換ツールもVRMモデルそのものではないので対象外。

BOOTHの0円掲載を根拠とするが、ログイン後のダウンロード、期間限定商品の公開継続、ZIP内部構成は未検証。Hermesによる一括実機検証時は `/mnt/hdd/vrm` に原本を保存する。

## 2026-10-08 無料VRM配布追加（35件）

BOOTHの商品ごとに「ダウンロード商品 ¥0」とVRM本体の配布案内を確認して収録（581→616）。前回と同様、ダウンロード・ZIP内部の検証は未実施。詳細は `data/models.json` を参照。

- [七百屋 vol.1](https://booth.pm/ja/items/4935982) — 無料ZIP中のアクアマリン、アメトリン、ルベライト、ペリドットを4件として登録。VRM 0.xと公式表記。
- [マシェリ](https://booth.pm/ja/items/4921493) — セーラー版・子うさぎ版の無料VRM 2件。有料の編集用モデルは対象外。
- [Openpose](https://booth.pm/ja/items/4716893) — 作者配布の0円ZIPを1件。[Openpose Full](https://booth.pm/ja/items/5451378) — 別作者の改変モデルをVRM 1.0・0.xの2件として収録（クレジット義務あり。元モデルとのライセンス関係は追加検証）。
- [あいすくん](https://booth.pm/ja/items/5950129)と[冬版](https://booth.pm/ja/items/6419264)、[VOLO](https://booth.pm/ja/items/6139844)、[魔法少女すもも](https://booth.pm/ja/items/8925032) — 軽量モデル・ボクセルアバター。
- [ドールシープ](https://booth.pm/ja/items/4875752)、[杏](https://booth.pm/ja/items/5182153)、[ルル](https://booth.pm/ja/items/3372986)、[口遊いろは](https://booth.pm/ja/items/2349118)、[Diva](https://booth.pm/ja/items/5808954)、[Mira](https://booth.pm/ja/items/7982191)、[竹燕](https://booth.pm/ja/items/8629412) — 公式作者の無料VRM。
- [ダークあいす](https://booth.pm/ja/items/8173063) — 作者オリジナル色違いのVRM 0.x／1.0を2件。
- [たわショップ](https://booth.pm/ja/items/5408796)、[みうこーショップ](https://booth.pm/ja/items/4150766)、[Yozora Neko](https://booth.pm/ja/items/5739237)、[si0JK_NEMU](https://booth.pm/ja/items/5969706)、[teoteome](https://booth.pm/ja/items/2453106) — その他の作者配布アバター。
- [美和子さん](https://booth.pm/ja/items/2328802)、[泉淳也](https://booth.pm/ja/items/8012631) — 公式作者がVRM形式を明示した無料配布物。

**引き続き保留**：[七百屋 vol.3](https://booth.pm/ja/items/4937868) は共通商品ページが0円と案内するもののショップ固有URLが「非公開中」と表示されるため、今回の追加対象外。VRMモデルの現物を明記していないアプリ、変換ツール、第三者IPのファンモデルも対象外。

ファイル原本は収録拡充後、Hermes Agentによる実機確認時に `/mnt/hdd/vrm` へ保存する。

## 新規CC0コレクションと作者BOOTH無料VRM（2026-10-08）

616→659件（+43件）に拡充。原作者配布元を追加し、既存のPolygonal Mind 400件に偏らないようにした。

### MJMoonbow（18件）

- [VRMavatars](https://github.com/MJMoonbow/VRMavatars) の作者READMEとCC0 1.0 LICENSEを確認。GitHubツリーに `.vrm` 23パスがあるうち、**5ファイルは2バイトしかなくVRMとして成立しないため除外**。それ以外の18ファイルの正確なパスとGitHub上のバイト数を `data/collections/mjmoonbow-fantasy.json` に記録。
- 原作者側がCC0と表明していることを根拠に採録。実ファイル内部・VRM仕様バージョン・レンダリングは未確認。

### BOOTH（25件）

- [Kado購買部フロウ](https://booth.pm/ja/items/8118323)：薄型、Ver.2の軽量・Perfect Sync、Ver.3通常・Perfect Sync・アウターなし2種、メモリアル版2種の9件。モデル単体と同じモデルを含むZIPは重複カウントせず、アウターなし版は「コンプリート版.zip」を配布元として記録。
- [彩瞳 Ayame](https://booth.pm/ja/items/3126282)：VRMセットの新旧2件。商品名Ver.1/2はVRM規格の0.x/1.0を意味しないため `vrm_version=null`。
- [ほしうさ](https://booth.pm/ja/items/2556708)：作者が2026年に無料再公開した旧アバター（くろ・ピンク）2件。[ぜろに](https://booth.pm/ja/items/6952609)：VRM 0.xの小型モデル。
- [リウォレ](https://booth.pm/ja/items/4458219)：無料の同一ZIPに `Normal_01.vrm`、`Normal_02.vrm`、`Rop_01.vrm`、`Rop_02.vrm` を公式記載し4件。
- [N](https://booth.pm/ja/items/6315693)、[△256穴子](https://booth.pm/ja/items/3983431)、[ぷち尚也／ぷち柚希](https://booth.pm/ja/items/6594471)、[紬たか](https://booth.pm/ja/items/3537750)、[PURIN／PURIN+](https://booth.pm/ja/items/5082441)も無償配布として登録。

**保留**：配布名にVRMとある衣装・髪型のセットなど、モデル本体が含まれるか不明な商品は除外。第三者が制作したモデルの二次配布や非公開モデル、作者の許可が未確認な場合も保留する。購入不要であることは実ダウンロード成功と同義ではなく、後日のHermes実機確認で取得可否を確認し、原本を `/mnt/hdd/vrm` に保存する。

## 2026-10-08 追加収録：無料VRM配布27件

659→686件（+27件）。すべて配布者本人のBOOTH商品ページで0円のVRM本体またはVRM収録ZIPを確認。実ダウンロード・ZIP内部の全ファイル名・VRM仕様バージョンは未確認のまま、`data/models.json` に収録した。

- [桜夜 Sakuya](https://booth.pm/ja/items/5513788)：作者が無料のVer.2／Ver.3.1 VRM ZIPを別々に公開（2件）。VRM仕様バージョンと作者の商品更新版番号は区別。
- [Hatsuka](https://booth.pm/ja/items/3871143)：作者がPC用とQuest用の異なるVRMを明記（2件）。[鳥アバター](https://booth.pm/ja/items/5444666)：鳥8とテクスチャ改良版の別VRM（2件）。
- [たぬきおにぎり](https://booth.pm/ja/items/7239598)：具切替対応VRMと「単体のもの」を同梱と説明（2件）。**単体版が別VRMとして独立しているかはZIP未解析につき要検証**。同一取得物の重複計上にならないか確認する。
- [Quanstella](https://booth.pm/ja/items/5922294)、[Lua](https://booth.pm/ja/items/7682427)、[UMEKO](https://booth.pm/ja/items/2152422)、[さよ](https://booth.pm/ja/items/7185501)、[花圓](https://booth.pm/ja/items/4649018)、[あにゃめ](https://booth.pm/ja/items/6013393) の作者配布VRM（6件）。
- [ほねまる家](https://booth.pm/ja/items/6530666)、[小動物系少女](https://booth.pm/ja/items/5094429)、[ゆるねこ](https://booth.pm/ja/items/8734821)、[たけぴよ](https://booth.pm/ja/items/5599857)、[なお](https://booth.pm/ja/items/6595645)、[こたつみかん](https://booth.pm/ja/items/6686224)、[もやし](https://booth.pm/ja/items/6859520) の作者配布VRM（7件）。
- [普通の女の子アバター](https://booth.pm/ja/items/7392963)、[刃切 切乃](https://booth.pm/ja/items/6100467)、[323](https://booth.pm/ja/items/4637936)、[ねこみみキャラ（白）](https://booth.pm/ja/items/5305879)、[熊野ゆちゃ](https://booth.pm/ja/items/7039529)、[鬼の子キリ](https://booth.pm/ja/items/5189443) の作者配布VRM（6件）。ねこみみキャラは期間限定無料として扱い、次回以降の公開継続を確認する。

共通注意：**無料配布は商用利用・再配布の自由を保証しない**。商品本文以外の同梱利用規約が存在する場合は後日の原本確認で照合する。原本保存と描画テストは登録件数拡充後、Hermes Agentが `/mnt/hdd/vrm` で一括実施し、GitHubにVRM/ZIP原本をコミットしない。

## 2026-10-08 無料VRM追加（686→729・43件）

BOOTHの商品ページで作者自身の0円ダウンロード商品、配布ファイル名およびVRM形式を照合し、`data/models.json` に43件追加。ZIP内の実ファイル名・GLBヘッダー・使用許諾のメタデータ・正常な表示は未確認（`official_free_distribution_listed_download_untested`）。

- [柊依屋](https://booth.pm/ja/items/6323296) **8件**：海羽Miu（通常/Perfect Sync）、[琴華Kotoha](https://booth.pm/ja/items/5943036)（通常/Perfect Sync）、[梓乃Shino](https://booth.pm/ja/items/5659808)（2配布ZIP）、[杏澄Asumi](https://booth.pm/ja/items/5776856)（2配布ZIP）。無料のVRM-only版のみ収録。有料のVRoid・VRChat同梱版は対象外。通常/PSの具体的な内部パスや各ZIP内の追加バリエーションは実取得時に要確認。
- [桜美堂](https://booth.pm/ja/items/5375274) **6件**：ブルーベル、[めいめい](https://booth.pm/ja/items/6516048)、[かみや](https://booth.pm/ja/items/6046175)、[みるっち](https://booth.pm/ja/items/5715397)、[めぐみっち](https://booth.pm/ja/items/5689713)、[まきのっち](https://booth.pm/ja/items/5597575)。VRM入り無料ZIPを収録。モデル個別にVTuber利用・クレジット義務などの違いがあるため一律のライセンスとは扱わない。
- [くらんも](https://booth.pm/ja/items/4150979) **4件**：クラゲ通常色の頭ゆれあり／なし2VRM、[弓使いエルフ](https://booth.pm/ja/items/5775364)と[魔法使いエルフ](https://booth.pm/ja/items/5775339)。無料クラゲの同一 `kurage-f.zip` が別商品ページにも掲載されているが重複登録しない。エルフのVTuber利用・改変制限に注意。
- [Mujo Moroyuki ぴえんシリーズ](https://booth.pm/ja/items/5389330) **7件**：ぴえん、ぴえ子、トゥクン、ぐすん、しょぼん、ぎゃふん、どきん。作者説明は無料ZIP内の7 VRMと明記。ファイル名はZIPのみを記録。
- [ペンギンのきゅうり屋さん バレンタインミミック](https://booth.pm/ja/items/5463323) **4件**：通常色・青・金・黒の直接配布 `.vrm`。無料の共通ZIPには同じモデルが入るため重複計上しない。
- [たこやきちゃん／あかしやきくん](https://booth.pm/ja/items/5960078) **2件**：同じVRM.zipを共有。[はんぺん／樫豆腐](https://booth.pm/ja/items/4671530) **2件**：直接VRM 2ファイル。いずれも作者による0円商品。
- [Renga Works Mira](https://booth.pm/ja/items/8684534)、[煌星](https://booth.pm/ja/items/4291108)、[ファラオ](https://booth.pm/ja/items/8629608) **3件**：MiraはVRM 1.0で、2026-08-11に不具合修正差し替えの説明がある。煌星はVRM 0.0で商用利用不可。
- [JIMA_3D](https://booth.pm/ja/items/8737858) **3件**：マッスル鳩（VRM 0.x）、[中年太りマーモット](https://booth.pm/ja/items/8806174)（VRM 1.0）、[マッスルカマキリ](https://booth.pm/ja/items/8768066)（VRM 1.0）。同ショップの有料商品は対象外。作者説明のVRM内部ファイル名と配布ZIPの名前は分けて扱う。
- [とりのともしび](https://booth.pm/ja/items/4226437) **3件**：赤・緑・青の3 VRM。改変元[たびマル倉庫「とり」](https://booth.pm/ja/items/3898075)の制作者から再配布許可を得た旨が商品説明にある。ただし許諾原文は未確認。今後の実機確認時に規約の現行性も検証。
- [めいどちゃん](https://booth.pm/ja/items/2593934) **1件**：従来登録の通常／黒服以外に、作者説明に第三のVRM（素体・髪アクセ付き）が明記されているため追加。

**残課題**：配布ZIPの正確なVRM数・内部ファイル名、変更された有料／無料の価格、表示・動作、各モデルの利用規約ファイル。無料公開の有無だけで検証済みとせず、増件終了後にHermes Agentで一括実取得・検証し、原本を `/mnt/hdd/vrm` に永続保存する。
