#!/usr/local/bin/python
# This Python file uses the following encoding: utf-8
# scripts/openrem_rdsr

"""Script to launch the rdsr to import information from DICOM Radiation SR objects 

    :param filename: relative or absolute path to Radiation Dose Structured Report.
    :type filename: str.

    Tested with:
        * CT: Siemens, Philips and GE RDSR, GE Enhanced SR.
        * Fluoro: Siemens Artis Zee RDSR
"""

if __name__ == "__main__":
    from openrem.remapp.extractors.rdsr import rdsr
    import openrem.remapp.tools.default_import as default_import
    # rdsr(r"I:\6232970\CT ABDOMEN LOW DOSE-2869792.03259103\onbekend-9001\SR-1-0")
    # rdsr(r"I:\8368413\CT THORAX-2865576.03254523\onbekend-9001\SR-1-0")
    # rdsr(r"I:\4276543\CT CEREBRAAL-2827275.03213034\onbekend-9001\SR-1-0")
    # rdsr(r"I:\1073597\CT THORAX I.V. CONTRAST-2853267.03241134\onbekend-9001\SR-1-0")
    rdsr(r"I:\1858391\CT THORAX LEVER 4F + ABDOMEN RUCO I.V. CONTRAST-2865305.03254222\onbekend-9001\SR-1-0")
    # default_import.default_import(
    #    rdsr,
    #    "import_rdsr",
    #    "the radiation dose structured report",
    #    0,
    #    {"import_rdsr": 1},
    # )
