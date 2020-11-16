# fds.datax Library

_Last Updated: July 2020_

## Overview

**fds.datax** offers instant access to define and retrieve a time-series universe of securities that is cached into a centralized
data store. Having access to a cached data store shifts the research period focused on building a universe to immediately
analyzing FactSet’s core & 3rd Party data using a consistent process.

At a high level, the library offers you the ability to:

- Generate a daily security universe from FDS Ownership data based on a defined ETF identifier _(spy-us)_ or a
    custom data set
- Generate universe DataFrame files that contain FDS Symbology, security reference, pricing and corporate
    actions metadata
- Maintain and view cached universes stored locally in a private or firm permissioned data store
- Access operations to support the generation of FDS symbology, security reference, pricing, and corporate
    actions DataFrames.

---

## Table of Contents

- Overview
- Getting Started
   - Import Library
   - Setting the Working Directory for the Data Store
   - Locate Existing Data Store
   - Create a new Data Cache Universe
   - Reading Data Store Caches
      - Load Symbology (Time Series)
      - Load Security Reference Data
      - Load Pricing Data
      - Load Corporate Action Adjustment Factors
   - Rebuild a Data Cache Universe
   - Deleting a Data Cache Universe
   - Next Steps – Connect Data Cache Universe to Data Exploration Content
- API Details
   - Details of Module Functionality
   - FDSArchive
      - Locate
      - Delete
      - Create
      - Rebuild
      - Read
   - GetSDFData
      - etf_universe
      - fds_symbology
      - fds_sec_ref
      - fds_fx_rates
      - fds_prices
      - fds_corp_actions
- Considerations
- Support / Questions / Feedback

---


## Getting Started

Currently the **fds.datax** library is preinstalled and available for use in the FactSet Data Exploration environment. To access
the library, please login to your Data Exploration account and launch a Jupyter Notebook file.

There are two available Jupyter Notebooks located under the “ _fds.datax/Notebooks_ ” folder created by FactSet to assist in an
overview of the features and functionality of the fds.datax library:

- **fds.datax Overview.ipynb**
    o An interactive overview notebook outlining the key _Universe_ method and underlying functions.
- **getsdfdata Overview.ipynb**
    o An interactive overview notebook highlighting the key utility functions within the _getsdfdata_ method.

The below walkthrough mimics the ` _fds.datax Overview.ipynb_ ` Jupyter notebook. To begin, please open the “ _fds.datax

Overview.ipynb_ ” notebook located in the “ _fds.datax/Notebooks_ ” folder or create a blank Jupyter Notebook to interactively
code.

### Import Library

To access the library within a Jupyter Notebook, please import **fds.datax**. In the example below, the fds.datax library is being

imported and set to the alias of “fds”

```
Example
```
1. **import** fds.datax as fds
2. **import os**

Once you have imported the **fds.datax** library, you can begin creating and managing cache universes that will connect to
FactSet’s core content. The FactSet team recommends leveraging this library at the start of your research process to
obtain a time-series universe to easily link with FactSet’s core content or 3rd Party data.

### Setting the Working Directory for the Data Store

Before creating a new cache universe, it is important to determine a default folder location as the data store that will
house all available cache universes. You can set the working directory to the “personal” folder location or the “client”
folder location. Depending on which folder the `dir_path` cache universe is stored, you can keep caches private or allow
all team members access to the cached universes.

```
Example
```
1. fds_path = os.getcwd()
2. ds = fds.Universe(dir_path=fds_path)
3. # Display the working directory
. ds.dir_path


### Locate Existing Data Store

First examine your existing data store to determine if there are any available data cache files. The `.locate()` command
will look for any available data cache files.

```
Example
```
1. ds.locate()

If the current working directory does not contain any cached data files, the code output will display:

_Detailed `.Locate()` API Information._

### Create a new Data Cache Universe

To create a new data cache universe, call the `.create()` command paired with the option parameter set to “generate”.
Then define the universe by selecting an ETF identifier, start date, end date, MSSQL Server DB connection, and currency.

