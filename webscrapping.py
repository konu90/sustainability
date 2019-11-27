# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.3'
#       jupytext_version: 1.0.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import itertools
import pandas as pd
import re
import numpy as np


def extraeWeb (webscrap): 
    auxInput = []

    # Obtén fecha
    regex = "dt=.\d*\"\>(\d\d\/\d\d\/\d\d|-)"
    matches = re.findall(regex, webscrap, re.MULTILINE)
    auxInput.append(matches)

    # Obtén energía generada (Generated)
    regex = "title=\"Exported: None\">(\d*\.\d*|-)"
    matches = re.findall(regex, webscrap, re.MULTILINE)
    auxInput.append(matches)

    # Obtén eficiencia (efficiency)
    regex = "style=\"padding-right:25px\">(.d*\.\d*|-)"
    matches = re.findall(regex, webscrap, re.MULTILINE)
    auxInput.append(matches)

    # Obtén pico de potencia (peak power)
    regex = "style=\"padding-right:35px\">(\d*\.\d*|-)"
    matches = re.findall(regex, webscrap, re.MULTILINE)
    auxInput.append(matches)

    # Obtén hora de pico (peak time)
    regex = "<td align=\"center\">(\d*\:\d*..|-)"
    matches = re.findall(regex, webscrap, re.MULTILINE)
    auxInput.append(matches)

    # Obtén tipo de día (condictions)
    regex = "<td nowrap=\"\">(\w*\s\w*|\w*|-)</td><td align=\"right\""
    matches = re.findall(regex, webscrap, re.MULTILINE)
    auxInput.append(matches)


    tomaMelon = np.array(auxInput).T.tolist()
    enpandas = pd.DataFrame(tomaMelon)
    return enpandas

