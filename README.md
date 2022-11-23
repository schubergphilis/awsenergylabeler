# AWSEnergyLabeler

This repository contains the lambda code to run the AWSEnergyLabeler in AWS Lambda.

To make the deployment as easy as possible, [Chalice](https://github.com/aws/chalice) is used. This automates most of the process.

## TL;DR
```
git clone https://github.com/schubergphilis/awsenergylabeler.git
cd awsenergylabeler
pipx install chalice
cp .chalice/config_example_single.json .chalice/config.json
cp .chalice/EnergyLabelerPolicy_example.json .chalice/EnergyLabelerPolicy.json
# <EDIT BOTH CONFIG FILES>
chalice deploy --stage prod
```

## Scope of the labeler
Normally speaking, you're managing an entire AWS Landing Zone. This should include a dedicated Audit account, where all SecurityHub findings are centrally gathered. The EnergyLabeler is designed to run in your Audit account, so findings from all accounts can be retrieved and scored accordingly. The EnergyLabeler will calculate a score per account and an over-all score for the entire Landing Zone.

### Single account
In certain cases you might not have access to the Audit account (in a different responsibility/engagement model). For these cases the possibility exists to run the EnergyLabeler in a "single account" mode. In this mode, only the account where the lambda runs will be scored. This method should only be used if running on the entire Landing Zone is impossible.

## Getting started
In order to get started, we need to prepare your environment.

### Prepare local environment
Start by cloning [this repository](https://github.com/schubergphilis/awsenergylabeler) and install the chalice python module. You can use `pipx` if you're familiar with it, this ensures that Chalice is installed in it's own virtual environment, not impacting other python packages. Read more about pipx [here](https://github.com/pypa/pipx).

```
git clone https://github.com/schubergphilis/awsenergylabeler.git
cd awsenergylabeler
pipx install chalice
```

You should now have your environment set up.

### Configure deployment
Before starting to deploy, a couple of variables need to be set in the configuration.


#### Organizations Zone
To set up the EnergyLabeler for your Landing Zone create a `config.json` and use the `config_example_single.json` as a starting point. Fill in all details for your environment in the environment variables on lines 6 to 10.
```json
     "environment_variables": {
        "AWS_LABELER_AUDIT_ZONE_NAME": "AUDITZONE",
        "AWS_LABELER_REGION": "eu-west-1",
        "AWS_LABELER_EXPORT_PATH": "s3://bucket/team/"
      }
```

At least the following variables need to be set:
* AWS_LABELER_ORGANIZATIONS_ZONE_NAME
* AWS_LABELER_REGION
* AWS_LABELER_EXPORT_PATH

Make sure that line 15 `"iam_policy_file": "EnergyLabelerPolicy_example.json"` refers to the policy you'll create next.

Next, also copy the `EnergyLabelerPolicy_example.json` to create `EnergyLabelerPolicy.json`. Make sure to update the S3 bucket resources on line 10 to 12.
```json
      "Resource": [
        "arn:aws:s3:::bucket/team/*",
        "arn:aws:s3:::bucket/team"
      ]
```

#### Audit zone and single account
To set up the EnergyLabeler for an audit zone or a single account create a `config.json` and use the `config_example_single.json` as a starting point. Fill in all details for your environment in the environment variables on lines 6 to 10.

```json
      "environment_variables": {
        "SINGLE_ACCOUNT_ID": "123456789012",
        "REGION": "eu-west-1",
        "EXPORT_PATH": "s3://bucket/team/"
      }
```

At least the following variables need to be set:
* AWS_LABELER_AUDIT_ZONE_NAME or AWS_LABELER_SINGLE_ACCOUNT_ID	
* AWS_LABELER_REGION
* AWS_LABELER_EXPORT_PATH

Make sure that line 15 `"iam_policy_file": "EnergyLabelerPolicy_example.json"` refers to the policy you'll create next.

Next, also copy the `EnergyLabelerPolicySingle_example.json` to create `EnergyLabelerPolicy.json`. Make sure to update the S3 bucket resources on line 10 to 12.
```json
      "Resource": [
        "arn:aws:s3:::bucket/team/*",
        "arn:aws:s3:::bucket/team"
      ]
```

#### Arguments
Every command line argument is also reflected in an environment variable which gives flexibility. Command line arguments take precedence over environment variables.
| Environment variable name               | CLI Argument                          | Required                                                                                                               | Example value                                      | Description                                                                                                                                                                                                                                                                                                                                                                                                                 |
|-----------------------------------------|---------------------------------------|------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| AWS_LABELER_LOG_CONFIG                  | `--log-config` `-l`                   | No                                                                                                                     | ~/log_config.json (default: `None`)                | The location of the logging config json file                                                                                                                                                                                                                                                                                                                                                                                |
| AWS_LABELER_LOG_LEVEL                   | `--log-level` `-L`                    | No                                                                                                                     | info (default)                                     | Provide the log level. Defaults to info.                                                                                                                                                                                                                                                                                                                                                                                    |
| AWS_LABELER_ORGANIZATIONS_ZONE_NAME     | `--organizations-zone-name` `-o`      | Either AWS_LABELER_ORGANIZATIONS_ZONE_NAME or AWS_LABELER_AUDIT_ZONE_NAME or AWS_LABELER_SINGLE_ACCOUNT_ID is required | TEST (default: `None`)                             | Name of the organizations zone being scored. This variable is mutually exclusive with SINGLE_ACCOUNT_ID and AWS_LABELER_AUDIT_ZONE_NAME                                                                                                                                                                                                                                                                                     |
| AWS_LABELER_AUDIT_ZONE_NAME             | `--audit-zone-name` `-z`              | Either AWS_LABELER_ORGANIZATIONS_ZONE_NAME or AWS_LABELER_AUDIT_ZONE_NAME or AWS_LABELER_SINGLE_ACCOUNT_ID is required | TEST (default: `None`)                             | Name of the audit zone being scored. This variable is mutually exclusive with SINGLE_ACCOUNT_ID and AWS_LABELER_ORGANIZATIONS_ZONE_NAME                                                                                                                                                                                                                                                                                     |
| AWS_LABELER_SINGLE_ACCOUNT_ID           | `--single-account-id` `-s`            | Either AWS_LABELER_ORGANIZATIONS_ZONE_NAME or AWS_LABELER_AUDIT_ZONE_NAME or AWS_LABELER_SINGLE_ACCOUNT_ID is required | 123456789102 (default: `None`)                     | The AWS Account ID of the single account to score. This should only be used if scoring the entire landing zone is not an option.                                                                                                                                                                                                                                                                                            |
| AWS_LABELER_REGION                      | `--region` `-r`                       | Yes                                                                                                                    | `eu-west-1` (default)                              | The main region to run the labeler from                                                                                                                                                                                                                                                                                                                                                                                     |
| AWS_LABELER_FRAMEWORKS                  | `--frameworks` `-f`                   | No                                                                                                                     | aws-foundational-security-best-practices (default) | The frameworks to include in the score                                                                                                                                                                                                                                                                                                                                                                                      |
| AWS_LABELER_ALLOWED_ACCOUNT_IDS         | `--allowed-account-ids` `-a`          | No                                                                                                                     | 123456789102,123456789103 (default: `None`)        | A list of account IDs that should be scored. No accounts will be scored EXCEPT for accounts in this list. This variable is mutually exclusive with DENIED_ACCOUNT_IDS                                                                                                                                                                                                                                                       |
| AWS_LABELER_DENIED_ACCOUNT_IDS          | `--denied-account-ids` `-d`           | No                                                                                                                     | 123456789102,123456789103 (default: `None`)        | A list of account IDs that should NOT be scored. All accounts will be scored EXCEPT accounts in this list. This variable is mutually exclusive with ALLOWED_ACCOUNT_IDS                                                                                                                                                                                                                                                     |
| AWS_LABELER_ALLOWED_REGIONS             | `--allowed-regions` `-ar`             | No                                                                                                                     | eu-west-1,eu-central-1 (default: `None`)           | A list of regions that should be included. No regions will be included EXCEPT for regions in this list. This variable is mutually exclusive with DENIED_REGIONS                                                                                                                                                                                                                                                             |
| AWS_LABELER_DENIED_REGIONS              | `--denied-regions` `-dr`              | No                                                                                                                     | eu-west-1,eu-central-1 (default: `None`)           | A list of regionss that should NOT be included. All regions will be included EXCEPT regions in this list. This variable is mutually exclusive with ALLOWED_REGIONS                                                                                                                                                                                                                                                          |
| AWS_LABELER_EXPORT_PATH                 | `--export-path` `-p`                  | Yes if `export metrics` or `export all` is true                                                                        | /tmp/aws_output (default: `None`)                  | The location where the output can be stored.                                                                                                                                                                                                                                                                                                                                                                                |
| AWS_LABELER_EXPORT_METRICS              | `--export-metrics-only` `-e`          | No                                                                                                                     | `False` (default)                                  | Exports metrics/statistics without sensitive findings data in JSON formatted files to the specified directory or S3 location.                                                                                                                                                                                                                                                                                               |
| AWS_LABELER_TO_JSON                     | `--to-json` `-j`                      | No                                                                                                                     | `False` (default)                                  | Return the report in json format.                                                                                                                                                                                                                                                                                                                                                                                           |
| AWS_LABELER_REPORT_CLOSED_FINDINGS_DAYS | `--report-closed-findings-days` `-rd` | No                                                                                                                     | `False` (default: `None`)                          | If set the report will contain info on the number of findings that were closed during the provided days count                                                                                                                                                                                                                                                                                                               |
| AWS_LABELER_REPORT_SUPPRESSED_FINDINGS  | `--report-suppressed-findings` `-rs`  | No                                                                                                                     | `False` (default)                                  | If set the report will contain info on the number of suppressed findings                                                                                                                                                                                                                                                                                                                                                    |
| AWS_LABELER_ACCOUNT_THRESHOLDS          | `--account-thresholds` `-at`          | No                                                                                                                     | `JSON` (default: `None`)                           | If set the account thresholds will be used instead of the default ones. Usage of this option will be reported on the report output and the metadata file upon export.                                                                                                                                                                                                                                                       |
| AWS_LABELER_ZONE_THRESHOLDS             | `--zone-thresholds` `-zt`             | No                                                                                                                     | `JSON` (default: `None`)                           | If set the zone thresholds will be used instead of the default ones. Usage of this option will be reported on the report output and the metadata file upon export.                                                                                                                                                                                                                                                          |
| AWS_LABELER_SECURITY_HUB_QUERY_FILTER   | `--security-hub-query-filter` `-sf`   | No                                                                                                                     | `JSON` (default: `None`)                           | If set, this filter will be used instead of the default built in. Usage of this option will be reported on the report output and the metadata file upon export. Usage of the allowed ips and denied ips options will still affect the filter as well as the default set frameworks. If no framework filtering is needed the built in default frameworks can be overriden by calling the "-f" option with "" as an argument. |

## Deployment
To deploy the EnergyLabeler after creating and configuring the `config.json` file, you can run Chalice to deploy everything required.
Make sure your local environment has AWS credentials set up to use from the command line. You can use AWS SSO or  [saml2aws](https://github.com/Versent/saml2aws) for example.

```
chalice deploy --stage prod
```

After this is done you should see some new resources being created in your environment:
* IAM Role
* Lambda function
* Eventbridge (CloudwatchEvents)

## Manual actions
A last action that needs to be performed is in the receiving S3 bucket.
The S3 bucket policy needs to allow PutObject by the role created by Chalice. If you are not the owner of the bucket, reach out to the owner to get the permissions set up. 

The policy should look something like the following, pay attention to line 5 for the role name, and lines 15 to 18 for the specific folder in the bucket.
```json
{
            "Sid": "Statement1",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:role/RoleName"
            },
            "Action": [
                "s3:AbortMultipartUpload",
                "s3:ListBucketMultipartUploads",
                "s3:ListMultipartUploadParts",
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::bucket",
                "arn:aws:s3:::bucket/team/*"
            ]
        }
```

## Testing
To test if everything works as expected, a test event can be triggered. This test event needs to mimic an EventBridge event such as the one below.
```json
{
  "id": "53dc4d37-cffa-4f76-80c9-8b7d4a4d2eaa",
  "detail-type": "Scheduled Event",
  "source": "aws.events",
  "account": "123456789012",
  "time": "2019-10-08T16:53:06Z",
  "region": "eu-west-1",
  "resources": [ "arn:aws:events:eu-west-1:123456789012:rule/MyScheduledRule" ],
  "detail": {},
  "version": ""
}
```