import React from 'react';

const OutputSettings = ({ settings, setSettings }) => {
  const update = (field, val) => {
    setSettings({ ...settings, [field]: val });
  };

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 p-5 flex flex-col gap-5">
      <h3 className="text-sm font-bold uppercase text-gray-400 tracking-wider">Output Settings</h3>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1.5">
          <label className="text-xs text-gray-500">Width (px)</label>
          <input
            type="number"
            value={settings.width}
            onChange={(e) => update('width', parseInt(e.target.value))}
            className="bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-sm outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="text-xs text-gray-500">Height (px)</label>
          <input
            type="number"
            value={settings.height}
            onChange={(e) => update('height', parseInt(e.target.value))}
            className="bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-sm outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-xs text-gray-500">Fit Mode</label>
        <select
          value={settings.fit_mode}
          onChange={(e) => update('fit_mode', e.target.value)}
          className="bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-sm outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="fill">Fill (Cover & Crop)</option>
          <option value="fit">Fit (Scale & Pad)</option>
        </select>
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-xs text-gray-500">Format</label>
        <select
          value={settings.format}
          onChange={(e) => update('format', e.target.value)}
          className="bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-sm outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="webp">WebP</option>
          <option value="png">PNG</option>
          <option value="jpeg">JPEG</option>
        </select>
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-xs text-gray-500">Compression</label>
        <select
          value={settings.compression}
          onChange={(e) => update('compression', e.target.value)}
          className="bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-sm outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="lossless">Lossless</option>
          <option value="balanced">Balanced</option>
          <option value="smallest">Smallest</option>
        </select>
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-xs text-gray-500">Max File Size (KB)</label>
        <input
          type="number"
          value={settings.max_kb || ''}
          onChange={(e) => update('max_kb', e.target.value ? parseInt(e.target.value) : null)}
          placeholder="Optional"
          className="bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-sm outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-xs text-gray-500">Background Color</label>
        <div className="flex gap-2">
          <input
            type="color"
            value={settings.background_color}
            onChange={(e) => update('background_color', e.target.value)}
            className="w-8 h-8 bg-transparent border-none p-0 cursor-pointer"
          />
          <input
            type="text"
            value={settings.background_color}
            onChange={(e) => update('background_color', e.target.value)}
            className="bg-gray-900 border border-gray-700 rounded px-2 py-1.5 text-sm flex-1 outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>
      </div>
    </div>
  );
};

export default OutputSettings;
