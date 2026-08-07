import api from "./api";

// Helper to automatically retry slow Edge AI requests that time out via the tunnel (502 Bad Gateway)
async function callApiWithRetry(apiCall, maxRetries = 40, delayMs = 6000) {
  let attempt = 0;
  while (attempt < maxRetries) {
    try {
      return await apiCall();
    } catch (err) {
      attempt++;
      const isTimeoutOr502 = !err.response || 
                             err.response.status === 502 || 
                             err.response.status === 503 || 
                             err.response.status === 504 ||
                             err.code === "ECONNABORTED";
                             
      if (isTimeoutOr502 && attempt < maxRetries) {
        console.warn(`Edge AI generating response... (Tunnel timed out with ${err.response?.status || 'Network Error'}, retrying ${attempt}/${maxRetries} in ${delayMs/1000}s)`);
        await new Promise(resolve => setTimeout(resolve, delayMs));
        continue;
      }
      throw err;
    }
  }
}

export async function fetchDocuments() {
  const res = await api.get("/documents");
  return res.data?.data?.documents || [];
}

export async function fetchDocument(documentId) {
  const res = await api.get(`/document/${documentId}`);
  return res.data?.data;
}

export async function deleteDocument(documentId) {
  const res = await api.delete(`/document/${documentId}`);
  return res.data?.data;
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await api.post("/upload", formData);
  return res.data?.data;
}

export async function fetchClasses() {
  const res = await api.get("/saksham/classes");
  return res.data?.data?.classes || [];
}

export async function fetchSubjects(classLevel) {
  const res = await api.get(`/saksham/subjects?class_level=${classLevel}`);
  return res.data?.data?.subjects || [];
}

export async function fetchChapters(classLevel, subject) {
  const res = await api.get(
    `/saksham/chapters?class_level=${classLevel}&subject=${encodeURIComponent(subject)}`,
  );
  return res.data?.data?.chapters || [];
}

export async function askQuestion(payload) {
  const res = await callApiWithRetry(() => api.post("/ask", payload));
  return res.data?.data?.answer || "No answer received.";
}

export async function generateSummary(payload) {
  const res = await callApiWithRetry(() => api.post("/summary", payload));
  return res.data?.data?.summary || "No summary generated.";
}

export async function simplifyExplanation(payload) {
  const res = await callApiWithRetry(() => api.post("/simplify", payload));
  return res.data?.data?.simplified_answer || "No simplified answer generated.";
}

export async function localizeHindi(payload) {
  const res = await callApiWithRetry(() => api.post("/localize/hi", payload));
  return res.data?.data?.hindi_text || "No translation generated.";
}

export async function generateQuiz(payload) {
  const res = await callApiWithRetry(() => api.post("/quiz", payload));
  const questions = res.data?.data?.questions;
  if (!Array.isArray(questions) || questions.length === 0) {
    throw new Error("The server returned an empty quiz.");
  }
  return questions;
}

export async function explainQuizAnswer({ question, options, correct_answer, student_answer, topic, subject, class_level }) {
  const res = await callApiWithRetry(() => api.post("/quiz/explain", {
    question,
    options,
    correct_answer,
    student_answer,
    topic,
    subject,
    class_level,
  }));
  return res.data?.data || null;
}

export async function explainQuizBatch(questions, studentAnswers, topic, subject, classLevel) {
  const res = await callApiWithRetry(() => api.post("/quiz/explain/batch", {
    questions,
    student_answers: studentAnswers,
    topic,
    subject,
    class_level: classLevel,
  }));
  return res.data?.data?.explanations || [];
}

export async function checkHealth() {
  const res = await api.get("/health");
  return res.data;
}

export function buildLearningPayload({
  source = "saksham",
  documentId,
  classLevel,
  subject,
  chapter,
  topic = "",
  profile = "standard",
  includeAudio = false,
}) {
  const payload = {
    source,
    accessibility_profile: profile === "standard" || !profile ? null : profile,
    include_audio: includeAudio,
  };

  if (source === "document") {
    const parsedDocumentId = Number(documentId);
    if (!Number.isInteger(parsedDocumentId) || parsedDocumentId <= 0) {
      throw new Error("Select an uploaded document first.");
    }
    payload.document_id = parsedDocumentId;
  } else {
    const parsedClassLevel = Number(classLevel);
    if (!Number.isInteger(parsedClassLevel) || !subject || !chapter) {
      throw new Error("Select a class, subject, and chapter first.");
    }
    payload.class_level = parsedClassLevel;
    payload.subject = subject;
    payload.chapter = chapter;
    if (topic) payload.topic = topic;
  }

  return payload;
}
