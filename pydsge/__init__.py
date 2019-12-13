#!/bin/python
# -*- coding: utf-8 -*-

import os
from .clsmethods import DSGE

pth = os.path.dirname(__file__)

example_model = os.path.join(pth,'examples','dfi.yaml')
example_data = os.path.join(pth,'examples','tsdata.csv')

example = example_model, example_data
