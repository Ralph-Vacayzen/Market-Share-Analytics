import streamlit as st
import pandas as pd
import numpy as np










st.set_page_config(page_title='Market Share Analytics', page_icon='📊', layout="wide", initial_sidebar_state="auto", menu_items=None)










def Style_Uploaded_And_Nonuploaded_Files(filename):
        color = '#C1E1C1' if filename not in missing else '#FAA0A0'
        return f'background-color: {color}'
    
def Get_Dates_From_Range(row):
        dates = pd.date_range(row.RentalAgreementStartDate, row.RentalAgreementEndDate, normalize=True).values
        return set(map(lambda x: pd.to_datetime(x).date(), dates))

def Style_Negative_And_Positive_Values(value):
    if   value > 0: return 'background-color: #C1E1C1'
    elif value < 0: return 'background-color: #FAA0A0'

def Get_Actual_Adjustment(row):
        match row.Type:
            case 'Initial Load':
                return row.Count
            case 'New Inventory':
                return row.Count
            case 'Rental Location Change':
                return row.Count
            case 'Retire':
                return row.Count * -1
            case 'Sold':
                return row.Count * -1
            case _:
                st.toast('Undefined type detected.')










st.caption('VACAYZEN')
st.title('Market Share Analytics')
st.info('Analysis of business areas to determine change in market share.')





l, r     = st.columns(2)

p1_start = l.date_input('**Period 1** Start', key='p1_start', value=pd.to_datetime(f'1/1/{pd.to_datetime('today').year}'))
p1_end   = r.date_input('**Period 1** End',   key='p1_end',   value=pd.to_datetime('today'), max_value=pd.to_datetime('today'))

p2_start = l.date_input('**Period 2** Start', key='p2_start', value=pd.to_datetime(f'{p1_start.month}/{p1_start.day}/{p1_start.year - 1}'))
p2_end   = r.date_input('**Period 2** End',   key='p2_end',   value=pd.to_datetime(f'{p1_end.month}/{p1_end.day}/{p1_end.year - 1}'))

p1_dates = pd.date_range(p1_start, p1_end)
p2_dates = pd.date_range(p2_start, p2_end)

ranges   = [p1_dates, p2_dates]










with st.expander('Uploaded Files', expanded=True):
    
    file_descriptions = [
        ['SWBSA Market Share Analysis','Export_ExportRentalsByDay.csv','An SWBSA integraRental export, Rentals By Day.'],
        ['Inventory Analysis','Inventory Adjustments.csv','An integraSoft database export, Inventory Adjustments.'],
        ['House Bike Analysis','Partner Program Register (PPR) - REGISTER.csv','An export from the Vacayzen Partner Progrom Register, REGISTER tab.']

    ]

    files = {
        'Export_ExportRentalsByDay.csv': None,
        'Inventory Adjustments.csv': None,
        'Partner Program Register (PPR) - REGISTER.csv': None
    }


    uploaded_files = st.file_uploader(
        label='Files (' + str(len(files)) + ')',
        accept_multiple_files=True
    )

    st.info('File names are **case sensitive** and **must be identical** to the file name below.')

    missing = []

    if len(uploaded_files) > 0:
        for index, file in enumerate(uploaded_files):
            files[file.name] = index

        hasAllRequiredFiles = True

        for file in files:
            if files[file] == None:
                hasAllRequiredFiles = False
                missing.append(file)
    
    if missing != []:
        st.dataframe(pd.DataFrame(file_descriptions, columns=['Area of Interest','Required File','File Source Location']).style.applymap(Style_Uploaded_And_Nonuploaded_Files, subset=['Required File']), hide_index=True, use_container_width=True)
    else:
        st.dataframe(pd.DataFrame(file_descriptions, columns=['Area of Interest','Required File','File Source Location']), hide_index=True, use_container_width=True)










