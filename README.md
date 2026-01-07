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

## 本地复原与启动指南 (如何从 GitHub 拉取代码并运行)

如果你在另一台电脑上克隆了本项目，请按照以下步骤复原环境：

### 1. 克隆项目
```bash
git clone https://github.com/guoxq971/okx-v2.git
cd okx-v2
```

### 2. 后端配置 (Backend)
后端依赖 Python 环境和 API Key 配置。
1. 进入后端目录:
   ```bash
   cd backend
   ```
2. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```
3. **关键步骤: 创建配置**
   - 复制示例配置文件:
     ```bash
     cp .env.example .env
     # 或者在 Windows 上手动复制并重命名
     ```
   - 打开 `.env` 文件，填入你的 OKX API Key:
     ```ini
     OKX_API_KEY=你的真实APIKey
     OKX_SECRET_KEY=你的SecretKey
     OKX_PASSPHRASE=你的密码
     OKX_SIMULATED=0
     ```
4. 启动后端:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

### 3. 前端配置 (Frontend)
前端依赖 Node.js 环境。
1. 进入前端目录:
   ```bash
   cd ../frontend
   ```
2. 安装依赖:
   ```bash
   npm install
   ```
3. 启动前端:
   ```bash
   npm run dev
   ```
4. 打开浏览器访问: `http://localhost:5173`

---

## 部署 (Deploy)
本项目支持一键部署到 Render。详情请查看仓库根目录下的 `render.yaml` 蓝图文件。

## 架构
- **后端**: FastAPI 作为代理服务器，处理 OKX V5 API 请求签名和转发。
- **前端**: Vue 3 + Pinia (状态管理) + Ant Design Vue (UI组件库)。
