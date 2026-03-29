"use client";

import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, Loader2, School, Square, Pause } from 'lucide-react';
import { ApiResponse } from '../../types';

export default function SunmarkAIAgent() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcription, setTranscription] = useState("");
  const [responses, setResponses] = useState<ApiResponse['responses'] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const recognitionRef = useRef<any>(null);

  // --- 1. Voice-to-Text Setup [cite: 16, 31] ---
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US'; 

      recognitionRef.current.onresult = (event: any) => {
        const text = event.results[0][0].transcript;
        setTranscription(text);
        handleQuery(text); // Requirement: One voice input -> Multiple answers [cite: 26]
      };

      recognitionRef.current.onend = () => setIsRecording(false);
    }
  }, []);

  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop();
    } else {
      setTranscription("");
      setResponses(null);
      recognitionRef.current?.start();
      setIsRecording(true);
    }
  };

  // --- 2. RAG API Call [cite: 17] ---
  const handleQuery = async (queryText: string) => {
    setIsLoading(true);
    try {
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input: queryText, chat_history: [] }),
      });
      const data: ApiResponse = await res.json();
      setResponses(data.responses);
    } catch (error) {
      console.error("Backend Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // --- 3. Text-to-Voice Controls [cite: 24, 35] ---
  const speak = (text: string | undefined) => {
    if (!text) return;
    window.speechSynthesis.cancel(); 
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    window.speechSynthesis.cancel();
  };

  const pauseSpeaking = () => {
    if (window.speechSynthesis.speaking) {
      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
      } else {
        window.speechSynthesis.pause();
      }
    }
  };

  return (
    <main className="min-h-screen bg-slate-50 p-4 md:p-10 font-sans text-slate-900">
      <div className="max-w-6xl mx-auto">
        
        {/* Header Section */}
        <div className="flex items-center justify-center gap-3 mb-8">
          <School className="text-indigo-600" size={32} />
          <h1 className="text-3xl font-bold text-slate-800">Sunmark School AI</h1>
        </div>

        {/* Voice Recording Button [cite: 31] */}
        <section className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200 mb-8 text-center">
          <button
            onClick={toggleRecording}
            className={`p-6 rounded-full transition-all duration-300 ${
              isRecording ? 'bg-red-500 scale-110' : 'bg-indigo-600 hover:bg-indigo-700 shadow-indigo-200 shadow-lg'
            } text-white`}
          >
            {isRecording ? <MicOff size={28} /> : <Mic size={28} />}
          </button>
          <div className="mt-4">
            <p className="text-sm font-medium text-slate-400 uppercase tracking-widest">
              {isRecording ? "Recording..." : "Click to Ask a Question"}
            </p>
            <p className="mt-2 text-lg text-slate-700 font-medium italic">
              {transcription || "Transcribed query will appear here..."} [cite: 32]
            </p>
          </div>
        </section>

        {/* 2-Column Multi-Model Comparison [cite: 25, 33] */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[
            { key: 'groq', label: 'Groq (Llama 3.3)' },
            { key: 'openrouter', label: 'OpenRouter (GPT-3.5)' }
          ].map((model) => (
            <div key={model.key} className="bg-white rounded-xl shadow-md border border-slate-200 flex flex-col min-h-[450px]">
              <div className="p-4 border-b bg-slate-50 rounded-t-xl font-bold text-slate-600">
                {model.label} [cite: 34]
              </div>
              
              <div className="p-6 flex-grow overflow-y-auto text-slate-600 leading-relaxed">
                {isLoading ? (
                  <div className="flex flex-col items-center justify-center h-full gap-2 text-slate-400">
                    <Loader2 className="animate-spin text-indigo-500" />
                    <span className="text-xs">Processing RAG...</span> [cite: 36]
                  </div>
                ) : responses ? (
                  <div className="animate-in fade-in duration-700">
                    {responses[model.key as keyof typeof responses].answer}
                  </div>
                ) : (
                  <div className="h-full flex items-center justify-center text-slate-300 italic">
                    Waiting for input
                  </div>
                )}
              </div>

              {/* Independent Audio Controls [cite: 35, 36] */}
              <div className="p-4 border-t bg-slate-50/50 flex flex-wrap gap-2">
                <button
                  disabled={!responses || isLoading}
                  onClick={() => speak(responses?.[model.key as keyof typeof responses]?.answer)}
                  className="flex-1 flex items-center justify-center gap-2 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-40 font-medium"
                >
                  <Volume2 size={16} /> Play
                </button>

                <div className="flex gap-2">
                  <button
                    disabled={!responses || isLoading}
                    onClick={pauseSpeaking}
                    className="px-4 py-2 border border-slate-200 bg-white text-slate-600 rounded-lg hover:bg-slate-100 disabled:opacity-40"
                  >
                    <Pause size={16} />
                  </button>
                  <button
                    disabled={!responses || isLoading}
                    onClick={stopSpeaking}
                    className="px-4 py-2 border border-red-100 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 disabled:opacity-40"
                  >
                    <Square size={16} fill="currentColor" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}