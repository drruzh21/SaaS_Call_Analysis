<!-- About Us Page -->
<template>
  <div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
      <!-- Header Section -->
      <div class="text-center mb-16">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">О нас и нашем сервисе</h1>
        <p class="text-xl text-gray-600">Инновационное решение для анализа звонков менеджеров по продажам</p>
      </div>

      <!-- Main Content -->
      <div class="space-y-12">
        <!-- About Us Section -->
        <section class="bg-white rounded-lg shadow-lg p-8">
          <h2 class="text-2xl font-semibold text-gray-900 mb-6">О платформе</h2>
          <p class="text-gray-700 leading-relaxed mb-6">
            Анализируем звонки менеджеров используя искусственный интеллект и находим упущенные сделки. 
          </p>
          <p class="text-gray-700 leading-relaxed mb-6">
            Наш сервис помогает отделам продаж:
          </p>
          <ul class="list-disc pl-6 text-gray-700 space-y-2 mb-6">
            <li>Выявлять ключевые возражения клиентов</li>
            <li>Автоматически проверять бизнес-коммуникации по чек-листам</li>
            <li>Отслеживать упоминания конкурентов</li>
            <li>Собирать данные для обучения менеджеров</li>
            <li>Тестировать новые скрипты продаж</li>
            <li>Проверяя A/B гипотезы, видеть результаты в реальном времени</li>
          </ul>
        </section>

        <!-- Key Features Section -->
        <section class="bg-white rounded-lg shadow-lg p-8">
          <h2 class="text-2xl font-semibold text-gray-900 mb-6">Ключевые функции платформы</h2>
          
          <!-- API Keys Feature -->
          <div class="mb-8">
            <h3 class="text-xl font-medium text-gray-900 mb-4">
              <span class="inline-flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-500 rounded-full mr-3">1</span>
              Безопасная авторизация через API-ключи
            </h3>
            <p class="text-gray-700 leading-relaxed pl-11">
              Наша система использует надежную авторизацию через API-ключи для обеспечения 
              безопасного взаимодействия между выгрузчиком звонков и нашим API. Это гарантирует, 
              что ваши данные защищены и доступны только авторизованным пользователям.
            </p>
          </div>

          <!-- GPT Filter Feature -->
          <div>
            <h3 class="text-xl font-medium text-gray-900 mb-4">
              <span class="inline-flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-500 rounded-full mr-3">2</span>
              Интеллектуальная фильтрация звонков
            </h3>
            <p class="text-gray-700 leading-relaxed pl-11">
              GPT-фильтр – это инновационное решение для интеллектуального отбора звонков. 
              Он автоматически определяет и исключает из анализа нерелевантные звонки, такие как:
            </p>
            <ul class="list-disc pl-16 mt-4 text-gray-700 space-y-2">
              <li>Консультативные звонки с существующими клиентами</li>
              <li>Технические консультации по уже приобретенным продуктам</li>
              <li>Звонки, не связанные с процессом продаж</li>
            </ul>
            <p class="text-gray-700 leading-relaxed pl-11 mt-4">
              Это позволяет сфокусировать аналитику на действительно важных звонках, 
              где происходит активный процесс продаж, что делает анализ более точным и полезным.
            </p>
          </div>
        </section>

        <!-- Results Section -->
        <section class="bg-white rounded-lg shadow-lg p-8">
          <h2 class="text-2xl font-semibold text-gray-900 mb-6">Что вы получаете</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="p-4 border border-gray-200 rounded-lg">
              <h3 class="text-lg font-medium text-gray-900 mb-2">Прозрачность отдела продаж</h3>
              <p class="text-gray-700">Анализируйте все коммуникации с клиентами и находите точки роста</p>
            </div>
            <div class="p-4 border border-gray-200 rounded-lg">
              <h3 class="text-lg font-medium text-gray-900 mb-2">Умный анализ</h3>
              <p class="text-gray-700">Автоматически проверяем звонки по вашим чек-листам и скриптам</p>
            </div>
            <div class="p-4 border border-gray-200 rounded-lg">
              <h3 class="text-lg font-medium text-gray-900 mb-2">Рост KPI</h3>
              <p class="text-gray-700">Повышаете конверсию каждого менеджера без увеличения штата и затрат на ФОТ</p>
            </div>
            <div class="p-4 border border-gray-200 rounded-lg">
              <h3 class="text-lg font-medium text-gray-900 mb-2">Тестирование гипотез</h3>
              <p class="text-gray-700">Творите A/B тесты и наблюдайте результаты в реальном времени</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'default',
  middleware: ['authenticated']
})
</script>

<style scoped>
/* Additional custom styles can be added here if needed */
</style>
