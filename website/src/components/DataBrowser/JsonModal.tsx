import React, { useState, useEffect, useCallback } from 'react';
import styles from './DataBrowser.module.css';

interface JsonModalProps {
  isOpen: boolean;
  url: string;
  title: string;
  onClose: () => void;
}

export default function JsonModal({
  isOpen,
  url,
  title,
  onClose,
}: JsonModalProps): JSX.Element | null {
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen && url) {
      setLoading(true);
      setError(null);
      setContent('');

      fetch(url)
        .then((response) => {
          if (!response.ok) {
            throw new Error(`Failed to load: ${response.statusText}`);
          }
          return response.text();
        })
        .then((text) => {
          const trimmed = text.trim();
          if (!trimmed) {
            setError('This dataset is empty and needs to be populated. Check the Missing Datasets Report for details.');
            setLoading(false);
            return;
          }
          try {
            const data = JSON.parse(trimmed);
            setContent(JSON.stringify(data, null, 2));
            setLoading(false);
          } catch (parseError) {
            setError('Invalid JSON format in this file.');
            setLoading(false);
          }
        })
        .catch((err) => {
          setError(err.message);
          setLoading(false);
        });
    }
  }, [isOpen, url]);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [content]);

  const handleDownload = useCallback(() => {
    const blob = new Blob([content], { type: 'application/json' });
    const downloadUrl = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = title.replace(/\s+-\s+/, '_').replace(/\s+/g, '_');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(downloadUrl);
  }, [content, title]);

  const handleBackdropClick = useCallback(
    (e: React.MouseEvent) => {
      if (e.target === e.currentTarget) {
        onClose();
      }
    },
    [onClose]
  );

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose]);

  if (!isOpen) {
    return null;
  }

  return (
    <div
      className={styles.modalBackdrop}
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div className={styles.modalContent}>
        <div className={styles.modalHeader}>
          <h3 id="modal-title" className={styles.modalTitle}>
            {title}
          </h3>
          <div className={styles.modalActions}>
            <button
              className={styles.modalActionButton}
              onClick={handleCopy}
              disabled={loading || !!error}
              title="Copy to clipboard"
            >
              {copied ? '✅ Copied!' : '📋 Copy'}
            </button>
            <button
              className={styles.modalActionButton}
              onClick={handleDownload}
              disabled={loading || !!error}
              title="Download JSON file"
            >
              💾 Download
            </button>
            <button
              className={styles.modalCloseButton}
              onClick={onClose}
              aria-label="Close modal"
            >
              ✕
            </button>
          </div>
        </div>
        <div className={styles.modalBody}>
          {loading && (
            <div className={styles.loadingState}>
              <div className={styles.spinner}></div>
              <p>Loading...</p>
            </div>
          )}
          {error && (
            <div className={styles.errorState}>
              <p>Error: {error}</p>
            </div>
          )}
          {!loading && !error && (
            <pre className={styles.jsonContent}>
              <code>{content}</code>
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
