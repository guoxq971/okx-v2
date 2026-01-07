<template>
  <div class="order-entry">
    <div class="tabs">
      <div class="tab active">合约下单</div>
    </div>
    
    <div class="form-container">
       <a-form layout="vertical" :model="orderForm" @finish="handleTrade">
          
          <!-- Mode Selection -->
          <a-form-item label="交易模式">
             <a-select v-model:value="orderForm.tdMode" size="small">
              <a-select-option value="cross">全仓 (Cross)</a-select-option>
              <a-select-option value="isolated">逐仓 (Isolated)</a-select-option>
              <a-select-option value="cash">现货 (Cash)</a-select-option>
            </a-select>
          </a-form-item>
          
          <!-- Leverage (Only for Cross/Isolated) -->
           <a-form-item label="杠杆倍数" v-if="orderForm.tdMode !== 'cash'">
            <a-input-number v-model:value="leverage" :min="1" :max="125" style="width: 100%" size="small" />
          </a-form-item>

          <!-- Order Type -->
          <a-form-item label="订单类型">
             <a-select v-model:value="orderForm.ordType" size="small">
              <a-select-option value="limit">限价单</a-select-option>
              <a-select-option value="market">市价单</a-select-option>
            </a-select>
          </a-form-item>

          <!-- Price -->
          <a-form-item label="价格 (USDT)" v-if="orderForm.ordType === 'limit'">
            <a-input v-model:value="orderForm.px" placeholder="价格" />
          </a-form-item>

          <!-- Size -->
          <a-form-item label="数量 (U本位)">
            <a-input v-model:value="orderForm.sz" placeholder="输入金额 (USDT)" />
          </a-form-item>

          <!-- Submit Buttons -->
          <div class="action-buttons">
              <a-button 
                type="primary" 
                :loading="tradeLoading" 
                block
                class="buy-btn"
                @click="handleTrade('buy')"
              >
                买入/做多
              </a-button>
              
              <a-button 
                type="primary" 
                :loading="tradeLoading" 
                block
                danger
                class="sell-btn"
                @click="handleTrade('sell')"
              >
                卖出/做空
              </a-button>
          </div>

       </a-form>
    </div>
    
    <div class="assets-info">
        <div class="row">
            <span>可用余额:</span>
            <span>{{ store.accountBalance.adjEq || '0.00' }} USD</span>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useMarketStore } from '../stores/market'
import axios from 'axios'
import { message } from 'ant-design-vue'

const store = useMarketStore()
const tradeLoading = ref(false)
const leverage = ref(5) // Default leverage 5

const orderForm = reactive({
    instId: store.selectedSymbol,
    side: 'buy',
    ordType: 'limit',
    px: '',
    sz: '',
    tdMode: 'cross' // Default to Cross
})

watch(() => store.selectedSymbol, (val) => {
    orderForm.instId = val
})

const handleTrade = async (side) => {
    tradeLoading.value = true
    try {
        const payload = { ...orderForm }
        payload.side = side // Set side based on button click
        if (payload.ordType === 'market') delete payload.px
        // Ensure instId is current
        payload.instId = store.selectedSymbol
        
        // If contract mode, usually need to set leverage first via API, 
        // but for simplicity here we assume user sets it in OKX app or we just place order.
        // NOTE: OKX V5 API requires setting leverage endpoint separately before placing order if changed.
        // For now, we will just place the order. Real implementation should call set-leverage endpoint.
        if (payload.tdMode !== 'cash') {
             // Optional: Call set leverage API here
             // Using axios instance or global axios
             await axios.post('/api/leverage', {
                 instId: payload.instId,
                 lever: leverage.value,
                 mgnMode: payload.tdMode
             }).catch(err => console.warn('Set leverage failed/ignored', err))
        }
        
        const res = await axios.post('/api/trade', payload)
        message.success(`下单成功: ${res.data.ordId}`)
        store.fetchBalance()
        store.fetchPositions()
        store.fetchOrders() // Refresh orders
    } catch (e) {
        message.error(e.response?.data?.detail || '下单失败')
    } finally {
        tradeLoading.value = false
    }
}
</script>

<style scoped>
.order-entry {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1f1f1f;
  border-left: 1px solid #333;
}
.tabs {
    display: flex;
    border-bottom: 1px solid #333;
}
.tab {
    flex: 1;
    text-align: center;
    padding: 12px;
    font-size: 14px;
    color: #888;
    cursor: pointer;
}
.tab.active {
    color: #42b883;
    border-bottom: 2px solid #42b883;
    font-weight: bold;
}
.form-container {
    padding: 16px;
    flex: 1;
}
.action-buttons {
    display: flex;
    gap: 10px;
    margin-top: 16px;
}
.buy-btn {
    background: #42b883;
    border-color: #42b883;
}
.buy-btn:hover {
    background: #369c6f;
    border-color: #369c6f;
}
.assets-info {
    padding: 16px;
    border-top: 1px solid #333;
    font-size: 12px;
    color: #aaa;
}
.row {
    display: flex;
    justify-content: space-between;
}
</style>
