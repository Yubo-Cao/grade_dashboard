import { cls } from "@/utils/common";
import RootLayout from "./layout";

type FunctionComponentProps = {
    title: string;
    description: string;
    onClick?: () => void;
};

function FunctionComponent({
    title,
    description,
    onClick,
}: FunctionComponentProps) {
    return (
        <div
            className={cls(
                "w-full h-full max-w-sm",
                "flex flex-col items-start p-6",
                "cursor-pointer",
                "rounded-lg border border-transparent hover:border hover:border-slate-400 hover:dark:border-slate-300",
                "transition-all"
            )}
            onClick={onClick}
        >
            <h2 className="font-black leading-8 text-4xl">
                {title}
                <span className="transition-all">{`->`}</span>
            </h2>
            <p className="text-base font-light text-start leading-loose mt-2">
                {description}
            </p>
            <style jsx>{`
                div:hover h2 span {
                    padding-left: 0.75em;
                }
                h2 span {
                    transform: translateX(0);
                    padding-left: 0.5em;
                }
            `}</style>
        </div>
    );
}

export default function Index() {
    return (
        <RootLayout>
            <div className="text-center flex flex-col h-full items-center gap-8 pb-8 sm:justify-between ">
                <div className="hidden sm:block"></div>
                <div>
                    <h1 className="text-slate-900 font-black text-6xl">
                        The Future of{" "}
                        <span className="text-slate-500 block">Grade Book</span>
                    </h1>
                    <p className="text-slate-600 text-2xl font-light leading-relaxed mt-4 max-w-4xl">
                        Better Gradebook is a free, open-source gradebook that
                        helps <span className="text-sky-500 font-medium">you </span>
                        check your grades, track your assignments, and stay on
                        top of your classes.
                    </p>
                </div>
                <div className="flex items-center justify-center gap-4">
                    <FunctionComponent
                        title="Gradebook"
                        description="Check grade for each of your classes, analyze the weight of each
                    assignment and how they contributed to your grade."
                        onClick={() => window.open("/courses", "_self")}
                    />
                    <FunctionComponent
                        title="Analyze"
                        description="Analyze your grades and see where is your weakness, strength, and record the historical trend of your grades."
                        onClick={() => window.open("/analyze", "_self")}
                    />
                    <FunctionComponent
                        title="Settings"
                        description="Configure your gradebook, set your credentials, and customize your gradebook, and more."
                        onClick={() => window.open("/settings", "_self")}
                    />
                </div>
            </div>
        </RootLayout>
    );
}
