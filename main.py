import streamlit as st
import pandas as pd

st.set_page_config(page_title='Market-share Analytics', page_icon='📊', layout="centered", initial_sidebar_state="auto", menu_items=None)


st.caption('VACAYZEN')
st.title('Market-share Analytics')
st.info('Analysis of business areas to determine change in market share.')

l, r = st.columns(2)
p1_start = l.date_input('Period 1 Start', key='p1_start', value=pd.to_datetime(f'1/1/{pd.to_datetime('today').year}'))
p1_end   = r.date_input('Period 1 End',   key='p1_end',   value=pd.to_datetime('today'), max_value=pd.to_datetime('today'))
p2_start = l.date_input('Period 2 Start', key='p2_start', value=pd.to_datetime(f'{p1_start.month}/{p1_start.day}/{p1_start.year - 1}'))
p2_end   = r.date_input('Period 2 End',   key='p2_end',   value=pd.to_datetime(f'{p1_end.month}/{p1_end.day}/{p1_end.year - 1}'))

p1_days = pd.date_range(p1_start, p1_end)
p2_days = pd.date_range(p2_start, p2_end)


with st.expander('Uploaded Files'):
    
    file_descriptions = [
        ['Export_ExportRentalsByDay.csv','An SWBSA integraRental export, Rentals By Day.']
    ]

    files = {
        'Export_ExportRentalsByDay.csv': None
    }


    uploaded_files = st.file_uploader(
        label='Files (' + str(len(files)) + ')',
        accept_multiple_files=True
    )

    st.info('File names are **case sensitive** and **must be identical** to the file name below.')
    st.dataframe(pd.DataFrame(file_descriptions, columns=['Required File','Source Location']), hide_index=True, use_container_width=True)



def GetDatesFromRange(row):
        dates = pd.date_range(row.RentalAgreementStartDate, row.RentalAgreementEndDate, normalize=True).values
        return set(map(lambda x: pd.to_datetime(x).date(), dates))



def SWBSA_Analytics(swbsa):
    st.subheader('SWBSA')
    swbsa.RentalAgreementStartDate = pd.to_datetime(swbsa.RentalAgreementStartDate).dt.date
    swbsa.RentalAgreementEndDate   = pd.to_datetime(swbsa.RentalAgreementEndDate).dt.date

    swbsa['Days'] = swbsa.apply(GetDatesFromRange, axis=1)

    results = []

    for date in p1_days:

        datesets = swbsa[[date.date() in d for d in swbsa.Days]]
        datesets = datesets.rename(columns={'Description':'Beach Access', 'Quantity':str(date.date())})
        datesets = datesets[datesets.RentalCompanyName == 'VACAYZEN']
            
        result = datesets.groupby('Beach Access', group_keys=True)[str(date.date())].apply(sum)

        results.append(result)
    
    final = pd.concat(results, axis=1)

    st.dataframe(final, use_container_width=True)

    





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