import { defineStore } from 'pinia'
import api from '../utils/axios'
import { useStatsStore } from './stats'

export const useSalaryStore = defineStore('salary', {
  state: () => ({
    list: [],
    loading: false,
    refreshing: false,
    filters: {
      personId: null,
      year: null,
      month: null,
    },
    _refreshTimer: null,
    _pendingRequests: new Set(),
  }),

  getters: {
    filteredList(state) {
      let filtered = [...state.list]
      
      if (state.filters.year) {
        filtered = filtered.filter(item => item.year === state.filters.year)
      }
      
      if (state.filters.month) {
        filtered = filtered.filter(item => item.month === state.filters.month)
      }
      
      filtered.sort((a, b) => {
        if (a.year !== b.year) return b.year - a.year
        return b.month - a.month
      })
      
      return filtered
    },

    stats(state) {
      const list = this.filteredList
      if (list.length === 0) return { total: 0, average: 0, latest: 0 }
      
      const total = list.reduce((sum, item) => sum + (item.net_income || 0), 0)
      const average = total / list.length
      const latest = list.length > 0 ? list[list.length - 1].net_income || 0 : 0
      
      return { total, average, latest }
    },

    yearOptions(state) {
      const years = [...new Set(state.list.map(item => item.year))].sort((a, b) => b - a)
      return years
    },
  },

  actions: {
    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
    },

    setPersonId(personId) {
      this.filters.personId = personId
    },

    setYear(year) {
      this.filters.year = year
    },

    setMonth(month) {
      this.filters.month = month
    },

    clearFilters() {
      this.filters.year = null
      this.filters.month = null
    },

    async fetchList(personId) {
      if (!personId) return
      
      this.loading = true
      try {
        const { data } = await api.get('/salaries/', { 
          params: { person_id: personId } 
        })
        this.list = data
        this.filters.personId = personId
      } catch (error) {
        console.error('Failed to fetch salary list:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async refreshList() {
      if (!this.filters.personId) return
      
      if (this._refreshTimer) {
        clearTimeout(this._refreshTimer)
      }

      this._refreshTimer = setTimeout(async () => {
        this.refreshing = true
        try {
          const { data } = await api.get('/salaries/', { 
            params: { person_id: this.filters.personId } 
          })
          this.list = data
        } catch (error) {
          console.error('Failed to refresh salary list:', error)
        } finally {
          this.refreshing = false
        }
      }, 100)
    },

    async createSalary(personId, payload) {
      const requestId = Date.now()
      
      if (this._pendingRequests.has('create')) {
        throw new Error('已有创建操作在进行中')
      }
      
      this._pendingRequests.add('create')
      
      try {
        const { data } = await api.post(`/salaries/${personId}`, payload)
        
        // Optimistic update: insert at the beginning
        this.list.unshift(data)
        
        // Trigger stats refresh
        const statsStore = useStatsStore()
        statsStore.refreshAll()
        
        // Refresh to ensure consistency
        await this.refreshList()
        
        return data
      } finally {
        this._pendingRequests.delete('create')
      }
    },

    async updateSalary(salaryId, payload) {
      const requestId = `update-${salaryId}`
      
      if (this._pendingRequests.has(requestId)) {
        throw new Error('已有更新操作在进行中')
      }
      
      this._pendingRequests.add(requestId)
      
      try {
        const { data } = await api.put(`/salaries/${salaryId}`, payload)
        
        // Optimistic update: update locally
        const index = this.list.findIndex(item => item.id === salaryId)
        if (index !== -1) {
          this.list[index] = data
        }
        
        // Trigger stats refresh
        const statsStore = useStatsStore()
        statsStore.refreshAll()
        
        // Refresh to ensure consistency
        await this.refreshList()
        
        return data
      } finally {
        this._pendingRequests.delete(requestId)
      }
    },

    async deleteSalary(salaryId) {
      const requestId = `delete-${salaryId}`
      
      if (this._pendingRequests.has(requestId)) {
        throw new Error('已有删除操作在进行中')
      }
      
      this._pendingRequests.add(requestId)
      
      try {
        await api.delete(`/salaries/${salaryId}`)
        
        // Optimistic update: remove locally
        this.list = this.list.filter(item => item.id !== salaryId)
        
        // Trigger stats refresh
        const statsStore = useStatsStore()
        statsStore.refreshAll()
        
        // Refresh to ensure consistency
        await this.refreshList()
      } finally {
        this._pendingRequests.delete(requestId)
      }
    },

    reset() {
      this.list = []
      this.filters = {
        personId: null,
        year: null,
        month: null,
      }
      this._pendingRequests.clear()
      if (this._refreshTimer) {
        clearTimeout(this._refreshTimer)
        this._refreshTimer = null
      }
    },
  },
})
