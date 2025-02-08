<template>
    <main>
      <!-- Hero section -->
      <div class="overflow-hidden pt-6 sm:pt-8 lg:relative lg:py-20">
        <div class="mx-auto max-w-md px-4 sm:max-w-3xl sm:px-6 lg:grid lg:max-w-7xl lg:grid-cols-2 lg:gap-24 lg:px-8">
          <div>
            <div class="mt-10">
              <div>
                <div class="inline-flex space-x-4">
                  <NuxtLinkLocale to="/about" class="rounded bg-rose-50 px-2.5 py-1 text-sm font-semibold text-rose-500">Возможности</NuxtLinkLocale>
                </div>
              </div>
              <div class="mt-6 sm:max-w-xl">
                <h1 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">Интеллектуальный анализ коммуникаций на базе AI</h1>
                <p class="mt-6 text-xl text-gray-500">Превращаем звонки в измеримые показатели. Автоматически выявляем ключевые метрики, тренды и зоны роста команды продаж.</p>
              </div>
              <div class="mt-6 sm:max-w-xl">
                <ul class="list-disc ml-6 text-gray-600">
                  <li>
                    <span class="font-bold">Анализ скриптов</span> - Контроль соблюдения скриптов продаж без ручной проверки
                  </li>
                  <li>
                    <span class="font-bold">Метрики менеджеров</span> - Объективная оценка эффективности каждого сотрудника
                  </li>
                  <li>
                    <span class="font-bold">Командная аналитика</span> - Прозрачная статистика для руководителей и команды
                  </li>
                  <li>
                    <span class="font-bold">Анализ возражений</span> - Отслеживание и анализ ключевых возражений клиентов
                  </li>
                  <li>
                    <span class="font-bold">Быстрый онбординг</span> - Сокращение времени обучения новых менеджеров
                  </li>
                </ul>
              </div>
              <div class="mt-8">
                <NuxtLinkLocale 
                  :to="startWorkRoute" 
                  class="inline-flex items-center rounded-md border border-transparent bg-rose-500 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-rose-600"
                >
                  Начать работу
                  <ChevronRightIcon class="ml-2 h-5 w-5" aria-hidden="true" />
                </NuxtLinkLocale>
              </div>
            </div>
          </div>
        </div>

        <div class="sm:mx-auto sm:max-w-3xl sm:px-6">
          <div class="py-12 sm:relative sm:mt-12 sm:py-16 lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2">
            <div class="hidden sm:block">
              <div class="absolute inset-y-0 left-1/2 w-screen rounded-l-3xl bg-gray-50 lg:left-80 lg:right-0 lg:w-full" />
              <svg class="absolute top-8 right-1/2 -mr-3 lg:left-0 lg:m-0" width="404" height="392" fill="none" viewBox="0 0 404 392">
                <defs>
                  <pattern id="837c3e70-6c3a-44e6-8854-cc48c737b659" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
                    <rect x="0" y="0" width="4" height="4" class="text-gray-200" fill="currentColor" />
                  </pattern>
                </defs>
                <rect width="404" height="392" fill="url(#837c3e70-6c3a-44e6-8854-cc48c737b659)" />
              </svg>
            </div>
            <div class="relative -mr-40 pl-4 sm:mx-auto sm:max-w-3xl sm:px-0 lg:h-full lg:max-w-none lg:pl-12">
              <img class="w-full rounded-md shadow-xl ring-1 ring-black ring-opacity-5 lg:h-full lg:w-auto lg:max-w-none" src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1470&q=80" alt="Панель анализа звонков" />
            </div>
          </div>
        </div>
      </div>
    </main>
</template>

<script setup lang="ts">
import { ChevronRightIcon } from "@heroicons/vue/20/solid"
import { tokenIsTOTP } from "@/utilities"
import { useAuthStore, useTokenStore } from "@/stores"
import { computed } from 'vue'

definePageMeta({
  layout: "default",
});

const authStore = useAuthStore()
const tokenStore = useTokenStore()
const route = useRoute()

/**
 * Computed property that determines the target route for the "Start Work" button
 * Returns '/ai-filter' if user is authenticated, '/login' otherwise
 * @returns {string} Target route path
 */
const startWorkRoute = computed(() => {
    return authStore.loggedIn ? '/ai-filter' : '/login'
})

const redirectTOTP = "/totp"
const redirectAfterLogin = "/"
const github = {
  name: "GitHub",
  href: "https://github.com/whythawk/full-stack-fastapi-postgresql",
  icon: defineComponent({
    render: () =>
      h("svg", { fill: "currentColor", viewBox: "0 0 24 24" }, [
        h("path", {
          "fill-rule": "evenodd",
          d: "M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z",
          "clip-rule": "evenodd",
        }),
      ]),
  }),
}

onMounted(async () => {
  // Check if email is being validated
  if (route.query && route.query.magic) {
    // No idea: https://stackoverflow.com/q/74759799/295606
    await new Promise((resolve) => {
      setTimeout(() => {
        resolve(true)
      }, 100)
    })
    if (!authStore.loggedIn) await authStore.magicLogin(route.query.magic as string)
    if (tokenIsTOTP(tokenStore.token)) await navigateTo(redirectTOTP)
    else await navigateTo(redirectAfterLogin) 
  }
})
</script>