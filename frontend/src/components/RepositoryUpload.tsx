import { useState, useRef } from "react";
import { Upload, Loader2, CheckCircle, XCircle, FolderArchive } from "lucide-react";

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
        message: "Please upload a .zip file",
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

      const data = await response.json();
      setUploadStatus({
        type: "success",
        message: `Successfully uploaded ${file.name}. Processing in background...`,
      });
      onUploadSuccess?.();
    } catch (error) {
      setUploadStatus({
        type: "error",
        message: "Upload failed. Make sure the backend is running.",
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
    <div className="w-full max-w-4xl mx-auto mb-8">
      <div
        className={`border-2 border-dashed rounded-lg p-8 transition-all ${
          dragActive
            ? "border-blue-500 bg-blue-500/10"
            : "border-slate-600 bg-slate-800/50"
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
            <div className="space-y-4">
              <Loader2 className="w-16 h-16 text-blue-500 mx-auto animate-spin" />
              <p className="text-gray-300 font-medium">Uploading...</p>
            </div>
          ) : (
            <div className="space-y-4">
              <FolderArchive className="w-16 h-16 text-gray-500 mx-auto" />
              <div>
                <p className="text-gray-300 font-medium mb-2">
                  Drag & drop a .zip file here
                </p>
                <p className="text-gray-500 text-sm mb-4">or</p>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
                >
                  <Upload className="w-5 h-5 inline mr-2" />
                  Choose File
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-4">
                Upload a .zip file containing your source code repository
              </p>
            </div>
          )}
        </div>

        {/* Status Messages */}
        {uploadStatus.type && (
          <div
            className={`mt-6 p-4 rounded-lg flex items-center gap-3 ${
              uploadStatus.type === "success"
                ? "bg-green-500/10 border border-green-500/50"
                : "bg-red-500/10 border border-red-500/50"
            }`}
          >
            {uploadStatus.type === "success" ? (
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
            ) : (
              <XCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
            )}
            <p
              className={`text-sm ${
                uploadStatus.type === "success"
                  ? "text-green-300"
                  : "text-red-300"
              }`}
            >
              {uploadStatus.message}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
