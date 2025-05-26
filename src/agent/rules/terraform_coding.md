# Terraformコーディング規約

## 1. 参照リソース
Snowflakeのterraformリソースを作成する場合は、以下のファイルを必ず参照してください：
- `terraform/snowflake/modules/`配下の`terraform-docs`
- `terraform/snowflake/environments/dsol_sandbox/`配下の`.tf`ファイル

## 2. モジュール使用ルール
### 2.1 必ずモジュールを使用するリソース（最優先）
1. 以下のリソースを作成する場合は、**必ず既存のモジュールを使用**してください：
    - `human-user`
    - `service-user`
    - `functional-role`
    - `service-role`
    - `personal-workspace`

2. terraform moduleはバージョンは最新のバージョンを使ってください

### 2.2 モジュールを使用しないリソース
以下のリソースを作成する場合は、**モジュールを使わず直接リソースを定義**してください：
- `database`作成
- `storage-integration`作成

## 3. コード生成指針
- 上記ルールを厳守したTerraformコードを生成してください
- 既存の命名規則や構造に従ってください
- 既存のコードベースと一貫性のあるコードを作成してください
- コメントアウトは必要ありません
