# プロンプトテンプレートの定義
PROGRAMMER_PROMPT_TEMPLATE = """
あなたは 'src/' ディレクトリをルートとするPythonプロジェクトのプログラマーエージェントです。
以下のユーザー指示に従ってファイルを編集してください。

必要に応じて以下のツールを活用してタスクを実行してください：
- GetFilesList：プロジェクト内のファイル一覧を取得する
- ReadFile：ファイルの内容を読む
- MakeNewFile：新しいファイルを作成する
- OverwriteFile：既存ファイルを上書きする
- ExecRspecTest：RSpecテストを実行する
- GeneratePullRequestParams：PR作成に必要な情報を生成する
- RecordLgtm：LGTM（レビュー承認）を記録する

ユーザーからの指示: 
{instruction}
"""

# エージェントのシステムメッセージ
AGENT_SYSTEM_MESSAGE = """あなたはプロフェッショナルなプログラミングアシスタントです。
ユーザーの指示に基づき、プロジェクト（ルートはq src/）の中で、適切なツールを組み合わせて
コーディング、ファイル操作、テスト実行、情報収集などを行い、目的達成を支援してください。

- 実行の前には、まず必要な情報を把握し、ツール選定と段階的な実行を行ってください。
- ディレクトリを指定された場合は、必ずどこにそのディレクトリがあるかを確認してください。
一貫性と再現性のある、正確なコード操作を心がけてください。
"""

# モジュール別READMEファイル内容
USER_HUMAN_DOCS = r"""
<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_snowflake"></a> [snowflake](#requirement\_snowflake) | ~> 1.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_snowflake"></a> [snowflake](#provider\_snowflake) | ~> 1.0 |

## Resources

| Name | Type |
|------|------|
| [snowflake_grant_account_role.granted_account_roles](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/grant_account_role) | resource |
| [snowflake_network_policy.user_policy](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/network_policy) | resource |
| [snowflake_user.main](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/user) | resource |
| [snowflake_user_authentication_policy_attachment.user_policy](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/user_authentication_policy_attachment) | resource |
| [snowflake_user_password_policy_attachment.attachment](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/user_password_policy_attachment) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_allowed_ip_list"></a> [allowed\_ip\_list](#input\_allowed\_ip\_list) | The list of allowed IP addresses for the user | `list(string)` | n/a | yes |
| <a name="input_authentication_policy_name"></a> [authentication\_policy\_name](#input\_authentication\_policy\_name) | The name of the authentication policy to attach to the user | `string` | `""` | no |
| <a name="input_blocked_ip_list"></a> [blocked\_ip\_list](#input\_blocked\_ip\_list) | The list of blocked IP addresses for the user | `list(string)` | n/a | yes |
| <a name="input_email"></a> [email](#input\_email) | The email of the user to create | `string` | n/a | yes |
| <a name="input_first_name"></a> [first\_name](#input\_first\_name) | The first name of the user to create | `string` | n/a | yes |
| <a name="input_granted_account_roles"></a> [granted\_account\_roles](#input\_granted\_account\_roles) | The account roles to grant to the role | `list(string)` | `[]` | no |
| <a name="input_last_name"></a> [last\_name](#input\_last\_name) | The last name of the user to create | `string` | n/a | yes |
| <a name="input_must_change_password"></a> [must\_change\_password](#input\_must\_change\_password) | Whether the user must change their password on first login | `string` | `"true"` | no |
| <a name="input_password_policy"></a> [password\_policy](#input\_password\_policy) | The password policy to attach to the user | `string` | n/a | yes |
| <a name="input_rsa_public_key"></a> [rsa\_public\_key](#input\_rsa\_public\_key) | The RSA public key for the user | `string` | `""` | no |
| <a name="input_rsa_public_key_2"></a> [rsa\_public\_key\_2](#input\_rsa\_public\_key\_2) | The second RSA public key for the user | `string` | `""` | no |
| <a name="input_user_name"></a> [user\_name](#input\_user\_name) | The name of the user to create. unique identifier for the user | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_human_user_name"></a> [human\_user\_name](#output\_human\_user\_name) | n/a |
<!-- END_TF_DOCS -->
"""

