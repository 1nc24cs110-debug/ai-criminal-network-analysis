import React, { useState, useEffect } from 'react';
import {
  FileSearch, Upload, FileText, CheckCircle2, Clock, AlertTriangle,
  ArrowRight, Sparkles, Eye, X, Plus, Shield, Check, Hash
} from 'lucide-react';
import { api } from '../api';
import { EvidenceDocument, Case } from '../types';

export const EvidenceCenterView: React.FC = () => {
  const [documents, setDocuments] = useState<EvidenceDocument[]>([]);
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<number | undefined>(undefined);
  const [selectedDoc, setSelectedDoc] = useState<EvidenceDocument | null>(null);
  const [loading, setLoading] = useState(true);

  // Upload modal state
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadCaseId, setUploadCaseId] = useState<number | ''>('');
  const [uploadTitle, setUploadTitle] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any | null>(null);

  // Direct Text Extraction state
  const [rawTextInput, setRawTextInput] = useState('');
  const [extracting, setExtracting] = useState(false);
  const [extractionPreview, setExtractionPreview] = useState<any | null>(null);
  const [commitLoading, setCommitLoading] = useState(false);
  const [syntheticSamples, setSyntheticSamples] = useState<any[]>([]);

  useEffect(() => {
    loadData();
  }, [selectedCaseId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [dData, cData, sData] = await Promise.all([
        api.listEvidenceDocuments(selectedCaseId),
        api.listCases(),
        api.listSyntheticSamples().catch(() => [])
      ]);
      setDocuments(dData);
      setCases(cData);
      setSyntheticSamples(sData);
      if (cData.length > 0 && !uploadCaseId) {
        setUploadCaseId(cData[0].id);
      }
    } catch (err) {
      console.error('Failed to load evidence documents', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile || !uploadCaseId || !uploadTitle) return;

    setUploadLoading(true);
    try {
      const formData = new FormData();
      formData.append('case_id', String(uploadCaseId));
      formData.append('title', uploadTitle);
      formData.append('file', selectedFile);

      const res = await api.uploadEvidenceDocument(formData);
      setUploadResult(res);
      await loadData();
    } catch (err: any) {
      alert(`Upload error: ${err.message}`);
    } finally {
      setUploadLoading(false);
    }
  };

  const handleRunTextExtraction = async () => {
    if (!rawTextInput.trim()) return;
    setExtracting(true);
    try {
      const res = await api.extractFromText(rawTextInput, selectedDoc?.id);
      setExtractionPreview(res);
    } catch (err: any) {
      alert(`Extraction error: ${err.message}`);
    } finally {
      setExtracting(false);
    }
  };

  const handleCommitExtraction = async () => {
    if (!extractionPreview || !selectedCaseId && !cases[0]?.id) return;
    setCommitLoading(true);
    try {
      const targetCaseId = selectedCaseId || cases[0].id;
      const res = await api.commitExtraction({
        case_id: targetCaseId,
        document_id: selectedDoc?.id,
        entities: extractionPreview.entities,
        relationships: extractionPreview.relationships
      });
      alert(`Successfully committed ${res.committed_entities} entities and ${res.committed_relationships} relationships into the investigation records (marked PENDING HUMAN REVIEW).`);
      setExtractionPreview(null);
      setRawTextInput('');
    } catch (err: any) {
      alert(`Commit error: ${err.message}`);
    } finally {
      setCommitLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800/80 gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-extrabold text-white tracking-wide">
              EVIDENCE PROVENANCE & NLP EXTRACTION CENTER
            </h1>
            <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-purple-950 text-purple-300 border border-purple-800">
              AUDITED PROVENANCE ENGINE
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Maintain source documents, timestamps, exact text spans, and human verification status of every extracted intelligence fact.
          </p>
        </div>

        <button
          onClick={() => {
            setShowUploadModal(true);
            setUploadResult(null);
          }}
          className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold text-xs tracking-wider uppercase transition-all shadow-lg shadow-purple-950 flex items-center space-x-2 self-start sm:self-auto"
        >
          <Upload className="w-4 h-4" />
          <span>Ingest Evidence File</span>
        </button>
      </div>

      {/* Main Grid: Document List on Left, Document & Extraction Viewer on Right */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Documents Directory */}
        <div className="space-y-4">
          <div className="p-4 rounded-xl bg-[#0D1527]/90 border border-slate-800 shadow-xl space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold tracking-wider uppercase text-slate-300">
                AUTHORIZED CASE EVIDENCE
              </span>
              <span className="text-[10px] font-mono text-cyan-400 px-2 py-0.5 rounded bg-cyan-950 border border-cyan-800">
                {documents.length} Files
              </span>
            </div>

            {/* Case Filter */}
            <select
              value={selectedCaseId || ''}
              onChange={(e) => setSelectedCaseId(e.target.value ? Number(e.target.value) : undefined)}
              className="w-full px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono focus:border-cyan-500 focus:outline-none"
            >
              <option value="">All Investigation Cases</option>
              {cases.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.case_number} - {c.title}
                </option>
              ))}
            </select>

            {/* Document List */}
            <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
              {documents.map((doc) => {
                const isSelected = selectedDoc?.id === doc.id;
                return (
                  <div
                    key={doc.id}
                    onClick={() => {
                      setSelectedDoc(doc);
                      setRawTextInput(doc.raw_text);
                      setExtractionPreview(null);
                    }}
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-purple-950/40 border-purple-600 text-purple-200 ring-1 ring-purple-500'
                        : 'bg-slate-900/70 border-slate-800 hover:border-slate-700 text-slate-300'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <h4 className="text-xs font-bold truncate pr-2">{doc.title}</h4>
                      <span className="text-[9px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 uppercase">
                        {doc.file_type}
                      </span>
                    </div>

                    <div className="flex items-center space-x-3 text-[10px] text-slate-400 font-mono mt-2">
                      <span>Ref Count: {doc.reference_count || 0}</span>
                      <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Columns: Evidence Inspector & NLP Extraction Workbench */}
        <div className="lg:col-span-2 space-y-4">
          <div className="p-5 rounded-xl bg-[#0D1527]/90 border border-slate-800 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800 gap-2">
              <div>
                <span className="text-[10px] font-mono text-cyan-400 uppercase font-semibold block">
                  {selectedDoc ? `INSPECTING: ${selectedDoc.title}` : 'NLP EXTRACTION WORKBENCH'}
                </span>
                <h3 className="text-sm font-bold text-white">
                  {selectedDoc ? selectedDoc.file_name : 'Direct Intelligence Text Input'}
                </h3>
              </div>

              <button
                onClick={handleRunTextExtraction}
                disabled={extracting || !rawTextInput.trim()}
                className="px-3.5 py-1.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs font-semibold flex items-center space-x-1.5 transition-all shadow-md shadow-cyan-950 disabled:opacity-40 self-start sm:self-auto"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>{extracting ? 'Processing NLP...' : 'Run Evidence Extraction'}</span>
              </button>
            </div>

            {/* Synthetic Sample Quick-Load Bar */}
            <div className="p-3 rounded-lg bg-slate-900/80 border border-cyan-800/60 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <span className="text-[11px] font-mono font-bold text-cyan-300 uppercase">
                  Load Synthetic Document Sample:
                </span>
              </div>
              <select
                onChange={(e) => {
                  const sample = syntheticSamples.find((s) => s.id === e.target.value);
                  if (sample) {
                    setRawTextInput(sample.text);
                    setSelectedDoc(null);
                    setExtractionPreview(null);
                  }
                }}
                defaultValue=""
                className="px-2.5 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-slate-200 text-xs font-mono focus:border-cyan-500 focus:outline-none"
              >
                <option value="" disabled>Choose a synthetic investigation memo...</option>
                {syntheticSamples.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.title}
                  </option>
                ))}
              </select>
            </div>

            {/* Document Raw Text Editor */}
            <div>
              <label className="block text-[11px] font-mono text-slate-400 uppercase mb-1">
                Document Text Excerpt & Source Material
              </label>
              <textarea
                value={rawTextInput}
                onChange={(e) => setRawTextInput(e.target.value)}
                rows={8}
                placeholder="Paste surveillance intercepts, police wiretaps, customs reports, or bank transaction logs..."
                className="w-full p-3 bg-slate-900 border border-slate-800 rounded-lg text-slate-200 text-xs font-mono focus:border-cyan-500 focus:outline-none leading-relaxed"
              />
            </div>

            {/* Extraction Results Preview */}
            {extractionPreview && (
              <div className="p-4 rounded-xl bg-slate-900/90 border border-cyan-800/80 space-y-4">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs font-mono font-bold text-cyan-300">
                      EXTRACTION RESULTS: {extractionPreview.total_entities_found} ENTITIES, {extractionPreview.total_relationships_found} RELATIONSHIPS
                    </span>
                  </div>

                  <button
                    disabled={commitLoading}
                    onClick={handleCommitExtraction}
                    className="px-3.5 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white font-mono text-xs font-bold transition-all shadow-md shadow-emerald-950 flex items-center space-x-1.5"
                  >
                    <Check className="w-3.5 h-3.5" />
                    <span>{commitLoading ? 'Committing...' : 'Commit to Case Records'}</span>
                  </button>
                </div>

                {/* Extracted Entities Chips */}
                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-400 block font-semibold mb-1.5">
                    Extracted Entities with Context Offsets:
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {extractionPreview.entities.map((e: any, idx: number) => (
                      <div
                        key={idx}
                        className="p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono space-y-0.5"
                      >
                        <div className="flex items-center space-x-1.5">
                          <span className="text-cyan-400 font-bold">{e.name}</span>
                          <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 uppercase">
                            {e.entity_type}
                          </span>
                        </div>
                        <div className="text-[10px] text-slate-500">
                          Confidence: {Math.round(e.confidence * 100)}% | Chars [{e.char_start}..{e.char_end}]
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Extracted Relationships */}
                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-400 block font-semibold mb-1.5">
                    Extracted Relationship Triples (Pending Review):
                  </span>
                  <div className="space-y-2">
                    {extractionPreview.relationships.map((r: any, idx: number) => (
                      <div
                        key={idx}
                        className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs font-mono space-y-1"
                      >
                        <div className="flex items-center space-x-2 text-slate-200">
                          <strong className="text-cyan-400">{r.source_name}</strong>
                          <span className="text-slate-500">➔</span>
                          <span className="px-1.5 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800 font-bold text-[10px]">
                            {r.relation_type}
                          </span>
                          <span className="text-slate-500">➔</span>
                          <strong className="text-cyan-400">{r.target_name}</strong>
                          <span className="text-[10px] text-slate-500 ml-auto">
                            Confidence: {Math.round(r.confidence * 100)}%
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 italic">"{r.evidence_excerpt}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Upload Evidence Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-lg bg-[#0D1527] border border-slate-800 rounded-2xl p-6 shadow-2xl relative">
            <button
              onClick={() => setShowUploadModal(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg bg-slate-900 border border-slate-800"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-2 mb-4">
              <Upload className="w-5 h-5 text-purple-400" />
              <h2 className="text-base font-bold text-white tracking-wide">
                INGEST EVIDENCE DOCUMENT
              </h2>
            </div>

            <form onSubmit={handleFileUpload} className="space-y-4">
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">TARGET INVESTIGATION CASE *</label>
                <select
                  value={uploadCaseId}
                  onChange={(e) => setUploadCaseId(Number(e.target.value))}
                  required
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 text-xs font-mono focus:border-cyan-500 focus:outline-none"
                >
                  {cases.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.case_number} - {c.title}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">DOCUMENT TITLE *</label>
                <input
                  type="text"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  required
                  placeholder="e.g. Customs Terminal Intercept Log #RT-2026-99"
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 text-xs focus:border-cyan-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">SELECT FILE (.TXT, .PDF, .JSON) *</label>
                <input
                  type="file"
                  accept=".txt,.pdf,.json"
                  onChange={(e) => setSelectedFile(e.target.files ? e.target.files[0] : null)}
                  required
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 text-xs font-mono file:mr-3 file:py-1 file:px-3 file:rounded file:border-0 file:bg-purple-900 file:text-purple-200 file:text-xs"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploadLoading}
                  className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs transition-all shadow-md shadow-purple-950 disabled:opacity-50"
                >
                  {uploadLoading ? 'Uploading & Parsing...' : 'Ingest & Extract'}
                </button>
              </div>
            </form>

            {/* Quick Upload Result preview */}
            {uploadResult && (
              <div className="mt-4 p-3 rounded-lg bg-emerald-950/60 border border-emerald-800 text-xs text-emerald-200 space-y-1">
                <div className="font-bold flex items-center space-x-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <span>Document Uploaded: {uploadResult.file_name}</span>
                </div>
                <p className="text-[11px] text-emerald-300 font-mono">
                  Extracted {uploadResult.entities_preview.length} entities and {uploadResult.relationships_preview.length} candidate links.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
