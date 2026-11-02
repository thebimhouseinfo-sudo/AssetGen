import React, { useState } from 'react';

const StylePresets = ({ onChange }) => {
  const [presets] = useState([
    { id: 'kideschool', name: 'Kids School', prompt: 'bright colors, educational style, clean vectors' },
    { id: 'corporate', name: 'Corporate', prompt: 'professional, minimalist, high-contrast blue' },
    { id: 'comic', name: 'Comic Book', prompt: 'ink lines, halftone dots, vibrant colors' },
  ]);
  const [selected, setSelected] = useState('kideschool');
  const [override, setOverride] = useState('');

  const choose = (preset) => {
    setSelected(preset.id);
    onChange([preset.prompt, override].filter(Boolean).join(', '));
  };

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 p-5 flex flex-col gap-5">
      <div className="flex justify-between items-center">
        <h3 className="text-sm font-bold uppercase text-gray-400 tracking-wider">Style Presets</h3>
      </div>

      <div className="flex flex-col gap-2">
        {presets.map(p => (
          <div
            key={p.id}
            onClick={() => choose(p)}
            className={`p-3 rounded-lg border cursor-pointer transition-all ${selected === p.id ? 'bg-indigo-600/20 border-indigo-500 text-white' : 'bg-gray-900 border-gray-700 text-gray-400 hover:border-gray-600'}`}
          >
            <div className="text-sm font-medium">{p.name}</div>
            <div className="text-[10px] opacity-60 truncate mt-1">{p.prompt}</div>
          </div>
        ))}
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-xs text-gray-500">Base Prompt Override</label>
        <textarea
          rows="3"
          value={override}
          onChange={(event) => {
            setOverride(event.target.value);
            const preset = presets.find(item => item.id === selected);
            onChange([preset.prompt, event.target.value].filter(Boolean).join(', '));
          }}
          className="bg-gray-900 border border-gray-700 rounded px-2 py-2 text-sm outline-none focus:ring-1 focus:ring-indigo-500 resize-none"
          placeholder="Add global style modifiers..."
        />
      </div>
    </div>
  );
};

export default StylePresets;
