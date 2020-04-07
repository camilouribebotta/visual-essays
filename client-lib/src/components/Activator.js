import Vue from 'vue'

const Activator1 = Vue.component('activator', {
  template:
    `<span
      :data-id="id"
      class="activator"
      :title="title"
      :style="style"
      @click="clickHandler"
    >
      <v-icon>mdi-view-compact-outline</v-icon>
    </span>`
})
const ActivatorComponent = Vue.extend(Activator1)

export function addActivator(root, id, top, title, clickHandler) {
  root.appendChild(
    new ActivatorComponent({
      data: {
        id,
        title,
        style: {
          position: 'absolute',
          top: `${top}px`,
          left: '0px',
          cursor: 'pointer'
        }
      },
      methods: {
        clickHandler
      }
    })
    .$mount().$el)
  }