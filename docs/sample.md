<a href="https://visual-essays.app/sample"><img src="images/ve-button.png"/></a>

<param ve-config
       title="Sample Essay"
       banner="images/da_vinci_banner.jpg"
       layout="vtl"
       author="Ron">

<param ve-component 
       name="network"
       src="components/Network.vue"
       selectors="tag:network"
       icon="fa-chart-network"
       label="Networks"
       dependencies="https://d3js.org/d3.v4.min.js">

<!--
<param ve-component 
       name="people"
       src="components/EntityViewer.vue"
       selectors="category:person"
       icon="fa-user"
       label="People">
-->

<param ve-component 
       name="plant-specimen"
       src="components/PlantSpecimenViewer.vue"
       selectors="tag:plant-specimen"
       icon="fa-seedling"
       label="Plant Specimens">

<param ve-component 
       name="plant-hierarchy"
       src="components/PlantHierarchy.vue"
       selectors="tag:plant-hierarchy"
       icon="fa-sitemap"
       label="Plant Hierarchy"
       dependencies="//unpkg.com/force-graph">

<param ve-entity title="Ginevra de' Benci" eid="Q1267893">
<param ve-entity title="Milan, Italy" eid="Q490">
<param ve-entity title="Bologna, Italy" eid="Q1891">
<param ve-entity title="Rome, Italy" eid="Q220">
<param ve-entity title="Venice, Italy" eid="Venice">
<param ve-entity title="Vinci, Tuscany, Italy" eid="Q82884">
<param ve-entity title="Leonardo da Vinci" eid="Q762">

## OpenSeadragon Image Viewer

Ginevra de' Benci is a portrait painting by Leonardo da Vinci of the 15th-century Florentine aristocrat Ginevra de' Benci (born c.  1458). The oil-on-wood portrait was acquired by the National Gallery of Art in Washington, D.C. in 1967. The sum of US$5 million—an absolute record price at the time—came from the Ailsa Mellon Bruce Fund and was paid to the Princely Family of Liechtenstein. It is the only painting by Leonardo on public view in the Americas.
<param ve-open-seadragon
       fit="cover"
       title="Ginevra de' Benci (cover)"
       url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg/985px-Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg"
       thumbnail="https://commons.wikimedia.org/w/thumb.php?f=Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg&w=140"
       hires="https://upload.wikimedia.org/wikipedia/commons/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg">
<param ve-image mirador
       manifest="https://tripleeyeeff-atjcn6za6q-uc.a.run.app/presentation/79729103d0f9e4d474ab359c6c5da50307c889f5e3b3ad21e1055757/manifest"
       annotations="iiif-annotations/benci.json">
<param ve-image
       manifest="https://iiif.harvardartmuseums.org/manifests/object/299843">
<param ve-image
       manifest="https://tripleeyeeff-atjcn6za6q-uc.a.run.app/presentation/968832e213390d9b1c7d13c30ed2c8f113b1beb797e0839b0efd02c7/manifest">

## Plant specimens

### Multiple specimens, using ve-specimen tag

Prunus occidentalis is a plant in the family Rosaceae of the order Rosales. The plant can be found in the Caribbean, Central America and northern South America. It is native to Puerto Rico. Its Spanish common names include almendrón. Its English common name is the western cherry laurel. The plant is common in the Toro Negro State Forest. Family of Liechtenstein. 
<param ve-plant-specimen primary eid="Q12844029" max="1" reverse="true">
<param ve-plant-specimen eid="Q165321" max="1">
<param ve-plant-specimen eid="Q5486220" max="1">

### Specimen, using image viewer

Prunus occidentalis is a plant in the family Rosaceae of the order Rosales. The plant can be found in the Caribbean, Central America and northern South America. It is native to Puerto Rico. Its Spanish common names include almendrón. Its English common name is the western cherry laurel. The plant is common in the Toro Negro State Forest. Family of Liechtenstein. 
<param ve-image
       title="Holotype of Prunus serrulata Lindley f. shibayama E. H. Wilson [family ROSACEAE]"
       fit="cover"
       url="https://plants.jstor.org/fsi/img/size3/alukaplant/a/phase_01/a0000/a00032200.jpg"
       thumbnail="https://plants.jstor.org/fsi/img/size1/alukaplant/a/phase_01/a0000/a00032200.jpg"
       hires="https://plants.jstor.org/seqapp/adore-djatoka/resolver?url_ver=Z39.88-2004&svc_id=info:lanl-repo/svc/getRegion&svc_val_fmt=info:ofi/fmt:kev:mtx:jpeg2000&svc.format=image/jpeg&rft_id=/jp2/fpx/16/gpi-a-typspe-01-42/a0000/a00032200.jp2">

### Plant Hierarchy Viewer

