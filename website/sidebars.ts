import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  mainSidebar: [
    {
      type: 'doc',
      id: 'index',
      label: 'Overview',
    },
    {
      type: 'doc',
      id: 'data-matrix',
      label: 'Data Matrix',
    },
    {
      type: 'doc',
      id: 'interactive-browser',
      label: 'Interactive Browser',
    },
    {
      type: 'category',
      label: 'Data Research',
      items: [
        {
          type: 'doc',
          id: 'research/acts',
          label: 'Acts',
        },
      ],
    },
    {
      type: 'doc',
      id: 'contribute',
      label: 'Contribute',
    },
    {
      type: 'doc',
      id: 'missing-datasets',
      label: 'Missing Datasets',
    },
  ],
};

export default sidebars;