def SWBSA_Analytics(swbsa):
    st.toast('Looking into SWBSA...')
    swbsa.RentalAgreementStartDate = pd.to_datetime(swbsa.RentalAgreementStartDate).dt.date
    swbsa.RentalAgreementEndDate   = pd.to_datetime(swbsa.RentalAgreementEndDate).dt.date

    swbsa['Dates'] = swbsa.apply(Get_Dates_From_Range, axis=1)

    results = []

    for i, range in enumerate(ranges, 1):
        st.toast(f'Looking into SWBSA... Period {i}...')

        market   = []
        vacayzen = []

        for date in range:

            date_sets        = swbsa[[date.date() in d for d in swbsa.Dates]]
            date_sets        = date_sets.rename(columns={'Description':'Beach Access', 'Quantity':str(date.date())})
            
            market_result    = date_sets.groupby('Beach Access', group_keys=True)[str(date.date())].apply(sum)

            vacayzen_sets    = date_sets[date_sets.RentalCompanyName == 'VACAYZEN']

            vacayzen_result  = vacayzen_sets.groupby('Beach Access', group_keys=True)[str(date.date())].apply(sum)

            market.append(market_result)
            vacayzen.append(vacayzen_result)
        
        market_final   = pd.concat(market,   axis=1)
        vacayzen_final = pd.concat(vacayzen, axis=1)

        market_final[f'Period {i}: Market']   = market_final.sum(axis=1)
        vacayzen_final[f'Period {i}: Vacayzen'] = vacayzen_final.sum(axis=1)

        market_final   = market_final[[f'Period {i}: Market']]
        vacayzen_final = vacayzen_final[[f'Period {i}: Vacayzen']]

        result = pd.concat([market_final, vacayzen_final], axis=1).fillna(0)
        result[f'Period {i}: Share'] = round((result[f'Period {i}: Vacayzen'] / result[f'Period {i}: Market']) * 100, 2)
        result = result.sort_index()

        results.append(result)
    
    final                = pd.concat(results, axis=1).fillna(0)
    final['Share Delta'] = final['Period 1: Share'] - final['Period 2: Share']

    l, m, r = st.columns(3)
    l.metric('**Market** Sets',   np.sum(final['Period 1: Market']),   np.sum(final['Period 1: Market'])   - np.sum(final['Period 2: Market']))
    m.metric('**Vacayzen** Sets', np.sum(final['Period 1: Vacayzen']), np.sum(final['Period 1: Vacayzen']) - np.sum(final['Period 2: Vacayzen']))
    r.metric('**Vacayzen Market Share**', f'{round(np.average(final['Period 1: Share']), 2)}%', f'{round(np.average(final['Period 1: Share']) - np.average(final['Period 2: Share']), 2)}%')

    st.dataframe(final.style.applymap(Style_Negative_And_Positive_Values, subset=['Share Delta']).format("{:.2f}"), use_container_width=True)
    st.toast('Looking into SWBSA... COMPLETE')










def Inventory_Analytics(inventory):
    df               = inventory
    df.columns       = ['Date','Product','Asset','Count','Type']
    df.Date          = pd.to_datetime(df.Date).dt.date
    df               = df.sort_values(['Date'])
    df['Adjustment'] = df.apply(Get_Actual_Adjustment, axis=1)

    l, r = st.columns(2)
    inventory_p1_date = l.date_input('Period 1 Date', value=p1_end)
    inventory_p2_date = r.date_input('Period 2 Date', value=p2_end)
    assets            = st.multiselect('Asset of Interest', df.Asset.unique())

    p1_assets = {}
    p2_assets = {}

    def Get_Inventory_At_Date(row):
        if row.Date <= inventory_p1_date:
            if row.Asset in p1_assets.keys():
                p1_assets[row.Asset] += row.Adjustment
            else:
                p1_assets[row.Asset]  = row.Adjustment
        if row.Date <= inventory_p2_date:
            if row.Asset in p2_assets.keys():
                p2_assets[row.Asset] += row.Adjustment
            else:
                p2_assets[row.Asset]  = row.Adjustment
        

    df.apply(Get_Inventory_At_Date, axis=1)

    p1_df = pd.DataFrame.from_dict(p1_assets, orient='index', columns=[str(inventory_p1_date)])
    p2_df = pd.DataFrame.from_dict(p2_assets, orient='index', columns=[str(inventory_p2_date)])

    idf   = pd.concat([p1_df, p2_df], axis=1)

    def Get_Difference_In_Count(row):
        return row[str(inventory_p1_date)] - row[str(inventory_p2_date)]
    
    def Get_Delta_In_Count(row):
        return round(((row[str(inventory_p1_date)] - row[str(inventory_p2_date)]) / row[str(inventory_p1_date)]) * 100, 2)
    
    idf['Difference'] = idf.apply(Get_Difference_In_Count, axis=1)
    idf['Delta %'] = idf.apply(Get_Delta_In_Count, axis=1)
    idf = idf[idf.index.isin(assets)]

    if assets != []:
        st.dataframe(idf.style.applymap(Style_Negative_And_Positive_Values, subset=['Difference']).format("{:.0f}"), use_container_width=True)
        









