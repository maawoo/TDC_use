'''
Description: This file contains a set of python functions for computing
remote sensing band indices on Digital Earth Australia data.

License: The code in this notebook is licensed under the Apache License,
Version 2.0 (https://www.apache.org/licenses/LICENSE-2.0). Digital Earth
Australia data is licensed under the Creative Commons by Attribution 4.0
license (https://creativecommons.org/licenses/by/4.0/).

Contact: If you need assistance, please post a question on the Open Data
Cube Slack channel (http://slack.opendatacube.org/) or on the GIS Stack
Exchange (https://gis.stackexchange.com/questions/ask?tags=open-data-cube)
using the `open-data-cube` tag (you can view previously asked questions
here: https://gis.stackexchange.com/questions/tagged/open-data-cube).

If you would like to report an issue with this script, you can file one
on Github (https://github.com/GeoscienceAustralia/dea-notebooks/issues/new).

Last modified: March 2021

========

Source: https://github.com/GeoscienceAustralia/dea-notebooks/blob/4407ec801289fc07dd8d3a8ffe53854ee851b8b5/Tools/dea_tools/bandindices.py
Modified for easier use with datasets that were processed with FORCE / ARDCube for the Thuringian Data Cube.
https://github.com/maawoo/ARDCube

Marco Wolsza (April 2021)

'''

import warnings
import numpy as np


