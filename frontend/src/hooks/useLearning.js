import { useEffect, useState } from "react";
import {
  fetchDocuments,
  fetchClasses,
  fetchSubjects,
  fetchChapters,
} from "../services/learningApi";

export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const reload = async () => {
    try {
      setLoading(true);
      setError(null);
      const docs = await fetchDocuments();
      setDocuments(docs);
      return docs;
    } catch (err) {
      setError(err.message);
      return [];
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const docs = await fetchDocuments();
        if (active) setDocuments(docs);
      } catch (err) {
        if (active) setError(err.message);
      } finally {
        if (active) setLoading(false);
      }
    };

    load();

    return () => {
      active = false;
    };
  }, []);

  return { documents, loading, error, reload };
}

export function useCurriculum(initialClass = null) {
  const [classes, setClasses] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [chapters, setChapters] = useState([]);
  const [selectedClass, setSelectedClass] = useState(initialClass || "");
  const [selectedSubject, setSelectedSubject] = useState("");
  const [selectedChapter, setSelectedChapter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const selectClass = (value) => {
    setLoading(true);
    setError(null);
    setSelectedClass(value);
    setSubjects([]);
    setChapters([]);
    setSelectedSubject("");
    setSelectedChapter("");
  };

  const selectSubject = (value) => {
    setLoading(true);
    setError(null);
    setSelectedSubject(value);
    setChapters([]);
    setSelectedChapter("");
  };

  useEffect(() => {
    fetchClasses()
      .then((list) => {
        setClasses(list);
        if (list.length > 0) {
          setSelectedClass((prev) => prev || list[0]);
        } else {
          setLoading(false);
        }
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!selectedClass) return;
    let active = true;
    fetchSubjects(selectedClass)
      .then((list) => {
        if (!active) return;
        setError(null);
        setSubjects(list);
        setSelectedSubject(list[0] || "");
        if (list.length === 0) setLoading(false);
      })
      .catch((err) => {
        if (active) {
          setError(err.message);
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [selectedClass]);

  useEffect(() => {
    if (!selectedClass || !selectedSubject) return;
    let active = true;
    fetchChapters(selectedClass, selectedSubject)
      .then((list) => {
        if (!active) return;
        setError(null);
        setChapters(list);
        setSelectedChapter(list[0]?.chapter_title || "");
      })
      .catch((err) => active && setError(err.message))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, [selectedClass, selectedSubject]);

  return {
    classes,
    subjects,
    chapters,
    selectedClass,
    setSelectedClass: selectClass,
    selectedSubject,
    setSelectedSubject: selectSubject,
    selectedChapter,
    setSelectedChapter,
    loading,
    error,
  };
}

export { useSpeechPlayer, useSpeech } from "./useSpeechPlayer";
