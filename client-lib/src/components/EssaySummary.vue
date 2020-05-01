<template>
  <v-container class="summary">
    <v-row style="height:100%;" no-gutters>

        <v-col cols="12" sm="5">
          <h3>Title of Essay</h3>
          <p id="author-name">The Author</p>
          <small id="author-role">The Author's Role</small>

        </v-col>
        <v-col cols="12" sm="4" style="margin-top: 38px;">
          <small>Published: date</small><br>
          <small>Share: </small>
        </v-col>
        <v-col class="align-end" cols="12" sm="3" style="text-align: right">
          <small>This visual essay contains:</small>
        </v-col>

    </v-row>
  </v-container>
</template>

<script>

  export default {
    name: 'EssaySummary',
    data: () => ({
    })
  }
</script>

<style>
  .summary {
    font-size: 12px;
    height: 100%;
  }

  .summary h3 {
    font-family: Georgia, serif;
    padding-left: 0px;
    font-size: 1.7em;
    margin-bottom: .5em;
  }

  #author-name {
    margin-bottom: .2em;
  }

  #author-role {
    margin-bottom: 0px;
    font-size: 10px;
  }
</style>