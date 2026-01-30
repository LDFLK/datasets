import React, { useState, useMemo, useCallback } from 'react';
import SearchBar from './SearchBar';
import FilterPanel from './FilterPanel';
import TreeView from './TreeView';
import JsonModal from './JsonModal';
import datasetIndex from '../../data/datasetIndex.json';
import styles from './DataBrowser.module.css';

export interface Dataset {
  id: string;
  name: string;
  year: string;
  government: string;
  president: string;
  ministry: string;
  department: string;
  category: string;
  path: string;
  metadataPath: string | null;
  hasMetadata: boolean;
  isEmpty: boolean;
  searchText: string;
  hierarchy: string[];
}

interface DatasetIndex {
  datasets: Dataset[];
  years: string[];
  ministries: string[];
  departments: string[];
  categories: string[];
  statistics: {
    totalDatasets: number;
    totalYears: number;
    totalMinistries: number;
    totalDepartments: number;
    totalCategories: number;
  };
}

const typedIndex = datasetIndex as DatasetIndex;

// Constants for fallback values
const UNKNOWN_YEAR = 'Unknown';
const OTHER_CATEGORY = 'Other';

// Helper to normalize year/category values
const normalizeYear = (year: string): string => year || UNKNOWN_YEAR;
const normalizeCategory = (category: string): string => category || OTHER_CATEGORY;

export default function DataBrowser(): JSX.Element {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedYears, setSelectedYears] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [modalData, setModalData] = useState<{
    isOpen: boolean;
    url: string;
    title: string;
  }>({
    isOpen: false,
    url: '',
    title: '',
  });

  // Compute available years and categories, including fallback values if needed
  const availableYears = useMemo(() => {
    const hasUnknownYear = typedIndex.datasets.some((d) => !d.year);
    const years = [...typedIndex.years];
    if (hasUnknownYear && !years.includes(UNKNOWN_YEAR)) {
      years.push(UNKNOWN_YEAR);
    }
    return years;
  }, []);

  const availableCategories = useMemo(() => {
    const hasOtherCategory = typedIndex.datasets.some((d) => !d.category);
    const categories = [...(typedIndex.categories || [])];
    if (hasOtherCategory && !categories.includes(OTHER_CATEGORY)) {
      categories.push(OTHER_CATEGORY);
    }
    return categories;
  }, []);

  // Filter datasets based on search and filters
  const filteredDatasets = useMemo(() => {
    let results = typedIndex.datasets;

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      results = results.filter((dataset) =>
        dataset.searchText.includes(query)
      );
    }

    // Apply year filter (using normalized values for consistency)
    if (selectedYears.length > 0) {
      results = results.filter((dataset) =>
        selectedYears.includes(normalizeYear(dataset.year))
      );
    }

    // Apply category filter (using normalized values for consistency)
    if (selectedCategories.length > 0) {
      results = results.filter((dataset) =>
        selectedCategories.includes(normalizeCategory(dataset.category))
      );
    }

    return results;
  }, [searchQuery, selectedYears, selectedCategories]);

  // Build filtered tree structure
  const filteredTree = useMemo(() => {
    const tree: Record<string, Record<string, Dataset[]>> = {};

    filteredDatasets.forEach((dataset) => {
      const year = normalizeYear(dataset.year);
      const category = normalizeCategory(dataset.category);

      if (!tree[year]) {
        tree[year] = {};
      }
      if (!tree[year][category]) {
        tree[year][category] = [];
      }
      tree[year][category].push(dataset);
    });

    return tree;
  }, [filteredDatasets]);

  const handleYearToggle = useCallback((year: string) => {
    setSelectedYears((prev) =>
      prev.includes(year)
        ? prev.filter((y) => y !== year)
        : [...prev, year]
    );
  }, []);

  const handleCategoryToggle = useCallback((category: string) => {
    setSelectedCategories((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category]
    );
  }, []);

  const handleClearFilters = useCallback(() => {
    setSearchQuery('');
    setSelectedYears([]);
    setSelectedCategories([]);
  }, []);

  const handleViewJson = useCallback((url: string, title: string) => {
    setModalData({ isOpen: true, url, title });
  }, []);

  const handleCloseModal = useCallback(() => {
    setModalData({ isOpen: false, url: '', title: '' });
  }, []);

  const hasActiveFilters =
    searchQuery.trim() !== '' ||
    selectedYears.length > 0 ||
    selectedCategories.length > 0;

  return (
    <div className={styles.dataBrowser}>
      <div className={styles.header}>
        <h2>Interactive Data Browser</h2>
        <p className={styles.subtitle}>
          Browse {typedIndex.statistics.totalDatasets} datasets across{' '}
          {typedIndex.statistics.totalYears} years and{' '}
          {typedIndex.statistics.totalCategories || availableCategories.length} categories
        </p>
      </div>

      <SearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        placeholder="Search datasets by name, category, year..."
      />

      <FilterPanel
        years={availableYears}
        categories={availableCategories}
        selectedYears={selectedYears}
        selectedCategories={selectedCategories}
        onYearToggle={handleYearToggle}
        onCategoryToggle={handleCategoryToggle}
        onClearAll={handleClearFilters}
        hasActiveFilters={hasActiveFilters}
      />

      <div className={styles.resultsInfo}>
        <span>
          Showing <strong>{filteredDatasets.length}</strong> of{' '}
          <strong>{typedIndex.statistics.totalDatasets}</strong> datasets
        </span>
        {hasActiveFilters && (
          <button
            className={styles.clearButton}
            onClick={handleClearFilters}
          >
            Clear all filters
          </button>
        )}
      </div>

      <TreeView
        tree={filteredTree}
        years={typedIndex.years}
        onViewJson={handleViewJson}
      />

      <JsonModal
        isOpen={modalData.isOpen}
        url={modalData.url}
        title={modalData.title}
        onClose={handleCloseModal}
      />
    </div>
  );
}
