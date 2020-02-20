# FlyLight Color Depth MIPs

Part of the [Janelia FlyLight Imagery](https://open.quiltdata.com/b/janelia-flylight-imagery) open data set.

This bucket contains Color Depth MIPs for all the published FlyLight and [https://www.janelia.org/project-team/flyem](FlyEM) imagery.

The color depth mask search technique, published in Otsuna, et. al[^otsuna], enables rapid and scalable 2d mask search across many terabytes of 3d data. Most importantly, it can be used to search from LM to EM and vice-versa, enabling cross-modal correspondence. 

The forthcoming *NeuronBridge* tool, built on AWS Lambda, will make this tool available as a web application. 

## Bucket Structure

* Root
    * `<alignment space>`
        * `<library name>`
            * color depth MIPs (PNG)

Example:
https://janelia-flylight-color-depth.s3.amazonaws.com/JRC2018_Unisex_20x_HR/FlyLight+Split-GAL4+Drivers/SS02702-20141222_80_B4-Split_GAL4-f-20x-brain-JRC2018_Unisex_20x_HR-color_depth_1.png

The file names contain metadata as follows:
```
[Line Name]-[Slide Code]-[Driver]-[Gender]-[Objective]-[Area/Tile]-[Alignment Space]-color_depth_[Channel].png
```

* **Line Name**: genetic fly line
* **Slide Code**: unique identifier for the sample
* **Driver**: GAL4, LexA, or Split_GAL4
* **Gender**: [m]ale or [f]emale
* **Objective**: microscope objective used to capture the original data
* **Area/Tile**: brain area (e.g. Brain vs VNC) or tile name
* **Alignment Space**: standard alignment space to which the MIP is registered. See [Janelia FlyLight Templates](https://open.quiltdata.com/b/janelia-flylight-templates) for more information about alignment spaces.
* **Channel**: number of the channel from the aligned image stack that is represented by this MIP

[^otsuna]: Otsuna, H., Ito, M., & Kawase, T. Color depth MIP mask search: a new tool to expedite Split-GAL4 creation. bioRxiv. 2018: 318006. DOI: [10.1101/318006](https://doi.org/10.1101/318006)
