<template>
    <div class="image" id="openseadragon1" :style="`width: ${width}px; height: ${height}px;`"></div>
</template>

<style>
    div.image {
        border: 1px solid #ccc;
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
        text-align: center;
    }
</style>

<script>
import osd from 'openseadragon'
export default {
    props: ["src", "x", "y", "x2", "y2", "width", "height"],
    data () {
        return {
            viewer: null,
            url: "",
        }
    },
    async mounted() {
        try {
            var dziURL = await this.axios.get('http://localhost:1323/generate?url=' + this.src)
            let options = {
                id: 'openseadragon1',
                tileSources: dziURL.data.data,
                showNavigationControl: false
            }
            this.viewer = OpenSeadragon(options);
            // if (this.x !== 0) {
            //     let vm = this
            //     this.viewer.addHandler("open", function(){
            //         let rect = vm.viewer.viewport.imageToViewportRectangle(this.x,this.y, this.x2-this.x, this.y2-this.y);
            //         vm.viewer.viewport.fitBounds(rect, true);
            //     });
            // }
        } catch (e) {
            console.error(e)
            return
        }
    }
}
</script>