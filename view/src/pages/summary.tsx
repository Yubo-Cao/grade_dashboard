import Tooltip from "@/components/Tooltip";
import RootLayout from "./layout";
import { ReactNode } from "react";
import { getScoreStyle } from "@/components/CourseCard";

type AssignmentItemProps = {
    // Title of the assignment
    title: string;
    // Type of the assignment, e.g., AKS Progress, AKS Summative, etc.
    measureType: string;
    // Score for the assignment. If it's NaN, it's not graded yet.
    score?: number;
    // Code for the comment, e.g., INP/NTI
    commentCode?: string;
    // Comment text
    comment?: string;
    // Weight of the assignment
    weight: number;
    // How much this assignment contributed towards the final grade
    contribute: number;
    // If base-on 1, what's the weight of this assignment
    blame: number;
    // It this for grading?
    grading: boolean;
};

function AssignmentItem({
    title,
    measureType,
    score,
    commentCode,
    comment,
    weight,
    contribute,
    blame,
    grading,
}: AssignmentItemProps) {
    if (score === undefined && !comment) {
        throw new Error("Either score or comment must be defined");
    }

    if (score !== undefined && comment) {
        throw new Error("You can't have both score and comment");
    }

    const scoreOrComment = comment ? (
        <Tooltip content={comment} direction="right">
            <p className="font-black text-6xl">{commentCode}</p>
        </Tooltip>
    ) : (
        <p
            className={`font-black text-6xl ${grading ? getScoreStyle(score!) : "text-slate-500"
                }`}
        >
            {score}
        </p>
    );

    const Meta = ({
        title,
        value,
        tooltip,
    }: {
        title: string;
        value: number;
        tooltip?: ReactNode;
    }) => (
        <div className="flex gap-1 items-center text-xs">
            <span className="font-light">{title}</span>
            <span className="font-black">
                {!value || isNaN(value) ? "N/A" : value}
            </span>
            {tooltip && (
                <Tooltip
                    content={tooltip}
                    direction="top"
                    className="text-xs font-light"
                    tooltipClassName="w-64 bg-white rounded-lg border text-[10px] text-slate-500"
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke-width="1.5"
                        stroke="currentColor"
                        className="w-4 h-4 text-slate-400 hover:text-slate-600"
                    >
                        <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z"
                        />
                    </svg>
                </Tooltip>
            )}
        </div>
    );
    return (
        <div className="flex justify-center items-center gap-4">
            {scoreOrComment}
            <div className="flex flex-col gap-0.5">
                <p className="font-semibold text-xl text-black">{title}</p>
                <div className="flex gap-4 items-center text-slate-500">
                    <span className="font-black text-[0.6875em]">
                        {measureType}
                    </span>
                    <Meta
                        title="Weight"
                        value={weight}
                        tooltip="The percentage of the assignment of this measure type contributed to your final grade"
                    />
                    <Meta
                        title="Contribute"
                        value={contribute}
                        tooltip="The percentage of the assignment of this measure type contributed to your final grade"
                    />
                    <Meta
                        title="Blame"
                        value={blame}
                        tooltip="The percentage of the assignment of this measure type contributed to your final grade"
                    />
                </div>
            </div>
        </div>
    );
}

export default function Analyze() {
    return (
        <RootLayout>
            <AssignmentItem
                title="AKS Summative ?!+!"
                measureType="AKS"
                score={100}
                weight={100}
                contribute={100}
                blame={100}
                grading={true}
            />
        </RootLayout>
    );
}
