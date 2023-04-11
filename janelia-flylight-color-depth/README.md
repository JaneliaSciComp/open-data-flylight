# FlyLight Color Depth MIPs

Part of the [Janelia FlyLight Imagery](https://data.janelia.org/3N5DS) open data set.

This bucket contains Color Depth MIPs for all the published FlyLight and [https://www.janelia.org/project-team/flyem](FlyEM) imagery, divided into libraries:
| Library                      | # images |
|------------------------------|----------|
| FlyEM_Hemibrain_v1.0         | 34717    |
| FlyEM_Hemibrain_v1.1         | 30894    |
| FlyEM_Hemibrain_v1.2.1       | 30790    |
| FlyLight_Annotator_Gen1_MCFO | 101215   |
| FlyLight_Gen1_GAL4           | 32932    |
| FlyLight_Gen1_LexA           | 5033     |
| FlyLight_Gen1_MCFO           | 136367   |
| FlyLight_Split-GAL4_Drivers  | 3045     |
| Vienna_Gen1_GAL4             | 3588     |
| Vienna_Gen1_LexA             | 2343     |

The color depth mask search technique, published in Otsuna, et. al[^otsuna], enables rapid and scalable 2d mask search across many terabytes of 3d data. Most importantly, it can be used to search from LM to EM and vice-versa, enabling cross-modal correspondence. 

The [*NeuronBridge*](https://neuronbridge.janelia.org/) tool, built on AWS Lambda, makes these Color Depth MIPs available via a web application. These are also available on [Quilt](https://data.janelia.org/oUjg4). 

## Bucket Structure

* Root
    * `<alignment space>`
        * `<library name>`
            * _color depth MIP files (PNG)_
            * counts_denormalized.json
            * keys_denormalized.json
            * searchable_neurons
            * OBJ (FlyEM only)
            * SWC (FlyEM only)
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
* **Status Code**: NeuPrint status code (optional)
* **Alignment Space**: standard alignment space to which the MIP is registered. See [Janelia FlyLight Templates](https://open.quiltdata.com/b/janelia-flylight-templates) for more information about alignment spaces.

Examples:
* **FlyEM Hemibrain v1.0**: 1038964771-RT-JRC2018_Unisex_20x_HR-CDM.png
* **FlyEM Hemibrain v1.2.1**: 267896359-JRC2018_Unisex_20x_HR-CDM.png

### counts_denormalized.json

A JSON file containing a count of PNG files in the current prefix

### keys_denormalized.json

A JSON file containing a list of PNG files in the current prefix

### searchable_neurons

This prefix is structured as follows:

* searchable_neurons
    * _partition subprefixes (1, 2, 3 ...)_
        * _TIFF images of neurons_
    * counts_denormalized.json
    * keys_denormalized.json
    * KEYS
    * pngs
        * _PNG images of neurons_

### _partition subprefixes (1, 2, 3 ...)_

These subprefixes contain up to 100 TIFF files, each one a neuron. TIFF file names contain metadata as follows:
```
[Publishing Name]-[Slide Code]-[Driver]-[Gender]-[Objective]-[Area/Tile]-[Alignment Space]-CDM_[Channel]-[neuron #].tif
```
Examples:
SS00724-20140623_34_F1-Split_GAL4-f-20x-brain-JRC2018_Unisex_20x_HR-CDM_2-01.tif
SS00724-20140623_34_F1-Split_GAL4-f-20x-brain-JRC2018_Unisex_20x_HR-CDM_2-02.tif

#### counts_denormalized.json

A JSON file containing a count of TIFF files in the subprefixes

#### keys_denormalized.json

A JSON file containing a list of TIFF files in the subprefixes

#### KEYS

This subprefix contains 100 subprefixes (0-99). Each of these subprefixes contains a duplicate of the keys_denormalized.json file

#### pngs

This subprefix contain PNG files, each one a neuron. PNG file names contain metadata as follows:
```
[Publishing Name]-[Slide Code]-[Driver]-[Gender]-[Objective]-[Area/Tile]-[Alignment Space]-CDM_[Channel]-[neuron #].png
```
Examples:
SS00724-20140623_34_F1-Split_GAL4-f-20x-brain-JRC2018_Unisex_20x_HR-CDM_2-01.png
SS00724-20140623_34_F1-Split_GAL4-f-20x-brain-JRC2018_Unisex_20x_HR-CDM_2-02.png

### OBJ

Contains OBJ files for FlyEM imagery. File names contain metadata as follows:

[Body ID].obj

### SWC

Contains SWC files for FlyEM imagery. File names contain metadata as follows:

[Body ID].swc

### Color_Depth_MIPs_For_Download

This area contains zip archives of alignment imagery. Files in FlyEM archives are named ad seen below in the "EM_Hemibrain" items. For FlyLight imagery, the file name contains Line name, slide code and gender. In the case of VT lines confocal scanned in Vienna, the file name have line name and genotype. Note that the [CDM search Fiji plugin](https://github.com/JaneliaSciComp/ColorMIP_Mask_Search/blob/master/Color_MIP_Mask_Search.jar) can recognize the line names to avoiding duplicate hits. Files are available on [Quilt](https://data.janelia.org/NLzbo). Archive names and descriptions follow.

#### Brain
* Gen1_GAL4_R_VT_JRC2018U_PackBits.zip: 55,814 color depth MIPs (CDMs) of the Gen1 GAL4 brain; R and VT lines that are aligned to the JFRC2018 unisex template. All images are from female flies. 
* Gen1_LexA_VT_R_JRC2018U.zip : 11,634 CDMs of the Gen1 LexA brain; R and VT lines that are aligned to the JFRC2018 unisex template. All images are from female flies. 
* 40x_MCFO_release_PackBits_06052020.zip: 80,812 released MCFO GAL4 CDM that are aligned to the JFRC2018 unisex template. 
* 40x_MCFO_release_gamma14_PackBits.zip: 80,812 released MCFO GAL4 CDM that are aligned to the JFRC2018 unisex template. Gamma correction of 1.4 applied for better visualization of dimmer neurons.
* EM_Hemibrain_Ver1.2_CDM_PackBits_gradient.zip: 44,476 CDM (30,789 original EM-CDM + 13,687 FL) from the JFRC2018 unisex template aligned EM-hemibrain. The CDM with _FL name is with the neuron crossing midline; for better matching with symmetrical GAL4 expressed neurons, we X-flipped the EM neuron and added the signals to the original CDM image. The CDM file name has the EM-body ID and tracing state.
* EM_Hemibrain1.2_SWC.zip: 30,789 SWC files translated to the JRC2018 unisex template space. These files can opened in [VVDviewer 3D/4D rendering software](https://github.com/takashi310/VVD_Viewer/releases) to overlay with LM data (.h5j files from [FlyLight website](https://www.janelia.org/project-team/flylight)).
* JRC2018_UNISEX_20x_HR.nrrd: The [template](https://www.janelia.org/publication/an-unbiased-template-of-the-drosophila-brain-and-ventral-nerve-cord) used for all brain CDM alignments.

#### VNC
* 40x_MCFO_VNC_JRC2018_UNISEX_g11_withString_for_Public.zip: 40x Gen1 MCFO GAL4 VNC aligned to the JRC2018 VNC unisex template. The color MIPs are generated by using gamma 1.1. Dimmer neurons are still dim, background value are low.
* 40x_MCFO_VNC_JRC2018_UNISEX_g14_withString_for_Public.zip: 40x Gen1 MCFO GAL4 VNC aligned to the JRC2018 VNC unisex template. The color depth MIPs are generated by using gamma 1.4. This gamma setting allows showing dimmer neurons clearly. However, it has higher background value and required higher background thresholding for color depth MIP search.
* Gen1_GAL4_VNC.zip: 13,998 CDMs of the Gen1 GAL4 VNC, R and VT lines. These are aligned to the 2017 female flyVNC symmetric template. All images are from female flies.
* JRC2018_VNC_UNISEX_461.nrrd: The unisex VNC template used for color depth MIP (An unbiased template of the Drosophila brain and ventral nerve cord: [https://journals.plos.org/plosone/article/comments?id=10.1371/journal.pone.0236495]).
* LexA_VNC.zip: 3,534 CDMs of the Gen1 LexA VNC, R and VT lines. These are aligned to the 2017 female flyVNC symmetric template. All images are from female flies. 

#### Larval brain
* Larva_original_GAL4_CDM.zip: 5,766 CDMs from Hen1 GAL4 FlyLight scanned larval brain. The alignment is from this work: [https://link.springer.com/article/10.1007/s12021-017-9349-6].
* Larva_Segmented_GAL4_CDM.zip: The 3D segmented aligned larval brain - 30,292 CDMs with 2D gradient map (original data before the segmentation in “Larva_original_GAL4_CDM.zip"). These CDMs have 0 background value, and provide a more accurate CDM search than the originals.


[^otsuna]: Otsuna, H., Ito, M., & Kawase, T. Color depth MIP mask search: a new tool to expedite Split-GAL4 creation. bioRxiv. 2018: 318006. DOI: [10.1101/318006](https://doi.org/10.1101/318006)
