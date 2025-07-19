# KVs - 高级键值存储桌面应用程序

[![版本](https://img.shields.io/badge/version-0.6.0-blue.svg)](https://github.com/Chaos-woo/kvs)
[![许可证](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![平台](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

KVs 是一个现代化、功能丰富的桌面应用程序，用于管理键值对，具有高级搜索功能、数据可视化和全面的数据管理工具。采用 Python Flask 后端和 Tauri + React 前端构建，为存储、搜索和分析键值数据提供无缝体验。

## 🚀 功能特性

### 核心功能
- **高级键值存储**：存储和管理键值对，支持每个键对应多个值
- **全文搜索 (FTS5)**：使用 SQLite FTS5 提供强大的搜索功能，快速准确
- **多种搜索模式**：支持不同的搜索策略（混合、精确、模糊）
- **数据聚类**：智能键聚类，更好地组织和分析数据
- **统计仪表板**：为您的数据提供全面的统计和分析

### 用户界面
- **现代化界面**：使用 shadcn/ui 组件构建的简洁直观界面
- **主题支持**：明暗主题模式，支持系统偏好检测
- **标签式导航**：有序的界面，包含"快记"和"快搜"标签
- **K视图浏览器**：高级数据探索和可视化工具
- **响应式设计**：针对桌面使用优化，具有适当的窗口管理

### 数据管理
- **导入/导出**：支持jsonl的数据导入和导出
- **批量操作**：高效的批量删除和多记录管理
- **数据清理**：内置数据维护和清理工具
- **备份和恢复**：全面的数据备份和恢复功能

### 开发者功能
- **全面日志记录**：详细的 API 请求/响应日志，结构化输出
- **调试工具**：内置调试界面，用于开发和故障排除
- **RESTful API**：文档完善的 REST API，支持程序化访问
- **广泛测试**：涵盖所有主要功能的全面测试套件

## 🏗️ 架构

### 后端 (Python + Flask)
- **框架**：Flask 配合 SQLAlchemy ORM
- **数据库**：SQLite 配合 FTS5 扩展进行全文搜索
- **API 设计**：RESTful API 配合版本控制 (`/api/v1/`)
- **日志记录**：结构化日志，分离 API 和错误日志
- **服务**：业务逻辑的模块化服务架构

### 前端 (Tauri + React)
- **框架**：React 18 配合 TypeScript 确保类型安全
- **桌面**：Tauri 框架提供原生桌面集成
- **UI 组件**：shadcn/ui 配合 Radix UI 原语
- **样式**：Tailwind CSS 配合自定义主题
- **状态管理**：React hooks 配合 context API

## 📋 先决条件

在开发部署和克隆 KVs 之前，请确保已安装以下软件：

- **Python 3.8+** 配合 pip 包管理器
- **Node.js 16+** 配合 npm
- **Rust 工具链**（用于 Tauri）
- **Visual Studio** 或 **Intellij IDEA** 配合 C++ 桌面开发（Windows）

## 🛠️ 安装和设置

### 快速开始（自动构建）

1. **克隆仓库**：
   ```bash
   git clone https://github.com/Chaos-woo/kvs.git
   cd kvs
   ```

2. **运行自动构建**：
   ```bash
   build.bat
   ```

   这将：
   - 安装所有依赖项
   - 构建后端可执行文件
   - 打包前端应用程序
   - 创建 Windows 安装程序

3. **查找安装程序**：
   ```
   frontend\src-tauri\target\release\bundle\
   ```

### 开发环境设置

#### 后端设置

1. **导航到后端目录**：
   ```bash
   cd backend
   ```

2. **创建虚拟环境**：
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **安装依赖项**：
   ```bash
   pip install -r requirements.txt
   ```

4. **运行开发服务器**：
   ```bash
   python app.py
   ```

   Flask 服务器将在 `http://localhost:5000` 启动

#### 前端设置

1. **导航到前端目录**：
   ```bash
   cd frontend
   ```

2. **安装依赖项**：
   ```bash
   npm install
   ```

3. **运行开发服务器**：
   ```bash
   npm run tauri dev
   ```

   同时进行后端和前端运行调试：
   ```bash
   npm run dev-with-backend
   ```

## 🔧 配置

### 环境变量

在后端目录中创建 `.env` 文件：

```env
FLASK_ENV=development
DATABASE_URL=sqlite:///kvs.db
LOG_LEVEL=INFO
API_VERSION=v1
```

### 数据库配置

应用程序在首次运行时自动创建 SQLite 数据库和 FTS5 表。数据库文件存储在：
- **开发环境**：`backend/kvs.db`
- **生产环境**：应用程序数据目录

### 日志配置

日志存储在 `backend/logs/` 目录中：
- `api.log` - API 请求/响应日志
- `error.log` - 错误和异常日志
- `frontend.log` - 前端应用程序日志

## 📖 API 文档

### 基础 URL
```
http://localhost:5000/api/v1
```

### 身份验证
目前，API 在本地桌面使用时不需要身份验证。

### 端点

#### 键值操作

**创建键值对**
```http
POST /api/v1/kv
Content-Type: application/json

{
  "key": "example_key",
  "values": ["value1", "value2", "value3"]
}
```

**获取所有键值对**
```http
GET /api/v1/kv
```

**获取特定键值对**
```http
GET /api/v1/kv/{key_id}
```

**更新键值对**
```http
PUT /api/v1/kv/{key_id}
Content-Type: application/json

{
  "key": "updated_key",
  "values": ["new_value1", "new_value2"]
}
```

**删除键值对**
```http
DELETE /api/v1/kv/{key_id}
```

**批量删除**
```http
DELETE /api/v1/kv/batch
Content-Type: application/json

{
  "key_ids": [1, 2, 3, 4]
}
```

#### 搜索操作

**搜索键值对**
```http
GET /api/v1/search?q={query}&mode={search_mode}
```

参数：
- `q`：搜索查询字符串
- `mode`：搜索模式（`mixed`、`key`、`value`）

#### 统计和分析

**获取统计信息**
```http
GET /api/v1/stats
```

**获取导出统计信息**
```http
GET /api/v1/export-stats
```

#### 数据管理

**导出数据**
```http
GET /api/v1/export?format={format}
```

**导入数据**
```http
POST /api/v1/import
Content-Type: multipart/form-data

file: [data_file]
```

**聚类键**
```http
POST /api/v1/cluster
Content-Type: application/json

{
  "algorithm": "kmeans",
  "n_clusters": 5
}
```

## 🧪 测试

### 运行测试

**后端测试**：
```bash
cd backend
python -m pytest tests/ -v
```

**前端测试**：
```bash
cd frontend
npm test
```

**运行特定测试**：
```bash
cd backend
python -m pytest tests/test_key_value.py -v
```

### 测试覆盖率

应用程序包含以下方面的全面测试：
- API 端点和响应
- 数据库操作和模型
- 搜索功能（FTS5）
- 数据导入/导出
- 聚类算法
- 错误处理和边缘情况
- 前端组件和交互

## 🚀 生产构建

### 前端构建
```bash
cd frontend
npm run tauri build
```

### 后端构建
```bash
cd backend
python build_backend.py
```

### 完整构建过程
```bash
# 从项目根目录
build.bat
```

构建过程创建：
- **Windows 安装程序**：`.msi` 文件，便于安装
- **便携式可执行文件**：独立的 `.exe` 文件
- **应用程序包**：完整的应用程序包

输出位置：`frontend\src-tauri\target\release\bundle\`

## 🐛 故障排除

### 常见问题

**后端连接问题**：
- 确保 Python 虚拟环境已激活
- 检查端口 5000 是否可用
- 验证所有依赖项已安装

**前端构建错误**：
- 将 Node.js 更新到 16+ 版本
- 清除 npm 缓存：`npm cache clean --force`
- 删除 `node_modules` 并重新安装：`rm -rf node_modules && npm install`

**Tauri 构建问题**：
- 确保 Rust 工具链已安装并更新
- 验证 Visual Studio C++ 工具已安装
- 检查 WebView2 运行时是否可用

**数据库问题**：
- 检查 SQLite 数据库权限
- 验证 FTS5 扩展是否可用
- 查看 `backend/logs/` 中的数据库日志

### 调试模式

通过设置环境变量启用调试日志：
```bash
set FLASK_ENV=development
```

通过应用程序菜单访问调试界面：`查看 > 调试日志`

## 📚 文档

`docs/` 目录中提供了其他文档：

- [日志系统](docs/LOGGING.md) - 全面的日志文档
- [调试指南](docs/DEBUGGING.md) - 开发和调试技巧
- [导入系统](docs/IMPORT_DESIGN.md) - 数据导入功能
- [K视图功能](docs/K_VIEW_IMPLEMENTATION_SUMMARY.md) - 数据探索工具

## 🤝 贡献

1. Fork 仓库
2. 创建功能分支：`git checkout -b feature-name`
3. 进行更改并添加测试
4. 确保所有测试通过：`npm test` 和 `pytest`
5. 提交更改：`git commit -am 'Add feature'`
6. 推送到分支：`git push origin feature-name`
7. 提交拉取请求

### 开发指南

- Python 代码遵循 PEP 8
- 所有前端代码使用 TypeScript
- 为新功能编写测试
- 为 API 更改更新文档
- 使用常规提交消息

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [Tauri](https://tauri.app/) - 桌面应用程序框架
- [React](https://reactjs.org/) - UI 库
- [shadcn/ui](https://ui.shadcn.com/) - UI 组件
- [SQLite](https://www.sqlite.org/) - 数据库引擎
- [Tailwind CSS](https://tailwindcss.com/) - CSS 框架

## 📞 支持

如需支持，请：
1. 查看[故障排除部分](#-故障排除)
2. 查看现有的[问题](https://github.com/Chaos-woo/kvs/issues)
3. 创建包含详细信息的新问题

---

**KVs** - 让键值数据管理变得简单而强大。