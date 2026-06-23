import { useCallback, useEffect, useRef, useState } from "react";

const VOLUME_KEY = "saksham-voice-volume";
const RATE_KEY = "saksham-voice-rate";

function readStored(key, fallback) {
  if (typeof window === "undefined") return fallback;
  const val = localStorage.getItem(key);
  const num = parseFloat(val);
  return Number.isFinite(num) ? num : fallback;
}

export function useSpeechPlayer() {
  const [status, setStatus] = useState("idle");
  const [volume, setVolumeState] = useState(() => readStored(VOLUME_KEY, 0.85));
  const [rate, setRateState] = useState(() => readStored(RATE_KEY, 1));
  const utteranceRef = useRef(null);
  const textRef = useRef("");

  const buildUtterance = useCallback(
    (text) => {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = rate;
      utterance.pitch = 1;
      utterance.volume = volume;
      utterance.onstart = () => setStatus("playing");
      utterance.onend = () => setStatus("idle");
      utterance.onerror = () => setStatus("idle");
      return utterance;
    },
    [rate, volume],
  );

  const speak = useCallback(
    (text) => {
      if (!text?.trim() || typeof window === "undefined") return;
      window.speechSynthesis.cancel();
      textRef.current = text;
      const utterance = buildUtterance(text);
      utteranceRef.current = utterance;
      window.speechSynthesis.speak(utterance);
    },
    [buildUtterance],
  );

  const pause = useCallback(() => {
    if (typeof window === "undefined") return;
    window.speechSynthesis.pause();
    setStatus("paused");
  }, []);

  const resume = useCallback(() => {
    if (typeof window === "undefined") return;
    window.speechSynthesis.resume();
    setStatus("playing");
  }, []);

  const stop = useCallback(() => {
    if (typeof window !== "undefined") {
      window.speechSynthesis.cancel();
    }
    setStatus("idle");
    utteranceRef.current = null;
  }, []);

  const toggle = useCallback(
    (text) => {
      if (status === "playing") {
        pause();
      } else if (status === "paused") {
        resume();
      } else {
        speak(text);
      }
    },
    [status, pause, resume, speak],
  );

  const setVolume = useCallback((value) => {
    const v = Math.min(1, Math.max(0, value));
    setVolumeState(v);
    localStorage.setItem(VOLUME_KEY, String(v));
    if (utteranceRef.current) utteranceRef.current.volume = v;
  }, []);

  const setRate = useCallback(
    (value) => {
      const r = Math.min(2, Math.max(0.5, value));
      setRateState(r);
      localStorage.setItem(RATE_KEY, String(r));
      if (status === "playing" || status === "paused") {
        stop();
        speak(textRef.current);
      }
    },
    [status, stop, speak],
  );

  useEffect(() => () => stop(), [stop]);

  return {
    status,
    isSpeaking: status === "playing",
    isPaused: status === "paused",
    isActive: status === "playing" || status === "paused",
    speak,
    pause,
    resume,
    toggle,
    stop,
    volume,
    setVolume,
    rate,
    setRate,
  };
}

export function useSpeech() {
  const player = useSpeechPlayer();
  return {
    isSpeaking: player.isSpeaking,
    speak: player.speak,
    stop: player.stop,
  };
}
