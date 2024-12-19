from cgi import parse_multipart
import code
from concurrent.futures import process
from contextlib import nullcontext
from operator import methodcaller
import sqlite3
import json
from urllib import request
import flask
import csrf
from flask import Flask, render_template, url_for, request, redirect, request
from flask_sqlalchemy import SQLAlchemy, model
from flask_restful import Api, Resource, reqparse
from flask_jsonpify import jsonpify
import sqlalchemy
import pandas as pd
import numpy as np
import math
from openpyxl import Workbook, load_workbook
from openpyxl.formatting import Rule
from openpyxl.styles import Color, PatternFill, Font, Border
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, FormulaRule
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from werkzeug.datastructures import ImmutableMultiDict

def bubbleSort(arr):
    n = len(arr)
    swapped = False

    for i in range(n-1):
        for j in range(0, n-i-1):
            if arr[j] < arr[j + 1]:
                swapped = True
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
        if not swapped:
            return
        
def bubbleSortrev(arr):
    n = len(arr)
    swapped = False

    for i in range(n-1):
        for j in range(0, n-i-1):
            if arr[j] > arr[j + 1]:
                swapped = True
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
        if not swapped:
            return


National = {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039}

Regional = {'Eastern Cape' :
            {'AM': 0.426,
           'CM': 0.063,
           'IM': 0.012,
           'VM': 0.026,
           'AF': 0.392,
           'CF': 0.054,
            'IF': 0.002,
           'WF': 0.024},
           'Free State' :
            {'AM': 0.486,
           'CM': 0.021,
           'IM': 0.004,
           'VM': 0.045,
           'AF': 0.404,
           'CF': 0.012,
            'IF': 0.000,
           'WF': 0.029},
           'Gauteng' :
            {'AM': 0.466,
           'CM': 0.014,
           'IM': 0.013,
           'VM': 0.061,
           'AF': 0.375,
           'CF': 0.011,
            'IF': 0.007,
           'WF': 0.052},
           'Kwazulu-Natal' :
            {'AM': 0.462,
           'CM': 0.006,
           'IM': 0.06,
           'VM': 0.015,
           'AF': 0.405,
           'CF': 0.005,
            'IF': 0.036,
           'WF': 0.011},
           'Limpopo' :
            {'AM': 0.528,
           'CM': 0.000,
           'IM': 0.015,
           'VM': 0.023,
           'AF': 0.440,
           'CF': 0.001,
            'IF': 0.001,
           'WF': 0.004},
           'Mpumalanga' :
            {'AM': 0.496,
           'CM': 0.003,
           'IM': 0.002,
           'VM': 0.044,
           'AF': 0.428,
           'CF': 0.003,
            'IF': 0.000,
           'WF': 0.024},
           'North West' :
            {'AM': 0.56,
           'CM': 0.000,
           'IM': 0.002,
           'VM': 0.039,
           'AF': 0.359,
           'CF': 0.004,
            'IF': 0.000,
           'WF': 0.035},
           'Northern Cape' :
            {'AM': 0.288,
           'CM': 0.238,
           'IM': 0.003,
           'VM': 0.029,
           'AF': 0.223,
           'CF': 0.182,
            'IF': 0.000,
           'WF': 0.037},
           'Western Cape' :
            {'AM': 0.205,
           'CM': 0.239,
           'IM': 0.011,
           'VM': 0.103,
           'AF': 0.159,
           'CF': 0.193,
            'IF': 0.004,
           'WF': 0.086}}


