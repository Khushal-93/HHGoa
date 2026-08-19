"use client";

import { useState, useRef, useEffect, useCallback } from "react";

export interface VoiceRecorderState {
  isRecording: boolean;
  recordingDuration: number;
  audioBlob: Blob | null;
  audioUrl: string | null;
  error: string | null;
  isSupported: boolean;
  mimeType: string;
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<Blob | null>;
  cancelRecording: () => void;
  clearAudio: () => void;
}

/**
 * Get preferred browser supported audio MIME type for MediaRecorder.
 */
function getSupportedMimeType(): string {
  if (typeof window === "undefined" || typeof MediaRecorder === "undefined") {
    return "";
  }

  const types = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/ogg;codecs=opus",
    "audio/ogg",
    "audio/mp4",
    "audio/aac",
  ];

  for (const t of types) {
    if (MediaRecorder.isTypeSupported(t)) {
      return t;
    }
  }

  return "";
}

export function useVoiceRecorder(): VoiceRecorderState {
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [recordingDuration, setRecordingDuration] = useState<number>(0);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSupported, setIsSupported] = useState<boolean>(true);
  const [mimeType, setMimeType] = useState<string>("");

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const stopResolveRef = useRef<((blob: Blob | null) => void) | null>(null);

  // Check browser support on mount
  useEffect(() => {
    if (
      typeof window === "undefined" ||
      !navigator?.mediaDevices?.getUserMedia ||
      typeof MediaRecorder === "undefined"
    ) {
      setIsSupported(false);
      setError("Audio recording is not supported in this browser environment.");
      return;
    }

    const detectedMime = getSupportedMimeType();
    setMimeType(detectedMime);
  }, []);

  // Stop tracks helper
  const cleanupStream = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.stop();
      });
      streamRef.current = null;
    }
  }, []);

  // Clear timer helper
  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    setRecordingDuration(0);
  }, []);

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      cleanupStream();
      clearTimer();
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [cleanupStream, clearTimer, audioUrl]);

  const startRecording = useCallback(async () => {
    setError(null);
    audioChunksRef.current = [];

    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }
    setAudioBlob(null);

    if (!navigator?.mediaDevices?.getUserMedia) {
      setError("Microphone API not supported on this browser.");
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 16000,
        },
      });

      streamRef.current = stream;

      const detectedMime = getSupportedMimeType();
      const options: MediaRecorderOptions = detectedMime ? { mimeType: detectedMime } : {};

      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const finalMime = mediaRecorder.mimeType || detectedMime || "audio/webm";
        const blob = new Blob(audioChunksRef.current, { type: finalMime });
        
        cleanupStream();
        clearTimer();
        setIsRecording(false);

        if (blob.size > 0) {
          const url = URL.createObjectURL(blob);
          setAudioBlob(blob);
          setAudioUrl(url);
          if (stopResolveRef.current) {
            stopResolveRef.current(blob);
            stopResolveRef.current = null;
          }
        } else {
          setError("No audio data recorded.");
          if (stopResolveRef.current) {
            stopResolveRef.current(null);
            stopResolveRef.current = null;
          }
        }
      };

      mediaRecorder.onerror = (event: any) => {
        setError(`Recording error: ${event.error?.message || "Unknown error"}`);
        cleanupStream();
        clearTimer();
        setIsRecording(false);
      };

      // Request chunks every 250ms for smooth recording
      mediaRecorder.start(250);
      setIsRecording(true);
      setRecordingDuration(0);

      timerRef.current = setInterval(() => {
        setRecordingDuration((prev) => prev + 1);
      }, 1000);
    } catch (err: any) {
      cleanupStream();
      clearTimer();
      setIsRecording(false);

      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        setError("Microphone permission denied. Please allow microphone access in your browser.");
      } else if (err.name === "NotFoundError" || err.name === "DevicesNotFoundError") {
        setError("No microphone found. Please connect a microphone and try again.");
      } else {
        setError(`Failed to access microphone: ${err.message || err}`);
      }
    }
  }, [audioUrl, cleanupStream, clearTimer]);

  const stopRecording = useCallback((): Promise<Blob | null> => {
    return new Promise((resolve) => {
      if (
        !mediaRecorderRef.current ||
        mediaRecorderRef.current.state === "inactive"
      ) {
        setIsRecording(false);
        resolve(audioBlob);
        return;
      }

      stopResolveRef.current = resolve;
      try {
        mediaRecorderRef.current.stop();
      } catch (e) {
        cleanupStream();
        clearTimer();
        setIsRecording(false);
        resolve(null);
      }
    });
  }, [audioBlob, cleanupStream, clearTimer]);

  const cancelRecording = useCallback(() => {
    if (
      mediaRecorderRef.current &&
      mediaRecorderRef.current.state !== "inactive"
    ) {
      stopResolveRef.current = null; // Don't trigger promise resolution on cancel
      try {
        mediaRecorderRef.current.stop();
      } catch {}
    }
    cleanupStream();
    clearTimer();
    setIsRecording(false);
    audioChunksRef.current = [];
    setAudioBlob(null);
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }
  }, [audioUrl, cleanupStream, clearTimer]);

  const clearAudio = useCallback(() => {
    setAudioBlob(null);
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
      setAudioUrl(null);
    }
    setError(null);
  }, [audioUrl]);

  return {
    isRecording,
    recordingDuration,
    audioBlob,
    audioUrl,
    error,
    isSupported,
    mimeType,
    startRecording,
    stopRecording,
    cancelRecording,
    clearAudio,
  };
}
