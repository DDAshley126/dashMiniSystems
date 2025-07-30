import json
import dash
from dash import Output, Input, State, ClientsideFunction, ALL
from app import app
import feffery_antd_components as fac
import feffery_utils_components as fuc
import feffery_markdown_components as fmc
from custom_service_model import ollama_llm, ollama_rag, apiModel, apiRAGModel, apiDify


app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="limitSwitch"),
    Input({'type': 'custom-service', 'index': ALL}, "checked")
)


# @app.callback(
#     Output('rag-files', 'children'),
#     Input({'type': 'custom-service', 'index': 'rag'}, 'checked')
# )
# def update(checked):
#     if checked:
#         return [
#             fac.AntdUpload(id='upload-files', apiUrl='/core/upload', fileMaxSize=9, fileTypes=['pdf'], buttonContent='请上传pdf文件', confirmBeforeDelete=True),
#         ]
#     else:
#         return ''


@app.callback(
    Output('rag-files', 'children'),
    Input({'type': 'custom-service', 'index': 'apiRAG'}, 'checked')
)
def update(checked):
    if checked:
        return [
            fac.AntdUpload(id='upload-files', apiUrl='/core/upload', fileMaxSize=9, fileTypes=['pdf'], buttonContent='请上传pdf文件', confirmBeforeDelete=True),
        ]
    else:
        return ''


@app.callback(
    Output('rag-files-info', 'data'),
    [
        Input('upload-files', 'listUploadTaskRecord'),
        Input('rag-files-info', 'data'),
    ],
    prevent_initial_call=True,
)
def upload_callback_demo(listUploadTaskRecord, data):
    if data is None:
        data = json.dumps([])
    if listUploadTaskRecord:
        data = json.loads(data)
        data.append(
            {
                'uid': listUploadTaskRecord[-1]['uid'],
                'fileName': listUploadTaskRecord[-1]['fileName']
            }
        )
        return json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        )


