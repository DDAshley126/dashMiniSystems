// 改造console.error()以隐藏无关痛痒的警告信息
const originalConsoleError = console.error;
console.error = function (...args) {
    // 检查args中是否包含需要过滤的内容
    const shouldFilter = args.some(arg => typeof arg === 'string' && arg.includes('Warning:'));

    if (!shouldFilter) {
        originalConsoleError.apply(console, args);
    }
};

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside_basic: {
        // 处理核心页面侧边栏展开/收起
        handleSideCollapse: (nClicks, originIcon, originHeaderSideStyle, coreConfig) => {
            // 若先前为展开状态
            if (originIcon === 'antd-menu-fold') {
                return [
                    // 更新图标
                    'antd-menu-unfold',
                    // 更新页首侧边容器样式
                    {
                        ...originHeaderSideStyle,
                        width: 110
                    },
                    // 更新页首标题样式
                    {
                        display: 'none'
                    },
                    // 更新侧边菜单容器样式
                    {
                        width: 110
                    },
                    // 更新侧边菜单折叠状态
                    true
                ]
            } else {
                return [
                    // 更新图标
                    'antd-menu-fold',
                    // 更新页首侧边容器样式
                    {
                        ...originHeaderSideStyle,
                        width: coreConfig.core_side_width
                    },
                    // 更新页首标题样式
                    {},
                    // 更新侧边菜单容器样式
                    {
                        width: coreConfig.core_side_width
                    },
                    // 更新侧边菜单折叠状态
                    false
                ]
            }
        },
        // 控制页面搜索切换页面的功能
        handleCorePageSearch: (value) => {
            if (value) {
                let pathname = value.split('|')[0]
                // 更新pathname
                window.location.pathname = pathname
            }
        },
        // 控制ctrl+k快捷键触发页面搜索框聚焦
        handleCorePageSearchFocus: (pressedCounts) => {
            return [true, pressedCounts.toString()]
        }
    },
    clientside: {
        limitSwitch: () => {
            // 获取当前打开状态的组件
            let checked_list = window.dash_clientside.callback_context.inputs_list[0].filter(
                item => item.value
            )
            // 获取本次回调触发源
            let triggered_id = window.dash_clientside.callback_context.triggered_id

            // 更新非本次触发源，且状态为打开的开关 -> 关闭
            if (checked_list.length == 2) {
                for (let item of checked_list) {
                    if (item.id.index != triggered_id.index) {
                        window.dash_clientside.set_props(
                            item.id,
                            { checked: false }
                        )
                    }
                }
            }
        }
    }
});