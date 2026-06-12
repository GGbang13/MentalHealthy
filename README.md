# MentalHealthy

基于 Spring Boot 3 + Vue 3 的心理健康服务平台，面向用户、心理咨询师和管理员提供心理测评、咨询预约、在线沟通、科普文章、后台管理和风险预测等功能。项目同时包含前端页面、后端接口、数据库脚本以及 CatBoost 机器学习模型，适合作为毕业设计、课程设计或心理健康服务系统原型使用。

## 项目功能

- 用户端：注册登录、个人信息维护、心理测评、测评结果查看、咨询师浏览、预约咨询、在线聊天、文章阅读、通知查看。
- 咨询师端：咨询师资料维护、预约处理、用户沟通、服务评价查看。
- 管理端：用户管理、咨询师管理、文章管理、通知管理、平台数据看板。
- 心理测评：支持 PHQ-9、GAD-7 等量表相关数据处理，并结合模型进行心理风险预测。
- 实时沟通：基于 WebSocket 实现聊天连接和消息收发。
- 机器学习：使用 CatBoost 训练并保存心理健康风险预测模型，后端可通过 Python 脚本调用模型完成预测。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 后端 | Spring Boot 3.1.12、Spring Security、MyBatis-Plus、JWT、WebSocket |
| 前端 | Vue 3、Vite、TypeScript、Pinia、Vue Router、Element Plus、ECharts、Axios |
| 数据库 | MySQL、Redis |
| 机器学习 | Python、CatBoost、Pandas、Scikit-learn |
| 构建工具 | Maven、npm |

## 目录结构

```text
MentalHealthy/
├── backend/                 # Spring Boot 后端服务
│   └── src/main/
│       ├── java/            # 控制器、服务、实体、配置、权限等代码
│       └── resources/       # application.yml、Mapper XML 等资源
├── frontend/                # Vue 3 前端项目
│   ├── src/                 # 页面、组件、路由、状态管理等源码
│   └── vite.config.ts       # Vite 配置与接口代理
├── ml/                      # CatBoost 模型训练、预测脚本与模型文件
│   ├── artifacts/           # 已训练模型和指标文件
│   ├── data/                # 模型数据样例与处理数据
│   ├── scripts/             # 数据处理、训练、解释和预测脚本
│   └── tests/               # 机器学习流程测试
├── dataset/                 # 原始数据集与问卷资料
├── sql/                     # 数据库初始化脚本
└── tools/                   # 文档、答辩材料等辅助脚本
```

## 环境要求

- JDK 21
- Maven 3.8+
- Node.js 18+ / npm
- MySQL 8+
- Redis 6+
- Python 3.10+

## 数据库初始化

1. 创建数据库：

```sql
CREATE DATABASE mental_health_platform
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

2. 导入 SQL 脚本：

```powershell
mysql -u root -p mental_health_platform < sql/mental_health_platform.sql
```

3. 确认 Redis 服务已启动，默认连接地址为：

```text
localhost:6379
```

## 后端启动

进入后端目录：

```powershell
cd backend
```

根据本地环境配置数据库、Redis、JWT 和机器学习脚本路径。项目支持通过环境变量覆盖默认配置：

| 环境变量 | 默认值 | 说明 |
| --- | --- | --- |
| `SERVER_PORT` | `8080` | 后端服务端口 |
| `MYSQL_URL` | `jdbc:mysql://localhost:3306/mental_health_platform?...` | MySQL 连接地址 |
| `MYSQL_USERNAME` | `root` | MySQL 用户名 |
| `MYSQL_PASSWORD` | `mysql` | MySQL 密码 |
| `REDIS_HOST` | `localhost` | Redis 地址 |
| `REDIS_PORT` | `6379` | Redis 端口 |
| `JWT_SECRET` | `ReplaceThisJwtSecretKeyForProductionEnvironment123456` | JWT 密钥，生产环境必须修改 |
| `APP_ML_ENABLED` | `true` | 是否启用机器学习预测 |
| `APP_ML_PYTHON_COMMAND` | `python` | Python 命令 |
| `APP_ML_SCRIPT_PATH` | `../ml/predict_catboost.py` | 预测脚本路径 |
| `APP_ML_ARTIFACTS_DIR` | `../ml/artifacts` | 模型文件目录 |

启动后端：

```powershell
mvn spring-boot:run
```

接口默认地址：

```text
http://localhost:8080
```

Swagger / OpenAPI 页面：

```text
http://localhost:8080/swagger-ui/index.html
```

## 前端启动

进入前端目录：

```powershell
cd frontend
npm install
npm run dev
```

前端默认运行在：

```text
http://localhost:5173
```

开发环境中，Vite 已配置代理：

- `/api` 转发到 `http://localhost:8080`
- `/ws` 转发到 `http://localhost:8080`

## 机器学习模块

进入机器学习目录：

```powershell
cd ml
pip install -r requirements.txt
```

常用脚本：

```powershell
python train_catboost.py
python predict_catboost.py
```

扩展版数据处理、训练和解释脚本位于：

```text
ml/scripts/
```

模型文件和训练指标位于：

```text
ml/artifacts/
```

## 构建命令

后端打包：

```powershell
cd backend
mvn clean package
```

前端构建：

```powershell
cd frontend
npm run build
```

前端预览：

```powershell
npm run preview
```

## Git 提交与推送

查看当前改动：

```powershell
git status
```

提交改动：

```powershell
git add -A
git commit -m "Update project documentation"
```

推送到 GitHub：

```powershell
git push
```

## 注意事项

- 不要提交 `.env`、数据库密码、JWT 生产密钥等敏感信息。
- `node_modules/`、`target/`、`dist/`、`uploads/`、`__pycache__/` 等生成文件已在 `.gitignore` 中忽略。
- 如果 GitHub 上仍能在历史提交中看到已删除文件，说明文件已从当前版本删除，但仍存在于 Git 历史中；敏感文件需要通过重写历史的方式彻底清理。
- 本项目用于学习、毕业设计和系统原型展示，心理风险预测结果仅作辅助参考，不能替代专业心理诊断。