_Example_
```
1. # Specify a cache name
2. cn = 'my_first_data_cache'
3.
4. # DSN name for a connection to a MSSQL Server DB containing FDS Standard DataFeeds content.
5. # `SDF` is the default as it connects to the FactSet Standard DataFeed data
6. mssql_dsn = 'SDF'
7.
8. # ETF ticker in a ticker-region format.
9. etf_ticker = 'SPY-US'
10.
11. # Currency for pricing data to be return, if local currency is desired set to "LOCAL"
12. currency = 'USD'
13.
14. # Earliest available report date in YYYY-MM-DD format
15. start_date = '2019- 01 - 01'
16.
17. # Most recent available report date to be returned in YYYY-MM-DD format
18. end_date = '2019- 12 - 31'
19.
20. # Call the `create()` function to generate a time-series universe.
21. ds.create('generate',cache_name = cn,
22. mssql_dsn = mssql_dsn,
23. etf_ticker = etf_ticker,
24. currency = currency,
25. start_date = start_date,
26. end_date = end_date)
```
After the cache universe is created, you can run the `.locate()` command again to view all available data caches. The
output now displays the “my_first_data_cache” record and respective metadata.

_Example_


1. ds.locate()

_Detailed `.Create()` API Information._

### Reading Data Store Caches

After locating an available data cache in your local data store, you can use the `.read()` command to load data files based
on cache name. You will need to supply the “cache_name” parameter with an available cache name. Then you will pass
in one of four options into the “options” parameter:

- **Universe** : load time series symbology information for a cache
- **Sec Ref** : load security reference for a cache
- **Prices** : load pricing data for a cache. Choose unadjusted, split, or split & spin-off.
- **Corp Actions** : load corporate action factors for a cache

_Examples_

#### Load Symbology (Time Series)

1. ds.read(option='Universe',cache_name='my_first_data_cache').head()

#### Load Security Reference Data

1. ds.read(option='Sec Ref',cache_name='my_first_data_cache').head()


#### Load Pricing Data

You can supply an additional parameter of “adj” to specific the type of adjustments to be applied to the data:

- 0 = Unadjusted Data
- 1 = Split Adjusted Data
- 2 = Split & Spin-off Adjusted Data
1. ds.read(option='Prices',cache_name='my_first_data_cache',adj=2).head()

---

#### Load Corporate Action Adjustment Factors

1. ds.read(option='Corp Actions',cache_name='my_first_data_cache').head()


_Detailed `.Read()` API Information._

### Rebuild a Data Cache Universe

To rebuild an existing data cache, call the `.rebuild` command. This will trigger a refresh of the content based on the
original inputs found within `ds.locate()` details, accounting for corporate actions since the last run date.

### Deleting a Data Cache Universe

The final functionality you can perform is an operation to delete an existing data cache universe. To perform this step,
you will use the “.detele()” function.

Example

1. ds.delete(cache_name='my_first_data_cache')

A code output message will display:


_Detailed `.Locate()` API Information._

### Next Steps – Connect Data Cache Universe to Data Exploration Content

You can leverage the data cache universe as a starting point to join other Data Exploration Content to this base universe
during your research process.

Examples include:

- Joining Universe to Factset Fundamentals dataset
- Create alpha factors using the cached data warehouse universe.
- < Have the group identify some good examples – We could also reference other Notebooks if created>

---

## API Details

This section provides technical information about each method & functions available within the **fds.datax** Library. The
library contains consistent python argument syntax, along with detailed doc strings to provide you a more accessible
option to view information.

### Details of Module Functionality

The **fds.datax** library’s core methods are Universe, a method to define, retrieve and cache a universe, and GetSDFdata, a utility
method that assists the Universe method in creating, locating and reading the cache universe files.

- **Universe** - Underlying functions that locate, delete, create, rebuild and read from the data store
    - **locate** - view a catalog of your local data store universes
    - **delete** – delete a catalog of your local data store universes
    - **create** – create a new data store universe
    - **rebuild** – rebuild a data store universe
    - **read** - read in data files for a specific data store universe
- **GetSDFData** - Underlying functions used to retrieve symbology, prices, corporate actions, and currency rates.

### FDSArchive

#### Locate

The "fds.datax.universe.locate()" function finds a list of existing data cache universes from the default data store.

_Default_

1. locate(self)

_Returns_

```
pd.DataFrame - returns a Pandas DataFrame containing metadata pertaining to each data cache universe that 
has been created. This data displays the inputs that were passed in the “fds.datax.universe.create()” function. The

`Last Updated Date` is based on the local time of your Data Exploration Server.
```

If no data cache universes are found, an output message will display:

