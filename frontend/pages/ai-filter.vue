<!--
  AI Filter configuration page
  Allows users to customize GPT prompt for call analysis
  @component AIFilter
-->
<template>
    <main class="min-h-full">
        <div class="mx-auto max-w-5xl py-12 px-4 sm:px-6 lg:px-8">
            <div>
                <h2 class="text-3xl font-bold tracking-tight text-gray-900">Настройка AI фильтра</h2>
                <p class="mt-2 text-sm text-gray-600">
                    Оптимизируйте анализ звонков с помощью интеллектуальной фильтрации
                </p>

                <!-- AI Filter Information Section -->
                <div class="mt-6 rounded-lg bg-white px-6 py-5 shadow">
                    <div class="text-sm text-gray-600">
                        AI фильтр автоматически определяет звонки, требующие детального анализа, на основе заданных критериев продаж. Это позволяет сфокусироваться только на важных разговорах и сократить расходы на анализ.
                    </div>
                </div>
            </div>

            <div class="mt-8">
                <div class="bg-white shadow sm:rounded-lg">
                    <div class="px-4 py-5 sm:p-6">
                        <Form @submit="handleSubmit" class="space-y-6">
                            <Field name="prompt" v-slot="{ field, errorMessage }" rules="required" v-model="formData.prompt">
                                <div>
                                    <label for="prompt" class="block text-sm font-medium text-gray-700">Промпт для GPT</label>
                                    <div class="mt-1">
                                        <textarea
                                            id="prompt"
                                            rows="12"
                                            v-bind="field"
                                            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-rose-500 focus:ring-rose-500 sm:text-sm"
                                        />
                                    </div>
                                    <p class="mt-2 text-sm text-gray-500">
                                        Настройте критерии фильтрации звонков. Промпт определяет, какие звонки требуют детального анализа.
                                    </p>
                                    <ErrorMessage name="prompt" class="mt-2 text-sm text-red-600" />
                                </div>
                            </Field>

                            <div class="flex justify-start space-x-4">
                                <button
                                    type="submit"
                                    :disabled="isLoading"
                                    class="inline-flex justify-center rounded-md border border-transparent bg-rose-500 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-rose-600 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:ring-offset-2"
                                >
                                    {{ isLoading ? 'Сохранение...' : 'Сохранить настройки' }}
                                </button>
                                <button
                                    type="button"
                                    @click="resetToDefault"
                                    class="inline-flex justify-center rounded-md border border-gray-300 bg-white py-2 px-4 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:ring-offset-2"
                                >
                                    Вернуть настройки по умолчанию
                                </button>
                            </div>
                        </Form>
                    </div>
                </div>
            </div>
        </div>
    </main>
</template>

<script setup lang="ts">
import { Form, Field, ErrorMessage } from 'vee-validate';
import { useAuthStore, useToastStore } from '@/stores'
import { useRouter } from '#app'
import { ref, onMounted } from 'vue'
import { DEFAULT_CALL_ANALYSIS_PROMPT } from '@/constants/prompts'

// Initialize stores
const authStore = useAuthStore()
const toast = useToastStore()
const router = useRouter()

// Form data with reactive state
const formData = ref({
    prompt: ''
})

const isLoading = ref(false)

// Load current user's prompt
const loadUserPrompt = async () => {
    isLoading.value = true;
    try {
        // Ждем инициализации токенов
        await authStore.tokenStore.refreshTokens();
        
        if (!authStore.tokenStore.token) {
            router.push('/login');
            return;
        }

        const response = await fetch('/api/v1/users/me/gpt-filter-prompt', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authStore.tokenStore.token}`
            },
            credentials: 'include'
        });

        if (response.status === 401 || response.status === 403) {
            router.push('/login');
            return;
        }

        if (!response.ok) {
            throw new Error('Failed to load prompt');
        }

        const data = await response.json();
        formData.value.prompt = data.gpt_filter_prompt || DEFAULT_CALL_ANALYSIS_PROMPT;
    } catch (error) {
        console.error('Error loading prompt:', error);
        formData.value.prompt = DEFAULT_CALL_ANALYSIS_PROMPT;
        toast.addNotice({
            title: "Ошибка загрузки",
            content: "Не удалось загрузить текущие настройки",
            icon: "error"
        });
    } finally {
        isLoading.value = false;
    }
}

// Reset form to default values
const resetToDefault = () => {
    formData.value.prompt = DEFAULT_CALL_ANALYSIS_PROMPT;
}

// Handle form submission
const handleSubmit = async (values: any) => {
    try {
        await authStore.tokenStore.refreshTokens()
        if (!authStore.loggedIn || !authStore.tokenStore.token) {
            router.push('/login');
            return;
        }

        const response = await fetch('/api/v1/users/me/gpt-filter-prompt', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authStore.tokenStore.token}`
            },
            credentials: 'include',
            body: JSON.stringify({
                gpt_filter_prompt: values.prompt
            })
        });

        if (response.status === 401 || response.status === 403) {
            router.push('/login');
            return;
        }

        if (!response.ok) {
            throw new Error('Failed to update prompt');
        }

        toast.addNotice({
            title: "Настройки сохранены",
            content: "Настройки AI фильтра успешно обновлены"
        });

    } catch (error) {
        toast.addNotice({
            title: "Ошибка сохранения",
            content: "Не удалось сохранить настройки",
            icon: "error"
        });
        console.error('Error saving settings:', error);
    }
}

// Route guard
onMounted(async () => {
    await authStore.$init;
    await authStore.tokenStore.refreshTokens();
    
    if (!authStore.loggedIn || !authStore.tokenStore.token) {
        router.push('/login');
        return;
    }
    loadUserPrompt();
})
</script>