def optical(ds,
            index=None,
            custom_varname=None,
            normalise=True,
            drop=False,
            inplace=False):
    """
    Takes an xarray dataset containing spectral bands, calculates one of
    a set of remote sensing indices, and adds the resulting array as a 
    new variable in the original dataset.  
    
    Note: by default, this function will create a new copy of the data
    in memory. This can be a memory-expensive operation, so to avoid
    this, set `inplace=True`.

    Last modified: March 2021
    
    Parameters
    ----------
    ds : xarray Dataset
        A two-dimensional or multi-dimensional array with containing the
        spectral bands required to calculate the index. These bands are
        used as inputs to calculate the selected water index.
    index : str or list of strs
        A string giving the name of the index to calculate or a list of
        strings giving the names of the indices to calculate:
        'AWEI_ns (Automated Water Extraction Index,
                  no shadows, Feyisa 2014)
        'AWEI_sh' (Automated Water Extraction Index,
                   shadows, Feyisa 2014)
        'BAEI' (Built-Up Area Extraction Index, Bouzekri et al. 2015)
        'BAI' (Burn Area Index, Martin 1998)
        'BSI' (Bare Soil Index, Rikimaru et al. 2002)
        'BUI' (Built-Up Index, He et al. 2010)
        'CMR' (Clay Minerals Ratio, Drury 1987)
        'EVI' (Enhanced Vegetation Index, Huete 2002)
        'FMR' (Ferrous Minerals Ratio, Segal 1982)
        'IOR' (Iron Oxide Ratio, Segal 1982)
        'LAI' (Leaf Area Index, Boegh 2002)
        'MNDWI' (Modified Normalised Difference Water Index, Xu 1996)
        'MSAVI' (Modified Soil Adjusted Vegetation Index,
                 Qi et al. 1994)              
        'NBI' (New Built-Up Index, Jieli et al. 2010)
        'NBR' (Normalised Burn Ratio, Lopez Garcia 1991)
        'NDBI' (Normalised Difference Built-Up Index, Zha 2003)
        'NDMI' (Normalised Difference Moisture Index, Gao 1996)        
        'NDSI' (Normalised Difference Snow Index, Hall 1995)
        'NDTI' (Normalise Difference Tillage Index,
                Van Deventeret et al. 1997)
        'NDVI' (Normalised Difference Vegetation Index, Rouse 1973)
        'NDWI' (Normalised Difference Water Index, McFeeters 1996)
        'SAVI' (Soil Adjusted Vegetation Index, Huete 1988)
        'TCB' (Tasseled Cap Brightness, Crist 1985)
        'TCG' (Tasseled Cap Greeness, Crist 1985)
        'TCW' (Tasseled Cap Wetness, Crist 1985)
        'WI' (Water Index, Fisher 2016)
        'kNDVI' (Non-linear Normalised Difference Vegation Index,
                 Camps-Valls et al. 2021)
    custom_varname : str, optional
        By default, the original dataset will be returned with 
        a new index variable named after `index` (e.g. 'NDVI'). To 
        specify a custom name instead, you can supply e.g. 
        `custom_varname='custom_name'`. Defaults to None, which uses
        `index` to name the variable. 
    normalise : bool, optional
        Some coefficient-based indices (e.g. 'WI', 'BAEI', 'AWEI_ns', 
        'AWEI_sh', 'TCW', 'TCG', 'TCB', 'EVI', 'LAI', 'SAVI', 'MSAVI') 
        produce different results if surface reflectance values are not 
        scaled between 0.0 and 1.0 prior to calculating the index. 
        Setting `normalise=True` first scales values to a 0.0-1.0 range
        by dividing by 10000.0. Defaults to True.  
    drop : bool, optional
        Provides the option to drop the original input data, thus saving
        space. if drop = True, returns only the index and its values.
    inplace: bool, optional
        If `inplace=True`, calculate_indices will modify the original
        array in-place, adding bands to the input dataset. The default
        is `inplace=False`, which will instead make a new copy of the
        original data (and use twice the memory).
        
    Returns
    -------
    ds : xarray Dataset
        The original xarray Dataset inputted into the function, with a 
        new varible containing the remote sensing index as a DataArray.
        If drop = True, the new variable/s as DataArrays in the 
        original Dataset. 
    """
    
    # Set ds equal to a copy of itself in order to prevent the function 
    # from editing the input dataset. This can prevent unexpected
    # behaviour though it uses twice as much memory.    
    if not inplace:
        ds = ds.copy(deep=True)
    
    # Capture input band names in order to drop these if drop=True
    if drop:
        bands_to_drop=list(ds.data_vars)
        print(f'Dropping bands {bands_to_drop}')

    # Dictionary containing remote sensing index band recipes
    index_dict = {
        # Normalised Difference Vegation Index, Rouse 1973
        'NDVI': lambda ds: (ds.nir - ds.red) /
                            (ds.nir + ds.red),
        
        # Non-linear Normalised Difference Vegation Index,
        # Camps-Valls et al. 2021
        'kNDVI': lambda ds: np.tanh(((ds.nir - ds.red) /
                                    (ds.nir + ds.red)) ** 2),

        # Enhanced Vegetation Index, Huete 2002
        'EVI': lambda ds: ((2.5 * (ds.nir - ds.red)) /
                            (ds.nir + 6 * ds.red -
                            7.5 * ds.blue + 1)),

        # Leaf Area Index, Boegh 2002
        'LAI': lambda ds: (3.618 * ((2.5 * (ds.nir - ds.red)) /
                            (ds.nir + 6 * ds.red -
                            7.5 * ds.blue + 1)) - 0.118),

        # Soil Adjusted Vegetation Index, Huete 1988
        'SAVI': lambda ds: ((1.5 * (ds.nir - ds.red)) /
                            (ds.nir + ds.red + 0.5)),
      
        # Mod. Soil Adjusted Vegetation Index, Qi et al. 1994
        'MSAVI': lambda ds: ((2 * ds.nir + 1 - 
                            ((2 * ds.nir + 1)**2 - 
                            8 * (ds.nir - ds.red))**0.5) / 2),    

        # Normalised Difference Moisture Index, Gao 1996
        'NDMI': lambda ds: (ds.nir - ds.swir1) /
                            (ds.nir + ds.swir1),

        # Normalised Burn Ratio, Lopez Garcia 1991
        'NBR': lambda ds: (ds.nir - ds.swir2) /
                            (ds.nir + ds.swir2),

        # Burn Area Index, Martin 1998
        'BAI': lambda ds: (1.0 / ((0.10 - ds.red) ** 2 +
                            (0.06 - ds.nir) ** 2)),


        # Normalised Difference Snow Index, Hall 1995
        'NDSI': lambda ds: (ds.green - ds.swir1) /
                            (ds.green + ds.swir1),

        # Normalised Difference Tillage Index,
        # Van Deventer et al. 1997
        'NDTI': lambda ds: (ds.swir1 - ds.swir2) /
                            (ds.swir1 + ds.swir2),

         # Normalised Difference Water Index, McFeeters 1996
        'NDWI': lambda ds: (ds.green - ds.nir) /
                            (ds.green + ds.nir),

        # Modified Normalised Difference Water Index, Xu 2006
        'MNDWI': lambda ds: (ds.green - ds.swir1) /
                            (ds.green + ds.swir1),
      
        # Normalised Difference Built-Up Index, Zha 2003
         'NDBI': lambda ds: (ds.swir1 - ds.nir) /
                             (ds.swir1 + ds.nir),
      
        # Built-Up Index, He et al. 2010
        'BUI': lambda ds:  ((ds.swir1 - ds.nir) /
                             (ds.swir1 + ds.nir)) -
                            ((ds.nir - ds.red) /
                             (ds.nir + ds.red)),
      
        # Built-up Area Extraction Index, Bouzekri et al. 2015
        'BAEI': lambda ds: (ds.red + 0.3) /
                         (ds.green + ds.swir1),
      
        # New Built-up Index, Jieli et al. 2010
        'NBI': lambda ds: (ds.swir1 + ds.red) / ds.nir,
      
        # Bare Soil Index, Rikimaru et al. 2002
        'BSI': lambda ds: ((ds.swir1 + ds.red) - 
                         (ds.nir + ds.blue)) / 
                          ((ds.swir1 + ds.red) + 
                          (ds.nir + ds.blue)),

        # Automated Water Extraction Index (no shadows), Feyisa 2014
        'AWEI_ns': lambda ds: (4 * (ds.green - ds.swir1) -
                            (0.25 * ds.nir * + 2.75 * ds.swir2)),

        # Automated Water Extraction Index (shadows), Feyisa 2014
        'AWEI_sh': lambda ds: (ds.blue + 2.5 * ds.green -
                             1.5 * (ds.nir + ds.swir1) -
                              0.25 * ds.swir2),

        # Water Index, Fisher 2016
        'WI': lambda ds: (1.7204 + 171 * ds.green + 3 * ds.red -
                        70 * ds.nir - 45 * ds.swir1 -
                         71 * ds.swir2),

        # Tasseled Cap Wetness, Crist 1985
        'TCW': lambda ds: (0.0315 * ds.blue + 0.2021 * ds.green +
                            0.3102 * ds.red + 0.1594 * ds.nir +
                        -0.6806 * ds.swir1 + -0.6109 * ds.swir2),

        # Tasseled Cap Greeness, Crist 1985
        'TCG': lambda ds: (-0.1603 * ds.blue + -0.2819 * ds.green +
                         -0.4934 * ds.red + 0.7940 * ds.nir +
                         -0.0002 * ds.swir1 + -0.1446 * ds.swir2),

        # Tasseled Cap Brightness, Crist 1985
        'TCB': lambda ds: (0.2043 * ds.blue + 0.4158 * ds.green +
                           0.5524 * ds.red + 0.5741 * ds.nir +
                          0.3124 * ds.swir1 + -0.2303 * ds.swir2),

        # Clay Minerals Ratio, Drury 1987
        'CMR': lambda ds: (ds.swir1 / ds.swir2),
        
        # Ferrous Minerals Ratio, Segal 1982
        'FMR': lambda ds: (ds.swir1 / ds.nir),

        # Iron Oxide Ratio, Segal 1982
        'IOR': lambda ds: (ds.red / ds.blue)
    }
    
    # If index supplied is not a list, convert to list. This allows us to
    # iterate through either multiple or single indices in the loop below
    indices = index if isinstance(index, list) else [index]
    
    #calculate for each index in the list of indices supplied (indexes)
    for index in indices:

        # Select an index function from the dictionary
        index_func = index_dict.get(str(index))

        # If no index is provided or if no function is returned due to an 
        # invalid option being provided, raise an exception informing user to 
        # choose from the list of valid options
        if index is None:

            raise ValueError(f"No remote sensing `index` was provided. Please "
                              "refer to the function \ndocumentation for a full "
                              "list of valid options for `index` (e.g. 'NDVI')")

        elif (index in ['WI', 'BAEI', 'AWEI_ns', 'AWEI_sh', 'TCW', 
                        'TCG', 'TCB', 'EVI', 'LAI', 'SAVI', 'MSAVI'] 
              and not normalise):

            warnings.warn(f"\nA coefficient-based index ('{index}') normally "
                           "applied to surface reflectance values in the \n"
                           "0.0-1.0 range was applied to values in the 0-10000 "
                           "range. This can produce unexpected results; \nif "
                           "required, resolve this by setting `normalise=True`")

        elif index_func is None:

            raise ValueError(f"The selected index '{index}' is not one of the "
                              "valid remote sensing index options. \nPlease "
                              "refer to the function documentation for a full "
                              "list of valid options for `index`")

        # Apply index function 
        try:
            # If normalised=True, divide data by 10,000 before applying func
            mult = 10000.0 if normalise else 1.0
            index_array = index_func(ds / mult)
            
        except AttributeError:
            raise ValueError(f'Please verify that all bands required to '
                             f'compute {index} are present in `ds`. \n')

        # Add as a new variable in dataset
        output_band_name = custom_varname if custom_varname else index
        ds[output_band_name] = index_array
    
    # Once all indexes are calculated, drop input bands if inplace=False
    if drop and not inplace:
        ds = ds.drop(bands_to_drop)

    # If inplace == True, delete bands in-place instead of using drop
    if drop and inplace:
        for band_to_drop in bands_to_drop:
            del ds[band_to_drop]

    return ds


