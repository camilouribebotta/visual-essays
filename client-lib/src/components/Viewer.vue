<template>
  <v-card id="viewer">
  
    <!-- <v-card-title class="text-center" style="padding:0; margin:0;" v-html="title"/> -->

    <v-card-text class="text-left" style="padding:0; margin:0;" >
      <!-- <lmap :center="[38.895, -77.036667]" :zoom="11"/> -->
      
      <!--
        <v-card>
        <v-card-title class="text-center">Items</v-card-title>
        <v-card-text class="text-left">
          <ul>
            <li v-for="item in itemsInActiveSections" :key="item.id">{{item.label || item.id}}</li>
          </ul>
        </v-card-text>
      </v-card>
      -->

      <!-- 
      &#x2318;
      <v-card v-if="entities.length">
        <v-card-title class="text-center">Entities</v-card-title>
        <v-card-text class="text-left">
          <ul>
            <li v-for="entity in entities" :key="entity.id">{{entity.label}}</li>
          </ul>
        </v-card-text>
      </v-card>
      --> 
      <v-card style="padding:0; margin:0;" >
        <v-card-text class="text-left" style="padding:0; margin:0;">
          <lmap/>
        </v-card-text>
      </v-card>

    </v-card-text>
  </v-card>   
</template>

<script>
  import Map from './Map'

  export default {
    name: 'Viewer',
    components: {
      lmap: Map
    },
    data: () => ({}),
    computed: {
      entities() { return this.$store.getters.itemsInActiveElements.filter(item => item.type === 'entity') },
      title() { return this.$store.getters.activeElement ? this.$store.getters.activeElement.title ? this.$store.getters.activeElement.title : this.$store.getters.activeElement.id : null }
    }
  }
</script>

<style>

  #viewer {
    height: 100%;
  }

</style>

