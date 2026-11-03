import React, { useState, useRef, useEffect } from 'react';
import * as monaco from 'monaco-editor';
import { useTheme } from '../context/ThemeContext';
import {
  Play,
  CheckCircle2,
  AlertTriangle,
  RotateCcw,
  FileCode,
  Info,
  ChevronDown,
  ChevronUp,
  Loader2,
  Terminal,
  Sparkles,
  BookOpen
} from 'lucide-react';
import { FeedbackWidget } from '../components/FeedbackWidget';
import './EditorPage.css';

const DEFAULT_SAMPLE_CODE = `// Sample C++ Program with Compiler Diagnostics
#include <iostream>

int main() {
    int count = 10
    std::cout << "Count is: " << count << std::endl;
    std::cout << undeclared_var << std::endl;
    return 0;
}
`;

const INITIAL_PREVIEW_RESULT = {
  submission_id: 1,
  compile_status: 'error',
  duration_ms: 184,
  raw_compiler_output: `/workspace/main.cpp: In function 'int main()':
/workspace/main.cpp:5:5: error: expected ';' before 'std'
/workspace/main.cpp:6:19: error: 'undeclared_var' was not declared in this scope
/workspace/main.cpp:6:19: note: suggested alternative: 'count'`,
  errors: [
    {
      id: 1,
      line: 5,
      column: 5,
      severity: 'error',
      message: "expected ';' before 'std'",
      notes: [],
      is_primary: true,
      is_follow_on: false,
      category: null,
      confidence: null,
      abstained: false
    },
    {
      id: 2,
      line: 6,
      column: 19,
      severity: 'error',
      message: "'undeclared_var' was not declared in this scope",
      notes: ["suggested alternative: 'count'"],
      is_primary: false,
      is_follow_on: true,
      category: null,
      confidence: null,
      abstained: false
    }
  ]
};

