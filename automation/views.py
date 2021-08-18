from django.shortcuts import render
from django.http import HttpResponse
from numpy import inner
from selenium import webdriver
from selenium.webdriver.common.by import By 
import matplotlib.pyplot as plt 
import pandas as pd
import time

# Create your views here.
def home(request):
    return render(request, 'automation/home.html')

def search(request):
    html_code = ""
    state_name = ""
    total_state_data=""
    
    if request.method == 'POST':
        state_name = request.POST['search'].capitalize()
        state_code_data = pd.read_csv('state_code.csv')
        state_code = state_code_data.loc[state_code_data["State"] == state_name, "State_code"].iloc[0]     
        url = "https://www.covid19india.org/state/"+state_code
        print("state code data :",state_code_data)
        print("state name :",state_name)
        print("state code :",state_code)
        print("url :",url)

        driver = webdriver.Chrome()
        driver.maximize_window()
        driver.get(url)
        time.sleep(2)
        map_block = driver.find_element(By.ID, "chart")
        html_code = map_block.get_attribute('outerHTML')
        print(html_code)
        time.sleep(2)
        driver.quit()
        state_wise_daily = pd.read_csv("state_wise_daily.csv")
        print(state_wise_daily.head())
        for_confirmed = state_wise_daily.loc[state_wise_daily['Status']=="Confirmed",['Date',state_code]]
        for_confirmed.rename(columns = {state_code: "Confirmed"},inplace=True)
        print(for_confirmed)

        for_recovered = state_wise_daily.loc[state_wise_daily['Status']=='Recovered',['Date', state_code]]
        for_recovered.rename(columns={state_code:"Recovered"}, inplace=True)

        for_decease = state_wise_daily.loc[state_wise_daily['Status']=='Deceased',['Date', state_code]]
        for_decease.rename(columns={state_code:"Deceased"}, inplace=True)

        temp = pd.merge(for_confirmed,for_recovered, on='Date', how=inner)
        final_state_wise = pd.merge(temp, for_decease, on='Date', how=inner)
        final_state_wise['Active'] = final_state_wise['Confirmed'] - final_state_wise['Recovered'] - final_state_wise['Deceased']
        final_state_wise['cf_Confirmed'] = final_state_wise['Confirmed'].cumsum()
        final_state_wise['cf_Recovered'] = final_state_wise['Recovered'].cumsum()
        final_state_wise['cf_Deceased'] = final_state_wise['Deceased'].cumsum()
        final_state_wise['cf_Active'] = final_state_wise['Active'].cumsum()
        final_state_wise = final_state_wise[['Date','cf_Confirmed','cf_Recovered','cf_Deceased','cf_Active']]
        print(final_state_wise.tail(2))
        total_state_data = final_state_wise.tail(1)
        final_state_wise.Date = pd.to_datetime(final_state_wise.Date)
        final_state_wise.set_index('Date', inplace=True)
        plot = final_state_wise.plot(figsize=(20,10), linewidth=5, fontsize=20,color = ['steelBlue','Green','Red','Orange'])
        plot.set_xlabel('Date', fontsize=20)
        plot.set_ylabel('No. of Cases', fontsize=20)
        plot.set_title(state_name, fontsize=20)
        plot.legend(["Confirmed","Recovered","Death","Active"],fontsize=20)
        fig = plot.get_figure()
        fig.savefig("static/images/output.png")

    context = {
        "html_code":html_code,
        "state_name":state_name,
        "total_state_data":total_state_data,
        "img_name":"output.png"
        }
    
    res = render(request, 'automation/home.html', context)
    return res


