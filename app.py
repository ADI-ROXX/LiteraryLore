from flask import Flask,render_template,request
import pandas as pd
from selenium import webdriver

from selenium.webdriver.firefox.options import Options
from thefuzz import fuzz,process
from selenium.webdriver.common.by import By

import json

import warnings

warnings.filterwarnings("ignore")


app = Flask(__name__)

popular=pd.read_csv('popular.csv')
similarity=pd.read_csv("collaborative_filter.csv")
pd.set_option("display.max_columns", 40)

def search_seq(seq):
    names=list(popular["Book-Title"])
    authors=list(popular["Book-Author"])
    ret=[]
    for i in process.extract(seq,names):
        if(i[1]>=70):
            ret.append(i[0])
    for i in process.extract(seq,authors):
        if(i[1]>=70):
            ret.append(i[0])
    print(ret)
    return ret

@app.route('/')
def hello():

    names_list=[]
    for i in popular["Book-Title"]:
        if len(i)>15:
            try:
                names_list.append(i[0:i.index(" ",60)]+"...")
            except:
                names_list.append(i)
                
        else:
            names_list.append(i)
    return render_template("index.html",isbn=list(popular["ISBN"].values),name=names_list,
                            author=list(popular["Book-Author"].values),
                            image=list(popular["Image-URL-L"].values))
    
@app.route("/search",methods=["post"])
def search():
    seq=str(request.form.get('isbn'))
    names_list=search_seq(seq)
    cols=popular.columns[2:]
    final_df=pd.DataFrame(columns=cols)
    for i in names_list:
        if(popular[popular["Book-Title"]==i].shape[0]==1):
            print(popular[popular["Book-Title"]==i].iloc[0,2:])
            final_df.loc[len(final_df.index)]=popular[popular["Book-Title"]==i].iloc[0,2:]
        if(popular[popular["Book-Author"]==i].shape[0]==1):
            print(popular[popular["Book-Author"]==i].iloc[0,2:])
            final_df.loc[len(final_df.index)]=popular[popular["Book-Author"]==i].iloc[0,2:]

    print(final_df)

    names_list=[]
    for i in final_df["Book-Title"]:
        if len(i)>15:
            try:
                names_list.append(i[0:i.index(" ",60)]+"...")
            except:
                names_list.append(i)
                
        else:
            names_list.append(i)
    return render_template("search.html",rec_name=names_list,rec_author=list(final_df["Book-Author"].values),
                                        rec_image=list(final_df["Image-URL-L"].values),
                                        rec_isbn=list(final_df["ISBN"].values))

@app.route("/recommend",methods=["post"])
def recommend():
    isbn = str(request.form.get('isbn'))

    closest = similarity[similarity["ISBN"]==isbn]
    if(closest.shape[0]==0):
        return render_template("search.html",rec_name=[])
    closest=closest.iloc[0,1:21]
    c=0
    dict={}
    for i in closest:
        dict[i]=c
        c+=1
    
    df=pd.DataFrame()
    df["ISBN"]=closest
    final_df=popular[popular["ISBN"].isin(df["ISBN"])]
    final_df=final_df.sort_values(by=['ISBN'], key=lambda x: x.map(dict))

    first=final_df.iloc[0,:]
    print(first)
    final_df=final_df.iloc[1:,:]
    content=first["Content"]
    first_content=""
    for i in range(len(content)):
        if not content[i]=="\n":
            break
    first_content=content[i:]
    names_list=[]
    for i in final_df["Book-Title"]:
        if len(i)>15:
            try:
                names_list.append(i[0:i.index(" ",60)]+"...")
            except:
                names_list.append(i)
                
        else:
            names_list.append(i)
    first_content=first_content.replace("\n\n","\n").replace("\n","\n\n")
    return render_template("recommend.html",name=names_list,author=list(final_df["Book-Author"].values),
                                        image=list(final_df["Image-URL-L"].values),
                                        isbn=list(final_df["ISBN"].values),
                                        first_name=first["Book-Title"],
                                        first_author=first["Book-Author"],
                                        first_image=first["Image-URL-L"],
                                        first_content=first_content
                                        )