export const EditorPage = () => {
  const { theme } = useTheme();
  const editorContainerRef = useRef(null);
  const editorInstanceRef = useRef(null);
  const prevDecorationsRef = useRef([]);

  const [code, setCode] = useState(DEFAULT_SAMPLE_CODE);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(INITIAL_PREVIEW_RESULT);
  const [errorBanner, setErrorBanner] = useState('');
  const [showRawOutput, setShowRawOutput] = useState(true);
  const [activeErrorId, setActiveErrorId] = useState(1);

  // Initialize Monaco directly from bundled local package
  useEffect(() => {
    if (!editorContainerRef.current) return;

    const editor = monaco.editor.create(editorContainerRef.current, {
      value: code,
      language: 'cpp',
      theme: theme === 'dark' ? 'vs-dark' : 'vs',
      quickSuggestions: false,
      suggestOnTriggerCharacters: false,
      parameterHints: { enabled: false },
      snippetSuggestions: 'none',
      wordBasedSuggestions: 'off',
      lightbulb: { enabled: false },
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      fontSize: 13,
      fontFamily: "'JetBrains Mono', 'Fira Code', Consolas, monospace",
      lineNumbersMinChars: 3,
      renderLineHighlight: 'all',
      automaticLayout: true
    });

    editorInstanceRef.current = editor;

    editor.onDidChangeModelContent(() => {
      setCode(editor.getValue());
    });

    return () => {
      editor.dispose();
    };
  }, []);

  // Sync theme
  useEffect(() => {
    if (editorInstanceRef.current) {
      monaco.editor.setTheme(theme === 'dark' ? 'vs-dark' : 'vs');
    }
  }, [theme]);

  // Synchronize decorations (error underlines) when analysis results arrive
  useEffect(() => {
    if (!editorInstanceRef.current) return;
    const editor = editorInstanceRef.current;

    if (!result || !result.errors || result.errors.length === 0) {
      prevDecorationsRef.current = editor.deltaDecorations(prevDecorationsRef.current, []);
      return;
    }

    const newDecorations = result.errors
      .filter(err => err.line && err.line > 0)
      .map(err => {
        const isErr = err.severity === 'error' || err.severity === 'fatal error';
        return {
          range: new monaco.Range(err.line, err.column || 1, err.line, (err.column || 1) + 12),
          options: {
            isWholeLine: !err.column,
            className: isErr ? 'monaco-error-line' : 'monaco-warning-line',
            hoverMessage: { value: `**${err.severity.toUpperCase()}**: ${err.message}` }
          }
        };
      });

    prevDecorationsRef.current = editor.deltaDecorations(prevDecorationsRef.current, newDecorations);
  }, [result]);

  const handleAnalyze = async () => {
    if (!code.trim()) {
      setErrorBanner('Please enter some C++ code to analyze.');
      return;
    }

    setAnalyzing(true);
    setErrorBanner('');

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ code })
      });

      const data = await response.json();

      if (!response.ok) {
        if (response.status === 429) {
          throw new Error('Analysis rate limit exceeded. Please wait a moment before trying again.');
        } else if (response.status === 503) {
          throw new Error(data.detail || 'Compiler sandbox is busy. Please try again in a few seconds.');
        } else {
          throw new Error(data.detail || 'Compilation request failed.');
        }
      }

      setResult(data);
      if (data.errors && data.errors.length > 0) {
        setActiveErrorId(data.errors[0].id || 0);
        jumpToLine(data.errors[0].line, data.errors[0].column);
      }
    } catch (err) {
      setErrorBanner(err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const jumpToLine = (line, col) => {
    if (!editorInstanceRef.current || !line) return;
    editorInstanceRef.current.revealLineInCenter(line);
    editorInstanceRef.current.setPosition({ lineNumber: line, column: col || 1 });
    editorInstanceRef.current.focus();
  };

  const handleReset = () => {
    if (editorInstanceRef.current) {
      editorInstanceRef.current.setValue(DEFAULT_SAMPLE_CODE);
    }
    setCode(DEFAULT_SAMPLE_CODE);
    setResult(null);
    setErrorBanner('');
  };

  return (
    <div className="editor-page-layout">
      {errorBanner && (
        <div className="alert alert-error banner-alert">
          <AlertTriangle size={16} style={{ flexShrink: 0 }} />
          <span>{errorBanner}</span>
        </div>
      )}

      {/* Main Split Layout */}
      <div className="editor-main-split">
        {/* Left: Monaco Editor Container */}
        <div className="editor-pane">
          <div className="pane-header editor-header-bar">
            <div className="compiler-badge">
              <FileCode size={15} />
              <span className="file-name">main.cpp</span>
              <span className="compiler-tag">g++ C++17 (Sandbox)</span>
            </div>

            <div className="pane-header-actions">
              <button
                onClick={handleReset}
                className="btn btn-secondary btn-sm"
                title="Reset to sample code"
                disabled={analyzing}
              >
                <RotateCcw size={13} />
                <span>Reset</span>
              </button>

              <button
                onClick={handleAnalyze}
                className="btn btn-primary btn-sm btn-analyze"
                disabled={analyzing}
              >
                {analyzing ? (
                  <>
                    <Loader2 size={14} className="spin" />
                    <span>Compiling...</span>
                  </>
                ) : (
                  <>
                    <Play size={13} fill="currentColor" />
                    <span>Analyze Code</span>
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="monaco-wrapper" ref={editorContainerRef} style={{ width: '100%', height: '100%' }} />
        </div>

        {/* Right: Diagnostic Cards Pane */}
        <div className="diagnostics-pane">
          <div className="pane-header">
            <span className="pane-title">Compiler Diagnostics</span>
            {result && (
              <span className="duration-tag">
                {result.duration_ms} ms
              </span>
            )}
          </div>

          <div className="diagnostics-content">
            {!result ? (
              <div className="empty-diagnostics-state">
                <Terminal size={36} className="empty-icon" />
                <h3>Ready to Compile</h3>
                <p>
                  Click <strong>Analyze Code</strong> to compile your C++ code in the isolated sandbox.
                  Real compiler errors will be parsed into structured cards here.
                </p>
              </div>
            ) : result.compile_status === 'clean' ? (
              <div className="clean-compilation-card">
                <CheckCircle2 size={32} className="clean-icon" />
                <div>
                  <h3>Compiled Cleanly</h3>
                  <p>g++ compiled and linked without any errors or warnings.</p>
                </div>
              </div>
            ) : (
              <div className="error-cards-list">
                <div className="results-summary-bar">
                  <span className="summary-title">
                    {result.errors.filter(e => e.severity === 'error' || e.severity === 'fatal error').length} Errors,{' '}
                    {result.errors.filter(e => e.severity === 'warning').length} Warnings
                  </span>
                  <span className="summary-sub">
                    Click any card to highlight and jump to the affected line
                  </span>
                </div>

                {result.errors.map((diag, idx) => {
                  const isErr = diag.severity === 'error' || diag.severity === 'fatal error';
                  const isSelected = activeErrorId === (diag.id || idx);

                  return (
                    <div
                      key={diag.id || idx}
                      className={`diagnostic-card ${isErr ? 'card-error' : 'card-warning'} ${isSelected ? 'selected' : ''}`}
                      onClick={() => {
                        setActiveErrorId(diag.id || idx);
                        jumpToLine(diag.line, diag.column);
                      }}
                    >
                      <div className="card-top-meta">
                        <div className="meta-left">
                          <span className={`badge ${isErr ? 'badge-error' : 'badge-warning'}`}>
                            {diag.severity.toUpperCase()}
                          </span>

                          {diag.category && diag.category !== 'ABSTAINED' && (
                            <span className="badge badge-category" title="Machine Learning Classification">
                              <Sparkles size={11} className="badge-icon" />
                              {diag.category.replace(/_/g, ' ')}
                            </span>
                          )}

                          {diag.is_primary && (
                            <span className="badge badge-primary-indicator" title="First syntax root cause">
                              Primary Error
                            </span>
                          )}

                          {diag.is_follow_on && (
                            <span className="badge badge-followon-indicator" title="Likely cascading from earlier error">
                              Follow-on
                            </span>
                          )}
                        </div>

                        <div className="meta-right">
                          {diag.abstained ? (
                            <span className="badge badge-abstained" title="Prediction confidence below safe threshold">
                              Abstained
                            </span>
                          ) : diag.confidence ? (
                            <span className="badge badge-confidence" title={`Calibrated Confidence: ${(diag.confidence * 100).toFixed(0)}%`}>
                              {(diag.confidence * 100).toFixed(0)}% Match
                            </span>
                          ) : null}

                          {diag.line && (
                            <span className="line-coord-badge">
                              Line {diag.line}{diag.column ? `:${diag.column}` : ''}
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="card-message">
                        <code>{diag.message}</code>
                      </div>

                      {diag.notes && diag.notes.length > 0 && (
                        <div className="card-notes-block">
                          <span className="notes-header">
                            <Info size={12} /> Compiler Hint:
                          </span>
                          {diag.notes.map((n, nIdx) => (
                            <p key={nIdx} className="note-text">{n}</p>
                          ))}
                        </div>
                      )}

                      {diag.explanation && (
                        <div className="card-explanation-block">
                          <div className="explanation-header">
                            <BookOpen size={14} className="explanation-icon" />
                            <span className="explanation-title">{diag.explanation.title}</span>
                          </div>
                          <p className="explanation-text">{diag.explanation.what_happened}</p>

                          {diag.explanation.how_to_fix && diag.explanation.how_to_fix.length > 0 && (
                            <div className="fix-list">
                              <span className="fix-list-title">Actionable Fix:</span>
                              <ul>
                                {diag.explanation.how_to_fix.map((step, sIdx) => (
                                  <li key={sIdx}>{step}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {diag.explanation.example_wrong && diag.explanation.example_fixed && (
                            <div className="example-comparison">
                              <div className="example-box example-wrong">
                                <span className="example-label label-wrong">Problematic</span>
                                <pre><code>{diag.explanation.example_wrong}</code></pre>
                              </div>
                              <div className="example-box example-fixed">
                                <span className="example-label label-fixed">Corrected</span>
                                <pre><code>{diag.explanation.example_fixed}</code></pre>
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {diag.id && (
                        <FeedbackWidget errorId={diag.id} initialCategory={diag.category} />
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Collapsible Raw Output Drawer */}
          {result && (
            <div className="raw-output-drawer">
              <button
                className="raw-drawer-toggle"
                onClick={() => setShowRawOutput(!showRawOutput)}
              >
                <span>Raw Compiler Log (g++ stdout/stderr)</span>
                {showRawOutput ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
              </button>

              {showRawOutput && (
                <pre className="raw-output-terminal">
                  {result.raw_compiler_output || '(No compiler output)'}
                </pre>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
