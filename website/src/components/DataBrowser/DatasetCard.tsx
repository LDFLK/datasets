import React from 'react';
import type { Dataset } from './index';
import styles from './DataBrowser.module.css';

interface DatasetCardProps {
  dataset: Dataset;
  onViewJson: (url: string, title: string) => void;
}

export default function DatasetCard({
  dataset,
  onViewJson,
}: DatasetCardProps): JSX.Element {
  const getCategoryEmoji = (category: string): string => {
    const emojiMap: Record<string, string> = {
      'diplomatic missions': '📊',
      'human resources': '👥',
      'org structure': '🏢',
      'official communications': '📰',
      'asylum seekers': '🏃',
      'deported foreign nationals': '✈️',
      'fake passports': '🆔',
      'fraudulent visa': '📋',
      refugees: '🏠',
      'refused foreign entry': '🚫',
      'complaints recieved': '📝',
      'complaints settled': '✅',
      'legal division performance': '⚖️',
      'local arrivals': '🛬',
      'local departures': '🛫',
      'monthly foreign exchange earnings': '💰',
      'raids conducted': '🔍',
      'remittances by country': '💸',
      'workers remittances': '💼',
      'slbfe registration': '📋',
      'annual tourism receipts': '💵',
      'location vs revenue vs visitors count': '📍',
      'top 10 source markets': '🏆',
      accommodations: '🏨',
      arrivals: '✈️',
      'occupancy rate': '📈',
      remittances: '💸',
      'ministry news': '📰',
      'mission news': '📰',
      'news from other sources': '📰',
      'special notices': '📢',
    };
    return emojiMap[category.toLowerCase()] || '📁';
  };

  const emoji = getCategoryEmoji(dataset.category || dataset.name);

  return (
    <div className={`${styles.datasetCard} ${dataset.isEmpty ? styles.datasetCardEmpty : ''}`}>
      <div className={styles.datasetInfo}>
        <span className={styles.datasetEmoji}>{emoji}</span>
        <span className={styles.datasetName}>{dataset.name}</span>
        {dataset.isEmpty && (
          <span className={styles.emptyBadge} title="This dataset needs to be populated">
            Empty
          </span>
        )}
      </div>
      <div className={styles.datasetActions}>
        <button
          className={`${styles.viewButton} ${dataset.isEmpty ? styles.viewButtonEmpty : ''}`}
          onClick={() =>
            onViewJson(`/${dataset.path}`, `${dataset.name} - data.json`)
          }
          title={dataset.isEmpty ? "View empty data.json" : "View data.json"}
        >
          📄 data.json
        </button>
        {dataset.hasMetadata && dataset.metadataPath && (
          <button
            className={styles.viewButton}
            onClick={() =>
              onViewJson(
                `/${dataset.metadataPath}`,
                `${dataset.name} - metadata.json`
              )
            }
            title="View metadata.json"
          >
            📄 metadata.json
          </button>
        )}
      </div>
    </div>
  );
}
