<template>
  <div class="chart-panel">
    <div class="chart-header">
       <span class="chart-title">{{ store.selectedSymbol }}</span>
       <div class="chart-intervals">
           <!-- Placeholder for interval buttons -->
           <a-radio-group v-model:value="bar" size="small" button-style="solid" @change="fetchCandles">
               <a-radio-button value="15m">15m</a-radio-button>
               <a-radio-button value="1H">1H</a-radio-button>
               <a-radio-button value="4H">4H</a-radio-button>
               <a-radio-button value="1D">1D</a-radio-button>
           </a-radio-group>
       </div>
    </div>
    <div ref="chartContainer" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { createChart } from 'lightweight-charts'
import axios from 'axios'
import { useMarketStore } from '../stores/market'

const store = useMarketStore()
const chartContainer = ref(null)
const bar = ref('1H')
let chart = null
let candlestickSeries = null

const initChart = () => {
  if (!chartContainer.value) return
  
  chart = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: chartContainer.value.clientHeight,
    layout: {
      background: { color: '#1a1a1a' },
      textColor: '#d1d4dc',
    },
    grid: {
      vertLines: { color: '#333' },
      horzLines: { color: '#333' },
    },
    timeScale: {
        timeVisible: true,
        secondsVisible: false,
    }
  })

  candlestickSeries = chart.addCandlestickSeries({
    upColor: '#42b883',
    downColor: '#ff4d4f',
    borderVisible: false,
    wickUpColor: '#42b883',
    wickDownColor: '#ff4d4f',
  })

  // Resize observer
  new ResizeObserver(entries => {
      if (entries.length === 0 || entries[0].target !== chartContainer.value) { return; }
      const newRect = entries[0].contentRect;
      chart.applyOptions({ height: newRect.height, width: newRect.width });
  }).observe(chartContainer.value);
}

const fetchCandles = async () => {
  if (!store.selectedSymbol) return
  try {
    const res = await axios.get(`/api/candles?instId=${store.selectedSymbol}&bar=${bar.value}`)
    // OKX: [ts, o, h, l, c, ...] (ts is string ms)
    const data = res.data.map(item => ({
      time: parseInt(item[0]) / 1000,
      open: parseFloat(item[1]),
      high: parseFloat(item[2]),
      low: parseFloat(item[3]),
      close: parseFloat(item[4]),
    })).sort((a, b) => a.time - b.time) 
    
    candlestickSeries.setData(data)
  } catch (e) {
    console.error(e)
  }
}

watch(() => store.selectedSymbol, (val) => {
  if (val) fetchCandles()
})

onMounted(() => {
    initChart()
    if (store.selectedSymbol) fetchCandles()
})

onUnmounted(() => {
  if (chart) {
    chart.remove()
    chart = null
  }
})
</script>

<style scoped>
.chart-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1a1a1a;
  position: relative;
}
.chart-header {
    padding: 8px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #333;
}
.chart-title {
    font-size: 16px;
    font-weight: bold;
    color: #fff;
}
.chart-container {
  flex: 1;
  width: 100%;
  overflow: hidden;
}
</style>
