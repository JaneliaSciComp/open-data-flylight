# FlyLight Alignment Templates

Part of the [Janelia FlyLight Imagery](https://open.quiltdata.com/b/janelia-flylight-imagery) open data set.

This bucket contains processed templates for registering images to standard alignment spaces. The [original source templates](https://www.janelia.org/open-science/jrc-2018-brain-templates) were published in Bogovic, et. al[^bogovic]. These transformed versions are optimized for alignment of FlyLight's data. 

## Bucket Structure

* Root
    * `<alignment space name>`
        * Template files (NRRD)

The image files are in standard 3d [NRRD](http://teem.sourceforge.net/nrrd/) format.

[^bogovic]: Bogovic, J. A., Otsuna, H., Heinrich, L., Ito, M., Jeter, J., Meissner, G., Nern, A., Colonell, J., Malkesman, O., Ito, K., Saalfeld, S.. An unbiased template of the Drosophila brain and ventral nerve cord. bioRxiv 376384; DOI: [10.1101/376384](https://doi.org/10.1101/376384)
