<template>
  <div class="account-panel">
    <div class="panel-header">
       <div class="tabs">
           <div class="tab" :class="{ active: activeTab === 'positions' }" @click="switchTab('positions')">当前持仓</div>
           <div class="tab" :class="{ active: activeTab === 'pending' }" @click="switchTab('pending')">当前委托</div>
           <div class="tab" :class="{ active: activeTab === 'history' }" @click="switchTab('history')">历史委托</div>
       </div>
       <div class="account-summary">
           <span>总权益: <span class="val">{{ formatAmount(store.accountBalance.totalEq) }}</span> USD</span>
           <span>可用: <span class="val">{{ formatAmount(getAvailableUsdt) }}</span> USD</span>
       </div>
    </div>
    
    <div class="panel-content">
        <!-- Positions Table -->
        <a-table 
            v-if="activeTab === 'positions'"
            :dataSource="store.positions" 
            :columns="positionColumns" 
            rowKey="instId" 
            size="small" 
            :pagination="false"
            :scroll="{ y: 200 }"
        >
             <template #bodyCell="{ column, record }">
                 <template v-if="column.key === 'instId'">
                     <div class="coin-info-cell">
                         <div class="icon-wrapper">
                             <img :src="getIconUrl(record.instId)" :data-symbol="record.instId.split('-')[0].toLowerCase()" class="coin-icon" @error="handleImageError" />
                         </div>
                         <span class="symbol-text">{{ formatSymbol(record.instId) }}</span>
                     </div>
                 </template>
                 <template v-else-if="column.key === 'upl'">
                     <div class="pnl-cell">
                         <span :class="getPnlColor(record.upl)">{{ formatAmount(record.upl) }}</span>
                         <span :class="getPnlColor(record.upl)" class="pnl-percent">
                             ({{ calculatePnlPercent(record) }}%)
                         </span>
                     </div>
                 </template>
                 <template v-else-if="column.key === 'lever'">
                     <span>{{ record.lever }}x</span>
                 </template>
                 <template v-else-if="column.key === 'posSide'">
                     <span :class="record.posSide === 'long' ? 'text-green' : 'text-red'">
                         {{ record.posSide === 'long' ? '多' : (record.posSide === 'short' ? '空' : '净') }}
                     </span>
                 </template>
                 <template v-else-if="column.key === 'cTime'">
                     {{ formatTime(record.cTime) }}
                 </template>
                 <template v-else-if="column.key === 'mgn'">
                    {{ formatAmount(record.mgn || record.imr) }}
                </template>
                <template v-else-if="column.key === 'mgnRatio'">
                    {{ formatMgnRatio(record.mgnRatio) }}
                </template>
                <template v-else-if="column.key === 'tpSl'">
                    <span class="tp-sl-cell">
                        <span class="text-green" v-if="record.tpTriggerPx">{{ record.tpTriggerPx }}</span>
                        <span v-else>--</span>
                        /
                        <span class="text-red" v-if="record.slTriggerPx">{{ record.slTriggerPx }}</span>
                        <span v-else>--</span>
                    </span>
                </template>
                <template v-else-if="column.key === 'avgPx'">
                    {{ formatPrice4(record.avgPx) }}
                </template>
                <template v-else-if="column.key === 'last'">
                    {{ formatPrice4(record.last) }}
                </template>
            </template>
        </a-table>

        <!-- Pending Orders Table -->
        <div v-if="activeTab === 'pending'" class="sub-tabs-container">
            <div class="sub-tabs">
                <div class="sub-tab" :class="{ active: pendingSubTab === 'limit' }" @click="pendingSubTab = 'limit'">限价/市价</div>
                <div class="sub-tab" :class="{ active: pendingSubTab === 'algo' }" @click="pendingSubTab = 'algo'">止盈止损</div>
            </div>
        </div>

        <a-table 
            v-if="activeTab === 'pending'"
            :dataSource="displayPendingOrders" 
            :columns="currentPendingColumns" 
            rowKey="ordId" 
            size="small" 
            :pagination="false"
            :scroll="{ y: 160 }"
        >
             <template #bodyCell="{ column, record }">
                 <template v-if="column.key === 'instId'">
                     <div class="coin-info-cell">
                         <div class="icon-wrapper">
                             <img :src="getIconUrl(record.instId)" :data-symbol="record.instId.split('-')[0].toLowerCase()" class="coin-icon" @error="handleImageError" />
                         </div>
                         <span class="symbol-text">{{ formatSymbol(record.instId) }}</span>
                     </div>
                 </template>
                 <template v-else-if="column.key === 'side'">
                     <span :class="record.side === 'buy' ? 'text-green' : 'text-red'">
                         {{ getSideText(record) }}
                     </span>
                 </template>
                 <template v-else-if="column.key === 'cTime'">
                     {{ formatTime(record.cTime) }}
                 </template>
                 <!-- Algo Specific Columns -->
                 <template v-else-if="column.key === 'triggerPx'">
                     {{ record.triggerPx || record.tpTriggerPx || record.slTriggerPx || '--' }}
                 </template>
                 <template v-else-if="column.key === 'ordType'">
                     {{ getOrdTypeText(record.ordType) }}
                 </template>
             </template>
        </a-table>

        <!-- History Orders Table -->
        <a-table 
            v-if="activeTab === 'history'"
            :dataSource="store.historyOrders" 
            :columns="orderColumns" 
            rowKey="ordId" 
            size="small" 
            :pagination="false"
            :scroll="{ y: 200 }"
        >
             <template #bodyCell="{ column, record }">
                 <template v-if="column.key === 'side'">
                     <span :class="record.side === 'buy' ? 'text-green' : 'text-red'">
                         {{ record.side === 'buy' ? '买入' : '卖出' }}
                     </span>
                 </template>
                 <template v-else-if="column.key === 'state'">
                     <a-tag :color="getOrderStateColor(record.state)">{{ getOrderStateText(record.state) }}</a-tag>
                 </template>
                 <template v-else-if="column.key === 'cTime'">
                     {{ formatTime(record.cTime) }}
                 </template>
             </template>
        </a-table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useMarketStore } from '../stores/market'