def sar(ds,
        index=None,
        custom_varname=None,
        drop=False,
        inplace=False):
    """
    Takes an xarray dataset containing spectral bands, calculates one of
    a set of remote sensing indices, and adds the resulting array as a 
    new variable in the original dataset.  
    
    Note: by default, this function will create a new copy of the data
    in memory. This can be a memory-expensive operation, so to avoid
    this, set `inplace=True`.

    Last modified: May 2021
    
    Parameters
    ----------
    ds : xarray Dataset
        A two-dimensional or multi-dimensional array with containing the
        spectral bands required to calculate the index. These bands are
        used as inputs to calculate the selected water index.
    index : str or list of strs
        A string giving the name of the index to calculate or a list of
        strings giving the names of the indices to calculate:
        
    custom_varname : str, optional
        By default, the original dataset will be returned with 
        a new index variable named after `index` (e.g. 'NDVI'). To 
        specify a custom name instead, you can supply e.g. 
        `custom_varname='custom_name'`. Defaults to None, which uses
        `index` to name the variable. 
    drop : bool, optional
        Provides the option to drop the original input data, thus saving
        space. if drop = True, returns only the index and its values.
    inplace: bool, optional
        If `inplace=True`, calculate_indices will modify the original
        array in-place, adding bands to the input dataset. The default
        is `inplace=False`, which will instead make a new copy of the
        original data (and use twice the memory).
        
    Returns
    -------
    ds : xarray Dataset
        The original xarray Dataset inputted into the function, with a 
        new varible containing the remote sensing index as a DataArray.
        If drop = True, the new variable/s as DataArrays in the 
        original Dataset. 
    """
    
    # Set ds equal to a copy of itself in order to prevent the function 
    # from editing the input dataset. This can prevent unexpected
    # behaviour though it uses twice as much memory.    
    if not inplace:
        ds = ds.copy(deep=True)
    
    # Capture input band names in order to drop these if drop=True
    if drop:
        bands_to_drop=list(ds.data_vars)
        print(f'Dropping bands {bands_to_drop}')
        
    # Dictionary containing remote sensing index band recipes
    index_dict = {
        
        # Simple VH/VV ratio
        'VHVV': lambda ds: ds.VH / ds.VV,
        
        # Simple VV/VH ratio
        'VVVH': lambda ds: ds.VV / ds.VH
        
        #...?
        
    }
    
    # If index supplied is not a list, convert to list. This allows us to
    # iterate through either multiple or single indices in the loop below
    indices = index if isinstance(index, list) else [index]
    
    #calculate for each index in the list of indices supplied (indexes)
    for index in indices:

        # Select an index function from the dictionary
        index_func = index_dict.get(str(index))

        # If no index is provided or if no function is returned due to an 
        # invalid option being provided, raise an exception informing user to 
        # choose from the list of valid options
        if index is None:

            raise ValueError(f"No remote sensing `index` was provided. Please "
                              "refer to the function \ndocumentation for a full "
                              "list of valid options for `index` (e.g. 'NDVI')")

        elif index_func is None:

            raise ValueError(f"The selected index '{index}' is not one of the "
                              "valid remote sensing index options. \nPlease "
                              "refer to the function documentation for a full "
                              "list of valid options for `index`")

        # Apply index function 
        try:
            index_array = index_func(ds)
            
        except AttributeError:
            raise ValueError(f'Please verify that all bands required to '
                             f'compute {index} are present in `ds`. \n')

        # Add as a new variable in dataset
        output_band_name = custom_varname if custom_varname else index
        ds[output_band_name] = index_array
    
    # Once all indexes are calculated, drop input bands if inplace=False
    if drop and not inplace:
        ds = ds.drop(bands_to_drop)

    # If inplace == True, delete bands in-place instead of using drop
    if drop and inplace:
        for band_to_drop in bands_to_drop:
            del ds[band_to_drop]

    return ds
    