<template>
  <a-modal
    :open="visible"
    :title="instId + ' K线图'"
    width="800px"
    @cancel="handleCancel"
    :footer="null"
  >
    <div ref="chartContainer" class="chart-container"></div>
  </a-modal>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { createChart } from 'lightweight-charts'
import axios from 'axios'

const props = defineProps({
  visible: Boolean,
  instId: String
})

const emit = defineEmits(['update:visible'])

const chartContainer = ref(null)
let chart = null
let candlestickSeries = null

const handleCancel = () => {
  emit('update:visible', false)
}

const initChart = () => {
  if (!chartContainer.value) return
  
  chart = createChart(chartContainer.value, {
    width: 750,
    height: 400,
    layout: {
      background: { color: '#242424' },
      textColor: '#d1d4dc',
    },
    grid: {
      vertLines: { color: '#333' },
      horzLines: { color: '#333' },
    },
  })

  candlestickSeries = chart.addCandlestickSeries({
    upColor: '#42b883',
    downColor: '#ff4d4f',
    borderVisible: false,
    wickUpColor: '#42b883',
    wickDownColor: '#ff4d4f',
  })
}

const fetchCandles = async () => {
  if (!props.instId) return
  try {
    const res = await axios.get(`/api/candles?instId=${props.instId}`)
    // OKX: [ts, o, h, l, c, ...] (ts is string ms)
    // LWC: { time: unix_seconds, open, high, low, close }
    const data = res.data.map(item => ({
      time: parseInt(item[0]) / 1000,
      open: parseFloat(item[1]),
      high: parseFloat(item[2]),
      low: parseFloat(item[3]),
      close: parseFloat(item[4]),
    })).sort((a, b) => a.time - b.time) // Sort ascending
    
    candlestickSeries.setData(data)
  } catch (e) {
    console.error(e)
  }
}

watch(() => props.visible, (val) => {
  if (val) {
    setTimeout(() => {
        if (!chart) initChart()
        fetchCandles()
    }, 100)
  }
})

watch(() => props.instId, () => {
  if (props.visible) fetchCandles()
})

onUnmounted(() => {
  if (chart) {
    chart.remove()
    chart = null
  }
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 400px;
}
</style>
