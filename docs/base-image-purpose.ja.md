# port-officeの目的と責務

port-officeはvPremisesが保守する、製品から独立したDockerベースイメージの正本です。製品リポジトリは公開済みのimmutable digestをFROMに指定し、製品固有の依存、設定、起動、データ、cloud権限は製品側で管理します。ベースの更新を採用する時期も利用側が決めます。

## 保守するもの

- OSベース: distro、上流image digest、CA trust、非root実行、作業directoryの共通契約。
- Runtimeベース: 必要性を確認したPython/Node等を別imageとして管理。OSだけが必要な利用者へruntimeやcompilerを強制しない。
- Build/配布: Docker Bakeを唯一の定義として、architecture・tag・上流digest・source revision・出力digestを記録。
- 受入: build、非root/TLS/指定runtimeの起動、SBOM・脆弱性検査と例外の期限、公開後のdigest/provenance照合。
- 保守: 上流support期間、更新PR、patch版の発行、旧版のdeprecated通知と利用側の明示的更新。

Frappe/Traefikの完成image、Terraformer/OpenTofu等の用途別toolbox、環境設定、Cloud account操作、秘密・tenant情報はこの正本の責務に含めません。旧ソースはGit履歴に保存し、現行のbuild/publish対象から撤去します。移管先を勝手に作成せず、必要な製品ownerが履歴から必要箇所を選択して管理します。

## 独立した運用

1. port-officeだけで公開sourceからbuild・受入できる。隣接checkout、private registry、中央CoelaReleaseへのアクセスは不要。
2. sourceのCIではimageをbuild/testし、レジストリへ公開しない。
3. 固定sourceと候補digestを確認後、ownerのGitHub Actionsで登録済みの配布先へ公開する。署名・SBOM・source provenanceとimmutable outputを照合する。
4. 利用側はdigestを固定して更新PRで受入。Docker socketやCloud資格情報、ベース更新の自動取り込みを要求しない。
5. 復旧は利用側が直前に受入したdigestへ戻す。既存公開版のtagを上書きして復旧しない。

## 物理配置

`images/`は保守するimageのDockerfile、`docker-bake.hcl`はbuild契約、`tests/`はimageの受入、`docs/`は用途・support・公開/更新手順です。各imageはOS/runtime/CPU platform、上流digest、非root UIDと作業directoryを一覧で示します。

初期imageの選定・検証結果はREADMEの現行catalogに反映します。歴史的な11target一覧は当時の記録であり、現行のサポート表として再利用しません。旧Terraformer不具合はDockerベースの受入条件から分離します。
