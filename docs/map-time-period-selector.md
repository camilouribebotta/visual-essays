<param ve-config
       title="Map time period selector example"
       banner="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/North_of_tehran.jpg/1280px-North_of_tehran.jpg"
       layout="vtl"
       author="Ron">


## Map time period selector

<param ve-map basemap="Esri_WorldPhysical" center="0,50">

This essay demonstrates the use of the `time-selector` attribute with the `ve-map` essay tag.  The essay uses a [GeoJSON file](https://github.com/JSTOR-Labs/visual-essays/blob/master/docs/geojson/cities.json) produced from a [Wikidata query of the top 100 cities world-wide based on population](https://w.wiki/Y9B).  The inception year is returned in the query and is used for the date filtering provided by the time selector in the map visualization.

Each geographic feature contained in a GeoJSON file to be used for time period based date filtering must include a date property.  The property label is assumed to be `date` unless explicitly set in the `ve-map-layer` tag using the `date-field` attribute.  In this example the GeoJSON date property is named _inception_ so this attribute is used.  The value of the date field is an [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) compatible date string.  Common formats are year only (_YYYY_), year and month (_YYYY-MM_), and day (_YYYY-MM-DD_).  Dates before the common era must include the _BCE_ suffix.

### Cities founded before the common era

<param ve-map time-selector="7300 BCE:0" basemap="Esri_WorldPhysical" center="25,50" zoom="3.5" hide-labels>
<param ve-map-layer geojson active url="geojson/cities.json" date-field="inception" title="Cities">

In this visualization the cities founded before the common era (BCE) are shown on the map as simple markers.  The automatic display of marker labels is inhibited using the `hide-labels` attribute on the `ve-map` tag.  The display of all labels can be enabled using the map control located at the top right of the map.  The label for individual markers wil display when the mouse hovers over the marker.  Clicking on a marker will show an infobox popup with an image and short description of the city.

### Cities founded in the common era

<param ve-map time-selector="0:2020" hide-labels>
<param ve-map-layer geojson active url="geojson/cities.json" date-field="inception" title="Cities">

In this visualization the cities founded during the common era (CE) are shown.  The time period used to select the city markers shown on the map can be adjusted using the time selection control located below the map. 
