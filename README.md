# FootHub - 竞彩足球资讯网站

一个基于 Flask + Tavily API 的竞彩足球资讯网站，提供实时赛事数据和专业分析。

## 功能特点

- 实时获取竞彩足球赛事数据
- 显示赔率和让球信息
- Tavily AI 智能分析赛事资讯
- 浅色主题界面，响应式设计

## 技术栈

- **后端**: Python Flask
- **前端**: HTML5 + Bootstrap 5
- **数据源**: 500彩票网竞彩足球
- **AI分析**: Tavily API

## 项目结构

```
FootHub/
├── backend/
│   ├── app.py                 # Flask主应用
│   ├── requirements.txt       # Python依赖
│   ├── scraper/               # 爬虫模块
│   │   └── scraper_500.py     # 500彩票网爬虫
│   └── services/              # 服务模块
│       ├── tavily_service.py  # Tavily API服务
│       └── deepseek_service.py # DeepSeek服务(可选)
├── frontend/
│   └── index.html            # 前端页面
├── .gitignore
├── start.bat                 # Windows启动脚本
└── README.md
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/LP2425158457/FootHub.git
cd FootHub
```

### 2. 配置后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写API密钥：

```
TAVILY_API_KEY=your_tavily_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 4. 启动服务

**方式一：使用启动脚本**
```bash
start.bat
```

**方式二：手动启动**
```bash
# 启动后端
cd backend
venv\Scripts\python app.py

# 启动前端（新终端）
cd frontend
python -m http.server 8080
```

### 5. 访问应用

- 前端页面: http://localhost:8080
- 后端API: http://localhost:5000

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/matches` | GET | 获取赛事列表 |
| `/api/match/<match_id>/news` | GET | 获取赛事资讯 |
| `/api/team/<team_name>/info` | GET | 获取球队信息 |
| `/api/league/<league_name>/news` | GET | 获取联赛新闻 |

## 获取API密钥

- **Tavily API**: https://tavily.com/
- **DeepSeek API**: https://platform.deepseek.com/

## 注意事项

- 本项目仅供学习参考
- 请理性购彩，量力而行
- 数据来源于公开网站，请遵守相关法律法规

## License

MIT License
