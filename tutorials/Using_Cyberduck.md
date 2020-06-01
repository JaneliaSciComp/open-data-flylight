# Using Cyberduck to download imagery

Imagery in the AWS Open Data buskes is accessible via many file transfer tools. One such tool is [Cyberduck](https://cyberduck.io/) for MacOS or Windows.
To download imagery, use the following instructions:

Click on the "Open Connection" button (tin the upper left of the window) or select File -> Open Connection from the main menu.

![Cyberduck 1](https://github.com/JaneliaSciComp/open-data-flylight/blob/master/tutorials/cd1.png "")

Add information as follows:
* For "Server", enter s3://janelia-flylight-color-depth.s3.amazonaws.com for Color Depth MIPs, or s3://janelia-flylight-imagery.s3.amazonaws.com for Fly Light Gen1/Split-GAL4 imagery or 
* Verify Amazon S3 is automatically selected in the top pulldown menu.
* Check the button for Anonymous Login.

![Cyberduck 2](https://github.com/JaneliaSciComp/open-data-flylight/blob/master/tutorials/cd2.png "")

Click the "Connect" button.
You can now navigate the directory structure, and download directories/files by dragging and dropping.

![Cyberduck 3](https://github.com/JaneliaSciComp/open-data-flylight/blob/master/tutorials/cd3.png "")
