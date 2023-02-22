import json
from collections import namedtuple 
import torch
import numpy as np
import pandas as pd
import networkx as nx

Edge = namedtuple('Edge', 'parent child')
Node = namedtuple('Node', 'entity attribute')
InstanceNode = namedtuple('InstanceNode', 'entity attribute instance')