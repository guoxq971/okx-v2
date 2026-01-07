# OKX 交易终端

基于 Python (FastAPI) 和 Vue 3 (Ant Design Vue) 构建的全栈加密货币交易应用。

## 功能特性
- **行情数据**: 实时展示现货、永续合约和交割合约的行情列表。
- **K线图表**: 基于 Lightweight Charts 的交互式K线图。
- **交易功能**: 支持直接从 UI 下单（市价/限价，支持现货/逐仓/全仓模式）。
- **账户管理**: 查看总权益和持仓信息。
- **自选收藏**: 收藏你关注的币种。
- **深色主题**: 类似 Vue 官网的深色模式。

## 环境要求
- Node.js (v16+)
- Python (3.8+)

## 安装与运行

### 1. 后端 (Backend)
1. 进入 `backend` 目录。
2. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```
3. **配置 API Key**:
   - 编辑 `.env` 文件。
   - 填入你的 OKX API Key, Secret, 和 Passphrase。
   - 如果使用模拟盘，请设置 `OKX_SIMULATED=1`。
   ```ini
   OKX_API_KEY=你的APIKey
   OKX_SECRET_KEY=你的SecretKey
   OKX_PASSPHRASE=你的Passphrase
   OKX_SIMULATED=0
   ```
4. 运行服务器:
   ```bash
   python main.py
   ```
   服务器运行在 `http://localhost:8000`。

### 2. 前端 (Frontend)
1. 进入 `frontend` 目录。
2. 安装依赖:
   ```bash
   npm install
   ```
3. 启动开发服务器:
   ```bash
   npm run dev
   ```
   访问地址 `http://localhost:5173`。

## 架构
- **后端**: FastAPI 作为代理服务器，处理 OKX V5 API 请求签名和转发。
- **前端**: Vue 3 + Pinia (状态管理) + Ant Design Vue (UI组件库)。
