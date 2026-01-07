<template>
  <div class="watchlist-grid">
    <div class="filters">
      <a-radio-group v-model:value="activeFilter" button-style="solid" size="middle" @change="handleFilterChange">
        <a-radio-button value="SPOT">现货</a-radio-button>
        <a-radio-button value="SWAP">永续</a-radio-button>
      </a-radio-group>
      
      <div class="search-box" style="display: flex; align-items: center;">
          <span style="font-size: 12px; color: #666; margin-right: 8px;">{{ displayTickers.length }}/{{ store.tickers.length }}</span>
          <a-input v-model:value="searchQuery" placeholder="搜索币种" size="small" allowClear>
              <template #prefix><SearchOutlined /></template>
          </a-input>
      </div>
      
      <div class="sort-controls" style="margin-left: 8px;">
         <a-button size="small" @click="showSortModal">
             排序 <FilterOutlined />
         </a-button>
         <a-button size="small" @click="resetFilters" style="margin-left: 4px;" title="重置筛选">
             <ReloadOutlined />
         </a-button>
      </div>
    </div>
    
    <div class="grid-content">
      <a-dropdown :trigger="['contextmenu']" v-for="item in displayTickers" :key="item.instId">
        <div 
          class="grid-item" 
          :class="{ active: store.selectedSymbol === item.instId, 'held-item': isHeld(item.instId) }"
          @click="selectSymbol(item.instId)"
          @contextmenu="selectSymbol(item.instId)"
        >
          <div class="grid-item-header">
               <div class="coin-info">
                 <div class="icon-wrapper">
                     <img :src="getIconUrl(item.instId)" :data-symbol="item.instId.split('-')[0].toLowerCase()" class="coin-icon" :class="{ 'held-border': isHeld(item.instId) }" @error="handleImageError" />
                     <div v-if="isHeld(item.instId)" class="held-indicator"></div>
                 </div>
                 <span class="symbol-text">{{ formatSymbol(item.instId) }}</span>
             </div>
               <StarFilled v-if="item.isFavorite" style="color: gold;" @click.stop="store.toggleFavorite(item.instId)" />
               <StarOutlined v-else style="color: #444;" @click.stop="store.toggleFavorite(item.instId)" />
          </div>
          
          <div class="grid-item-price" :class="getPriceColor(item)">
              {{ formatPrice(item.last) }}
          </div>
          
          <div class="grid-item-change" :class="getChangeColor(item)">
               {{ formatChange(item) }}%
          </div>
          
          <div class="grid-item-vol">
              Vol: {{ formatVol(item.vol24h) }}
          </div>
          <div class="grid-item-cap">
              Turnover: {{ formatVol(item.volCcy24h) }}
          </div>
        </div>
        <template #overlay>
          <a-menu>
            <a-menu-item @click="openOkx(item.instId)">打开 OKX 官网</a-menu-item>
            <a-menu-item @click="openOkxEmbed(item.instId)">打开 OKX 内嵌</a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
    </div>

    <a-modal 
        v-model:open="embedModalVisible" 
        :title="embedTitle" 
        width="90%" 
        style="top: 20px"
        :footer="null"
        :bodyStyle="{ padding: 0, height: '80vh' }"
    >
        <iframe 
            v-if="embedUrl" 
            :src="embedUrl" 
            width="100%" 
            height="100%" 
            frameborder="0" 
            allowfullscreen
        ></iframe>
    </a-modal>

    <a-modal v-model:open="sortModalVisible" title="列表配置 (筛选 & 排序)" width="600px" @ok="sortModalVisible = false">
        <!-- Filter Section -->
        <div class="config-section">
            <h3>筛选规则</h3>
            <div style="margin-bottom: 10px;">
                <a-radio-group v-model:value="filterLogic" size="small">
                    <a-radio-button value="AND">满足所有 (AND)</a-radio-button>
                    <a-radio-button value="OR">满足任一 (OR)</a-radio-button>
                </a-radio-group>
            </div>
            
            <div class="rule-list">
                <div class="rule-item" v-for="(rule, index) in filterRules" :key="'filter'+index">
                    <a-checkbox v-model:checked="rule.enabled" style="margin-right: 8px;" />
                    <a-select v-model:value="rule.field" style="width: 120px" size="small">
                        <a-select-option value="vol24h">成交量</a-select-option>
                        <a-select-option value="change24h">涨跌幅(%)</a-select-option>
                        <a-select-option value="amp24h">24H振幅(%)</a-select-option>
                        <a-select-option value="last">最新价</a-select-option>
                    </a-select>
                    <a-select v-model:value="rule.op" style="width: 80px; margin: 0 8px;" size="small">
                        <a-select-option value="gt">大于</a-select-option>
                        <a-select-option value="lt">小于</a-select-option>
                    </a-select>
                    <a-input v-model:value="rule.value" placeholder="数值" style="width: 100px" size="small" />
                    <a-button type="text" danger size="small" @click="removeFilterRule(index)">
                        <DeleteOutlined />
                    </a-button>
                </div>
            </div>
             <a-button type="dashed" block size="small" @click="addFilterRule">
                + 添加筛选条件
            </a-button>
        </div>

        <a-divider />

        <!-- Sort Section -->
        <div class="config-section">
            <h3>排序规则 (优先级从上到下)</h3>
            <div class="rule-list">
            <div class="rule-item" v-for="(rule, index) in sortRules" :key="'sort'+index">
                <span class="rule-index">{{ index + 1 }}.</span>
                <a-select v-model:value="rule.field" style="width: 120px" size="small">
                    <a-select-option value="change24h">涨跌幅</a-select-option>
                    <a-select-option value="vol24h">成交量</a-select-option>
                    <a-select-option value="last">最新价</a-select-option>
                    <a-select-option value="instId">名称</a-select-option>
                    <a-select-option value="amp24h">24H振幅</a-select-option>
                </a-select>
                <a-radio-group v-model:value="rule.dir" button-style="solid" style="margin-left: 10px" size="small">
                    <a-radio-button value="asc">升序</a-radio-button>
                    <a-radio-button value="desc">降序</a-radio-button>
                </a-radio-group>
                <a-button type="text" danger @click="removeSortRule(index)" v-if="sortRules.length > 1" size="small">
                    <DeleteOutlined />
                </a-button>
            </div>
            </div>
            <a-button type="dashed" block size="small" @click="addSortRule" v-if="sortRules.length < 3">
                + 添加排序条件
            </a-button>
        </div>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useMarketStore } from '../stores/market'
