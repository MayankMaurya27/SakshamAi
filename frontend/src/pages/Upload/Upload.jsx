import { useEffect, useState } from "react";
import MainLayout from "../../components/layout/MainLayout";
import api from "../../services/api";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [message, setMessage] = useState("");

  const loadDocuments = async () => {
    try {
      const res = await api.get("/documents");
      setDocuments(res.data.data.documents || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleUpload = async () => {
    if (!file) {
      setMessage("Please select a PDF.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setMessage("");

      const res = await api.post("/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const data = res.data.data;

      setMessage(
        `Uploaded successfully. Document ID: ${data.document_id}`
      );
      setFile(null);

      await loadDocuments();
    } catch (error) {
      console.error(error);

      setMessage(
        error?.response?.data?.error ||
        "Upload failed."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto px-4 py-10">

        <h1 className="text-4xl font-bold text-[#1E3A5F]">
          Upload Learning Material
        </h1>

        <p className="mt-3 text-slate-600">
          Upload a PDF and Saksham AI will generate
          summaries, quizzes and searchable knowledge.
        </p>

        <div className="mt-8 bg-white rounded-3xl border border-slate-200 p-8">

          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setFile(e.target.files[0])}
          />

          <button
            onClick={handleUpload}
            disabled={loading}
            className="
              mt-5
              bg-[#1E3A5F]
              text-white
              px-6
              py-3
              rounded-xl
            "
          >
            {loading ? "Processing..." : "Upload PDF"}
          </button>

          {message && (
            <div className="mt-4 text-sm">
              {message}
            </div>
          )}

        </div>

        <div className="mt-10">

          <h2 className="text-2xl font-semibold mb-6">
            Document Library
          </h2>

          <div className="space-y-4">

            {documents.length === 0 && (
              <div className="text-slate-500">
                No documents uploaded.
              </div>
            )}

            {documents.map((doc) => (
              <div
                key={doc.id}
                className="
                  bg-white
                  border
                  border-slate-200
                  rounded-2xl
                  p-5
                "
              >
                <div className="flex justify-between items-start">

                  <div>

                    <h3 className="font-semibold">
                      {doc.filename}
                    </h3>

                    <p className="text-sm text-slate-500 mt-1">
                      Document ID: {doc.id}
                    </p>

                  </div>

                </div>

                {doc.summary && (
                  <p className="mt-4 text-slate-600 line-clamp-4">
                    {doc.summary}
                  </p>
                )}

              </div>
            ))}

          </div>

        </div>

      </div>
    </MainLayout>
  );
}