@app.callback(
    [
        Output('chat-records', 'children'),
        Output('new-question-input', 'value'),
        Output('send-new-question', 'loading')
    ],
    [
        Input({'type': 'custom-service', 'index': 'normal'}, 'checked'),
        Input({'type': 'custom-service', 'index': 'rag'}, 'checked'),
        Input({'type': 'custom-service', 'index': 'api'}, 'checked'),
        Input({'type': 'custom-service', 'index': 'apiRAG'}, 'checked'),
        Input('prompt', 'value'),
        Input('rag-files-info', 'data'),
        Input('send-new-question', 'nClicks'),
     ],
    [
        State('new-question-input', 'value'),
        State('chat-records', 'children')
    ],
    prevent_initial_call=True
)
def send_new_question(normal_checked, rag_checked, api_checked, api_rag_checked, prompt, files_info, nClicks, question, origin_children):
    if normal_checked and nClicks and question:
        response = ollama_llm(prompt=prompt, question=question)
        return [
            [
                *origin_children,
                # 渲染当前问题
                fac.AntdSpace(
                    [
                        fac.AntdAvatar(
                            mode='text',
                            text='我',
                            style={
                                'background': '#1890ff'
                            }
                        ),
                        fuc.FefferyDiv(
                            fac.AntdParagraph(
                                [
                                    question
                                ],
                                copyable=True
                            ),
                            style={
                                'background': 'white',
                                'borderRadius': 6,
                                'padding': 15,
                                'boxShadow': '0 2px 12px 0 rgb(0 0 0 / 10%)',
                                'maxWidth': 680
                            }
                        )
                    ],
                    align='start',
                    style={
                        'padding': '10px 15px',
                        'width': '100%',
                        'flexDirection': 'row-reverse'
                    }
                ),
                # 渲染当前问题的回复
                fac.AntdSpace(
                    [
                        fac.AntdAvatar(
                            mode='icon',
                            icon='antd-robot',
                            style={
                                'background': '#1890ff'
                            }
                        ),
                        fuc.FefferyDiv(
                            fmc.FefferyMarkdown(
                                markdownStr=response,
                                codeTheme='a11y-dark'
                            ),
                            style={
                                'background': 'white',
                                'borderRadius': 6,
                                'padding': 15,
                                'boxShadow': '0 2px 12px 0 rgb(0 0 0 / 10%)',
                                'maxWidth': 680
                            }
                        )
                    ],
                    align='start',
                    style={
                        'padding': '10px 15px',
                        'width': '100%'
                    }
                )
            ],
            None,
            False
        ]
    if rag_checked and nClicks and question:
        files_info = json.loads(files_info)
        files_path = ['./upload/' + i['fileName'] for i in files_info]  # 暂时只能写绝对路径
        response = ollama_rag(prompt=prompt, files_path=files_path, question=question)
        return [
            [
                *origin_children,
                # 渲染当前问题
                fac.AntdSpace(
                    [
                        fac.AntdAvatar(
                            mode='text',
                            text='我',
                            style={
                                'background': '#1890ff'
                            }
                        ),
                        fuc.FefferyDiv(
                            fac.AntdParagraph(
                                [
                                    question
                                ],
                                copyable=True
                            ),
                            style={
                                'background': 'rgb(149, 236, 105)',
                                'borderRadius': 6,
                                'padding': 15,
                                'boxShadow': '0 2px 12px 0 rgb(0 0 0 / 10%)',
                                'maxWidth': 680
                            }
                        )
                    ],
                    align='start',
                    style={
                        'padding': '10px 15px',
                        'width': '100%',
                        'flexDirection': 'row-reverse'
                    }
                ),
                # 渲染当前问题的回复
                fac.AntdSpace(
                    [
                        fac.AntdAvatar(
                            mode='icon',
                            icon='antd-robot',
                            style={
                                'background': '#1890ff'
                            }
                        ),
                        fuc.FefferyDiv(
                            fmc.FefferyMarkdown(
                                markdownStr=response,
                                codeTheme='a11y-dark'
                            ),
                            style={
                                'background': 'white',
                                'borderRadius': 6,
                                'padding': 15,
                                'boxShadow': '0 2px 12px 0 rgb(0 0 0 / 10%)',
                                'maxWidth': 680
                            }
                        )
                    ],
                    align='start',
                    style={
                        'padding': '10px 15px',
                        'width': '100%'
                    }
                )
            ],
            None,
            False
        ]
    if api_checked and nClicks and question:
        response = apiModel().api_model(question)
        return [
            [
                *origin_children,
                # 渲染当前问题
                fac.AntdSpace(
                    [
                        fac.AntdAvatar(
                            mode='text',
                            text='我',
                            style={
                                'background': '#1890ff'
                            }
                        ),
                        fuc.FefferyDiv(
                            fac.AntdParagraph(
                                [
                                    question
                                ],
                                copyable=True
                            ),
                            style={
                                'background': 'rgb(149, 236, 105)',
                                'borderRadius': 6,
                                'padding': 15,
                                'boxShadow': '0 2px 12px 0 rgb(0 0 0 / 10%)',
                                'maxWidth': 680
                            }
                        )
                    ],
                    align='start',
                    style={
                        'padding': '10px 15px',
                        'width': '100%',
                        'flexDirection': 'row-reverse'
                    }
                ),
                # 渲染当前问题的回复
                fac.AntdSpace(
                    [
                        fac.AntdAvatar(
                            mode='icon',
                            icon='antd-robot',
                            style={
                                'background': '#1890ff'
                            }
                        ),
                        fuc.FefferyDiv(
                            fmc.FefferyMarkdown(
                                markdownStr=response,
                                codeTheme='a11y-dark'
                            ),
                            style={
                                'background': 'white',
                                'borderRadius': 6,
                                'padding': 15,
                                'boxShadow': '0 2px 12px 0 rgb(0 0 0 / 10%)',
                                'maxWidth': 680
                            }
                        )
                    ],
                    align='start',
                    style={
                        'padding': '10px 15px',
                        'width': '100%'
                    }
                )
            ],
            None,
            False
        ]
    if api_rag_checked and nClicks and question:
        files_info = json.loads(files_info)
        files_path = ['./upload/' + i['fileName'] for i in
                      files_info]  # 暂时只能写绝对路径
        response = apiRAGModel().api_model(files_path, question)
        return [
            [
                *origin_children,
                # 渲染当前问题
                fac.AntdSpace(
                    [
                        fac.AntdAvatar(
                            mode='text',
                            text='我',
                            style={
                                'background': '#1890ff'
                            }
                        ),
                        fuc.FefferyDiv(
                            fac.AntdParagraph(
                                [
                                    question
                                ],
                                copyable=True
                            ),
                            style={
                                'background': 'rgb(149, 236, 105)',
                                'borderRadius': 6,
                                'padding': 15,
                                'boxShadow': '0 2px 12px 0 rgb(0 0 0 / 10%)',
                                'maxWidth': 680
                            }
                        )
                    ],
                    align='start',
                    style={
                        'padding': '10px 15px',
                        'width': '100%',
                        'flexDirection': 'row-reverse'
                    }
                ),
                # 渲染当前问题的回复
                fac.AntdSpace(
                    [
                        fac.AntdAvatar(
                            mode='icon',
                            icon='antd-robot',
                            style={
                                'background': '#1890ff'
                            }
                        ),
                        fuc.FefferyDiv(
                            fmc.FefferyMarkdown(
                                markdownStr=response,
                                codeTheme='a11y-dark'
                            ),
                            style={
                                'background': 'white',
                                'borderRadius': 6,
                                'padding': 15,
                                'boxShadow': '0 2px 12px 0 rgb(0 0 0 / 10%)',
                                'maxWidth': 680
                            }
                        )
                    ],
                    align='start',
                    style={
                        'padding': '10px 15px',
                        'width': '100%'
                    }
                )
            ],
            None,
            False
        ]
    return dash.no_update



