import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'LDF Datasets',
  tagline: 'Open, structured datasets curated by the Lanka Data Foundation',
  favicon: 'img/favicon.png',

  future: {
    v4: true,
  },

  url: 'https://ldflk.github.io',
  baseUrl: '/datasets/',

  organizationName: 'LDFLK',
  projectName: 'datasets',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  staticDirectories: ['static', '../data'],

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/browse',
          editUrl: 'https://github.com/LDFLK/datasets/tree/main/website/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/social-card.jpg',
    colorMode: {
      defaultMode: 'light',
      disableSwitch: false,
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'LDF Datasets',
      logo: {
        alt: 'LDF Datasets Logo',
        src: 'img/logo.png',
        height: 32,
      },
      items: [
        {
          to: '/',
          label: 'Home',
          position: 'left',
          activeBaseRegex: '^/$',
        },
        {
          to: '/browse/data-matrix',
          label: 'Data Matrix',
          position: 'left',
        },
        {
          to: '/browse/interactive-browser',
          label: 'Interactive Browser',
          position: 'left',
        },
        {
          to: '/browse/research/acts',
          label: 'Data Research',
          position: 'left',
        },
        {
          to: '/browse/contribute',
          label: 'Contribute',
          position: 'left',
        },
        {
          href: 'https://github.com/LDFLK/datasets',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Data',
          items: [
            {
              label: 'Data Matrix',
              to: '/browse/data-matrix',
            },
            {
              label: 'Interactive Browser',
              to: '/browse/interactive-browser',
            },
            {
              label: 'Missing Datasets',
              to: '/browse/missing-datasets',
            },
          ],
        },
        {
          title: 'Learn',
          items: [
            {
              label: 'Data Research',
              to: '/browse/research/acts',
            },
            {
              label: 'Contribute',
              to: '/browse/contribute',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/LDFLK/datasets',
            },
          ],
        },
      ],
      copyright: `Copyright ${new Date().getFullYear()} Lanka Data Foundation. Licensed under CC BY-NC-SA 4.0.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
