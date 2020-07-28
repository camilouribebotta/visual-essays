<param ve-config
       title="Cities"
       banner="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/North_of_tehran.jpg/1280px-North_of_tehran.jpg"
       layout="vtl"
       author="JSTOR Labs team">


## Introduction

This essay demonstrates the use of the `time-selector` attribute with the `ve-map` essay tag.  The essay uses a GeoJSON file produced from a Wikidata query of the top 100 cities world-wide based on population.  The inception year is returned in the query and is used for the date filtering in the visualization.
<param ve-map basemap="Esri_WorldPhysical" center="0,50">

### Cities founded before the common era

In this visualization the cities founded before the common era (BCE) are shown on the map as simple markers.  The automatic display of marker labels is inhibited using the `hide-labels` attribute on the `ve-map` tag.  The display of all labels can be enabled using the map control located at the top right of the map.  The label for individual markers wil display when the mouse hovers over the marker.  Clicking on a marker will show an infobox popup with an image and short description of the city.
<param ve-map time-selector="7300 BCE:0" basemap="Esri_WorldPhysical" center="25,50" zoom="3.5" hide-labels>
<param ve-map-layer geojson active url="geojson/cities.json" date-field="inception" title="Cities">

### Cities founded in the common era

In this visualization the cities founded during the common era (CE) are shown.  The time period used to select the city markers shown on the map can be adjusted using the time selection control located below the map. 
<param ve-map time-selector="0:2020" hide-labels>
<param ve-map-layer geojson active url="geojson/cities.json" date-field="inception" title="Cities">