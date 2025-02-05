<!--
  Footer component
  A minimal footer displaying copyright information and support contact
  @component Footer
-->
<template>
    <!-- 
  Footer component
  - Removed top margin as it's now handled by flex layout
  - bg-gray-900 maintains the dark theme
  - py-8 provides consistent vertical padding
-->
<footer class="bg-gray-900">
      <div class="mx-auto max-w-7xl py-8 px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col items-center space-y-4">
          <a href="mailto:b2b.ai.agency@gmail.com" class="text-base text-gray-400 hover:text-gray-300">
            Поддержка: b2b.ai.agency@gmail.com
          </a>
          <p class="text-base text-gray-400">&copy; 2025 App, All Rights Reserved.</p>
        </div>
      </div>
    </footer>
</template>

<script setup lang="ts">
// Footer component is now stateless
</script>

<style>
.pwa-toast {
  position: fixed;
  right: 0;
  bottom: 0;
  margin: 16px;
  padding: 12px;
  border: 1px solid #8885;
  border-radius: 4px;
  z-index: 1;
  text-align: left;
  box-shadow: 3px 4px 5px 0 #8885;
}
.pwa-toast .message {
  margin-bottom: 8px;
}
.pwa-toast button {
  border: 1px solid #8885;
  outline: none;
  margin-right: 5px;
  border-radius: 2px;
  padding: 3px 10px;
}
</style>