USER_SYSTEM_DOCS = r"""
<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_snowflake"></a> [snowflake](#requirement\_snowflake) | ~> 1.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_snowflake"></a> [snowflake](#provider\_snowflake) | ~> 1.0 |

## Resources

| Name | Type |
|------|------|
| [snowflake_grant_account_role.granted_account_roles](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/grant_account_role) | resource |
| [snowflake_legacy_service_user.service_legacy_user](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/legacy_service_user) | resource |
| [snowflake_network_policy.user_policy](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/network_policy) | resource |
| [snowflake_service_user.service_user](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/service_user) | resource |
| [snowflake_user_authentication_policy_attachment.attachment](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/user_authentication_policy_attachment) | resource |
| [snowflake_user_password_policy_attachment.attachment](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/user_password_policy_attachment) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_allowed_ip_list"></a> [allowed\_ip\_list](#input\_allowed\_ip\_list) | The list of allowed IP addresses for the user | `list(string)` | `[]` | no |
| <a name="input_authentication_policy_name"></a> [authentication\_policy\_name](#input\_authentication\_policy\_name) | The name of the authentication policy to attach to the user | `string` | `""` | no |
| <a name="input_blocked_ip_list"></a> [blocked\_ip\_list](#input\_blocked\_ip\_list) | The list of blocked IP addresses for the user | `list(string)` | `[]` | no |
| <a name="input_granted_account_roles"></a> [granted\_account\_roles](#input\_granted\_account\_roles) | The account roles to grant to the role | `list(string)` | `[]` | no |
| <a name="input_is_legacy_user"></a> [is\_legacy\_user](#input\_is\_legacy\_user) | service userをtype = legacyで作成するかどうか | `bool` | `false` | no |
| <a name="input_password_policy_name"></a> [password\_policy\_name](#input\_password\_policy\_name) | The password policy to attach to the user | `string` | `""` | no |
| <a name="input_rsa_public_key"></a> [rsa\_public\_key](#input\_rsa\_public\_key) | The RSA public key for the user | `string` | `""` | no |
| <a name="input_rsa_public_key_2"></a> [rsa\_public\_key\_2](#input\_rsa\_public\_key\_2) | The second RSA public key for the user | `string` | `""` | no |
| <a name="input_user_name"></a> [user\_name](#input\_user\_name) | The name of the user to create | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_service_user_name"></a> [service\_user\_name](#output\_service\_user\_name) | n/a |
<!-- END_TF_DOCS -->
"""

ROLE_WAREHOUSE_DOCS = r"""
<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_snowflake"></a> [snowflake](#requirement\_snowflake) | ~> 1.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_snowflake"></a> [snowflake](#provider\_snowflake) | ~> 1.0 |

## Resources

| Name | Type |
|------|------|
| [snowflake_account_role.main](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/account_role) | resource |
| [snowflake_grant_account_role.sysadmin](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/grant_account_role) | resource |
| [snowflake_grant_database_role.granted_database_roles](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/grant_database_role) | resource |
| [snowflake_grant_privileges_to_account_role.grant_usage_external_volume](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/grant_privileges_to_account_role) | resource |
| [snowflake_grant_privileges_to_account_role.grant_usage_integration](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/grant_privileges_to_account_role) | resource |
| [snowflake_grant_privileges_to_account_role.snowpark_optimized](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/grant_privileges_to_account_role) | resource |
| [snowflake_grant_privileges_to_account_role.standard](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/grant_privileges_to_account_role) | resource |
| [snowflake_grant_privileges_to_account_role.view_lineage](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/grant_privileges_to_account_role) | resource |
| [snowflake_resource_monitor.minimal](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/resource_monitor) | resource |
| [snowflake_warehouse.snowpark_optimized](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/warehouse) | resource |
| [snowflake_warehouse.standard](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/warehouse) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_enable_view_lineage"></a> [enable\_view\_lineage](#input\_enable\_view\_lineage) | Whether to enable the VIEW LINEAGE privilege for the role | `bool` | `false` | no |
| <a name="input_env"></a> [env](#input\_env) | The environment to create the service / functional role in | `string` | n/a | yes |
| <a name="input_external_integration_usages"></a> [external\_integration\_usages](#input\_external\_integration\_usages) | A list of integrations for which usage permissions can be granted. Required for iceberg table operations as storage integration usage is needed | `list(string)` | `[]` | no |
| <a name="input_external_volume_usages"></a> [external\_volume\_usages](#input\_external\_volume\_usages) | List of external\_volumes that can be granted usage permissions. Required for iceberg table operations as external volume usage is needed | `list(string)` | `[]` | no |
| <a name="input_granted_database_roles"></a> [granted\_database\_roles](#input\_granted\_database\_roles) | The database roles to grant to the service / functional role | `list(string)` | `[]` | no |
| <a name="input_resource_monitor_credit_quota"></a> [resource\_monitor\_credit\_quota](#input\_resource\_monitor\_credit\_quota) | The credit quota for the resource monitor | `number` | `0` | no |
| <a name="input_resource_monitor_notify_users"></a> [resource\_monitor\_notify\_users](#input\_resource\_monitor\_notify\_users) | The users to notify when the resource monitor is exceeded | `list(string)` | `[]` | no |
| <a name="input_role_name"></a> [role\_name](#input\_role\_name) | The name of the service / functional role to create | `string` | n/a | yes |
| <a name="input_role_type"></a> [role\_type](#input\_role\_type) | The type of the service / functional role to create | `string` | n/a | yes |
| <a name="input_snowpark_optimized_warehouse_size"></a> [snowpark\_optimized\_warehouse\_size](#input\_snowpark\_optimized\_warehouse\_size) | The size of the snowpark optimized warehouse to create | `list(string)` | `[]` | no |
| <a name="input_standard_warehouse_size"></a> [standard\_warehouse\_size](#input\_standard\_warehouse\_size) | The size of the warehouse to create | `list(string)` | <pre>[<br/>  "XSMALL"<br/>]</pre> | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_role_name"></a> [role\_name](#output\_role\_name) | n/a |
| <a name="output_warehouse_name_default"></a> [warehouse\_name\_default](#output\_warehouse\_name\_default) | n/a |
<!-- END_TF_DOCS -->
"""