import { SearchOutlined, StarOutlined, StarFilled, FilterOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons-vue'

const store = useMarketStore()
const activeFilter = ref('SWAP') // Default to SWAP

const selectSymbol = (instId) => {
    if (store.selectedSymbol === instId) {
        store.selectedSymbol = '' // Deselect if already selected
    } else {
        store.selectedSymbol = instId
    }
}

const handleFilterChange = (e) => {
  // e.target.value contains the new value
  // Need to update store or re-fetch
  // But wait, fetchTickers updates store.tickers, which is what we display.
  // We need to make sure we actually call fetchTickers when this changes.
  store.fetchTickers(activeFilter.value)
  // Also clear search query on tab change? Maybe optional.
}
const searchQuery = ref('')
const sortModalVisible = ref(false)
const embedModalVisible = ref(false)
const embedUrl = ref('')
const embedTitle = ref('')

// Default sort rules: 1. Volume DESC
const sortRules = reactive([
    { field: 'vol24h', dir: 'desc' }
])

const filterRules = reactive([])
const filterLogic = ref('AND')

const addFilterRule = () => {
    filterRules.push({ field: 'vol24h', op: 'gt', value: '', enabled: true })
}

const removeFilterRule = (index) => {
    filterRules.splice(index, 1)
}

const isHeld = (instId) => {
    return store.positions.some(p => p.instId === instId)
}

const addSortRule = () => {
    sortRules.push({ field: 'change24h', dir: 'desc' })
}

const removeSortRule = (index) => {
    sortRules.splice(index, 1)
}

const showSortModal = () => {
    sortModalVisible.value = true
}

const resetFilters = () => {
    filterRules.splice(0, filterRules.length)
    sortRules.splice(0, sortRules.length)
    sortRules.push({ field: 'vol24h', dir: 'desc' })
    searchQuery.value = ''
    store.fetchTickers(activeFilter.value)
}

const displayTickers = computed(() => {
  let list = [...store.tickers] // Copy array
  
  // Filter by Search
  if (searchQuery.value) {
      const q = searchQuery.value.toUpperCase().trim()
      const keywords = q.split(/[\s,]+/).filter(k => k) // Split by space or comma
      
      if (keywords.length > 0) {
          list = list.filter(t => {
              const rawId = t.instId
              const cleanId = rawId.replace('-', '')
              // Match ANY keyword (OR logic for search terms)
              return keywords.some(k => rawId.includes(k) || cleanId.includes(k))
          })
      }
  }

      // Filter by Search
      // ... search logic ...
  
      // Ensure we don't have a stray filter rule blocking everything
      // If list is filtered down to 1 item unexpectedly, it might be due to filter rules
      // or sort logic returning NaN.
      
      // Filter by Advanced Rules
      if (filterRules.length > 0) {
          list = list.filter(t => {
              // Calculate derived values for filtering
              const values = {
                  last: parseFloat(t.last || 0),
                  vol24h: parseFloat(t.vol24h || 0),
                  change24h: parseFloat(t.open24h) ? ((parseFloat(t.last) - parseFloat(t.open24h)) / parseFloat(t.open24h) * 100) : 0,
                  amp24h: parseFloat(t.open24h) ? ((parseFloat(t.high24h) - parseFloat(t.low24h)) / parseFloat(t.open24h) * 100) : 0
              }
    
              const results = filterRules.map(rule => {
                  if (!rule.enabled) return true // Ignore disabled rules
                  // If rule value is empty, ignore it
                  if (rule.value === '' || rule.value === null || rule.value === undefined) return true
                  
                  const val = values[rule.field]
                  const limit = parseFloat(rule.value)
                  if (isNaN(limit)) return true
                  
                  if (rule.op === 'gt') return val > limit
                  if (rule.op === 'lt') return val < limit
                  return true
              })
    
              if (filterLogic.value === 'AND') {
                  return results.every(r => r)
              } else {
                  return results.some(r => r)
              }
          })
      }
  
  // Multi-level Sort
  list.sort((a, b) => {
      // 0. Favorites ALWAYS first
      if (a.isFavorite && !b.isFavorite) return -1
      if (!a.isFavorite && b.isFavorite) return 1
      
      // Iterate through sort rules
      for (const rule of sortRules) {
          const field = rule.field
          const dir = rule.dir
          
          let valA = a[field]
          let valB = b[field]
          
          // Numeric fields
          if (['last', 'change24h', 'vol24h', 'open24h', 'high24h', 'low24h', 'amp24h'].includes(field)) {
               // Pre-calculate amp24h if needed, since it's not in raw data usually
               if (field === 'amp24h') {
                   const openA = parseFloat(a.open24h || 0)
                   valA = openA ? ((parseFloat(a.high24h) - parseFloat(a.low24h)) / openA) : 0
                   const openB = parseFloat(b.open24h || 0)
                   valB = openB ? ((parseFloat(b.high24h) - parseFloat(b.low24h)) / openB) : 0
               } else if (field === 'change24h') {
                   // Calculate change % for sorting
                   const openA = parseFloat(a.open24h || 0)
                   const lastA = parseFloat(a.last || 0)
                   valA = openA ? ((lastA - openA) / openA) : -9999
                   
                   const openB = parseFloat(b.open24h || 0)
                   const lastB = parseFloat(b.last || 0)
                   valB = openB ? ((lastB - openB) / openB) : -9999
               } else {
                   valA = parseFloat(valA || 0)
                   valB = parseFloat(valB || 0)
               }
          }
          
          // Handle NaN safely
          if (isNaN(valA)) valA = -Infinity
          if (isNaN(valB)) valB = -Infinity

          if (valA === valB) continue
          
          if (dir === 'asc') {
              return valA > valB ? 1 : -1
          } else {
              return valA < valB ? 1 : -1
          }
      }
      return 0
  })
  
  return list
})

const getIconUrl = (instId) => {
  const symbol = instId.split('-')[0].toLowerCase()
  // Strategy: OKX CDN -> Github -> CoinCap -> Fallback
  // OKX CDN usually uses uppercase for some, lowercase for others. Let's try lowercase first.
  return `https://static.okx.com/cdn/oksupport/asset/currency/icon/${symbol}.png`
}

const handleImageError = (e) => {
  const symbol = e.target.getAttribute('data-symbol')
  const currentSrc = e.target.src
  
  // Strategy 1: OKX -> Github
  if (currentSrc.includes('static.okx.com')) {
       e.target.src = `https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/${symbol}.png`
  } 
  // Strategy 2: Github -> Coincap
  else if (currentSrc.includes('githubusercontent')) {
       e.target.src = `https://assets.coincap.io/assets/icons/${symbol}@2x.png`
  }
  // Strategy 3: Coincap -> Hide
  else if (currentSrc.includes('coincap')) {
       e.target.style.display = 'none'
  }
}

const openOkx = (instId) => {
    // OKX URL logic
    // Spot: https://www.okx.com/trade-spot/btc-usdt
    // Swap: https://www.okx.com/trade-swap/btc-usdt-swap
    if (!instId) return
    const isSwap = instId.includes('-SWAP')
    const type = isSwap ? 'trade-swap' : 'trade-spot'
    const url = `https://www.okx.com/${type}/${instId.toLowerCase()}`
    window.open(url, '_blank')
}

const openOkxEmbed = (instId) => {
    if (!instId) return
    // Standard trading page often blocks iframe. 
    // Trying TradingView chart embed if possible, but OKX specific:
    // https://www.okx.com/chart/embed/btc-usdt
    // Or maybe we can use a third party chart if OKX blocks it?
    // Let's try the chart specific URL which is more likely to allow embedding.
    const symbol = instId.replace('-SWAP', '') // For chart, usually just BTC-USDT
    // OKX doesn't have a public documented embed URL that is guaranteed to work everywhere due to X-Frame-Options.
    // However, we can try to use the mobile web view or a specific chart path.
    // Alternative: Use TradingView widget for the modal.
    // Let's try a common workaround or just fallback to TradingView for the embed since it's reliable.
    
    // TradingView Widget URL construction
    // Symbol format for TV: "OKX:BTCUSDT.P" for swap, "OKX:BTCUSDT" for spot
    let tvSymbol = 'OKX:' + instId.replace('-', '').replace('-', '') // Remove all dashes first
    if (instId.includes('-SWAP')) {
        tvSymbol = 'OKX:' + instId.split('-')[0] + instId.split('-')[1] + '.P' // e.g. OKX:BTCUSDT.P
    } else {
        tvSymbol = 'OKX:' + instId.replace('-', '') // e.g. OKX:BTCUSDT
    }
    
    const url = `https://s.tradingview.com/widgetembed/?frameElementId=tradingview_76d87&symbol=${tvSymbol}&interval=D&hidesidetoolbar=1&hidetoptoolbar=1&symboledit=1&saveimage=1&toolbarbg=F1F3F6&studies=[]&hideideas=1&theme=Dark&style=1&timezone=Etc%2FUTC&studies_overrides={}&overrides={}&enabled_features=[]&disabled_features=[]&locale=en&utm_source=localhost&utm_medium=widget&utm_campaign=chart&utm_term=${tvSymbol}`
    
    embedUrl.value = url
    embedTitle.value = `Chart - ${instId}`
    embedModalVisible.value = true
}

const formatSymbol = (instId) => {
  if (!instId) return ''
  return instId.replace('-USDT', '').replace('-USD', '').replace('-SWAP', '')
}

const formatPrice = (price) => {
  return parseFloat(price).toString()
}

const formatVol = (vol) => {
    const v = parseFloat(vol)
    if (v > 1000000) return (v / 1000000).toFixed(2) + 'M'
    if (v > 1000) return (v / 1000).toFixed(2) + 'K'
    return v.toFixed(2)
}

const getChangeColor = (record) => {
     const change = parseFloat(record.last) - parseFloat(record.open24h)
     return change >= 0 ? 'text-green' : 'text-red'
}

const getPriceColor = (record) => {
    return getChangeColor(record)
}

const formatChange = (record) => {
  const open = parseFloat(record.open24h)
  const last = parseFloat(record.last)
  if (!open) return '0.00'
  return ((last - open) / open * 100).toFixed(2)
}

onMounted(() => {
  store.fetchTickers('SWAP')
})
</script>

<style scoped>
.watchlist-grid {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1a1a1a;
  padding: 8px;
}
.filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.search-box {
    width: 150px;
}
.grid-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  padding-right: 14px; /* Add extra padding for scrollbar */
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
  align-content: start;
}
.grid-item {
  background: #242424;
  border-radius: 4px;
  padding: 10px;
  cursor: pointer;
  border: 1px solid #333;
  transition: all 0.2s;
}
.grid-item:hover {
  background-color: #2a2a2a;
  border-color: #555;
}
.grid-item.active {
  border: 1px solid #42b883 !important;
  background-color: rgba(66, 184, 131, 0.15) !important;
}
.rule-list {
    margin-bottom: 10px;
}
.rule-item {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
    background: #242424;
    padding: 6px;
    border-radius: 4px;
}
.rule-index {
    margin-right: 8px;
    color: #888;
    width: 20px;
}
.held-border {
    border: 2px solid #42b883;
    box-sizing: border-box;
}
.icon-wrapper {
    position: relative;
    margin-right: 6px;
    width: 18px;
    height: 18px;
}
.coin-icon { width: 100%; height: 100%; border-radius: 50%; display: block; }
.held-item {
    background-color: #242a26;
    background-image: repeating-linear-gradient(45deg, rgba(66, 184, 131, 0.04) 0px, rgba(66, 184, 131, 0.04) 10px, transparent 10px, transparent 20px);
    /* No border for held items by default, only pattern */
    border: 1px solid transparent; 
}
/* Retain pattern on hover for held items */
.held-item:hover {
    background-color: #2e3630;
}

/* Remove duplicate active block and clean up */

/* When item is BOTH held and active:
   1. Keep Vue Green border (from active)
   2. Keep Light Green background (from active)
   3. OVERLAY the held pattern on top
*/
.grid-item.active.held-item {
    border: 1px solid #42b883 !important;
    background-color: rgba(66, 184, 131, 0.2) !important;
    background-image: repeating-linear-gradient(45deg, rgba(66, 184, 131, 0.04) 0px, rgba(66, 184, 131, 0.04) 10px, transparent 10px, transparent 20px) !important;
}

.grid-item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
}
.coin-info {
    display: flex;
    align-items: center;
}
.symbol-text { font-weight: bold; font-size: 13px; color: #eee; }

.grid-item-price {
    font-size: 15px;
    font-weight: bold;
    margin-bottom: 4px;
}
.grid-item-change {
    font-size: 12px;
}
.grid-item-vol {
    font-size: 11px;
    color: #666;
    margin-top: 4px;
}
.grid-item-cap {
    font-size: 11px;
    color: #888;
    margin-top: 2px;
}

.text-green { color: #42b883; }
.text-red { color: #ff4d4f; }
</style>
