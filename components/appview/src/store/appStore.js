import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'

// App Core State - mirrors Vue AppCore + Page architecture
export const useAppStore = create(subscribeWithSelector((set, get) => ({
  // App Identity & Config
  appId: 'react-app',
  config: {
    baseUrl: '',
    assetsUrl: '',
    privacyUrl: '',
  },
  
  // Page State - mirrors Vue Page class
  page: {
    name: 'app',
    route: '/',
    elements: [],
    locals: {},
    version: 0
  },
  
  // UI State
  theme: 'light',
  locale: 'zh-CN',
  loading: false,
  
  // Modal & Alert System - mirrors Vue helpers
  modal: {
    current: null,
    stack: [],
    root: null
  },
  alerts: [],
  
  // Session & Platform
  sessionStarted: false,
  privacyAgreed: false,
  platform: {
    name: 'web',
    userAgent: navigator.userAgent
  },
  
  // Actions
  setTheme: (theme) => set({ theme }),
  setLocale: (locale) => set({ locale }),
  setLoading: (loading) => set({ loading }),
  
  // Page Management - mirrors Vue Page methods
  updatePage: (pageData) => set(state => ({
    page: {
      ...state.page,
      ...pageData,
      version: state.page.version + 1
    }
  })),
  
  resetPage: () => set(state => ({
    page: {
      ...state.page,
      elements: [],
      locals: {},
      version: state.page.version + 1
    }
  })),
  
  setPageLocals: (locals) => set(state => ({
    page: {
      ...state.page,
      locals: { ...state.page.locals, ...locals }
    }
  })),
  
  // Navigation - mirrors Vue navigateTo
  navigateTo: async (route) => {
    set({ loading: true })
    // TODO: Implement navigation logic similar to Vue AppCore.navigateTo
    set(state => ({
      page: { ...state.page, route },
      loading: false
    }))
  },
  
  // Modal Management - mirrors Vue ModalHelper
  openModal: (modalId, options) => set(state => {
    const newModal = {
      modalId,
      options,
      closeListeners: []
    }
    return {
      modal: {
        ...state.modal,
        current: newModal,
        root: state.modal.root || newModal
      }
    }
  }),
  
  closeModal: (modalId) => set(state => {
    if (state.modal.current?.modalId === modalId) {
      const newStack = [...state.modal.stack]
      const prevModal = newStack.pop()
      return {
        modal: {
          ...state.modal,
          current: prevModal || null,
          stack: newStack
        }
      }
    }
    return state
  }),
  
  // Alert Management - mirrors Vue AlertHelper
  showAlert: (message, header, options = {}) => {
    const alertId = `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const alert = {
      id: alertId,
      message,
      header,
      ...options
    }
    set(state => ({
      alerts: [...state.alerts, alert]
    }))
    
    // Auto remove after duration
    setTimeout(() => {
      set(state => ({
        alerts: state.alerts.filter(a => a.id !== alertId)
      }))
    }, options.duration || 3000)
  },
  
  removeAlert: (alertId) => set(state => ({
    alerts: state.alerts.filter(a => a.id !== alertId)
  })),
  
  // Session Management
  setSessionStarted: (started) => set({ sessionStarted: started }),
  setPrivacyAgreed: (agreed) => set({ privacyAgreed: agreed }),
  
  // Command Execution - mirrors Vue handleImmediateCommands
  executeCommand: async (command) => {
    const { name, args } = command
    
    switch (name) {
      case 'show_alert':
        get().showAlert(args.text, args.title, { duration: args.duration })
        break
      case 'show_modal':
        // TODO: Implement modal showing
        break
      case 'show_motion':
        // TODO: Implement motion showing (excluding motion modules)
        break
      default:
        console.log(`Unknown command: ${name}`, args)
    }
  },
  
  // Action Execution - mirrors Vue executeAction
  executeAction: async (action, args = {}, context = {}) => {
    console.log('Execute action:', action, args)
    const [namespace, method] = action.split('.')
    
    switch (namespace) {
      case 'route':
        if (method === 'navigate_to') {
          await get().navigateTo(args.route || '/')
        }
        break
      case 'builtin':
        // TODO: Implement builtin actions
        break
      default:
        console.log(`Unknown action namespace: ${namespace}`)
    }
  }
})))