Heliconia, derived from the Greek word Ἑλικώνιος (helikṓnios), is a genus of flowering plants in the monotypic family Heliconiaceae. Most of the ca 194 known species are native to the tropical Americas, but a few are indigenous to certain islands of the western Pacific and Maluku. Many species of Heliconia are found in the tropical forests of these regions. Most species are listed as either “vulnerable” or “data deficient” by the IUCN Red List of threatened species. Several species are widely cultivated as ornamentals, and a few are naturalized in Florida, Gambia and Thailand. Common names for the genus include lobster-claws, toucan beak, wild plantains or false bird-of-paradise. The last term refers to their close similarity to the bird-of-paradise flowers (Strelitzia). Collectively, these plants are also simply referred to as heliconias.
<param ve-plant-hierarchy primary eid="Q624242">
<param ve-network>

## Images ## {: #link1 }

### Images - Gallery with contain and cover fit

Ginevra de' Benci is a portrait painting by Leonardo da Vinci of the 15th-century Florentine aristocrat Ginevra de' Benci (born c.  1458). The oil-on-wood portrait was acquired by the National Gallery of Art in Washington, D.C. in 1967. The sum of US$5 million—an absolute record price at the time—came from the Ailsa Mellon Bruce Fund and was paid to the Princely Family of Liechtenstein. It is the only painting by Leonardo on public view in the Americas.
<param ve-image
       fit="cover"
       title="Ginevra de' Benci (cover)"
       url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg/985px-Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg"
       thumbnail="https://commons.wikimedia.org/w/thumb.php?f=Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg&w=140"
       hires="https://upload.wikimedia.org/wikipedia/commons/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg">
<param ve-image
       title="Holotype of Prunus serrulata Lindley f. shibayama E. H. Wilson [family ROSACEAE]"
       fit="cover"
       url="https://plants.jstor.org/fsi/img/size3/alukaplant/a/phase_01/a0000/a00032200.jpg"
       thumbnail="https://plants.jstor.org/fsi/img/size1/alukaplant/a/phase_01/a0000/a00032200.jpg"
       hires="https://plants.jstor.org/seqapp/adore-djatoka/resolver?url_ver=Z39.88-2004&svc_id=info:lanl-repo/svc/getRegion&svc_val_fmt=info:ofi/fmt:kev:mtx:jpeg2000&svc.format=image/jpeg&rft_id=/jp2/fpx/16/gpi-a-typspe-01-42/a0000/a00032200.jp2">

## Maps

### Simple markers

