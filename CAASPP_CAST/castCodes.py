import pandas as pd
import glob

def get_schoolName(code, keyDict): 
    try: 
        return keyDict[code] 
    except KeyError: 
        return code 

CountyDF = pd.read_csv('data_files/cast_ca19-25_all.csv')
CountyDF = CountyDF[CountyDF['County Code'].isin([0, 44])] # 0 is State, 44 is Santa Cruz

groupsKey = pd.read_csv('data_files/StudentGroups_2025.txt',  encoding="cp1252", delimiter='^').set_index('Demographic ID Num')

# Concat all entities files
entities_files = glob.glob('data_files/*entities_csv.txt')
entities = pd.concat([pd.read_csv(f, encoding="cp1252",  delimiter='^') for f in entities_files])
# parse District and School codes to int
entities['District Code'] = entities['District Code'].astype('Int64')
entities['School Code'] = entities['School Code'].astype('Int64')
entities = entities.drop_duplicates(subset=['District Code', 'School Code'])
# entities = pd.read_csv('data_files/sb_ca2024entities_csv.txt', encoding="ISO-8859-1",  delimiter='^')

districts = entities[['District Code', 'District Name', 'School Code']]
districtsKey = districts[['District Code', 'District Name']][districts["School Code"]== 0000000].set_index('District Code').to_dict()['District Name']

schools = entities[['School Code', 'School Name']]
schoolsKey = schools.set_index('School Code').to_dict()['School Name']
schoolsKey[100305] = 'Cypress Charter High'
schoolsKey[123083] = 'Home and Hospital'
schoolsKey[4475432] = 'District Level Program'

# Associate Cypress Charter High (100305) to SC COE district
CountyDF['District Code'][CountyDF['School Code'] == 100305] = 10447  
CountyDF['District Code'][(CountyDF['District Code'] == 69765) & (CountyDF['Grade'] == 11)] = 10447 # All LO Grade 11 data is from Cypress High

CountyDF['Student Groups'] = CountyDF['Student Group ID'].map(lambda x: groupsKey['Demographic Name'].to_dict()[x])
CountyDF['Student Group Category'] = CountyDF['Student Group ID'].map(lambda x: groupsKey['Student Group'].to_dict()[x])
CountyDF['District'] = CountyDF['District Code'].map(lambda x: districtsKey[x] if x in districtsKey else x)
CountyDF['School'] = CountyDF['School Code'].apply(lambda x: get_schoolName(x, schoolsKey))
CountyDF['Test Name'] = 'California Science Test (CAST)'
CountyDF['Aggregate Level'] = CountyDF['Type ID'].map({4: 'State', 5: 'County', 6: 'District', 7: 'School', 9: 'Charter School', 10: 'Charter School'})
CountyDF['Test Type Description'] = 'California Science Test (CAST)'
CountyDF['Grade Level'] = CountyDF['Grade'].map({3: 'Grade 3', 4: 'Grade 4', 5: 'Grade 5', 6: 'Grade 6', 7: 'Grade 7', 8: 'Grade 8', 11: 'Grade 11', 13: 'All Grades' })

CountyDF["Area 1 Percentage Above Standard"] = CountyDF["Earth and Space Sciences Domain Percent Above Standard"]
CountyDF["Area 1 Percentage Near Standard"] = CountyDF["Earth and Space Sciences Domain Percent Near Standard"]
CountyDF["Area 1 Percentage Below Standard"] = CountyDF["Earth and Space Sciences Domain Percent Below Standard"]
CountyDF["Area 1 Count Above Standard"] = CountyDF["Earth and Space Sciences Domain Count Above Standard"]
CountyDF["Area 1 Count Near Standard"] = CountyDF["Earth and Space Sciences Domain Count Near Standard"]
CountyDF["Area 1 Count Below Standard"] = CountyDF["Earth and Space Sciences Domain Count Below Standard"]

CountyDF["Area 2 Percentage Above Standard"] = CountyDF["Life Sciences Domain Percent Above Standard"]
CountyDF["Area 2 Percentage Near Standard"] = CountyDF["Life Sciences Domain Percent Near Standard"]
CountyDF["Area 2 Percentage Below Standard"] = CountyDF["Life Sciences Domain Percent Below Standard"]
CountyDF["Area 2 Count Above Standard"] = CountyDF["Life Sciences Domain Count Above Standard"]
CountyDF["Area 2 Count Near Standard"] = CountyDF["Life Sciences Domain Count Near Standard"]
CountyDF["Area 2 Count Below Standard"] = CountyDF["Life Sciences Domain Count Below Standard"]

CountyDF["Area 3 Percentage Above Standard"] = CountyDF["Physical Sciences Domain Percent Above Standard"]
CountyDF["Area 3 Percentage Near Standard"] = CountyDF["Physical Sciences Domain Percent Near Standard"]
CountyDF["Area 3 Percentage Below Standard"] = CountyDF["Physical Sciences Domain Percent Below Standard"]
CountyDF["Area 3 Count Above Standard"] = CountyDF["Physical Sciences Domain Count Above Standard"]
CountyDF["Area 3 Count Near Standard"] = CountyDF["Physical Sciences Domain Count Near Standard"]
CountyDF["Area 3 Count Below Standard"] = CountyDF["Physical Sciences Domain Count Below Standard"]

CountyDF.to_csv('CAST_STATE.csv', index=False)

# If the CAASPP_STATE.csv is in the local directory, concatenate the two files
try:
    CountyDF = CountyDF.rename(columns={"Test ID": "Test Id", "Type ID": "Type Id", "Student Group ID": "Subgroup ID"})
    caaspp = pd.read_csv('CAASPP_STATE.csv')
    combined = pd.concat([caaspp, CountyDF])
    combined.to_csv('CAASPP-CAST_STATE.csv', index=False)
except FileNotFoundError:
    pass

