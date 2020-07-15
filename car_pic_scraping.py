#!/usr/bin/env python
# coding: utf-8

# ### 車の写真をダウンロードする 
#   
# 川口先生、澤田先生こんにちは。こちらローカルのディレクトリ内にurlから画像をダウンロードして、相対パスを取得するコードになります。 
# カレントディレクトリ内にpicturesというフォルダを作成し、そこに画像をダウンロードしていくものになります。      
# 使用するファイルは、slackでお送りしたcar_pictures.csvというファイルです。このファイルにはutf-8形式で  
# ```
# [manufacture,model,version,pic_no,pic_url]
# ``` 
# が格納されています。      
# このpic_urlから画像をダウンロードするコードになります。（画像名はmanufacture_version_picnoになります）    
# （例）"レクサスＣＴ ＣＴ２００ｈ バージョンＬ（2011年8月）0"     
# 最終的に出力されるファイル"car_pictures_complete.csv"には、もともとのcar_pictures.csvのファイルの5列目にダウンロードした先の相対パスを格納したものになります。     
# 最初は小さめのデータセットで試していただいて（car_pictures_small.csvという名前のファイルです）、ファイルがpicturesのフォルダに200個ダウンロードされるかを確認してください。問題がなければダウンロードした画像をすべて消去したのちに、本番のデータセットで実施していただければと思います。 200個の画像ファイルをダウンロードするのに約22.5秒かかりました。今回は約51万件の画像データがありますので、順調にいっても15時間以上かかる計算です、、、

# In[1]:


#picture scrapingに必要なlibraryをインポート
import os
import pprint
import time
import urllib.error
import urllib.request
import csv
import pandas as pd


# In[2]:


#urlから写真をダウンロードする関数を定義
def download_file(url, dst_path):
    try:
        with urllib.request.urlopen(url) as web_file, open(dst_path, 'wb') as local_file:
            local_file.write(web_file.read())
    except urllib.error.URLError as e:
        print(e)    


# In[10]:


#カレントディレクトリ内にpicturesという名前のフォルダを作成。このフォルダの中にダウンロードしていく
new_dir_path = os.path.join(str(os.getcwd()),"pictures")
os.mkdir(new_dir_path)
#カレントディレクトリを確認
print(os.getcwd())

#もしカレントディレクトリを変更したい場合は下記のコードで行って下さい
#os.chdir('Documents/川口先生RA')


# In[3]:


#車種と写真のダウンロード元urlが入っているcar_pictures.csvを読み込み、df_picsに格納
#car_pictures.csvのファイルはこのコードと同じ階層のフォルダに格納して下さい

#練習用
df_pics = pd.read_csv('car_pictures_small.csv', encoding = 'utf-8',index_col=0)
# ※本番用※
#df_pics = pd.read_csv('car_pictures.csv', encoding = 'utf-8')

lst_path = []
j = 0

#カレントディレクトリ内に作成したpicturesというフォルダにダウンロードしています
for i in range(len(df_pics)):
    add_path = str(df_pics.iloc[i,0]) + str(df_pics.iloc[i,2]) + str(df_pics.iloc[i,3])
    dst_path = "pictures/"+add_path+'.png'
    url = df_pics.iloc[i,4]
    download_file(url, dst_path)
    lst_path.append(dst_path)

    
#df_picsの末尾列にダウンロードしたファイルのパスを格納
df_pics = df_pics.assign(path = lst_path)

#ダウンロード先のpathも格納されたパネルデータがcar_pictures_complete.csvという名前で出力されます（utf-8出力）
df_pics.to_csv('car_pictures_complete.csv', encoding = 'utf-8')

#'done'と表示されたら正常に終了しています
print('done')
print(df_pics)

