<template>
  <div>{{$options.name}}: items={{items.length}}
</template>

<script>
  module.exports = {
    name: 'CustomEntityViewer',
    props: {
      items: { type: Array, default: () => ([]) }
    }
  }
</script>

<style></style>
