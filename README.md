# Wellcounter-Modified

## Overview

Wellcounter-M is derived from the original Wellcounter system developed by the Stelzer lab at the University of Innsbruck, first published in 2025:

> Stelzer, C.-P., & Groffman, D. (2025). Wellcounter: Automated high-throughput phenotyping for aquatic microinvertebrates. Methods in Ecology and Evolution, 00, 1–14. <https://doi.org/10.1111/2041-210X.70012>

The general code structure and image manipulation algorithms originated from this publication. The version presented here (Wellcounter-M) is a heavily adapted version of this software used by the CRITTERS (Climate, Resource, and Image Tracking in Tiny Ecologically Representative Systems) lab at the University of Melbourne. These modifications were necessary to enable Wellcounter to generate accurate counts of *Paramecium caudatum* in our system.

## Installation

Wellcounter-M is written in Python and should be installed by creating a Conda environment:

```         
conda env create -f wellcounterM.yml
conda activate wellcounterM
```

## Citations

As with the original Wellcounter, this code is distributed under a MIT open-source license. If the code in this repository is used to generate future research outputs, please cite [both]{.underline} the original Wellcounter paper and the CRITTERS preprint presenting Wellcounter-M:

> Stelzer, C.-P., & Groffman, D. (2025). Wellcounter: Automated high-throughput phenotyping for aquatic microinvertebrates. Methods in Ecology and Evolution, 00, 1–14. <https://doi.org/10.1111/2041-210X.70012>

> Stern, E.R., Kelleher S., Vesk P., McCarthy M. (2026). CRITTERS: Climate, Resource, and Image Tracking in Tiny, Ecologically Representative Systems. EcoEvoRXiv. <https://doi.org/10.32942/X28S9F>