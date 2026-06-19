import { useEffect, useState } from "react";
import MainLayout from "../../components/layout/MainLayout";
import api from "../../services/api";
import { BookOpen, Brain, Languages, FileText, Volume2 } from "lucide-react";

export default function Learn() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState("");

  const [classes, setClasses] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [chapters, setChapters] = useState([]);
  const [selectedChapter, setSelectedChapter] = useState("");

  const [profile, setProfile] = useState("beginner");

  const [selectedClass, setSelectedClass] = useState(6);
  const [selectedSubject, setSelectedSubject] = useState("");

  const [hasResponse, setHasResponse] = useState(false);
  const [summary, setSummary] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);

  const [simplifiedText, setSimplifiedText] = useState("");
  const [simplifyLoading, setSimplifyLoading] = useState(false);

  const [hindiText, setHindiText] = useState("");
  const [hindiLoading, setHindiLoading] = useState(false);

  const [quiz, setQuiz] = useState([]);
  const [quizLoading, setQuizLoading] = useState(false);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [score, setScore] = useState(null);

  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (selectedClass) {
      loadSubjects(selectedClass);
    }
  }, [selectedClass]);

  useEffect(() => {
    if (selectedClass && selectedSubject) {
      loadChapters(selectedClass, selectedSubject);
    }
  }, [selectedClass, selectedSubject]);

  const loadInitialData = async () => {
    try {
      const [docsRes, classesRes] = await Promise.all([
        api.get("/documents"),
        api.get("/saksham/classes"),
      ]);

      const docs = docsRes.data?.data?.documents || [];

      const classList = classesRes.data?.data?.classes || [];

      setDocuments(docs);
      setClasses(classList);

      if (docs.length > 0) {
        setSelectedDocument(docs[0].id);
      }

      if (classList.length > 0) {
        setSelectedClass(classList[0]);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const loadSubjects = async (classLevel) => {
    try {
      const response = await api.get(
        `/saksham/subjects?class_level=${classLevel}`,
      );

      const subjectList = response.data?.data?.subjects || [];

      setSubjects(subjectList);

      if (subjectList.length > 0) {
        setSelectedSubject(subjectList[0]);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const loadChapters = async (classLevel, subject) => {
    try {
      const response = await api.get(
        `/saksham/chapters?class_level=${classLevel}&subject=${encodeURIComponent(
          subject,
        )}`,
      );

      const chapterList = response.data?.data?.chapters || [];

      setChapters(chapterList);

      if (chapterList.length > 0) {
        setSelectedChapter(chapterList[0].chapter_title);
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;

    if (!selectedDocument) {
      alert("Please upload/select a document first.");
      return;
    }

    try {
      setLoading(true);

      const response = await api.post("/ask", {
        question,
        source: "document",
        document_id: Number(selectedDocument),
        class_level: Number(selectedClass),
        subject: selectedSubject.toLowerCase(),
        chapter: selectedChapter,
        topic: "",
        mode: "learn",
        accessibility_profile: profile,
        include_audio: false,
      });

      setAnswer(response.data?.data?.answer || "No answer received.");

      setHasResponse(true);
    } catch (error) {
      console.error(error);
      setAnswer("Failed to generate answer.");
      setHasResponse(true);
    } finally {
      setLoading(false);
    }
  };

  const handleSummary = async () => {
    try {
      setSummaryLoading(true);

      const response = await api.post("/summary", {
        source: "document",
        document_id: Number(selectedDocument),
        class_level: Number(selectedClass),
        subject: selectedSubject.toLowerCase(),
        chapter: selectedChapter,
        topic: question || selectedChapter,
        regenerate: false,
        accessibility_profile: profile,
        include_audio: false,
      });

      setSummary(response.data?.data?.summary || "No summary generated.");
    } catch (error) {
      console.error(error);
      alert("Failed to generate summary");
    } finally {
      setSummaryLoading(false);
    }
  };

  const handleSimplify = async () => {
    try {
      setSimplifyLoading(true);

      const response = await api.post("/simplify", {
        question: question,
        source: "document",
        document_id: Number(selectedDocument),
        class_level: Number(selectedClass),
        subject: selectedSubject.toLowerCase(),
        chapter: selectedChapter,
        topic: "",
        accessibility_profile: profile,
        include_audio: false,
      });

      setSimplifiedText(
        response.data?.data?.simplified_answer ||
          "No simplified answer generated.",
      );
    } catch (error) {
      console.error(error);
      alert("Failed to simplify explanation");
    } finally {
      setSimplifyLoading(false);
    }
  };

  const handleHindi = async () => {
    try {
      setHindiLoading(true);

      const response = await api.post("/localize/hi", {
        text: answer,
        content_type: "answer",
        class_level: Number(selectedClass),
        subject: selectedSubject,
        include_audio: false,
        preserve_terms: [],
      });

      setHindiText(
        response.data?.data?.hindi_text || "No translation generated.",
      );
    } catch (error) {
      console.error(error.response?.data);
      console.error(error);

      alert("Hindi translation failed");
    } finally {
      setHindiLoading(false);
    }
  };

  const handleQuiz = async () => {
    try {
      setQuizLoading(true);

      const response = await api.post("/quiz", {
        source: "document",
        document_id: Number(selectedDocument),
        class_level: Number(selectedClass),
        subject: selectedSubject.toLowerCase(),
        chapter: selectedChapter,
        topic: question || selectedChapter,
        question_count: 5,
        accessibility_profile: profile,
        include_audio: false,
      });

      setQuiz(response.data?.data?.questions || []);

      setSelectedAnswers({});
      setScore(null);
    } catch (error) {
      console.error(error.response?.data);
      console.error(error);

      alert("Quiz generation failed");
    } finally {
      setQuizLoading(false);
    }
  };

  const submitQuiz = () => {
    let total = 0;

    quiz.forEach((q, index) => {
      if (selectedAnswers[index] === q.correct_answer) {
        total++;
      }
    });

    setScore(total);
    setQuizSubmitted(true);
  };

  const speakText = (text) => {
    if (!text) return;

    speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;

    utterance.onstart = () => setIsSpeaking(true);

    utterance.onend = () => setIsSpeaking(false);

    speechSynthesis.speak(utterance);
  };

  const stopAudio = () => {
    speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto px-4 md:px-6 py-10">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold text-[#1E3A5F]">
            Learning Workspace
          </h1>

          <p className="mt-3 text-slate-600">
            Ask questions, understand concepts, revise smarter and practice
            effectively.
          </p>
        </div>

        <div className="mt-10 bg-white border border-slate-200 rounded-3xl p-5 shadow-sm">
          <div className="grid md:grid-cols-4 gap-4">
            <select
              value={selectedClass}
              onChange={(e) => setSelectedClass(e.target.value)}
              className="border rounded-xl px-4 py-3"
            >
              {classes.map((cls) => (
                <option key={cls} value={cls}>
                  Class {cls}
                </option>
              ))}
            </select>

            <select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              className="border rounded-xl px-4 py-3"
            >
              {subjects.map((subject) => (
                <option key={subject} value={subject}>
                  {subject}
                </option>
              ))}
            </select>

            <select
              value={selectedChapter}
              onChange={(e) => setSelectedChapter(e.target.value)}
              className="border rounded-xl px-4 py-3"
            >
              {chapters.map((chapter) => (
                <option key={chapter.chapter_id} value={chapter.chapter_title}>
                  {chapter.chapter_title}
                </option>
              ))}
            </select>

            <select
              value={selectedDocument}
              onChange={(e) => setSelectedDocument(e.target.value)}
              className="border rounded-xl px-4 py-3"
            >
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.filename}
                </option>
              ))}
            </select>

            <select
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
              className="border rounded-xl px-4 py-3"
            >
              <option value="beginner">Beginner</option>
              <option value="dyslexia">Dyslexia Friendly</option>
              <option value="visual">Visually Impaired</option>
            </select>
          </div>
        </div>

        <div className="mt-8 grid lg:grid-cols-[1fr_320px] gap-6">
          <div className="space-y-6">
            <div className="bg-white border border-slate-200 rounded-3xl p-6">
              <h2 className="text-xl font-semibold mb-4">Ask Question</h2>

              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask anything from your uploaded document..."
                className="
                  w-full
                  min-h-[140px]
                  resize-none
                  border
                  rounded-2xl
                  p-4
                  outline-none
                "
              />

              <button
                onClick={handleAsk}
                disabled={loading}
                className="
                  mt-4
                  bg-[#1E3A5F]
                  text-white
                  px-6
                  py-3
                  rounded-xl
                  font-medium
                "
              >
                {loading ? "Generating..." : "Ask Saksham AI"}
              </button>
            </div>

            {hasResponse && (
              <>
                <div className="bg-white border border-slate-200 rounded-3xl p-6">
                  <h2 className="text-xl font-semibold mb-4">Explanation</h2>

                  {loading ? (
                    <div className="text-slate-500">Generating answer...</div>
                  ) : (
                    <div className="whitespace-pre-wrap leading-8 text-slate-700">
                      {answer}
                    </div>
                  )}
                </div>

                {summary && (
                  <div className="bg-white border border-slate-200 rounded-3xl p-6">
                    <h2 className="text-xl font-semibold mb-4">Summary</h2>

                    {summaryLoading ? (
                      <div className="text-slate-500">
                        Generating summary...
                      </div>
                    ) : (
                      <div className="whitespace-pre-wrap leading-8 text-slate-700">
                        {summary}
                      </div>
                    )}
                  </div>
                )}

                {simplifiedText && (
                  <div className="bg-white border border-slate-200 rounded-3xl p-6">
                    <h2 className="text-xl font-semibold mb-4">
                      Simplified Explanation
                    </h2>

                    {simplifyLoading ? (
                      <div className="text-slate-500">Simplifying...</div>
                    ) : (
                      <div className="whitespace-pre-wrap leading-8 text-slate-700">
                        {simplifiedText}
                      </div>
                    )}
                  </div>
                )}

                {hindiText && (
                  <div className="bg-white border border-slate-200 rounded-3xl p-6">
                    <h2 className="text-xl font-semibold mb-4">
                      Hindi Explanation
                    </h2>

                    {hindiLoading ? (
                      <div className="text-slate-500">Translating...</div>
                    ) : (
                      <div className="whitespace-pre-wrap leading-8 text-slate-700">
                        {hindiText}
                      </div>
                    )}
                  </div>
                )}

                {quiz.length > 0 && (
                  <div className="bg-white border border-slate-200 rounded-3xl p-6">
                    <h2 className="text-xl font-semibold mb-6">Quiz</h2>

                    {quiz.map((q, index) => (
                      <div key={index} className="mb-8">
                        <p className="font-medium mb-4">
                          {index + 1}. {q.question}
                        </p>

                        {["A", "B", "C", "D"].map((option) => (
                          <label
                            key={option}
                            className={`block mb-2 p-2 rounded-lg ${
                              quizSubmitted && option === q.correct_answer
                                ? "bg-green-50 border border-green-300"
                                : quizSubmitted &&
                                    selectedAnswers[index] === option &&
                                    option !== q.correct_answer
                                  ? "bg-red-50 border border-red-300"
                                  : ""
                            }`}
                          >
                            <input
                              type="radio"
                              disabled={quizSubmitted}
                              name={`question-${index}`}
                              value={option}
                              checked={selectedAnswers[index] === option}
                              onChange={() =>
                                setSelectedAnswers({
                                  ...selectedAnswers,
                                  [index]: option,
                                })
                              }
                              className="mr-2"
                            />
                            {option}. {q.options[option]}
                            {quizSubmitted && q.correct_answer === option && (
                              <span className="ml-2 text-green-600 font-medium">
                                ✓ Correct Answer
                              </span>
                            )}
                            {quizSubmitted &&
                              selectedAnswers[index] === option &&
                              option !== q.correct_answer && (
                                <span className="ml-2 text-red-600 font-medium">
                                  ✗ Your Choice
                                </span>
                              )}
                          </label>
                        ))}
                      </div>
                    ))}

                    <button
                      onClick={submitQuiz}
                      disabled={quizSubmitted}
                      className={`
        bg-[#1E3A5F]
        text-white
        px-6
        py-3
        rounded-xl
        ${quizSubmitted ? "opacity-50 cursor-not-allowed" : ""}
      `}
                    >
                      Submit Quiz
                    </button>

                    {score !== null && (
                      <div className="mt-4 font-semibold">
                        <div className="mt-6 p-4 rounded-2xl bg-slate-50">
                          <h3 className="font-semibold">Quiz Result</h3>

                          <p className="mt-2">
                            Score: {score}/{quiz.length}
                          </p>

                          <p className="text-slate-500 mt-1">
                            {Math.round((score / quiz.length) * 100)}% Accuracy
                          </p>
                        </div>

                        <button
                          onClick={() => {
                            setQuiz([]);
                            setScore(null);
                            setQuizSubmitted(false);
                            setSelectedAnswers({});
                            handleQuiz();
                            setQuizSubmitted(false);
                          }}
                          className="
    mt-4
    border
    px-4                              
    py-2
    rounded-xl
  "
                        >
                          Generate New Quiz
                        </button>
                      </div>
                    )}
                  </div>
                )}

                <div className="bg-white border border-slate-200 rounded-3xl p-6">
                  <h2 className="text-xl font-semibold mb-4">Sources</h2>

                  <div className="text-slate-500">
                    Document:{" "}
                    {
                      documents.find((d) => d.id === Number(selectedDocument))
                        ?.filename
                    }
                  </div>
                </div>
              </>
            )}
          </div>

          {hasResponse && (
            <div>
              <div className="bg-white border border-slate-200 rounded-3xl p-6 sticky top-24">
                <h2 className="text-xl font-semibold mb-6">Learning Tools</h2>

                <div className="space-y-4">
                  <button
                    onClick={handleQuiz}
                    className="w-full flex items-center gap-3 border rounded-2xl px-4 py-4 hover:bg-slate-50"
                  >
                    <Brain size={20} />
                    Generate Quiz
                  </button>

                  <button
                    onClick={handleSummary}
                    className="w-full flex items-center gap-3 border rounded-2xl px-4 py-4 hover:bg-slate-50"
                  >
                    <FileText size={20} />
                    Summarize
                  </button>

                  <button
                    onClick={handleSimplify}
                    className="w-full flex items-center gap-3 border rounded-2xl px-4 py-4 hover:bg-slate-50"
                  >
                    <BookOpen size={20} />
                    Simplify
                  </button>

                  <button
                    onClick={handleHindi}
                    className="w-full flex items-center gap-3 border rounded-2xl px-4 py-4 hover:bg-slate-50"
                  >
                    <Languages size={20} />
                    Hindi
                  </button>

                  <button
                    onClick={() =>
                      isSpeaking ? stopAudio() : speakText(answer)
                    }
                    className="w-full flex items-center gap-3 border rounded-2xl px-4 py-4 hover:bg-slate-50"
                  >
                    <Volume2 size={20} />
                    {isSpeaking ? "Stop Audio" : "Read Aloud"}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
