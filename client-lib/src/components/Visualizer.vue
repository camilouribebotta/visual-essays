<template>
  <div
    class="text-center"
    style="height:100%;"
  >
    <viewer/>
  </div>
</template>

<script>

export default {
  name: 'visualizer',
  methods: {
    clickHandler(e) {
      this.$store.dispatch('setSelectedItemID', e.toElement.attributes['data-itemid'].value)
    },
    addClickHandlers(elemId) {
      document.getElementById(elemId).querySelectorAll('.inferred, .tagged').forEach((entity) => {
        entity.addEventListener('click', this.clickHandler)
      })
    },
    removeClickHandlers(elemId) {
      const elem = document.getElementById(elemId)
      if (elem) {
        document.getElementById(elemId).querySelectorAll('.inferred, .tagged').forEach((entity) => {
          entity.removeEventListener('click', this.clickHandler)
        })
      }
    }
  },
  watch: {
    visualizerIsOpen(isOpen) {
      if (!isOpen) {
        this.$store.dispatch('setSelectedItemID')
      }
    },
    activeElement(current, prior) {
      if (current) {
        if (prior) {
          this.removeClickHandlers(prior)
        }            
        this.addClickHandlers(current)
      }
    }
  }
}
</script>
