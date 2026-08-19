"use client";

import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mic,
  Square,
  Send,
  Sparkles,
  ShieldCheck,
  ShieldAlert,
  Clock,
  Database,
  Layers,
  Search,
  Volume2,
  AlertCircle,
  RefreshCw,
  XCircle,
  FileText,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import {
  queryRag,
  voiceQuery,
  healthCheck,
  GroundedQueryApiResponse,
  VoiceQueryApiResponse,
  HealthResponse,
  ApiError,
} from "@/lib/api";
import { useVoiceRecorder } from "@/hooks/useVoiceRecorder";

const SAMPLE_QUERIES = [
  {
    lang: "English",
    code: "eng_Latn",
    text: "What are the legal liabilities of a corporation?",
  },
  {
    lang: "Hindi",
    code: "hin_Deva",
    text: "कॉर्पोरेशन की कानूनी देनदारियां क्या हैं?",
  },
  {
    lang: "Bengali",
    code: "ben_Beng",
    text: "কর্পোরেশনের আইনি দায়বদ্ধতা কি কি?",
  },
];

const LANGUAGE_OPTIONS = [
  { value: "hin_Deva", label: "Hindi (हिन्दी)" },
  { value: "eng_Latn", label: "English" },
  { value: "ben_Beng", label: "Bengali (বাংলা)" },
];

