<template>
    <Html :lang="htmlAttrs.lang" :dir="htmlAttrs.dir">
        <Body>
            <!-- 
  Main layout wrapper
  Uses flex layout to ensure footer stays at bottom:
  - min-h-screen: ensures minimum height is full viewport
  - flex flex-col: creates vertical flex container
  - flex-1: allows main content to grow and push footer down
-->
<div class="min-h-screen flex flex-col bg-white">
                <slot name="header" >
                    <LayoutsDefaultNavigation />
                </slot>
                <!-- Main content wrapper with flex-1 to push footer down -->
<main class="flex-1">
  <slot />
</main>
                <slot name="footer" >
                    <LayoutsNotification />
                    <LayoutsDefaultFooter />
                </slot>
            </div>
        </Body>
    </Html>
</template>

<script setup lang="ts">
const head = useLocaleHead({
    addDirAttribute: true,
    addSeoAttributes: true,
})
const htmlAttrs = computed(() => head.value.htmlAttrs!)
</script>