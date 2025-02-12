import pandas as pd
import folium
import numpy as np

# 避難所データ
url = "https://data.bodik.jp/dataset/d169e872-ffe1-4ce7-8bf7-f6550d89d119/resource/ed5a87de-9b3c-443a-ab6e-41b87a55baac/download/siteihinanjo20240401.csv"
df_evac = pd.read_csv(url)

# AEDデータ
url = "https://data.bodik.jp/dataset/5b8584bf-9044-499e-8d85-084e32a90334/resource/9401f2d1-bcf7-40e3-b7ac-294228bb06d4/download/aed202403.csv"
df_aed = pd.read_csv(url, encoding="shift_jis")

pd.set_option('display.unicode.east_asian_width', True)
# print(df.head())

# 宮崎市中心
pos = [31.9111, 131.4239]
map = folium.Map(location=pos, zoom_start=15)

# 避難所レイヤー
evac_layer = folium.FeatureGroup(name="避難所").add_to(map)
# 避難所マーカー
evac_center = df_evac[["緯度", "経度", "名称", "住所", "電話番号", "想定収容人数"]].values
for data_evac in evac_center:
    if np.isnan(data_evac[0]) or np.isnan(data_evac[1]):
        continue # エラー防止
    popup_html = f"""
    <div style="width: 200px; font-size:12px;">
        <b style="font-size: 14px; display: block">{data_evac[2]}</b><br>
        <b>住所：</b>{data_evac[3]}<br>
        <b>電話：</b>{data_evac[4]}<br>
        <b>想定収容人数：</b>{data_evac[5]}人<br>
    </div>
    """
    folium.Marker(
        location=[data_evac[0], data_evac[1]],
        tooltip=data_evac[2],
        popup=folium.Popup(popup_html, max_width=250),
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(evac_layer)

# AEDレイヤー
aed_layer = folium.FeatureGroup(name="AED").add_to(map)
# AEDマーカー
aed_location = df_aed[["緯度", "経度", "名称", "住所", "設置位置"]].values
for data_aed in aed_location:
    if np.isnan(data_aed[0]) or np.isnan(data_aed[1]):
        continue
    popup_html = f"""
    <div style="width: 200px; font-size:12px;">
        <b style="font-size: 14px; display: block">{data_aed[2]}</b><br>    
        <b>住所：</b>{data_aed[3]}<br>
        <b>設置位置：</b>{data_aed[4]}<br>
    </div>
    """
    folium.Marker(
        location=[data_aed[0], data_aed[1]],
        tooltip=data_aed[2],
        popup=folium.Popup(popup_html, max_width=250),
        icon=folium.Icon(color="orange", icon="heart")
    ).add_to(aed_layer)

# 洪水ハザードマップ（想定最大規模）
flood_tile_url = "https://disaportaldata.gsi.go.jp/raster/01_flood_l2_shinsuishin_data/{z}/{x}/{y}.png"
folium.TileLayer(
    tiles=flood_tile_url,
    attr="国土地理院", # 右下に@国土地地理院と表示される
    name="洪水ハザードエリア",
    overlay=True,
    control=True,
    opacity=0.7
).add_to(map)

# 津波ハザードマップ（宮崎県）
tsunami_tile_url = "https://disaportaldata.gsi.go.jp/raster/04_tsunami_newlegend_pref_data/45/{z}/{x}/{y}.png"
folium.TileLayer(
    tiles=tsunami_tile_url,
    attr="国土地理院",
    name="津波ハザードエリア",
    overlay=True,
    control=True, # LayerControlに追加
    opacity=0.7
).add_to(map)

# 洪水・津波凡例（画像）を地図に追加
legend_html = """
<div style="
    position: absolute; 
    bottom: 20px; left: 20px; 
    width: 180px; 
    background-color: rgba(255, 255, 255, 0.7); 
    padding: 10px; 
    font-size: 12px; 
    border: 1px solid black; 
    z-index:9999;">
    <b>凡例</b><br>
    <img src="static/shinsui_legend3.png">
</div>
"""
# folium に凡例を追加
map.get_root().html.add_child(folium.Element(legend_html))
"""
map.get_root() → Foliumの地図のルート（HTMLのベース要素）を取得
.html.add_child(...) → 地図のHTMLに新しい要素を追加
folium.Element(legend_html) → legend_html（カスタムHTML）を FoliumのHTML要素として認識 させる
"""

# CCライセンス
cc_license_html = """
    <div style="position: absolute; bottom: 0px; right: 10px; background-color: rgba(255, 255, 255, 0.7);
                padding: 8px; font-size: 8px; z-index: 1000;">
        <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">
            <img style="margin-bottom: 10px;" src="https://licensebuttons.net/l/by/4.0/88x31.png" alt="CC BY 4.0">
        </a>
        <p>この地図のデータは <a href="https://data.bodik.jp/dataset/452017_hinanjo" target="_blank">宮崎市避難所データ</a> を使用し、CC BY 4.0 ライセンスのもとで提供されています。</p>
        <p>この地図のデータは <a href="https://data.bodik.jp/dataset/452017_aed" target="_blank">AED設置場所一覧</a> を使用し、CC BY 4.0 ライセンスのもとで提供されています。</p>
        <p>この地図のデータは <a href="https://disaportal.gsi.go.jp/hazardmapportal/hazardmap/copyright/opendata.html#l2shinsuishin" target="_blank">国土地理院ハザードマップ</a> を使用し、CC BY 4.0 ライセンスのもとで提供されています。</p>
    </div>
    """
map.get_root().html.add_child(folium.Element(cc_license_html))    

# カスタムCSSを定義
custom_css = """
<style>
    .leaflet-control-layers {
        font-size: 16px !important;  /* プルダウン全体のフォントサイズを大きく */
        padding: 20px !important; /* 余白を広げる */
        width: 200px !important;
        height: 170px !important; 
        background-color: rgba(0, 0, 0, 0.8) !important; 
        border-radius: 8px !important;  
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3) !important;  /* 影をつける */
        color: white !important;
    }
    .leaflet-control-layers-toggle {
        width: 50px !important;  /* ボタンの幅を広げる */
        height: 50px !important;  /* ボタンの高さを広げる */
    }
    .leaflet-control-layers-list {
        font-size: 14px !important;  /* リストのフォントサイズ */
    }
</style>
"""
# CSSを地図に追加
map.get_root().header.add_child(folium.Element(custom_css))

# レイヤーコントロールを追加
folium.LayerControl(collapsed=False).add_to(map)

map.save("dp_map.html")

