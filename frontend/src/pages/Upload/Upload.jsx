import { useState, useRef } from "react";
import { motion } from "framer-motion";
import {
  Upload as UploadIcon,
  FileText,
  Trash2,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
} from "lucide-react";
import MainLayout from "../../components/layout/MainLayout";
import PageHeader from "../../components/ui/PageHeader";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import { LoadingState } from "../../components/ui/Spinner";
import KnowledgeBackground from "../../components/background/KnowledgeBackground";
import { useDocuments } from "../../hooks/useLearning";
import { uploadDocument, deleteDocument } from "../../services/learningApi";

export default function Upload() {
  const { documents, loading, reload } = useDocuments();
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });
  const [deletingId, setDeletingId] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const handleUpload = async () => {
    if (!file) {
      setMessage({ type: "error", text: "Please select a PDF file." });
      return;
    }
    if (file.type !== "application/pdf" && !file.name.toLowerCase().endsWith(".pdf")) {
      setMessage({ type: "error", text: "Only PDF files are supported." });
      return;
    }
    if (file.size > 25 * 1024 * 1024) {
      setMessage({ type: "error", text: "PDF files must be 25 MB or smaller." });
      return;
    }

    try {
      setUploading(true);
      setMessage({ type: "", text: "" });
      const data = await uploadDocument(file);
      setMessage({
        type: "success",
        text: `Uploaded successfully. Document ID: ${data.document_id}`,
      });
      setFile(null);
      if (inputRef.current) inputRef.current.value = "";
      await reload();
    } catch (error) {
      setMessage({ type: "error", text: error.message });
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId) => {
    if (!confirm("Delete this document and its indexed content?")) return;
    try {
      setDeletingId(docId);
      await deleteDocument(docId);
      await reload();
      setMessage({ type: "success", text: "Document deleted." });
    } catch (error) {
      setMessage({ type: "error", text: error.message });
    } finally {
      setDeletingId(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped?.type === "application/pdf") {
      setFile(dropped);
    } else {
      setMessage({ type: "error", text: "Only PDF files are supported." });
    }
  };

  return (
    <MainLayout>
      <KnowledgeBackground intensity="subtle" />
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <PageHeader
          eyebrow="Knowledge Library"
          title="Upload learning material"
          description="Upload PDFs and Saksham AI will index them for Q&A, summaries, quizzes, and adaptive learning."
        />

        <Card className="mt-8">
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            className={`
              border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer
              transition-all duration-300
              ${
                dragOver
                  ? "border-accent bg-accent/5"
                  : "border-border hover:border-accent/50 hover:bg-accent/3"
              }
            `}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,application/pdf"
              onChange={(e) => {
                setFile(e.target.files[0] || null);
                setMessage({ type: "", text: "" });
              }}
              className="hidden"
            />
            <div className="w-14 h-14 mx-auto rounded-2xl bg-accent/10 text-accent flex items-center justify-center">
              <UploadIcon size={24} />
            </div>
            <p className="mt-4 font-semibold text-primary">
              {file ? file.name : "Drop your PDF here or click to browse"}
            </p>
            <p className="mt-2 text-sm text-ink-muted">
              PDF files only · Curriculum notes, textbooks, study guides
            </p>
          </div>

          <div className="mt-6 flex flex-wrap gap-3">
            <Button onClick={handleUpload} loading={uploading} icon={UploadIcon}>
              {uploading ? "Processing..." : "Upload PDF"}
            </Button>
          </div>

          {message.text && (
            <div
              className={`mt-4 flex items-center gap-2 text-sm font-medium ${
                message.type === "success" ? "text-success" : "text-error"
              }`}
            >
              {message.type === "success" ? (
                <CheckCircle2 size={16} />
              ) : (
                <AlertCircle size={16} />
              )}
              {message.text}
            </div>
          )}
        </Card>

        <div className="mt-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-primary">Document Library</h2>
            <Badge variant="neural">{documents.length} documents</Badge>
          </div>

          {loading ? (
            <LoadingState message="Loading documents..." />
          ) : documents.length === 0 ? (
            <Card className="text-center py-16">
              <FileText size={40} className="mx-auto text-ink-faint" />
              <p className="mt-4 text-ink-muted">No documents uploaded yet.</p>
              <p className="text-sm text-ink-faint mt-1">
                Upload a PDF to start learning.
              </p>
            </Card>
          ) : (
            <div className="space-y-4">
              {documents.map((doc, i) => (
                <motion.div
                  key={doc.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Card hover className="group">
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                      <div className="flex items-start gap-4 flex-1 min-w-0">
                        <div className="w-11 h-11 rounded-xl bg-primary/8 text-primary flex items-center justify-center shrink-0">
                          <FileText size={20} />
                        </div>
                        <div className="min-w-0">
                          <h3 className="font-semibold text-primary truncate">
                            {doc.filename}
                          </h3>
                          <p className="text-xs text-ink-muted mt-1">
                            ID: {doc.id}
                          </p>
                          {doc.summary && (
                            <p className="mt-3 text-sm text-ink-muted line-clamp-3 leading-relaxed">
                              {doc.summary}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <Button
                          variant="secondary"
                          size="sm"
                          icon={ArrowRight}
                          to={`/learn?source=document&document=${doc.id}`}
                        >
                          Learn
                        </Button>
                        <Button
                          variant="danger"
                          size="sm"
                          icon={Trash2}
                          loading={deletingId === doc.id}
                          onClick={() => handleDelete(doc.id)}
                        >
                          Delete
                        </Button>
                      </div>
                    </div>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
