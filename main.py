import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title='Market-share Analytics', page_icon='📊', layout="wide", initial_sidebar_state="auto", menu_items=None)





st.caption('VACAYZEN')
st.title('Market-share Analytics')
st.info('Analysis of business areas to determine change in market share.')





l, r     = st.columns(2)

p1_start = l.date_input('**Period 1** Start', key='p1_start', value=pd.to_datetime(f'1/1/{pd.to_datetime('today').year}'))
p1_end   = r.date_input('**Period 1** End',   key='p1_end',   value=pd.to_datetime('today'), max_value=pd.to_datetime('today'))

p2_start = l.date_input('**Period 2** Start', key='p2_start', value=pd.to_datetime(f'{p1_start.month}/{p1_start.day}/{p1_start.year - 1}'))
p2_end   = r.date_input('**Period 2** End',   key='p2_end',   value=pd.to_datetime(f'{p1_end.month}/{p1_end.day}/{p1_end.year - 1}'))

p1_dates = pd.date_range(p1_start, p1_end)
p2_dates = pd.date_range(p2_start, p2_end)

ranges   = [p1_dates, p2_dates]










with st.expander('Uploaded Files'):
    
    file_descriptions = [
        ['SWBSA Market Share Analysis', 'Export_ExportRentalsByDay.csv','An SWBSA integraRental export, Rentals By Day.']
    ]

    files = {
        'Export_ExportRentalsByDay.csv': None
    }


    uploaded_files = st.file_uploader(
        label='Files (' + str(len(files)) + ')',
        accept_multiple_files=True
    )

    st.info('File names are **case sensitive** and **must be identical** to the file name below.')
    st.dataframe(pd.DataFrame(file_descriptions, columns=['Area of Interest','Required File','File Source Location']), hide_index=True, use_container_width=True)









def Get_Dates_From_Range(row):
        dates = pd.date_range(row.RentalAgreementStartDate, row.RentalAgreementEndDate, normalize=True).values
        return set(map(lambda x: pd.to_datetime(x).date(), dates))

def Style_Negative_And_Positive_Values(value):
    color = '#50C878' if value >= 0 else '#DE3163'
    return f'background-color: {color}'










def SWBSA_Analytics(swbsa):
    st.subheader('SWBSA Market Share Analysis')
    swbsa.RentalAgreementStartDate = pd.to_datetime(swbsa.RentalAgreementStartDate).dt.date
    swbsa.RentalAgreementEndDate   = pd.to_datetime(swbsa.RentalAgreementEndDate).dt.date

    swbsa['Dates'] = swbsa.apply(Get_Dates_From_Range, axis=1)

    results = []

    for i, range in enumerate(ranges, 1):

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
    
    final = pd.concat(results, axis=1).fillna(0)
    final['Share Delta'] = final['Period 1: Share'] - final['Period 2: Share']

    l, m, r = st.columns(3)
    l.metric('**Market** Sets',   np.sum(final['Period 1: Market']),   np.sum(final['Period 1: Market'])   - np.sum(final['Period 2: Market']))
    m.metric('**Vacayzen** Sets', np.sum(final['Period 1: Vacayzen']), np.sum(final['Period 1: Vacayzen']) - np.sum(final['Period 2: Vacayzen']))
    r.metric('**Vacayzen Market Share**', f'{round(np.average(final['Period 1: Share']), 2)}%', f'{round(np.average(final['Period 1: Share']) - np.average(final['Period 2: Share']), 2)}%')

    st.dataframe(final.style.applymap(Style_Negative_And_Positive_Values, subset=['Share Delta']).format("{:.2f}"), use_container_width=True)

    





    # for date in p1_dates:

    #     datesets = swbsa[[date.date() in d for d in swbsa.Dates]]
    #     datesets = datesets.rename(columns={'Description':'Beach Access', 'Quantity':str(date.date())})
    #     datesets = datesets[datesets.RentalCompanyName == 'VACAYZEN']
            
    #     result = datesets.groupby('Beach Access', group_keys=True)[str(date.date())].apply(sum)

    #     results.append(result)
    
    # final = pd.concat(results, axis=1)


    # st.dataframe(final, use_container_width=True)

    





if len(uploaded_files) > 0:
    for index, file in enumerate(uploaded_files):
        files[file.name] = index

    hasAllRequiredFiles = True
    missing = []

    for file in files:
        if files[file] == None:
            hasAllRequiredFiles = False
            missing.append(file)

if len(uploaded_files) > 0 and not hasAllRequiredFiles:
    for item in missing:
        st.warning('**' + item + '** is missing and required.')    


elif len(uploaded_files) > 0 and hasAllRequiredFiles:
    swbsa = pd.read_csv(uploaded_files[files['Export_ExportRentalsByDay.csv']], index_col=False)

    SWBSA_Analytics(swbsa)