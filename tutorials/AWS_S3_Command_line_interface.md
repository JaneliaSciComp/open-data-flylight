## Introduction
Amazon provides a command line interface (CLI) for the AWS web services. Janelia Research Campus uses AWS S3 (Simple Storage Service) to
store all of the published FlyLight imagery, and you can easily use AWS CLI to search and download those files.

## Installation
First, you'll nned to install the AWS CLI on your computer. Follow Amazon's [instructions](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html).

## Configuration
Janelia Research Campus' buckets are set up to enable anonymous access, so no configuration is needed. If you already have an AWS account,
no changes to your configuration are needed.

## Listing files
Use the AWS CLI S3 *ls* command to list the contents of a bucket:
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
Note that any spaces in a prefix or object must be escaped with a backslash ("__\\__"):
```
aws s3 ls s3://janelia-flylight-imagery/Gen1\ MCFO/ --no-sign-request
```
You can list files recursively with the *--recursive* parameter:
```
s3 ls s3://janelia-flylight-imagery/LPLC2_paper/ --no-sign-request --recursive
2020-04-01 13:40:44      77680 LPLC2_paper/LPLC2_paper.metadata.json
2020-04-18 14:11:06   49710318 LPLC2_paper/OL0047B/OL0047B-20131122_32_H5-f-63x-Brain-Split_GAL4-JRC2018_FEMALE_63x_DS-aligned_stack.h5j
                        .
                        .
                        .
```
## Copying files
Use the AWS CLI S3 *cp* command to copy objects:
```
aws s3 cp s3://janelia-flylight-imagery/LPLC2_paper/OL0047B . --recursive --no-sign-request
```
The above command will copy all onjects under janelia-flylight-imagery/LPLC2_paper/OL0047B to your current directory. As the files
are copied, you'll see a running list of files and current status:
```
download: s3://janelia-flylight-imagery/LPLC2_paper/OL0047B/OL0047B-20131122_32_H5-f-63x-Brain-Split_GAL4-multichannel_mip.png to ./OL0047B-20131122_32_H5-f-63x-Brain-Split_GAL4-multichannel_mip.png
download: s3://janelia-flylight-imagery/LPLC2_paper/OL0047B/OL0047B-20131122_32_H5-f-63x-Brain-Split_GAL4-signals_mip.png to ./OL0047B-20131122_32_H5-f-63x-Brain-Split_GAL4-signals_mip.png
Completed 108.7 MiB/~9.5 GiB (9.1 MiB/s) with ~37 file(s) remaining (calculating...
```
It's always a good idea to simulate the copy first with the *--dryrun* parameter:
```
aws s3 cp s3://janelia-flylight-imagery/LPLC2_paper/OL0047B . --recursive --no-sign-request --dryrun
```
You'll see what it would have copied:
```
(dryrun) download: s3://janelia-flylight-imagery/LPLC2_paper/OL0047B/OL0047B-20131122_32_H5-f-63x-Brain-Split_GAL4-JRC2018_FEMALE_63x_DS-aligned_stack.h5j to ./OL0047B-20131122_32_H5-f-63x-Brain-Split_GAL4-JRC2018_FEMALE_63x_DS-aligned_stack.h5j
(dryrun) download: s3://janelia-flylight-imagery/LPLC2_paper/OL0047B/OL0047B-20131122_32_H5-f-63x-Brain-Split_GAL4-JRC2018_FEMALE_63x_DS-aligned_stack.png to ./OL0047B-20131122_32_H5-f-63x-Brain-Split_GAL4-JRC2018_FEMALE_63x_DS-aligned_stack.png
(dryrun) download: s3://janelia-flylight-imagery/LPLC2_paper/OL0047B/OL0047B-20131122_32_H5-f-63x-Brain-Split_GAL4-JRC2018_Unisex_20x_HR-CDM_1.png to ./OL0047B-20131122_32_H5-f-63x-Brain-Split_GAL4-JRC2018_Unisex_20x_HR-CDM_1.png
                        .
                        .
                        .
```
