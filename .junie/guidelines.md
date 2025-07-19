# KVs Windows 桌面应用程序的开发指南

本文档提供了开发和维护 "KVs" 此 Windows 桌面应用程序的指导原则。它面向熟悉本项目所用核心技术的高级开发人员。

## 技术栈概述

- **后台**：使用 Flask 框架的 Python
- **前端**：Tauri + React 与 shadcn/ui 组件
- **目标平台**：Windows 桌面

## 生成和配置说明

#### 后端设置（Python + Flask）

#### 先决条件
- 已安装 Python 3.8+
- pip 软件包管理器
- 虚拟环境工具（venv）

#### 设置步骤
1. **环境设置**：
```bash
python -m venv venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. **开发服务器**：
```bash
python app.py
# 或
flask run --debug
```

3. **API 配置**：
- 应在 `routes/` 目录中定义 API 端点
- 使用 Flask Blueprints 组织路由模块
- 执行正确的错误处理和状态代码

4. **数据库集成**（如适用）：
- 将 SQLAlchemy 用作 ORM
- 在单独的 `models/` 目录中定义模型
- 迁移应使用 Alembic 进行管理
- 使用SQLite作为轻量持久化数据库
- 持久化的时间均使用UTC+0时间
- 集成SQLite FTS5作为数据全文检索扩展组件

#### 前端设置（Tauri + React + shadcn/ui）

#### 先决条件
- Node.js 16+ 和 npm
- Rust 工具链（用于 Tauri）
- IntelliJ IDEA 构建工具与 C++ 桌面开发工作量

#### 设置步骤
1. **安装依赖项**：
```bash
cd frontend
npm install
```

2. **开发模式**：
```bash
并发启动前端和后端: dev-with-backend
仅启动前端: npm run tauri dev
# 或
yarn tauri dev
```

3. **为生产而建设**：
```bash
npm run tauri build
```

4. **shadcn/ui 组件**：
- 使用 CLI 添加新组件
```bash
cd frontend
npx shadcn@latest add [component-name]
```
For example, to add the Accordion component:

```bash
npx shadcn@latest add accordion
```

Note: `npx shadcn-ui@latest` is deprecated, use `npx shadcn@latest` instead
- 在 `src/styles/globals.css` 中自定义主题

### 整合配置

1. ** 后端-前端通信**：
- 用于 Rust 与 JavaScript 直接通信的 Tauri 命令
- 用于 Flask 后端通信的 HTTP API 调用
- 用于实时功能的 WebSocket（如需要）

2. **环境配置**：
- 使用 `.env` 文件获取特定环境变量
- 独立的 dev/prod 配置
- 将敏感信息加密存储在持久化数据库中，而不是代码中

### 最佳编码实践

### Python（后端）最佳实践

1. **项目结构**：
```
backend/
├── app.py              # Application entry point
├── config.py           # Configuration settings
├── models/             # Database models
├── routes/             # API routes/endpoints
├── services/           # Business logic
├── utils/              # Helper functions
└── tests/              # Test cases
```

2. **代码样式**：
- 遵循 PEP 8 准则
- 对函数参数和返回值使用类型提示
- 用 docstrings 记录函数和类
- 代码格式使用黑色

3. **API 设计**：
- RESTful API 设计原则
- 版本化的应用程序接口端点（例如，`/api/v1/resource`）。
- 采用适当 HTTP 状态代码的一致错误响应
- 请求/响应体使用 JSON

4. **测试**：
- 使用 pytest 编写单元测试
- 争取实现关键路径的高测试覆盖率
- 使用夹具进行测试设置
- 模拟外部依赖关系

### Flask最佳实践
- 阅读 ./flask-rules.md ，其中包含了使用Flask的最佳实践说明

### React（前端）最佳实践

1. **项目结构**：
```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── hooks/          # Custom React hooks
│   ├── pages/          # Page components
│   ├── services/       # API service functions
│   ├── store/          # State management
│   ├── styles/         # Global styles and themes
│   ├── types/          # TypeScript type definitions
│   └── utils/          # Helper functions
```

2. **代码样式**：
- 使用 TypeScript 实现类型安全
- 使用钩子跟踪功能组件模式
- 使用 ESLint 和 Prettier 进行代码格式化
- 遵循组件构成模式

3. **状态管理**：
- 使用 React 上下文 API 获取全局状态
- 考虑使用 Zustand 或 Redux 满足复杂的状态要求
- 尽可能将组件状态保持在本地
- 使用 React 查询进行服务器状态管理

4. **UI组件**：
- 必须遵循**Shadcn/UI最佳实践**
- 必须使用shadcn/ui组件，除非沟通特殊需求，否则不要自行实现组件
- 为第三方组件创建抽象层
- 使用 Tailwind CSS 实施响应式设计
- 遵循原子设计原则
- UI展示的时间需要根据当前系统时区进行转换（后端接口查询到的时间都是UTC+0时间）

### Shadcn/UI最佳实践
- 阅读 ./shadcnui-rules.md ，其中包含了使用shadcn/ui的最佳实践说明

### Tauri最佳实践

1. **安全考虑因素**：
- 限制 `tauri.conf.json` 中允许的 API
- 使用 allowlist 模式访问文件系统
- 验证所有用户输入
- 为 Rust 代码实现正确的错误处理

2. **性能优化**：
- 尽量减少主线程阻塞操作
- 使用 async/await 进行输入/输出操作
- 在 Rust 代码中实施适当的内存管理
- 优化分配资产的大小

3. **跨平台兼容性**：
- 尽可能使用与平台无关的应用程序接口
- 处理特定平台的边缘情况

4. **更新和分发**：
- Implement auto-update functionality
- Sign your application for distribution
- Use semantic versioning for releases

## 部署工作流程

1. **持续整合**：
- 设置 GitHub 操作或 Azure DevOps 管道
- 前台和后台测试自动化
- 在 CI 过程中检查代码

2. **Release Process**：
- 使用semantic versioning标记发布
- 自动生成更新日志
- 为 Windows 构建安装程序（.msi、.exe）
- 使用可信证书签署应用程序

3. **监测和记录**：
- 实施应用程序日志记录
- 考虑集成误差跟踪功能（Sentry）
- 为使用分析添加遥测功能（如适用）

## 常见问题解答

1. **Tauri构建问题**：
- 确保 Rust 工具链为最新版本
- 验证 WebView2 运行时已安装

2. **Python/Flask 问题**：
- 检查虚拟环境激活情况
- 验证所有依赖项已安装
- 使用 Flask 开发服务器调试

3. **整合问题**：
- 检查网络配置和 CORS 设置
- 在前端代码中验证 API 端点 URL

## 其他资源

- [Tauri 文档](https://v2.tauri.app/start/)
- [Tayru 配置文档](https://v1.tauri.app/v1/api/config/#allowlistconfig.protocol)
- [React 文档](https://reactjs.org/docs/getting-started.html)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [Flask 文档](https://flask.palletsprojects.com/)
- [Python 类型提示](https://docs.python.org/3/library/typing.html)