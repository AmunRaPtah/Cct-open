"""
CCT-Open: Open Source Computational Framework for Addiction Liability Prediction.

Implements Consolidation Control Theory (CCT) across three computational layers:
    1. Receptor Binding Input Module
    2. Receptor-to-Axis Transfer Module
    3. CCT Encoding Probability Module

The GATE extension applies the same framework to BCI stimulation safety.

Theoretical framework: https://doi.org/10.5281/zenodo.20427785
Repository: https://github.com/Amunraptah/cct-open
License: Apache 2.0
"""

__version__ = "0.1.0-dev"
__author__ = "Eniola Olutogun"
__license__ = "Apache-2.0"
__doi__ = "10.5281/zenodo.20427785"

from cct_open.core import CCTModel

__all__ = ["CCTModel"]