import dayjs from 'dayjs'

const store = useMarketStore()
const activeTab = ref('positions')
const pendingSubTab = ref('limit') // limit, algo

const positionColumns = [
    { title: '币种', dataIndex: 'instId', key: 'instId', width: 140 },
    { title: '方向', dataIndex: 'posSide', key: 'posSide', width: 80 },
    { title: '杠杆', dataIndex: 'lever', key: 'lever', width: 80 },
    { title: '持仓量', dataIndex: 'pos', key: 'pos', width: 100 },
    { title: '开仓均价', dataIndex: 'avgPx', key: 'avgPx', width: 100 },
    { title: '当前价格', dataIndex: 'last', key: 'last', width: 100 },
    { title: '未实现盈亏 (收益率)', dataIndex: 'upl', key: 'upl', width: 200 },
    { title: '保证金', dataIndex: 'mgn', key: 'mgn', width: 100 },
    { title: '维持保证金率', dataIndex: 'mgnRatio', key: 'mgnRatio', width: 100 },
    { title: '止盈/止损', dataIndex: 'tpSl', key: 'tpSl', width: 150 },
    { title: '创建时间', dataIndex: 'cTime', key: 'cTime', width: 150 },
]

const orderColumns = [
    { title: '币种', dataIndex: 'instId', key: 'instId', width: 140 },
    { title: '方向', dataIndex: 'side', key: 'side', width: 80 },
    { title: '类型', dataIndex: 'ordType', key: 'ordType', width: 100 },
    { title: '价格', dataIndex: 'px', key: 'px', width: 100 },
    { title: '数量', dataIndex: 'sz', key: 'sz', width: 100 },
    { title: '状态', dataIndex: 'state', key: 'state', width: 100 },
    { title: '创建时间', dataIndex: 'cTime', key: 'cTime', width: 150 },
]

const algoOrderColumns = [
    { title: '币种', dataIndex: 'instId', key: 'instId', width: 140 },
    { title: '方向', dataIndex: 'side', key: 'side', width: 80 },
    { title: '类型', dataIndex: 'ordType', key: 'ordType', width: 100 },
    { title: '触发价格', dataIndex: 'triggerPx', key: 'triggerPx', width: 100 },
    { title: '委托价格', dataIndex: 'ordPx', key: 'ordPx', width: 100 },
    { title: '数量', dataIndex: 'sz', key: 'sz', width: 100 },
    { title: '状态', dataIndex: 'state', key: 'state', width: 100 },
    { title: '创建时间', dataIndex: 'cTime', key: 'cTime', width: 150 },
]

const displayPendingOrders = computed(() => {
    if (activeTab.value !== 'pending') return []
    if (pendingSubTab.value === 'limit') {
        return store.pendingOrders.filter(o => !o.isAlgo)
    } else {
        return store.pendingOrders.filter(o => o.isAlgo)
    }
})

const currentPendingColumns = computed(() => {
    return pendingSubTab.value === 'algo' ? algoOrderColumns : orderColumns
})

const getSideText = (record) => {
    if (record.side === 'buy') return '买入'
    if (record.side === 'sell') return '卖出'
    return record.side
}

const getOrdTypeText = (type) => {
    const map = {
        'limit': '限价',
        'market': '市价',
        'stop': '止盈止损',
        'trigger': '计划委托',
        'oco': '双向止盈止损',
        'conditional': '条件委托',
        'move_order_stop': '移动止盈',
        'twap': 'TWAP'
    }
    return map[type] || type
}

