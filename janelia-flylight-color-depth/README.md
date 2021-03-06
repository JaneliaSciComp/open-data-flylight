# FlyLight Color Depth MIPs

Part of the [Janelia FlyLight Imagery](https://data.janelia.org/3N5DS) open data set.

This bucket contains Color Depth MIPs for all the published FlyLight and [https://www.janelia.org/project-team/flyem](FlyEM) imagery, divided into libraries:
| Library              | # images |
|----------------------|----------|
| FlyEM_Hemibrain_v1.0 | 34717    |
| FlyLight_GEN1_GAL4   | 32932    |
| FlyLight_Gen1_LexA   | 5033     |
| Vienna_Gen1_GAL4     | 3588     |
| Vienna_Gen1_LexA     | 2343     |

The color depth mask search technique, published in Otsuna, et. al[^otsuna], enables rapid and scalable 2d mask search across many terabytes of 3d data. Most importantly, it can be used to search from LM to EM and vice-versa, enabling cross-modal correspondence. 

The [*NeuronBridge*](https://neuronbridge.janelia.org/) tool, built on AWS Lambda, makes these Color Depth MIPs available via a web application. These are also available on [Quilt](https://data.janelia.org/oUjg4). 

## Bucket Structure

* Root
    * `<alignment space>`
        * `<library name>`
            * _color depth MIP files (PNG)_
    * Color_Depth_MIPs_For_Download


### `<alignment space>`

FlyLight file names contain metadata as follows:
```
[Publishing Name]-[Slide Code]-[Driver]-[Gender]-[Objective]-[Area/Tile]-[Alignment Space]-CDM_[Channel].png
```

* **Publishing Name**: Publishing name for genetic fly line
* **Slide Code**: unique identifier for the sample
* **Driver**: GAL4, LexA, or Split_GAL4
* **Gender**: [m]ale or [f]emale
* **Objective**: microscope objective used to capture the original data
* **Area/Tile**: brain area (e.g. Brain vs VNC) or tile name
* **Alignment Space**: standard alignment space to which the MIP is registered. See [Janelia FlyLight Templates](https://open.quiltdata.com/b/janelia-flylight-templates) for more information about alignment spaces.
* **Channel**: number of the channel from the aligned image stack that is represented by this MIP


Examples:
* **FlyLight Gen1 GAL4**: R16E08-20111230_32_mA01b_20111230103554390-GAL4-m-20x-brain-JRC2018_Unisex_20x_HR-CDM_1.png
* **FlyLight Gen1 LexA**: R80G01-20110719_02_fA01b_20110720114726843-LexA-f-20x-brain-JRC2018_Unisex_20x_HR-CDM_1.png
* **FlyLight Gen1 MCFO**: VT014706-20180221_62_I1-GAL4-f-40x-brain-JRC2018_Unisex_20x_HR-CDM_3.png
* **FlyLight Split-GAL4 Drivers**: SS02702-20141222_80_B4-Split_GAL4-f-20x-brain-JRC2018_Unisex_20x_HR-CDM_1.png
* **Vienna Gen1 GAL4**: VT061925-sample_004038-GAL4-f-20x-brain-JRC2018_Unisex_20x_HR-CDM_1.png
* **Vienna Gen1 LexA**: VT064305-sample_008723-LexA-f-20x-brain-JRC2018_Unisex_20x_HR-CDM_1.png

Fly EM file names contain metadata as follows:
```
[Body ID]-[Status Code]-[Alignment Space]-CDM.png
```

* **Body ID**: NeuPrint Body ID
* **Status Code**: NeuPrint status code
* **Alignment Space**: standard alignment space to which the MIP is registered. See [Janelia FlyLight Templates](https://open.quiltdata.com/b/janelia-flylight-templates) for more information about alignment spaces.

Examples:
* **FlyEM Hemibrain v1.0**: 1038964771-RT-JRC2018_Unisex_20x_HR-CDM.png

### Color_Depth_MIPs_For_Download

This area contains zip archives of alignment imagery. Files in FlyEM archives are named ad seen below in the "EM_Hemibrain" items. For FlyLight imagery, the file name contains Line name, slide code and gender. In the case of VT lines confocal scanned in Vienna, the file name have line name and genotype. Note that the [CDM search Fiji plugin](https://github.com/JaneliaSciComp/ColorMIP_Mask_Search/blob/master/Color_MIP_Mask_Search.jar) can recognize the line names to avoiding duplicate hits. Files are available on [Quilt](https://data.janelia.org/NLzbo). Archive names and descriptions follow.

#### Brain
* Gen1_GAL4_R_VT_JRC2018U_PackBits.zip: 55,814 color depth MIPs (CDMs) of the Gen1 GAL4 brain; R and VT lines that are aligned to the JFRC2018 unisex template. All images are from female flies. 
* Gen1_LexA_VT_R_JRC2018U.zip : 11,634 CDMs of the Gen1 LexA brain; R and VT lines that are aligned to the JFRC2018 unisex template. All images are from female flies. 
* 40x_MCFO_release_PackBits_06052020.zip: 80,812 released MCFO GAL4 CDM that are aligned to the JFRC2018 unisex template. 
* 40x_MCFO_release_gamma14_PackBits.zip: 80,812 released MCFO GAL4 CDM that are aligned to the JFRC2018 unisex template. Gamma correction of 1.4 applied for better visualization of dimmer neurons.
* EM_Hemibrain11_0630_2020_radi2_PackBits_noNeuronName.zip: 32,777 CDM from the JFRC2018 unisex template aligned EM-hemibrain. The CDM file name has the EM-body ID and tracing state.
* EM_Hemibrain11_0630_2020_radi2_PackBits_withNeuronName.zip: 32,777 CDM from the JFRC2018 unisex template aligned EM-hemibrain. The CDM file name has the EM-body ID, neuron name, and tracing state. This set requires newly released (ver. July 2020) [CDM search Fiji plugin](https://github.com/JaneliaSciComp/ColorMIP_Mask_Search/blob/master/Color_MIP_Mask_Search.jar).
* Hemibrain1.1_SWC_Skeleton: 32,777 SWC files translated to the JRC2018 unisex template space. These files can opened in [VVDviewer 3D/4D rendering software](https://github.com/takashi310/VVD_Viewer/releases) to overlay with LM data (.h5j files from [FlyLight website](https://www.janelia.org/project-team/flylight)).
* JRC2018_UNISEX_20x_HR.nrrd: The [template](https://www.janelia.org/publication/an-unbiased-template-of-the-drosophila-brain-and-ventral-nerve-cord) used for all brain CDM alignments.

#### VNC
* Gen1_GAL4_VNC.zip: 13,998 CDMs of the Gen1 GAL4 VNC, R and VT lines. These are aligned to the 2017 female flyVNC symmetric template. All images are from female flies. 
* LexA_VNC.zip: 3,534 CDMs of the Gen1 LexA VNC, R and VT lines. These are aligned to the 2017 female flyVNC symmetric template. All images are from female flies. 

#### Larval brain
* Larva_original_GAL4_CDM.zip: 5,766 CDMs from Hen1 GAL4 FlyLight scanned larval brain. The alignment is from this work: [https://link.springer.com/article/10.1007/s12021-017-9349-6].
* Larva_Segmented_GAL4_CDM.zip: The 3D segmented aligned larval brain - 30,292 CDMs with 2D gradient map (original data before the segmentation in “Larva_original_GAL4_CDM.zip"). These CDMs have 0 background value, and provide a more accurate CDM search than the originals.


[^otsuna]: Otsuna, H., Ito, M., & Kawase, T. Color depth MIP mask search: a new tool to expedite Split-GAL4 creation. bioRxiv. 2018: 318006. DOI: [10.1101/318006](https://doi.org/10.1101/318006)
