import React, { useState, useCallback } from 'react';
import useBaseUrl from '@docusaurus/useBaseUrl';
import DatasetCard from './DatasetCard';
import type { Dataset } from './index';
import styles from './DataBrowser.module.css';

interface TreeViewProps {
  tree: Record<string, Record<string, Dataset[]>>;
  years: string[];
  onViewJson: (url: string, title: string) => void;
}

interface YearSectionProps {
  year: string;
  ministries: Record<string, Dataset[]>;
  onViewJson: (url: string, title: string) => void;
  defaultExpanded?: boolean;
}

interface MinistrySectionProps {
  ministry: string;
  datasets: Dataset[];
  onViewJson: (url: string, title: string) => void;
  defaultExpanded?: boolean;
}

function MinistrySection({
  ministry,
  datasets,
  onViewJson,
  defaultExpanded = false,
}: MinistrySectionProps): JSX.Element {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  // Group datasets by department
  const departmentGroups = datasets.reduce((acc, dataset) => {
    const dept = dataset.department || 'General';
    if (!acc[dept]) {
      acc[dept] = [];
    }
    acc[dept].push(dataset);
    return acc;
  }, {} as Record<string, Dataset[]>);

  return (
    <div className={styles.ministrySection}>
      <button
        className={`${styles.sectionHeader} ${styles.ministryHeader}`}
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
      >
        <span className={styles.expandIcon}>{isExpanded ? '▼' : '▶'}</span>
        <span className={styles.sectionIcon}>🏛️</span>
        <span className={styles.sectionTitle}>{ministry}</span>
        <span className={styles.datasetCount}>({datasets.length} datasets)</span>
      </button>
      {isExpanded && (
        <div className={styles.sectionContent}>
          {Object.entries(departmentGroups).map(([dept, deptDatasets]) => (
            <DepartmentSection
              key={dept}
              department={dept}
              datasets={deptDatasets}
              onViewJson={onViewJson}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface DepartmentSectionProps {
  department: string;
  datasets: Dataset[];
  onViewJson: (url: string, title: string) => void;
}

function DepartmentSection({
  department,
  datasets,
  onViewJson,
}: DepartmentSectionProps): JSX.Element {
  const [isExpanded, setIsExpanded] = useState(true);

  return (
    <div className={styles.departmentSection}>
      <button
        className={`${styles.sectionHeader} ${styles.departmentHeader}`}
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
      >
        <span className={styles.expandIcon}>{isExpanded ? '▼' : '▶'}</span>
        <span className={styles.sectionIcon}>🏢</span>
        <span className={styles.sectionTitle}>{department}</span>
        <span className={styles.datasetCount}>({datasets.length})</span>
      </button>
      {isExpanded && (
        <div className={styles.datasetList}>
          {datasets.map((dataset) => (
            <DatasetCard
              key={dataset.id}
              dataset={dataset}
              onViewJson={onViewJson}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function YearSection({
  year,
  ministries,
  onViewJson,
  defaultExpanded = false,
}: YearSectionProps): JSX.Element {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const downloadUrl = useBaseUrl(`/downloads/${year}_Data.zip`);

  const totalDatasets = Object.values(ministries).reduce(
    (sum, datasets) => sum + datasets.length,
    0
  );

  return (
    <div className={styles.yearSection}>
      <button
        className={`${styles.sectionHeader} ${styles.yearHeader}`}
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
      >
        <span className={styles.expandIcon}>{isExpanded ? '▼' : '▶'}</span>
        <span className={styles.sectionIcon}>📅</span>
        <span className={styles.sectionTitle}>{year}</span>
        <span className={styles.datasetCount}>({totalDatasets} datasets)</span>
        <a
          href={downloadUrl}
          className={styles.downloadBtn}
          onClick={(e) => e.stopPropagation()}
          download
        >
          📦 Download All
        </a>
      </button>
      {isExpanded && (
        <div className={styles.sectionContent}>
          {Object.entries(ministries)
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([ministry, datasets]) => (
              <MinistrySection
                key={ministry}
                ministry={ministry}
                datasets={datasets}
                onViewJson={onViewJson}
              />
            ))}
        </div>
      )}
    </div>
  );
}

export default function TreeView({
  tree,
  years,
  onViewJson,
}: TreeViewProps): JSX.Element {
  const sortedYears = Object.keys(tree).sort((a, b) => b.localeCompare(a));

  if (sortedYears.length === 0) {
    return (
      <div className={styles.noResults}>
        <p>No datasets found matching your criteria.</p>
        <p>Try adjusting your search or filters.</p>
      </div>
    );
  }

  return (
    <div className={styles.treeView}>
      {sortedYears.map((year, index) => (
        <YearSection
          key={year}
          year={year}
          ministries={tree[year]}
          onViewJson={onViewJson}
          defaultExpanded={index === 0}
        />
      ))}
    </div>
  );
}