#### Delete

The "fds.datax.universe.delete()" function identifies a data cache universe and deletes the cache from the default data store.

_Default_

2. delete(self, cache_name='')

_Parameters_

```
cache_name (string) – A string parameter that will specify the cache name to be deleted.
```
```
Example - delete
```
1. delete(cache_name='my_first_data_cache')

_Returns_

```
Delete (string) - returns a Success message once the identified data cache universe has been removed.
```
#### Create

The "fds.datax.universe.create()" generates a new universe cache in the data store based on the FactSet Ownership data or
one supplied by the user in the form of a Pandas DataFrame. The data cache is saved in the default data store.

_Default_

1. create(self, option='generate',cache_name='', mssql_dsn='', etf_ticker='', currency='', start_date=''
    , end_date='', source ='sdf'):

_Parameters_

```
option (string) – A string parameter that excepts three valid values:
```
- generate – generates a universe data file for a given ETF identifier and time series.
- load – load a custom DataFrame containing a universe.

```
Generate Parameters
```
```
cache_name (string) – Unique name to define the collection of cache files
```

```
mssql_dsn (string) – DSN name for a connection to MSSQL Server DB containing FDS Standard DataFeeds
content.
curreny (string) – currency for pricing data to be return, if local currency is desired set to “LOCAL”
etf_ticker (string) – ETF-regional identifier used to retrieve information from FDS Ownership data
start_date (date - YYYY-MM-DD) – date for the start of the universe pull (first available)
end_date (date - YYYY-MM-DD) – date for the end of the universe pull (most recent)
source (string) – This references the ultimate source of the underlying data. ‘SDF’ represents the FactSet
Standard DataFeed. Future support will be developed for API sourced content.
```
```
Example
```
```
1. # Specify a cache name
2. cn = 'my_first_data_cache'
3.
4. # DSN name for a connection to a MSSQL Server DB containing FDS Standard DataFeeds content.
5. # `SDF` is the default as it connects to the FactSet Standard DataFeed data
6. mssql_dsn = 'SDF'
7.
8. # ETF ticker in a ticker-region format.
9. etf_ticker = 'SPY-US'
10.
11. # Currency for pricing data to be return, if local currency is desired set to "LOCAL"
12. currency = 'USD'
13.
14. # Earliest available report date in YYYY-MM-DD format
15. start_date = '2019- 01 - 01'
16.
17. # Most recent available report date to be returned in YYYY-MM-DD format
18. end_date = '2019- 12 - 31'
19.
20. # Call the `create()` function to generate a time-series universe.
21. ds.create('generate',cache_name = cn,
22. mssql_dsn = mssql_dsn,
23. etf_ticker = etf_ticker,
24. currency = currency,
25. start_date = start_date,
26. end_date = end_date)
```
```
Load Parameters
```
```
data (pd.DataFrame) – A pandas DataFrame containing a time series universe. File must include the following
headers:
```
- ref_id – such as ISIN, CUSIP, SEDOL, Ticker-region (AAPL-US) or Ticker-Exchange (AAPL-NAS)
- date – date in a YYYY-MM-DD format
**cache_name** (string) – Unique name to define the collection of cache files
**mssql_dsn** (string) – DSN name for a connection to MSSQL Server DB containing FDS Standard DataFeeds
content.
**curreny** (string) – currency for pricing data to be return, if local currency is desired set to “LOCAL”
**start_date** (date - YYYY-MM-DD) – date for the start of the universe pull (first available)

_Returns_

Return Type: string


```
Each option – Generate & Load – will return a string status message informing you that the universe was
generated or loaded in the data store.
```
#### Rebuild

The `fds.universe.rebuild()` function rebuilds an existing data cache universe leveraging the details contained in the fds
details file.

_Default_

1. rebuild(self, cache_name =''):

_Parameters_

```
cache_name (string) – A data cache universe name available in the default data store.
```
_Returns_

```
A string status message stating that the universe was rebuilt. To access the content created, utilize
“fds.universe.read()”
```
#### Read

The `fds.universe.read()` function will load a specific data cache universe and the respective data files specified.

_Default_

1. read(self, cache_name, option='universe', adj=1):

_Parameters_

