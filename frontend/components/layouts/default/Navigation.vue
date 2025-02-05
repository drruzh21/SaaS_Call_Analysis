<!--
  Main navigation component for the application
  This component handles both desktop and mobile navigation, as well as user authentication
  @component Navigation
-->
<template>
    <header class="bg-white">
        <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div class="flex h-16 justify-between">
                <div class="flex flex-1">
                    <!-- Logo -->
                    <div class="flex flex-shrink-0 items-center">
                        <NuxtLinkLocale to="/">
                            <img class="h-8 w-auto" src="~/assets/logo.png" alt="EMG Logo" />
                        </NuxtLinkLocale>
                    </div>

                    <!-- Desktop Navigation Links -->
                    <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
                        <NuxtLinkLocale
                            v-for="item in filteredNavigation"
                            :key="item.to"
                            :to="item.to"
                            class="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-sm font-medium text-gray-900 hover:border-rose-500 hover:text-rose-500"
                        >
                            {{ item.name }}
                        </NuxtLinkLocale>
                    </div>
                </div>

                <!-- User Menu -->
                <div class="flex items-center">
                    <Menu as="div" class="relative ml-3">
                        <div v-if="!authStore.loggedIn">
                            <NuxtLinkLocale 
                                to="/login"
                                class="rounded-full bg-white p-1 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:ring-offset-2"
                            >
                                <ArrowLeftEndOnRectangleIcon class="h-6 w-6" />
                            </NuxtLinkLocale>
                        </div>
                        <div v-else>
                            <MenuButton class="flex rounded-full bg-white text-sm focus:outline-none focus:ring-2 focus:ring-rose-500 focus:ring-offset-2">
                                <span class="sr-only">Открыть меню пользователя</span>
                                <img 
                                    class="h-8 w-8 rounded-full" 
                                    src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80" 
                                    alt="" 
                                />
                            </MenuButton>
                        </div>
                        <transition 
                            enter-active-class="transition ease-out duration-200"
                            enter-from-class="transform opacity-0 scale-95"
                            enter-to-class="transform opacity-100 scale-100"
                            leave-active-class="transition ease-in duration-75"
                            leave-from-class="transform opacity-100 scale-100"
                            leave-to-class="transform opacity-0 scale-95"
                        >
                            <MenuItems class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                                <MenuItem v-slot="{ active }">
                                    <NuxtLinkLocale 
                                        to="/settings" 
                                        :class="[active ? 'bg-gray-100' : '', 'block px-4 py-2 text-sm text-gray-700']"
                                    >
                                        Настройки
                                    </NuxtLinkLocale>
                                </MenuItem>
                                <MenuItem v-slot="{ active }">
                                    <a
                                        @click="handleLogout"
                                        :class="[active ? 'bg-gray-100' : '', 'block px-4 py-2 text-sm text-gray-700 cursor-pointer']"
                                    >
                                        Выйти
                                    </a>
                                </MenuItem>
                            </MenuItems>
                        </transition>
                    </Menu>

                    <!-- Mobile menu button -->
                    <div class="flex items-center sm:hidden">
                        <button 
                            type="button"
                            class="inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-rose-500"
                            @click="mobileMenuOpen = !mobileMenuOpen"
                        >
                            <span class="sr-only">Открыть меню</span>
                            <Bars3Icon v-if="!mobileMenuOpen" class="h-6 w-6" />
                            <XMarkIcon v-if="mobileMenuOpen" class="h-6 w-6" />
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Mobile menu panel -->
        <div v-show="mobileMenuOpen" class="sm:hidden">
            <div class="space-y-1 pb-3 pt-2">
                <NuxtLinkLocale
                    v-for="item in filteredNavigation"
                    :key="item.to"
                    :to="item.to"
                    class="block border-l-4 border-transparent py-2 pl-3 pr-4 text-base font-medium text-gray-500 hover:border-rose-500 hover:bg-gray-50 hover:text-rose-500"
                    @click="mobileMenuOpen = false"
                >
                    {{ item.name }}
                </NuxtLinkLocale>
            </div>
        </div>
    </header>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/vue'
import { Bars3Icon, XMarkIcon, ArrowLeftEndOnRectangleIcon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores'
import { useRouter } from '#app'

// Initialize stores and router
const authStore = useAuthStore()
const router = useRouter()

// Mobile menu state
const mobileMenuOpen = ref(false)

// Navigation items
const navigation = [
    { name: 'О нас', to: '/about' },
    { name: 'AI Фильтр', to: '/ai-filter', requiresAuth: true }
]

/**
 * Computed property that filters navigation items based on authentication state
 * This ensures reactive updates when auth state changes
 * @returns {Array} Filtered navigation items based on current auth state
 */
const filteredNavigation = computed(() => {
    return navigation.filter(item => {
        // If item requires auth, only show when user is logged in
        if (item.requiresAuth) {
            return authStore.loggedIn
        }
        // Always show items that don't require auth
        return true
    })
})

// Handle user logout
const handleLogout = async () => {
    await authStore.logOut()
    router.push('/')
}
</script>