#!/bin/env python
# add your header here
""" Program to perform basic data
    quality check on meteorological 
    data and generating graphs
    highlighting the changes
    
    Author: Varun Aggarwal
    Username: aggarw82
    Github: https://github.com/Environmental-Informatics/09-data-quality-checking-aggarw82
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "Date", "Precip", "Max Temp", "Min Temp", "Wind Speed". Function
    returns the completed DataFrame, and a dictionary designed to contain all 
    missing value counts."""
    
    # define column names
    colNames = ['Date','Precip','Max Temp', 'Min Temp','Wind Speed']

    # open and read the file
    DataDF = pd.read_csv("DataQualityChecking.txt",
                            header=None, 
                            names=colNames,  
                            delimiter=r"\s+",
                            parse_dates=[0])
    DataDF = DataDF.set_index('Date')
    
    # define and initialize the missing data dictionary
    ReplacedValuesDF = pd.DataFrame(0, 
                                    index=["1. No Data"], 
                                    columns=colNames[1:])
     
    return( DataDF, ReplacedValuesDF )
 
def Check01_RemoveNoDataValues( DataDF, ReplacedValuesDF ):
    """This check replaces the defined No Data value with the NumPy NaN value
    so that further analysis does not use the No Data values.  Function returns
    the modified DataFrame and a count of No Data values replaced."""

    # add your code here
    DataDF = DataDF.replace(-999, np.NaN)

    # locate NaN for keeping record
    ReplacedValuesDF.loc["1. No Data", :] = DataDF.isna().sum()

    return( DataDF, ReplacedValuesDF )
    
def Check02_GrossErrors( DataDF, ReplacedValuesDF ):
    """This function checks for gross errors, values well outside the expected 
    range, and removes them from the dataset.  The function returns modified 
    DataFrames with data the has passed, and counts of data that have not 
    passed the check."""
 
    # add your code here

    # replace values with NaN for each column
    DataDF['Wind Speed'][(DataDF['Wind Speed'] <  0)] = np.NaN
    DataDF['Wind Speed'][(DataDF['Wind Speed'] > 10)] = np.NaN
    
    DataDF['Precip'][(DataDF['Precip'] <  0)] = np.NaN
    DataDF['Precip'][(DataDF['Precip'] > 25)] = np.NaN
    
    DataDF['Max Temp'][(DataDF['Max Temp'] < -25)] = np.NaN
    DataDF['Max Temp'][(DataDF['Max Temp'] >  35)] = np.NaN
    
    DataDF['Min Temp'][(DataDF['Min Temp'] < -25)] = np.NaN
    DataDF['Min Temp'][(DataDF['Min Temp'] >  35)] = np.NaN

    # count NaN values in ReplacesValuesDF
    count = ReplacedValuesDF.sum()
    ReplacedValuesDF.loc["2. Gross Error", :] = DataDF.isna().sum() - count

    return( DataDF, ReplacedValuesDF )
    
def Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture is less than
    minimum air temperature, and swaps the values when found.  The function 
    returns modified DataFrames with data that has been fixed, and with counts 
    of how many times the fix has been applied."""
    
    # add your code here

    counter = 0 # counter for tracking changes
    
    # iterate over all values of the dataframe
    for i in range(0,len(DataDF)-1):
        # swap the values 
        if DataDF.iloc[i,1] < DataDF.iloc[i,2]:
            DataDF.iloc[i,2] = DataDF.iloc[i,2] + DataDF.iloc[i,1]
            DataDF.iloc[i,1] = DataDF.iloc[i,2] - DataDF.iloc[i,1]
            DataDF.iloc[i,2] = DataDF.iloc[i,2] - DataDF.iloc[i,1]
            counter = counter + 1

    ReplacedValuesDF.loc["3. Swapped", :] = [0,counter,counter,0]
     
    return( DataDF, ReplacedValuesDF )
    
def Check04_TmaxTminRange( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture minus 
    minimum air temperature exceeds a maximum range, and replaces both values 
    with NaNs when found.  The function returns modified DataFrames with data 
    that has been checked, and with counts of how many days of data have been 
    removed through the process."""
    
    # add your code here

    counter = 0 # counter for tracking changes
    
    # iterate over all values of the dataframe
    for i in range(0,len(DataDF)-1):
        # swap the values if temperature range is more than 25
        if DataDF.iloc[i,1]  - DataDF.iloc[i,2] > 25:
            DataDF.iloc[i,1] = np.NaN
            DataDF.iloc[i,2] = np.NaN
            counter = counter + 1

    ReplacedValuesDF.loc["4. Range Fail", :] = [0,counter,counter,0]

    return( DataDF, ReplacedValuesDF )
    

# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    fileName = "DataQualityChecking.txt"
    DataDF, ReplacedValuesDF = ReadData(fileName)
    
    print("\nRaw data.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check01_RemoveNoDataValues( DataDF, ReplacedValuesDF )
    
    print("\nMissing values removed.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check02_GrossErrors( DataDF, ReplacedValuesDF )
    
    print("\nCheck for gross errors complete.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF )
    
    print("\nCheck for swapped temperatures complete.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check04_TmaxTminRange( DataDF, ReplacedValuesDF )
    
    print("\nAll processing finished.....\n", DataDF.describe())
    print("\nFinal changed values counts.....\n", ReplacedValuesDF)



    #read the initial file again to compare, RawData  
    fileName = "DataQualityChecking.txt"
    Data, DataReplacedValuesDF = ReadData(fileName)

    #Precip plot
    plt.plot(DataDF.index.values, Data['Precip'], 'r*-', label = "raw data") # Original Data
    plt.plot(DataDF.index.values, DataDF['Precip'], 'g*-', label = "corrected data") # Final Data
    plt.xlabel('Date')
    plt.ylabel('Precipitation (mm)')
    plt.title('Precipitation')
    plt.legend()
    plt.savefig('precip.png')
    plt.show()
    plt.close()

    #Max temp plot
    plt.plot(DataDF.index.values, Data['Max Temp'], 'r*-', label = "raw data") # Original Data
    plt.plot(DataDF.index.values, DataDF['Max Temp'], 'g*-', label = "corrected data") # Final Data
    plt.xlabel('Date')
    plt.ylabel('Max Temp(C)')
    plt.title('Maximum Temperature')
    plt.legend()
    plt.savefig('maxtemp.png')
    plt.show()
    plt.close()


    # Min temp plot
    plt.plot(DataDF.index.values, Data['Min Temp'], 'r*-', label = "raw data") # Original Data
    plt.plot(DataDF.index.values, DataDF['Min Temp'], 'g*-', label = "corrected data") # Final Data
    plt.xlabel('Date')
    plt.ylabel('Min Temp(C)')
    plt.title('Minimum Temperature')
    plt.legend()
    plt.savefig('mintemp.png')
    plt.show()
    plt.close()

    #Wind Speed plot
    plt.plot(DataDF.index.values, Data['Wind Speed'], 'r*-', label = "raw data") # Original Data
    plt.plot(DataDF.index.values, DataDF['Wind Speed'], 'g*-', label = "corrected data") # Final Data
    plt.xlabel('Date')
    plt.ylabel('Wind Speed (m/s)')
    plt.title('Wind Speed')
    plt.legend()
    plt.savefig('wind.png')
    plt.show()
    plt.close()

    # saving final data
    DataDF.to_csv("Clean_Data.txt", sep = " ", header = None)
    ReplacedValuesDF.to_csv("Stats_for_DQC.txt", sep = "\t")