import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
    title: "HighOrder",
    description: "HighOrder",
    base: '/docs/',
    head: [['link', { rel: 'icon', href: '/favicon.ico' }]],
    locales: {
        root: {
            label: 'Chinese',
            lang: 'ch'
        },
        fr: {
            label: 'English',
            lang: 'en', // optional, will be added  as `lang` attribute on `html` tag
            link: '/en/' // default /fr/ -- shows on navbar translations menu, can be external
        }
    },
    themeConfig: {
        // https://vitepress.dev/reference/default-theme-config
        nav: [
            { text: 'HighOrder', link: 'http://highorder.xyz/' },
            { text: '文档', link: '/' }
        ],

        sidebar: [
            {
                text: 'Examples',
                items: [
                    { text: 'Markdown Examples', link: '/markdown-examples' },
                    { text: 'Runtime API Examples', link: '/api-examples' }
                ]
            }
        ],

        socialLinks: [
            { icon: 'github', link: 'https://github.com/highorder-xyz/highorder' }
        ]
    }
})
