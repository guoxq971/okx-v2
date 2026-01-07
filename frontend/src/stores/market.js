import { defineStore } from 'pinia'
import axios from 'axios'
import { ref, computed } from 'vue'

// Configure Axios Base URL
// In development, Vite proxy handles '/api'.
// In production, we need VITE_API_BASE_URL env var or it defaults to same origin (which might be wrong if backend is elsewhere).
// But usually for simple deploy, we want explicit control.
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || ''
if (apiBaseUrl) {
    axios.defaults.baseURL = apiBaseUrl
}

export const useMarketStore = defineStore('market', () => {
  const tickers = ref([])
  const instruments = ref([])
  const loading = ref(false)
  const favorites = ref(JSON.parse(localStorage.getItem('okx_favorites') || '[]'))
  const accountBalance = ref({})
  const positions = ref([])
  const pendingOrders = ref([])
  const historyOrders = ref([])

  const selectedSymbol = ref('BTC-USDT')
  let pollingInterval = null

  const fetchTickers = async (instType = 'SPOT') => {
    // loading.value = true // Remove loading flicker for polling
    try {
      const response = await axios.get(`/api/tickers?instType=${instType}`)
      // console.log('Tickers API Response:', response.data) // Debug log
      const data = Array.isArray(response.data) ? response.data : (response.data.data || [])
      
      if (Array.isArray(data)) {
          tickers.value = data.map(t => ({
            ...t,
            tag: instType,
            isFavorite: favorites.value.includes(t.instId)
          }))
      } else {
          console.error('Unexpected API response structure:', response.data)
      }
    } catch (error) {
      console.error('Failed to fetch tickers:', error)
    } finally {
      loading.value = false
    }
  }

  const startPolling = () => {
      if (pollingInterval) return
      // Initial fetch based on current tickers tag or default
      fetchTickers(tickers.value[0]?.tag || 'SWAP') // Default to SWAP
      
      pollingInterval = setInterval(() => {
          // We need to know which instType is currently active to poll correct data
          // But store doesn't track active tab, the component does.
          // However, tickers array has 'tag' property we added.
          const currentType = tickers.value[0]?.tag || 'SWAP'
          fetchTickers(currentType)
          fetchBalance()
          fetchPositions()
          fetchOrders()
      }, 3000)
  }

  const stopPolling = () => {
      if (pollingInterval) {
          clearInterval(pollingInterval)
          pollingInterval = null
      }
  }

  const toggleFavorite = (instId) => {
    if (favorites.value.includes(instId)) {
      favorites.value = favorites.value.filter(id => id !== instId)
    } else {
      favorites.value.push(instId)
    }
    localStorage.setItem('okx_favorites', JSON.stringify(favorites.value))
    
    // Update tickers local state
    const t = tickers.value.find(t => t.instId === instId)
    if (t) {
      t.isFavorite = favorites.value.includes(instId)
    }
  }

  const fetchBalance = async () => {
    try {
      const response = await axios.get('/api/balance')
      console.log('Balance API Response:', response.data) // Debug log
      accountBalance.value = response.data
    } catch (error) {
      console.error('Failed to fetch balance:', error)
    }
  }
  
  const fetchPositions = async () => {
    try {
      const response = await axios.get('/api/positions')
      positions.value = response.data
    } catch (error) {
       console.error('Failed to fetch positions:', error)
    }
  }

  const fetchOrders = async () => {
    try {
      // Fetch both pending and history
      // Remove hardcoded instType=SWAP for pending to ensure we get ALL types (Spot + Swap + Algo)
      // Since backend now handles merging and default behavior allows all if not specified.
      // For history, we still default to SWAP as it's often huge if unbounded, but user might want all?
      // Let's keep SWAP for history for now to match user's contract focus, but open pending to all.
      const [pendingRes, historyRes] = await Promise.all([
        axios.get('/api/orders/pending'), 
        axios.get('/api/orders/history?instType=SWAP')
      ])
      console.log('Pending Orders API Response:', pendingRes.data) // Debug Log
      console.log('History Orders API Response:', historyRes.data) // Debug Log
      
      pendingOrders.value = Array.isArray(pendingRes.data) ? pendingRes.data : []
      historyOrders.value = Array.isArray(historyRes.data) ? historyRes.data : []
    } catch (error) {
      console.error('Failed to fetch orders:', error)
    }
  }

  return {
    tickers,
    instruments,
    loading,
    favorites,
    accountBalance,
    positions,
    pendingOrders,
    historyOrders,
    selectedSymbol,
    fetchTickers,
    toggleFavorite,
    fetchBalance,
    fetchPositions,
    fetchOrders,
    startPolling,
    stopPolling
  }
})
