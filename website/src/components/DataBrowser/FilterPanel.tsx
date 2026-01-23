import React, { useState } from 'react';
import styles from './DataBrowser.module.css';

interface FilterPanelProps {
  years: string[];
  ministries: string[];
  selectedYears: string[];
  selectedMinistries: string[];
  onYearToggle: (year: string) => void;
  onMinistryToggle: (ministry: string) => void;
  onClearAll: () => void;
  hasActiveFilters: boolean;
}

export default function FilterPanel({
  years,
  ministries,
  selectedYears,
  selectedMinistries,
  onYearToggle,
  onMinistryToggle,
  onClearAll,
  hasActiveFilters,
}: FilterPanelProps): JSX.Element {
  const [showAllMinistries, setShowAllMinistries] = useState(false);

  const visibleMinistries = showAllMinistries
    ? ministries
    : ministries.slice(0, 5);

  return (
    <div className={styles.filterPanel}>
      <div className={styles.filterSection}>
        <h4 className={styles.filterTitle}>Filter by Year</h4>
        <div className={styles.filterChips}>
          {years.map((year) => (
            <button
              key={year}
              className={`${styles.filterChip} ${
                selectedYears.includes(year) ? styles.filterChipActive : ''
              }`}
              onClick={() => onYearToggle(year)}
              aria-pressed={selectedYears.includes(year)}
            >
              {year}
            </button>
          ))}
        </div>
      </div>

      <div className={styles.filterSection}>
        <h4 className={styles.filterTitle}>Filter by Ministry</h4>
        <div className={styles.filterChips}>
          {visibleMinistries.map((ministry) => (
            <button
              key={ministry}
              className={`${styles.filterChip} ${
                selectedMinistries.includes(ministry)
                  ? styles.filterChipActive
                  : ''
              }`}
              onClick={() => onMinistryToggle(ministry)}
              aria-pressed={selectedMinistries.includes(ministry)}
              title={ministry}
            >
              {ministry.length > 30
                ? `${ministry.substring(0, 30)}...`
                : ministry}
            </button>
          ))}
          {ministries.length > 5 && (
            <button
              className={styles.showMoreButton}
              onClick={() => setShowAllMinistries(!showAllMinistries)}
            >
              {showAllMinistries
                ? 'Show less'
                : `+${ministries.length - 5} more`}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
