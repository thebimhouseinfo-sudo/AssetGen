import React, { useState } from 'react';
import template from '../../prompt-template.txt?raw';

const PromptTemplate = () => {
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);

  const copyTemplate = async () => {
    let success = false;
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(template);
        success = true;
      }
    } catch {
      // Fall back to selecting a temporary textarea below.
    }
    if (!success) {
      let fallback;
      try {
        fallback = document.createElement('textarea');
        fallback.value = template;
        fallback.style.position = 'fixed';
        fallback.style.opacity = '0';
        document.body.appendChild(fallback);
        fallback.select();
        success = document.execCommand('copy');
      } catch {
        success = false;
      } finally {
        fallback?.remove();
      }
    }
    if (success) {
      setCopied(true);
      setCopyError(false);
      setTimeout(() => setCopied(false), 2500);
    } else {
      setCopied(false);
      setCopyError(true);
    }
  };

  return (
    <section className="bg-gray-800 rounded-xl border border-gray-700 p-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-bold uppercase text-gray-300">Mẫu yêu cầu AI chat</h2>
          <p className="text-xs text-gray-400 mt-1">Gửi mẫu cho AI chat, rồi mô tả các ảnh bạn muốn tạo. Dán câu trả lời bên dưới hoặc upload file .txt.</p>
        </div>
        <button type="button" onClick={copyTemplate} className="shrink-0 px-3 py-2 rounded bg-indigo-600 hover:bg-indigo-500 text-sm text-white">
          {copied ? 'Đã copy' : 'Copy mẫu'}
        </button>
      </div>
      {copyError && <p role="alert" className="text-xs text-red-300 mt-2">Không thể copy tự động. Hãy thử lại trong trình duyệt.</p>}
    </section>
  );
};

export default PromptTemplate;