```
cache_name (string) – A data cache universe in the available current data store.
```
```
option (string) – A string parameter that accepts four valid values:
```
- universe – load time series symbology information for a data cache universe
- sec ref – load security reference data for a data cache universe
- prices – load pricing data for a data cache universe. Choose unadjusted, split, or split & spin-off data
- corp actions – load corporate action factors for a data cache universe

```
adj (int) – A parameter that defines the adjustments that should be applied to the pricing data.
```
- 0 = unadjusted values
- 1 = split adjusted values
- 2 = split and spin-off adjusted values
- 3 = all types

```
Example 1 – universe
```
1. fds.sdf.read(option='universe',cache_name='my_first_data_cache').head()


```
Example 1 – sec ref
```
1. fds.sdf.read(option='sec ref',cache_name='my_first_data_cache').head()

```
Example 1 – prices
```
1. fds.sdf.read(option='prices',cache_name='my_first_data_cache',adj=2).head()

```
Example 1 – corp actions
```
1. fds.sdf.read(option='corp actions',cache_name='my_first_data_cache').head()

_Returns_

All four options – universe, sec ref, prices, and corp actions – return a Pandas DataFrame contain metadata that
pertains to the respective option.

```
“Universe” Returns
A Pandas DataFrame containing the data cached universe and FDS symbology:
```
- **ref_id** (string) – Unique FactSet-generated identifier representing a security level instrument
- **fsym_primary_listing_id** (string) – Most liquid individual listing for a security
- **fsym_primary_equity_id** (string) – FactSet Permanent Identifier representing the primary equity
    on the identifier’s most liquid exchange
- **date** (date) – Displays each date that the security is within the universe
- **proper_name** (string) – Name of the security associated with the identifier
- **factset_entity_id** (string) – Unique FactSet-generated identifier representing an entity

```
“Sec Ref” Returns
A Pandas DataFrame containing security reference data:
```
- **ref_id** (string) – Unique FactSet-generated identifier representing a security level instrument
- **factset_entity_id** (string) – Unique FactSet-generated identifier representing an entity
- **country** (string) – Common name of the Country
- **region** (string) - Textual description of the FactSet proprietary global region
- **rbics_l1** - RBICS level 1 textual description (Economy)
- **rbics_l2** - RBICS level 2 textual description (Sector)
- **rbics_l3** - RBICS level 3 textual description (Sub-Sector)
- **rbics_l4** - RBICS level 4 textual description (Industry Group)
- **rbics_l1_id** (string) – RBICS level 1 identifier (Economy)
- **rbics_l 2 _id** (string) – RBICS level 2 identifier (Sector)
- **rbics_l 3 _id** (string) – RBICS level 3 identifier (Sub-Sector)
- **rbics_l4_id** (string) – RBICS level 4 identifier (Industry Group)

```
“Prices” Returns
```
```
A Pandas DataFrame containing daily pricing information for the data cache universe:
```
- **ref_id** (string) – Unique FactSet-generated identifier representing a security level instrument
- **fsym_id** (string) – Unique FactSet-generated identifier representing a regional level instrument


- **price_date** (date) – Date on which the security is priced
- **currency** (string) – Code representing the currency in which the security trades
- **market_value** (double) – Number of shares outstanding _(in thousands)_ multiplied by closing
    price
- **one_day_total_returns** (double) - Returns the price performance of the security since the
    previous trade date
- **volume** (double) – Volume _(in thousands)_
- **shares_outstanding** (double) – Number of shares outstanding _(in thousands)_
- **price_close** (double) – Closing price
- **price_high** (double) – High price
- **price_low** (double) – Low price
- **price_open** (double) – Opening price

```
“Corp Actions” Returns
```
```
A Pandas DataFrame containing cumulative adjustment factors for splits and spin-offs for a universe:
```
- **ref_id** (string) – Unique FactSet-generated identifier representing a security level instrument
- **fsym_id** (string) – Unique FactSet-generated identifier representing a regional level instrument
- **price_date** (date) – Date on which the security is priced
- **cum_split_factor** (double) – cumulative split factor
- **cum_spin_factor** (double) – cumulative spinoff factor

### GetSDFData

The `GetSDFData` method is designed to streamline the retrieval of data from FactSet's Standard DataFeeds. Each
function is designed to retrieve a specific set of data items.

Main Features

- Utilize FactSet's Ownership Database to access historical ETF holdings as a baseline universe.
- Retrieve all levels of FactSet's Entity centric symbology model to all instance access to any content set within the
    Standard DataFeed ecosystem.
