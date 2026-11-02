import React, { useEffect, useState } from 'react';
import BatchWorkspace from './components/BatchWorkspace';
import BatchGallery from './components/BatchGallery';
import OutputSettings from './components/OutputSettings';
import StylePresets from './components/StylePresets';

const UI_STATE_KEY = 'assetgen.ui-state';

const readUiState = () => {
  try {
    const saved = JSON.parse(localStorage.getItem(UI_STATE_KEY) || '{}');
    return {
      activeTab: ['batch', 'concept', 'gallery'].includes(saved.activeTab) ? saved.activeTab : 'batch',
      projectId: typeof saved.projectId === 'string' ? saved.projectId : null,
      error: null,
    };
  } catch (error) {
    return {
      activeTab: 'batch',
      projectId: null,
      error: `Saved application state could not be read: ${error.message || error}`,
    };
  }
};

const App = () => {
  const [initialUiState] = useState(readUiState);
  const [activeTab, setActiveTab] = useState(initialUiState.activeTab);
  const [projectId, setProjectId] = useState(initialUiState.projectId);
  const [storageError, setStorageError] = useState(initialUiState.error);
  const [stylePrompt, setStylePrompt] = useState('bright colors, educational style, clean vectors');
  const [globalSettings, setGlobalSettings] = useState({
    width: 512,
    height: 512,
    fit_mode: 'fill',
    format: 'webp',
    compression: 'balanced',
    max_kb: null,
    background_color: '#FFFFFF'
  });

  useEffect(() => {
    try {
      localStorage.setItem(UI_STATE_KEY, JSON.stringify({ activeTab, projectId }));
      setStorageError(null);
    } catch (error) {
      setStorageError(`Application state could not be saved: ${error.message || error}`);
    }
  }, [activeTab, projectId]);

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100 font-sans">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900 px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center font-bold text-white">A</div>
          <h1 className="text-xl font-semibold tracking-tight">AssetGen <span className="text-gray-500 text-sm font-normal">v1.0</span></h1>
        </div>
        <div className="flex items-center gap-4">
          <nav className="flex bg-gray-800 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('batch')}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeTab === 'batch' ? 'bg-gray-700 text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'}`}
            >
              Batch Generate
            </button>
          <button
            onClick={() => setActiveTab('concept')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeTab === 'concept' ? 'bg-gray-700 text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'}`}
          >
            Concept
          </button>
            <button
              onClick={() => setActiveTab('gallery')}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeTab === 'gallery' ? 'bg-gray-700 text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'}`}
            >
              Gallery
            </button>
          </nav>
        </div>
      </header>

      <main className="p-6">
        {storageError && (
          <div role="alert" className="mb-4 rounded border border-amber-800 bg-amber-950/30 p-3 text-xs text-amber-200">
            {storageError}
          </div>
        )}
        {activeTab === 'batch' ? (
          <div className="grid grid-cols-12 gap-6">
            <div className="col-span-8">
              <BatchWorkspace
                projectId={projectId}
                setProjectId={setProjectId}
                globalSettings={globalSettings}
                stylePrompt={stylePrompt}
                onOpenGallery={() => setActiveTab('gallery')}
              />
            </div>
            <div className="col-span-4 flex flex-col gap-6">
              <OutputSettings
                settings={globalSettings}
                setSettings={setGlobalSettings}
              />
              <StylePresets onChange={setStylePrompt} />
            </div>
          </div>
        ) : activeTab === 'concept' ? (
          <section className="rounded-xl border border-gray-700 bg-gray-800 p-6" aria-labelledby="concept-preview-heading">
            <h2 id="concept-preview-heading" className="text-lg font-semibold">Concept preview</h2>
            <p className="mt-3 text-gray-300">Chưa kết nối trình render HTML</p>
            <p className="mt-1 text-sm text-gray-400">Trang này đang được chuẩn bị cho workflow concept mới.</p>
          </section>
        ) : (
          <BatchGallery projectId={projectId} />
        )}
      </main>
    </div>
  );
};

export default App;