SCHEMA_WITH_ROLE_DOCS = r"""
<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_snowflake"></a> [snowflake](#requirement\_snowflake) | ~> 1.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_snowflake"></a> [snowflake](#provider\_snowflake) | ~> 1.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_database_name"></a> [database\_name](#input\_database\_name) | name of database where schema will be created in | `string` | n/a | yes |
| <a name="input_enable_dynamic_table"></a> [enable\_dynamic\_table](#input\_enable\_dynamic\_table) | Enable dynamic table via access roles | `bool` | `false` | no |
| <a name="input_enable_external_table"></a> [enable\_external\_table](#input\_enable\_external\_table) | Enable external table via access roles | `bool` | `false` | no |
| <a name="input_enable_function"></a> [enable\_function](#input\_enable\_function) | Enable udf via access roles | `bool` | `false` | no |
| <a name="input_enable_iceberg_table"></a> [enable\_iceberg\_table](#input\_enable\_iceberg\_table) | Enable iceberg table via access roles | `bool` | `false` | no |
| <a name="input_enable_procedure"></a> [enable\_procedure](#input\_enable\_procedure) | Enable stored procedure via access roles | `bool` | `false` | no |
| <a name="input_enable_stage"></a> [enable\_stage](#input\_enable\_stage) | Enable stage via access roles | `bool` | `false` | no |
| <a name="input_enable_streamlit"></a> [enable\_streamlit](#input\_enable\_streamlit) | Enable streamlit in snowflake via access roles | `bool` | `false` | no |
| <a name="input_is_managed_schema"></a> [is\_managed\_schema](#input\_is\_managed\_schema) | Enable managed schema | `bool` | `true` | no |
| <a name="input_schema_log_level"></a> [schema\_log\_level](#input\_schema\_log\_level) | log level for schema | `string` | `""` | no |
| <a name="input_schema_name"></a> [schema\_name](#input\_schema\_name) | n/a | `string` | n/a | yes |
| <a name="input_schema_trace_level"></a> [schema\_trace\_level](#input\_schema\_trace\_level) | trace level for schema | `string` | `""` | no |
| <a name="input_stage_params"></a> [stage\_params](#input\_stage\_params) | n/a | `list(map(string))` | `[]` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_schema_name"></a> [schema\_name](#output\_schema\_name) | n/a |
<!-- END_TF_DOCS -->
"""