- Access baseline categorical information such as country of domicile, sector classifications, and other company
    specific meta data.
- Fetch prices (OHLC), 1 - day total returns, market cap, exchange rates, and corporate action adjustment ratios for
    a universe.

#### etf_universe

The `etf_universe` function returns the constituents of an ETF from FDS Ownership in a pandas DataFrame. ETF
Ownership is available on an annual, semi-annual, quarterly, or monthly frequency depending on the frequency of
filings. Data will be resampled daily by forward filling the data set.

_Default_

1. etf_universe(cls, etf_ticker, start_date, end_date, mssql_dsn):


_Parameters_
**etf_ticker** (string) – ETF identifier formatted in a ticker-region format. Example: SPY-US
**start_date** (date – YYYY-MM-DD) – earliest available report date in a YYYY-MM-DD format
**end_date** (date – YYYY-MM-DD) – most recent report date to be returned in a YYYY-MM-DD format
**mssql_dsn** (string) – The name of the DSN connection that has access to the FactSet Standard DataFeeds

_Returns_
A Pandas DataFrame containing:

- **ref_id** (string) – Unique FactSet-generated identifier representing a security level instrument
- **fsym_primary_listing_id** (string) – Most liquid individual listing for a security
- **fsym_primary_equity_id** (string) – FactSet Permanent Identifier representing the primary equity on the
    identifier’s most liquid exchange
- **date** (date) – Displays each date that the security is within the universe

#### fds_symbology

The `fds_symbology` function returns FDS symbology at the -R, -S, and -E level. Data at the -E level will be returned in a
point-in-time manner based on the date in the input data frame.

_Default_

1. fds_symbology(cls, univ_df, mssql_dsn, id_type='0', ref_id='ref_id', ref_date='date'):

_Parameters_
**univ_df** (pd.DataFrame) – an input Pandas DataFrame containing a market identifier or FDS identifier.
**mssql_dsn** (string) – DSN name for a connection to a MSSQL Server Database containing FDS Standard
DataFeeds content.
**id_type** (int) – flagged designating if the input identifier is a market identifier or FDS identifier
1 = Market ID (SEDOL, CUSIP, ISNIN – all must include a check digit)
2 = FactSet ID
**ref_id** (string) – column name within the univ_def file to identify the primary identifier field.
**ref_date** (date) – column name within the univ_def file to identify the primary date field.

_Returns_
A Pandas DataFrame containing:

- **ref_id** (string) – Unique FactSet-generated identifier representing a security level instrument
- **fsym_primary_listing_id** (string) – Most liquid individual listing for a security
- **fsym_primary_equity_id** (string) – FactSet Permanent Identifier representing the primary equity on the
    identifier’s most liquid exchange
- **date** (date) – Displays each date that the security is within the universe
- **adj_holding** (double) - Share amount held by the fund as of the report date, adjusted for corporate
    actions
- **proper_name** (string) – Name of the security associated with the identifier
- **factset_entity_id** (string) – Unique FactSet-generated identifier representing an entity


#### fds_sec_ref

The `fds_sec_ref` function returns current country and RBICS classifications level 1 through 4 for a specified universe.

_Default_

1. fds_sec_ref(cls, entity_id_list, mssql_dsn)

_Parameters_
**entity_id_list** (list) – a python list containing FactSet Entity identifiers for the universe. To retrieve FactSet Entity
identifiers, use the fds_smybology method.
**mssql_dsn** (string) – DSN name for a connection to a MSSQL Server Database containing FDS Standard
DataFeeds content.

_Returns_
A Pandas DataFrame containing:

- **factset_entity_id** (string) – Unique FactSet-generated identifier representing an entity
- **country** (string) – Common name of the Country
- **region** (string) - Textual description of the FactSet proprietary global region
- **rbics_l1** - RBICS level 1 textual description (Economy)
- **rbics_l2** - RBICS level 2 textual description (Sector)
- **rbics_l3** - RBICS level 3 textual description (SubSector)
- **rbics_l4** - RBICS level 4 textual description (IndustryGroup)
- **rbics_l1_id** (string) – RBICS level 1 identifier (Economy)
- **rbics_l2_id** (string) – RBICS level 2 identifier (Sector)
- **rbics_l3_id** (string) – RBICS level 3 identifier (Sub-Sector)
- **rbics_l4_id** (string) – RBICS level 4 identifier (Industry Group)

