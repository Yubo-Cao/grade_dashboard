import Tooltip from "@/components/Tooltip";
import RootLayout from "./layout";

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
}

function AssignmentItem({ title, measureType, score, commentCode, comment, weight, contribute, blame, grading }: AssignmentItemProps) {
    if (score === undefined && !(commentCode !== undefined && comment !== undefined)) {
        throw new Error("Either score or comment must be defined");
    }
    if (score !== undefined && (commentCode !== undefined || comment !== undefined)) {
        throw new Error("You can't have both score and comment");
    }

}

export default function Analyze() {
    return (
        <RootLayout>
            <Tooltip content="This is a tooltip" direction="right">
                <div className="bg-slate-50 h-64"></div>
            </Tooltip>
        </RootLayout>
    );
}