export default function VoiceRagPlayground() {
  const [activeTab, setActiveTab] = useState<"text" | "voice">("text");
  const [queryText, setQueryText] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState("hin_Deva");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Results
  const [textResult, setTextResult] = useState<GroundedQueryApiResponse | null>(null);
  const [voiceResult, setVoiceResult] = useState<VoiceQueryApiResponse | null>(null);
  const [lastQueryType, setLastQueryType] = useState<"text" | "voice" | null>(null);

  // Backend Health
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);

  // Citation card expansion state
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({});

  // Voice recorder hook
  const {
    isRecording,
    recordingDuration,
    error: recorderError,
    startRecording,
    stopRecording,
    cancelRecording,
  } = useVoiceRecorder();

  // Load backend health on mount
  useEffect(() => {
    let isMounted = true;
    async function checkBackend() {
      try {
        setHealthLoading(true);
        const data = await healthCheck();
        if (isMounted) {
          setHealth(data);
        }
      } catch (err: any) {
        if (isMounted) {
          setHealth(null);
        }
      } finally {
        if (isMounted) {
          setHealthLoading(false);
        }
      }
    }

    checkBackend();
    return () => {
      isMounted = false;
    };
  }, []);

  const handleTextSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = queryText.trim();
    if (!trimmed) {
      setError("Please enter a question.");
      return;
    }

    setError(null);
    setIsLoading(true);
    setTextResult(null);
    setVoiceResult(null);

    try {
      const res = await queryRag(trimmed);
      setTextResult(res);
      setLastQueryType("text");
    } catch (err: any) {
      setError(err.message || "Failed to execute text RAG query.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceStart = async () => {
    setError(null);
    try {
      await startRecording();
    } catch (err: any) {
      setError(err.message || "Failed to start audio recording.");
    }
  };

  const handleVoiceStopAndSubmit = async () => {
    setIsLoading(true);
    setError(null);
    setTextResult(null);
    setVoiceResult(null);

    try {
      const audioBlob = await stopRecording();
      if (!audioBlob) {
        throw new Error("No audio was recorded.");
      }

      const res = await voiceQuery(audioBlob, selectedLanguage);
      setVoiceResult(res);
      setLastQueryType("voice");
    } catch (err: any) {
      setError(err.message || "Voice query processing failed.");
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSourceExpand = (id: string) => {
    setExpandedSources((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const activeResult = lastQueryType === "voice" ? voiceResult : textResult;

  return (
    <section
      id="rag-playground"
      className="rounded-2xl border-2 border-[#E5D7B5] bg-[#073523] p-6 sm:p-8 lg:p-10 shadow-2xl text-[#FFF8E8]"
    >
      {/* ── TOP HEADER & LIVE BACKEND STATUS BAR ── */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-[#144833] pb-6">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="flex h-3 w-3 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#F6BE2C] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-[#F6BE2C]"></span>
            </span>
            <p className="label-upper text-[#F6BE2C] font-bold tracking-[0.2em] text-xs">
              Live Production Harness
            </p>
          </div>
          <h2 className="editorial-heading mt-1 text-2xl sm:text-3xl text-[#FFF8E8] font-bold">
            Interactive RAG Playground
          </h2>
        </div>

        {/* Index Status Badge */}
        <div className="flex items-center gap-3">
          {healthLoading ? (
            <div className="flex items-center gap-2 rounded-lg bg-[#041E15] px-3.5 py-1.5 text-xs text-[#EDE3C9] border border-[#185338]">
              <RefreshCw className="h-3.5 w-3.5 animate-spin text-[#F6BE2C]" />
              <span>Checking backend...</span>
            </div>
          ) : health?.index_loaded ? (
            <div className="flex items-center gap-2 rounded-lg bg-[#041E15] px-3.5 py-1.5 text-xs text-[#FFF8E8] border border-[#1C7D47]">
              <Database className="h-3.5 w-3.5 text-[#38B36E]" />
              <span>
                <strong>{health.indexed_chunks.toLocaleString()}</strong> Chunks
              </span>
              <span className="text-[#A59475]">|</span>
              <span className="text-[#38B36E] font-mono text-[11px]">
                {health.index_type} (ef={health.ef_search})
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-2 rounded-lg bg-[#3B1219] px-3.5 py-1.5 text-xs text-[#FF8596] border border-[#8C1E2F]">
              <AlertCircle className="h-3.5 w-3.5" />
              <span>Backend Offline (Check port 8000)</span>
            </div>
          )}
        </div>
      </div>

      {/* ── MODE TABS: TEXT vs VOICE ── */}
      <div className="mt-6 flex flex-wrap items-center justify-between gap-4">
        <div className="inline-flex rounded-xl bg-[#041E15] p-1.5 border border-[#185338]">
          <button
            type="button"
            onClick={() => {
              setActiveTab("text");
              setError(null);
            }}
            className={`flex items-center gap-2 rounded-lg px-5 py-2 text-xs font-bold uppercase tracking-wider transition-all ${
              activeTab === "text"
                ? "bg-[#F6BE2C] text-[#073523] shadow-md font-extrabold"
                : "text-[#EDE3C9] hover:text-[#FFF8E8]"
            }`}
          >
            <FileText className="h-4 w-4" />
            <span>Text Query</span>
          </button>

          <button
            type="button"
            onClick={() => {
              setActiveTab("voice");
              setError(null);
            }}
            className={`flex items-center gap-2 rounded-lg px-5 py-2 text-xs font-bold uppercase tracking-wider transition-all ${
              activeTab === "voice"
                ? "bg-[#FF007A] text-white shadow-md font-extrabold"
                : "text-[#EDE3C9] hover:text-[#FFF8E8]"
            }`}
          >
            <Mic className="h-4 w-4" />
            <span>Voice In (STT)</span>
          </button>
        </div>

        {/* Language Selection */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-[#EDE3C9] font-medium">Target Language:</span>
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="rounded-lg border border-[#185338] bg-[#041E15] px-3 py-2 text-xs text-[#F6BE2C] font-semibold focus:border-[#F6BE2C] focus:outline-none cursor-pointer"
          >
            {LANGUAGE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value} className="bg-[#073523] text-white">
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* ── INPUT PANELS ── */}
      <div className="mt-6">
        {activeTab === "text" ? (
          /* TEXT QUERY INPUT */
          <form onSubmit={handleTextSubmit} className="space-y-4">
            <div className="relative">
              <textarea
                value={queryText}
                onChange={(e) => setQueryText(e.target.value)}
                placeholder="Ask a question in English, Hindi, or Bengali (e.g. 'What is a corporation?')..."
                rows={3}
                className="w-full rounded-xl border border-[#185338] bg-[#041E15] p-4 text-sm sm:text-base text-[#FFF8E8] placeholder:text-[#EDE3C9]/40 focus:border-[#F6BE2C] focus:ring-1 focus:ring-[#F6BE2C] focus:outline-none font-sans leading-relaxed"
                disabled={isLoading}
              />
            </div>

            {/* Quick Sample Queries */}
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-[#A59475]">
                Quick Queries:
              </span>
              {SAMPLE_QUERIES.map((sample) => (
                <button
                  key={sample.code}
                  type="button"
                  onClick={() => {
                    setQueryText(sample.text);
                    setSelectedLanguage(sample.code);
                  }}
                  className="rounded-md border border-[#1E5D3F] bg-[#05281A] px-2.5 py-1 text-xs text-[#EDE3C9] hover:border-[#F6BE2C] hover:text-[#F6BE2C] transition-colors"
                >
                  <span className="text-[#F6BE2C] font-semibold">{sample.lang}:</span>{" "}
                  &quot;{sample.text.slice(0, 28)}...&quot;
                </button>
              ))}
            </div>

            {/* Action Bar */}
            <div className="flex justify-end gap-3 pt-2">
              <button
                type="submit"
                disabled={isLoading || !queryText.trim()}
                className="inline-flex items-center gap-2 rounded-lg bg-[#F6BE2C] px-6 py-3 text-xs font-bold uppercase tracking-wider text-[#073523] transition-all hover:bg-[#E5A610] hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed shadow-md shadow-black/20"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    <span>Retrieving & Generating...</span>
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    <span>Run Query</span>
                  </>
                )}
              </button>
            </div>
          </form>
        ) : (
          /* VOICE QUERY INPUT */
          <div className="rounded-xl border border-[#185338] bg-[#041E15] p-6 text-center space-y-6">
            <div className="mx-auto flex max-w-md flex-col items-center">
              <p className="text-sm text-[#EDE3C9] font-medium mb-4">
                Click the microphone to record your question in{" "}
                <span className="text-[#F6BE2C] font-semibold">
                  {LANGUAGE_OPTIONS.find((l) => l.value === selectedLanguage)?.label}
                </span>
                . Audio is processed via Sarvam STT and retrieved with FAISS HNSW.
              </p>

              {/* Pulsating Record Button */}
              <div className="relative my-4">
                {isRecording && (
                  <motion.div
                    className="absolute -inset-4 rounded-full bg-[#FF007A]/30"
                    animate={{ scale: [1, 1.3, 1], opacity: [0.6, 0.2, 0.6] }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  />
                )}

                {!isRecording ? (
                  <button
                    type="button"
                    onClick={handleVoiceStart}
                    disabled={isLoading}
                    className="relative flex h-20 w-20 items-center justify-center rounded-full bg-[#FF007A] text-white shadow-xl shadow-[#FF007A]/30 transition-transform hover:scale-105 active:scale-95 disabled:opacity-50"
                    title="Start Voice Recording"
                  >
                    <Mic className="h-9 w-9" />
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleVoiceStopAndSubmit}
                    disabled={isLoading}
                    className="relative flex h-20 w-20 items-center justify-center rounded-full bg-[#E60067] text-white shadow-xl shadow-[#E60067]/40 transition-transform hover:scale-105 active:scale-95"
                    title="Stop and Transcribe"
                  >
                    <Square className="h-8 w-8 fill-current" />
                  </button>
                )}
              </div>

              {/* Recording Status & Timer */}
              {isRecording && (
                <div className="flex items-center gap-3 mt-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-[#FF007A] animate-ping" />
                  <span className="text-sm font-mono font-bold text-[#FF007A]">
                    Recording: {recordingDuration}s
                  </span>
                  <button
                    type="button"
                    onClick={cancelRecording}
                    className="text-xs text-[#EDE3C9] hover:text-white underline ml-2"
                  >
                    Cancel
                  </button>
                </div>
              )}

              {isLoading && (
                <div className="flex items-center gap-2 mt-4 text-[#F6BE2C] text-sm">
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Transcribing with Sarvam STT & Searching Vector Index...</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* ── ERROR DISPLAY ── */}
      {(error || recorderError) && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 flex items-start gap-3 rounded-xl border border-[#8C1E2F] bg-[#3B1219] p-4 text-sm text-[#FF8596]"
        >
          <XCircle className="h-5 w-5 shrink-0 text-[#FF546D] mt-0.5" />
          <div className="flex-1">
            <p className="font-bold text-white">Execution Error</p>
            <p className="mt-1 text-xs leading-relaxed text-[#FFD0D6]">
              {error || recorderError}
            </p>
          </div>
        </motion.div>
      )}

      {/* ── RESULTS SECTION ── */}
      <AnimatePresence>
        {activeResult && !isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-8 space-y-6 border-t border-[#144833] pt-8"
          >
            {/* 1. Voice Transcript (if voice query) */}
            {lastQueryType === "voice" && voiceResult?.transcript && (
              <div className="rounded-xl border border-[#185338] bg-[#041E15] p-5">
                <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-[#A59475]">
                  <div className="flex items-center gap-2 text-[#F6BE2C]">
                    <Volume2 className="h-4 w-4" />
                    <span>Recognized Speech Transcript</span>
                  </div>
                  <span className="rounded bg-[#073523] px-2 py-0.5 text-[10px] text-[#EDE3C9] border border-[#144833]">
                    STT Latency: {voiceResult.timing.stt_ms.toFixed(1)} ms
                  </span>
                </div>
                <p className="mt-2.5 font-serif text-lg text-[#FFF8E8] italic">
                  &ldquo;{voiceResult.transcript}&rdquo;
                </p>
              </div>
            )}

            {/* 2. Grounded Answer Card */}
            <div className="rounded-xl border border-[#E5D7B5]/30 bg-[#FFFDF8] p-6 sm:p-7 text-[#073523] shadow-lg">
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#E5D7B5] pb-4">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-[#E60067]" />
                  <h3 className="editorial-heading text-xl font-bold text-[#073523]">
                    Grounded Answer
                  </h3>
                </div>

                {/* Guardrail & Confidence Status */}
                <div className="flex items-center gap-2">
                  {activeResult.grounded ? (
                    <span className="inline-flex items-center gap-1.5 rounded-md bg-[#1C7D47]/15 border border-[#1C7D47]/30 px-2.5 py-1 text-[11px] font-bold text-[#1C7D47] uppercase tracking-wider">
                      <ShieldCheck className="h-3.5 w-3.5" />
                      Grounded
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 rounded-md bg-[#E60067]/15 border border-[#E60067]/30 px-2.5 py-1 text-[11px] font-bold text-[#E60067] uppercase tracking-wider">
                      <ShieldAlert className="h-3.5 w-3.5" />
                      Ungrounded / Refusal
                    </span>
                  )}

                  <span className="rounded-md bg-[#073523]/5 px-2.5 py-1 text-[11px] font-mono font-bold text-[#073523] border border-[#073523]/15">
                    Confidence: {(activeResult.confidence_score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>

              {/* Answer Content */}
              <p className="mt-4 font-serif text-base sm:text-lg leading-relaxed text-[#14261D] font-medium">
                {activeResult.answer}
              </p>
            </div>

            {/* 3. Real Latency Breakdown Grid */}
            <div className="rounded-xl border border-[#185338] bg-[#041E15] p-5">
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#F6BE2C] mb-4">
                <Clock className="h-4 w-4" />
                <span>Real Backend Latency Breakdown</span>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {/* Total Latency Card */}
                <div className="rounded-lg border border-[#1C7D47] bg-[#073523] p-3.5">
                  <p className="text-[10px] font-bold uppercase tracking-wider text-[#EDE3C9]">
                    Total Pipeline
                  </p>
                  <p className="mt-1 font-mono text-xl font-bold text-[#38B36E]">
                    {activeResult.timing.total_pipeline_ms.toFixed(2)} ms
                  </p>
                  <p className="text-[10px] text-[#A59475] mt-0.5">
                    {lastQueryType === "voice" ? "Full Voice Roundtrip" : "Post-Query Total"}
                  </p>
                </div>

                {/* Post-STT RAG Latency (for voice) or ONNX Embedding */}
                {lastQueryType === "voice" ? (
                  <div className="rounded-lg border border-[#185338] bg-[#073523] p-3.5">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-[#EDE3C9]">
                      Post-STT RAG Core
                    </p>
                    <p className="mt-1 font-mono text-xl font-bold text-[#F6BE2C]">
                      {(
                        activeResult.timing.total_pipeline_ms -
                        (activeResult.timing.stt_ms || 0)
                      ).toFixed(2)}{" "}
                      ms
                    </p>
                    <p className="text-[10px] text-[#A59475] mt-0.5">
                      Sub-20ms Post-STT Core
                    </p>
                  </div>
                ) : (
                  <div className="rounded-lg border border-[#185338] bg-[#073523] p-3.5">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-[#EDE3C9]">
                      ONNX E5-Small Embed
                    </p>
                    <p className="mt-1 font-mono text-xl font-bold text-[#F6BE2C]">
                      {activeResult.timing.query_embedding_ms.toFixed(2)} ms
                    </p>
                    <p className="text-[10px] text-[#A59475] mt-0.5">Multilingual Vectorizer</p>
                  </div>
                )}

                {/* FAISS Vector Search */}
                <div className="rounded-lg border border-[#185338] bg-[#073523] p-3.5">
                  <p className="text-[10px] font-bold uppercase tracking-wider text-[#EDE3C9]">
                    FAISS HNSW Search
                  </p>
                  <p className="mt-1 font-mono text-xl font-bold text-[#FFF8E8]">
                    {activeResult.timing.vector_search_ms.toFixed(3)} ms
                  </p>
                  <p className="text-[10px] text-[#A59475] mt-0.5">360k-Vector Index (ef=128)</p>
                </div>

                {/* STT or Gate + Synthesizer */}
                {lastQueryType === "voice" ? (
                  <div className="rounded-lg border border-[#185338] bg-[#073523] p-3.5">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-[#EDE3C9]">
                      Sarvam STT API
                    </p>
                    <p className="mt-1 font-mono text-xl font-bold text-[#FF8596]">
                      {activeResult.timing.stt_ms.toFixed(1)} ms
                    </p>
                    <p className="text-[10px] text-[#A59475] mt-0.5">External STT Service</p>
                  </div>
                ) : (
                  <div className="rounded-lg border border-[#185338] bg-[#073523] p-3.5">
                    <p className="text-[10px] font-bold uppercase tracking-wider text-[#EDE3C9]">
                      Gate + Synthesizer
                    </p>
                    <p className="mt-1 font-mono text-xl font-bold text-[#FFF8E8]">
                      {(
                        activeResult.timing.answerability_check_ms +
                        activeResult.timing.llm_generation_ms +
                        activeResult.timing.grounding_validation_ms
                      ).toFixed(3)}{" "}
                      ms
                    </p>
                    <p className="text-[10px] text-[#A59475] mt-0.5">Fast Grounded Generator</p>
                  </div>
                )}
              </div>
            </div>

            {/* 4. Retrieved Source Citations */}
            {activeResult.sources && activeResult.sources.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-[#EDE3C9]">
                  <div className="flex items-center gap-2 text-[#F6BE2C]">
                    <Layers className="h-4 w-4" />
                    <span>Verified Source Citations ({activeResult.sources.length})</span>
                  </div>
                  <span className="text-[11px] text-[#A59475] font-normal">
                    Passed CitationValidator
                  </span>
                </div>

                <div className="space-y-2.5">
                  {activeResult.sources.map((src, idx) => {
                    const isExpanded = expandedSources[src.chunk_id] || false;
                    return (
                      <div
                        key={src.chunk_id}
                        className="rounded-xl border border-[#185338] bg-[#05281A] p-4 transition-all hover:border-[#F6BE2C]/40"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span className="rounded bg-[#1C7D47]/20 border border-[#1C7D47]/40 px-2 py-0.5 font-mono text-xs font-bold text-[#38B36E]">
                              #{idx + 1}
                            </span>
                            <span className="font-mono text-xs text-[#EDE3C9]">
                              ID: {src.chunk_id}
                            </span>
                            <span className="rounded bg-[#073523] px-2 py-0.5 text-[10px] text-[#A59475] border border-[#144833]">
                              {src.language}
                            </span>
                          </div>

                          <div className="flex items-center gap-3">
                            <span className="font-mono text-xs font-bold text-[#F6BE2C]">
                              Similarity: {(src.score * 100).toFixed(1)}%
                            </span>
                            <button
                              type="button"
                              onClick={() => toggleSourceExpand(src.chunk_id)}
                              className="text-xs text-[#EDE3C9] hover:text-[#F6BE2C] flex items-center gap-1"
                            >
                              {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                            </button>
                          </div>
                        </div>

                        {/* Text Excerpt */}
                        <p className="mt-3 font-serif text-sm leading-relaxed text-[#EDE3C9]">
                          {isExpanded
                            ? src.text
                            : src.text.length > 200
                            ? `${src.text.slice(0, 200)}...`
                            : src.text}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}
