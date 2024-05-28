import pandas as pd
from dashboard_lib import parse_address, get_location_lat_long


df = pd.read_csv('webScrapping/LongIsland/suffolkLib.csv')

#add columns to the dataframe
df['city'] = ''
df['state'] = ''
df['zipcode'] = ''
df['street_number'] = ''
df['street_name'] = ''
df['unit'] = ''
    
df_small = df.head(5)


for index, row in df_small.iterrows():
    #parse the address
    print(row['Library Address'])
    parsed_address = parse_address(row['Library Address'])
    #add the parsed address to the dataframe
    df.loc[index, 'city'] = parsed_address[0]
    df.loc[index, 'state'] = parsed_address[1]
    df.loc[index, 'zipcode'] = parsed_address[2]
    df.loc[index, 'street_number'] = parsed_address[3]
    df.loc[index, 'street_name'] = parsed_address[4]
    df.loc[index, 'unit'] =  parsed_address[5]



#single example
city, state, zip, street_number, street_name, unit = parse_address('21 5 Main Street,PO Box 2550 Amagansett, NY 11930')




for index, row in df_small.iterrows():
    state = row['state']
    city = row['city']
    street_number = row['street_number']
    street_name = row['street_name']
    row['lat'], row['lon'] = get_location_lat_long(street_number + " " + street_name +", " + city + ", " + state + " " + zip)



###