#!/usr/bin/env python
# coding: utf-8

# ## 車の写真をダウンロードする    
#    
# こちらは車のデータをスクレイピングするコードになります。まず、ウェブサイトのurlとその構造は下記の通りです。      
# 
# [グーネット中古車 ウェブサイト](https://www.goo-net.com/catalog/)    
# ├── LEXUS     
#     ├── CT      
#         ├── CT200h 2019年10月モデル      
#         ├── CT200h バージョンC 2019年10月モデル      
#         ├── CT200h Fスポーツ 2019年10月モデル      
#         ├── CT200h 2018年10月モデル       
#         （続く）     
#     ├── ES        
#     ├── GS        
#     ├──GSF       
#     （続く）     
# ├── トヨタ     
# ├── 日産     
# ├── ホンダ       
# ├── マツダ      
# └── ユーノス       
#       
# 下記コードにはこれらの階層を潜っていく際に、"manufacture", "model", "grade", "version" という4つの種類の変数が登場しますが、それらはそれぞれ各車の以下の情報を指しています。gradeとversionが情報がかぶっていたり、日本語のモデルと"model"が対応していなかったりして申し訳ありませんが、対象サイトのHTML表記に従った結果ですので何卒ご理解いただけますと幸いです。  
# ```
# "manufacture" = "LEXUS"    
# "model" = "CT"    
# "grade" = "CT200h"    
# "version" = "CT200h 2019年10月モデル"    
# ```   
#    
# ウェブサイトを見ていただけると、1つの "version" から取得したデータが1行に並ぶ形です。本コードでは、"urls.csv"（"version"とそのサイトのurlが一対一に対応しているデータ）というファイルからすべての車の "version" の情報をスクレイピングしていきます。   
# およそ10万件すべてのウェブページが同じHTML表記で記載されているわけではなかったので、エラーが起こる旅にそこまでスクレイプしたデータをいったん保存し、エラー原因を修正した後に再び再開する、というのを繰り返しました。一番最後に今までのデータをつなぎ合わせて一つのデータセットにしましたので、このコードが全くエラーなく10万件ダウンロードするとは限りません。ご了承ください。

# In[2]:


#共通DL
#このコードに必要なライブラリをインポートします。
import re
import requests
import time
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0"}
feature = ["column1","column2"]
from urllib.parse import urljoin
base_url = 'https://www.goo-net.com/'


# In[9]:


#必要な関数を定義

