import { useAuthStore } from "@/stores"

export default defineNuxtRouteMiddleware((to, from) => {
  const authStore = useAuthStore()
  const routes = ["/login", "/join", "/recover-password", "/reset-password", "/about"]
  if (!authStore.loggedIn) {
    if (routes.includes(to.path)) return // разрешаем доступ к публичным маршрутам
    else return navigateTo("/login") // перенаправляем на логин для защищенных маршрутов
  }
})