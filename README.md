# dashMiniSystems

#### 介绍
本仓库收集各式各样的dash应用，仓库内应用均基于[dash框架](https://blog.csdn.net/dududdu666666/article/details/142142486)和开源组件库[dash_bootstrap_components](https://github.com/facultyai/dash-bootstrap-components)、[feffery_antd_components](https://fac.feffery.tech/)开发。

#### 项目结构
dash内默认assets文件夹下存放css文件，pages文件夹存放页面文件，如需修改在应用实例化时直接配置。本仓库内的dash应用的架构均如下显示：
```
- projectName
    ─ assets    # 静态资源目录
        - css    # 存放css文件
        - imgs    # 存放图片
        - js    # 存放js文件
        - videos    # 存放视频
        - favicon.ico    # 应用icon
    - callbacks    # 回调
    - components    # 
    - configs    # 配置文件
    - models    # 数据模型
    - common    # 通用函数和组件
    - views/pages    # 页面
    - app.py    # 启动函数
    - server.py
    - requirements.txt
```  


#### 安装教程

1.  下载好相应应用完整源码解压后，在项目根目录打开终端，激活你的**Python**环境（推荐使用**3.12**），接着执行**pip install -r requirements.txt**完成依赖库安装。
2.  在终端执行**python app.py**即可启动应用，按照控制台提示的信息，浏览器访问本地**http://127.0.0.1:8050**地址即可访问应用。

#### 应用

1.  dash-stockhistory-system：股票历史行情展示系统