#各車の"version"のページに含まれている情報をスクレイピングして、1行×120～130列のpd.Seriesデータとして出力する関数です。
def scrape_Car_info(url,manu,model,grade):
    #モデル、新車価格、中古車価格、細かい情報をpd.Seriesとして返す
    #indexも同時に設定する
    #lst_indexを定義
    lst_index = ['manufacture','model','grade','version','new_car_price','used_car_price_min','used_car_price_max']
    
    #car_info（リスト型）変数を定義
    lst_car_price=[]    #lst_car_price　このリストにページ上の情報を一つ一つ.appendで格納していく
    lst_car_price.append(manu)
    lst_car_price.append(model)
    lst_car_price.append(grade)
    response = requests.get(url=url, headers=headers)
    html = response.content
    soup = BeautifulSoup(html, "html.parser")
    
    #タイトルをスクレイピングする。これが各車のversion（〇〇年モデルも含む各車固有の名前）に相当する
    title = soup.find_all("title")
    title_text = title[0].get_text(strip=True)
    txt_title = title_text.split('のカタ')[0]
    lst_car_price.append(txt_title)
    
    #価格をスクレイピング（新車→中古車の順）
    prices = soup.find_all("span",{"class","price"})
    for i in prices:
        price =i.get_text(strip=True)
        lst_car_price.append(price)
    #中古車価格が存在しない場合もあったため、その時は中古車価格の列に欠損値を入力するようにしている
    if len(prices) == 1:       
        lst_car_price.append(np.nan)
        lst_car_price.append(np.nan)

    sr_car_price = pd.Series(lst_car_price)
    
    #細かい情報をスクレイピング　エラーはここで発生することがほとんどです。
    #ここで、対象ページにある表形式のデータがすべてdfのかたまりとして複数取得されるのだが、車種によって何個目のかたまりにどの情報が含まれるか
    #というのが異なってくるので、ここでエラー毎にサイトの構造に合わせて条件分岐を作成した。
    #大体の場合、df[0]からdf[9]までに普通の情報が含まれ（80行程度×2列のデータ）、df[10]に車の色とメーカーオプションに関するデータが含まれる
    #（20行程度×3列のデータ。列数が異なるため別々に処理して、色のデータも2列のデータに変更している）
    df = pd.read_html(url)
    a = df[0].columns
    if len(df)>12:
        b = df[12].columns
        #d = df[13].columns
    else:
        b = []
        #d = []
    c = df[11].columns
    
    if len(a)==3: #ホンダインテグラ
        if len(c) == 3 : #ルノー　メガーヌ
            df_car_info = pd.concat([df[1],df[2], df[3],df[4], df[5],df[6],df[7],df[8], df[9], df[10]], axis=0)
            df_car_color = df[11]
        else:
            df_car_info = pd.concat([df[1],df[2], df[3],df[4], df[5],df[6],df[7],df[8], df[9], df[10],df[11],df[12]], axis=0)
            df_car_color = df[13]
    elif len(b)==3: #ホンダ　アコードインスパイア
        df_car_info = pd.concat([df[0],df[1],df[2], df[3],df[4], df[5],df[6],df[7],df[8], df[9], df[10],df[11]], axis=0)
        df_car_color = df[12]
    elif len(c) == 3: #ホンダ　バモス
        df_car_info = pd.concat([df[0],df[1],df[2], df[3],df[4], df[5],df[6],df[7],df[8], df[9], df[10]], axis=0)
        df_car_color = df[11]
    else: #通常, ヤリスなどlen(df)が13のものも存在するため
        df_car_info = pd.concat([df[0], df[1],df[2], df[3],df[4], df[5],df[6],df[7],df[8], df[9]], axis=0)
        df_car_color = df[10]
    
    #二列目に各車固有のデータが格納されるので、column2と名付けた2列目を取得
    df_car_info.columns=feature
    sr_car_info = df_car_info['column2']
    
    #細かい情報のindexを設定
    sr_index = df_car_info['column1']
    lst_index_add = sr_index.values.tolist()
    
    #色をスクレイピング
    sr_car_color_1 = df_car_color['メーカー標準']
    sr_car_color_2 = df_car_color['メーカーオプション']
    
    #色のindexを設定
    sr_index_color = df_car_color['色系統']   
    lst_index_color = sr_index_color.values.tolist()
    lst_index_color_mo = [i + '_mo' for i in lst_index_color]
    
    #indexのリスト同士をつなげる
    lst_index.extend(lst_index_add)
    lst_index.extend(lst_index_color)
    lst_index.extend(lst_index_color_mo)
    
    #pd.Seriesとしてつなげる
    sr_car_info_cmp = pd.concat([sr_car_price, sr_car_info, sr_car_color_1, sr_car_color_2])
    sr_car_info_cmp.name = model
    
    #sr_car_info_cmpのindexを設定
    sr_car_info_cmp.index = lst_index
    
    return sr_car_info_cmp

