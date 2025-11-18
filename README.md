
# Alien Invasion - 作业项目说明

## 1. 项目概述（Project Overview）

本项目基于经典游戏《外星人入侵》（Alien Invasion）进行开发，在原游戏基础上新增核心玩法与体验优化，完成课程作业的要求。

## 2. 环境配置（Environment Setup）

### 前置依赖
- Python 版本：3.8 及以上  
- 核心库：Pygame  

### 安装步骤

1. **安装 Python**  
   从 [Python 官网](https://www.python.org/downloads/) 下载对应系统版本（Windows/macOS/Linux），安装时勾选「Add Python to PATH」。

2. **安装 Pygame**  
   打开终端/命令提示符，执行以下命令：
   ```bash
   pip install pygame
   ```

3. **克隆仓库（Clone Repository）**
   ```bash
   git clone https://github.com/RobertAlanJohnson/python2.git
   cd python2
   ```

4. **运行游戏（Run the Game）**  
   在项目根目录下执行主程序脚本：
   ```bash
   python alien_invasion.py
   ```

### 游戏控制说明（Controls）
- 方向键 `←` `→`：控制飞船左右移动  
- 空格键（Spacebar）：发射子弹  
- 字母 `Q`：退出游戏  

## 3. 项目结构（Project Structure）

```plaintext
python2/
├── alien_invasion.py       # 游戏主程序（入口文件）
├── settings.py             # 游戏配置文件（分辨率、速度、音效等参数）
├── game_stats.py           # 游戏状态管理（得分、最高分、游戏进度）
├── sounds/                 # 音效资源文件夹
│   ├── shoot.wav           # 射击音效
│   ├── explode.wav         # 爆炸音效（外星人被击中）
│   ├── background.mp3      # 背景音乐
│   └── shield_hit.wav      # 护盾被击音效
└── README.md               # 项目说明文档（本文件）
```

## 4. 实现功能（Implemented Features）

### 核心扩展功能
- **外星人子弹系统**：外星人将随机向下发射子弹，增加游戏对抗性  
- **飞船护盾机制**：为玩家飞船添加可摧毁护盾，护盾可抵御双方子弹（被子弹击中后逐步损坏）  
- **音效系统集成**：通过 `pygame.mixer` 模块添加射击、爆炸、护盾撞击等音效，提升沉浸感  
- **持久化最高分**：解决原游戏重启后最高分重置问题，通过文件读写实现最高分永久保存（程序退出时写入、启动时读取）  

### 基础功能保留
- 飞船移动与子弹发射  
- 外星人编队移动与碰撞检测  
- 得分统计与关卡进阶  

## 5. 常见问题与注意事项（Notes）

- **音效文件缺失报错（`FileNotFoundError`）**：  
  - 确认 `sounds/` 文件夹存在且包含 `shoot.wav`、`explode.wav`、`shield_hit.wav` 三个文件  
  - 音效资源可从免费平台获取：[FreeSound](https://freesound.org/)、[ZapSplat](https://www.zapsplat.com/)，下载后放入 `sounds/` 文件夹即可  

- **Pygame 初始化失败**：  
  - 检查 Python 版本是否兼容（建议 3.8–3.11）  
  - 重新安装 Pygame：  
    ```bash
    pip uninstall pygame && pip install pygame
    ```

- **最高分未保存**：  
  - 确保程序正常退出（通过 `Q` 键或关闭窗口，避免强制终止）  
  - 检查文件读写权限（项目目录需允许创建 / 修改文件）  

## 6. 项目仓库（GitHub Repository）

完整代码与提交历史：  
🔗 [https://github.com/RobertAlanJohnson/python2](https://github.com/RobertAlanJohnson/python2)

## 7. 联系方式

若有问题可通过邮箱联系：  
📧 `RobertAlanJohnson@proton.me`
