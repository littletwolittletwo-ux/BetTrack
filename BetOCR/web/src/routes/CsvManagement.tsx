import { useEffect, useState } from "react";
import { Card, CardTitle } from "@/components/Card";
import { useToast } from "@/components/Toast";

type CsvUpload = {
  id: number;
  original_filename: string;
  uploaded_by: string;
  uploaded_at: string;
  file_size: number;
  records_imported: number;
  records_skipped: number;
  file_exists: boolean;
  days_old: number;
};

export default function CsvManagement() {
  const [uploads, setUploads] = useState<CsvUpload[]>([]);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(7);
  const { push } = useToast();

  const fetchUploads = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const response = await fetch(`/admin/csv/uploads?days=${days}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (!response.ok) throw new Error("Failed to fetch CSV uploads");
      
      const data = await response.json();
      setUploads(data.uploads);
    } catch (err: any) {
      push({ msg: err.message || "Failed to fetch uploads", type: "err" });
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = async (id: number, filename: string) => {
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/admin/csv/uploads/${id}/download`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (!response.ok) throw new Error("Failed to download file");
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      push({ msg: "File downloaded successfully", type: "ok" });
    } catch (err: any) {
      push({ msg: err.message || "Download failed", type: "err" });
    }
  };

  const deleteUpload = async (id: number) => {
    if (!confirm("Are you sure you want to delete this CSV upload?")) return;
    
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/admin/csv/uploads/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (!response.ok) throw new Error("Failed to delete upload");
      
      push({ msg: "Upload deleted successfully", type: "ok" });
      fetchUploads(); // Refresh list
    } catch (err: any) {
      push({ msg: err.message || "Delete failed", type: "err" });
    }
  };

  const cleanupOldFiles = async () => {
    if (!confirm("Are you sure you want to delete all CSV files older than 7 days?")) return;
    
    try {
      const token = localStorage.getItem("token");
      const response = await fetch(`/admin/csv/cleanup?days=7`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (!response.ok) throw new Error("Failed to cleanup files");
      
      const data = await response.json();
      push({ msg: `Cleanup complete: ${data.deleted_files} files, ${data.deleted_records} records deleted`, type: "ok" });
      fetchUploads(); // Refresh list
    } catch (err: any) {
      push({ msg: err.message || "Cleanup failed", type: "err" });
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  useEffect(() => {
    fetchUploads();
  }, [days]);

  return (
    <div className="grid gap-6">
      <Card>
        <CardTitle>CSV Upload Management</CardTitle>
        <div className="text-sm text-mut mb-2">
          CSV files are automatically retained for 7 days only. Downloads are blocked after this period.
        </div>
        <div className="mt-4 flex gap-4 items-center">
          <label className="flex items-center gap-2">
            <span className="text-sm text-mut">Show uploads from last:</span>
            <select 
              value={days} 
              onChange={e => setDays(Number(e.target.value))}
              className="px-2 py-1 border rounded"
            >
              <option value={1}>1 day</option>
              <option value={7}>7 days</option>
            </select>
          </label>
          <button 
            onClick={fetchUploads}
            className="btn px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700"
            disabled={loading}
          >
            {loading ? "Loading..." : "Refresh"}
          </button>
          <button 
            onClick={cleanupOldFiles}
            className="btn px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700"
            disabled={loading}
          >
            Manual Cleanup (7 days)
          </button>
        </div>
      </Card>

      <Card>
        <CardTitle>CSV Uploads ({uploads.length})</CardTitle>
        {loading ? (
          <div className="text-center py-8 text-mut">Loading...</div>
        ) : uploads.length === 0 ? (
          <div className="text-center py-8 text-mut">No CSV uploads found for the selected period</div>
        ) : (
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-line">
                  <th className="text-left py-2">Filename</th>
                  <th className="text-left py-2">Uploaded By</th>
                  <th className="text-left py-2">Date</th>
                  <th className="text-left py-2">Size</th>
                  <th className="text-left py-2">Records</th>
                  <th className="text-left py-2">Age</th>
                  <th className="text-left py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {uploads.map(upload => (
                  <tr key={upload.id} className="border-b border-line/50">
                    <td className="py-2">
                      <div className="flex items-center gap-2">
                        <span className={upload.file_exists ? "text-white" : "text-red-400"}>
                          {upload.original_filename}
                        </span>
                        {!upload.file_exists && (
                          <span className="text-xs text-red-400">(File Missing)</span>
                        )}
                      </div>
                    </td>
                    <td className="py-2 text-mut">{upload.uploaded_by}</td>
                    <td className="py-2 text-mut">{formatDate(upload.uploaded_at)}</td>
                    <td className="py-2 text-mut">{formatFileSize(upload.file_size)}</td>
                    <td className="py-2 text-mut">
                      <span className="text-green-400">{upload.records_imported}</span>
                      {upload.records_skipped > 0 && (
                        <span className="text-red-400"> / {upload.records_skipped} skipped</span>
                      )}
                    </td>
                    <td className="py-2 text-mut">
                      {upload.days_old === 0 ? "Today" : `${upload.days_old} days`}
                    </td>
                    <td className="py-2">
                      <div className="flex gap-2">
                        {upload.file_exists && (
                          <button
                            onClick={() => downloadFile(upload.id, upload.original_filename)}
                            className="text-xs px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded"
                          >
                            Download
                          </button>
                        )}
                        <button
                          onClick={() => deleteUpload(upload.id)}
                          className="text-xs px-2 py-1 bg-red-600 hover:bg-red-700 rounded"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}