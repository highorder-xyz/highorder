
from usr.render import PageRender
from usr.boot import bootup

bootup()

if __name__ == '__main__':
    render = PageRender(None)
    page1 = {
                "name": "",
                "route": "/dashboard",
                "refresh": {
                    "interval": 3
                },
                "locals": {},
                "elements": [
                    {
                        "type": "column",
                        "elements": [
                            {
                                "type": "clock",
                                "style": {
                                    "tags": [
                                        "digital"
                                    ]
                                },
                                "show_date": True
                            },
                            {
                                "type": "plain-text",
                                "text": "新的todo，测试owner  (11月27日)",
                                "style": {
                                    "tags": ["strike"]
                                }
                            },
                            {
                                "type": "plain-text",
                                "text": "有一个todo  (11月27日)",
                                "style": {
                                    "tags": ["strike"]
                                }
                            },
                            {
                                "type": "plain-text",
                                "text": "还有一个todo  (。。。)",
                                "style": {
                                    "tags": ["strike"]
                                }
                            },
                            {
                                "type": "divider"
                            },
                            {
                                "type": "plain-text",
                                "text": "第二个测试用的LIST"
                            },
                            {
                                "type": "progressbar",
                                "style": {
                                    "size_hint": 5
                                },
                                "percent": 66.66666666666667
                            },
                            {
                                "type": "divider"
                            },
                            {
                                "type": "plain-text",
                                "text": "测试的TodoList 标题"
                            },
                            {
                                "type": "progressbar",
                                "style": {
                                    "size_hint": 5
                                },
                                "percent": 0
                            },
                            {
                                "type": "divider"
                            },
                            {
                                "type": "plain-text",
                                "text": "这是第一个todolist"
                            },
                            {
                                "type": "progressbar",
                                "style": {
                                    "size_hint": 5
                                },
                                "percent": 25
                            }
                        ],
                        "style": {
                            "size_hint": 3
                        }
                    }
                ]
            }

    page2 = {
        "type": "page",
        "route": "/",
        "elements": [
            {
                "type": "plain-text",
                "text": "设备初始化，请选择设备类型："
            },
            {
                "type": "row",
                "elements": [
                    {
                        "type": "button",
                        "text": "会议室设备"
                    },
                    {
                        "type": "qrcode",
                        "code": "saomaodenglu",
                        "text": "扫描登录"
                    }
                ]
            }
        ]
    }

    render.render(page1)