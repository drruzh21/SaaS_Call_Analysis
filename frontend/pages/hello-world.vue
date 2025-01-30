<template>
  <div class="min-h-screen flex flex-col">
    <!-- Using existing layout components -->
    <div class="flex-grow flex flex-col items-center justify-center px-4">
      <h1 class="text-4xl font-bold mb-8 text-center">Hello World</h1>

      <!-- Simple form with vanilla JS handling -->
      <form id="dataForm" class="w-full max-w-md">
        <div class="mb-4">
          <label for="inputData" class="block text-sm font-medium text-gray-700 mb-2">
            Enter your data
          </label>
          <input
            type="text"
            id="inputData"
            name="inputData"
            class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Type something..."
          />
        </div>
        <button
          type="submit"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Submit
        </button>
      </form>

      <!-- Response message -->
      <div id="responseMessage" class="mt-4 text-center hidden">
        <p class="text-green-600">Data sent successfully!</p>
      </div>
    </div>
  </div>
</template>

<script>
// Disable Options API since we're not using Vue features
export default {
  name: 'HelloWorld',
}
</script>

<script setup>
import { onMounted } from 'vue'

// Setup the form handler when the component is mounted
onMounted(() => {
  const form = document.getElementById('dataForm')
  const responseMessage = document.getElementById('responseMessage')

  form.addEventListener('submit', async (e) => {
    e.preventDefault()

    const inputData = document.getElementById('inputData').value

    try {
      // Using the correct backend URL and GET method
      const response = await fetch('http://localhost:8000/api/v1/users/data', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          // Get the token from localStorage if needed
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Response:', data) // Add logging to see the response
        responseMessage.classList.remove('hidden')
        form.reset()

        // Hide the message after 3 seconds
        setTimeout(() => {
          responseMessage.classList.add('hidden')
        }, 3000)
      } else {
        throw new Error('Failed to send data')
      }
    } catch (error) {
      console.error('Error:', error)
      alert('Failed to send data. Please try again.')
    }
  })
})
</script>
