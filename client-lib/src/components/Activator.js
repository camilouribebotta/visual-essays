import Vue from 'vue'

const FunctionalActivator = Vue.component('activator', {
  functional: true,
  render: function (createElement) {
    return createElement(
      'span',
      {
        attrs: {
            'data-id': this.item.id
        },
        domProps: {
            innerHTML: 'X'
        },
        style: {
          position: 'absolute',
          left: this.item.left === null ? null : `${this.item.left}px`,
          right:  this.item.right === null ? null : `${this.item.right}px`,
          top: `${this.item.top}px`,
          cursor: 'pointer',
          paddingRight: '2px',
          paddingLeft: '3px'
        },
        on: {
          click: this.clickHandler
        }
      }
    )
  }
})
const FunctionalActivatorComponent = Vue.extend(FunctionalActivator)

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
          left: '-30px',
          cursor: 'pointer'
        }
      },
      methods: {
        clickHandler
      }
    })
    .$mount().$el)
  }