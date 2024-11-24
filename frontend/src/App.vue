<template>
  <div id="app" class="container">
    <TheNavbar />
    <FlashMessages :messages="messages" />
    <router-view />
  </div>
</template>

<script>
import TheNavbar from "@/components/TheNavbar.vue";
import FlashMessages from "@/components/FlashMessages.vue";

export default {
  components: {
    TheNavbar,
    FlashMessages,
  },
};
</script>
