import streamlit as st
import numpy as np
import pandas as pd
from streamlit import caching

def main():
    st.header('Keeping Nova Scotian Businesses Running Safely')
    st.image('img/lighthouse.jpg', use_column_width=True)
    #Side bar
    st.sidebar.title("Search Options")
    app_mode = st.sidebar.selectbox("Select topic", ["Purchasing PPE", "Managing Labor"])
    if app_mode == "Purchasing PPE": ppe()
    elif app_mode == "Managing Labor": hire()

# IF PPE IS SELECTED IN SIDE BAR
def ppe():
    caching.clear_cache()
    file_path = "PPE Supplier Encoded.xlsx" #Excel file with PPE suppliers
    data = pd.read_excel(file_path)

    #Get types of PPE
    types_PPE = pd.read_excel(file_path, sheet_name='DATA').columns[5:13].tolist()

    #Multiselect bar for types of PPE
    st.sidebar.write(' ')
    options = st.sidebar.multiselect('What PPE are you looking for?', types_PPE)

    if len(options) > 0:
        type_master = {} #Initialize dictionary - to store all the codes (#s indicating what suppliers carry)
        wanted_type = {} #Initialize dictionary - to store all the sub-types desired
        for t in types_PPE:
            type_master[t]=0
            wanted_type[t]={}
            for p in pd.read_excel(file_path, sheet_name=t).columns[1:].tolist():
                wanted_type[t][p]=0

        st.sidebar.image('img/bline.jpg', use_column_width=True)
        
        #Creates sub-type multiselects (none required for N95)
        for o in options:
            if o == 'N95 Masks':
                hold=['N95 Masks']
            else: hold = st.sidebar.multiselect('What types of ' + str(o) + ' ?', list(wanted_type[o].keys()))
            if len(hold) > 0:
                for h in hold:
                    wanted_type[o][h]=1 #Set value in dictionary to 1 if sub-type selected

        #Retreive codes based on sub-type selection
        for w in options:
            df=pd.read_excel(file_path, sheet_name=w)
            r = np.ones((df.shape[0]), dtype=bool) #Initialize array of booleans
            for v in wanted_type[w]:
                if wanted_type[w][v]==1:
                    r = r & (df[v]==1)
            if np.any(r):
               type_master[w]=df[r].iloc[:,0].tolist()
        
        #Lead Time multiselect
        type_master['Lead Time']=0
        st.sidebar.image('img/bline.jpg', use_column_width=True)
        maxLT = st.sidebar.selectbox('What is your maximum acceptable lead time', pd.read_excel(file_path, sheet_name='Lead Time').columns[1:].tolist())
        df=pd.read_excel(file_path, sheet_name='Lead Time')
        #Retrieve codes for lead time
        type_master['Lead Time'] = df[df[maxLT]==1].iloc[:,0].tolist()

        if len(hold) > 0:
            df=pd.read_excel(file_path, sheet_name='DATA')
            df=df.set_index('Supplier Name')
            x = np.ones((df.shape[0]), dtype=bool) #Boolean to select suppliers
            for z in options:    
                x = x & (df[z].isin(type_master[z])) #Changes boolean list based on codes
            x = x & (df['Lead Time'].isin(type_master['Lead Time'])) #Changes boolean list based on lead time
            
            if np.any(x): #Output supplier table   
                st.subheader("These companies can provide all your PPE")
                st.table(df[x].iloc[:,1:4])
            else: #Message if no suppliers match search criteria
                st.write('Sorry, no suppliers meet all your criteria. Try removing a few PPE types or increasing your maximum allowable lead time. Multiple suppliers may have to be contracted.')

#IF HIRE IS SELECTED IN SIDE BAR
def hire():
    caching.clear_cache()
    
    df = pd.read_csv("NSW_Locations.csv")

    st.sidebar.write(' ')
    #Select bar for region
    region = st.sidebar.selectbox("Select region", ["Choose an option","Halifax Regional Municipality", "Cape Breton", "Northern", "South Shore/Valley"])

    #Calls display function
    if region:
        if region == "Halifax Regional Municipality":
            reg="HRM"
            display_NSW(df, reg)
        elif region == "Cape Breton":
            reg="CB"
            display_NSW(df, reg)
        elif region == "Northern":
            reg="Northern"
            display_NSW(df, reg)
        elif region == "South Shore/Valley":
            reg="South Shore/Valley"
            display_NSW(df, reg)

#Display function
def display_NSW(df, reg):
    reg_cities=df.loc[(df['Region']==reg)];
    st.sidebar.write(' ')
    city = st.sidebar.multiselect(
    'Select nearby cities?', reg_cities['City/Town'].unique())
    if len(city) > 0:
        r = np.zeros((1, df.shape[0]), dtype=bool) #Initialize array of booleans
        st.subheader("These are the Nova Scotia Works Employment Centers nearest to you:")
        st.image('img/bline.jpg', use_column_width=True)
        #Set value of booleans based on cities selected
        for i in city:
            r = r | (df['City/Town']==i)

        #Format output
        for j in range(0, len(r)):
            if r[j]:
                a=df.iloc[j]['City/Town']
                b=df.iloc[j]['Street Address']
                c=df.loc[j, ['Phone']].to_string(index=False)
                d=df.loc[j, ['Email']].to_string(index=False)
                st.write(str(a) + ',  ' + str(b))
                st.write('Phone: ' + str(c))
                st.write('Email: ' + str(d))
                st.image('img/bline.jpg', use_column_width=True)

#Calls main function
if __name__ == "__main__":
    main()