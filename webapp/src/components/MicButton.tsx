import { useEffect, useRef, useState } from "react";
import { Mic, MicOff } from "lucide-react";
import { isSttAvailable, createStt, type SttSession } from "@/common/speech";

export function MicButton({
  input,
  setInput,
}: {
  input: string;
  setInput: (val: string) => void;
}) {
  const [listening, setListening] = useState(false);
  const [interim, setInterim] = useState("");
  const sttRef = useRef<SttSession | null>(null);

  useEffect(() => {
    if (!isSttAvailable()) return;
    sttRef.current = createStt(
      (transcript, isFinal) => {
        if (isFinal) {
          setInput(input + (input ? " " : "") + transcript);
          setInterim("");
        } else {
          setInterim(transcript);
        }
      },
      () => setListening(false),
    );
    return () => { sttRef.current?.stop(); };
  }, []);

  if (!isSttAvailable()) return null;

  return (
    <>
      {interim && (
        <p className="text-xs text-slate-500 mb-1 italic">
          &ldquo;{interim}&rdquo;
        </p>
      )}
      <button
        type="button"
        onClick={() => {
          if (!sttRef.current) return;
          if (listening) {
            sttRef.current.stop();
            setListening(false);
          } else {
            sttRef.current.start();
            setListening(true);
          }
        }}
        className={
          listening
            ? "p-2 rounded-md border border-slate-700 text-red-400 border-red-500/50 bg-red-500/10 animate-pulse flex-shrink-0"
            : "p-2 rounded-md border border-slate-700 text-slate-400 hover:bg-slate-800 flex-shrink-0"
        }
        title={listening ? "Stop listening" : "Voice input"}
      >
        {listening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
      </button>
    </>
  );
}
