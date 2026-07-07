import { useState, useEffect, useRef, useCallback } from "react";
import api from "../services/api";

// Procedural sound effects using Web Audio API
class AudioSynthCues {
  constructor() {
    this.ctx = null;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
  }

  playMicOpen() {
    this.init();
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    
    // Quick rising ding-up tone
    const now = this.ctx.currentTime;
    osc.type = "sine";
    osc.frequency.setValueAtTime(440, now);
    osc.frequency.exponentialRampToValueAtTime(880, now + 0.15);
    
    gain.gain.setValueAtTime(0.15, now);
    gain.gain.linearRampToValueAtTime(0.01, now + 0.18);
    
    osc.start(now);
    osc.stop(now + 0.2);
  }

  playSuccess() {
    this.init();
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    
    // Pleasant double beep
    const now = this.ctx.currentTime;
    osc.type = "sine";
    osc.frequency.setValueAtTime(660, now);
    osc.frequency.setValueAtTime(880, now + 0.1);
    
    gain.gain.setValueAtTime(0.12, now);
    gain.gain.linearRampToValueAtTime(0.01, now + 0.25);
    
    osc.start(now);
    osc.stop(now + 0.28);
  }

  playError() {
    this.init();
    if (!this.ctx) return;
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.connect(gain);
    gain.connect(this.ctx.destination);
    
    // Low double buzz
    const now = this.ctx.currentTime;
    osc.type = "sawtooth";
    osc.frequency.setValueAtTime(150, now);
    osc.frequency.setValueAtTime(100, now + 0.12);
    
    gain.gain.setValueAtTime(0.15, now);
    gain.gain.linearRampToValueAtTime(0.01, now + 0.3);
    
    osc.start(now);
    osc.stop(now + 0.35);
  }
}

const audioCues = new AudioSynthCues();

