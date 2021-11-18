from flask import Flask, render_template
import geopandas as gpd
import pandas as pd
import folium

def create_app():
    app = Flask(__name__)    

    @app.route('/')
    def home():
        # 獲得109年度資料 (Get Data)
        taiwan_data = pd.read_csv('./web/data/birth-109.csv')

        # 用 Slice分隔縣市與區域，再加入新增的 Column 
        # (Before added in new Column, use 'Slice' divide 'city' and 'region' from orginal data)
        taiwan_data['city'] = taiwan_data.site_id.str[:3]

        # 使用縣市做 groupby，並且加總 (Use 'city' column do groupby and get sum)
        city_group = taiwan_data.groupby('city')
        city_group_total = city_group.sum()

        # 為了與'城市經緯度'資料做 Merge 改名 
        # (Change name 'city' to 'COUNTYNAME' for Merge data with 'LatLng data')
        city_group_total.index.rename('COUNTYNAME', inplace=True)

        # 讀取台灣縣市的經緯度資料 (Get data of Taiwan city LatLng)
        tw_region = gpd.read_file('./web/data/COUNTY_MOI_1090820.json')

        # Merge Data
        taiwan_region_birth = tw_region.merge(city_group_total,on="COUNTYNAME")

        # Create map
        m = folium.Map(location=[23.858987, 120.917631],zoom_start=8)

        # Change folium theme
        folium.TileLayer('CartoDB positron', name="Light Map").add_to(m)

        style_function = lambda x: {'fillColor': '#ffffff', 
                                    'color':'#000000', 
                                    'fillOpacity': 0.1, 
                                    'weight': 0.1}
        highlight_function = lambda x: {'fillColor': '#000000', 
                                        'color':'#000000', 
                                        'fillOpacity': 0.50, 
                                        'weight': 0.1}

        folium.GeoJson(
            taiwan_region_birth,
            style_function=style_function,
            control=False,
            highlight_function=highlight_function, 
            tooltip=folium.features.GeoJsonTooltip(
                fields=['COUNTYNAME','birth_count'],
                aliases=['城市: ','出生人數: '],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
            )
        ).add_to(m)
        m.keep_in_front()
        
        return m._repr_html_()

    return app
