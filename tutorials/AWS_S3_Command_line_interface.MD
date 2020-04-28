## Introduction
Amazon provides a command line interface (CLI) for the AWS web services. Janelia Research Campus uses AWS S3 (Simple Storage Service) to
store all of the published FlyLight imagery, and you can easily use AWS CLI to search and download those files.

## Installation
First, you'll nned to install the AWS CLI on your computer. Follow Amazon's instructions: [https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html].

## Configuration
Janelia Research Campus' buckets are set up to enable anonymous access, so no configuration is needed. If you already have an AWS account,
no changes to your configuration are needed.

## Listing files
Use the AWS CLI *ls* command to list the contents of a bucket:
```
aws s3 ls s3://janelia-flylight-imagery --no-sign-request
```
The *--no-sign-request* parameter is necessary for anonymous access. You may omit it if you're using your own AWS account.