const getIconUrl = (instId) => {
  const symbol = instId.split('-')[0].toLowerCase()
  // Strategy: OKX CDN -> Github -> CoinCap -> Fallback
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

const formatSymbol = (instId) => {
  if (!instId) return ''
  return instId.replace('-USDT', '').replace('-USD', '').replace('-SWAP', '')
}

const getPnlColor = (val) => {
    return parseFloat(val) >= 0 ? 'text-green' : 'text-red'
}

const getAvailableUsdt = computed(() => {
    // Try to find USDT in details
    if (store.accountBalance.details && Array.isArray(store.accountBalance.details)) {
        const usdt = store.accountBalance.details.find(d => d.ccy === 'USDT')
        if (usdt) {
            return usdt.availEq || usdt.cashBal // availEq is usually available equity
        }
    }
    // Fallback to adjEq if no details
    return store.accountBalance.adjEq
})

const switchTab = (tab) => {
    activeTab.value = tab
    // Optional: Refresh data when switching tabs if needed, 
    // though polling handles it generally.
    if (tab === 'pending' || tab === 'history') {
        store.fetchOrders()
    } else if (tab === 'positions') {
        store.fetchPositions()
    }
}
const calculatePnlPercent = (record) => {
    if (record.uplRatio) {
        return (parseFloat(record.uplRatio) * 100).toFixed(2)
    }
    const mgn = parseFloat(record.mgn || record.imr)
    if (!mgn) return '0.00'
    const upl = parseFloat(record.upl)
    return ((upl / mgn) * 100).toFixed(2)
}

const formatPrice4 = (val) => {
    if (!val) return '--'
    const num = parseFloat(val)
    if (isNaN(num)) return val
    
    // For small numbers (e.g. 0.00080512...), keep 4 significant figures? 
    // User asked: "0.000805128130648 = 0.0008051" -> This looks like 7 decimal places? 
    // Or maybe just truncate to 4 significant digits if < 1?
    // "保留后面的4位整数" -> "Keep 4 integers behind"? 
    // Usually means 4 significant digits or fixed decimals. 
    // Example: 0.0008051 -> 4 significant digits.
    
    // Let's implement significant digit logic similar to OKX
    if (num < 1) {
        // Count leading zeros
        const s = num.toFixed(20)
        const match = s.match(/^0\.0*([1-9])/)
        if (match) {
             // For very small numbers, we usually want ~4 significant digits
             return num.toPrecision(4)
        }
        return num.toFixed(4)
    } else if (num < 10) {
        return num.toFixed(4)
    } else {
        return num.toFixed(2)
    }
}

const formatAmount = (val) => {
    if (!val) return '0.00'
    return parseFloat(val).toFixed(2)
}

const formatMgnRatio = (val) => {
    if (!val) return '0.00%'
    return (parseFloat(val) * 100).toFixed(2) + '%'
}

const formatTime = (ts) => {
    if (!ts) return '-'
    return dayjs(parseInt(ts)).format('YYYY-MM-DD HH:mm:ss')
}

const getOrderStateColor = (state) => {
    switch (state) {
        case 'live': return 'processing'
        case 'filled': return 'success'
        case 'canceled': return 'default'
        case 'partially_filled': return 'warning'
        default: return 'default'
    }
}

const getOrderStateText = (state) => {
    switch (state) {
        case 'live': return '等待成交'
        case 'filled': return '完全成交'
        case 'canceled': return '已撤单'
        case 'partially_filled': return '部分成交'
        default: return state
    }
}
</script>

<style scoped>
.sub-tabs-container {
    padding: 0 16px;
    background: #242424;
    border-bottom: 1px solid #333;
}
.sub-tabs {
    display: flex;
    gap: 20px;
}
.sub-tab {
    padding: 8px 0;
    font-size: 12px;
    color: #888;
    cursor: pointer;
    border-bottom: 2px solid transparent;
}
.sub-tab.active {
    color: #42b883;
    border-bottom-color: #42b883;
}
.account-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1f1f1f;
  border-top: 1px solid #333;
}
.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #242424;
    padding: 0 16px;
    height: 40px;
    border-bottom: 1px solid #333;
}
.tabs { display: flex; height: 100%; }
.tab {
    padding: 0 16px;
    display: flex;
    align-items: center;
    cursor: pointer;
    color: #888;
    font-size: 13px;
    border-right: 1px solid #333;
}
.tab.active {
    background: #1f1f1f;
    color: #42b883;
    font-weight: bold;
    border-top: 2px solid #42b883;
}
.account-summary {
    font-size: 12px;
    color: #aaa;
}
.account-summary span { margin-left: 16px; }
.val { color: #fff; font-weight: bold; }
.panel-content {
    flex: 1;
    overflow: hidden;
}
.text-green { color: #42b883; }
.text-red { color: #ff4d4f; }
.pnl-cell { display: flex; flex-direction: column; line-height: 1.2; }
.pnl-percent { font-size: 11px; }

.coin-info-cell {
    display: flex;
    align-items: center;
}
.icon-wrapper {
    position: relative;
    margin-right: 6px;
    width: 16px;
    height: 16px;
}
.coin-icon { width: 100%; height: 100%; border-radius: 50%; display: block; }
.symbol-text { font-weight: bold; color: #eee; }
.tp-sl-cell { font-size: 12px; }
</style>
