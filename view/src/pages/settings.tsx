import RootLayout from "./layout";

export default function Settings() {
    const textStyle = `block
        w-full
        rounded-md
        border-gray-300
        shadow-sm
        focus:border-sky-300 focus:ring focus:ring-sky-200 focus:ring-opacity-50`;
    const checkboxStyle = `rounded
    border-gray-300
    text-indigo-600
    shadow-sm
    focus:border-sky-300
    focus:ring
    focus:ring-offset-0
    focus:ring-sky-200
    focus:ring-opacity-50`
    return (
        <RootLayout>
            <div className="grid grid-cols-1 gap-6">
                <label htmlFor="username" className="block">
                    <span className="mb-1 text-slate-700 block font-medium">Username for eClass Login</span>
                    <input type="text" placeholder="" className={textStyle} id="username" />
                </label>
                <label htmlFor="password" className="block">
                    <span className="mb-1 text-slate-700 block font-medium">Password for eClass Login</span>
                    <input type="password" placeholder="" className={textStyle} id="password" />
                </label>
                <label htmlFor="weighted" className="block">
                    <input type="checkbox" className={checkboxStyle} id="weighted" />
                    <span className="ml-2 text-slate-700 font-medium">Weighted grades (+10 for AP)</span>
                </label>
                <label htmlFor="normalize" className="block">
                    <input type="checkbox" className={checkboxStyle} id="normalize" />
                    <span className="ml-2 text-slate-700 font-medium">Normalize grades</span>
                </label>
                <label htmlFor="notify" className="block">
                    <input type="checkbox" className={checkboxStyle} />
                    <span className="ml-2 text-slate-700 font-medium">Notify me when grade drops</span>
                </label>
            </div>
        </RootLayout>
    );
}