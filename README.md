# LOL助手 (Loler)

一个基于 FastAPI + Pydantic 的英雄联盟数据查询服务

## 功能特点

✅ **完整的英雄数据** - 包含159个英雄的完整信息(12.6.1版本)
✅ **Pydantic 模型** - 类型安全的数据模型,自动验证
✅ **RESTful API** - 提供完整的 REST API 接口
✅ **内存加载** - 数据在启动时加载到内存,查询速度快
✅ **多种查询** - 支持ID查询、名称搜索、标签过滤等
✅ **交互式文档** - 自动生成的 Swagger UI 文档
✅ **Web 界面** - 精美的 LOL 主题 UI 界面

## 快速开始

### 1. 启动应用

```bash
uv run python run.py
```

### 2. 访问服务

- **主页:** http://localhost:8000
- **API 文档:** http://localhost:8000/docs
- **健康检查:** http://localhost:8000/health

### 3. API 示例

```bash
# 获取所有英雄
curl http://localhost:8000/api/champions

# 获取单个英雄
curl http://localhost:8000/api/champions/Yasuo

# 搜索英雄
curl http://localhost:8000/api/champions/search/剑

# 按标签获取
curl http://localhost:8000/api/champions/tag/Assassin
```

## 技术栈

- **FastAPI** - 现代化的 Python Web 框架
- **Pydantic** - 数据验证和模型
- **Jinja2** - 模板引擎
- **Uvicorn** - ASGI 服务器
- **Python 3.12** - 编程语言

## 项目结构

```
loler/
├── models/                         # Pydantic 模型
│   └── champion.py                 # 英雄数据模型
├── services/                       # 业务逻辑
│   └── champion_service.py         # 英雄数据服务
├── dragontail/                     # 游戏数据
│   └── 12.6.1/
│       └── data/zh_CN/
│           └── championFull.json   # 英雄完整数据
├── app.py                          # FastAPI 应用
├── run.py                          # 启动脚本
└── test_champion_data.py           # 测试脚本
```

## 数据统计

- **英雄总数:** 159
- **数据版本:** 12.6.1
- **Pydantic 模型:** 9个
- **API 端点:** 5个

## 文档

- [快速开始](快速开始.md) - 快速上手指南
- [使用说明](使用说明.md) - 详细使用说明
- [API使用示例](API使用示例.md) - API 使用示例
- [实现总结](实现总结.md) - 技术实现总结

## 测试

```bash
uv run python test_champion_data.py
```

## 开发

应用使用热重载模式,修改代码后自动重启:

```bash
uv run python run.py
```

## License

MIT

## 下一步

- [x] 复活时间
- [ ] 上线时间
- [x] ai对比分析装备和英雄
- [ ] ai分析符文
- [ ] ai分析版本