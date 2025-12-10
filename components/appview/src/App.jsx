import React from 'react'
import { useAppStore } from './store/appStore'
import { 
  NavBar, 
  Modal, 
  Alert, 
  Button, 
  Title, 
  Paragraph, 
  Divider, 
  Link, 
  Icon, 
  IconText, 
  IconTitle, 
  ProgressBar, 
  Row, 
  Column, 
  Card, 
  Input, 
  Checkbox, 
  Radio, 
  Select, 
  Switch, 
  TextArea,
  Badge,
  Dropdown,
  Tooltip,
  Tag,
  Avatar,
  Breadcrumb,
  Tabs,
  List,
  DataTable,
  Pagination,
  Accordion,
  Slider,
  Rating,
  Upload,
  Calendar,
  Menu,
  Carousel,
  Timeline,
  Stepper,
  ColorPicker,
  Tree
} from './components/ui'

function App() {
  const {
    theme,
    locale,
    loading,
    page,
    modal,
    alerts,
    setTheme,
    setLocale,
    navigateTo,
    executeAction,
    executeCommand,
    removeAlert
  } = useAppStore()

  // Navigation handlers - mirror Vue App methods
  const handleHomeClick = () => {
    navigateTo('/')
  }

  const handleBackClick = () => {
    window.history.back()
  }

  // Command execution - mirror Vue handleImmediateCommands
  const handleCommand = async (command) => {
    await executeCommand(command)
  }

  // Action execution - mirror Vue executeAction
  const handleAction = async (action, args = {}) => {
    await executeAction(action, args, { route: page.route })
  }

  return (
    <div data-theme={theme} className="min-h-screen bg-base-200 text-base-content">
      {/* Navigation Bar - mirrors Vue NavBar */}
      <NavBar
        title="HighOrder React App"
        showHome={true}
        showBack={page.route !== '/'}
        onHomeClicked={handleHomeClick}
        onBackClicked={handleBackClick}
      />

      {/* Theme and Locale Controls */}
      <div className="navbar bg-base-100 shadow-sm">
        <div className="flex-1 px-2">
          <span className="text-lg font-semibold">Settings</span>
        </div>
        <div className="flex-none flex items-center gap-2 pr-4">
          <select
            className="select select-sm select-bordered"
            value={locale}
            onChange={e => setLocale(e.target.value)}
          >
            <option value="zh-CN">简体中文</option>
            <option value="en">English</option>
          </select>
          <select
            className="select select-sm select-bordered"
            value={theme}
            onChange={e => setTheme(e.target.value)}
          >
            <option value="light">light</option>
            <option value="dark">dark</option>
            <option value="cupcake">cupcake</option>
          </select>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 space-y-6">
        {/* Page Info */}
        <div className="card bg-base-100 shadow-md">
          <div className="card-body">
            <h2 className="card-title">React App Architecture</h2>
            <p>Current Route: <code>{page.route}</code></p>
            <p>Page Version: <code>{page.version}</code></p>
            <p>Session Started: <code>{useAppStore.getState().sessionStarted ? 'Yes' : 'No'}</code></p>
            <p>Privacy Agreed: <code>{useAppStore.getState().privacyAgreed ? 'Yes' : 'No'}</code></p>
          </div>
        </div>

        {/* Demo Actions - mirror Vue action system */}
        <div className="card bg-base-100 shadow-md">
          <div className="card-body">
            <h2 className="card-title">Action System Demo</h2>
            <div className="flex gap-2 flex-wrap">
              <button 
                className="btn btn-primary"
                onClick={() => handleAction('route.navigate_to', { route: '/demo' })}
              >
                Navigate to /demo
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => handleCommand({ name: 'show_alert', args: { text: 'Hello from React!', title: 'Demo Alert' } })}
              >
                Show Alert
              </button>
              <button 
                className="btn btn-accent"
                onClick={() => useAppStore.getState().openModal('demo-modal', { title: 'Demo Modal', text: 'This is a modal!' })}
              >
                Show Modal
              </button>
            </div>
          </div>
        </div>

        {/* Store State Inspector */}
        <div className="card bg-base-100 shadow-md">
          <div className="card-body">
            <h2 className="card-title">Store State</h2>
            <details className="collapse collapse-arrow">
              <summary className="collapse-title text-lg font-medium">
                Click to expand store state
              </summary>
              <div className="collapse-content">
                <pre className="text-sm overflow-auto">
                  {JSON.stringify({
                    theme,
                    locale,
                    loading,
                    page: { name: page.name, route: page.route, version: page.version },
                    modal: { hasCurrent: !!modal.current, stackSize: modal.stack.length },
                    alertsCount: alerts.length
                  }, null, 2)}
                </pre>
              </div>
            </details>
          </div>
        </div>

        {/* UI Components Showcase */}
        <div className="card bg-base-100 shadow-md">
          <div className="card-body">
            <h2 className="card-title">UI Components Showcase</h2>
            <p className="text-base-content/70 mb-4">展示所有迁移的UI组件</p>
            
            {/* Text Components */}
            <div className="space-y-4">
              <Title title="标题组件" level={2} sub_title="这是一个副标题" />
              <Paragraph 
                text="这是段落组件。支持多行文本显示。可以用来展示各种内容。" 
                align="center"
              />
              <Divider />
            </div>

            {/* Icon Components */}
            <div className="space-y-4">
              <IconTitle 
                title="图标标题组件" 
                icon="star" 
                level={3} 
                icon_size={32} 
                color="primary"
              />
              <Row gap={3}>
                <Icon icon="home" size={24} color="primary" />
                <IconText text="图标文本" icon="favorite" size={20} color="error" />
                <Link text="链接组件" onClick={() => console.log('Link clicked')} />
              </Row>
            </div>

            {/* Form Components */}
            <div className="space-y-4">
              <Title title="表单组件" level={3} />
              <Row gap={2}>
                <Input placeholder="输入框" value="" />
                <Select 
                  placeholder="选择框" 
                  options={['选项1', '选项2', '选项3']} 
                  value=""
                />
              </Row>
              <Row gap={2}>
                <Checkbox label="复选框" />
                <Radio label="单选框" />
                <Switch label="开关" />
              </Row>
              <TextArea placeholder="文本域" rows={3} />
            </div>

            {/* Progress and Layout */}
            <div className="space-y-4">
              <Title title="进度和布局" level={3} />
              <ProgressBar value={75} max={100} showText color="primary" />
              <Row gap={2}>
                <Button text="按钮组件" color="primary" />
                <Button text="次要按钮" color="secondary" />
                <Button text="强调按钮" color="accent" />
              </Row>
            </div>

            {/* Card Component */}
            <div className="space-y-4">
              <Title title="卡片组件" level={3} />
              <Card 
                title="卡片标题" 
                subtitle="卡片副标题" 
                content="这是一个卡片组件的内容。可以包含各种信息。"
                actions={[
                  { text: "取消", color: "secondary" },
                  { text: "确定", color: "primary" }
                ]}
              />
            </div>

            {/* Advanced Components */}
            <div className="space-y-4">
              <Title title="高级组件" level={3} />
              <Row gap={2}>
                <Badge text="徽章" color="primary" />
                <Badge text="成功" color="success" variant="outline" />
                <Tag text="标签" color="accent" closable />
                <Avatar src="" alt="用户" size="small" status="online" />
              </Row>
              
              <Breadcrumb 
                items={[
                  { label: "首页", href: "/" },
                  { label: "用户", href: "/users" },
                  { label: "详情", active: true }
                ]}
              />
              
              <Dropdown trigger="hover" placement="bottom">
                <Button text="下拉菜单" color="primary" />
                <ul>
                  <li><a>选项 1</a></li>
                  <li><a>选项 2</a></li>
                </ul>
              </Dropdown>
              
              <Tooltip text="这是提示文本">
                <Button text="悬停提示" color="secondary" />
              </Tooltip>
            </div>

            {/* Data Components */}
            <div className="space-y-4">
              <Title title="数据组件" level={3} />
              <List 
                items={[
                  { title: "列表项 1", subtitle: "副标题" },
                  { title: "列表项 2", subtitle: "副标题" }
                ]}
                variant="hover"
              />
              
              <DataTable 
                data={[
                  { name: "张三", age: 25, city: "北京" },
                  { name: "李四", age: 30, city: "上海" }
                ]}
                columns={[
                  { field: "name", header: "姓名" },
                  { field: "age", header: "年龄" },
                  { field: "city", header: "城市" }
                ]}
                paginator={false}
              />
              
              <Pagination 
                current={1}
                total={50}
                pageSize={10}
                showSizeChanger={true}
                showQuickJumper={true}
              />
            </div>

            {/* Interactive Components */}
            <div className="space-y-4">
              <Title title="交互组件" level={3} />
              <Row gap={4}>
                <div className="flex-1">
                  <Slider 
                    value={50} 
                    min={0} 
                    max={100} 
                    showValue={true}
                    color="primary"
                  />
                </div>
                <div className="flex-1">
                  <Rating 
                    value={4} 
                    max={5} 
                    showValue={true}
                    color="primary"
                  />
                </div>
              </Row>
              
              <Accordion 
                items={[
                  { title: "手风琴项 1", content: "这是第一个手风琴项的内容" },
                  { title: "手风琴项 2", content: "这是第二个手风琴项的内容" }
                ]}
                allowMultiple={false}
              />
            </div>

            {/* Form Components */}
            <div className="space-y-4">
              <Title title="表单组件" level={3} />
              <Row gap={4}>
                <div className="flex-1">
                  <Calendar 
                    placeholder="选择日期"
                    mode="single"
                  />
                </div>
                <div className="flex-1">
                  <Upload 
                    accept="image/*"
                    multiple={false}
                    uploadText="上传图片"
                    dragText="拖拽图片到此处"
                  />
                </div>
              </Row>
            </div>

            {/* Navigation Components */}
            <div className="space-y-4">
              <Title title="导航组件" level={3} />
              <Menu 
                items={[
                  { key: '1', label: '首页', icon: 'home' },
                  { 
                    key: '2', 
                    label: '用户管理', 
                    icon: 'people',
                    children: [
                      { key: '2-1', label: '用户列表' },
                      { key: '2-2', label: '用户权限' }
                    ]
                  },
                  { key: '3', label: '设置', icon: 'settings' }
                ]}
                mode="vertical"
                collapsed={false}
              />
            </div>

            {/* Advanced Display Components */}
            <div className="space-y-4">
              <Title title="高级展示组件" level={3} />
              <Carousel 
                items={[
                  { title: "轮播图 1", subtitle: "第一个轮播项" },
                  { title: "轮播图 2", subtitle: "第二个轮播项" },
                  { title: "轮播图 3", subtitle: "第三个轮播项" }
                ]}
                autoplay={true}
                showIndicators={true}
                showNavigators={true}
              />
              
              <Timeline 
                items={[
                  { title: "步骤 1", content: "这是第一个步骤的内容", date: "2025-01-01" },
                  { title: "步骤 2", content: "这是第二个步骤的内容", date: "2025-01-02" },
                  { title: "步骤 3", content: "这是第三个步骤的内容", date: "2025-01-03" }
                ]}
                showDate={true}
              />
              
              <Stepper 
                steps={[
                  { title: "步骤 1", description: "第一步描述" },
                  { title: "步骤 2", description: "第二步描述" },
                  { title: "步骤 3", description: "第三步描述" }
                ]}
                current={1}
              />
            </div>

            {/* Utility Components */}
            <div className="space-y-4">
              <Title title="工具组件" level={3} />
              <Row gap={4}>
                <div className="flex-1">
                  <ColorPicker value="#ff0000" />
                </div>
                <div className="flex-1">
                  <Tree 
                    data={[
                      { key: '1', title: '根节点', children: [
                        { key: '1-1', title: '子节点 1' },
                        { key: '1-2', title: '子节点 2' }
                      ]}
                    ]}
                    checkable={true}
                    showIcon={true}
                  />
                </div>
              </Row>
            </div>
          </div>
        </div>
      </main>

      {/* Loading Overlay - mirror Vue loading state */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="loading loading-spinner loading-lg text-primary"></div>
        </div>
      )}

      {/* Alerts - mirror Vue AlertHelper */}
      {alerts.map(alert => (
        <Alert
          key={alert.id}
          message={alert.message}
          header={alert.header}
          severity={alert.severity || 'info'}
          position={alert.position || 'top'}
          duration={alert.duration || 3000}
          show={true}
          onHide={() => removeAlert(alert.id)}
        />
      ))}

      {/* Modals - mirror Vue ModalHelper */}
      {modal.current && (
        <Modal
          show={true}
          title={modal.current.options.title || ''}
          text={modal.current.options.text || ''}
          content_html={modal.current.options.content_html || ''}
          actions={modal.current.options.actions || []}
          actionConfirmText={modal.current.options.actionConfirmText}
          actionCancelText={modal.current.options.actionCancelText}
          onModalConfirmed={() => {
            if (modal.current.options.onModalConfirmed) {
              modal.current.options.onModalConfirmed()
            }
            useAppStore.getState().closeModal(modal.current.modalId)
          }}
          onModalCancelled={() => {
            if (modal.current.options.onModalCancelled) {
              modal.current.options.onModalCancelled()
            }
            useAppStore.getState().closeModal(modal.current.modalId)
          }}
          onModalClosed={() => {
            useAppStore.getState().closeModal(modal.current.modalId)
          }}
        />
      )}
    </div>
  )
}

export default App