export function useVoiceAssistant() {
  const [isActive, setIsActive] = useState(false);
  const [status, setStatus] = useState("idle"); // idle, listening, processing, speaking, error
  const [transcript, setTranscript] = useState("");
  const [log, setLog] = useState([]);
  
  // Slots Context
  const [classLevel, setClassLevel] = useState(null);
  const [subject, setSubject] = useState(null);
  const [chapter, setChapter] = useState(null);

  // Phase 2: Active Task and Progress States
  const [activeTask, setActiveTask] = useState("idle"); // idle, summary, quiz
  const [summaryParagraphs, setSummaryParagraphs] = useState([]);
  const [summaryParagraphIdx, setSummaryParagraphIdx] = useState(0);
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [quizQuestionIdx, setQuizQuestionIdx] = useState(0);
  const [quizScore, setQuizScore] = useState(0);
  
  const recognitionRef = useRef(null);
  const synthesisRef = useRef(null);
  const isStartedRef = useRef(false);
  const shouldListenRef = useRef(false);
  
  const addLog = useCallback((message, type = "info") => {
    setLog((prev) => [...prev, { text: message, type, time: new Date().toLocaleTimeString() }]);
  }, []);

  const speakText = useCallback((text, onEndCallback = null) => {
    if (typeof window === "undefined" || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    
    setStatus("speaking");
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.volume = 0.9;
    
    utterance.onend = () => {
      setStatus("idle");
      if (onEndCallback) {
        setTimeout(onEndCallback, 300); // 300ms delay to allow browser audio subsystem to release device lock
      }
    };
    utterance.onerror = () => {
      setStatus("idle");
      if (onEndCallback) {
        setTimeout(onEndCallback, 300);
      }
    };
    
    window.speechSynthesis.speak(utterance);
  }, []);

  const stopSpeaking = useCallback(() => {
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setStatus("idle");
  }, []);

  const startListening = useCallback(() => {
    if (!recognitionRef.current) return;
    
    // Stop TTS if speaking so the mic doesn't catch it
    stopSpeaking();
    
    shouldListenRef.current = true;
    if (!isStartedRef.current) {
      try {
        recognitionRef.current.start();
      } catch (e) {
        addLog(`Mic activation error: ${e.message}`, "error");
      }
    }
  }, [stopSpeaking, addLog]);

  const stopListening = useCallback(() => {
    shouldListenRef.current = false;
    if (recognitionRef.current && isStartedRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  // Helper to read a specific paragraph of the summary
  const readSummaryParagraph = useCallback((paragraphs, idx) => {
    if (idx < 0 || idx >= paragraphs.length) {
      speakText("You have reached the end of the summary. Returning to the main menu.");
      setActiveTask("idle");
      return;
    }
    const paragraphText = paragraphs[idx];
    const prefix = idx === 0 ? "Reading the chapter summary. " : "";
    const suffix = idx === paragraphs.length - 1 
      ? ". This is the end of the summary. What would you like to do next? You can say start quiz, read summary again, or ask a question."
      : ". Would you like to hear the next part? You can say next, back, or stop.";
      
    speakText(`${prefix}${paragraphText}${suffix}`, () => {
      if (idx < paragraphs.length - 1) {
        startListening();
      } else {
        setActiveTask("idle");
      }
    });
  }, [speakText, startListening]);

  // Helper to read a specific quiz question
  const readQuizQuestion = useCallback((questions, idx) => {
    if (idx < 0 || idx >= questions.length) {
      return;
    }
    const q = questions[idx];
    const prefix = idx === 0 ? `Starting the quiz of ${questions.length} questions. ` : "";
    const questionSpeech = `${prefix}Question ${idx + 1}. ${q.question}. Option A: ${q.options.A}. Option B: ${q.options.B}. Option C: ${q.options.C}. Option D: ${q.options.D}. What is your answer?`;
    
    speakText(questionSpeech, () => {
      startListening();
    });
  }, [speakText, startListening]);

  // Helper to handle MCQ option selection
  const handleQuizAnswer = useCallback((answer, questions, idx, currentScore) => {
    const currentQ = questions[idx];
    const isCorrect = answer.toUpperCase() === currentQ.correct_answer.toUpperCase();
    let newScore = currentScore;
    
    if (isCorrect) {
      audioCues.playSuccess();
      newScore = currentScore + 1;
      setQuizScore(newScore);
    } else {
      audioCues.playError();
    }
    
    const feedback = isCorrect 
      ? `Correct! ` 
      : `Incorrect. The correct answer was option ${currentQ.correct_answer}. `;
      
    const nextIdx = idx + 1;
    if (nextIdx < questions.length) {
      speakText(`${feedback} Ready for the next question.`, () => {
        setQuizQuestionIdx(nextIdx);
        readQuizQuestion(questions, nextIdx);
      });
    } else {
      speakText(`${feedback} Quiz complete! You scored ${newScore} out of ${questions.length}. Returning to the main menu. You can say start quiz, read summary, or ask a question.`, () => {
        setActiveTask("idle");
      });
    }
  }, [speakText, readQuizQuestion]);

  // Handle parsing results and state updates
  const handleParse = useCallback(async (textInput) => {
    if (!textInput?.trim()) return;
    
    const cleanInput = textInput.toLowerCase().trim();
    
    // --- Phase 2: Client-side navigation / answer shortcuts ---
    if (activeTask === "summary") {
      if (["yes", "yeah", "yup", "sure", "ok", "okay", "next", "continue", "read next"].some(v => cleanInput.includes(v))) {
        addLog(`Shortcut: Next Paragraph`, "success");
        const nextIdx = summaryParagraphIdx + 1;
        setSummaryParagraphIdx(nextIdx);
        readSummaryParagraph(summaryParagraphs, nextIdx);
        return;
      }
      if (["back", "previous", "go back", "read previous"].some(v => cleanInput.includes(v))) {
        addLog(`Shortcut: Previous Paragraph`, "success");
        const prevIdx = Math.max(0, summaryParagraphIdx - 1);
        setSummaryParagraphIdx(prevIdx);
        readSummaryParagraph(summaryParagraphs, prevIdx);
        return;
      }
      if (["repeat", "read again", "say again", "once more"].some(v => cleanInput.includes(v))) {
        addLog(`Shortcut: Repeat Paragraph`, "success");
        readSummaryParagraph(summaryParagraphs, summaryParagraphIdx);
        return;
      }
      if (["no", "nope", "stop", "cancel", "exit", "finish", "done"].some(v => cleanInput.includes(v))) {
        addLog(`Shortcut: Stop Summary`, "info");
        setActiveTask("idle");
        speakText("Stopping summary reading. Returning to main menu.");
        return;
      }
    }
    
    if (activeTask === "quiz") {
      // Check for MCQ answers: option A, option B, choice A, etc. or just "A" / "B"
      const match = cleanInput.match(/\b(option|choice|answer\s*is|select)?\s*\b([a-d])\b/);
      if (match && cleanInput.split(/\s+/).length <= 3) {
        const selectedOption = match[2].toUpperCase();
        addLog(`Shortcut: Select Option ${selectedOption}`, "success");
        handleQuizAnswer(selectedOption, quizQuestions, quizQuestionIdx, quizScore);
        return;
      }
      if (["repeat", "read again", "say again", "once more"].some(v => cleanInput.includes(v))) {
        addLog(`Shortcut: Repeat Question`, "success");
        readQuizQuestion(quizQuestions, quizQuestionIdx);
        return;
      }
      if (["stop", "cancel", "exit", "quit"].some(v => cleanInput.includes(v))) {
        addLog(`Shortcut: Stop Quiz`, "info");
        setActiveTask("idle");
        speakText("Stopping the quiz. Returning to main menu.");
        return;
      }
    }

    setStatus("processing");
    addLog(`Parsing: "${textInput}"`, "process");
    
    try {
      const response = await api.post("/voice/parse", {
        transcript: textInput,
        class_level: classLevel,
        subject: subject,
        chapter: chapter,
      });
      
      const { success, data } = response.data;
      if (!success || !data) throw new Error("Invalid backend NLU response");
      
      const { intent, class_level: newClass, subject: newSubject, chapter: newChapter, query } = data;
      
      addLog(`Parsed intent: ${intent} | Slots: Class=${newClass}, Subject=${newSubject}, Chapter=${newChapter}`, "success");
      
      // Update slots
      if (newClass) setClassLevel(newClass);
      if (newSubject) setSubject(newSubject);
      if (newChapter) setChapter(newChapter);

      audioCues.playSuccess();

      // State Dialogue flow logic
      if (intent === "stop") {
        speakText("Stopping voice assistant mode. Goodbye!");
        setIsActive(false);
        setActiveTask("idle");
        return;
      }
      
      if (intent === "repeat") {
        speakText(`We are in Class ${newClass || classLevel || "Not Set"} ${newSubject || subject || "Not Set"}, Chapter: ${newChapter || chapter || "Not Set"}. You can say read summary, start quiz, or ask me any question.`, () => {
          startListening();
        });
        return;
      }

      // Check slot context flow
      if (!newClass && !classLevel) {
        speakText("Which class are you in? Please say Class 6, 7, 8, 9, or 10.", () => {
          startListening();
        });
        return;
      }

      if (!newSubject && !subject) {
        speakText(`Great, Class ${newClass || classLevel}. Which subject? Say Science or Social Science.`, () => {
          startListening();
        });
        return;
      }

      if (!newChapter && !chapter) {
        speakText(`Class ${newClass || classLevel} ${newSubject || subject}. Which chapter would you like to study?`, () => {
          startListening();
        });
        return;
      }

      // Context is complete! Class, Subject, and Chapter resolved
      if (intent === "set_context") {
        speakText(`Okay, we are in Class ${newClass || classLevel} ${newSubject || subject}, Chapter: ${newChapter || chapter}. You can say read summary, start quiz, or ask me any question.`, () => {
          // Keep active but idle
        });
        return;
      }

      if (intent === "generate_quiz") {
        setStatus("processing");
        addLog("Generating quiz...", "process");
        speakText("Generating the quiz. Please wait.", async () => {
          try {
            const response = await api.post("/quiz", {
              source: "saksham",
              class_level: newClass || classLevel,
              subject: newSubject || subject,
              chapter: newChapter || chapter,
              question_count: 5
            });
            const { success, data } = response.data;
            if (!success || !data?.questions || data.questions.length === 0) {
              throw new Error("Could not generate quiz questions");
            }
            
            setActiveTask("quiz");
            setQuizQuestions(data.questions);
            setQuizQuestionIdx(0);
            setQuizScore(0);
            readQuizQuestion(data.questions, 0);
          } catch (e) {
            audioCues.playError();
            setStatus("error");
            addLog(`Quiz error: ${e.message}`, "error");
            speakText("Sorry, I encountered an error generating the quiz. Returning to main menu.");
          }
        });
        return;
      }

      if (intent === "get_summary") {
        setStatus("processing");
        addLog("Fetching revision summary...", "process");
        speakText("Fetching the revision summary. Please wait.", async () => {
          try {
            const response = await api.post("/summary", {
              source: "saksham",
              class_level: newClass || classLevel,
              subject: newSubject || subject,
              chapter: newChapter || chapter
            });
            const { success, data } = response.data;
            if (!success || !data?.summary) throw new Error("Could not load summary");
            
            const summaryText = data.summary;
            const paragraphs = summaryText
              .split(/\n+/)
              .map(p => p.trim())
              .filter(p => p.length > 0);
              
            if (paragraphs.length === 0) {
              speakText("Sorry, the summary text is empty. Returning to main menu.");
              return;
            }
            
            setActiveTask("summary");
            setSummaryParagraphs(paragraphs);
            setSummaryParagraphIdx(0);
            readSummaryParagraph(paragraphs, 0);
          } catch (e) {
            audioCues.playError();
            setStatus("error");
            addLog(`Summary error: ${e.message}`, "error");
            speakText("Sorry, I encountered an error fetching the summary. Returning to main menu.");
          }
        });
        return;
      }

      if (intent === "ask_question" && query) {
        setStatus("processing");
        addLog(`Querying RAG: "${query}"`, "process");
        speakText("Searching the context, please wait.", async () => {
          try {
            const response = await api.post("/ask", {
              question: query,
              source: "saksham",
              class_level: newClass || classLevel,
              subject: newSubject || subject,
              chapter: newChapter || chapter
            });
            const { success, data } = response.data;
            if (!success || !data?.answer) throw new Error("Could not get answer from RAG");
            
            const answer = data.answer;
            speakText(`${answer}. Do you have any other questions? Or say start quiz or read summary.`, () => {
              startListening();
            });
          } catch (e) {
            audioCues.playError();
            setStatus("error");
            addLog(`RAG error: ${e.message}`, "error");
            speakText("Sorry, I had trouble finding an answer to that question. Please try asking again.", () => {
              startListening();
            });
          }
        });
        return;
      }

      // Default state guide
      speakText("Context set. Say read summary, start quiz, or ask a question.");

    } catch (error) {
      audioCues.playError();
      setStatus("error");
      addLog(`NLU parse error: ${error.message}`, "error");
      speakText("Sorry, I had trouble parsing that. Please say that again.", () => {
        startListening();
      });
    }
  }, [
    classLevel,
    subject,
    chapter,
    speakText,
    startListening,
    addLog,
    activeTask,
    summaryParagraphs,
    summaryParagraphIdx,
    quizQuestions,
    quizQuestionIdx,
    quizScore,
    readSummaryParagraph,
    readQuizQuestion,
    handleQuizAnswer
  ]);

  // Toggle Assistant Mode
  const toggleAssistant = useCallback(() => {
    if (isActive) {
      stopSpeaking();
      stopListening();
      setIsActive(false);
      setActiveTask("idle");
      
      // Reset slots and states completely back to scratch
      setClassLevel(null);
      setSubject(null);
      setChapter(null);
      setTranscript("");
      setLog([]);
      setSummaryParagraphs([]);
      setSummaryParagraphIdx(0);
      setQuizQuestions([]);
      setQuizQuestionIdx(0);
      setQuizScore(0);
    } else {
      setIsActive(true);
      setActiveTask("idle");
      
      // Clear logs first when enabling so it starts fresh
      setLog([{ text: "Voice assistant enabled.", type: "info", time: new Date().toLocaleTimeString() }]);
      
      speakText("Hello! I am Saksham Voice Assistant. Let's set up your workspace. Which class are you in?", () => {
        startListening();
      });
    }
  }, [isActive, speakText, startListening, stopListening, stopSpeaking]);

  const handleParseRef = useRef(handleParse);
  const statusRef = useRef(status);
  const addLogRef = useRef(addLog);

  // Keep references up to date to avoid running useEffect cleanup/init on every state change
  useEffect(() => {
    handleParseRef.current = handleParse;
  }, [handleParse]);

  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  useEffect(() => {
    addLogRef.current = addLog;
  }, [addLog]);

  // Hook Initialization
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      addLogRef.current("SpeechRecognition is not supported in this browser.", "error");
      return;
    }

    // Check for Brave browser silently closing SpeechRecognition connection
    if (navigator.brave && typeof navigator.brave.isBrave === 'function') {
      navigator.brave.isBrave().then(isBrave => {
        if (isBrave) {
          addLogRef.current("Brave browser detected! Brave does not support Google Speech Recognition backend. It will fail silently. Please use Google Chrome or Safari.", "error");
        }
      });
    }
    
    const rec = new SpeechRecognition();
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = "en-IN"; // Set to Indian English accent
    
    rec.onstart = () => {
      isStartedRef.current = true;
      setStatus("listening");
      audioCues.playMicOpen();
      addLogRef.current("Microphone active. Listening...", "mic");
    };

    rec.onresult = (event) => {
      const resultText = event.results[0][0].transcript;
      setTranscript(resultText);
      
      shouldListenRef.current = false;
      rec.stop();
      
      handleParseRef.current(resultText);
    };
    
    rec.onerror = (event) => {
      shouldListenRef.current = false;
      if (event.error === "no-speech") {
        addLogRef.current("No speech detected. Timed out.", "info");
        setStatus("idle");
      } else if (event.error === "not-allowed") {
        addLogRef.current("Microphone access denied! Click the lock icon in the address bar to allow microphone access.", "error");
        setStatus("error");
        audioCues.playError();
      } else if (event.error === "network") {
        addLogRef.current("Speech recognition requires an internet connection (Google Speech Service). Please check your connection.", "error");
        setStatus("error");
        audioCues.playError();
      } else if (event.error === "service-not-allowed") {
        addLogRef.current("Speech service not allowed. If using Brave, enable Google Speech Services in brave://settings.", "error");
        setStatus("error");
        audioCues.playError();
      } else {
        addLogRef.current(`Speech Recognition error: ${event.error}`, "error");
        audioCues.playError();
        setStatus("error");
      }
    };
    
    rec.onend = () => {
      isStartedRef.current = false;
      setStatus("idle");
      if (shouldListenRef.current) {
        try {
          rec.start();
        } catch (e) {
          console.error("Error restarting recognition:", e);
        }
      }
    };
    
    recognitionRef.current = rec;
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  // Key Event bindings (Spacebar to listen, Escape to stop)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!isActive) return;
      
      if (e.code === "Space" && status !== "listening" && status !== "processing" && status !== "speaking") {
        e.preventDefault();
        startListening();
      } else if (e.code === "Escape") {
        e.preventDefault();
        stopSpeaking();
        stopListening();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isActive, status, startListening, stopSpeaking, stopListening]);

  return {
    isActive,
    status,
    transcript,
    log,
    classLevel,
    subject,
    chapter,
    activeTask,
    summaryParagraphs,
    summaryParagraphIdx,
    quizQuestions,
    quizQuestionIdx,
    quizScore,
    toggleAssistant,
    startListening,
    stopListening,
    speakText,
    stopSpeaking,
    clearLog: () => setLog([]),
  };
}
