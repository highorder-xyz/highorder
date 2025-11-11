const config = {
  title: 'HighOrder',
  tagline: 'HighOrder and Hola',
  url: 'https://highorder.xyz',
  baseUrl: '/docs/',
  favicon: 'img/favicon.ico',
  organizationName: 'highorder-xyz',
  projectName: 'highorder',
  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },
  i18n: {
    defaultLocale: 'zh',
    locales: ['zh', 'en'],
    localeConfigs: {
      zh: { label: '中文' },
      en: { label: 'English' },
    },
  },
  presets: [
    [
      'classic',
      (
        {
          docs: {
            path: 'docs',
            routeBasePath: '/',
            sidebarPath: require.resolve('./sidebars.cjs'),
            editCurrentVersion: false,
          },
          blog: false,
          theme: {
          },
        }
      ),
    ],
  ],
  themeConfig: ({
      navbar: {
        title: 'HighOrder',
        items: [
          { href: 'http://highorder.xyz/', label: 'HighOrder', position: 'left' },
          { to: '/', label: '文档', position: 'left' },
          {
            type: 'localeDropdown',
            position: 'right',
          },
          { href: 'https://github.com/highorder-xyz/highorder', label: 'GitHub', position: 'right' },
        ],
      },
      footer: {
        style: 'dark',
        links: [],
        copyright: `Copyright © ${new Date().getFullYear()} HighOrder` ,
      },
    }),
};

module.exports = config;
