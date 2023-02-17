import Icon from "./Logo";
import Link from "next/link";
import { useState } from "react";

export default function Header() {
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    return (
        <header className="w-[100vw] px-8 md:px-12 lg:px-16">
            <div className="relative py-6 lg:py-8 flex items-center justify-between text-slate-700 font-semibold text-sm leading-6 dark:text-slate-200">
                <Link href="/">
                    <div className="flex items-center gap-2">
                        <Icon size={24} />
                        <h1 className="text-2xl font-bold">Better Gradebook</h1>
                    </div>
                </Link>
                {isMenuOpen && (
                    <div
                        className="fixed top-0 left-0 bottom-0 right-0 backdrop-blur-sm bg-slate-900/20"
                        onClick={() => setIsMenuOpen(false)}
                    />
                )}
                <nav>
                    <ul
                        className={
                            (isMenuOpen
                                ? "fixed top-4 right-4 w-full max-w-xs bg-white rounded-lg shadow-lg p-6 text-base space-y-6 font-semibold" +
                                "text-slate-900 dark:bg-slate-800 dark:text-slate-400 dark:highlight-white/5"
                                : "max-md:hidden") +
                            " flex flex-col md:static md:flex-row md:items-center gap-x-8"
                        }
                    >
                        <Link
                            href="/courses"
                            className="hover:text-sky-500 dark:hover:text-sky-400"
                        >
                            Courses
                        </Link>
                        <Link
                            href="/summary"
                            className="hover:text-sky-500 dark:hover:text-sky-400"
                        >
                            Summary
                        </Link>
                        <Link
                            href="/settings"
                            className="hover:text-sky-500 dark:hover:text-sky-400"
                        >
                            Settings
                        </Link>
                        <img
                            src="/icons/close.svg"
                            alt="close"
                            className="absolute md:hidden top-0 right-6 cursor-pointer text-slate-700 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-300"
                            onClick={() => setIsMenuOpen(false)}
                        />
                    </ul>
                    <img
                        src="/icons/menu.svg"
                        alt="menu"
                        className="md:hidden rounded-full bg-slate-50 p-2 hover:bg-slate-100 cursor-pointer"
                        onClick={() => setIsMenuOpen(!isMenuOpen)}
                    />
                </nav>
            </div>
        </header>
    );
}