def House_Bike_Analytics(house_bikes):
    df          = house_bikes
    df          = df[['PARTNER','UNIT CODE','NAME','AREA','ADDRESS','ORDER #','# OF BIKES','BIKE TYPE','BIKE START DATE','BIKE END DATE']]
    df.columns  = ['Partner','Unit','Name','Area','Address','Order','Count','Type','Start','End']
    df          = df[df.Count > 0]
    df['Start'] = pd.to_datetime(df['Start']).dt.date
    df['End']   = df['End'].fillna(pd.to_datetime('12/31/2099', errors='coerce'))
    df['End']   = pd.to_datetime(df['End']).dt.date

    df1 = df[
        ((df.Start <= p1_start) & ((p1_start <= df.End) & (df.End <= p1_end))) |
        (((p1_start <= df.Start) & (df.Start <= p1_end)) & ((p1_start <= df.End) & (df.End <= p1_end))) |
        (((p1_start <= df.Start) & (df.Start <= p1_end)) & (p1_end <= df.End)) |
        ((df.Start <= p1_start) & (p1_end <= df.End))
        ]
    
    df1 = df1.groupby('Partner').sum(numeric_only=True)
    df1 = df1[['Count']]
    df1.columns = [f'{p1_start} - {p1_end}']

    df2 = df[
        ((df.Start <= p2_start) & ((p2_start <= df.End) & (df.End <= p2_end))) |
        (((p2_start <= df.Start) & (df.Start <= p2_end)) & ((p2_start <= df.End) & (df.End <= p2_end))) |
        (((p2_start <= df.Start) & (df.Start <= p2_end)) & (p2_end <= df.End)) |
        ((df.Start <= p2_start) & (p2_end <= df.End))
        ]
    
    df2 = df2.groupby('Partner').sum(numeric_only=True)
    df2 = df2[['Count']]
    df2.columns = [f'{p2_start} - {p2_end}']

    hbdf = pd.concat([df1, df2], axis=1)

    def HB_Get_Difference_In_Count(row):
        return row[f'{p1_start} - {p1_end}'] - row[f'{p2_start} - {p2_end}']
    
    def HB_Get_Delta_In_Count(row):
        return round(((row[f'{p1_start} - {p1_end}'] - row[f'{p2_start} - {p2_end}']) / row[f'{p1_start} - {p1_end}']) * 100, 2)
    
    hbdf['Difference'] = hbdf.apply(HB_Get_Difference_In_Count, axis=1)
    hbdf['Delata %']   = hbdf.apply(HB_Get_Delta_In_Count, axis=1)

    st.dataframe(hbdf.style.applymap(Style_Negative_And_Positive_Values, subset=['Difference']).format("{:.0f}"), use_container_width=True)













if files['Export_ExportRentalsByDay.csv'] is not None:
    swbsa = pd.read_csv(uploaded_files[files['Export_ExportRentalsByDay.csv']], index_col=False)
    with st.expander('**SWBSA Market Share Analysis**'):
        SWBSA_Analytics(swbsa)


if files['Inventory Adjustments.csv'] is not None:
    inventory = pd.read_csv(uploaded_files[files['Inventory Adjustments.csv']], index_col=False)
    with st.expander('**Inventory Analysis**'):
        Inventory_Analytics(inventory)


if files['Partner Program Register (PPR) - REGISTER.csv'] is not None:
    house_bikes = pd.read_csv(uploaded_files[files['Partner Program Register (PPR) - REGISTER.csv']], index_col=False)
    with st.expander('**House Bike Analysis**'):
        House_Bike_Analytics(house_bikes)