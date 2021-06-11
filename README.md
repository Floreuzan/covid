# Covid-19 Visualization Tool

This visualization tool built was built using version 6 of D3.js. We used Python to download,
wrangle, and merge our two datasets. Maps were created using [Leaflet](https://leafletjs.com/) to plot country
polygons contained in GeoJSON from [Datahub](https://datahub.io/core/geo-countries) (and originally provided by [Natural
Earth](https://www.naturalearthdata.com/)), and Mapbox was used to serve the map tiles. Combined, Leaflet and [Mapbox](https://www.mapbox.com/)
allows our visualization’s users to pan and zoom. Note that we constrained the panning
within a certain window to prevent users from panning out of the area on which the
polygons were plotted.

# Data

*  covid_data.csv is the Covid-19 data itself, a CSV created from the [Oxford](https://www.bsg.ox.ac.uk/research/research-projects/covid-19-government-response-tracker) and [Our World in Data](https://github.com/owid/covid-19-data/tree/master/public/data) datasets with the [data_downloader.py](https://github.com/Floreuzan/covid/blob/main/data/data_downloader.py).
*  country_polygons.json is the GeoJSON file containing the country polygons mentioned earlier. 
*  data_dictionary.csv is a data dictionary which tells our visualization how to present each feature. It
contains a key column identifying the variable name as written in the CSV data file; the
type of data (string, date, or numeric); a user-friendly name (e.g., “New cases” instead
of new_cases); a sort order for dropdown menus; a feature category (“cases & deaths”,
“tests”, “vaccinations”, etc.); and a column indicating whether larger values are “good”,
“bad”, or “neutral” (e.g., more cases is bad, more vaccinations is good, and population is
neutral), which is used to drive the color scheme on the map. In addition, there is a
column used for ordinal variables, identifying a numeric form of a given ordinal variable
which, when combined with the ordinal column, allows us to easily plot the data on a
continuous axis while represent the ordinal value in a user-friendly way (e.g.,
“1-National”).

# Architecture

The general architecture consists of one object for each visualization, each
containing references to the variables and functions associated with its visualization.
This prevented us from polluting the global namespace and potentially re-using another
visualization’s variable by mistake. This also makes the overall site very modular,
making it easy to remove any of the three visualizations, or to add one visualization to a
different site. Each visualization is drawn and updated by its own “make” and a “redraw”
function. For example, the second visualization has functions makeViz2 and redrawViz2.
The make function is called once, at page load, and creates the objects (axes, scales,
etc.) underlying the visualization. Meanwhile, the redraw function actually plots the data
and is called anytime the data in the visualization changes, such as by moving the date
slider or choosing a new attribute. 

* The first visualization, which is made up of a map, a
bar chart, and a line chart, is created and updated with three corresponding make and
redraw functions, one for each sub-chart.
  * For the map, the Covid data were joined to the GeoJSON data using [ISO alpha-3
codes](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) to avoid issues with alternative spellings of country names (e.g., “Bahamas” vs.
“The Bahamas”, “Côte d'Ivoire” vs. “Ivory Coast”). Countries’ polygons were given a
class name of “shape-ISO” (e.g., “shape-USA”), which allowed easier selection. A
transparent rectangle was overlaid on top of the entire map SVG to allow users to click
anywhere to remove countries from their selection. The redrawViz1a function is where the
data were bound to each polygon, using the polygon’s class to determine its country(“USA” in “shape-USA”). The click event was coded to allow users to select multiple
countries by holding the Ctrl key before clicking. Adding or removing to/from the
selection triggers a redraw of the bar chart (viz1b) and the line chart (viz1c).
  * The bar chart underneath the map was constructed in the usual way for D3 bar
charts. However, one key feature that was added was the ability to hover over the bar at
any length along the bar. This was accomplished by adding a series of “invisible” bars
that span the length of the bar chart. In addition, a series of text labels containing the
words “No data” were added to the visualization to appear when a given country had no
data for an attribute on a given date. This is to distinguish a value of zero from not
having any data.
  * The line chart below the map and to the right of the bar chart was also
constructed in the usual way for D3 line charts. One tricky aspect was handling how to
put an arbitrary and dynamic number of lines on the plot at any one time. This required
using a nested/grouped structure to make a “map” with country as the “key” and the
values for the selected attribute as the “value”. The trickiest part of this visualization was
the hover effect, which highlights the line closest to the cursor. The mousemove event
takes the (X,Y) position of the cursor and inverts it using the X and Y-scales to get the
corresponding date and attribute values, respectively. It then computes the nearest date
in the dataset using the bisectCenter function and filters the data to rows from the
selected countries for that nearest date. Then we compute the vertical distance between
the inverted Y-position and the attribute value for each country at that date, and the
country with the closest value is identified.


* The second visualization (the summary table and line chart) is created and
updated with the makeViz2 and redrawViz2 functions. The line chart is constructed
identically to the line chart in the first visualization, although without a hover effect or
tooltip because the focus of this visualization is on the table. The table was constructed
by building the HTML for the table a row and a cell at a time. CSS was used to make
the table take up 80% of the screen, up to a max of 800 pixels, and to make the first
column header “sticky” so that when a user scrolls across inside the table, the attribute
names scroll too.

* The final visualization on the site uses the typical approach for making scatter
plots with D3, with the exception of special handling for the ordinal scales. Because this
visualization is meant to provide information about the relationship between two
attributes, we made the choice to let the x- and y-scales vary with time, rather than fix
them at the maximum value achieved over the dataset. This is so that, at any point
along the time scale, a user could look for correlation, outliers, etc. If we fixed the
scales’ domains at the extremes of the dataset, all countries’ points would have been
pushed close to the origin and it would have been difficult to accomplish this task.