Born out of wedlock to a notary, Piero da Vinci, and a peasant woman, Caterina, in Vinci, in the region of Florence, Italy, Leonardo was educated in the studio of the renowned Italian painter Andrea del Verrocchio. Much of his earlier working life was spent in the service of Ludovico il Moro in Milan, and he later worked in Rome, Bologna and Venice. He spent his last three years in France, where he died in 1519.
<param ve-map basemap="Esri_WorldPhysical" center="Q82884" zoom="7">
{: #link2 }

### Hide labels

Born out of wedlock to a notary, Piero da Vinci, and a peasant woman, Caterina, in Vinci, in the region of Florence, Italy, Leonardo was educated in the studio of the renowned Italian painter Andrea del Verrocchio. Much of his earlier working life was spent in the service of Ludovico il Moro in Milan, and he later worked in Rome, Bologna and Venice. He spent his last three years in France, where he died in 1519.
<param ve-map center="Q82884" zoom="7" hide-labels>

### Map - Show locations as GeoJSON regions

Born out of wedlock to a notary, Piero da Vinci, and a peasant woman, Caterina, in Vinci, in the region of Florence, Italy, Leonardo was educated in the studio of the renowned Italian painter Andrea del Verrocchio. Much of his earlier working life was spent in the service of Ludovico il Moro in Milan, and he later worked in Rome, Bologna and Venice. He spent his last three years in France, where he died in 1519.
<param ve-map center="Q82884" zoom="7" prefer-geojson>
<param ve-map-layer geojson active url="https://data.whosonfirst.org/101/752/643/101752643.geojson" aliases="florence">
<param ve-map-layer geojson active url="geojson/test.json">

### Map - Show locations as GeoJSON regions with no labels

Born out of wedlock to a notary, Piero da Vinci, and a peasant woman, Caterina, in Vinci, in the region of Florence, Italy, Leonardo was educated in the studio of the renowned Italian painter Andrea del Verrocchio. Much of his earlier working life was spent in the service of Ludovico il Moro in Milan, and he later worked in Rome, Bologna and Venice. He spent his last three years in France, where he died in 1519.
<param ve-map center="Q82884" zoom="7" prefer-geojson hide-labels>
<param ve-map-layer geojson active url="https://data.whosonfirst.org/101/752/643/101752643.geojson" aliases="florence">
<param ve-map-layer geojson active url="geojson/test.json" title="Test">
<param ve-network>

### Map - Flyto Rome

Born out of wedlock to a notary, Piero da Vinci, and a peasant woman, Caterina, in Vinci, in the region of Florence, Italy, Leonardo was educated in the studio of the renowned Italian painter Andrea del Verrocchio. Much of his earlier working life was spent in the service of Ludovico il Moro in Milan, and he later worked in Rome, Bologna and Venice. He spent his last three years in France, where he died in 1519.
<param ve-map center="Q220" zoom="11" prefer-geojson>

## Images

### Images - Gallery with contain and cover fit

Ginevra de' Benci is a portrait painting by Leonardo da Vinci of the 15th-century Florentine aristocrat Ginevra de' Benci (born c.  1458). The oil-on-wood portrait was acquired by the National Gallery of Art in Washington, D.C. in 1967. The sum of US$5 million—an absolute record price at the time—came from the Ailsa Mellon Bruce Fund and was paid to the Princely Family of Liechtenstein. It is the only painting by Leonardo on public view in the Americas.
<param ve-image 
       fit="cover"
       title="Ginevra de' Benci (cover)"
       url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg/985px-Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg"
       thumbnail="https://commons.wikimedia.org/w/thumb.php?f=Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg&w=140"
       hires="https://upload.wikimedia.org/wikipedia/commons/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg">


### Images - Gallery with contain and cover fit

Ginevra de' Benci is a portrait painting by Leonardo da Vinci of the 15th-century Florentine aristocrat Ginevra de' Benci (born c.  1458). The oil-on-wood portrait was acquired by the National Gallery of Art in Washington, D.C. in 1967. The sum of US$5 million—an absolute record price at the time—came from the Ailsa Mellon Bruce Fund and was paid to the Princely Family of Liechtenstein. It is the only painting by Leonardo on public view in the Americas.
<param ve-image 
       fit="cover"
       title="Ginevra de' Benci (cover)"
       url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg/985px-Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg"
       thumbnail="https://commons.wikimedia.org/w/thumb.php?f=Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg&w=140"
       hires="https://upload.wikimedia.org/wikipedia/commons/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg">
<param ve-image 
       fit="contain"
       title="Ginevra de' Benci (contain)"
       url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg/985px-Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg"
       thumbnail="https://commons.wikimedia.org/w/thumb.php?f=Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg&w=140"
       hires="https://upload.wikimedia.org/wikipedia/commons/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg">

### Images - Cards view as default

Ginevra de' Benci is a portrait painting by Leonardo da Vinci of the 15th-century Florentine aristocrat Ginevra de' Benci (born c.  1458). The oil-on-wood portrait was acquired by the National Gallery of Art in Washington, D.C. in 1967. The sum of US$5 million—an absolute record price at the time—came from the Ailsa Mellon Bruce Fund and was paid to the Princely Family of Liechtenstein. It is the only painting by Leonardo on public view in the Americas.
<param ve-primary="image" mode="cards">
<param ve-image 
       fit="contain"
       title="Ginevra de' Benci (contain)"
       url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg/985px-Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg"
       thumbnail="https://commons.wikimedia.org/w/thumb.php?f=Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg&w=140"
       hires="https://upload.wikimedia.org/wikipedia/commons/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg">
<param ve-image 
       fit="cover"
       title="Ginevra de' Benci (cover)"
       url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg/985px-Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg"
       thumbnail="https://commons.wikimedia.org/w/thumb.php?f=Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg&w=140"
       hires="https://upload.wikimedia.org/wikipedia/commons/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg">

### Images - Paragraph with map and images

Ginevra de' Benci is a portrait painting by Leonardo da Vinci of the 15th-century Florentine aristocrat Ginevra de' Benci (born c.  1458). The oil-on-wood portrait was acquired by the National Gallery of Art in Washington, D.C. in 1967. The sum of US$5 million—an absolute record price at the time—came from the Ailsa Mellon Bruce Fund and was paid to the Princely Family of Liechtenstein. It is the only painting by Leonardo on public view in the Americas.
<param ve-map center="Q220" zoom="11" prefer-geojson>
<param ve-image 
       fit="contain"
       title="Ginevra de' Benci (contain)"
       url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg/985px-Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg"
       thumbnail="https://commons.wikimedia.org/w/thumb.php?f=Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg&w=140"
       hires="https://upload.wikimedia.org/wikipedia/commons/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg">

### Images - Paragraph with map and images - initial images

Ginevra de' Benci is a portrait painting by Leonardo da Vinci of the 15th-century Florentine aristocrat Ginevra de' Benci (born c.  1458). The oil-on-wood portrait was acquired by the National Gallery of Art in Washington, D.C. in 1967. The sum of US$5 million—an absolute record price at the time—came from the Ailsa Mellon Bruce Fund and was paid to the Princely Family of Liechtenstein. It is the only painting by Leonardo on public view in the Americas.
<param ve-primary="image">
<param ve-map center="Q220" zoom="11" prefer-geojson>
<param ve-image 
       fit="contain"
       title="Ginevra de' Benci (contain)"
       url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg/985px-Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg"
       thumbnail="https://commons.wikimedia.org/w/thumb.php?f=Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg&w=140"
       hires="https://upload.wikimedia.org/wikipedia/commons/1/18/Leonardo_da_Vinci_-_Ginevra_de%27_Benci_-_Google_Art_ProjectFXD.jpg">]
