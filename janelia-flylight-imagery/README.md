# FlyLight Imagery

## Overview

Neuroscience research is being revolutionized by the comprehensive mapping of whole nervous systems. Janelia Research Campus is leading this effort in the fruit fly, Drosophila melanogaster, via light and electron microscopy. FlyLight is a Project Team at Janelia developing tools to characterize (at the light level) and manipulate related groups of neurons. FlyLight works with researchers to produce genetic driver lines with specific expression patterns to target neurons and circuits of interest. These expression patterns are visualized in the central nervous system of each fly by using confocal laser scanning microscope to produce a 3d image. 

Janelia’s FlyLight imagery collection is the largest and most comprehensive such data set in the world. It documents the expression patterns of both “Generation 1” lines that have broad expression patterns (Jenett, et al., 2012[^jenett]) and cell type-specific intersections created using the Split-GAL4 system (e.g. Aso, et al., 2014[^aso]). 

In addition to the imagery and metadata, Janelia is making all of the genetic driver fly stocks available to researchers, subject to relevant Material Transfer Agreements. With the image data documenting which neurons are targeted by each line, researchers can use the lines to further study specific cell populations for their effects on fly behavior and other experiments to associate structure with function. Bloomington Stock Center, the primary depository for fly stocks, has shipped Janelia lines over 125,000 times to 683 organizations in 46 countries. 

Alignment of the data to a standard template allows additional purely anatomical studies. Patterns of expression of different genetic drivers in different fly brains can be precisely compared, enabling comprehensive mapping of neural structures and cell types. As new light and electron microscopy data becomes available, it can be aligned to the same template for comparison. 

One of FlyLight’s goals is to produce tools to target specific cell types in the nervous system. This is a widespread need in the research community, and the primary method to achieve the required specificity is the split-GAL4 system (Luan, et al., 2006[^luan]). The Generation 1 GAL4 lines included here form the basis for making split-GAL4 halves and predicting which combinations are most likely to give the desired control of target neurons. 

This dataset includes images aligned to the JRC2018 brain and VNC templates (Bogovic, et al., 2018[^bogovic]). The fly nervous system has subtle differences between males and females, and our data is aligned to both sex-specific templates (for optimal within-sex alignments) and to an averaged unisex template (for optimal between-sex alignments). This improved template and associated alignments enable optimal comparison between samples or imaging modalities. 

Color depth MIP mask search is a new technique (Otsuna, et al., 2018[^otsuna]) that allows extremely fast 3d image mask search and can bridge the gap between light microscopy (LM) and electron microscopy (EM) by allowing researchers to find similar neurons in both modalities. The EM-based Drosophila connectome that will be published by our FlyEM project early in 2020 represents a fundamental shift in how neuroscience research is done, similar to how the Human Genome Project affected the medical research community. The LM data that is part of this data set allows researchers to start with EM and find genetic lines which express their neurons of interest, enabling cell-specific research.

## Bucket Structure

Files are organized by release, each of which is linked to a scientific publication. Within a release, there are multiple fly lines, and each line can be multiple published samples (i.e. specimens). 

* Root
    * `<release name>`
        * _JSON metadata file_ - metadata about the release including the associated publication(s)
        * `<fly line publishing name>`
            * _JSON metadata file_ - metadata about the images, including curated anatomical annotations
            * _LSM files (LSM)_ - microscope imagery in Zeiss LSM format
            * _unaligned image stack files (H5J)_ - 3d imagery, distortion corrected, merged, and stitched
            * _aligned image stack files (H5J)_ - 3d imagery registered to a canonical template
            * _MIP files (PNG)_ - maximum intensity projections for rapid viewing
            * _movie files (MP4)_ - small movies for rapid viewing of Z slices

FlyLight file names contain metadata as follows:
```
[Publishing Name]-[Slide Code]-[Driver]-[Gender]-[Objective]-[Area/Tile]-[Alignment Space].[extension]
```

