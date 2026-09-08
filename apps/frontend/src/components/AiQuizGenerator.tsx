import { useRef, useState } from 'react';
import { BiTrash, BiUpload } from 'react-icons/bi';
import { BsStars } from 'react-icons/bs';
import { LuFileText, LuLoader } from 'react-icons/lu';
import {
    generateQuiz,
    genaiErrorMessage,
    type GeneratedQuestion,
} from '../services/genaiApi';

// A generated question plus the local review state layered on top of it.
interface DraftQuestion extends GeneratedQuestion {
    selected: boolean;
}

interface Props {
    // Persists one question; the parent owns the quiz API call.
    onSave: (question: GeneratedQuestion, timeLimit: number) => Promise<void>;
    onSaved: () => void;
    onClose: () => void;
}

const DIFFICULTY_STYLES: Record<string, string> = {
    Low: 'bg-green-500/10 text-green-400 border-green-500/20',
    Medium: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
    High: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
};

function AiQuizGenerator({ onSave, onClose, onSaved }: Props) {
    const fileInput = useRef<HTMLInputElement>(null);

    const [file, setFile] = useState<File | null>(null);
    const [prompt, setPrompt] = useState('Generate 5 questions');
    const [timeLimit, setTimeLimit] = useState('15');

    const [drafts, setDrafts] = useState<DraftQuestion[]>([]);
    const [generating, setGenerating] = useState(false);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    const selectedCount = drafts.filter((d) => d.selected).length;

    const handlePick = (picked: File | undefined) => {
        if (!picked) return;

        if (picked.type !== 'application/pdf') {
            setError('Only PDF files are supported.');
            return;
        }

        setError('');
        setFile(picked);
    };

    const handleGenerate = async () => {
        if (!file) return setError('Choose a PDF first.');
        if (!prompt.trim()) return setError('Describe what to generate.');

        setGenerating(true);
        setError('');

        try {
            const questions = await generateQuiz(file, prompt);

            setDrafts(questions.map((q) => ({ ...q, selected: true })));
        } catch (err) {
            setError(genaiErrorMessage(err, 'Failed to generate questions.'));
        } finally {
            setGenerating(false);
        }
    };

    const updateDraft = (idx: number, patch: Partial<DraftQuestion>) => {
        setDrafts((prev) =>
            prev.map((d, i) => (i === idx ? { ...d, ...patch } : d))
        );
    };

    const setCorrect = (qIdx: number, optIdx: number) => {
        setDrafts((prev) =>
            prev.map((d, i) =>
                i === qIdx
                    ? {
                          ...d,
                          options: d.options.map((o, oi) => ({
                              ...o,
                              isCorrect: oi === optIdx,
                          })),
                      }
                    : d
            )
        );
    };

    const setOptionText = (qIdx: number, optIdx: number, text: string) => {
        setDrafts((prev) =>
            prev.map((d, i) =>
                i === qIdx
                    ? {
                          ...d,
                          options: d.options.map((o, oi) =>
                              oi === optIdx ? { ...o, text } : o
                          ),
                      }
                    : d
            )
        );
    };

    const handleSaveSelected = async () => {
        const chosen = drafts.filter((d) => d.selected);

        if (chosen.length === 0) return setError('Select at least one question.');

        const invalid = chosen.find(
            (q) => !q.text.trim() || q.options.some((o) => !o.text.trim())
        );

        if (invalid) return setError('Every question and option needs text.');

        setSaving(true);
        setError('');

        try {
            // Saved sequentially: the API takes one question per request,
            // and this keeps ordering stable in the quiz.
            for (const q of chosen) {
                await onSave(q, parseInt(timeLimit) || 15);
            }

            setDrafts([]);
            setFile(null);
            onSaved();
            onClose();
        } catch {
            setError('Saved some questions, but one failed. Check the list.');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="glass-card py-8 px-10 mt-6 bg-zinc-900/40 border border-purple-800/40 rounded-2xl">
            <div className="flex items-center gap-3 mb-6">
                <BsStars className="w-5 h-5 text-purple-400" />
                <h3 className="font-secondary font-extrabold tracking-wider text-lg text-gray-200">
                    Generate with AI
                </h3>
                <span className="text-xs text-zinc-500 font-secondary tracking-wide">
                    Upload a PDF and describe what you want
                </span>
            </div>

            {/* Upload + prompt */}
            <div className="grid md:grid-cols-[1fr_1fr_auto] gap-4 items-start">
                <div>
                    <input
                        ref={fileInput}
                        type="file"
                        accept="application/pdf"
                        className="hidden"
                        onChange={(e) => handlePick(e.target.files?.[0])}
                    />
                    <button
                        type="button"
                        onClick={() => fileInput.current?.click()}
                        className="w-full flex items-center gap-3 py-4 px-5 rounded-xl border border-dashed border-purple-700/50 bg-purple-900/10 hover:bg-purple-900/20 cursor-pointer transition-colors text-left"
                    >
                        {file ? (
                            <>
                                <LuFileText className="w-5 h-5 text-purple-400 shrink-0" />
                                <span className="text-gray-300 font-secondary text-sm truncate">
                                    {file.name}
                                </span>
                            </>
                        ) : (
                            <>
                                <BiUpload className="w-5 h-5 text-purple-400 shrink-0" />
                                <span className="text-zinc-400 font-secondary text-sm">
                                    Choose a PDF
                                </span>
                            </>
                        )}
                    </button>
                </div>

                <input
                    type="text"
                    placeholder="e.g. 5 medium questions about chapter 2"
                    className="py-4 px-5 font-secondary outline-none border border-purple-800/50 rounded-xl text-gray-200 bg-transparent w-full"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                />

                <button
                    onClick={handleGenerate}
                    disabled={generating || !file}
                    className="flex items-center justify-center gap-2 py-4 px-7 rounded-xl bg-purple-600/30 hover:bg-purple-600/40 border border-purple-600/50 text-purple-300 font-secondary font-extrabold tracking-wider cursor-pointer active:scale-95 transition disabled:opacity-40 disabled:cursor-not-allowed whitespace-nowrap"
                >
                    {generating ? (
                        <>
                            <LuLoader className="w-4 h-4 animate-spin" />
                            Generating...
                        </>
                    ) : (
                        <>
                            <BsStars className="w-4 h-4" />
                            Generate
                        </>
                    )}
                </button>
            </div>

            {generating && (
                <p className="mt-4 text-sm text-zinc-500 font-secondary tracking-wide">
                    Reading the PDF and writing questions. This can take up to a
                    minute for large documents.
                </p>
            )}

            {error && (
                <p className="mt-4 text-sm text-rose-400 font-secondary tracking-wide border border-rose-800/40 bg-rose-900/10 rounded-lg py-3 px-4">
                    {error}
                </p>
            )}

            {/* Review step */}
            {drafts.length > 0 && (
                <div className="mt-8 pt-6 border-t border-white/10">
                    <div className="flex items-center justify-between mb-5 flex-wrap gap-4">
                        <h4 className="font-secondary font-bold tracking-wider text-gray-300">
                            Review{' '}
                            <span className="text-purple-400">
                                {selectedCount}
                            </span>{' '}
                            of {drafts.length} selected
                        </h4>

                        <div className="flex items-center gap-3">
                            <div className="flex items-center gap-2">
                                <input
                                    type="text"
                                    className="text-center bg-green-800/20 outline-none border border-green-800 w-16 py-2 text-gray-50 font-extrabold rounded-lg"
                                    value={timeLimit}
                                    onChange={(e) => setTimeLimit(e.target.value)}
                                />
                                <span className="text-xs text-green-500 tracking-widest font-bold">
                                    SECS EACH
                                </span>
                            </div>

                            <button
                                onClick={handleSaveSelected}
                                disabled={saving || selectedCount === 0}
                                className="flex items-center gap-2 py-2.5 px-5 rounded-xl bg-green-600/20 hover:bg-green-600/30 border border-green-600/40 text-green-300 font-secondary font-extrabold tracking-wider cursor-pointer active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed"
                            >
                                {saving
                                    ? 'Saving...'
                                    : `Add ${selectedCount} to Quiz`}
                            </button>
                        </div>
                    </div>

                    <div className="space-y-4">
                        {drafts.map((q, qIdx) => (
                            <div
                                key={qIdx}
                                className={`rounded-xl border py-5 px-6 transition-colors ${
                                    q.selected
                                        ? 'bg-zinc-900/50 border-purple-800/40'
                                        : 'bg-zinc-900/20 border-gray-800/40 opacity-50'
                                }`}
                            >
                                <div className="flex items-start gap-4 mb-4">
                                    <input
                                        type="checkbox"
                                        checked={q.selected}
                                        onChange={(e) =>
                                            updateDraft(qIdx, {
                                                selected: e.target.checked,
                                            })
                                        }
                                        className="mt-2 w-4 h-4 accent-purple-500 cursor-pointer shrink-0"
                                    />

                                    <input
                                        type="text"
                                        value={q.text}
                                        onChange={(e) =>
                                            updateDraft(qIdx, {
                                                text: e.target.value,
                                            })
                                        }
                                        className="flex-1 bg-transparent border-b border-transparent hover:border-gray-700 focus:border-purple-600 outline-none font-secondary text-gray-200 tracking-wide font-semibold pb-1"
                                    />

                                    <span
                                        className={`text-xs px-2 py-0.5 rounded border font-medium shrink-0 ${
                                            DIFFICULTY_STYLES[q.difficulty] ??
                                            DIFFICULTY_STYLES.Medium
                                        }`}
                                    >
                                        {q.difficulty}
                                    </span>

                                    <button
                                        onClick={() =>
                                            setDrafts((prev) =>
                                                prev.filter((_, i) => i !== qIdx)
                                            )
                                        }
                                        className="text-rose-400 hover:text-rose-300 cursor-pointer shrink-0"
                                        title="Discard this question"
                                    >
                                        <BiTrash className="w-4 h-4" />
                                    </button>
                                </div>

                                <div className="grid sm:grid-cols-2 gap-3 pl-8">
                                    {q.options.map((opt, optIdx) => (
                                        <div
                                            key={optIdx}
                                            className={`flex items-center border rounded-lg overflow-hidden ${
                                                opt.isCorrect
                                                    ? 'border-green-500/50 bg-green-500/5'
                                                    : 'border-gray-800/60 bg-white/5'
                                            }`}
                                        >
                                            <button
                                                onClick={() =>
                                                    setCorrect(qIdx, optIdx)
                                                }
                                                title="Mark as the correct answer"
                                                className={`w-10 self-stretch flex items-center justify-center cursor-pointer ${
                                                    opt.isCorrect
                                                        ? 'bg-green-500 text-gray-100 font-extrabold'
                                                        : 'hover:bg-white/5 text-zinc-600'
                                                }`}
                                            >
                                                {opt.isCorrect ? '✓' : ''}
                                            </button>
                                            <input
                                                type="text"
                                                value={opt.text}
                                                onChange={(e) =>
                                                    setOptionText(
                                                        qIdx,
                                                        optIdx,
                                                        e.target.value
                                                    )
                                                }
                                                className="w-full bg-transparent px-3 py-2.5 font-secondary text-sm text-zinc-300 focus:outline-none"
                                            />
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default AiQuizGenerator;
