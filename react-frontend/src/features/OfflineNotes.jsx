import React, { useState } from 'react';
import { Download, Loader2, FileText } from 'lucide-react';

const API = 'http://localhost:8000';

export function OfflineNotesButton({ moduleId, token, moduleTitle }) {
  const [isLoading, setIsLoading] = useState(false);

  const handleDownload = async () => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API}/modules/${moduleId}/offline-notes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Failed to fetch notes');
      const data = await res.json();
      
      const element = document.createElement("a");
      const file = new Blob([data.notes], {type: 'text/markdown'});
      element.href = URL.createObjectURL(file);
      element.download = `${moduleTitle.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_notes.md`;
      document.body.appendChild(element); // Required for this to work in FireFox
      element.click();
    } catch (err) {
      alert("Could not generate notes: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button 
      onClick={handleDownload}
      disabled={isLoading}
      className="flex items-center gap-2 px-4 py-2 bg-subtle border border-border rounded-lg hover:bg-overlay transition-colors text-sm text-text-secondary disabled:opacity-50"
    >
      {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
      <span>{isLoading ? 'Generating...' : 'Offline Notes'}</span>
    </button>
  );
}
