import json
from collections import namedtuple 
import torch
import numpy as np
import pandas as pd
import networkx as nx

CausalEdge = namedtuple('CausalEdge', 'parent child')
RelationalNode = namedtuple('RelationalNode', 'entity attribute')
InstanceNode = namedtuple('InstanceNode', 'entity attribute instance')