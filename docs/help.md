## Visual Essay Help

- [Introduction](#introduction)
- [Essay Markup](#essay-markup)
- [Essay Authoring](#essay-authoring)
- [Resources](#resources)
  - [Linked Open Data](#linked-open-data)
    - [Wikidata Knowledge Graoh](#wikidata-knowledge-graph)
    - [JSTOR Knowledge Graph](#jstor-knowledge-graph)
    - [Supplementing Knowledge Graph Data](#supplementing-knowledge-graph-data)
  - [MapWarper](#mapwarper)
  - [GeoJSON](#geojson)
- [Creating and Hosting Custom Sites](#creating-and-hosting-custom-sites)
  - [Custom Components](#custom-components)
  - [Custom Site Configuration](#custom-site-configuration)

## Introduction

Visual essays are web pages created from annotated text files.  The text files can be formatted using [Markdown](https://www.markdownguide.org/getting-started/),
a lightweight markup language.  The essay text can be annotated with simple tags that associate entities (people, locations, etc), images, maps, and videos with 
sections of text that can be a small as a single word or include the entire essay.  The visual essay tools add interactive visualizations to the rendered web page 
using information contained in the tags.

Visual essays are especially well suited for story telling that uses maps, images, and videos.  Adding a few simple tags to a text can result in an engaging web page 
that provides context and depth to the written text

The ability to easily associate text with maps and multimedia is useful but the real power in the visual essay approach used here is the ability to leverage open knowledge
graphs such as Wikidata to obtain data that can be used for automatically generating information dialogs, location coordinates, image URLs, and other information about entities
associated with a section of text.  At present the visual essays can use entities from both the Wikidata and JSTOR knowledge graphs.  Support for using other linked
open data (LOD) sources may be provided in future versions.

## Essay markup

The essays are written in plain text and can be formatted using Markdown, a lightweight text markup language.  Markdown has become something of a de-facto standard and is used by a number of popular web sites including Github, Stack Overflow, Reddit, and many others.  Markdown is a superset of HTML and as such any valid HTML is also valid Markdown.  In most typical uses a user will rarely need to augment the Markdown tags with HTML.  The visual essay processing code takes advantage of the ability to use HTML in Markdown.  Directives to add maps, images and other visualizations to an essay are accomplished using a simple HTML tag with custom attributes. 

### Markdown

Markdown is a lightweight language used to add formatting to plain text documents.  It can be used to easily define section headings, lists, and text styling in plain text with minimal syntax.  Markdown is also platform independent and portable.  It can be written in any number of tools ranging from simple text editors to full-featured integrated development environments.  There are also a number of good web-based editors available for writing Markdown.

### HTML

Any valid HTML can be used in markdown.  HTML tags are often used in a markdown document to accomplish custom formatting that is not directly 
supported by markdown.  The visual essay directives are defined using HTML tags and can be specified using any of the HTML `var`, `span` or `param` tags.  While these are equivalent this document will typically use the `param` tag as it is a self-closing tag and more concise and arguably more readable.  The `var` and `span` tags are not self closing and require a end tag (`</var>` or `</span>` to be valid.  For example, the following forms of the `data-map` visual essay directive are equivalent.  One uses the `var` tag and thus requires a `</var>` end tag to close.  The other form uses the `param` tag that does not require an end tag as it can be self closing.

```html
<var data-map data-center="42.2813, -83.7483" data-zoom="6"></var>
```

```html
<param data-map data-center="42.2813, -83.7483" data-zoom="6">
```

In whichever tag form is used the type of visual essay directive is defined using a null value attribute.  This attribute can be specified anywhere in the tag but is typically the first attribute.  A null data attribute is an attribute with the prefix `data-` without a corresponding value.  For instance, the examples above defines a `map` tag type with the map `center` and `zoom` attributes.

## Visual essay directives

Visual essay directives currently include:

- [data-essay](#data-essay) - Essay metadata for defining title, banner image, layout, and other custom attributes
- [data-entity](#data-entity) - Associates an entity with an element
- [data-map](#data-map) - Defines a map to add to the essay
- [data-map-layer](#data-map) - Defines a map layer to add to current map
- [data-image](#data-image) - Associates an image with an element
- [data-video](#data-video) - Associates a vide with an element
- [data-primary](#data-primary) - Identifies the content type to initially show when multiple are available for an element

### data-essay directive

The `data-essay` directive is used to define essay metadata.

#### Standard data-essay attributes

- __title__:  The essay title
- __data-author__:  The essay author name(s)
- __data-banner__:  A URL to a image to use in the essay header.  This can be an absolute URL to an externally hosted image or a relative URL to an image in the sane content 
repository in which the essay text is hosted, for instance `data-banner="images/some-banner-image.png"`
- __data-layout__:  One of `hc` (horizontal closed), `ho` (horizontal open), `vtl`, (vertical text left), `vtr` (vertical text right).  By default, essays will be displayed in a horizontal orientation with the visulaization pane hidden (__hc__).  The value __ho__ can be used to render the essay horizontally with the viewer pane initially opened.  The vertical orientation options allow the text location to be set to the right or left view pane.

#### Custom data-essay attributes

The `data-essay` directive can also be used for site-specific custom attributes.  For instance, the __Plant humanities__ project uses the following attributes to define values used in
a custom header:

- __data-num-maps__:  The number of maps used in the essay
- __data-num-images__:  The number of images used in the essay
- __data-num-primary-sources__:  The number of primary sources used in the essay
- __data-num-plant-specimens__:  The number of plan specimens used in the essay

#### Example data-essay directives

Below is an example of a `data-essay` directive using a local banner image and vtl layout:

```html
<param data-essay
       data-title="Charles Dickens"
       data-banner="images/Viking_Bay_Broadstairs.jpg"
       data-layout="vtl">
```

### data-entity

### data-map

- __data-basemap__: `mapwarper` or `geojson`

### data-map-layer

- __data-type__: `mapwarper` or `geojson`

### data-image

### data-video

### data-primary


## Entities

The data used by the widgets in the visualization pane is typically retrieved from Wikidata (the knowledge base behind Wikipedia).  Wikidata is a Linked Open Data (LOD) knowledge base containing nearly 80 million entities (as of Feb 2020) and growing at the rate of nearly 1 million per month.  Each entity (person, location, organization, etc) in Wikidata is assigned a unique identifier commonly called a ‘Q’ ID as each of the identifiers starts with the ‘Q’ character followed by a number.  For instance, Washington DC is assigned the identifier Q61.

Connecting text to a Wikidata entity is accomplished by adding an HTML `var` tag to the text with an `id` attribute the consists of the Wikidata QID associated with the entity.  For instance, to associate Washington DC with text in the document the tag `<var id=“Q62”></var>` is added to the text.  The `var` tag is not displayed in the rendered text but provides information enabling the software to associate mentions of Washington DC in the text to the Wikidata entity with the identifier Q61.  Wikidata entities provide rich information enabling a range of visualizations and tools.  For entities that are locations (such as our Washington DC example) the Wikidata entity will often include geographic coordinates enabling the location to be visualized on a map.

When an entity is declared in a text using a `var` tag the software will use information in the Wikidata entity to find references in the text.  Wikidata entities include a label and optionally one or more aliases that are used to find the text references.  Additional aliases may be entered in the `var` tag to supplement those available in the Wikidata entity.  For example, if a document included the text “capital of the United States” the information available in the label and aliases properties in the Wikidata entity would be insufficient to connect that phrase to the entity.  In this case additional aliases can be provided with a `data-aliases` attribute in the `var` tag.  Multiple aliases are separated using the pipe (`|`) character.  For instance, `<var id=“Q61” data-aliases=“capital of the United States|the district”></var>`.

Other attributes available for entity declarations include:

- `data-scope` which can used to restrict the document regions considered when associating text with an entity.  For entity associations a `var` declaration is by default of **global** scope meaning that any mention in any part of the document is associated with the entity.  This behavior can be overridden by declaring an entities scope as **local** which would restrict associations to those mentions in the local region in which the `var` tag was defined.  The locality can be a paragraph or higher-level section depending on where the tag was entered.  To restrict locality to a single paragraph the `var` tag must be entered in the associated paragraph text block with no intervening blank lines and include the `data-scope=“local”` attribute.

## Maps

Maps are added to the visualization pane using a `var` tag with a `data-map` attribute defined.  In declaring a map a `data-center` attribute must be provided indicating the map center point.  Optionally, a `data-zoom` attribute can be provided defining the initial zoom level for the interactive map.

- `data-center` attribute values may be expressed as longitude/latitude coordinates (comma-separated float values) or using a QID for an entity than contains a position coordinate.
- `data-zoom` attribute values are expressed as an integer or a floating point number (with tenths precision).  The higher the value the more detailed the map.

## Map layers

Maps may include optional layers.  MapWarper tiles and GeoJSON feature layers are currently supported.

### MapWarper tile layers

MapWarper is an open source tool and online service that generates map tiles from image files.  A common use case for this is to overlay an historical map on base map tiles.  MapWarper provides tools for fitting an image to base map geo-coordinates by relating map feature points.

### GeoJSON feature layers

### data-essay

### Editing essays
Since both the essay and annotations are plain text the essays can be created and maintained in any number of ways.  The only requirement is that the essay file be available on the internet.  One possible approach is to host the essay files in a [Github](https://github.com) repository.  Git is an open-source version control system that was started by Linus Torvalds—the same person who created the Linux operating system.  Github is an online service providing hosting of Git code repositories.  Since its inception Github has become wildly popular and is often used for much more than just version control on software projects.  Github offers free accounts and while its user interface may initially be a little intimidating to non-technical users it is actually a pretty simple to use service and a convenient way to manage text files.  When coupled with Github enabled tools much (or all) of the actual interaction with the Github service is handled through more user-friendly and familiar interfaces.  One such tool is [StackEdit](https://stackedit.io) which provides a browser-based Markdown editor with options for publishing files directly to Github.  [This page](/stackedit-setup) provides step-by-step instructions for setting up a StackEdit environment for publishing files to Github.

The `visual essays` service creates an interactive web page merging text content with external data, including:

- information from knowledge graphs such as [Wikidata](https://www.wikidata.org),
- maps with optional tile layers and geojson features

The text content is written in plain text with [markdown]([https://daringfireball.net/projects/markdown/syntax](https://daringfireball.net/projects/markdown/syntax)) or [wikitext]([https://meta.wikimedia.org/wiki/Help:Wikitext_examples](https://meta.wikimedia.org/wiki/Help:Wikitext_examples)) markup for simple formatting.  External data is linked to the text through the addition of HTML `var` tags that provide instructions and hints adding contextualized interactive features in the rendered page.

Initially, the rendered page only displays the formatted text content.  Interactive features are enabled when page sections are selected.  Selecting a page section (generally a paragraph) be clicking on the text will open a visualization pane in the lower section of the page.

When the visualization pane is enabled supplemental information associated with the corresponding text in the top portion of the page is available for viewing and in many cases interaction.  For example, if a location is mentioned in the text a map could be displayed showing the location of the place mentioned on an interactive map.  As another example, if a person is mentioned in the text more information (including images) can be displayed providing context and background on the person mentioned.

### Entities

The data used by the widgets in the visualization pane is typically retrieved from Wikidata (the knowledge base behind Wikipedia).  Wikidata is a Linked Open Data (LOD) knowledge base containing nearly 80 million entities (as of Feb 2020) and growing at the rate of nearly 1 million per month.  Each entity (person, location, organization, etc) in Wikidata is assigned a unique identifier commonly called a ‘Q’ ID as each of the identifiers starts with the ‘Q’ character followed by a number.  For instance, Washington DC is assigned the identifier Q61.

Connecting text to a Wikidata entity is accomplished by adding an HTML `var` tag to the text with an `id` attribute the consists of the Wikidata QID associated with the entity.  For instance, to associate Washington DC with text in the document the tag `<var id=“Q62”></var>` is added to the text.  The `var` tag is not displayed in the rendered text but provides information enabling the software to associate mentions of Washington DC in the text to the Wikidata entity with the identifier Q61.  Wikidata entities provide rich information enabling a range of visualizations and tools.  For entities that are locations (such as our Washington DC example) the Wikidata entity will often include geographic coordinates enabling the location to be visualized on a map.

When an entity is declared in a text using a `var` tag the software will use information in the Wikidata entity to find references in the text.  Wikidata entities include a label and optionally one or more aliases that are used to find the text references.  Additional aliases may be entered in the `var` tag to supplement those available in the Wikidata entity.  For example, if a document included the text “capital of the United States” the information available in the label and aliases properties in the Wikidata entity would be insufficient to connect that phrase to the entity.  In this case additional aliases can be provided with a `data-aliases` attribute in the `var` tag.  Multiple aliases are separated using the pipe (`|`) character.  For instance, `<var id=“Q61” data-aliases=“capital of the United States|the district”></var>`.

Other attributes available for entity declarations include:

- `data-scope` which can used to restrict the document regions considered when associating text with an entity.  For entity associations a `var` declaration is by default of **global** scope meaning that any mention in any part of the document is associated with the entity.  This behavior can be overridden by declaring an entities scope as **local** which would restrict associations to those mentions in the local region in which the `var` tag was defined.  The locality can be a paragraph or higher-level section depending on where the tag was entered.  To restrict locality to a single paragraph the `var` tag must be entered in the associated paragraph text block with no intervening blank lines and include the `data-scope=“local”` attribute.

### Maps

Maps are added to the visualization pane using a `var` tag with a `data-map` attribute defined.  In declaring a map a `data-center` attribute must be provided indicating the map center point.  Optionally, a `data-zoom` attribute can be provided defining the initial zoom level for the interactive map.

- `data-center` attribute values may be expressed as longitude/latitude coordinates (comma-separated float values) or using a QID for an entity than contains a position coordinate.
- `data-zoom` attribute values are expressed as an integer or a floating point number (with tenths precision).  The higher the value the more detailed the map.

### Map layers

Maps may include optional layers.  MapWarper tiles and GeoJSON feature layers are currently supported.

#### MapWarper tile layers

MapWarper is an open source tool and online service that generates map tiles from image files.  A common use case for this is overlaying an historical map on base map tiles.  MapWarper provides tools for fitting an image to base map geo-coordinates by relating map feature points.

## Essay Authoring

## Custom Sites

### Custom Components

### Custom Site Configuration
<!--stackedit_data:
eyJoaXN0b3J5IjpbMTM4OTYzNjY5NCwtMjEyNTYzNjI5MSwxMz
g5NjM2Njk0XX0=
-->