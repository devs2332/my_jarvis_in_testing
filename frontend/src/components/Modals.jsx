import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export function Modal({ isOpen, onClose, title, children, actions }) {
    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="absolute inset-0 bg-black/40 backdrop-blur-sm"
                />
                <motion.div
                    initial={{ scale: 0.95, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.95, opacity: 0 }}
                    className="relative bg-white dark:bg-surface-dark rounded-xl shadow-xl w-full max-w-md overflow-hidden border border-slate-200 dark:border-slate-800"
                >
                    <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center">
                        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h3>
                        <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                            <span className="material-icons text-xl">close</span>
                        </button>
                    </div>
                    <div className="p-6">
                        {children}
                    </div>
                    {actions && (
                        <div className="px-6 py-4 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-800 flex justify-end gap-3">
                            {actions}
                        </div>
                    )}
                </motion.div>
            </div>
        </AnimatePresence>
    );
}

export function DeleteConfirmationModal({ isOpen, onClose, onConfirm, itemName }) {
    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title="Delete Conversation"
            actions={
                <>
                    <button
                        onClick={onClose}
                        className="px-4 py-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-sm font-medium"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={onConfirm}
                        className="px-4 py-2 rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors text-sm font-medium shadow-sm shadow-red-500/20"
                    >
                        Delete
                    </button>
                </>
            }
        >
            <p className="text-slate-600 dark:text-slate-300">
                Are you sure you want to delete <span className="font-semibold text-slate-900 dark:text-white">"{itemName}"</span>? This action cannot be undone.
            </p>
        </Modal>
    );
}

export function ExportHistoryModal({ isOpen, onClose, onExport }) {
    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title="Export Chat History"
            actions={
                <>
                    <button
                        onClick={onClose}
                        className="px-4 py-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-sm font-medium"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={onExport}
                        className="px-4 py-2 rounded-lg bg-primary text-white hover:bg-blue-600 transition-colors text-sm font-medium shadow-sm shadow-primary/20"
                    >
                        Export
                    </button>
                </>
            }
        >
            <div className="space-y-4">
                <p className="text-slate-600 dark:text-slate-300 text-sm">
                    Choose a format to export your conversation history.
                </p>
                <div className="grid grid-cols-2 gap-3">
                    <button className="flex flex-col items-center justify-center p-4 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-primary dark:hover:border-primary hover:bg-blue-50 dark:hover:bg-blue-900/10 transition-all group">
                        <span className="material-icons text-3xl text-slate-400 group-hover:text-primary mb-2">description</span>
                        <span className="text-sm font-medium text-slate-700 dark:text-slate-200">PDF</span>
                    </button>
                    <button className="flex flex-col items-center justify-center p-4 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-primary dark:hover:border-primary hover:bg-blue-50 dark:hover:bg-blue-900/10 transition-all group">
                        <span className="material-icons text-3xl text-slate-400 group-hover:text-primary mb-2">code</span>
                        <span className="text-sm font-medium text-slate-700 dark:text-slate-200">JSON</span>
                    </button>
                </div>
            </div>
        </Modal>
    );
}
