import React from 'react';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import styles from './index.module.css';

function HeroSection() {
  return (
    <header className={styles.hero}>
      <div className={styles.heroContent}>
        <h1 className={styles.heroTitle}>LDF Datasets</h1>
        <p className={styles.heroSubtitle}>
          Open, structured datasets curated by the Lanka Data Foundation
        </p>
        <p className={styles.heroDescription}>
          Freely accessible government data from Sri Lanka, cleaned and organized
          for researchers, journalists, developers, and citizens.
        </p>
        <div className={styles.heroButtons}>
          <Link className={styles.primaryButton} to="/browse/interactive-browser">
            Browse Datasets
          </Link>
          <Link className={styles.secondaryButton} to="/browse/data-matrix">
            View Data Matrix
          </Link>
        </div>
      </div>
    </header>
  );
}

function StatsSection() {
  const stats = [
    { value: '212', label: 'Datasets' },
    { value: '6', label: 'Years (2019-2024)' },
    { value: '15', label: 'Ministries' },
    { value: 'JSON', label: 'Format' },
  ];

  return (
    <section className={styles.stats}>
      <div className={styles.statsGrid}>
        {stats.map((stat, index) => (
          <div key={index} className={styles.statCard}>
            <div className={styles.statValue}>{stat.value}</div>
            <div className={styles.statLabel}>{stat.label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function FeaturesSection() {
  const features = [
    {
      title: 'Data Matrix',
      description: 'Tabular overview of all datasets organized by ministry, showing years available and verification status.',
      link: '/browse/data-matrix',
      icon: '📊',
    },
    {
      title: 'Interactive Browser',
      description: 'Search and filter datasets with an interactive tree view. View JSON data directly in the browser.',
      link: '/browse/interactive-browser',
      icon: '🔍',
    },
    {
      title: 'Acts Research',
      description: 'Research on Sri Lankan Acts and their anatomy, understanding how government institutions are governed.',
      link: '/browse/acts',
      icon: '📜',
    },
    {
      title: 'Contribute',
      description: 'Learn how to contribute government data and help expand this open data initiative.',
      link: '/browse/contribute',
      icon: '🤝',
    },
  ];

  return (
    <section className={styles.features}>
      <h2 className={styles.sectionTitle}>Explore</h2>
      <div className={styles.featuresGrid}>
        {features.map((feature, index) => (
          <Link key={index} to={feature.link} className={styles.featureCard}>
            <span className={styles.featureIcon}>{feature.icon}</span>
            <h3 className={styles.featureTitle}>{feature.title}</h3>
            <p className={styles.featureDescription}>{feature.description}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}

function SourcesSection() {
  const sources = [
    {
      name: 'Sri Lanka Tourism Development Authority',
      url: 'https://www.sltda.gov.lk',
      description: 'Tourism statistics, arrivals, accommodations, and revenue data',
    },
    {
      name: 'Sri Lanka Bureau of Foreign Employment',
      url: 'https://www.slbfe.lk',
      description: 'Foreign employment registrations, departures, remittances, and complaints data',
    },
    {
      name: 'Department of Immigration and Emigration',
      url: 'https://www.immigration.gov.lk',
      description: 'Immigration statistics including asylum seekers, deportations, and visa data',
    },
    {
      name: 'Ministry of Foreign Affairs',
      url: 'https://www.mfa.gov.lk',
      description: 'Diplomatic communications, media releases, and cadre management data',
    },
    {
      name: 'Government Gazette - Sri Lanka',
      url: 'https://documents.gov.lk',
      description: 'Official government documents, acts, and legal notices',
    },
  ];

  return (
    <section className={styles.sources}>
      <h2 className={styles.sectionTitle}>Data Sources</h2>
      <p className={styles.sourcesIntro}>
        All data is sourced from official Sri Lankan government publications and websites.
        We gratefully acknowledge these institutions for making this information publicly available.
      </p>
      <div className={styles.sourcesList}>
        {sources.map((source, index) => (
          <div key={index} className={styles.sourceCard}>
            <h4 className={styles.sourceName}>
              <a href={source.url} target="_blank" rel="noopener noreferrer">
                {source.name}
              </a>
            </h4>
            <p className={styles.sourceDescription}>{source.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function LicenseSection() {
  return (
    <section className={styles.license}>
      <h2 className={styles.sectionTitle}>License</h2>
      <div className={styles.licenseContent}>
        <div className={styles.licenseIcon}>
          <a rel="license" href="https://creativecommons.org/licenses/by/4.0/">
            <img
              alt="Creative Commons License"
              src="https://i.creativecommons.org/l/by/4.0/88x31.png"
            />
          </a>
        </div>
        <div className={styles.licenseText}>
          <p>
            This work is licensed under a{' '}
            <a rel="license" href="https://creativecommons.org/licenses/by/4.0/">
              Creative Commons Attribution 4.0 International License (CC BY 4.0)
            </a>.
          </p>
          <p className={styles.licenseDetails}>
            You are free to:
          </p>
          <ul>
            <li><strong>Share</strong> - copy and redistribute the material in any medium or format</li>
            <li><strong>Adapt</strong> - remix, transform, and build upon the material for any purpose, even commercially</li>
          </ul>
          <p className={styles.licenseDetails}>
            Under the following terms:
          </p>
          <ul>
            <li><strong>Attribution</strong> - You must give appropriate credit to the Lanka Data Foundation and the original government sources, provide a link to the license, and indicate if changes were made.</li>
          </ul>
        </div>
      </div>
      <div className={styles.disclaimer}>
        <h4>Disclaimer</h4>
        <p>
          The original data is published by Sri Lankan government institutions and remains subject to their respective terms.
          This project collects, cleans, and structures the data to improve accessibility.
          While we strive for accuracy, users should verify critical data with original sources.
          The Lanka Data Foundation is not affiliated with the Sri Lankan government.
        </p>
      </div>
    </section>
  );
}

function AboutSection() {
  return (
    <section className={styles.about}>
      <h2 className={styles.sectionTitle}>About Lanka Data Foundation</h2>
      <p>
        The Lanka Data Foundation (LDF) is dedicated to making Sri Lankan public data more accessible,
        usable, and valuable for everyone. We believe that open data empowers citizens, enables research,
        supports journalism, and drives informed decision-making.
      </p>
      <p>
        This datasets project focuses on collecting, cleaning, and organizing government statistics
        that inform labor, social welfare, tourism, and economic planning. By providing structured,
        machine-readable data, we aim to lower barriers for researchers, developers, and organizations
        working to understand and improve Sri Lanka.
      </p>
    </section>
  );
}

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout
      title="Home"
      description="Open, structured datasets from Sri Lanka curated by the Lanka Data Foundation"
    >
      <main>
        <HeroSection />
        <StatsSection />
        <FeaturesSection />
        <SourcesSection />
        <LicenseSection />
        <AboutSection />
      </main>
    </Layout>
  );
}
