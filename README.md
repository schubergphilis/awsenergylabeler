# AWSEnergyLabeler

This repository contains the lambda code to run the AWSEnergyLabeler in AWS Lambda.

To make the deployment as easy as possible, [Chalice](https://github.com/aws/chalice) is used. This automates most of the process.

## TL;DR
```
git clone https://github.com/schubergphilis/awsenergylabeler.git
cd awsenergylabeler
pipx install chalice
cp config_example_single.json config.json
vim config.json
chalice deploy --stage prod
```

## Scope of the labeler
Normally speaking, you're managing an entire AWS Landing Zone. This should include a dedicated Audit account, where all SecurityHub findings are centrally gathered. The EnergyLabeler is designed to run in your Audit account, so findings from all accounts can be retrieved and scored accordingly. The EnergyLabeler will calculate a score per account and an over-all score for the entire Landing Zone.

### Single account
In certain cases you might not have access to the Audit account (in a different responsibility/engagement model). For these cases the possibility exists to run the EnergyLabeler in a "single account" mode. In this mode, only the account where the lambda runs will be scored. This method should only be used if running on the entire Landing Zone is impossble.

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


#### Landing Zone
To set up the EnergyLabeler for your Landing Zone create a `config.json` and use the `config_example_single.json` as a starting point. Fill in all details for your environment in the environment variables.

At least the following variables need to be set:
* LANDING_ZONE_NAME	
* REGION
* EXPORT_PATH

#### Single account
To set up the EnergyLabeler for a single account create a `config.json` and use the `config_example_single.json` as a starting point. Fill in all details for your environment in the environment variables.

At least the following variables need to be set:
* SINGLE_ACCOUNT_ID	
* REGION
* EXPORT_PATH

#### All environment variables
The following variables can/should be set:
|Environment variable name|Required|Default|Description|
|-------------------------|--------|-------|-----------|
|LANDING_ZONE_NAME|Either LANDING_ZONE_NAME or SINGLE_ACCOUNT_ID must be set|None|Name of the landing zone being scored. This variable is mutually exclusive with SINGLE_ACCOUNT_ID|
|SINGLE_ACCOUNT_ID|Either SINGLE_ACCOUNT_ID or LANDING_ZONE_NAME must be set|None|The AWS Account ID of the single account to score. This should only be used if scoring the entire landing zone is not an option.|
|REGION|Yes|None|The main region to run the labeler from|
|EXPORT_PATH|Yes|None|The location (must be an S3 bucket) where the output can be stored. Must be in the form of `s3://BUCKET_NAME/FOLDER_NAME/`|
|ALLOWED_ACCOUNT_IDS|No|None|A list[] of account IDs that should be scored. No accounts will be scored EXCEPT for accounts in this list. This variable is mutually exclusive with DENIED_ACCOUNT_IDS|
|DENIED_ACCOUNT_IDS|No|None|A list[] of account IDs that should NOT be scored. All accounts will be scored EXCEPT accounts in this list. This variable is mutually exclusive with ALLOWED_ACCOUNT_IDS|
|ALLOWED_REGIONS|No|None|A list[] of regions that should be included. No regions will be included EXCEPT for regions in this list. This variable is mutually exclusive with DENIED_REGIONS|
|DENIED_REGIONS|No|None|A list[] of regionss that should NOT be included. All regions will be included EXCEPT regions in this list. This variable is mutually exclusive with ALLOWED_REGIONS|
|LOG_LEVEL|No|INFO|The verbosity of logging. Can be any of `['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']`|

## Deployment
To deploy the EnergyLabeler after creating and configuring the `config.json` file, you can run Chalice to deploy everything required.
Make sure your local environment has AWS credentials set up to use from the command line. You can use [saml2aws](https://github.com/Versent/saml2aws) for example.

```
chalice deploy --stage prod
```

After this is done you should see some new resources being created in your environment:
* IAM Role
* Lambda function
* Eventbridge (CloudwatchEvents)

## Manual actions
A last action that needs to be performed is in the receiving S3 bucket.
The S3 bucket policy needs to allow PutObject by the role created by Chalice.