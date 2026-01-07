<template>
  <a-card title="交易与账户" class="trade-panel">
    <div class="account-info">
      <a-statistic title="总权益 (USD)" :value="store.accountBalance.totalEq || '---'" :precision="2" />
      <a-statistic title="可用余额 (USD)" :value="store.accountBalance.adjEq || '---'" :precision="2" style="margin-left: 20px" />
      <a-button @click="refresh" :loading="store.loading" style="margin-left: auto">刷新</a-button>
    </div>

    <a-divider>持仓</a-divider>
    <a-table :dataSource="store.positions" :columns="positionColumns" rowKey="instId" size="small" :pagination="false">
         <template #bodyCell="{ column, record }">
             <template v-if="column.key === 'upl'">
                 <span :class="parseFloat(record.upl) >= 0 ? 'text-green' : 'text-red'">{{ record.upl }}</span>
             </template>
         </template>
    </a-table>

    <a-divider>下单</a-divider>
    <a-form layout="vertical" :model="orderForm" @finish="handleTrade">
      <a-row :gutter="16">
        <a-col :span="6">
          <a-form-item label="币种" name="instId" :rules="[{ required: true }]">
            <a-input v-model:value="orderForm.instId" placeholder="e.g. BTC-USDT" />
          </a-form-item>
        </a-col>
        <a-col :span="6">
          <a-form-item label="方向" name="side">
            <a-select v-model:value="orderForm.side">
              <a-select-option value="buy">买入</a-select-option>
              <a-select-option value="sell">卖出</a-select-option>
            </a-select>
          </a-form-item>
        </a-col>
        <a-col :span="6">
          <a-form-item label="类型" name="ordType">
             <a-select v-model:value="orderForm.ordType">
              <a-select-option value="market">市价</a-select-option>
              <a-select-option value="limit">限价</a-select-option>
            </a-select>
          </a-form-item>
        </a-col>
         <a-col :span="6">
          <a-form-item label="价格" name="px">
            <a-input v-model:value="orderForm.px" :disabled="orderForm.ordType === 'market'" />
          </a-form-item>
        </a-col>
         <a-col :span="6">
          <a-form-item label="数量" name="sz" :rules="[{ required: true }]">
            <a-input v-model:value="orderForm.sz" />
          </a-form-item>
        </a-col>
         <a-col :span="6">
          <a-form-item label="模式" name="tdMode">
             <a-select v-model:value="orderForm.tdMode">
              <a-select-option value="cash">现货</a-select-option>
              <a-select-option value="isolated">逐仓</a-select-option>
              <a-select-option value="cross">全仓</a-select-option>
            </a-select>
          </a-form-item>
        </a-col>
         <a-col :span="6">
            <a-button type="primary" html-type="submit" :loading="tradeLoading" style="margin-top: 30px;">提交订单</a-button>
        </a-col>
      </a-row>
    </a-form>
  </a-card>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useMarketStore } from '../stores/market'
import axios from 'axios'
import { message } from 'ant-design-vue'

const store = useMarketStore()
const tradeLoading = ref(false)

const orderForm = reactive({
    instId: '',
    side: 'buy',
    ordType: 'limit',
    px: '',
    sz: '',
    tdMode: 'cash'
})

const positionColumns = [
    { title: '币种', dataIndex: 'instId', key: 'instId' },
    { title: '持仓量', dataIndex: 'pos', key: 'pos' },
    { title: '开仓均价', dataIndex: 'avgPx', key: 'avgPx' },
    { title: '未实现盈亏', dataIndex: 'upl', key: 'upl' },
]

const refresh = () => {
    store.fetchBalance()
    store.fetchPositions()
}

const handleTrade = async () => {
    tradeLoading.value = true
    try {
        const payload = { ...orderForm }
        if (payload.ordType === 'market') delete payload.px
        
        const res = await axios.post('/api/trade', payload)
        message.success(`下单成功: ${res.data.ordId}`)
        refresh()
    } catch (e) {
        message.error(e.response?.data?.detail || '下单失败')
    } finally {
        tradeLoading.value = false
    }
}

onMounted(() => {
    refresh()
})
</script>

<style scoped>
.trade-panel {
    margin-bottom: 20px;
}
.account-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.text-green { color: #42b883; }
.text-red { color: #ff4d4f; }
</style>
