<script setup>
import { RouterView } from 'vue-router'
import Navbar from './components/Navbar.vue'

/**
 * Later in future, when doing session logins, should check state management for status, then send request to check session
 * If session returns diff data (auth state & isAdmin), don't allow login or force logout (if logged in already)
 */
</script>

<template>
  <v-app>
		<Navbar />
		<RouterView v-slot="{Component}">
			<Transition name="fade" mode="out-in">
				<component :is="Component" id="main" class="h-100 w-100" />
			</Transition>
		</RouterView>
	</v-app>
</template>

<style>
#main {
	margin: 0 56px;
	max-width: 90%;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.35s ease-out;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 1rem;
  text-align: left;
  margin: 0 0.5rem 0 0;
	padding: 1rem 0;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
</style>