#データベースの列名に当たるものを取得する。
def scrape_Car_index(url):
    #indexになるものをリスト形式で返す
    #モデル、新車価格、中古車価格
    lst_index = ['manufacture','model','grade','version','new_car_price','used_car_price_min','used_car_price_max']
    #細かい情報
    df_1 = pd.read_html(url)
    df_index = pd.concat([df_1[0], df_1[1],df_1[2], df_1[3],df_1[4], df_1[5],df_1[6],df_1[7],df_1[8], df_1[9]], axis=0)
    df_index.columns = feature
    sr_index = df_index['column1']
    lst_index_add = sr_index.values.tolist()
    #色
    df_index_color = df_1[10]
    sr_index_color = df_index_color['色系統']
    lst_index_color = sr_index_color.values.tolist()
    lst_index_color_mo = [i + '_mo' for i in lst_index_color]
    #リスト同士をつなげる
    lst_index.extend(lst_index_add)
    lst_index.extend(lst_index_color)
    lst_index.extend(lst_index_color_mo)
    return lst_index


# In[6]:


#df_urls_allをcsvから読み取る
df_urls_all = pd.read_csv('urls.csv', encoding = 'utf-8', index_col=0)
print(df_urls_all)


# In[7]:


##Scrape Car Information 

#dfのindexと空のdfを作成
index_ = scrape_Car_index('https://www.goo-net.com/catalog/LEXUS/CT/10123971/') 
df_a =pd.DataFrame(columns = index_)

#データ数が94168件あるのでfor文で繰り返す。len()を使用してもよかったのだが、エラーが各所で発生したので、2万件づつ区切って実施していたことから
#range関数を利用してfor文を書いている。
for k in range(0,94168):
    df_info = df_urls_all.iloc[k]                                   #'urls.csv'のk行目のデータをdf_infoに格納します
    txt_mf = df_info[0]                                             #df_info[0]が'manufacture'なのでtxt_mfに格納
    txt_m = df_info[1]                                              #df_info[1]が'model'なのでtxt_mに格納
    txt_g = df_info[2]                                              #df_info[2]が'grade'なのでtxt_gに格納
    url_g = df_info[3]                                              #df_info[3]が'url'なのでurl_gに格納
    sr_car_info_ = scrape_Car_info(url_g, txt_mf, txt_m, txt_g)     #sr_car_info_にスクレイプしたpd.Seriesデータを格納
    df_a = df_a.append(sr_car_info_, ignore_index = True)          #df_aの一番末尾行にsr_car_info_に格納したデータを追加
    
#データ保存　※ファイル名を必ず変更すること　（例）20200704_beforeメガクルーザー.csv
df_a.to_csv('DataBase.csv', encoding='utf-8')
#doneと表示されたら終了しています。
print('done')


# ## エラーが発生したら   
#     
# 下記にエラーが発生したときの私の修正方法を書きます。     
# 私がスクレイプしたときに発生したエラーは条件分岐で回避するようにコーディングしたのですが、まだエラーが起こる可能性は捨てきれませんのでもしもの時に備えて。

# In[ ]:


#データ確認
#エラーが発生した行数から、どこの車のページでエラーが発生したのか確認し、そのページに飛んでHTMLの構造を見ます
print(k)    #この値が再びスクレイピングを再開する数字（行数）になります
print(df_a)


# In[ ]:


#とりあえずここまでスクレいいピングしたデータをcsvファイルとして保存します。例は7月4日にメガクルーザーの手前でエラーが発生した場合
#データ保存　※ファイル名を必ず変更すること　（例）20200704_beforeメガクルーザー.csv
df_a.to_csv('20200704_beforeメガクルーザー.csv', encoding='utf-8')


# In[ ]:


#エラー処理
#大体の場合が、scrape_Car_info関数の「細かい情報をスクレイピング」というところで発生します。
#そこで実施していることを抜き出して下記でやってみて、dfの何個目にどんなデータが入っているのか確認し、次に同じタイプのページがあったときは
#分岐してくれるようにコーディングを修正します。

df = pd.read_html('https://www.goo-net.com/catalog/RENAULT/MEGANE/10095015/')
print(df[11])
print(df[13])
print(len(df[13]))
a = df[0].columns
print(len(a))


# In[ ]:


##Scrape Car Informationの下記の行の、range()のなかの数字の前者を、エラーが発生した変数"k"の値に交換して、再開する
##for k in range(※この値を更新※,94168):

