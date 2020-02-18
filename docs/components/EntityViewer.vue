<template>
  <div>{{$options.name}}: items={{items.length}}
</template>

<script>
  export default {
    name: 'CustomEntityViewer',
    props: {
      items: { type: Array, default: () => ([]) }
    }
  }
</script>
