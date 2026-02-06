import { useState, useRef } from "react";
import { Upload, Loader2, CheckCircle, XCircle, FolderArchive, X } from "lucide-react";

interface RepositoryUploadProps {
  onUploadSuccess?: () => void;
}

export const RepositoryUpload: React.FC<RepositoryUploadProps> = ({
  onUploadSuccess,
}) => {
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{
    type: "success" | "error" | null;
    message: string;
  }>({ type: null, message: "" });
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (file: File) => {
    if (!file.name.endsWith(".zip")) {
      setUploadStatus({
        type: "error",
        message: "Please upload a .zip file containing your code repository",
      });
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    setUploadStatus({ type: null, message: "" });

    try {
      const response = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      setUploadStatus({
        type: "success",
        message: `Successfully uploaded ${file.name}! Processing embeddings in background...`,
      });
      setTimeout(() => {
        onUploadSuccess?.();
      }, 2000);
    } catch (error) {
      setUploadStatus({
        type: "error",
        message: "Upload failed. Make sure the backend is running on port 8000.",
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleUpload(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleUpload(e.target.files[0]);
    }
  };

  return (
    <div className="w-full">
      <div
        className={`relative border-3 border-dashed rounded-2xl p-12 transition-all ${
          dragActive
            ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20 scale-[1.02]"
            : "border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-900 hover:border-blue-400 dark:hover:border-blue-600"
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".zip"
          onChange={handleChange}
          className="hidden"
          disabled={uploading}
        />

        <div className="text-center">
          {uploading ? (
            <div className="space-y-6">
              <div className="relative inline-flex">
                <div className="absolute inset-0 bg-blue-500 rounded-full animate-ping opacity-25"></div>
                <div className="relative bg-gradient-to-br from-blue-500 to-purple-600 p-6 rounded-full">
                  <Loader2 className="w-12 h-12 text-white animate-spin" />
                </div>
              </div>
              <div>
                <p className="text-xl font-bold text-gray-900 dark:text-white">Uploading...</p>
                <p className="text-gray-600 dark:text-gray-400 mt-2">Processing your repository</p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="inline-flex p-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-xl shadow-blue-500/25">
                <FolderArchive className="w-16 h-16 text-white" />
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
                  Upload Your Repository
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-lg mb-6">
                  Drag & drop a .zip file here, or click to browse
                </p>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl transition-all font-semibold text-lg shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/40 inline-flex items-center gap-3"
                >
                  <Upload className="w-6 h-6" />
                  Choose File
                </button>
              </div>
              <div className="pt-4 border-t border-gray-200 dark:border-gray-800">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  📦 Supported format: .zip files containing source code
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  🤖 AI embeddings will be generated automatically
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Status Messages */}
        {uploadStatus.type && (
          <div
            className={`mt-6 p-5 rounded-xl flex items-start gap-4 border-2 ${
              uploadStatus.type === "success"
                ? "bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700"
                : "bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700"
            }`}
          >
            {uploadStatus.type === "success" ? (
              <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400 flex-shrink-0" />
            ) : (
              <XCircle className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0" />
            )}
            <div className="flex-1">
              <p
                className={`font-semibold ${
                  uploadStatus.type === "success"
                    ? "text-green-900 dark:text-green-100"
                    : "text-red-900 dark:text-red-100"
                }`}
              >
                {uploadStatus.type === "success" ? "Success!" : "Upload Failed"}
              </p>
              <p
                className={`text-sm mt-1 ${
                  uploadStatus.type === "success"
                    ? "text-green-700 dark:text-green-300"
                    : "text-red-700 dark:text-red-300"
                }`}
              >
                {uploadStatus.message}
              </p>
            </div>
            <button
              onClick={() => setUploadStatus({ type: null, message: "" })}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