Industry = {'Education': 
        {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Water Supply, Sewerage Management and Remediation': 
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Accomodation and Food Services': 
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Human Health and Social Work':
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Agriculture, Forestry and Fishing': 
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Entertainment and Recreation':
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Wholesale and Retail Trade, Repair of Motor Vehicles and Motorcycles':
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Administrative and Support':
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Professional, Scientific and Technical': 
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Transportation and Storage':
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Electricity, Gas, Steam and Air Conditioning Supply':
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Financial and Insurance Activities':
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Mining and Quarrying':
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Public Administration and Defence Compulsory Social Security': 
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Manufacturing':
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Information and Communication': 
            {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Construction': {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039},
'Real Estate': {'AM': 0.436,
           'CM': 0.05,
           'IM': 0.018,
           'VM': 0.049,
           'AF': 0.358,
           'CF': 0.041,
            'IF': 0.009,
           'WF': 0.039}}

Ranking_List = ['African Female', 'Coloured Female', 'Indian Female', 'African Male', 'Coloured Male', 'Indian Male', 'White Female', 'White Male']


def expectedEAP(companydb, level, seclevel):
    data = companydb
    totalEAP = int(data.iloc[8][11])
    EAP = []
    diff = []
    increase = np.zeros(8)
    decrease = np.zeros(8)
        
        
        
    if (level == 'Regional') or (level == 'Industry'):
        if (level == 'Regional'):
            expectedEAP = list((Regional[seclevel].values()))
            for k in range(0, len(expectedEAP)):
                expectedEAP[k] = round(expectedEAP[k]*totalEAP, 2)
        elif (level == 'Industry'):
            expectedEAP = list((Industry[seclevel].values()))
            for k in range(0, len(expectedEAP)):
                expectedEAP[k] = round(expectedEAP[k]*totalEAP, 2)
    else: 
        expectedEAP = list((National.values()))
        for k in range(0, len(expectedEAP)):
            expectedEAP[k] = round(expectedEAP[k]*totalEAP, 2)
    for k in range(1, 9):
        EAP.append(data.iloc[8][k])
    for k in range(0, len(expectedEAP)): 
        kdiff = expectedEAP[k] - EAP[k]
        
        diff.append(kdiff)
    for k in range(0, len(diff)):
        if (diff[k] < 0):
            decrease[k] = abs(diff[k])
        else:
            increase[k] = diff[k]
    increase = list(increase)
    decrease = list(decrease)
    increase.insert(0, 'Increase')
    decrease.insert(0, 'Decrease')
    for k in range(len(increase)-1, len(increase)+2):
        increase.append(' ')
        decrease.append(' ')
    data.loc[len(data.index)+1] = increase
    data.loc[len(data.index)+1] = decrease
   
    return data

def organisationalEAP(companydb, level, seclevel):
    
    data = companydb
    totalEAP = int(data.iloc[8][11])
    Occupational_Levels = []
    OLEAP = {}
    expected_OLEAP = {}
    OLEAP_Total = []
    for k in range(0,6):
        Occupational_Levels.append(data.iloc[k].values[0])
    for k in range(0, len(Occupational_Levels)):
        OLEAP[Occupational_Levels[k]] = list(data.iloc[k].values[1:len(data.iloc[0].values)-3])
    for k in range(0, len(Occupational_Levels)):
        OLEAP_Total.append(sum(OLEAP[Occupational_Levels[k]]))
    if (level == 'National'):
        expected = list(National.values())
    if (level == 'Regional'):
        expected = list(Regional[seclevel].values())
    if (level == 'Industry'):
        expected = list(Industry[seclevel].values())
    for k in range(0, 6):
        expectedlst = []
        for j in range(0, 8):
            var = round(expected[j]*OLEAP_Total[k],2)
            expectedlst.append(var)
        expected_OLEAP[Occupational_Levels[k]] = list(expectedlst)
    
    
    first_entry = [list(data.iloc[0].values[0:9])]
    diff = []
    total = 0
    percentages = []
    tf = []
    tfovun = []
    for k in range(0, 8):
        diff.append(expected_OLEAP[Occupational_Levels[0]][k] - OLEAP[Occupational_Levels[0]][k])

    for k in range(1,9):
        total += list(data.iloc[0])[k]
    if total != 0:
        percentages = list(data.iloc[0][1:9])/total*100
    else:
        percentages = np.zeros(8)
    
    for k in range(0,len(expected)):
        tf.append(expected[k]*100)
    for k in range(0, len(expected)):
        tfovun.append(tf[k] - percentages[k])
    percentages = list(percentages)
    increase = np.zeros(8)
    decrease = np.zeros(8)
    for k in range(0, 8):
        if (diff[k] < 0):
            decrease[k] = abs(diff[k])
        else:
            increase[k] = diff[k]
    
    tfovun = list(tfovun)
    increase = list(increase)
    decrease = list(decrease)
    increase.insert(0, 'Increase')
    decrease.insert(0, 'Decrease')
    percentages.insert(0, 'Percentage Current Representation')
    tfovun.insert(0,'Underpresented / Overrepresented (-) %')
    first_entry.append(increase)
    first_entry.append(decrease)
    first_entry.append(percentages)
    first_entry.append(tfovun)
    column_header = data.columns[0:9]
    df1 = pd.DataFrame(first_entry, columns = column_header, index = [1, 2, 3, 4, 5])
    indexnum = 6
    next_entry = []
    for k in range(1, 6):
        next_entry = []
        next_entry.append(list(data.iloc[k].values[0:9]))
        diff = []
        total = 0
        percentages = []
        tf = []
        tfovun = []
        for j in range(0, 8):
            diff.append(expected_OLEAP[Occupational_Levels[k]][j] - OLEAP[Occupational_Levels[k]][j])
        increase = np.zeros(8)
        decrease = np.zeros(8)
        for p in range(0, 8):
            if (diff[p] < 0):
                decrease[p] = abs(diff[p])
            else:
                increase[p] = diff[p]     
        for i in range(1,9):
            total += list(data.iloc[k])[i]
        if total != 0:
            percentages = list(data.iloc[k][1:9])/total*100
        else:
            percentages = np.zeros(8)
        for k in range(0,len(expected)):
            tf.append(expected[k]*100)
        for k in range(0, len(expected)):
            tfovun.append(tf[k] - percentages[k])
        tfovun = list(tfovun)
        percentages = list(percentages)
        increase = list(increase)
        decrease = list(decrease)
        increase.insert(0, 'Increase')
        decrease.insert(0, 'Decrease')
        percentages.insert(0, 'Percentage Current Representation')
        tfovun.insert(0,'Underpresented / Overrepresented (-) %')
        next_entry.append(increase)
        next_entry.append(decrease)
        next_entry.append(percentages)
        next_entry.append(tfovun)
        column_header = data.columns[0:9]
        df2 = pd.DataFrame(next_entry, columns = column_header, index = [indexnum,indexnum +1 ,indexnum + 2, indexnum + 3, indexnum +4])
        df1 = pd.concat([df1, df2])

    return df1


def yearplan(companydb, level, seclevel, growth):
    data1 = companydb
    totalEAP = int(data1.iloc[8][11])
    EAPafteryrs = totalEAP*((100 + growth)/100)
    newEAP = round((EAPafteryrs - totalEAP),0)
    
    
    
    
    
    
    data2 = organisationalEAP(companydb, level, seclevel)
    data3 = data2
    
    increase = 0
    for k in range(1,29,5):
        increase += sum(list(data2.iloc[k])[1:len(data2.iloc[0])])
    
    ratio = newEAP/increase
    increasedata = []
    data2.index = pd.RangeIndex(len(data2.index))

    for k in range(1,30,5):
        for j in range(1, len((data2.iloc[k])[1:len(data2.iloc[0])])+1):
            increasedata.append(list(data2.iloc[k])[j])
    increasedata = np.round(np.array(increasedata)*ratio,2)
    bubbleSort(increasedata)
    increasedata = list(filter(lambda x: x != 0, increasedata))
    index = list(filter(lambda x: x in [1, 6, 11, 16, 21, 26], data2.index))
    
    
    pos = []
    for k in range(0, len(increasedata)):
        for j in range(0, len(index)):
            for i in range(0, len(Ranking_List)):
                if (type(data2.at[index[j],Ranking_List[i]]) in [float, np.float64, int]):
                    if (increasedata[k] == np.round((data2.at[index[j],Ranking_List[i]])*ratio,2)):
                        pos.append(tuple([index[j], Ranking_List[i]]))
            
    pos = list(dict.fromkeys(pos))
    counter = 0
    counteremp = 0
    newemp = []
    posemp = []
    while (counter != newEAP):
        addemp = 0
        fcount = 0
        colouremp = []
        rankemp = []
        temparray = []
        instancecounter = 1
        instances = False
        inc = increasedata[counteremp]
        posindex = pos[counteremp][0]
        poscolumn = pos[counteremp][1]
        rowtotal = list(data2.iloc[posindex-1])
        del rowtotal[0]
        rowtotal = sum(rowtotal)
        if counteremp >= len(increasedata)-1:
            counteremp = 0
            fcount += 1
        if round(increasedata[counteremp],2) != round(increasedata[counteremp+1],2):
            while (round(inc,0) >= 0) and (newEAP - counter > 0):
                if fcount != 0:
                    inc = 1
                addemp += 1
                counter += 1
                inc = (inc - 1)*(rowtotal/(rowtotal + 1))
            
            counteremp += 1
            newemp.append(data2.at[posindex - 1, poscolumn] + addemp)
            posemp.append([posindex, poscolumn])
            data3.loc[posindex -1, poscolumn] = newemp[len(newemp)-1]
    

        
        else:
            while (instances == False):
                if ((counteremp + instancecounter) <= len(increasedata)):
                    if (increasedata[counteremp] == increasedata[counteremp + instancecounter]):
                        instancecounter += 1
                    #else:
                        for k in range(0, instancecounter):
                            colourpos = [pos[counteremp+ k][1]]
                            colouremp.append(colourpos[0])
                            temparray.append(pos[counteremp+k])
                        for j in range(0, len(colouremp)):
                            for i in range(0, len(Ranking_List)):
                                if (colouremp[j] == Ranking_List[i]):
                                    rankemp.append(i)
                        p = len(rankemp)
                        for i in range(p-1):
                            for j in range(0, p-i-1):
                                if rankemp[j] > rankemp[j + 1]:
                                    rankemp[j], rankemp[j+1] = rankemp[j+1], rankemp[j]
                                    temparray[j], temparray[j + 1] = temparray[j + 1], temparray[j]
                        for k in range(0, len(temparray)):
                            for j in range(0, len(pos)):
                                if temparray[k] == pos[j]:
                                    addemp = 0
                                    posindex = pos[j][0]
                                    poscolumn = pos[j][1]
                                    inc = increasedata[j]
                                    while (round(inc,0) >= 0) and (newEAP - counter > 0):
                                        if fcount != 0:
                                            inc = 1
                                        addemp += 1
                                        counter += 1
                                        inc = (inc - 1)*(rowtotal/(rowtotal + 1))
                                    
                                    newemp.append(data2.at[posindex - 1, poscolumn] + addemp)
                                    posemp.append([posindex, poscolumn])
                                    data3.loc[posindex -1, poscolumn] = newemp[len(newemp)-1]
                    counteremp += instancecounter
                    instances = True
        if round(sum(increasedata),0) < newEAP:
            break
                    
        
    data3.index = pd.RangeIndex(len(data3.index))
    data3 = data3.drop([1,2,3,4,6,7,8,9,11,12,13,14,16,17,18,19,21,22,23,24,26,27,28,29])
    data3 = data3.reset_index(drop = True)       
    
    FNMtotal = data1.iloc[6,9]
    FNFtotal = data1.iloc[6,10]
    temp = (list(data1.iloc[7]))
   
    data1 = data1.reset_index(drop = False)
    data1.index += 1
    data1 = data1.iloc[:6]
    total = ['TOTAL PERMANENT']
    grandtotal = ['GRAND TOTAL']
    for k in range(1,9):
        TotalColour = 0
        
        for j in range(0,6):
            TotalColour += data3.iat[j,k]
        total.append(TotalColour)
        grandtotal.append(TotalColour)
    data3.loc[len(data3.index)+1] = total
    grandtotal.append(FNMtotal)
    grandtotal.append(FNFtotal)
    
  
    
    FNMdata = list(data1['Foreign National Male'])
    FNFdata = list(data1['Foreign National Female'])
    FNMdata.append(FNMtotal)
    FNFdata.append(FNFtotal)
    data3['Foreign National Male'] = FNMdata
    data3['Foreign National Female'] = FNFdata
    colourtotals = []
    temptotal = 0
    for k in range(0,7):
        coloursum = 0
        for j in range(1,11):
            coloursum += data3.iat[k,j]   
        colourtotals.append(coloursum)
    
    data3['Total'] =  colourtotals  
    
    data3 = data3.reset_index(drop = True)
    data3.index += 1
    data3.loc[len(data3.index)+1] = temp
    grandtotal.append(colourtotals[len(colourtotals)-1] + temp[-1])
    for j in range(1,11):
        grandtotal[j] = grandtotal[j] + temp[j]
    data3.loc[len(data3.index)+1] = grandtotal
    return data3


def yearplanner(companydb, level, seclevel, growth, years):
    data1 = expectedEAP(companydb, level, seclevel)
    for k in range(0, years):
        yeardata = yearplan(data1, level, seclevel, growth)
        data1 = expectedEAP(yeardata, level, seclevel)
    yeardata.drop([10, 11])
    return yeardata


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///companies.db'

db = SQLAlchemy(app)

#db.init_app(app)
dbentry = []
Rowheadings = ['Top Management',
 'Senior Management',
  'Professionally qualified and experienced specialists and mid-management',
  'Skilled technical and academically qualified workers, junior management, supervisors, foremen, and superintendents',
  'Semi-skilled and discretionary decision making',
  'Unskilled and defined decision making',
  'TOTAL PERMANENT',
  'Temporary employees',
  'GRAND TOTAL']
Rowcontent = ['MA',
'MC',
'MI',
'MW',
'FA',
'FC',
'FI',
'FW',
'FNM',
'FNF']


class company(db.Model):
    Occupational_Level = db.Column('Occupational Levels',db.String, primary_key = True)
    AM = db.Column('African Male',db.Integer, nullable =False)
    CM = db.Column('Coloured Male',db.Integer, nullable =False)
    IM = db.Column('Indian Male', db.Integer, nullable =False)
    WM = db.Column('White Male',db.Integer, nullable =False)
    AF = db.Column('African Female',db.Integer, nullable =False)
    CF = db.Column('Coloured Female',db.Integer, nullable =False)
    IF = db.Column('Indian Female',db.Integer, nullable =False)
    WF = db.Column('White Female',db.Integer, nullable =False)
    FNM = db.Column('Foreign National Male',db.Integer, nullable =False)
    FNF = db.Column('Foreign National Female',db.Integer, nullable =False)
    Total = db.Column('Total',db.Integer, nullable =False)

def __repr__(self):
    return self.AM, self.CM, self.IM, self.WM, self.AF, self.CF, self.IF, self.WF, self.FNM, self.FNF







@app.route('/OPD', methods = ['POST', 'GET'])



def index():
    if request.method == 'POST':
        
        with app.app_context():
            db.drop_all()
        with app.app_context():
            db.create_all()
        dbentry = []
        for k in range(0, 6):
            dbnewentry = []
            total = 0
            dbnewentry.append(Rowheadings[k])
            for j in range(0, len(Rowcontent)):
                add_str = Rowcontent[j] + str(k+1)
                dbnewentry.append(int(request.form[add_str]))
                total += int(request.form[add_str])
            dbnewentry.append(total)
        
            dbentry.append(dbnewentry)
        dbnewentry = ['TOTAL PERMANENT']
        total = 0
        for k in range(0, len(Rowcontent)):
            totalperm = 0
            for j in range(0, 6):
                add_str = Rowcontent[k] + str(j+1)
                totalperm += int(request.form[add_str])
                total += int(request.form[add_str])
            dbnewentry.append(totalperm)
        dbnewentry.append(total)
        dbentry.append(dbnewentry)
        dbnewentry = ['Temporary Employees']
        total = 0
        for k in range(0, len(Rowcontent)):
            add_str = Rowcontent[k] + str(7)
            dbnewentry.append(int(request.form[add_str]))
            total += int(request.form[add_str])
        dbnewentry.append(total)
        dbentry.append(dbnewentry)
        dbnewentry = ['GRAND TOTAL']
        grandtotal = 0 
        total = 0
        for k in range(1,len(Rowcontent)+1):
            grandtotal += int(dbentry[6][k])
            grandtotal += int(dbentry[7][k])
            dbnewentry.append(grandtotal)
            total += grandtotal
            grandtotal = 0
        dbnewentry.append(total)
        dbentry.append(dbnewentry) 

        for k in range(0, len(Rowheadings)):
            next_entry = company(
            Occupational_Level = dbentry[k][0],
            AM = dbentry[k][1],
            CM = dbentry[k][2],
            IM = dbentry[k][3],
            WM = dbentry[k][4],
            AF = dbentry[k][5],
            CF = dbentry[k][6],
            IF = dbentry[k][7],
            WF = dbentry[k][8],
            FNM = dbentry[k][9],
            FNF = dbentry[k][10],
            Total = dbentry[k][11])
            with app.app_context():
                db.session.add(next_entry)
                db.session.commit()

        
        return redirect('/Result')
       
    else:
        pass
    return render_template('OPD.html')

@app.route('/display', methods = ['GET', 'POST'])
def display():
    if request.method == 'GET':
        return render_template('display.html')

    
@app.route('/Result', methods = ['GET', 'POST'])
    
def calc():
    if request.method == 'GET':
        
        return render_template('Result.html')

@csrf_exempt
@app.route('/process', methods = ['POST', 'GET'])
def ProcessCompanyInfo():
    if request.method == 'POST':
        global Company_Name, Level, Sec_Level, Growth, Years
        company_dict = request.form.to_dict(flat=False)
        Company_Name = company_dict['CompanyName'][0]
        Level = company_dict['Level'][0]
        Sec_Level = company_dict['SecLevel'][0]
        Growth = int(company_dict['Growth'][0])
        Years = int(company_dict['Years'][0])
        return json.dumps({'success': True})
    if request.method == 'GET':
        conn = sqlite3.connect('C:\\Users\\jamie\\OPD-Calculator\\instance\\companies.db')
        sql_query = pd.read_sql('''SELECT * from company''', conn)
        companydf = pd.DataFrame(sql_query, columns = ['Occupational Levels',
        'African Male',
        'Coloured Male',
        'Indian Male',
        'White Male',
        'African Female',
        'Coloured Female',
        'Indian Female',
        'White Female',
        'Foreign National Male',
        'Foreign National Female',
        'Total'])
        primarydict = {}
        data1 = expectedEAP(companydf, Level, Sec_Level)
        for i in range(0, Years):
            data2 = yearplan(data1, Level, Sec_Level, Growth)
            data2 = data2.iloc[:9]
            data1 = expectedEAP(data2, Level, Sec_Level)
            JSON_list = data2.values.tolist()
            JSONkeys = []
            JSONdata = []
            for k in range(0, len(JSON_list)):
                JSONkeys.append(JSON_list[k][0])
                tempdata = []
                for j in range(1, len(JSON_list[0])):
                    tempdata.append(JSON_list[k][j])
                JSONdata.append(tempdata)
            JSONdict = dict.fromkeys(JSONkeys)
            for j, val in enumerate(JSONkeys):
                JSONdict[val] = JSONdata[j]
            Year_str = "Year%s" % (i+1)
            primarydict.update({Year_str: JSONdict})
            JSONdict = {}
    
        return jsonpify(primarydict)

@app.route('/employees', methods = ['GET'])
def getExpectedEAP():
    conn = sqlite3.connect('C:\\Users\\jamie\\OPD-Calculator\\instance\\companies.db')
    sql_query = pd.read_sql('''SELECT * from company''', conn)
    companydf = pd.DataFrame(sql_query, columns = ['Occupational Levels',
    'African Male',
    'Coloured Male',
    'Indian Male',
    'White Male',
    'African Female',
    'Coloured Female',
    'Indian Female',
    'White Female',
    'Foreign National Male',
    'Foreign National Female',
    'Total'])
    primarydict = {}
    data1 = expectedEAP(companydf, Level, Sec_Level)
    for i in range(0, Years):
        JSON_list = data1.values.tolist()
        JSONkeys = []
        JSONdata = []
        for k in range(0, len(JSON_list)):
            JSONkeys.append(JSON_list[k][0])
            tempdata = []
            for j in range(1, len(JSON_list[0])):
                tempdata.append(JSON_list[k][j])
            tempdata = [float(item) if item != ' ' else item for  item in tempdata]
            tempdata= [round(item, 2) if item != ' ' else item for item in tempdata]
            JSONdata.append(tempdata)
        JSONdict = dict.fromkeys(JSONkeys)
        for j, val in enumerate(JSONkeys):
            JSONdict[val] = JSONdata[j]
        Year_str = "Year%s" % (i+1)
        primarydict.update({Year_str: JSONdict})
        JSONdict = {}
        data1 = yearplan(data1, Level, Sec_Level, Growth)
        data1 = expectedEAP(data1, Level, Sec_Level)
    return jsonpify(primarydict)

@app.route('/organisational', methods = ['GET'])
def getOrganisationalEAP():
    conn = sqlite3.connect('C:\\Users\\jamie\\OPD-Calculator\\instance\\companies.db')
    sql_query = pd.read_sql('''SELECT * from company''', conn)
    companydf = pd.DataFrame(sql_query, columns = ['Occupational Levels',
    'African Male',
    'Coloured Male',
    'Indian Male',
    'White Male',
    'African Female',
    'Coloured Female',
    'Indian Female',
    'White Female',
    'Foreign National Male',
    'Foreign National Female',
    'Total'])
    primarydict = {}
    data1 = organisationalEAP(companydf, Level, Sec_Level)
    data3 = yearplan(companydf,Level, Sec_Level, Growth)
    for i in range(0, Years):
        JSON_list = data1.values.tolist()
        JSONkeys = []
        JSONdata = []
        for k in range(0, len(JSON_list)):
            if JSON_list[k][0] in JSONkeys:
                continue
            else:
                JSONkeys.append(JSON_list[k][0])
        JSONdict = dict.fromkeys(JSONkeys)
        for j, val in enumerate(JSON_list):
            JSONdata = val[1:]
            JSONdata = [float(item) for item in JSONdata]
            JSONdata = [round(item, 2) for item in JSONdata]
            if (val[0] in JSONkeys[1:5]) and (JSONdict[val[0]] != None):
                JSONdict[val[0]] += JSONdata
            else:
                JSONdict[val[0]] = JSONdata
        Year_str = "Year%s" % (i+1)
        primarydict.update({Year_str: JSONdict})
        JSONdict = {}
        data3 = yearplan(data3, Level, Sec_Level, Growth)
        data1 = organisationalEAP(data3, Level, Sec_Level)
    return jsonpify(primarydict)





app.static_folder = 'static'

if __name__== '__main__':
    app.run(port=8000, debug=True)

