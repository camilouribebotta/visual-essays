## About Visual Essays

[JSTOR Labs](https://labs.jstor.org) `visual essays` service creates an interactive web page merging text content with external data, including:

## About essay markup

### Markdown

### HTML

Any valid HTML can be used in markdown.  HTML tags are often used in a markdown document to accomplish custom formatting that is not directly 
supported by markdown.

To define visualizations to add to an essay the `var` HTML tag is used with a number of custom attributes.  The __var__ tags that are used to define visual essay behavior generally do not include text and thus are not visible when the document is rendered.  The __var__ tags evaluated by the visual essay processor will include a null data attribute defining the type.  A null data attribute is an attribute with the prefix `data-` without a value.  For instance, the example below defines a `map` tag type with the map specific `center` and `zoom` attributes.

```html
<var data-map data-center="42.2813, -83.7483" data-zoom="6"></var>
```

```html
<param data-map data-center="42.2813, -83.7483" data-zoom="6"/>
```

## Visual Essay HTML tags

- [data-essay](#data-essay) - Essay metadata for defining title, banner image, layout, and other custom attributes
- [data-entity](#data-entity) - Associates an entity with the essay or element
- [data-map](#data-map) - Associates a map with a section or paragraph
- [data-image](#data-image) - Associates an image with a section or paragraph

information from knowledge graphs such as [Wikidata](https://www.wikidata.org),
maps with optional tile layers and geojson features

The text content is written in plain text with [markdown]([https://daringfireball.net/projects/markdown/syntax](https://daringfireball.net/projects/markdown/syntax)) or [wikitext]([https://meta.wikimedia.org/wiki/Help:Wikitext_examples](https://meta.wikimedia.org/wiki/Help:Wikitext_examples)) markup for simple formatting.  External data is linked to the text through the addition of HTML `var` tags that provide instructions and hints adding contextualized interactive features in the rendered page.

Initially, the rendered page only displays the formatted text content.  Interactive features are enabled when page sections are selected.  Selecting a page section (generally a paragraph) be clicking on the text will open a visualization pane in the lower section of the page.

When the visualization pane is enabled supplemental information associated with the corresponding text in the top portion of the page is available for viewing and in many cases interaction.  For example, if a location is mentioned in the text a map could be displayed showing the location of the place mentioned on an interactive map.  As another example, if a person is mentioned in the text more information (including images) can be displayed providing context and background on the person mentioned.

```html
<var data-essay
     data-title="Essay title"
     data-layout="vtl"></var>
<var data-map data-center="Q1234"></var>
```

## Entities

The data used by the widgets in the visualization pane is typically retrieved from Wikidata (the knowledge base behind WIkipedia).  Wikidata is a Linked Open Data (LOD) knowledge base containing nearly 80 million entities (as of Feb 2020) and growing at the rate of nearly 1 million per month.  Each entity (person, location, organization, etc) in Wikidata is assigned a unique identifier commonly called a ‘Q’ ID as each of the identifiers starts with the ‘Q’ character followed by a number.  For instance, Washington DC is assigned the identifier Q61.

Connecting text to a Wikidata entity is accomplished by adding an HTML `var` tag to the text with an `id` attribute the consists of the Wikidata QID associated with the entity.  For instance, to associate Washington DC with text in the document the tag `<var id=“Q62”></var>` is added to the text.  The `var` tag is not displayed in the rendered text but provides information enabling the software to associate mentions of Washington DC in the text to the Wikidata entity with the identifier Q61.  Wikidata entities provide rich information enabling a range of visualizations and tools.  For entities that are locations (such as our Washington DC example) the Wikidata entity will often include geographic coordinates enabling the location to be visualized on a map.

When an entity is declared in a text using a `var` tag the software will use information in the Wikidata entity to find references in the text.  Wikidata entities include a label and optionally one or more aliases that are used to find the text references.  Additional aliases may be entered in the `var` tag to supplement those available in the Wikidata entity.  For example, if a document included the text “capital of the United States” the information available in the label and aliases properties in the Wikidata entity would be insufficient to connect that phrase to the entity.  In this case additional aliases can be provided with a `data-aliases` attribute in the `var` tag.  Multiple aliases are separated using the pipe (`|`) character.  For instance, `<var id=“Q61” data-aliases=“capital of the United States|the district”></var>`.

Other attributes available for entity declarations include:
* `data-scope` which can used to restrict the document regions considered when associating text with an entity.  For entity associations a `var` declaration is by default of **global** scope meaning that any mention in any part of the document is associated with the entity.  This behavior can be overridden by declaring an entities scope as **local** which would restrict associations to those mentions in the local region in which the `var` tag was defined.  The locality can be a paragraph or higher-level section depending on where the tag was entered.  To restrict locality to a single paragraph the `var` tag must be entered in the associated paragraph text block with no intervening blank lines and include the `data-scope=“local”` attribute.

## Maps

Maps are added to the visualization pane using a `var` tag with a `data-map` attribute defined.  In declaring a map a `data-center` attribute must be provided indicating the map center point.  Optionally, a `data-zoom` attribute can be provided defining the initial zoom level for the interactive map.
* `data-center` attribute values may be expressed as longitude/latitude coordinates (comma-separated float values) or using a QID for an entity than contains a position coordinate.
* `data-zoom` attribute values are expressed as an integer or a floating point number (with tenths precision).  The higher the value the more detailed the map.

## Map layers

Maps may include optional layers.  Mapwarper tiles and GeoJSON feature layers are currently supported.

### Mapwarper tile layers

Mapwarper is an open source tool and online service that generates map tiles from image files.  A common use case for this is to overlay an historical map on base map tiles.  Mapwarper provides tools for fitting an image to base map geocoordinates by relating map feature points.

### GeoJSON feature layers

### data-essay
