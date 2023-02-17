export type CourseCardProps = {
    score: number;
    name: string;
    teacher: string;
    email: string;
    onClick: () => void;
};

function getScoreStyle(score: number) {
    let scoreStyle = "bg-gradient-to-br from-blue-500 to-indigo-500";
    if (score < 80) {
        scoreStyle = "bg-blue-200";
    } else if (score < 90) {
        scoreStyle = "bg-blue-300";
    } else if (score < 100) {
        scoreStyle = "bg-blue-400";
    }
    return scoreStyle + " text-transparent bg-clip-text";
}

function titleCase(str: string) {
    return str
        .toLowerCase()
        .split(" ")
        .map((word) => word[0].toUpperCase() + word.slice(1))
        .map(
            (word) =>
                ({
                    I: "I",
                    Ii: "II",
                    Iii: "III",
                    Iv: "IV",
                    V: "V",
                    Vi: "VI",
                    Ap: "AP",
                    Gf: "GF",
                    Bc: "BC",
                    AB: "AB",
                }[word] || word)
        )
        .join(" ");
}

export default function CourseCard(props: CourseCardProps) {
    const { score, name, teacher, email, onClick } = props;
    return (
        <div
            className="flex flex-col justify-center sm:items-center w-full sm:w-64 h-64 p-8 bg-slate-50 cursor-pointer hover:bg-slate-100"
            onClick={onClick}
        >
            <div className="flex justify-between flex-col sm:w-48 h-48">
                <p
                    className={
                        "font-black leading-none text-[79px] " +
                        getScoreStyle(score)
                    }
                >
                    {props.score}
                </p>
                <div className="w-full flex flex-col gap-0">
                    <p className="text-2xl font-bold mb-1 capitalize">
                        {titleCase(name)}
                    </p>
                    <p className="text-sm font-light leading-snug text-ellipsis max-w-full overflow-clip">{`${teacher}`}</p>
                    <p
                        className="text-sm font-light leading-snug text-ellipsis max-w-full overflow-clip cursor-pointer"
                        onClick={(e) => {
                            window.open(`mailto:${email}`, "_blank");
                        }}
                    >{`${email}`}</p>
                </div>
            </div>
        </div>
    );
}
