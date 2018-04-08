from flask import Flask, request,redirect, url_for,render_template,flash
import flask
from wtforms import Form, StringField, SelectField,validators
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from Server import Server

app = Flask(__name__)
server = Server()
app.config['GOOGLEMAPS_KEY'] = "AIzaSyDe8MW30wBuY6wBbz9SJo3_apIZeabX_i0"
app.secret_key = "super secret key"
GoogleMaps(app)

class SearchForm(Form):
    name = StringField('Area eg.SW4,NG,London', [validators.Length(min=1, max=50)])
    house_type =SelectField('Property type', choices=[("flat","Flat"),("terraced","Terraced"),("end terrace","End terrace"),("semi-detached","Semi-detached"),("detached","Detached")])


@app.route('/', methods=['GET', 'POST'])
def home_page():
    form = SearchForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        house_type = form.house_type.data
        area = server.parse_sentence(name)
        if area == "Value Error":
            error = "Looks like you entered an unknown region!"
            flash(error)
        else:
            return redirect("/results/"+area+"&"+house_type)
            #search(name,house_type)

    return flask.render_template('index.html', form=form)


@app.route('/results/<name>&<house_type>',methods=['GET'])
def search(name,house_type):
    error = None
    mymap = None

    area_info = server.fetch_area_info(name,house_type)
    house_info = server.fetch_house_info(name,house_type)
    print(area_info)
    if house_info.empty:
        error = "No records"
        return render_template("results.html",error = error, mymap = mymap)
    else:
        house_info['neighbour'] = house_info['neighbour'].apply(eval)
        #valued_house = house_info[:5].copy()
        redmark= [{
            'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
            'lat':  house.lat,
            'lng':  house.lon,
            'infobox': "<p>Price: %s</p>"
                       "<p>Type: %s</p>"
                       "<p>Number of Bedroom: %d"
                       "<p>Price to rent: %.5f</p>"
                       "<p>Neighbours:</p> %s"
                       "<a href = \"https://zoopla.co.uk/for-sale/details/%s\">links</a>"%(house.price,house.property_type,house.num_bed,house.PTR,"".join(["<p><a href = \"https://zoopla.co.uk/for-sale/details/{0}\">{0}</p>".format(item) for item in house.neighbour]),house.listing_id)
        } for index,house in house_info[:5].iterrows()]
        greenmark=[
            {
                'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat':  house.lat,
                'lng':  house.lon,
                'infobox': "<p>Price: %s</p>"
                           "<p>Type: %s</p>"
                           "<p>Number of Bedroom: %d"
                           "<p>Price to rent: %.5f</p>"
                           "<p>Neighbours:</p> %s"
                        
                           "<a href = \"https://zoopla.co.uk/for-sale/details/%s\">links</a>"%(house.price,house.property_type,
                                                                                               house.num_bed,house.PTR,
                                                                                               "".join(["<p><a href = \"https://zoopla.co.uk/for-sale/details/{0}\">{0}</p>".format(item) for item in house.neighbour]),house.listing_id)
            } for index,house in house_info[5:].iterrows()]

        mymap = Map(
        identifier="housemap",
        lat=house_info.iloc[0].lat,
        lng=house_info.iloc[0].lon,
        markers=redmark+greenmark,
        fit_markers_to_bounds = True,
        style = "height:600px;width:800px;margin:0;"
        )
        return render_template('results.html',mymap = mymap,area = area_info)


@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/map-unbounded/')
def map_unbounded():
    """Create map with markers out of bounds."""
    locations = [[37.4419,-122.1419],[37.4300,-122.1400]]    # long list of coordinates
    map = Map(
        identifier="catsmap",
        lat=locations[0][0],
        lng=locations[0][1],
        markers=[(loc[0], loc[1]) for loc in locations]
    )
    return render_template('map.html', map=map)



if __name__ == '__main__':
    app.run(debug=True)
