import React, { useMemo } from 'react';
import { motion } from 'framer-motion';

/**
 * InlineWaveform — A ChatGPT-style waveform visualizer that fits inside the input bar.
 * Shows dynamic bars that respond to audio level, with cancel (X) and confirm (✔) buttons.
 */
export default function InlineWaveform({ audioLevel = 0, onCancel, onConfirm }) {
    // Generate ~40 bars for a realistic waveform look
    const NUM_BARS = 40;

    // Create stable random seeds for each bar so they don't change on re-render
    const barSeeds = useMemo(() => {
        return Array.from({ length: NUM_BARS }, (_, i) => {
            // Use a pseudo-random pattern based on index for varied heights
            return Math.sin(i * 1.7 + 3) * 0.5 + 0.5; // 0-1 range
        });
    }, []);

    return (
        <div className="flex items-center gap-2 w-full px-2">
            {/* Plus / attachment button placeholder (left side) */}
            <button
                className="w-10 h-10 flex items-center justify-center rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-slate-700 transition shrink-0"
                title="Attach"
            >
                <span className="material-icons text-[24px]">add</span>
            </button>

            {/* Waveform area — fills the middle */}
            <div className="flex-1 flex items-center justify-center h-10 gap-[2px] overflow-hidden">
                {barSeeds.map((seed, i) => {
                    // Each bar height is driven by the audio level + its seed offset
                    // Silent: bars are ~2-4px tall (flat line)
                    // Speaking: bars scale up to 24-32px
                    const silentHeight = 3;
                    const maxHeight = 28;

                    // Add time-varying offset using seed to create organic movement
                    const levelFactor = audioLevel * (0.4 + seed * 0.6);
                    const height = silentHeight + (maxHeight - silentHeight) * levelFactor;

                    return (
                        <motion.div
                            key={i}
                            animate={{ height }}
                            transition={{
                                type: "spring",
                                stiffness: 400,
                                damping: 25,
                                mass: 0.3,
                            }}
                            className="w-[3px] rounded-full bg-gray-400 dark:bg-slate-400"
                            style={{ minHeight: silentHeight }}
                        />
                    );
                })}
            </div>

            {/* Cancel (X) button */}
            <button
                onClick={onCancel}
                className="w-9 h-9 flex items-center justify-center rounded-full text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition shrink-0"
                title="Cancel recording"
            >
                <span className="material-icons text-xl">close</span>
            </button>

            {/* Confirm (✔) button */}
            <button
                onClick={onConfirm}
                className="w-9 h-9 flex items-center justify-center rounded-full bg-primary text-white hover:bg-primary-hover transition shrink-0 shadow-sm"
                title="Confirm recording"
            >
                <span className="material-icons text-xl">check</span>
            </button>
        </div>
    );
}
