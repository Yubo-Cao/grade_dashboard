import {
    useState,
    ReactNode,
    Dispatch,
    SetStateAction,
    useEffect,
} from "react";

export type DialogProps = {
    children: ReactNode;
    className?: string;
    isOpen: boolean;
    onOpenChange: Dispatch<SetStateAction<boolean>>;
};

export default function Dialog({
    children,
    isOpen,
    onOpenChange,
    className,
}: DialogProps) {
    useEffect(() => {
        if (isOpen) {
            const escHandler = (event: KeyboardEvent) => {
                if (event.key === "Escape") {
                    onOpenChange(false);
                }
            };
            const resizeHandler = () => {
                onOpenChange(false);
            };
            window.addEventListener("keydown", escHandler);
            window.addEventListener("resize", resizeHandler);
            return () => {
                window.removeEventListener("keydown", escHandler);
                window.removeEventListener("resize", resizeHandler);
            };
        }
    }, [isOpen]);
    return (
        <>
            {isOpen && (
                <div
                    className="fixed top-0 left-0 bottom-0 right-0 backdrop-blur-sm bg-slate-900/20"
                    onClick={() => onOpenChange(false)}
                />
            )}
            <div
                className={
                    (isOpen
                        ? "fixed bg-white rounded-lg shadow-lg p-6 text-base" +
                          "text-slate-900 dark:bg-slate-800 dark:text-slate-400 dark:highlight-white/5"
                        : "hidden") +
                    " " +
                    className
                }
            >
                {children}
                <img
                    src="/icons/close.svg"
                    alt="close"
                    className="absolute md:hidden top-0 right-6 cursor-pointer text-slate-700 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-300"
                    onClick={() => onOpenChange(false)}
                />
            </div>
        </>
    );
}
