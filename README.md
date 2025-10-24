# 🚀 LMHack

**The Smart Bridge for Local LLM Ecosystems**

*Intelligent proxy that connects LM Studio seamlessly with AnyLLM, BrowserOS, and beyond. Zero-config, auto-healing, context-aware.*

---

## 🎯 What Makes LMHack Different?

While the original [vscode-lm-proxy](https://github.com/ryonakae/vscode-lm-proxy) focuses on exposing GitHub Copilot, **LMHack adds the crucial 20%** that transforms your local LLM setup into a professional, unified ecosystem.

### ✨ **The 20% That Changes Everything**

#### 🔧 **Zero-Touch Configuration**
- **Auto-detection** of LM Studio instances
- **Smart configuration** of AnyLLM and BrowserOS
- **One-click setup** instead of manual endpoint management

#### 🩺 **Intelligent Health Monitoring** 
- **Auto-reconnection** when LM Studio restarts
- **Real-time performance** metrics (GPU, memory, tokens/sec)
- **Proactive notifications** to connected clients

#### 🔄 **Unified Model Management**
- **Centralized control** of LM Studio models from any app
- **Hot model switching** without restart
- **Load balancing** across multiple model instances

#### 🧠 **Context Sharing Revolution**
- **Cross-app memory**: AnyLLM analysis ↔ BrowserOS actions
- **Intelligent routing** based on task type
- **Persistent context** across sessions

---

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    AnyLLM       │◄──►│    LMHack       │◄──►│   BrowserOS     │
│  (Documents)    │    │  Smart Proxy    │    │  (Web Actions)  │  
│                 │    │                 │    │                 │
│ • RAG Queries   │    │ • Auto Config   │    │ • Web Research  │
│ • Doc Analysis  │    │ • Health Check  │    │ • Data Extract  │
│ • Knowledge     │    │ • Model Switch  │    │ • Automation    │
└─────────────────┘    │ • Context Share │    └─────────────────┘
                       │ • Performance   │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   LM Studio     │
                       │  (Local Models) │
                       │                 │
                       │ • Llama 3.2     │
                       │ • Qwen 2.5      │
                       │ • Mistral 7B    │
                       └─────────────────┘
```

---

## 🚀 **Quick Start**

### Prerequisites
- [LM Studio](https://lmstudio.ai) running with local server enabled
- [AnyLLM](https://useanything.com) and/or [BrowserOS](https://browseros.com) installed
- VS Code (for extension mode)

### Installation

#### Option 1: VS Code Extension (Recommended)
```bash
# Install from VS Code Marketplace
code --install-extension gerivdb.lmhack
```

#### Option 2: Standalone CLI
```bash
npm install -g lmhack
lmhack start
```

#### Option 3: Docker
```bash
docker run -p 4000:4000 gerivdb/lmhack
```

### Zero-Config Setup
```bash
# LMHack auto-detects and configures everything!
lmhack init
# ✅ Found LM Studio at localhost:1234
# ✅ Configured AnyLLM connection
# ✅ Configured BrowserOS connection  
# 🚀 LMHack bridge active at localhost:4000
```

---

## 🔌 **Supported Integrations**

### **Primary Targets**
- ✅ **LM Studio** - Full model management & health monitoring
- ✅ **AnyLLM** - Document processing & RAG workflows
- ✅ **BrowserOS** - Web automation & research

### **Extended Compatibility**
- ✅ **Cursor** - Code completion with local models
- ✅ **Continue.dev** - VS Code coding assistant
- ✅ **Open WebUI** - Chat interface
- ✅ **Any OpenAI-compatible tool**

---

## 📊 **Performance Dashboard**

LMHack includes a real-time monitoring dashboard:

```bash
lmhack dashboard
```

**Metrics tracked:**
- 🔥 GPU utilization and memory usage
- ⚡ Tokens per second throughput 
- 📊 Request queue length
- ⏱️ Model load times
- 🔄 Auto-reconnection events
- 📈 Cross-app context sharing

---

## 🛠️ **Advanced Features**

### Model Hot-Swapping
```javascript
// Switch models based on task complexity
const response = await lmhack.request({
    message: "Complex coding task",
    auto_model: "performance" // Auto-selects best model
});
```

### Context Bridging
```javascript
// AnyLLM processes document
const analysis = await anyllm.analyze(document);

// Context automatically available in BrowserOS
const webActions = await browseros.actOnAnalysis();
```

### Health Monitoring
```javascript
lmhack.on('lmstudio_disconnected', async () => {
    await lmhack.waitForReconnection();
    await lmhack.notifyClients('LM Studio reconnected');
});
```

---

## 🔧 **Configuration**

### VS Code Settings
```json
{
  "lmhack.port": 4000,
  "lmhack.autoConfig": true,
  "lmhack.contextSharing": true,
  "lmhack.healthMonitoring": true,
  "lmhack.performanceDashboard": true
}
```

### Standalone Config
```yaml
# lmhack.config.yml
server:
  port: 4000
  host: "0.0.0.0"

lmstudio:
  endpoint: "http://localhost:1234"
  auto_detect: true
  health_check_interval: 5000

integrations:
  anyllm:
    enabled: true
    auto_configure: true
  browseros:
    enabled: true
    auto_configure: true

features:
  context_sharing: true
  model_management: true
  performance_monitoring: true
```

---

## 🤝 **Contributing**

LMHack is built on the solid foundation of [vscode-lm-proxy](https://github.com/ryonakae/vscode-lm-proxy) by [@ryonakae](https://github.com/ryonakae). 

**Areas where we need help:**
- 🔌 Additional integrations (Ollama, MLX, etc.)
- 📊 Enhanced performance metrics
- 🎨 Dashboard UI improvements
- 🐛 Bug fixes and optimizations

### Development Setup
```bash
git clone https://github.com/gerivdb/lmhack.git
cd lmhack
npm install
npm run dev
```

---

## 📜 **License**

MIT License - Same as the original vscode-lm-proxy

---

## 🙏 **Acknowledgments**

- **[@ryonakae](https://github.com/ryonakae)** for the excellent vscode-lm-proxy foundation
- **LM Studio team** for the best local LLM server
- **AnyLLM & BrowserOS communities** for pushing local-first AI

---

## 🚀 **What's Next?**

- [ ] **LMHack Pro**: Advanced load balancing
- [ ] **LMHack Cloud**: Secure tunnel for remote access  
- [ ] **LMHack Marketplace**: Plugin ecosystem
- [ ] **Multi-GPU support**: Distribute workloads

---

*"Hacking the future of local LLM ecosystems, one bridge at a time."* ⚡

**Star ⭐ this repo if LMHack solves your local LLM integration challenges!**