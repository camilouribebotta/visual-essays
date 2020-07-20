<style>.v-application a, .v-application li, .v-application p { font-size: 1.3rem; }</style>

# Visual Essay Help

- [Introduction](#introduction)
- [Essay markup](#essay-markup)
- [Visual essay directives](#visual-essay-directives)
    - [ve-config](#ve-config)
    - [ve-entity](#ve-entity)
    - [ve-map](#ve-map)
    - [ve-map-layer](#ve-map-layer)
    - [ve-image](#ve-image)
    - [ve-video](#ve-video)
    - [ve-plant-specimen](#ve-plant-specimen)
    - [ve-storiiies](#ve-storiiies)
    - [ve-graph](#ve-graph)
- [Essay hosting](#essay-hosting)
- [Essay authoring](#essay-authoring)
    - [Markdown](#markdown)
    - [Footnotes](#footnotes)
    - [Viewing essay text](#viewing-essay-text)
    - [Editing essays](#editing-essays)
    - [Advanced usage](#advanced-usage)
- [GeoJSON](#geojson)
- [IIIF](#international-image-interoperability-framework-iiif)
- [Frequently asked questions](#frequently-asked-questions)
- [Tips and tricks](#tips-and-tricks)

# Introduction

Visual essays are web pages created from annotated text files.  The text files are formatted using [Markdown](https://www.markdownguide.org/getting-started/),
a lightweight markup language.  The essay text can be annotated with simple tags that associate entities (people, locations, etc), images, maps, and videos with sections of text, typically paragraphs but can also be as small as a single word or as large as the entire essay.  The visual essay tools add interactive visualizations to the rendered web page using information contained in the tags.

Visual essays are especially well suited for story telling that uses maps, images, and videos.  Adding a few simple tags to a text can result in an engaging web page that provides context and depth to the written text

The ability to easily associate text with maps and multimedia is useful but the real power in the visual essay approach used here is the ability to leverage open knowledge graphs such as [Wikidata](https://www.wikidata.org) to obtain data that can be used for automatically generating information dialogs, location coordinates, image URLs, and other information about entities associated with a section of text.  At present the visual essays can use entities from both the Wikidata and JSTOR knowledge graphs.  Support for using other linked open data (LOD) sources may be provided in future versions.

# Essay markup

The essays are written in plain text and are formatted using Markdown.  Markdown has become something of a de-facto standard and is used by a number of popular web sites including Github, Stack Overflow, Reddit, and many others.  Markdown is a superset of HTML and as such any valid HTML is also valid Markdown.  In most typical uses a user will rarely need to augment the Markdown tags with HTML for text formatting as Markdown provides a rich set of easier to use tags for this purpose.  The visual essay processing code takes advantage of the ability to extend the Markdown tags with arbitrary HTML.  The visual essay directives to add maps, images and other visualizations to an essay are accomplished using a simple HTML tag with some custom attributes.  These custom directives and attributes are described in detail in the following sections.

## Markdown

Markdown is a lightweight language that is commonly used to add simple formatting to plain text documents.  Markdown can be used to easily define section headings, lists, and text styling in plain text documents.  Markdown is also platform independent and portable.  It can be written in any number of tools ranging from simple text editors to full-featured integrated development environments.  There are also a number of good web-based editors available for writing Markdown.  More information on creating and modifying essay text files can be found in the [essay authoring](#essay-authoring) section.

## HTML

Any valid HTML can be used in markdown.  HTML tags are often used in a markdown document to accomplish custom formatting that is not directly supported by markdown.  The visual essay directives are also defined using HTML tags and can be specified using any of the HTML `var`, `span` or `param` tags.  While these tags are equivalent in their use as a "wrapper" for the visual essay directives and can be used interchangeably, this document will typically use the `param` tag as it is a self-closing tag and is more concise (and arguably more readable).  The `var` and `span` tags are not self closing and require an end tag (`</var>` or `</span>`) to be valid.  For example, the following forms of the `data-map` visual essay directive are equivalent.  One uses the `var` tag and thus also requires a `</var>` end tag to close.  The other form of the directive uses the `param` tag that does not require an end tag as it can be self closing.

```html
<var ve-map center="42.2813, -83.7483" zoom="6"></var>
<param ve-map center="42.2813, -83.7483" zoom="6">
```

In whichever tag form is used the type of visual essay directive is defined using a null value attribute.  This attribute can be specified anywhere in the tag but is typically the first attribute defined in the HTML wrapper tag.  A null data attribute is simply an attribute with the prefix `data-` and no corresponding value.  For instance, the examples above define a directive of `map` type with directive specific `center` and `zoom` attributes.

## Text Elements

Throughout this document the association of visual essay directives to _text elements_ are described.  A text element can be be a single word or phrase, a single paragraph, all paragraphs in a section, or even all text in the entire essay.  The placement of the visual essay directive in the document defines the scope of text element to which it applies.

It is common to add Markdown headings to documents to define sections of related content, and for longer documents nested heading levels are often used resulting in a document that is hierarchical.

## Active Paragraphs

 An essay includes one or more paragraphs that are often hierarchical based on the nesting level of the markdown headings added.  As a user scrolls through a document a single paragraph is said to be "active".  The active paragraph is a paragraph in the top portion of the browser window and is displayed with a visual treatment that identifies it as the active paragraph.  
 
 Any visualization components associated with the active paragraph are displayed in the visualization panel.  Multiple visualization components can be associated with a single paragraph.  In some cases the components are explicitly associated with the paragraph as the corresponding directive(s) were bound to the paragraph, and in other cases the associations are implied by the scope of the directive placement.  A directive is bound to a single paragraph when there are no blank lines between the paragraph text and the directive.

# Visual essay directives

Visual essay directives currently include:

- [ve-config](#ve-config) - Essay metadata for defining title, banner image, layout, and other custom attributes.
- [ve-entity](#ve-entity) - Associates an entity (person, location, organization, etc) with an element.  An entity is defined using a unique identifer in either the Wikidata or JSTOR knowledge graphs.
- [ve-map](#ve-map) - Defines a map to add to the essay.
- [ve-map-layer](#ve-map) - Defines a map layer to add to current map.
- [ve-image](#ve-image) - Associates an image with an element.
- [ve-video](#ve-video) - Associates a video with an element.
- [ve-plant-specimen](#ve-plant-specimen) - Displays plant type specimens from [Global Plants](https://plants.jstor.org).
- [ve-storiiies](#ve-storiiies) - Displays an annotated IIIF image in an interactive viewer.
- [ve-graph](#ve-graph) - Displays a graph (network diagram).

## ve-config

The `ve-config` directive is used to define essay metadata.  This directive is optional but when used is typically placed at the top of the essay.

### Standard ve-config attributes

- __title__:  The essay title
- __author__:  The essay author name(s)
- __banner__:  A URL to an image to use in the essay header.  This can be an absolute URL to an externally hosted image or a relative URL to an image in the same content repository in which the essay text is hosted, for instance `data-banner="images/some-banner-image.png"`
- __layout__:  One of `hc` (horizontal closed), `ho` (horizontal open), `vtl`, (vertical text left), `vtr` (vertical text right).  By default, essays will be displayed in a horizontal orientation with the visualization pane hidden (__hc__).  The value __ho__ can be used to render the essay horizontally with the viewer pane initially opened.  The vertical orientation options allow the text location to be set to the right or left view pane.

### Custom ve-config attributes

The `ve-config` directive can also be used for site-specific custom attributes.  For instance, the _**Plant humanities**_ project uses the following attributes to define values used in a custom header:

- __num-maps__:  The number of maps used in the essay
- __num-images__:  The number of images used in the essay
- __num-primary-sources__:  The number of primary sources used in the essay
- __num-plant-specimens__:  The number of plan specimens used in the essay

### Example ve-config directives

Below is an example of a `ve-config` directive defining a banner image (using a relative URL) and layout for the essay:

```html
<param ve-config
       title="Charles Dickens"
       banner="images/Viking_Bay_Broadstairs.jpg"
       layout="vtl">
```

This example illustrates the incorporation of custom attributes and an absolute URL for the banner image:

```html
<param ve-config
	   title="Cacao: An indigenous network and global commodity"
	   banner="https://upload.wikimedia.org/wikipedia/commons/3/31/Cacao_Nacional_Fino_de_Aroma.jpg"
       layout="vtl"
       num-plant-specimens="1"
       num-maps="7"
       num-images="20"
       num-primary-sources="14">
```

## ve-entity

The `ve-entity` associates an element (again, anything from a word to the entire document) to an entity (person, place, organization, etc).  Entities are identified through the use of a globally unique identifier.  The current version of the visual essay tools assumes that entity identifiers are URIs that are resolvable in a publicly accessible knowledge graph.  Both Wikidata and the JSTOR knowledge graph are currently supported.  The entity identifier prefix for Wikidata is `http://www.wikidata.org/entity/`.  The JSTOR knowledge graph prefix is `http://kg.jstor.org/entity/`.  For both the Wikidata and JSTOR knowledge graphs a complete identifier consists of the prefix and a knowledge graph specific identifier that starts with the letter `Q` followed by one or more number, commonly referred to as a "Q" identifier or "QID".  The `ve-entity` directive requires the inclusion of an `eid` (entity id) attribute specifying the QID of the entity.  

Wikidata is the default knowledge graph used by the visual essay tool so it is sufficient to just use the QID as the value in the `eid` attribute.  When referring to an entity in the JSTOR knowledge graph the QID requires a namespace qualifier in the form of the string `jstor:` preceding the QID.  Namespacing is necessary as QIDs are not unique between knowledge graphs and the namespace (or prefix) guarantees a unique value.  Consider the country of France.  In the JSTOR knowledge graph the identifier for France is `http://kg.jstor.org/entity/Q10302`.  Simply using "Q10302" in the `eid` attribute in a `ve-entity` directive would incorrectly to the Wikidata entity with the identifier `http://www.wikidata.org/entity/Q10302` which is associated with _Sestriere_, an Italian comune.  To correctly refer to the entity for France in the JSTOR knowledge graph the `eid` attribute value would be `jstor:Q10302`.  While not required (as it is the default), QIDs for entities in the Wikidata knowledge graph may be specified using the `wd:` namespace.

Since `ve-entity` directives are used so frequently they are the default directive type and can be used in an un-typed wrapper.  For instance, the following directives are equivalent:

```html
<param ve-entity eid="Q10302" title="France">
<param eid="Q10302">
```
In the interest of maintainability and future proofing the longer form version is recommended.

### ve-entity attributes

- __title__:  The entity label.  This has special meaning for location entities but is otherwise not used.  The actual entity label used in information boxes and elsewhere comes from the label property in the referenced entity.  Although the title is not used for non-location entities including a title is still helpful as a means to identify the purpose of the `data-entity` directive in the essay source text.  Essays will often include directives for many entities and the title field provides a convenient way for an author to see what is referenced.
When a `title` attribute is included in a `data-entity` attribute for a location the value of this attribute will override any previously defined label from the knowledge graph or external map data, such as that included in existing GeoJSON feature files.
- __eid__:  The identifier for the entity, typically a 'Q' identifier.  If not namespaced this refers to an entity in the Wikidata knowledge graph.
- __aliases__:  When tagging entities in the essay text the text to match is defined by the label and aliases contained in the knowledge graph.  It is not uncommon for an entity to be reference in some other way in the essay text and the `aliases` attribute can enable the visual essay tagger to make the connection.  As an example, say the text is describing a location like Chicago but the text simply includes "the city".  To associate "the city" with Chicago include `aliases="the city"` in the directive.  Multiple aliases may be provided using a pipe (`|`) delimiter to separate multiple terms, for instance `aliases="the city|the windy city"`.

## ve-map

The `ve-map` directive indicates that a map should be added as a visualization component for the associated text element(s).  Maps can be further customized with `ve-map-layer` directives that define layers or overlays to be applied to the map. 

### ve-map attributes

- __basemap__:  By default, [OpenStreetMap (OSM)](https://www.openstreetmap.org/) is used for the base map.  Other base maps are available and can be requested with this attribute.  The available base maps are:
    - [`OpenSteetMap`](https://leaflet-extras.github.io/leaflet-providers/preview/#filter=OpenStreetMap.Mapnik)  
    - [`OpenTopoMap`](https://leaflet-extras.github.io/leaflet-providers/preview/#filter=OpenTopoMap)  
    - [`Stamen_Watercolor`](https://leaflet-extras.github.io/leaflet-providers/preview/#filter=Stamen.Watercolor)  
    - [`Esri_WorldPhysical`](https://leaflet-extras.github.io/leaflet-providers/preview/#filter=Esri.WorldPhysical)
- __center__:  This attribute defines the center point for the map.  The center point can be defined as a latitude and longitude coordinates or using a QID for an entity that is associated with geo-coordinates.  For instance, the following are equivalent.  They both use the city of Ann Arbor, Michigan as the map center point.  In the first version the latitude and longitude coordinates are specified and in the second the Wikidata QID for Ann Arbor is provided. 
    ```html
    <param ve-map center="42.2813, -83.7483">
    <param ve-map center="Q485172">
    ```
- __zoom__:  This attribute defines the starting map zoom level.  This number can be expressed in 0.1 increments, such as `zoom="3.4"`
- __hide-labels__:  By default, the labels for any locations plotted on a map (both markers and GeoJSON features) will be displayed.  This attribute can be used to inhibit this default behavior.  Note that a user can still open the label by hovering over and/or clicking on the label or GeoJSON defined region.
- __prefer-geojson__:  Location entities are automatically added to a map components that is visible for an active text element.  By default the location is represented as a marker pinned at a discrete geo-coordinate.  However, many location entities in the Wikidata knowledge graph can also be associated with GeoJSON shape files that represent the location as region using a polygon shape.  If the visualization of a location on a map using the GeoJSON defined region is preferred over a simple marker/pin this attribute is used to express that preference.
- __active__: Defines whether the layer is initially displayed on the map.  The default value is `false`.  If this attribute is not set to `true` the user will need to activate the layer from the map control located on the map.  Since `active` is a boolean property (supporting just `true` and `false` values) a shorthand version of the attribute (the attribute name without a value) can be used.

## ve-map-layer

The map shown for an active element can be augmented with one or more layers.  Two types of layers are currently supported.

### ve-map-layer attributes

- __type__:  `mapwarper` or `geojson`.  Defines the specific layer type.
- __title__:  The title attribute serves a couple purposes for map layers.  First, it is used a the label on map controls that enable/disable MapWarper layers and control the layer opacity.  When the layer type is geojson the title, when provided, will override any predefined labels in the GeoJSON file when displaying location labels on a map.  Note that when multiple features (and labels) are defined in a single GeoJSON file the title value will be used once for the aggregate features.
- __url__:  URL to a GeoJSON file.  This attribute is only used when the layer type is `geojson`.  This can be a relative URL (for example, `geojson/portugal.json`) if the geojson file is located in the same Github repository as the essay.  If not, the URL must be absolute.
- __mapwarper-id__:  Defines the overlay ID when the layer type is `mapwarper`
- __active__:  One of `true` (default if attribute is not provided) or `false`.  This attribute defines whether the layer is activated on the map when initially displayed.  In either case the user can toggle individual layers on/off using controls on the map.  

## ve-image

Associates an image with a text element.  The directive provides the ability to define 3 versions of the image URL, the normal URL (`url`), an IIIF URL (`iiif-url`) or an IIIF manifest URL (`manifest`).  The `iiif-url` and/or `manifest` attributes should be used for images with existing IIIF service links or manifests.  If not, use the `url` attribute and IIIF manifests will be automatically created by the visual essay service.

### ve-image attributes

- __title__:  The title attribute is used for the image caption.  Markdown text formatting is supported in the title allowing for italicized and bold text.
- __url__:  The URL to the source version of the image.
- __iiif-url__:  The URL to a IIIF service endpoint for the image, if one exists.
- __manifest__:  The URL to the IIIF presentation manifest for the image, if one exists.
- __fit__:  This attribute defines how an image will be scaled or cropped in the image viewer window.  Possible values for this attribute are
    -  `contain`:  The replaced content is scaled to maintain its aspect ratio while fitting within the element's content box
    -  `cover`:  (default) The replaced content is sized to maintain its aspect ratio while filling the element's entire content box. The object will be clipped to fit
 - __region__: The region attribute is used to show a cropped region of the image in the image viewer.  The entire image is loaded and can be seen by zooming and panning but the initial display will only include the specified region.  The value for a region is a comma separated sequence of 4 integers representing the origin, width and height.  The origin includes both the x and y coordinates relative to the top left of the image.  The region may be expressed as absolute pixel values or as percentages of the relative values.  More information on IIIF regions can be found at [https://iiif.io/api/image/2.0/#region](https://iiif.io/api/image/2.0/#region)
 - __attribution__:  An attribution statement to associate with the image.

### ve-image location-specific attributes

## ve-video

Associates a video with a text element.  Youtube videos are supported in the current version of the visual essay tool.  Other streaming services may be added in future versions.

### ve-video attributes

- __vid__:  The Youtube video ID.
- __title__:  The title attribute is used for the image caption.  Markdown text formatting is supported in the title allowing for italicized and bold text.
- __start__:  The starting timestamp (in seconds).  If not provided the video will start playing from the beginning.

## ve-plant-specimen

Displays a high resolution image for a plant type specimen retrieved from the [Global Plants](https://https://plants.jstor.org) database.

### ve-plant-specimen attributes

- __eid__:  The Wikidata QID for a species-level taxon name.  For example, [Q12844029](https://www.wikidata.org/entity/Q624242)
- __max__: The maximum number of specimens to return
- __reverse__:  Reverses the date sorting within a type group (holotype, isotype, etc).  By default, multiple specimens within the same type group are sorted by date in ascending order (oldest is first).  Setting this attribute to `true` will display the most recent first.
 
## ve-storiiies

Displays an IIIF annotated image.

### ve-storiiies attributes

- __id__:  The 5-digit identifier assigned by the Storiiies editor

## ve-graph

Associates a graph (or network diagram) with a text element.  Graphs are defined using delimited (comma or tab) text files that include the information for plotting the nodes and edges in the graph.  The graph specification is loaded from a URL provided in the `ve-graph` tag.

### ve-graph attributes

- __url__:  The URL to a comma delimited text file containing the graph specification.
- __title__:  The title to use for the graph in the viewer.

### Example ve-graph directives

- [medici.tsv](https://github.com/JSTOR-Labs/plant-humanities/blob/master/graphs/medici.tsv) - A tab separated text file defining a graph using a mix of ad-hoc nodes and nodes defined using Wikidata entities

# Essay hosting

# Essay authoring

## Markdown

## Footnotes

Footnotes and endnotes are not part of the core Markdown syntax.  However, the visual essay Markdown processor supports a common extension that enables footnote linking in the essay text.  The syntax is `[^ref]`, where "ref" can be any string.  A pair of these footnote tags are used in the markdown text.  The first is located with the essay text to be associated with the footnote.  The second is included in an aggregated footnotes list, typically located at the end of the essay following a section heading of `References` or something equivalent. 

## Viewing essay text

## Editing essays

### Default editor

### StackEdit editor

## Advanced usage

### Adding custom styling

# GeoJSON

## Sources for existing GeoJSON files

## Creating and hosting a custom GeoJSON file

# International Image Interoperability Framework (IIIF)

# Frequently asked questions

1.  How do I ...  
     **Answer**:  hmmm, good question  
2.  What is ...  
    **Answer**:  well, that depends. 

# Tips and tricks

1. 
<!--stackedit_data:
eyJoaXN0b3J5IjpbLTIxMDA4NTMzMDcsMjEzMjQyNjc1LC01ND
cyODY4NDQsMjA4NjY1NzUwOCwtNzM3NTkyMDQyLDExMTI1Nzc0
NjMsNjQwODU3MjEsMTY5NDE5MjA1NF19
-->