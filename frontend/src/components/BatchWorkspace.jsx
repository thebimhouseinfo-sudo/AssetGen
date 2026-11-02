import React, { useState } from 'react';
import PromptTemplate from './PromptTemplate';

const BatchWorkspace = ({ projectId, setProjectId, globalSettings, stylePrompt, onOpenGallery }) => {
  const [jobs, setJobs] = useState([]);
  const [errors, setErrors] = useState([]);
  const [pastedText, setPastedText] = useState('');
  const [isParsing, setIsParsing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');

  const createProject = async () => {
    const res = await fetch('http://localhost:8001/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ name: 'AssetGen Batch Project' }),
    });
    if (!res.ok) throw new Error('Không thể tạo project. Kiểm tra backend đang chạy.');
    const project = await res.json();
    setProjectId(project.id);
    return project.id;
  };

  const handleNewProject = async () => {
    try {
      await createProject();
      setErrors([]);
      setStatusMessage('Đã tạo project mới.');
    } catch (err) {
      setErrors([{ code: 'PROJECT_CREATE_FAILED', message: err.message }]);
    }
  };

  const parseFile = async (file) => {
    setIsParsing(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8001/batch/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail?.message || 'Could not parse prompts');
      setJobs(data.jobs || []);
      setErrors(data.errors || []);
    } catch (err) {
      setJobs([]);
      setErrors([{ code: 'PARSE_FAILED', message: err.message }]);
    } finally {
      setIsParsing(false);
    }
  };

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files?.[0];
    if (uploadedFile) parseFile(uploadedFile);
  };

  const handlePasteImport = () => {
    if (!pastedText.trim()) {
      setErrors([{ code: 'EMPTY_INPUT', message: 'Dán nội dung prompt trước khi nhập.' }]);
      setJobs([]);
      return;
    }
    parseFile(new File([pastedText], 'pasted-prompts.txt', { type: 'text/plain' }));
  };

  const updateJob = (index, field, value) => {
    const newJobs = [...jobs];
    newJobs[index][field] = value;
    setJobs(newJobs);
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setStatusMessage('');
    try {
      const activeProjectId = projectId || await createProject();
      const saved = await fetch(`http://localhost:8001/projects/${activeProjectId}/batch/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jobs.map(job => ({
          ...job,
          target_width: globalSettings.width,
          target_height: globalSettings.height,
          output_format: globalSettings.format,
          compression_mode: globalSettings.compression,
          fit_mode: globalSettings.fit_mode,
          max_kb: globalSettings.max_kb,
          background_color: globalSettings.background_color,
          style_prompt: stylePrompt,
        }))),
      });
      if (!saved.ok) {
        const problem = await saved.json();
        const details = problem.detail?.details;
        setErrors(Array.isArray(details) && details.length ? details.map(item => ({ ...item, message: item.message || item.code })) : [{ code: problem.detail?.code || 'SAVE_FAILED', message: problem.detail?.message || 'Không thể lưu prompt.' }]);
        return;
      }
      const res = await fetch('http://localhost:8001/batch/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ project_id: activeProjectId }),
      });
      if (!res.ok) {
        const problem = await res.json();
        throw new Error(problem.detail?.message || 'Không thể xếp hàng tạo ảnh.');
      }
      const result = await res.json();
      setErrors([]);
      if (result.count === 0) {
        setStatusMessage('Không có asset mới để tạo trong project này.');
      } else {
        setStatusMessage(`Đã xếp hàng ${result.count} ảnh. Đang mở Gallery để xem tiến độ.`);
        onOpenGallery();
      }
    } catch (err) {
      setErrors([{ code: 'GENERATE_FAILED', message: err.message || 'Không thể kết nối backend.' }]);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <PromptTemplate />
      {/* Upload Section */}
      <div className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center hover:border-indigo-500 transition-colors group cursor-pointer relative">
        <input
          type="file"
          onChange={handleFileUpload}
          className="absolute inset-0 opacity-0 cursor-pointer"
          accept=".txt"
        />
        <div className="text-gray-400 group-hover:text-gray-200 transition-colors">
          <p className="text-lg font-medium">Drop prompt file here or click to upload</p>
          <p className="text-sm text-gray-500 mt-1">Supports .txt files with === ASSET === blocks</p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-xl border border-gray-700 p-5 space-y-3">
        <label htmlFor="pasted-prompts" className="block text-sm font-semibold text-gray-200">Hoặc dán nội dung prompt</label>
        <textarea
          id="pasted-prompts"
          value={pastedText}
          onChange={(event) => { setPastedText(event.target.value); setJobs([]); setErrors([]); }}
          placeholder={'=== ASSET ===\nname: ten-asset\nratio: 1:1\nprompt: Noi dung prompt\n=== END ==='}
          className="w-full h-40 rounded bg-gray-950 border border-gray-700 p-3 text-sm text-gray-100 font-mono resize-y"
        />
        <button type="button" onClick={handlePasteImport} disabled={isParsing || !pastedText.trim()} className="px-4 py-2 rounded bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-700 disabled:text-gray-500 text-sm font-medium text-white">
          {isParsing ? 'Đang kiểm tra...' : 'Nhập nội dung đã dán'}
        </button>
      </div>

      {/* Project status */}
      <div className="flex items-center gap-3 bg-gray-800 p-3 rounded-lg border border-gray-700">
        <div className="flex-1 min-w-0">
          <span className="text-sm text-gray-300">{projectId ? 'Project hiện tại' : 'Project sẽ được tạo tự động khi Generate'}</span>
          {projectId && <div className="text-xs text-gray-500 truncate">{projectId}</div>}
        </div>
        <button type="button" onClick={handleNewProject} className="px-3 py-1 bg-indigo-600 rounded text-sm">Project mới</button>
      </div>

      {statusMessage && <p role="status" className="text-sm text-green-300">{statusMessage}</p>}

      {/* Errors Display */}
      {errors.length > 0 && (
        <div className="bg-red-900/20 border border-red-900/50 rounded-lg p-4">
          <h3 className="text-red-400 text-sm font-semibold mb-2">Validation Errors ({errors.length})</h3>
          <ul className="text-xs text-red-300 space-y-1">
            {errors.map((err, i) => (
              <li key={i}>Line {err.line || '?'}: {err.message} ({err.asset || 'General'})</li>
            ))}
          </ul>
        </div>
      )}

      {/* Preview Table */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-700/50 text-gray-400 uppercase text-xs font-bold">
            <tr>
              <th className="px-4 py-3">Name</th>
              <th className="px-4 py-3 w-24">Ratio</th>
              <th className="px-4 py-3">Prompt</th>
              <th className="px-4 py-3 w-20">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {jobs.length === 0 ? (
              <tr>
                <td colSpan="4" className="px-4 py-12 text-center text-gray-500 italic">No assets uploaded yet</td>
              </tr>
            ) : (
              jobs.map((job, i) => (
                <tr key={job.id} className="hover:bg-gray-700/30 transition-colors">
                  <td className="px-4 py-3">
                    <input
                      type="text"
                      value={job.name}
                      onChange={(e) => updateJob(i, 'name', e.target.value)}
                      className="bg-transparent border-none focus:ring-0 w-full outline-none"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <input
                      type="text"
                      value={job.ratio || '1:1'}
                      onChange={(e) => updateJob(i, 'ratio', e.target.value)}
                      className="bg-transparent border-none focus:ring-0 w-full outline-none"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <textarea
                      value={job.prompt}
                      onChange={(e) => updateJob(i, 'prompt', e.target.value)}
                      className="bg-transparent border-none focus:ring-0 w-full outline-none resize-none h-8"
                      rows="1"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded-full bg-gray-700 text-gray-400 text-[10px] font-bold uppercase">
                      {job.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Action Button */}
      <button
        onClick={handleGenerate}
        disabled={isGenerating || jobs.length === 0 || errors.some(e => e.level !== 'warning')}
        className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-700 disabled:text-gray-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-indigo-900/20"
      >
        {isGenerating ? 'Generating...' : 'Generate All Assets'}
      </button>
    </div>
  );
};

export default BatchWorkspace;
