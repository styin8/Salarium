import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    username: '',
  }),
  actions: {
    setToken(t) {
      this.token = t
      localStorage.setItem('token', t)
    },
    logout() {
      this.token = ''
      localStorage.removeItem('token')
    },
    setUsername(name) {
      this.username = name
    },
  },
})