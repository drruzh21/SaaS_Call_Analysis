<!--
  API Keys settings component
  Allows users to manage their API keys
  @component SettingsApiKeys
-->
<template>
  <div>
    <div class="space-y-6 sm:px-6 lg:col-span-9 lg:px-0">
      <section aria-labelledby="api-keys-heading">
        <div class="shadow sm:overflow-hidden sm:rounded-md">
          <div class="bg-white py-6 px-4 sm:p-6">
            <div>
              <h2 id="api-keys-heading" class="text-lg font-medium leading-6 text-gray-900">API ключи</h2>
              <p class="mt-1 text-sm text-gray-500">
                Управляйте API ключами для доступа к сервису через API
              </p>
            </div>

            <div class="mt-6">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-sm font-medium text-gray-900">Активные ключи</h3>
                <button
                  type="button"
                  class="inline-flex items-center rounded-md bg-rose-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-rose-500"
                  @click="createNewKey"
                >
                  Создать новый ключ
                </button>
              </div>

              <!-- API Keys List -->
              <div class="mt-4 divide-y divide-gray-200">
                <div v-if="!apiKeys.length" class="text-sm text-gray-500 py-4">
                  У вас пока нет API ключей
                </div>
                <div
                  v-for="key in apiKeys"
                  :key="key.id"
                  class="flex items-center justify-between py-4"
                >
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ key.name }}</p>
                    <p class="text-sm font-mono text-gray-600">{{ key.key }}</p>
                    <p class="text-sm text-gray-500">Создан: {{ formatDate(new Date(key.created_at)) }}</p>
                  </div>
                  <button
                    type="button"
                    class="inline-flex items-center rounded-md bg-white px-2.5 py-1.5 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
                    @click="revokeKey(key.id)"
                  >
                    Отозвать
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- New API Key Modal -->
    <TransitionRoot as="template" :show="isModalOpen">
      <Dialog as="div" class="relative z-10" @close="closeModal">
        <TransitionChild
          as="template"
          enter="ease-out duration-300"
          enter-from="opacity-0"
          enter-to="opacity-100"
          leave="ease-in duration-200"
          leave-from="opacity-100"
          leave-to="opacity-0"
        >
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </TransitionChild>

        <div class="fixed inset-0 z-10 overflow-y-auto">
          <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <TransitionChild
              as="template"
              enter="ease-out duration-300"
              enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enter-to="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leave-from="opacity-100 translate-y-0 sm:scale-100"
              leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
                <div>
                  <div class="mt-3 text-center sm:mt-5">
                    <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                      Создание нового API ключа
                    </DialogTitle>
                    <div class="mt-2">
                      <p class="text-sm text-gray-500">
                        Введите название для нового API ключа. После создания ключ будет показан только один раз.
                      </p>
                    </div>
                    <div v-if="newKeyData" class="mt-4 p-4 bg-gray-50 rounded-md">
                      <p class="text-sm font-medium text-gray-900">Ваш новый API ключ:</p>
                      <p class="mt-2 font-mono text-sm text-gray-600 break-all">{{ newKeyData.key }}</p>
                      <p class="mt-2 text-sm text-gray-500">
                        Сохраните этот ключ! Он будет показан только один раз.
                      </p>
                    </div>
                    <div class="mt-4">
                      <input
                        type="text"
                        v-model="newKeyName"
                        class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-rose-600 sm:text-sm sm:leading-6"
                        placeholder="Например: Тестовый ключ"
                      />
                    </div>
                  </div>
                </div>
                <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                  <button
                    type="button"
                    class="inline-flex w-full justify-center rounded-md bg-rose-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-rose-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-rose-600 sm:col-start-2"
                    @click="confirmCreateKey"
                  >
                    Создать
                  </button>
                  <button
                    type="button"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
                    @click="closeModal"
                  >
                    Отмена
                  </button>
                </div>
              </DialogPanel>
            </TransitionChild>
          </div>
        </div>
      </Dialog>
    </TransitionRoot>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  TransitionChild,
  TransitionRoot,
} from '@headlessui/vue'

import type { IApiKey } from '@/interfaces/api-key'
import { generateApiKey, maskApiKey } from '@/utilities/api-key'

interface NewKeyData {
  key: string
  name: string
}

const apiKeys = ref<IApiKey[]>([])
const newKeyData = ref<NewKeyData | null>(null)
const isModalOpen = ref(false)
const newKeyName = ref('')

function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  }).format(date)
}

function createNewKey() {
  isModalOpen.value = true
}

function closeModal() {
  isModalOpen.value = false
  newKeyName.value = ''
  newKeyData.value = null
}

function confirmCreateKey() {
  if (newKeyName.value.trim()) {
    const key = generateApiKey()
    const newKey: IApiKey = {
      id: Math.random().toString(36).substring(7),
      name: newKeyName.value,
      key: key,
      created_at: new Date().toISOString(),
      is_active: true
    }
    
    // Сохраняем ключ для показа пользователю
    newKeyData.value = {
      key: key,
      name: newKeyName.value
    }
    
    // Добавляем замаскированную версию в список
    apiKeys.value.push({
      ...newKey,
      key: maskApiKey(key)
    })
    
    // В будущем здесь будет отправка на бэкенд
    // await createApiKey(newKey)
    
    closeModal()
  }
}

function revokeKey(keyId: string) {
  apiKeys.value = apiKeys.value.filter(key => key.id !== keyId)
}

onMounted(() => {
  // Добавляем тестовый ключ для проверки отображения
  const testKey = generateApiKey()
  apiKeys.value.push({
    id: '1',
    name: 'Тестовый ключ',
    key: maskApiKey(testKey),
    created_at: new Date().toISOString(),
    is_active: true
  })
})
</script>
