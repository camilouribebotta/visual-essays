<param ve-config
       title="Plant specimens example"
       banner="images/plant-specimen.jpg"
       layout="vtl"
       author="Ron">


## Plant specimens

This essay demonstrates the use of the `ve-plant-specimen` essay tag.  This tag creates a plant specimen viewer will display one or more high resolution specimen images from the [Global Plants](https://plants.jstor.org/) database.  The specimen images are selected using either a Wikidata QID for a species-level taxon entity or a Global Plants ID for a specific specimen.  When using a Wikidata entity ID for a species multiple specimens are often available in the Global Plants database.  In this case multiple images are returned ordered by type (holotype->isotype->lectotype->other) and collection date (ascending by date), by default.  The result is that the first specimen in a list of multiple specimens will typically be the holotype with the earliest collection date.  The date ordering can be reversed using the `reverse` tag attribute.  By default the top 5 specimens are returned.  This can be overridden using the `max` attribute.

### Plant specimens using Wikidata species entity

This example displays a type specimen from the Global Plants site for the species _Agave americana_ which is associated with the Wikidata entity [Q161115](https://www.wikidata.org/entity/Q161115)
<param ve-plant-specimen eid="Q161115">

### Plant specimen using Global Plants identifier

This example also displays a type specimen from the Global Plants site for the species _Agave americana_.  In this example the Global Plants identifier ([10.5555/al.ap.specimen.us00092112](https://plants.jstor.org/stable/10.5555/al.ap.specimen.us00092112)) is used to display the image for a specific specimen.
<param ve-plant-specimen jpid="10.5555/al.ap.specimen.us00092112">
