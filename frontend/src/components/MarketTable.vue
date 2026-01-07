<template>
  <div class="market-table-container">
    <div class="toolbar">
      <div class="filters">
        <a-radio-group v-model:value="activeFilter" button-style="solid" @change="handleFilterChange">
          <a-radio-button value="SPOT">现货</a-radio-button>
          <a-radio-button value="SWAP">永续合约</a-radio-button>
          <a-radio-button value="FUTURES">交割合约</a-radio-button>
        </a-radio-group>
      </div>
      <div class="actions">
        <a-button type="default" @click="handleRefresh" :loading="store.loading" style="margin-right: 8px">
          <template #icon><ReloadOutlined /></template>
          刷新
        </a-button>
        <a-popover title="配置显示列" trigger="click" placement="bottomRight">
          <template #content>
            <div class="column-config">
              <a-checkbox-group v-model:value="visibleColumns" :options="allColumnOptions" />
            </div>
          </template>
          <a-button type="primary">
            <template #icon><SettingOutlined /></template>
            列设置
          </a-button>
        </a-popover>
      </div>
    </div>

    <a-table
      :dataSource="filteredTickers"
      :columns="tableColumns"
      :loading="store.loading"
      :pagination="{ pageSize: 20 }"
      rowKey="instId"
      :customRow="customRow"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'instId'">
          <div class="coin-info">
             <span class="symbol">{{ record.instId }}</span>
             <a-tag color="blue" v-if="record.tag">{{ record.tag }}</a-tag>
             <StarFilled v-if="record.isFavorite" style="color: gold; margin-left: 8px;" @click.stop="toggleFav(record)" />
             <StarOutlined v-else style="color: gray; margin-left: 8px;" @click.stop="toggleFav(record)" />
          </div>
        </template>
        <template v-else-if="column.key === 'last'">
            <span :class="getPriceColor(record)">{{ record.last }}</span>
        </template>
         <template v-else-if="column.key === 'change24h'">
            <span :class="getChangeColor(record)">{{ (parseFloat(record.open24h || 0) !== 0 ? ((parseFloat(record.last) - parseFloat(record.open24h))/parseFloat(record.open24h) * 100).toFixed(2) : 0) }}%</span>
        </template>
      </template>
    </a-table>

    <KLineModal
      v-model:visible="showChart"
      :instId="selectedInstId"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMarketStore } from '../stores/market'
import { SettingOutlined, StarOutlined, StarFilled, ReloadOutlined } from '@ant-design/icons-vue'
import KLineModal from './KLineModal.vue'

const store = useMarketStore()
const activeFilter = ref('SPOT')
const showChart = ref(false)
const selectedInstId = ref('')

// Default columns
const defaultColumns = ['instId', 'last', 'change24h', 'vol24h', 'ts']
const visibleColumns = ref([...defaultColumns])

// All possible columns from OKX Ticker API
const allColumnOptions = [
  { label: '币种', value: 'instId' },
  { label: '最新价', value: 'last' },
  { label: '24h涨跌幅', value: 'change24h' },
  { label: '24h成交量', value: 'vol24h' },
  { label: '24h开盘价', value: 'open24h' },
  { label: '24h最高价', value: 'high24h' },
  { label: '24h最低价', value: 'low24h' },
  { label: '时间戳', value: 'ts' }
]

const tableColumns = computed(() => {
  return visibleColumns.value.map(key => {
    const option = allColumnOptions.find(o => o.value === key)
    return {
      title: option ? option.label : key,
      dataIndex: key,
      key: key,
      sorter: (a, b) => {
          if (key === 'instId') return a.instId.localeCompare(b.instId);
          return parseFloat(a[key] || 0) - parseFloat(b[key] || 0);
      }
    }
  })
})

const filteredTickers = computed(() => {
  return store.tickers
})

const handleFilterChange = () => {
  store.fetchTickers(activeFilter.value)
}

const handleRefresh = () => {
  store.fetchTickers(activeFilter.value)
}

const customRow = (record) => {
  return {
    onClick: () => {
      selectedInstId.value = record.instId
      showChart.value = true
    }
  }
}

const toggleFav = (record) => {
    store.toggleFavorite(record.instId)
}

const getPriceColor = (record) => {
    const change = parseFloat(record.last) - parseFloat(record.open24h)
    return change >= 0 ? 'text-green' : 'text-red'
}

const getChangeColor = (record) => {
     const change = parseFloat(record.last) - parseFloat(record.open24h)
     return change >= 0 ? 'text-green' : 'text-red'
}

onMounted(() => {
  store.fetchTickers('SPOT')
})
</script>

<style scoped>
.market-table-container {
  padding: 20px;
}
.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}
.text-green { color: #42b883; }
.text-red { color: #ff4d4f; }
.coin-info { display: flex; align-items: center; cursor: pointer; }
.column-config { display: flex; flex-direction: column; gap: 8px; max-height: 300px; overflow-y: auto; }
</style>
