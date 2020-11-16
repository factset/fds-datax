# fds.datax

fds.datax offers instant access to define and retrieve a time-series universe of securities that is cached into a centralized data store. Having access to a cached data store shifts the research period focused on building a universe to immediately analyzing FactSet’s core & 3rd Party data using a consistent process.

At a high level, the library offers you the ability to:

- Generate a daily security universe from FDS Ownership data based on a defined ETF identifier (spy-us) or a custom data set
- Generate universe DataFrame files that contain FDS Symbology, security reference, pricing and corporate actions metadata
- Maintain and view cached universes stored locally in a private or firm permissioned data store
- Access operations to support the generation of FDS symbology, security reference, pricing, and corporate actions DataFrames.

## Installation

To install this package locally, follow these steps:

1. Download the zip of the repo or clone the repository locally
2. Unzip if necessary, and note the location of the **fds.datax** folder
3. Open the Anaconda Prompt and enter the following:
```
pip install -e "<path to downloaded folder containing fds.datax>\."
```
