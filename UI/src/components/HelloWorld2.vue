<script>
import {ref} from "vue"
export default {
  name: "HelloWorld2",
  props: {
    msg: {
      type: String,
      required: true
    },
  },
  data: () => ({
    thing1: "",
  }),
  mounted() {
    this.thing1 = this.msg
  },
  // mixed in newer way
  setup(props) {
    const thing2 = ref("")
    thing2.value = props.msg
  },
}
</script>

<template>
  <div class="greetings">
    <h1 class="green">{{ msg }}</h1>
    <h3>
      You’ve successfully created a project with
      <a href="https://vitejs.dev/" target="_blank" rel="noopener">Vite</a> +
      <a href="https://vuejs.org/" target="_blank" rel="noopener">Vue 3</a>.
    </h3>
  </div>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  position: relative;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
