<template>
  <div></div>
</template>

<script>
  export default {
    name: 'Index',
    fetch({ from, redirect }) {
      redirect(302, '/essay/', { src: from.query.src || process.env.root_essay })
    }
  }
</script>
