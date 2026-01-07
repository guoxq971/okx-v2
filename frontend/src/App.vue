<template>
  <a-config-provider
    :locale="zhCN"
    :theme="{
      token: {
        colorPrimary: '#42b883',
        colorBgBase: '#1a1a1a',
        colorTextBase: 'rgba(255, 255, 255, 0.87)',
        colorBorder: '#333'
      },
      algorithm: theme.darkAlgorithm
    }"
  >
    <div class="app-container">
      <!-- Header -->
      <header class="header">
        <div class="logo">OKX 交易终端</div>
        <div class="header-actions">
           <a-button type="primary" ghost size="small" @click="showConfig">
             <template #icon><SettingOutlined /></template>
             配置 API
           </a-button>
        </div>
      </header>

      <!-- Main Layout -->
      <main class="main-content">
          <!-- Left: Removed -->
          
          <!-- Center: Watchlist Grid & Bottom Panel -->
          <section class="center-area" ref="centerArea">
              <div class="grid-area" :style="{ height: `calc(100% - ${bottomHeight}px)` }">
                  <WatchList />
              </div>
              
              <!-- Resizer Handle -->
              <div class="resizer" @mousedown="startResize"></div>

              <div class="bottom-area" :style="{ height: `${bottomHeight}px` }">
                  <AccountBottomPanel />
              </div>
          </section>

          <!-- Right: Order Entry -->
          <aside class="sidebar-right" :class="{ collapsed: isOrderCollapsed }">
              <div class="toggle-handle" @click="isOrderCollapsed = !isOrderCollapsed">
                  <LeftOutlined v-if="isOrderCollapsed" />
                  <RightOutlined v-else />
              </div>
              <div class="sidebar-content" v-show="!isOrderCollapsed">
                  <OrderEntry />
              </div>
          </aside>
      </main>

      <!-- Config Modal -->
      <a-modal
        v-model:open="configVisible"
        title="配置 API Key"
        @ok="handleConfigSubmit"
        :confirmLoading="configLoading"
      >
        <a-form layout="vertical" :model="configForm">
          <a-form-item label="API Key" name="api_key" :rules="[{ required: true, message: '请输入 API Key' }]">
            <a-input v-model:value="configForm.api_key" />
          </a-form-item>
          <a-form-item label="Secret Key" name="secret_key" :rules="[{ required: true, message: '请输入 Secret Key' }]">
            <a-input-password v-model:value="configForm.secret_key" />
          </a-form-item>
          <a-form-item label="Passphrase" name="passphrase" :rules="[{ required: true, message: '请输入 Passphrase' }]">
            <a-input-password v-model:value="configForm.passphrase" />
          </a-form-item>
           <a-form-item label="模拟盘交易" name="is_simulated">
            <a-switch v-model:checked="configForm.is_simulated" />
          </a-form-item>
        </a-form>
      </a-modal>
    </div>
  </a-config-provider>
</template>

<script setup>
import { theme, message } from 'ant-design-vue';
import { SettingOutlined, LeftOutlined, RightOutlined } from '@ant-design/icons-vue';
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import zhCN from 'ant-design-vue/es/locale/zh_CN';
import { useMarketStore } from './stores/market';

// Components
import WatchList from './components/WatchList.vue';
import ChartPanel from './components/ChartPanel.vue';
import OrderEntry from './components/OrderEntry.vue';
import AccountBottomPanel from './components/AccountBottomPanel.vue';

const store = useMarketStore();
const configVisible = ref(false);
const configLoading = ref(false);
const bottomHeight = ref(250); // Default height
const centerArea = ref(null);
const isOrderCollapsed = ref(true); // Default collapsed

const startResize = (e) => {
    e.preventDefault();
    const startY = e.clientY;
    const startHeight = bottomHeight.value;
    
    const doResize = (moveEvent) => {
        const delta = startY - moveEvent.clientY;
        const newHeight = startHeight + delta;
        // Min 100px, Max 80% of screen
        if (newHeight > 100 && newHeight < window.innerHeight * 0.8) {
            bottomHeight.value = newHeight;
        }
    };
    
    const stopResize = () => {
        document.removeEventListener('mousemove', doResize);
        document.removeEventListener('mouseup', stopResize);
    };
    
    document.addEventListener('mousemove', doResize);
    document.addEventListener('mouseup', stopResize);
};

const configForm = reactive({
  api_key: '',
  secret_key: '',
  passphrase: '',
  is_simulated: false
});

const showConfig = async () => {
  try {
    const res = await axios.get('/api/config');
    if (res.data.api_key) {
        configForm.api_key = res.data.api_key;
        configForm.secret_key = res.data.secret_key;
        configForm.passphrase = res.data.passphrase;
        configForm.is_simulated = res.data.is_simulated;
    }
  } catch (e) {
    console.error("Failed to fetch config", e);
  }
  configVisible.value = true;
};

const handleConfigSubmit = async () => {
  configLoading.value = true;
  try {
    await axios.post('/api/config', configForm);
    message.success('API 配置已更新');
    configVisible.value = false;
    store.fetchBalance();
  } catch (e) {
    message.error('配置更新失败');
  } finally {
    configLoading.value = false;
  }
};

onMounted(() => {
    store.startPolling();
});

onUnmounted(() => {
    store.stopPolling();
});
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #1a1a1a;
  color: #d1d4dc;
  overflow: hidden;
}

.header {
  height: 48px;
  background: #242424;
  border-bottom: 1px solid #333;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  flex-shrink: 0;
}

.logo {
  color: #42b883;
  font-size: 18px;
  font-weight: bold;
}

.main-content {
    flex: 1;
    display: flex;
    overflow: hidden;
}

.sidebar-left {
    width: 280px;
    flex-shrink: 0;
}

.center-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0; /* Fix flex overflow */
}

.chart-area {
    flex: 1;
    min-height: 0; /* Fix flex overflow */
}

.grid-area {
    /* flex: 1; Removed flex to use manual height */
    min-height: 0;
    overflow: hidden;
}

.resizer {
    height: 5px;
    background: #333;
    cursor: row-resize;
    flex-shrink: 0;
    transition: background 0.2s;
}

.resizer:hover {
    background: #42b883;
}

.bottom-area {
    /* height: 250px; Removed fixed height */
    flex-shrink: 0;
}

.sidebar-right {
    width: 300px;
    flex-shrink: 0;
    position: relative;
    transition: width 0.3s;
    background: #1f1f1f;
    border-left: 1px solid #333;
    display: flex;
}

.sidebar-right.collapsed {
    width: 24px;
}

.sidebar-content {
    flex: 1;
    overflow: hidden;
    min-width: 300px; /* Prevent content squishing */
}

.toggle-handle {
    width: 24px;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    background: #2a2a2a;
    border-right: 1px solid #333;
    color: #888;
}

.toggle-handle:hover {
    color: #fff;
    background: #333;
}
</style>
