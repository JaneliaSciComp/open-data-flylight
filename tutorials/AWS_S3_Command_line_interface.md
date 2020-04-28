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
You should see something similar to this:
```
                           PRE Aso&Rubin 2016/
                           PRE Descending Neurons 2018/
                           PRE Gen1 MCFO/
                           PRE Hampel 2015/
                           PRE LPLC2_paper/
                           PRE Robie 2017/
                           PRE Wolff 2018/
                           PRE oviDN 2020/
2020-04-17 14:44:10       8123 README.md
```
Theere is one object (file) in the listing above: README.md. The other entries are prefixes (indicated by __PRE__) - analogous to dieectories. If you want to see the objects and/or prefixes under a prefix, simply append it to the bucket:
```
aws s3 ls s3://janelia-flylight-imagery/LPLC2_paper/ --no-sign-request
```
...and you'll see a list of prefixes in the LPLC2_paper prefix:
```
                           PRE OL0047B/
                           PRE OL0048B/
                           PRE SS00810/
                           PRE SS03752/
```
