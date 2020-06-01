# Using Cyberduck to download imagery

Imagery in the AWS Open Data buckets is accessible via many file transfer tools. One such tool is [Cyberduck](https://cyberduck.io/) for MacOS or Windows.
To download imagery, use the following instructions:

Click on the "Open Connection" button (in the upper left of the window) or select File -> Open Connection from the main menu.

![Cyberduck 1](https://github.com/JaneliaSciComp/open-data-flylight/blob/master/tutorials/cd1.png "")

Add information as follows:
* Ensure that the connection method in the first pulldown menu is set to "FTP (File Transfer Protocol)".
* Check the button for Anonymous Login.
* For "Server", enter s3://janelia-flylight-color-depth.s3.amazonaws.com for Color Depth MIPs, or s3://janelia-flylight-imagery.s3.amazonaws.com for Fly Light Gen1/Split-GAL4 imagery.
* Verify that "Amazon S3" is automatically selected in the top pulldown menu (it should automatically change to this when you enter the Server).

![Cyberduck 2](https://github.com/JaneliaSciComp/open-data-flylight/blob/master/tutorials/cd2.png "")

Click the "Connect" button.
You can now navigate the directory structure, and download directories/files by dragging and dropping.

![Cyberduck 3](https://github.com/JaneliaSciComp/open-data-flylight/blob/master/tutorials/cd3.png "")
