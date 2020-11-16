__docformat__ = "restructuredtext"

from fds.datax._get_data._get_data import GetSDFData as getSDFdata
from fds.datax.universe import Universe

# module level doc-string
__doc__ = """
fds.datax is a Python library that allows you to define and retrieve a series of dataframes based on a universe of 
securities, the corresponding metadata, and cache the data locally to connect a universe to FactSet’s core content. 
This library offers you the ability to create a data store of cached universes or load your cached universe from a 
local private or shared folder, removing the need to re-create your universe each time and preserving the universe 
criteria for consistent analysis. 
At a high level, the library offers you the ability to:
•	Generate a daily security universe from FDS Ownership data based on a defined ETF identifier (spy-us), 
or custom data set
•	Generate files for a universe that will contain FDS Symbology, security reference, pricing and corporate actions 
data
•	Maintain and view a list of cache universe files stored locally in a data store
•	Operations to support the generation of FDS symbology, security reference, pricing, and corporate actions 
Dataframes. 

_____________________"""
