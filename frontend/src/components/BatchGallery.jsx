import React, { useState, useEffect } from 'react';

const API = 'http://localhost:8001';

const BatchGallery = ({ projectId }) => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [selectedId, setSelectedId] = useState(null);
  const [editedPrompt, setEditedPrompt] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const selected = status?.jobs.find(job => job.id === selectedId);

  const fetchStatus = async () => {
    if (!projectId) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/batch/status?project_id=${projectId}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail?.message || 'Không thể đọc tiến độ.');
      setStatus(data);
    } catch (err) {
      setMessage(err.message || 'Không thể kết nối để đọc tiến độ.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setStatus(null);
    setSelectedId(null);
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, [projectId]);

  const openImage = job => {
    setSelectedId(job.id);
    setEditedPrompt(job.prompt || '');
    setMessage('');
  };

  const regenerate = async () => {
    if (!selected || !editedPrompt.trim()) return;
    setSubmitting(true);
    setMessage('');
    try {
      const res = await fetch(`${API}/batch/regenerate`, {
        method: 'POST',
        body: new URLSearchParams({ project_id: projectId, job_id: selected.id, prompt: editedPrompt.trim() }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Không thể tạo lại ảnh.');
      setMessage('Đã đưa ảnh vào hàng chờ tạo lại.');
      await fetchStatus();
    } catch (err) {
      setMessage(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const openFolder = async () => {
    try {
      const res = await fetch(`${API}/projects/${projectId}/open-image-folder`, { method: 'POST' });
      if (!res.ok) throw new Error('Không thể mở thư mục ảnh.');
    } catch (err) {
      setMessage(err.message);
    }
  };

  const copyFolder = async () => {
    try {
      await navigator.clipboard.writeText(status.image_folder);
      setMessage('Đã sao chép đường dẫn thư mục ảnh.');
    } catch {
      setMessage('Không thể sao chép. Bạn có thể chọn và sao chép đường dẫn bên dưới.');
    }
  };

  if (!projectId) return <div className="text-center py-12 text-gray-500">Hãy nhập prompt và bấm Generate trước.</div>;
  if (loading && !status) return <div className="text-center py-12 text-gray-500">Đang tải ảnh...</div>;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap justify-between items-center gap-3">
        <div>
          <h2 className="text-xl font-semibold">Ảnh đã tạo</h2>
          <p className="text-sm text-gray-400 mt-1">Bấm vào ảnh để xem prompt, sửa và tạo lại.</p>
        </div>
        <div className="flex gap-2">
          <button onClick={fetchStatus} className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-md text-sm">Làm mới</button>
          <button onClick={openFolder} className="px-3 py-2 bg-indigo-600 rounded-md text-sm">Mở thư mục ảnh</button>
        </div>
      </div>
      {status?.image_folder && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-3 flex flex-wrap items-center gap-3">
          <span className="text-sm text-gray-400">Tất cả ảnh nằm tại:</span>
          <span className="text-sm break-all select-text flex-1">{status.image_folder}</span>
          <button onClick={copyFolder} className="px-3 py-1.5 bg-gray-700 rounded-md text-sm">Copy đường dẫn</button>
        </div>
      )}
      {message && <p className="text-sm text-gray-300" role="status">{message}</p>}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {status?.jobs.map(job => (
          <button key={job.id} type="button" onClick={() => openImage(job)} className="text-left bg-gray-800 border border-gray-700 rounded-xl overflow-hidden hover:border-indigo-500 transition-colors">
            <div className="aspect-square bg-gray-900 relative flex items-center justify-center overflow-hidden">
              {job.image_url ? <img src={`${API}${job.image_url}`} alt={job.name} className="w-full h-full object-cover" /> : <span className="text-gray-500 text-sm">{job.status}</span>}
              <span className="absolute top-2 right-2 px-2 py-0.5 rounded-full bg-black/70 text-white text-xs">{job.status}</span>
            </div>
            <div className="p-3">
              <h3 className="text-sm font-medium truncate">{job.name}</h3>
              {job.output_filename && <p className="text-xs text-gray-400 truncate mt-1">{job.output_filename}</p>}
              {job.error && <p className="text-xs text-red-300 mt-2 break-words">{job.error}</p>}
            </div>
          </button>
        ))}
      </div>
      {status?.jobs.length === 0 && <p className="text-center py-12 text-gray-500">Chưa có ảnh nào trong project này.</p>}

      {selected && (
        <div className="fixed inset-0 z-50 bg-black/75 flex items-center justify-center p-4" onClick={() => setSelectedId(null)}>
          <div role="dialog" aria-modal="true" aria-label={`Sửa prompt cho ${selected.name}`} className="bg-gray-800 border border-gray-700 rounded-xl w-full max-w-3xl max-h-[90vh] overflow-y-auto p-5" onClick={event => event.stopPropagation()}>
            <div className="flex justify-between items-center gap-3 mb-4">
              <h2 className="text-lg font-semibold">{selected.name}</h2>
              <button onClick={() => setSelectedId(null)} aria-label="Đóng" className="text-gray-300 hover:text-white text-xl">×</button>
            </div>
            {selected.image_url && <img src={`${API}${selected.image_url}`} alt={selected.name} className="max-h-80 mx-auto object-contain rounded-lg mb-4" />}
            <label htmlFor="edit-image-prompt" className="block text-sm text-gray-300 mb-2">Prompt</label>
            <textarea id="edit-image-prompt" value={editedPrompt} onChange={event => setEditedPrompt(event.target.value)} rows={5} className="w-full bg-gray-900 border border-gray-600 rounded-lg p-3 text-sm text-white" />
            <div className="flex flex-wrap justify-between items-center gap-3 mt-4">
              <span className="text-sm text-gray-400">{selected.output_filename || selected.status}</span>
              <button onClick={regenerate} disabled={submitting || !editedPrompt.trim() || ['QUEUED', 'GENERATING', 'POSTPROCESSING'].includes(selected.status)} className="px-4 py-2 bg-indigo-600 rounded-md text-sm disabled:opacity-50">{submitting ? 'Đang gửi...' : 'Tạo lại ảnh'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BatchGallery;
