from flask import Flask, request, jsonify
import pandas as pd
import numpy as np 
from flask_cors import CORS
import os
from dotenv import load_dotenv 
import google.generativeai as genai

load_dotenv() 


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/')
def home():
    return jsonify({"message": "Hello flask application"})


@app.route('/preprocess', methods=['POST'])
def preprocess_data():
    try:
        # Get JSON data from the request
        data = request.json
        if not data or 'dataframe' not in data:
            return jsonify({"error": "No dataframe found in the request"}), 400

        # Convert JSON dataframe to pandas DataFrame
        dataframe = pd.DataFrame(data['dataframe'])
        # print(dataframe)
        # dataframe = dataframe.dropna()
        print('hello')
        # Columns to validate and extract
        required_columns = [
            'Item_Visibility', 'Item_Type','Item_MRP',
            'Outlet_Establishment_Year',
            'Outlet_Location_Type', 'Outlet_Type', 'Item_Outlet_Sales'
        ]
        

        extracted_data = {}
        missing_columns = []

        # print(extracted_data)
        
        # Validate and extract required columns
        for column in required_columns:
            if column in dataframe.columns:
                extracted_data[column] = dataframe[column].to_numpy().tolist()
            else:
                missing_columns.append(column)
        
        if 'Outlet_Establishment_Year' in dataframe.columns: 
            extracted_data['max_year'] = int(dataframe['Outlet_Establishment_Year'].max()) 
            extracted_data['min_year'] = int(dataframe['Outlet_Establishment_Year'].min()) 
            extracted_data['years'] = dataframe['Outlet_Establishment_Year'].unique().tolist()
            
        
        print('year task completed')
        
        if 'Item_Outlet_Sales' in dataframe.columns: 
            extracted_data['sum_sales'] = int(dataframe['Item_Outlet_Sales'].sum())
        
        print('item sales task completed')
        if 'Item_MRP' in dataframe.columns: 
            extracted_data['sum_mrp'] = int(dataframe['Item_MRP'].sum())
        
        
        print('mrp task completed')
        if 'Outlet_Type' in dataframe.columns: 
            extracted_data['Unique_Outlet_Type'] = dataframe['Outlet_Type'].unique().tolist() 
            print(dataframe['Outlet_Type'].unique()) 
        # print(extracted_data)
        
        print('outlet type task completed')
        # way to find total sales per outlet type 
        outlet_sales_data = {}
        for outlet in extracted_data['Unique_Outlet_Type']:
            outlet_data = dataframe.loc[dataframe['Outlet_Type'] == outlet] 
            total_sales = int(outlet_data['Item_Outlet_Sales'].sum()) 
            outlet_sales_data[outlet] = total_sales
        
        extracted_data['outlet_type_per_sales'] = outlet_sales_data 
        
        print('outlet type per sales task completed')
        
        # item cost per item type
        if 'Item_Type' in dataframe.columns: 
            extracted_data['items'] = dataframe['Item_Type'].unique().tolist() 
        
        print('item type task completed')
        item_sales_data = []
        for item in extracted_data['items']: 
            item_data = dataframe.loc[dataframe['Item_Type'] == item] 
            total_cost = int(item_data['Item_MRP'].sum()) 
            temp_data = {}
            temp_data['name'] = item 
            temp_data['cost'] = total_cost
            item_sales_data.append(temp_data)
            
        print('item cost task completed')
         
        extracted_data['items_cost_per_item'] = item_sales_data 
        
        print('line 92 no error')
        # code to calculate the sum during each year 
        year_data = {}
        for year in extracted_data['years']: 
            year_record = dataframe.loc[dataframe['Outlet_Establishment_Year'] == year]
            sum_of_items = int(year_record['Item_Outlet_Sales'].sum()) 
            year_data[year] = sum_of_items
        
        extracted_data['year_total_sales'] = year_data
        
        print('error')

        # calculating the sales on each outlet type location
        
        extracted_data['locations'] = dataframe['Outlet_Location_Type'].unique().tolist() 
        location_data = {} 
        for location in extracted_data['locations']: 
            location_record = dataframe.loc[dataframe['Outlet_Location_Type'] == location]
            total_sales = int(location_record['Item_Outlet_Sales'].sum())
            location_data[location] = total_sales 
        
        extracted_data['location_data'] = location_data
        
        item_per_sales_data = []
        for item in extracted_data['items']: 
            item_record = dataframe.loc[dataframe['Item_Type'] == item] 
            total_sales = int(item_record['Item_Outlet_Sales'].sum())
            item_per_sales_data.append({'item':item,'sales':total_sales}) 
        
        extracted_data['items_sales_per_items'] = item_per_sales_data
        print('no error upto line 130')
        
        item_visibility = {} 
        for item in extracted_data['items']: 
            item_record = dataframe.loc[dataframe['Item_Type'] == item] 
            avg_visibility = item_record['Item_Visibility'].sum()
            print(item_record) 
            item_visibility[item] = avg_visibility 
        extracted_data['item_total_visibility'] = item_visibility
        
        print(extracted_data) 
        
        return jsonify({
            "message": "Dataset preprocessed successfully!",
            "data": extracted_data
        })
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500



