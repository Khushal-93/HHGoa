/**
 * HHGoa Voice RAG System - Frontend API Client
 * Connects directly to the FastAPI Grounded RAG backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface SourceItem {
  chunk_id: string;
  text: string;
  score: number;
  language: string;
  metadata?: Record<string, any>;
}

export interface PipelineTiming {
  stt_ms: number;
  query_preprocessing_ms: number;
  query_embedding_ms: number;
  vector_search_ms: number;
  metadata_lookup_ms: number;
  retrieval_total_ms: number;
  answerability_check_ms: number;
  context_build_ms: number;
  llm_generation_ms: number;
  grounding_validation_ms: number;
  api_overhead_ms: number;
  total_pipeline_ms: number;
}

export interface GroundedQueryApiResponse {
  answer: string;
  sources: SourceItem[];
  timing: PipelineTiming;
  grounded: boolean;
  confidence_score: number;
}

export interface VoiceQueryApiResponse {
  transcript: string;
  answer: string;
  sources: SourceItem[];
  timing: PipelineTiming;
  grounded: boolean;
  confidence_score: number;
}

export interface ResultItem {
  chunk_id: string;
  text: string;
  score: number;
  language: string;
  metadata?: Record<string, any>;
}

export interface RetrievalTimingItem {
  embedding_ms: number;
  retrieval_ms: number;
  total_ms: number;
}

export interface RetrievalApiResponse {
  results: ResultItem[];
  timing: RetrievalTimingItem;
}

export interface HealthResponse {
  status: string;
  index_loaded: boolean;
  indexed_chunks: number;
  vector_count: number;
  dimension: number;
  index_type: string;
  ef_search: number | null;
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/**
 * Fetch health status of the backend FAISS index and embedding engine.
 */
export async function healthCheck(): Promise<HealthResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, {
      method: "GET",
      cache: "no-store",
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new ApiError(`Health check failed (${res.status}): ${errorText}`, res.status);
    }

    return await res.json();
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(
      `Cannot reach backend at ${API_BASE_URL}. Ensure the FastAPI server is running.`,
      0
    );
  }
}

/**
 * Execute end-to-end Grounded Text RAG query.
 */
export async function queryRag(query: string): Promise<GroundedQueryApiResponse> {
  const trimmed = query.trim();
  if (!trimmed) {
    throw new ApiError("Query string cannot be empty", 400);
  }

  try {
    const res = await fetch(`${API_BASE_URL}/api/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: trimmed }),
    });

    if (!res.ok) {
      let detail = `HTTP ${res.status}`;
      try {
        const errorJson = await res.json();
        detail = errorJson.detail || detail;
      } catch {
        const rawText = await res.text();
        if (rawText) detail = rawText;
      }
      throw new ApiError(`Query failed: ${detail}`, res.status);
    }

    return await res.json();
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(
      `Network error connecting to backend: ${err.message || err}`,
      0
    );
  }
}

/**
 * Execute retrieval only (passages without answer generation).
 */
export async function retrieve(query: string, topK: number = 5): Promise<RetrievalApiResponse> {
  const trimmed = query.trim();
  if (!trimmed) {
    throw new ApiError("Query string cannot be empty", 400);
  }

  try {
    const res = await fetch(`${API_BASE_URL}/api/retrieve`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query: trimmed, top_k: topK }),
    });

    if (!res.ok) {
      let detail = `HTTP ${res.status}`;
      try {
        const errorJson = await res.json();
        detail = errorJson.detail || detail;
      } catch {
        detail = await res.text();
      }
      throw new ApiError(`Retrieval failed: ${detail}`, res.status);
    }

    return await res.json();
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(
      `Network error connecting to backend: ${err.message || err}`,
      0
    );
  }
}

/**
 * Upload recorded audio to /api/voice/ask for STT transcription and grounded RAG answer.
 */
export async function voiceQuery(
  audioBlob: Blob,
  language: string = "hin_Deva"
): Promise<VoiceQueryApiResponse> {
  if (!audioBlob || audioBlob.size === 0) {
    throw new ApiError("Audio recording is empty", 400);
  }

  // Determine appropriate filename extension from blob mime type
  let filename = "query_audio.webm";
  if (audioBlob.type.includes("wav")) {
    filename = "query_audio.wav";
  } else if (audioBlob.type.includes("mp4") || audioBlob.type.includes("m4a")) {
    filename = "query_audio.mp4";
  } else if (audioBlob.type.includes("ogg")) {
    filename = "query_audio.ogg";
  }

  const formData = new FormData();
  formData.append("file", audioBlob, filename);
  formData.append("language", language);

  try {
    // Note: Do NOT set Content-Type header manually for FormData; browser sets boundary automatically
    const res = await fetch(`${API_BASE_URL}/api/voice/ask`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      let detail = `HTTP ${res.status}`;
      try {
        const errorJson = await res.json();
        detail = errorJson.detail || detail;
      } catch {
        detail = await res.text();
      }
      throw new ApiError(`Voice query failed: ${detail}`, res.status);
    }

    return await res.json();
  } catch (err: any) {
    if (err instanceof ApiError) throw err;
    throw new ApiError(
      `Network error during voice query: ${err.message || err}`,
      0
    );
  }
}
