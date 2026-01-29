import React, { useState } from 'react';
import styles from './DataBrowser.module.css';

interface FilterPanelProps {
  years: string[];
  categories: string[];
  selectedYears: string[];
  selectedCategories: string[];
  onYearToggle: (year: string) => void;
  onCategoryToggle: (category: string) => void;
  onClearAll: () => void;
  hasActiveFilters: boolean;
}

export default function FilterPanel({
  years,
  categories,
  selectedYears,
  selectedCategories,
  onYearToggle,
  onCategoryToggle,
  onClearAll,
  hasActiveFilters,
}: FilterPanelProps): JSX.Element {
  const [showAllCategories, setShowAllCategories] = useState(false);

  const visibleCategories = showAllCategories
    ? categories
    : categories.slice(0, 6);

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
        <h4 className={styles.filterTitle}>Filter by Category</h4>
        <div className={styles.filterChips}>
          {visibleCategories.map((category) => (
            <button
              key={category}
              className={`${styles.filterChip} ${
                selectedCategories.includes(category)
                  ? styles.filterChipActive
                  : ''
              }`}
              onClick={() => onCategoryToggle(category)}
              aria-pressed={selectedCategories.includes(category)}
              title={category}
            >
              {category.length > 30
                ? `${category.substring(0, 30)}...`
                : category}
            </button>
          ))}
          {categories.length > 6 && (
            <button
              className={styles.showMoreButton}
              onClick={() => setShowAllCategories(!showAllCategories)}
            >
              {showAllCategories
                ? 'Show less'
                : `+${categories.length - 6} more`}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
