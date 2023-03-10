from flask import Flask, render_template, request, redirect
from web_back import get_coords
from web_back import search_for_artist_name
from web_back import get_top_1_song_of_artist
import folium

app = Flask(__name__)


@app.route('/search4', methods=['POST'])

def do_search():
    phrase = request.form['phrase']
    if search_for_artist_name(phrase) == None:
        return render_template('mistake.html')
    elif get_top_1_song_of_artist(phrase) == None:
        return render_template('mistake.html')
    coords = get_coords(phrase)

    map = folium.Map(zoom_start=3)
    second_map = folium.FeatureGroup(name="Second layer")
    

    html = """Country name: {}<br>"""

    
    for i in (coords):
            iframe = folium.IFrame(html=html.format(i[0]),
                          width=200,
                          height=100)
            second_map.add_child(folium.Marker(location=[i[1][0], i[1][1]],
                                    popup=folium.Popup(iframe),
                                    icon=folium.Icon(color = "red"), zoom_start = 3))
    map.add_child(second_map)
    map.add_child(folium.LayerControl())
    return render_template('results.html', map=map._repr_html_())

@app.route('/')
@app.route('/entry')
def entry_page():
    return render_template('entry.html', the_title='Welcome to the available markets looker')

if __name__ == '__main__':
    app.run(debug = True)