PERSONAL_WORKSPACE_DOCS = r"""
<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_snowflake"></a> [snowflake](#requirement\_snowflake) | ~> 1.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_snowflake"></a> [snowflake](#provider\_snowflake) | ~> 1.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_default_workspace_schema"></a> [default\_workspace\_schema](#module\_default\_workspace\_schema) | ../../schema-with-role/v1 | n/a |
| <a name="module_role_for_personal_workspace"></a> [role\_for\_personal\_workspace](#module\_role\_for\_personal\_workspace) | ../../role-warehouse-service-functional/v2 | n/a |

## Resources

| Name | Type |
|------|------|
| [snowflake_database.personal_workspace](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/database) | resource |
| [snowflake_grant_account_role.granted_account_roles](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/grant_account_role) | resource |
| [snowflake_grant_database_role.granted_database_roles_ownership_schema](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs/resources/grant_database_role) | resource |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_database_name"></a> [database\_name](#input\_database\_name) | The name of the database to create | `string` | `""` | no |
| <a name="input_granted_database_roles"></a> [granted\_database\_roles](#input\_granted\_database\_roles) | functional-roles that allow access to databases and schemas outside of the workspace. | `list(string)` | `[]` | no |
| <a name="input_resource_monitor_credit_quota"></a> [resource\_monitor\_credit\_quota](#input\_resource\_monitor\_credit\_quota) | The credit quota for the resource monitor | `number` | `0` | no |
| <a name="input_resource_monitor_notify_users"></a> [resource\_monitor\_notify\_users](#input\_resource\_monitor\_notify\_users) | The users to notify when the resource monitor is exceeded | `list(string)` | `[]` | no |
| <a name="input_snowpark_optimized_warehouse_size"></a> [snowpark\_optimized\_warehouse\_size](#input\_snowpark\_optimized\_warehouse\_size) | The size of the snowpark optimized warehouse to create | `list(string)` | `[]` | no |
| <a name="input_standard_warehouse_size"></a> [standard\_warehouse\_size](#input\_standard\_warehouse\_size) | The size of the warehouse to create | `list(string)` | <pre>[<br/>  "XSMALL"<br/>]</pre> | no |
| <a name="input_username"></a> [username](#input\_username) | The username to use workspace. usernames are capitalized and joined with \_ | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_database_name"></a> [database\_name](#output\_database\_name) | n/a |
<!-- END_TF_DOCS -->
"""


VALIDATOR_PROMPT_TEMPLATE_BASE = """
あなたはSnowflakeのリソース構成をバリデーションするエージェントです。
以下のユーザー指示に従って、必要に応じてツールを活用して構成に必要な情報を収集してください。

## 利用可能なツール一覧
- GetUserHumanFunction：humanユーザーの設定情報を取得（user_name, first_name, last_name, email, allowed_ip_list, blocked_ip_list, password_policy）
- GetUserSystemFunction：systemユーザーの設定情報を取得（user_name）
- GetInputSchemaRoleWarehouseFunction：ロールとWarehouseの関連情報を取得（role_name, role_type, env）
- GetSchemaWithRoleFunction：スキーマとロールの関連情報を取得（database_name, schema_name）
- GetInputSchemaPersonalWorkspaceFunction：個人ワークスペース用の入力スキーマを取得（username, database_name, granted_database_roles, resource_monitor_credit_quota, resource_monitor_notify_users, snowpark_optimized_warehouse_size, standard_warehouse_size）

## 各Moduleのドキュメント
[UserHuman]
{user_human_docs}
[UserSystem]
{user_system_docs}
[RoleWarehouse]
{role_warehouse_docs}
[SchemaWithRole]
{schema_with_role_docs}
[PersonalWorkspace]
{personal_workspace_docs}

## あなたの役割
- 与えられた構成名やユーザー名を元にリソース定義を取得
- 不足項目があれば明確に聞き返し、最終的に構成をPydanticモデル形式で出力
- 設定の整合性や標準ポリシーへの準拠状況を確認
- リソースに必要な情報についてはツールを用いて、取得する様にしてください。

## Snowflakeの前提知識
- "dsol-sandbox" は Snowflake 上の環境名として使われています。
- 設定対象がSnowflakeである場合、AWSやGCPでの操作は不要です。
- ユーザー作成の際には、humanユーザーとsystemユーザーの2種類が存在するので、確認してください。

## ユーザー指示
{instruction}
"""
