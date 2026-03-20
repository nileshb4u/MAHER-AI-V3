import React, { useState, useRef, useEffect } from 'react';
import { apiClient, KnowledgeDocument, KnowledgeSummary } from '../client';

interface KnowledgeUploadProps {
  agentId: string;
  onKnowledgeUpdated?: () => void;
}

const KnowledgeUpload: React.FC<KnowledgeUploadProps> = ({ agentId, onKnowledgeUpdated }) => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploadedDocs, setUploadedDocs] = useState<KnowledgeDocument[]>([]);
  const [summary, setSummary] = useState<KnowledgeSummary | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const MAX_FILES = 5;
  const ACCEPTED_TYPES = '.pdf,.txt,.docx';
  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

  // Load existing knowledge on mount
  useEffect(() => {
    loadKnowledge();
  }, [agentId]);

  const loadKnowledge = async () => {
    try {
      const response = await apiClient.getAgentKnowledge(agentId);
      setUploadedDocs(response.knowledge.documents);
      setSummary(response.summary);
    } catch (err) {
      console.log('No existing knowledge found');
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []);

    // Validate number of files
    const currentTotal = uploadedDocs.length + files.length;
    if (currentTotal + selectedFiles.length > MAX_FILES) {
      setError(`Maximum ${MAX_FILES} files allowed. You currently have ${currentTotal} files.`);
      return;
    }

    // Validate file sizes and types
    const validFiles: File[] = [];
    const errors: string[] = [];

    selectedFiles.forEach(file => {
      const ext = file.name.toLowerCase().split('.').pop();
      if (!['pdf', 'txt', 'docx'].includes(ext || '')) {
        errors.push(`${file.name}: Unsupported file type`);
        return;
      }

      if (file.size > MAX_FILE_SIZE) {
        errors.push(`${file.name}: File too large (max 10MB)`);
        return;
      }

      validFiles.push(file);
    });

    if (errors.length > 0) {
      setError(errors.join(', '));
    }

    if (validFiles.length > 0) {
      setFiles(prev => [...prev, ...validFiles]);
      setError(null);
    }

    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Please select files to upload');
      return;
    }

    setIsUploading(true);
    setError(null);
    setSuccess(null);
    setUploadProgress(0);

    try {
      const response = await apiClient.uploadKnowledge(
        agentId,
        files,
        (progress) => setUploadProgress(progress)
      );

      setSuccess(`Successfully uploaded ${response.processed_files.length} file(s)`);
      setFiles([]);

      // Reload knowledge
      await loadKnowledge();

      if (onKnowledgeUpdated) {
        onKnowledgeUpdated();
      }

      if (response.errors && response.errors.length > 0) {
        setError(`Some files failed: ${response.errors.join(', ')}`);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to upload files');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const deleteUploadedFile = async (fileId: string, filename: string) => {
    if (!confirm(`Delete ${filename}?`)) return;

    try {
      await apiClient.deleteKnowledgeFile(agentId, fileId);
      setSuccess(`Deleted ${filename}`);
      await loadKnowledge();

      if (onKnowledgeUpdated) {
        onKnowledgeUpdated();
      }
    } catch (err: any) {
      setError(err.message || 'Failed to delete file');
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-2">Knowledge Base / Memory Upload</h3>
        <p className="text-sm text-brand-gray">
          Upload documents (PDF, TXT, DOCX) to give your agent long-term memory and domain knowledge.
          The agent will automatically use this information when responding.
        </p>
      </div>

      {/* Summary Stats */}
      {summary && summary.total_files > 0 && (
        <div className="bg-brand-light-blue/10 rounded-lg p-4">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-brand-accent-orange">{summary.total_files}</div>
              <div className="text-xs text-brand-gray">Files</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-brand-accent-orange">
                {Math.round(summary.total_size / 1024)}KB
              </div>
              <div className="text-xs text-brand-gray">Total Size</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-brand-accent-orange">
                {summary.total_words.toLocaleString()}
              </div>
              <div className="text-xs text-brand-gray">Words</div>
            </div>
          </div>
        </div>
      )}

      {/* Error/Success Messages */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      {success && (
        <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
          <p className="text-sm text-green-400">{success}</p>
        </div>
      )}

      {/* File Selection */}
      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading || uploadedDocs.length + files.length >= MAX_FILES}
            className="px-4 py-2 bg-brand-accent-orange text-white rounded-lg hover:bg-opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
          >
            Select Files
          </button>
          <span className="text-sm text-brand-gray">
            {uploadedDocs.length + files.length} / {MAX_FILES} files
          </span>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept={ACCEPTED_TYPES}
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        {/* Pending Files List */}
        {files.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-white">Files to Upload:</h4>
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between bg-brand-light-blue/10 rounded-lg p-3"
              >
                <div className="flex-1">
                  <div className="text-sm text-white font-medium">{file.name}</div>
                  <div className="text-xs text-brand-gray mt-1">
                    {formatFileSize(file.size)} • {file.type || 'Document'}
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  disabled={isUploading}
                  className="p-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors disabled:opacity-50"
                  aria-label="Remove file"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}

            {/* Upload Button */}
            <button
              onClick={handleUpload}
              disabled={isUploading}
              className="w-full px-4 py-2 bg-brand-accent-orange text-white rounded-lg hover:bg-opacity-90 transition-colors disabled:opacity-50 font-medium"
            >
              {isUploading ? 'Uploading...' : `Upload ${files.length} File(s)`}
            </button>
          </div>
        )}
      </div>

      {/* Uploaded Files List */}
      {uploadedDocs.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-white">Uploaded Knowledge:</h4>
          <div className="space-y-2">
            {uploadedDocs.map((doc) => (
              <div
                key={doc.id}
                className="bg-brand-light-blue/10 rounded-lg p-3 space-y-2"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="text-sm text-white font-medium flex items-center gap-2">
                      <span className="text-brand-accent-orange">
                        {doc.extension === '.pdf' && '📄'}
                        {doc.extension === '.txt' && '📝'}
                        {doc.extension === '.docx' && '📘'}
                      </span>
                      {doc.filename}
                    </div>
                    <div className="text-xs text-brand-gray mt-1">
                      {formatFileSize(doc.size)} • {doc.word_count.toLocaleString()} words
                    </div>
                  </div>
                  <button
                    onClick={() => deleteUploadedFile(doc.id, doc.filename)}
                    className="p-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                    aria-label="Delete file"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>

                {/* Summary Preview */}
                <div className="text-xs text-brand-gray bg-brand-blue/50 rounded p-2">
                  <span className="font-medium">Preview: </span>
                  {doc.summary}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Help Text */}
      <div className="text-xs text-brand-gray bg-brand-light-blue/5 rounded-lg p-3 space-y-1">
        <p><strong>Supported formats:</strong> PDF, TXT, DOCX</p>
        <p><strong>Max file size:</strong> 10MB per file</p>
        <p><strong>Max files:</strong> {MAX_FILES} files per agent</p>
        <p><strong>Usage:</strong> Documents are automatically included in agent responses</p>
      </div>
    </div>
  );
};

export default KnowledgeUpload;
