window.dash_clientside = Object.assign({}, window.dash_clientside, {
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