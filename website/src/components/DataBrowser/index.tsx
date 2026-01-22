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
  statistics: {
    totalDatasets: number;
    totalYears: number;
    totalMinistries: number;
    totalDepartments: number;
  };
}

const typedIndex = datasetIndex as DatasetIndex;

export default function DataBrowser(): JSX.Element {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedYears, setSelectedYears] = useState<string[]>([]);
  const [selectedMinistries, setSelectedMinistries] = useState<string[]>([]);
  const [modalData, setModalData] = useState<{
    isOpen: boolean;
    url: string;
    title: string;
  }>({
    isOpen: false,
    url: '',
    title: '',
  });

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

    // Apply year filter
    if (selectedYears.length > 0) {
      results = results.filter((dataset) =>
        selectedYears.includes(dataset.year)
      );
    }

    // Apply ministry filter
    if (selectedMinistries.length > 0) {
      results = results.filter((dataset) =>
        selectedMinistries.includes(dataset.ministry)
      );
    }

    return results;
  }, [searchQuery, selectedYears, selectedMinistries]);

  // Build filtered tree structure
  const filteredTree = useMemo(() => {
    const tree: Record<string, Record<string, Dataset[]>> = {};

    filteredDatasets.forEach((dataset) => {
      const year = dataset.year || 'Unknown';
      const ministry = dataset.ministry || 'Other';

      if (!tree[year]) {
        tree[year] = {};
      }
      if (!tree[year][ministry]) {
        tree[year][ministry] = [];
      }
      tree[year][ministry].push(dataset);
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

  const handleMinistryToggle = useCallback((ministry: string) => {
    setSelectedMinistries((prev) =>
      prev.includes(ministry)
        ? prev.filter((m) => m !== ministry)
        : [...prev, ministry]
    );
  }, []);

  const handleClearFilters = useCallback(() => {
    setSearchQuery('');
    setSelectedYears([]);
    setSelectedMinistries([]);
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
    selectedMinistries.length > 0;

  return (
    <div className={styles.dataBrowser}>
      <div className={styles.header}>
        <h2>Interactive Data Browser</h2>
        <p className={styles.subtitle}>
          Browse {typedIndex.statistics.totalDatasets} datasets across{' '}
          {typedIndex.statistics.totalYears} years and{' '}
          {typedIndex.statistics.totalMinistries} ministries
        </p>
      </div>

      <SearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        placeholder="Search datasets by name, ministry, department..."
      />

      <FilterPanel
        years={typedIndex.years}
        ministries={typedIndex.ministries}
        selectedYears={selectedYears}
        selectedMinistries={selectedMinistries}
        onYearToggle={handleYearToggle}
        onMinistryToggle={handleMinistryToggle}
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