#### fds_fx_rates

The `fds_fx_rates` function returns daily exchange rates by converting the currency list to a common target currency.

_Default_

1. fds_fx_rates(cls, currency_list, target_currency, start_date, end_date, mssql_dsn):

_Parameters_
**curreny_list** (list) – a python list containing ISO-3 codes
**target_currency** (string) – the target currency value using an ISO-3 code
**start_date** (date – YYYY-MM-DD) – earliest FX rate to be returned in a YYYY-MM-DD format
**end_date** (date – YYYY-MM-DD) – most recent FX rate to be returned in a YYYY-MM-DD format

_Returns_
A Pandas DataFrame containing:

- **price_date** (date) – Date on which the security is priced
- **currency** (string) - Code representing the starting currency


- **currency_to** (string) – Code representing the currency into which the starting currency is being
    converted to
- **exch_rate_usd** (double) – Exchange rate – ISO_Currency in US Dollars
- **exch_rate_per_usd_to** (double) – Exchange rate – ISO _Currency per US Dollars
- **fx_rate** (double) – Foreign Exchange rate for the respective currency pair on p_date

#### fds_prices

The `fds_prices` function returns daily pricing information for the specified universe.

_Default_

1. fds_prices(cls, regional_id_list, start_date, end_date, currency, adjtype, mssql_dsn):

_Parameters_
**regional_id_list** (list) – a python list containing FactSet Entity identifiers for the universe. To retrieve FactSet
entity identifiers, use the fds_symbology method.
**start_date** (date – YYYY-MM-DD) – earliest date for which pricing data will be retrieved in a YYYY-MM-DD format
**end_date** (date – YYYY-MM-DD) – most recent date for which pricing data to be retrieved in a YYYY-MM-DD
format
**currency** (string) – the currency for pricing data to be returned using ISO-3 codes as the input. If local currency is
desired for each asset, set this input to “Local”.
**adjtype** (int) – specifies the type of pricing to be returned:

- 0 = unadjusted value
- 1 = split adjusted values
- 2 = split and spin-off adjusted values
- 3 = all types
**mssql_dsn** (string) – DSN name for a connection to a MSSQL Server DB containing FDS Standard DataFeeds
content.

_Returns_
A Pandas DataFrame containing:

- **ref_id** (string) – Unique FactSet-generated identifier representing a security level instrument
- **fsym_id** (string) – Unique FactSet-generated identifier representing a regional level instrument
- **price_date** (date) – Date on which the security is priced
- **currency** (string) – Code representing the currency in which the security trades
- **one_day_total_returns** (double) - Returns the price performance of the security since the previous
    trade date
- **volume** (double) – Volume _(in thousands)_
- **shares_outstanding** (double) – Number of shares outstanding _(in thousands)_
- **price_close** (double) – Closing price
- **price_high** (double) – High price
- **price_low** (double) – Low price
- **price_open** (double) – Opening price
- **market_value** (double) – Number of shares outstanding _(in thousands)_ multiplied by closing price


#### fds_corp_actions

The `fds_corp_actions` function returns cumulative adjustment factors for splits and spin-offs for a universe.

_Default_

1. fds_corp_actions(cls, regional_id_list, mssql_dsn):

_Parameters_
**regional_id_list** (list) – a python list containing FactSet Entity identifiers for the universe. To retrieve FactSet
entity identifiers, use the fds_symbology method.
**mssql_dsn** (string) – DSN name for a connection to a MSSQL Server DB containing FDS Standard DataFeeds
content.

_Returns_
A Pandas DataFrame containing:

- **ref_id** (string) – Unique FactSet-generated identifier representing a security level instrument
- **fsym_id** (string) – Unique FactSet-generated identifier representing a regional level instrument
- **price_date** (date) – Date on which the security is priced
- **cum_split_factor** (double) – cumulative split factor
- **cum_spin_factor** (double) – cumulative spinoff factor

## Considerations

Considerations and limitations in mind while using fds.datax:

```
1) Please keep in mind that saving out a universe will store all daily pricing, reference, and metadata for all assets
on your DX file storage container.
```
## Support / Questions / Feedback

For Python Library support, questions, or feedback, please file a bug report / feature request or speak with
your FactSet CTS representative.