@app.route('/specific_data',methods=['POST']) 
def specify_data(): 
    data = request.json 
    name_of_store = data.get('store_type') 
    dataframe = data.get('dataframe') 
    
    print(dataframe)
    
    if not data or 'dataframe' not in data or 'store_type' not in data:
        return jsonify({"error": "No dataframe found in the request"}), 400

    # Convert JSON dataframe to pandas DataFrame
    dataframe = pd.DataFrame(data['dataframe'])
    specified_dataframe = dataframe.loc[dataframe['Outlet_Type'] == name_of_store] 
    
    required_columns = [
            'Item_Visibility', 'Item_Type','Item_MRP',
            'Outlet_Establishment_Year',
            'Outlet_Location_Type', 'Outlet_Type', 'Item_Outlet_Sales'
        ]
        

    extracted_data = {}
    missing_columns = []

    # print(extracted_data)
        
    # Validate and extract required columns
    for column in required_columns:
        if column in specified_dataframe.columns:
            extracted_data[column] = specified_dataframe[column].to_numpy().tolist()
        else:
            missing_columns.append(column)
        
    if 'Outlet_Establishment_Year' in specified_dataframe.columns: 
        extracted_data['max_year'] = int(specified_dataframe['Outlet_Establishment_Year'].max()) 
        extracted_data['min_year'] = int(specified_dataframe['Outlet_Establishment_Year'].min() )
        
    if 'Item_Outlet_Sales' in specified_dataframe.columns: 
        extracted_data['sum_sales'] = int(specified_dataframe['Item_Outlet_Sales'].sum())
        
    if 'Item_MRP' in specified_dataframe.columns: 
        extracted_data['sum_mrp'] = int(specified_dataframe['Item_MRP'].sum())
        
    if 'Outlet_Type' in specified_dataframe.columns: 
        extracted_data['Unique_Outlet_Type'] = dataframe['Outlet_Type'].unique().tolist() 
        print(specified_dataframe['Outlet_Type'].unique()) 
    # print(extracted_data)
    
    outlet_sales_data = {}
    for outlet in extracted_data['Unique_Outlet_Type']:
        outlet_data = dataframe.loc[dataframe['Outlet_Type'] == outlet] 
        total_sales = int(outlet_data['Item_Outlet_Sales'].sum()) 
        outlet_sales_data[outlet] = total_sales
        
    extracted_data['outlet_type_per_sales'] = outlet_sales_data 
    
    if 'Item_Type' in dataframe.columns: 
        extracted_data['items'] = dataframe['Item_Type'].unique().tolist()
    
    item_sales_data = []
    for item in extracted_data['items']: 
        print(item)
        item_data = specified_dataframe.loc[specified_dataframe['Item_Type'] == item] 
        total_cost = int(item_data['Item_MRP'].sum()) 
        temp_data = {}
        temp_data['name'] = item 
        temp_data['cost'] = total_cost
        item_sales_data.append(temp_data)
             
         
    extracted_data['items_cost_per_item'] = item_sales_data 
    print(extracted_data)
    
    extracted_data['locations'] = dataframe['Outlet_Location_Type'].unique().tolist() 
    location_data = {} 
    for location in extracted_data['locations']: 
        location_record = dataframe.loc[dataframe['Outlet_Location_Type'] == location]
        total_sales = int(location_record['Item_Outlet_Sales'].sum())
        location_data[location] = total_sales 
        
    extracted_data['location_data'] = location_data
    
            
    item_per_sales_data = []
    for item in extracted_data['items']: 
        item_record = dataframe.loc[dataframe['Item_Type'] == item] 
        total_sales = int(item_record['Item_Outlet_Sales'].sum())
        item_per_sales_data.append({'item':item,'sales':total_sales}) 
        
    extracted_data['items_sales_per_items'] = item_per_sales_data
        
    
    return jsonify({
            "message": "Dataset preprocessed successfully!",
            "data": extracted_data
    }),200
        

@app.route('/gemini',methods=['POST']) 
def generate_content_ai(): 
    try: 
        data = request.json 
        dataframe = data.get('sent_data', {})
        chat = data.get('chat')
        print(chat) 
        print(dataframe.items)
        data_to_sent = {
            'Unique_Outlet_Type': dataframe.get('Unique_Outlet_Type'), 
            'item_total_visibility':dataframe.get('item_total_visibility'), 
            'items':dataframe.get('items'), 
            'items_cost_per_item':dataframe.get('items_cost_per_item'), 
            'items_sales_per_items':dataframe.get('items_sales_per_items'), 
            'location_data':dataframe.get('location_data'), 
            'locations':dataframe.get('locations'), 
            'years': [dataframe.get('max_year'), dataframe.get('min_year')],
            'outlet_type_per_sales':dataframe.get('outlet_type_per_sales'), 
            'sum_mrp':dataframe.get('sum_mrp'), 
            'sum_sales':dataframe.get('sum_sales'), 
            'years':dataframe.get('years'), 
            'years_total_sales':dataframe.get('year_total_sales')
        }
        
        print(data_to_sent)
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        respose = model.generate_content(
            f"{data_to_sent} based on this data,please answer in short and in plain text {chat}"
        )
        print(respose.text); 
        
        return jsonify({'message':'succesfully got answer !','response':respose.text}),200 

    except Exception as e: 
        return jsonify({'message':'error has occured','error':str(e)}),500     



if __name__ == '__main__':
    app.run(debug=True)