* **Publishing Name**: Publishing name for genetic fly line
* **Slide Code**: unique identifier for the sample
* **Gender**: [m]ale or [f]emale
* **Objective**: microscope objective used to capture the original data
* **Area/Tile**: brain area (e.g. Brain vs VNC) or tile name
* **Driver**: GAL4, LexA, or Split_GAL4
* **Alignment Space**: optional standard alignment space to which the MIP is registered. See [Janelia FlyLight Templates](https://open.quiltdata.com/b/janelia-flylight-templates) for more information about alignment spaces. This is only included for aligned stacks, unaligned stacks, and Color Depth MIPs.
* **Product**: this will differ according to the type of file it is - see examples below. For Color Depth MIPs, this will be in the form CDM_[Channel].
* **Exstension** a file extension (png, mp4, h5j, lsm, lsm.bz2, json)

Examples:
* **JSON metadata file**: SS02702-20141222_80_B4-f-20x-brain-Split_GAL4-metadata.json
* **LSM file**: SS02702-20141222_80_B4-f-20x-brain-Split_GAL4.lsm.bz2
* **Unaligned image stack file**: SS02702-20141222_80_B4-f-20x-brain-Split_GAL4-unaligned_stack.h5j
* **Aligned image stack file**: SS02702-20141222_80_B4-f-20x-brain-Split_GAL4-JRC2018_FEMALE_20x_HR-aligned_stack.h5j
* **Color depth MIP**: SS02702-20141222_80_B4-f-20x-brain-Split_GAL4-JRC2018_Unisex_20x_HR-CDM_1.png
* **Other MIP**: SS02702-20141222_80_B4-f-20x-brain-Split_GAL4-multichannel_mip.png
* **Movie**: SS02702-20141222_80_B4-f-20x-brain-Split_GAL4-signals_translation.mp4

## Related buckets

* [FlyLight Alignment Templates](https://open.quiltdata.com/b/janelia-flylight-templates)
* [FlyLight Color Depth MIPs](https://open.quiltdata.com/b/janelia-flylight-color-depth)

## References

[^jenett]: Jenett, A., Rubin, G. M., Ngo, T., Shepherd, D., Murphy, C., Dionne, H., Pfeiffer, B. D., Cavallaro, A., Hall, D., Jeter, J., Iyer, N., Fetter, D., Hausenfluck, J. H., Peng, H., Trautman, E. T., Svirskas, R. R., Myers, E. W., Iwinski, Z. R., Aso, Y., DePasquale, G. M., Enos, A., Hulamm, P., Lam, S. C. B., Li, H., Laverty, T. R., Long, F., Qu, L., Murphy, S. D., Rokicki, K., Safford, T., Shaw, K., Simpson, J. H., Sowell, A., Tae, S., Yu, Y., & Zugates, C. T. A GAL4-Driver Line Resource for Drosophila Neurobiology. Cell Reports. 2012; 2: 991-1001. DOI: [10.1016/j.celrep.2012.09.011](https://doi.org/10.1016/j.celrep.2012.09.011)

[^aso]: Aso, Y., Hattori, D., Yu, Y., Johnston, R. M., Iyer, N. A., Ngo, T., Dionne, H., Abbott, L., Axel, R., Tanimoto, H., & Rubin, G. M. The neuronal architecture of the mushroom body provides a logic for associative learning. eLife. 2014; 3: elife.04577. DOI: [10.7554/eLife.04577](https://doi.org/10.7554/eLife.04577)

[^otsuna]: Otsuna, H., Ito, M., & Kawase, T. Color depth MIP mask search: a new tool to expedite Split-GAL4 creation. bioRxiv. 2018: 318006. DOI: [10.1101/318006](https://doi.org/10.1101/318006)

[^luan]: Luan H, Peabody NC, Vinson CR, White BH. Refined spatial manipulation of neuronal function by combinatorial restriction of transgene expression. Neuron. 2006 Nov 9;52(3):425-36. DOI: [10.1016/j.neuron.2006.08.028](https://doi.org/10.1016/j.neuron.2006.08.028)

[^bogovic]: Bogovic, J. A., Otsuna, H., Heinrich, L., Ito, M., Jeter, J., Meissner, G., Nern, A., Colonell, J., Malkesman, O., Ito, K., Saalfeld, S.. An unbiased template of the Drosophila brain and ventral nerve cord. bioRxiv 376384; DOI: [10.1101/376384](https://doi.org/10.1101/376384)
