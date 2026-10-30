import React, { useId, useState } from "react";
import { KopanoAssertReceipt } from "../types/rtc";

interface KopanoAssertStampProps {
  receipt: KopanoAssertReceipt;
  className?: string;
}

export const KopanoAssertStamp: React.FC<KopanoAssertStampProps> = ({
  receipt,
  className = "",
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);
  const detailsId = useId();

  const handleCopyProof = async () => {
    setCopied(false);
    setCopyError(false);
    try {
      await navigator.clipboard.writeText(receipt.proof_hash);
      setCopied(true);
    } catch {
      setCopyError(true);
    }
  };

  return (
    <div className={`assert-stamp-wrapper ${className}`}>
      {/* Compact Sovereign Stamp Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-cyan-950/40 hover:bg-cyan-900/60 border border-cyan-500/30 hover:border-cyan-400 text-[11px] font-mono text-cyan-300 transition-all cursor-pointer shadow-sm shadow-cyan-950/40"
        title="Inspect returned receipt; independent verification is pending"
        aria-expanded={isOpen}
        aria-controls={detailsId}
      >
        <span className="w-2 h-2 rounded-full bg-amber-400" />
        <span className="font-bold text-amber-300">{receipt.assert_id}</span>
        <span className="text-slate-500">•</span>
        <span className="text-slate-300">Verification pending</span>
        <span className="text-slate-500">•</span>
        <span className="text-cyan-400 font-semibold">Returned receipt</span>
      </button>

      {/* Expandable Sovereign Proof Card */}
      {isOpen && (
        <div id={detailsId} className="mt-3 p-4 rounded-2xl bg-slate-950/90 border border-cyan-500/40 shadow-2xl backdrop-blur-md text-xs space-y-3 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <span className="text-base">📜</span>
              <span className="font-bold text-slate-100 uppercase tracking-wider">
                Returned Kopano Receipt
              </span>
            </div>
            <span className="px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-[10px] font-mono font-bold">
              NOT_INDEPENDENTLY_VERIFIED
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-[11px]">
            <div>
              <span className="text-slate-400 block mb-0.5">INTENT DOMAIN:</span>
              <span className="font-mono text-cyan-300 font-semibold">{receipt.intent_domain}</span>
            </div>
            <div>
              <span className="text-slate-400 block mb-0.5">REQUESTED PERSONA:</span>
              <span className="font-mono text-amber-300 font-semibold">{receipt.rtc_identity}</span>
            </div>
          </div>

          <div>
            <span className="text-slate-400 block mb-0.5">REPORTED CLAIM:</span>
            <p className="text-slate-200 bg-slate-900/60 p-2 rounded-xl border border-slate-800">
              "{receipt.claim}"
            </p>
          </div>
          <p>Reported status: {receipt.status}. Reported region: {receipt.residency}.</p>
          <p>This returned record does not establish ledger persistence, execution, or data residency.</p>

          <div className="pt-2 border-t border-slate-900 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-[10px] font-mono text-slate-400">
            <div className="break-all max-w-xs">
              SHA256: <span className="text-slate-300">{receipt.proof_hash}</span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleCopyProof}
                className="px-2 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition cursor-pointer"
              >
                {copied ? "✓ Copied Hash" : "Copy Hash"}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="px-2 py-1 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 transition cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
          {copyError && <p role="alert">Couldn’t copy the hash. You can select it from the receipt instead.</p>}
        </div>
      )}
    </div>
  );
};

export default KopanoAssertStamp;
